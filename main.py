import difflib
import distance
import docx
from os.path import basename, splitext, abspath
import re
import sys
from json import dump
import win32com.client as win32
from docx.document import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from win32com.client import constants


def save_as_docx(doc_path: str) -> str:
    """
    Converts `.doc` file to a file with the `.docx` extension.

    :param doc_path: the path to the file with the .doc extension
    :return: the path to the file with the .docx extension
    """
    # Opening MS Word
    word = win32.gencache.EnsureDispatch("Word.Application")
    word_doc = word.Documents.Open(doc_path)
    word_doc.Activate()

    # Rename path file with .docx
    new_file_abs = abspath(doc_path)
    new_file_abs = re.sub(r"\.\w+$", ".docx", new_file_abs)

    # Save and Close
    word.ActiveDocument.SaveAs(new_file_abs, FileFormat=constants.wdFormatXMLDocument)
    word_doc.Close(False)

    return new_file_abs


def is_paragraph_heading(paragraph: Paragraph) -> bool:
    """
    Checks whether the paragraph is a header.

    :return: True if the paragraph is the title, otherwise — False.
    """
    if paragraph.text.strip() == "":
        return False

    if "Heading" in paragraph.style.name:
        return True

    # Start of by initializing an empty string to store bold words inside a run
    run_bold_text = ""

    # Iterate over all runs of the curr paragraph and collect all the words which are bold
    for run in paragraph.runs:
        if run.bold:
            run_bold_text += run.text

    # Now check if run_bold_text matches the entire paragraph text.
    # If it matches, it means all the words in the current paragraph are bold and can be considered as a heading
    return run_bold_text.strip() == paragraph.text.strip() and paragraph.paragraph_format.alignment is None


def is_table_element(doc_with_tables: docx.Document, paragraph: Paragraph) -> bool:
    """
    Checks whether a paragraph is a table element.

    :return: True if the paragraph is the title, otherwise — False.
    """
    for table in doc_with_tables.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip() == paragraph.text.strip():
                    return True
    return False


def iter_paragraphs(parent):
    """
    Yield each paragraph and table child within `parent`, in document order.
    Each returned value is an instance of `Paragraph`. `parent`
    would most commonly be a reference to a main `Document` object, but
    also works for a `_Cell` object, which itself can contain paragraphs and tables.
    """
    if isinstance(parent, docx.document.Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent.tc
    else:
        raise TypeError(repr(type(parent)))

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            table = Table(child, parent)
            for row in table.table.rows:
                for cell in row.cells:
                    for child_paragraph in iter_paragraphs(cell):
                        yield child_paragraph


def get_headings_with_texts(doc: docx.Document) -> dict:
    """
    :param doc: docx.Document containing headings and the corresponding text.
    :return: a collection of pairs of the form: {"heading_text": "text under heading", ...}.
    """
    result = {}

    # remember the heading and appropriate paragraphs
    curr_heading_text = ""
    curr_heading_paragraphs = []

    for paragraph in iter_paragraphs(doc):
        # tables contain their own headings, which we do not take into account
        if is_paragraph_heading(paragraph) and not is_table_element(doc, paragraph):
            if curr_heading_text != "":
                result[curr_heading_text] = "\n".join(curr_heading_paragraphs)

            curr_heading_text = paragraph.text.strip()
            curr_heading_paragraphs.clear()
        else:
            curr_heading_paragraphs.append(paragraph.text)
    return result


def restore_headings_hierarchy(headings_with_texts: dict) -> list:
    """
    Restores the hierarchy of headings expressed by nesting levels.

    :param headings_with_texts: see: get_headings_with_texts(doc: docx.Document).
    :return: a list containing a collection of pairs of the form: {"section_name": "...", "text": "..."} or
    {"section_name": "", "sub_sections": [{"section_name": "...", "text": "..."}, {"section_name": "...", "text":
    "..."}]}.
    """
    global nesting_levels, completed_levels

    hierarchy = []
    for heading, heading_text in headings_with_texts.items():
        rec_add_heading_in_hierarchy(hierarchy, nesting_levels, heading, heading_text)
        if completed_levels > 1:
            nesting_levels -= (nesting_levels - completed_levels)
            completed_levels = 0
    return hierarchy


def strings_similarity(s1: str, s2: str) -> float:
    """
    Determines the similarity coefficient of strings `s1` and `s2`.

    :return: 0.0 — completely dissimilar, 1.0 — equal.
    """
    diff = difflib.SequenceMatcher(None, s1, s2).ratio()
    sor = 1 - distance.sorensen(s1, s2)
    jac = 1 - distance.jaccard(s1, s2)
    return (diff + sor + jac) / 3


nesting_levels = 0  # the number of nesting levels from the topmost element to the lowest element in the hierarchy
completed_levels = 0  # the number of nesting levels passed in the process of compiling the header hierarchy
last_heading_section = None


def rec_add_heading_in_hierarchy(hierarchy: list, nesting_level: int, heading: str, heading_text: str):
    """
    Recursively moves through hierarchy and determines where to insert the heading along with its contents (future
    subheadings or text).

    :param hierarchy: a list representing the hierarchy of nesting or its separate part.
    :param nesting_level: the number of nesting levels remaining before the leaf element in the hierarchy.
    :param heading: heading name.
    :param heading_text: the text corresponding to the heading.
    """
    global nesting_levels, completed_levels, last_heading_section

    # if the hierarchy has 0 levels of nesting
    if nesting_level == 0:
        if last_heading_section is not None:
            # if the heading is the parent for another heading (this is evidenced by an empty string in
            # heading_text[1], in place of which the child heading should stand with its own text)
            if heading_text == "":
                heading_section = {"section_name": heading, "sub_sections": []}
                last_heading_section["sub_sections"].append(heading_section)
                nesting_levels += 1
                last_heading_section = heading_section
            else:
                last_heading_section["sub_sections"].append({"section_name": heading, "text": heading_text})
        else:
            if heading_text == "":
                heading_section = {"section_name": heading, "sub_sections": []}
                hierarchy.append(heading_section)
                nesting_levels += 1
                last_heading_section = heading_section
            else:
                hierarchy.append({"section_name": heading, "text": heading_text})
    # if the hierarchy has one or more levels of nesting
    else:
        if hierarchy[len(hierarchy) - 1].get("sub_sections") is not None:
            ratio = strings_similarity(hierarchy[len(hierarchy) - 1]["section_name"].strip(), heading.strip())
            if ratio >= 0.5:
                last_heading_section = hierarchy[len(hierarchy) - 1]
                completed_levels += 1
            rec_add_heading_in_hierarchy(hierarchy[len(hierarchy) - 1]["sub_sections"], nesting_level - 1, heading,
                                         heading_text)
        else:
            rec_add_heading_in_hierarchy(hierarchy, 0, heading, heading_text)


if __name__ == "__main__":
    try:
        path = sys.argv[1]
        if path.endswith(".doc"):
            doc_abspath = abspath(path)
            path = save_as_docx(doc_abspath)

        document = docx.Document(path)
        heading_with_texts = get_headings_with_texts(document)
        headings_hierarchy = restore_headings_hierarchy(heading_with_texts)

        with open(f"out/{splitext(basename(path))[0]}.json", "w", encoding='UTF8') as file:
            dump(headings_hierarchy, file, ensure_ascii=False)
        exit(0)
    except PackageNotFoundError:
        print(f"File not found at {sys.argv[1]}")
        exit(1)
