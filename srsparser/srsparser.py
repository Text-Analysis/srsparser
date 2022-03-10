import re

from docx import Document
from docx.document import Document as DocumentWithTable
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from srsparser import configs
from srsparser.nlp import NLProcessor
from srsparser.sections_tree import SectionsTree


class SRSParser:
    """
    Parser analyzing .docx files with SRS and forming sections tree mongo_documents according to the SRS structure templates.
    """

    def __init__(self, sections_tree_template: dict):
        """
        :param sections_tree_template: SRS sections tree template containing certain sections tree structure,
            which will be filled text content according to the relevant .docx file.
        """
        self.sections_tree = SectionsTree(sections_tree_template)
        self.nlp = NLProcessor(init_pullenti=False)

    def parse_docx(self, docx_path: str) -> dict:
        """
        Reads text document (file with .docx extension) and
        returns sections tree structure filled according to the it's content.

        :param docx_path: path to the text document containing SRS.
        """
        document = Document(docx_path)
        return self.get_docx_structure(document)

    def get_docx_structure(self, doc: Document) -> dict:
        """
        Returns sections tree structure filled according to the text document content.
        """
        sections = self.get_sections_first(doc)
        self.fill_sections_tree(sections)

        sections = self.get_sections_second(doc)
        self.fill_sections_tree(sections)

        return self.sections_tree.to_dict()

    def get_sections_first(self, doc: Document) -> dict:
        """
        Returns sections according to parsing paragraphs content.
        The section heading can be to the left of the first occurrence of the colon.
        (example: 1.2 Условное обозначение: АИС «Товарищество собственников жилья»).

        :return: dictionary containing pairs like "section heading" — "section content".
        """
        result = {}

        for paragraph in self.iter_paragraphs(doc):
            p_text_split = paragraph.text.split(':', 1)
            if len(p_text_split) <= 1:
                continue

            if self.is_heading_of_sec(p_text_split[0]) and not self.is_table_element(paragraph, doc):
                if p_text_split[0] != '' and p_text_split[1] != '':
                    result[p_text_split[0]] = p_text_split[1].strip()
        return result

    def get_sections_second(self, doc: Document) -> dict:
        """
        Returns sections according to the position of paragraphs in a text document.

        :return: dictionary containing pairs like "section heading" — "section content".
        """
        result = {}
        curr_heading_text = ''
        curr_heading_paragraphs = []

        for paragraph in self.iter_paragraphs(doc):
            # tables contain their own headings, so we do not take them into account
            if self.is_heading_of_sec(paragraph.text) and not self.is_table_element(paragraph, doc):
                if curr_heading_text != '':
                    result[curr_heading_text] = '\n'.join(curr_heading_paragraphs)

                curr_heading_text = paragraph.text.strip()
                curr_heading_paragraphs.clear()
            else:
                curr_heading_paragraphs.append(re.sub(configs.NUMBERING_PATTERN, '', paragraph.text.strip()))
        result[curr_heading_text] = '\n'.join(curr_heading_paragraphs)
        return result

    def fill_sections_tree(self, headings_with_texts: dict):
        """
        Fills leaf sections tree structure expressed section nesting levels.

        :param headings_with_texts: dictionary containing pairs like "section heading" — "section content".
        """
        for heading, text in headings_with_texts.items():
            max_ratio = 0
            text_parent = None
            for section in self.sections_tree.get_leaf_sections():
                ratio = self.nlp.strings_similarity(section.name, heading)
                if ratio >= max_ratio:
                    max_ratio = ratio
                    text_parent = section
            if text_parent is not None:
                text_parent.text = text.strip()

    def iter_paragraphs(self, parent):
        if isinstance(parent, DocumentWithTable):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
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

    def is_heading_of_sec(self, p_text: str) -> bool:
        """
        Checks whether the paragraph is the heading of the section tree structure.

        :return: True — yes, else — False.
        """
        for section in self.sections_tree.get_leaf_sections():
            if self.nlp.strings_similarity(section.name, p_text) >= configs.MIN_SIMILARITY_RATIO:
                return True
        return False

    @staticmethod
    def is_table_element(paragraph: Paragraph, doc: Document) -> bool:
        """
        Checks whether the paragraph is a table element.

        :return: True — yes, else — False.
        """
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip() == paragraph.text.strip():
                        return True
        return False
