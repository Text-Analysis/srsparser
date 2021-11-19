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
from sections_tree import SectionsTree, Section
from nlp import strings_similarity, patterns

example_tree = SectionsTree()


def save_as_docx(doc_path: str) -> str:
    """
    Converts `.s` file to a file with the `.docx` extension.

    :param doc_path: the path to the file with the .s extension
    :return: the path to the file with the .docx extension
    """
    # opening MS Word
    word = win32.gencache.EnsureDispatch("Word.Application")
    word_doc = word.Documents.Open(doc_path)
    word_doc.Activate()

    # rename path file with .docx
    new_file_abs = abspath(doc_path)
    new_file_abs = re.sub(r"\.\w+$", ".docx", new_file_abs)

    # save and Close
    word.ActiveDocument.SaveAs(new_file_abs, FileFormat=constants.wdFormatXMLDocument)
    word_doc.Close(False)

    return new_file_abs


def is_paragraph_heading(paragraph: Paragraph) -> bool:
    """
    Checks whether the paragraph is a heading.

    :return: True if the paragraph is the heading, otherwise — False.
    """
    if paragraph.text.strip() == "":
        return False

    if "Heading" in paragraph.style.name:
        return True

    # start of by initializing an empty string to store bold words inside a run
    run_bold_text = ""

    # iterate over all runs of the curr paragraph and collect all the words which are bold
    for run in paragraph.runs:
        if run.bold:
            run_bold_text += run.text

    # now check if run_bold_text matches the entire paragraph text.
    # if it matches, it means all the words in the current paragraph are bold and can be considered as a heading
    return run_bold_text.strip() == paragraph.text.strip() and paragraph.paragraph_format.alignment is None


def is_paragraph_contains_heading(p: Paragraph) -> bool:
    """
    Checks whether the paragraph contains a section heading.

    :return: True if the paragraph contains the heading, otherwise — False.
    """
    global example_tree

    # a potential section title can be placed before a colon in a paragraph (e.g. 1.2 Условное обозначение: АИС
    # «Товарищество собственников жилья».)
    possible_heading = p.text.split(":")[0]

    possible_heading = re.sub(patterns, "", possible_heading)

    if possible_heading == "":
        return False

    for leaf_section in example_tree.get_leaf_sections():
        if strings_similarity(leaf_section.name, possible_heading) >= 0.6:
            return True

    for section in example_tree.get_sections():
        if strings_similarity(section.name, possible_heading) >= 0.6:
            return True

    return False


def is_table_element(doc_with_tables: docx.Document, paragraph: Paragraph) -> bool:
    """
    Checks whether a paragraph is a table element.

    :return: True if the paragraph is a table element, otherwise — False.
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

            curr_heading_text = re.sub(patterns, "", paragraph.text.strip())
            curr_heading_paragraphs.clear()
        elif is_paragraph_contains_heading(paragraph):
            heading_with_text = paragraph.text.split(":")
            heading, text = heading_with_text[0], ":".join(heading_with_text[1:])
            heading = re.sub(patterns, "", heading.strip())
            if text != "":
                result[heading] = text
        else:
            curr_heading_paragraphs.append(paragraph.text)
    return result


def restore_headings_hierarchy(headings_with_texts: dict) -> dict:
    """
    Restores the hierarchy of headings expressed by nesting levels.

    :param headings_with_texts: see: get_headings_with_texts(s: docx.Document).
    :return: returns a dictionary representing the hierarchy of document sections.
    """
    tree = SectionsTree()
    for heading, text in headings_with_texts.items():
        if text != "":
            max_ratio = 0.5
            text_parent = None
            for section in tree.get_leaf_sections():
                ratio = strings_similarity(section.name, heading)
                if ratio >= max_ratio:
                    max_ratio = ratio
                    text_parent = section
            if text_parent is not None:
                text_parent.text = text
            else:
                max_ratio = 0
                for section in tree.get_sections():
                    ratio = strings_similarity(section.name, heading)
                    if ratio >= max_ratio:
                        max_ratio = ratio
                        text_parent = section
                if text_parent is not None:
                    heading_without_numbering = " ".join(heading.split()[1:])
                    Section(name=heading_without_numbering, text=text, parent=text_parent)
    return tree.get_dict_from_root()


if __name__ == "__main__":
    try:
        path = sys.argv[1]
        if path.endswith(".doc"):
            doc_abspath = abspath(path)
            path = save_as_docx(doc_abspath)

        document = docx.Document(path)
        headings_with_texts = get_headings_with_texts(document)
        headings_hierarchy = restore_headings_hierarchy(headings_with_texts)

        with open(f"out/{splitext(basename(path))[0]}.json", "w", encoding='UTF8') as file:
            dump(headings_hierarchy, file, ensure_ascii=False)
        exit(0)
    except PackageNotFoundError:
        print(f"File not found at {sys.argv[1]}")
        exit(1)
