import re
import win32com.client as win32
from win32com.client import constants
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.document import Document
from os.path import abspath
from sections_tree import SectionsTree
from nlp import strings_similarity, numbering_pattern

MIN_SIMILARITY_RATIO = 0.5


class DocxAnalyzer:
    """
    A class that analyzes a Word document with the technical specification and forms a tree structure based on it.
    """

    def __init__(self, doc: Document, tree_tmpl: dict):
        """
        :param doc: the object of a Word document containing information about the technical specification.
        :param tree_tmpl: section tree template.
        """
        self.doc = doc

        # A tree containing the approved structure of the technical specification, which will be filled by the
        # contents of the document
        self.tree = SectionsTree(tree_tmpl)

    def get_docx_structure(self) -> dict:
        """
        Get the structure of the document by parsing it in several ways.
        """
        sections = self.get_sections_first()
        self.fill_sections_tree(sections)

        sections = self.get_sections_second()
        self.fill_sections_tree(sections)

        return self.tree.get_dict_from_root()

    def get_sections_first(self) -> dict:
        """
        Returns sections based on the analysis of the paragraph content. The potential heading may be to the left of
        the first colon.

        :return: a collection of pairs of the form: "heading" — "text under heading".
        """
        result = {}

        for paragraph in self.iter_paragraphs(self.doc):
            # a potential section title can be placed before a colon in a paragraph (e.g. 1.2 Условное обозначение: АИС
            # «Товарищество собственников жилья».)
            p_text_split = paragraph.text.split(":", 1)
            if len(p_text_split) <= 1:
                continue

            if self.is_heading_of_sec(p_text_split[0]) and not self.is_table_element(paragraph):
                if p_text_split[0] != "" and p_text_split[1] != "":
                    result[p_text_split[0]] = p_text_split[1]
        return result

    def get_sections_second(self) -> dict:
        """
        Returns sections based on the analysis of the paragraph content.

        :return: a collection of pairs of the form: "heading" — "text under heading".
        """
        result = {}

        # remember the heading and appropriate paragraphs
        curr_heading_text = ""
        curr_heading_paragraphs = []

        for paragraph in self.iter_paragraphs(self.doc):
            # tables contain their own headings, which we do not take into account
            if self.is_heading_of_sec(paragraph.text) and not self.is_table_element(paragraph):
                if curr_heading_text != "":
                    result[curr_heading_text] = "\n".join(curr_heading_paragraphs)

                curr_heading_text = paragraph.text
                curr_heading_paragraphs.clear()
            else:
                curr_heading_paragraphs.append(re.sub(numbering_pattern, "", paragraph.text))
        result[curr_heading_text] = "\n".join(curr_heading_paragraphs)
        return result

    def fill_sections_tree(self, headings_with_texts: dict):
        """
        Restores the sections tree structure expressed by nesting levels.
        """
        for heading, text in headings_with_texts.items():
            max_ratio = 0
            text_parent = None
            for section in self.tree.get_leaf_sections():
                ratio = strings_similarity(section.name, heading)
                if ratio >= max_ratio:
                    max_ratio = ratio
                    text_parent = section
            if text_parent is not None:
                text_parent.text = text

    def iter_paragraphs(self, parent):
        """
        Yield each paragraph and table child within `parent`, in document order.
        Each returned value is an instance of `Paragraph`. `parent`
        would most commonly be a reference to a main `Document` object, but
        also works for a `_Cell` object, which itself can contain paragraphs and tables.
        """
        if isinstance(parent, Document):
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
                        for child_paragraph in self.iter_paragraphs(cell):
                            yield child_paragraph

    def is_heading_of_sec(self, p_text: str) -> (bool, float):
        """
        Checks whether the p_text is a heading of the sections tree.

        :return: True if the p_text is a heading of the sections tree, otherwise — False.
        """
        for section in self.tree.get_leaf_sections():
            if strings_similarity(section.name, p_text) >= MIN_SIMILARITY_RATIO:
                return True
        return False

    def is_table_element(self, paragraph: Paragraph) -> bool:
        """
        Checks whether a paragraph is a table element.

        :return: True if the paragraph is a table element, otherwise — False.
        """
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip() == paragraph.text.strip():
                        return True
        return False

    @staticmethod
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

        # save and close
        word.ActiveDocument.SaveAs(new_file_abs, FileFormat=constants.wdFormatXMLDocument)
        word_doc.Close(False)

        return new_file_abs
