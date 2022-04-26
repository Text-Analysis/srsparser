import re

from docx import Document
from docx.document import Document as DocumentWithTable
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from srsparser import configs
from srsparser.language_processor import LanguageProcessor
from srsparser.sections_tree import SectionsTree


class Parser:
    """
    Parser analyzes semi-structured .docx documents and forming sections tree documents according to the templates.
    """

    def __init__(self, sections_tree_template: dict):
        """
        :param sections_tree_template: sections tree structure containing certain sections tree structure,
            which will be filled text content according to the relevant .docx file.
        """
        self.sections_tree = SectionsTree(sections_tree_template)
        self.nlp = LanguageProcessor(init_pullenti=False)

    def parse_docx(self, path: str) -> dict:
        """
        Reads .docx document and returns sections tree structure filled according to the it's content.
        """
        document = Document(path)
        return self.get_sections_structure(document)

    def get_sections_structure(self, doc: Document) -> dict:
        """
        Returns sections tree structure filled according to the text document content.
        """
        sections = self.get_sections_first(doc)
        self.fill_tree(sections)

        sections = self.get_sections_second(doc)
        self.fill_tree(sections)

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
            # section is array where the first el is heading and the second is content
            section = paragraph.text.split(':', 1)
            if len(section) <= 1:
                continue

            if self.is_heading(section[0]) and not self.is_table_element(paragraph, doc):
                if section[0] and section[1]:
                    result[section[0]] = section[1].strip()
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
            if self.is_heading(paragraph.text) and not self.is_table_element(paragraph, doc):
                if curr_heading_text and curr_heading_paragraphs:
                    result[curr_heading_text] = ' '.join(curr_heading_paragraphs)

                curr_heading_text = re.sub(configs.NUMBERING_PATTERN, '', paragraph.text).strip()
                curr_heading_paragraphs.clear()
            elif len(paragraph.text) > 1:
                curr_heading_paragraph = re.sub(configs.NUMBERING_PATTERN, '', paragraph.text).strip()
                if self.nlp.punct_at_end_pattern.match(curr_heading_paragraph) is None:
                    curr_heading_paragraph += '.'
                curr_heading_paragraphs.append(curr_heading_paragraph)
        result[curr_heading_text] = ' '.join(curr_heading_paragraphs)
        return result

    def fill_tree(self, sections: dict):
        """
        Fills leaf sections tree structure expressed section nesting levels.

        :param sections: dictionary containing pairs like "section heading" — "section content".
        """
        for heading, text in sections.items():
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

    def is_heading(self, p_text: str) -> bool:
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
