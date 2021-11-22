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


def get_headings_with_texts_p_styles(doc: docx.Document) -> dict:
    """
    Returns headings and their corresponding text content based on the analysis of paragraph styles.

    :param doc: docx.Document containing headings and the corresponding text.
    :return: a collection of pairs of the form: "heading" — "text under heading".
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
            curr_heading_paragraphs.append(paragraph.text.strip())
    return result


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

    return False


def get_headings_with_texts_containing_check(doc: docx.Document) -> dict:
    """
    Returns headings and their corresponding text content based on the analysis of the paragraph content.
    The potential heading may be to the left of the first colon.

    :param doc: docx.Document containing headings and the corresponding text.
    :return: a collection of pairs of the form: "heading" — "text under heading".
    """
    result = {}

    for paragraph in iter_paragraphs(doc):
        if is_paragraph_contains_heading(paragraph) and not is_table_element(doc, paragraph):
            p_split = paragraph.text.split(":")

            heading = p_split[0]
            heading = re.sub(patterns, "", heading).strip()

            text = ":".join(p_split[1:]).strip()

            if heading != "" and text != "":
                result[heading] = text
    return result


def get_headings_with_texts_containing_and_appending(doc: docx.Document) -> dict:
    """
    Returns headers and their corresponding text content based on the analysis of the paragraph content and combining
    several paragraphs under one section.

    :param doc: docx.Document containing headings and the corresponding text.
    :return: a collection of pairs of the form: "heading" — "text under heading".
    """
    result = {}

    # remember the heading and appropriate paragraphs
    curr_heading = ""
    curr_heading_paragraphs = []

    for paragraph in iter_paragraphs(doc):
        p_split = paragraph.text.split(":")
        if is_paragraph_contains_heading(paragraph) and not is_table_element(doc, paragraph):
            if curr_heading != "" and curr_heading_paragraphs:
                result[curr_heading] = " .".join(curr_heading_paragraphs)

            curr_heading = re.sub(patterns, "", p_split[0]).strip()
            curr_heading_paragraphs.clear()
            curr_heading_paragraphs.append(":".join(p_split[1:]).strip())
        elif re.match('^([а-яё0-9][).])+.+', p_split[0]):
            heading = re.sub(patterns, "", p_split[0]).strip()
            text = ":".join(p_split[1:]).strip()
            if heading != "" and text != "":
                result[heading] = text
        else:
            if not is_paragraph_heading(paragraph) and paragraph.text != "":
                curr_heading_paragraphs.append(paragraph.text.strip())
    return result


def restore_headings_hierarchy(headings_with_texts: dict, hierarchy_tree: SectionsTree):
    """
    Restores the hierarchy of headings expressed by nesting levels.

    :param headings_with_texts: see: get_headings_with_texts(s: docx.Document).
    :param hierarchy_tree: the titles of this tree_skeleton will correspond to the texts.
    """
    for heading, text in headings_with_texts.items():
        max_ratio = 0.5
        text_parent = None
        for section in hierarchy_tree.get_leaf_sections():
            ratio = strings_similarity(section.name, heading)
            if ratio >= max_ratio:
                max_ratio = ratio
                text_parent = section
        if text_parent is not None and text_parent.text == "":
            text_parent.text = text


if __name__ == "__main__":
    try:
        path = sys.argv[1]
        if path.endswith(".doc"):
            doc_abspath = abspath(path)
            path = save_as_docx(doc_abspath)

        document = docx.Document(path)

        # initialize the template of the section tree, which will be filled with texts corresponding to the sections
        tree_skeleton = SectionsTree()

        # we are looking for texts in three different ways that will correspond to the sections of the tree skeleton:
        # 1
        headings_with_texts = get_headings_with_texts_p_styles(document)
        restore_headings_hierarchy(headings_with_texts, tree_skeleton)
        # 2
        headings_with_texts = get_headings_with_texts_containing_check(document)
        restore_headings_hierarchy(headings_with_texts, tree_skeleton)
        # 3
        headings_with_texts = get_headings_with_texts_containing_and_appending(document)
        restore_headings_hierarchy(headings_with_texts, tree_skeleton)

        with open(f"out/{splitext(basename(path))[0]}.json", "w", encoding='UTF8') as file:
            dump(tree_skeleton.get_dict_from_root(), file, ensure_ascii=False)
        exit(0)
    except PackageNotFoundError:
        print(f"File not found at {sys.argv[1]}")
        exit(1)
