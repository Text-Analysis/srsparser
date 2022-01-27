import re

from docx import Document
from docx.document import Document as DocumentWithTable
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from srsparser import configs
from srsparser.nlp import strings_similarity
from srsparser.sections_tree import SectionsTree


class Parser:
    """
    Класс, анализирующий текстовые документы в формате .docx, содержащие ТЗ, и формирующий деревья разделов на основе
    данных шаблонов.
    """

    def __init__(self, sections_tree_template: dict):
        """
        :param sections_tree_template: шаблон дерева разделов, содержащий в себе определённую структуру дерева
            разделов, которая будет наполняться текстовым содержимым, найденным парсером.
        """
        self.sections_tree = SectionsTree(sections_tree_template)

    def parse_docx(self, path: str) -> dict:
        """
        Возвращает заполненную в соответствии с содержимым текстового документа с ТЗ структуру дерева разделов.

        :param path: путь к текстовому документу в формате .docx, содержащему ТЗ.
        """
        document = Document(path)
        return self.get_docx_structure(document)

    def get_docx_structure(self, doc: Document) -> dict:
        """
        Возвращает заполненную структуру дерева разделов текстового документа с ТЗ.
        """
        sections = self.get_sections_first(doc)
        self.fill_sections_tree(sections)

        sections = self.get_sections_second(doc)
        self.fill_sections_tree(sections)

        return self.sections_tree.to_dict()

    def get_sections_first(self, doc: Document) -> dict:
        """
        Возвращает разделы, основываясь на анализе содержимого абзацев:
        потенциальные заголовки разделов могут быть слева от первого вхождения символа ":"
        (прим.: 1.2 Условное обозначение: АИС «Товарищество собственников жилья»).

        :return: словарь пар вида: "заголовок раздела" — "содержимое заголовка раздела (текст под ним)".
        """
        result = {}

        for paragraph in self.iter_paragraphs(doc):
            p_text_split = paragraph.text.split(":", 1)
            if len(p_text_split) <= 1:
                continue

            if self.is_heading_of_sec(p_text_split[0]) and not self.is_table_element(paragraph, doc):
                if p_text_split[0] != "" and p_text_split[1] != "":
                    result[p_text_split[0]] = p_text_split[1].strip()
        return result

    def get_sections_second(self, doc: Document) -> dict:
        """
        Возвращает разделы, основываясь на положении абзацев в текстовом документе с ТЗ.

        :return: словарь пар вида: "заголовок раздела" — "содержимое заголовка раздела (текст под ним)".
        """
        result = {}
        curr_heading_text = ""
        curr_heading_paragraphs = []

        for paragraph in self.iter_paragraphs(doc):
            # таблицы содержат свои заголовки, поэтому их не берём во внимание
            if self.is_heading_of_sec(paragraph.text) and not self.is_table_element(paragraph, doc):
                if curr_heading_text != "":
                    result[curr_heading_text] = "\n".join(curr_heading_paragraphs)

                curr_heading_text = paragraph.text.strip()
                curr_heading_paragraphs.clear()
            else:
                curr_heading_paragraphs.append(re.sub(configs.NUMBERING_PATTERN, "", paragraph.text.strip()))
        result[curr_heading_text] = "\n".join(curr_heading_paragraphs)
        return result

    def fill_sections_tree(self, headings_with_texts: dict):
        """
        Заполняет структуру дерева разделов, выраженную уровнями вложенности разделов.
        """
        for heading, text in headings_with_texts.items():
            max_ratio = 0
            text_parent = None
            for section in self.sections_tree.get_leaf_sections():
                ratio = strings_similarity(section.name, heading)
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
        Проверяет, является ли абзац заголовком структуры дерева разделов.

        :return: True — да, иначе — False.
        """
        for section in self.sections_tree.get_leaf_sections():
            if strings_similarity(section.name, p_text) >= configs.MIN_SIMILARITY_RATIO:
                return True
        return False

    @staticmethod
    def is_table_element(paragraph: Paragraph, doc: Document) -> bool:
        """
        Проверяет, является ли абзац элементом таблицы.

        :return: True — да, иначе — False.
        """
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip() == paragraph.text.strip():
                        return True
        return False
