import docx
import re
import win32com.client as win32
from win32com.client import constants
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.document import Document
from os.path import abspath
from sections_tree import SectionsTree, Section
from nlp import strings_similarity, numbering_pattern, strip_spec_char_pattern


class DocxAnalyzer:
    """
    A class that analyzes a Word document with the technical specification and forms a tree structure based on it.
    """

    def __init__(self, doc: Document):
        """
        :param doc: the object of a Word document containing information about the technical specification, which
        should be distributed across the section tree.
        """
        self.doc = doc

        # A tree containing the approved structure of the technical specification, which will be filled by the
        # contents of the document
        self.tree = SectionsTree()

    def get_docx_structure(self) -> dict:
        """
        Get the structure of the document by parsing it in several ways.

        :return:
        """
        sections = self.get_sections_first()
        self.fill_sections_tree_first(sections)

        sections = self.get_sections_second()
        self.fill_sections_tree(sections)

        sections = self.get_sections_third()
        self.fill_sections_tree(sections)

        return self.tree.get_dict_from_root()

    def get_sections_first(self) -> dict:
        """
        Returns sections based on the analysis of paragraph styles.

        :return: a collection of pairs of the form: "heading" — "text under heading".
        """
        result = {}

        # remember the heading and appropriate paragraphs
        curr_heading_text = ""
        curr_heading_paragraphs = []

        for paragraph in self.iter_paragraphs(self.doc):
            # tables contain their own headings, which we do not take into account
            if self.is_heading(paragraph) and not self.is_table_element(self.doc, paragraph):
                if curr_heading_text != "":
                    result[curr_heading_text] = "\n".join(curr_heading_paragraphs)

                curr_heading_text = re.sub(strip_spec_char_pattern, "", paragraph.text)
                curr_heading_paragraphs.clear()
            else:
                curr_heading_paragraphs.append(re.sub(strip_spec_char_pattern, "", paragraph.text))
        return result

    def get_sections_second(self) -> dict:
        """
        Returns sections based on the analysis of the paragraph content. The potential heading may be to the left of
        the first colon.

        :return: a collection of pairs of the form: "heading" — "text under heading".
        """
        result = {}

        for paragraph in self.iter_paragraphs(self.doc):
            if self.does_contain_heading(paragraph) and not self.is_table_element(self.doc, paragraph):
                p_split = paragraph.text.split(":", 1)
                if len(p_split) > 1:
                    heading = re.sub(numbering_pattern, "", p_split[0]).strip()
                    text = re.sub(strip_spec_char_pattern, "", p_split[1])
                    if heading != "" and text != "":
                        result[heading] = text
        return result

    def get_sections_third(self) -> dict:
        """
        Returns sections based on the analysis of the paragraph content and combining several paragraphs under one
        section.

        :return: a collection of pairs of the form: "heading" — "text under heading".
        """
        result = {}

        # remember the heading and appropriate paragraphs
        curr_heading = ""
        curr_heading_paragraphs = []

        for paragraph in self.iter_paragraphs(self.doc):
            p_split = paragraph.text.split(":", 1)
            if len(p_split) > 1:
                if self.does_contain_heading(paragraph) and not self.is_table_element(self.doc, paragraph):
                    if curr_heading != "" and curr_heading_paragraphs:
                        result[curr_heading] = " .".join(curr_heading_paragraphs)

                    curr_heading = re.sub(numbering_pattern, "", p_split[0]).strip()

                    curr_heading_paragraphs.clear()
                    text = re.sub(strip_spec_char_pattern, "", p_split[1])
                    curr_heading_paragraphs.append(text)
                elif re.match(f'{numbering_pattern}.+', p_split[0]):
                    heading = re.sub(numbering_pattern, "", p_split[0]).strip()
                    text = re.sub(strip_spec_char_pattern, "", p_split[1])
                    if heading != "" and text != "":
                        result[heading] = text
            elif not self.is_heading(paragraph) and paragraph.text != "":
                curr_heading_paragraphs.append(re.sub(strip_spec_char_pattern, "", paragraph.text))
        return result

    def fill_sections_tree_first(self, headings_with_texts: dict):
        """
        Restores the sections tree structure expressed by nesting levels. If there is a section that is not in the
        section tree, then add it to the most appropriate section with a leaf element.
        """
        for heading, text in headings_with_texts.items():
            max_ratio = 0.5
            text_parent = None
            for section in self.tree.get_leaf_sections():
                ratio = strings_similarity(section.name, heading)
                if ratio >= max_ratio:
                    max_ratio = ratio
                    text_parent = section
            if text_parent is not None and text_parent.text == "":
                text_parent.text = text
            else:
                max_ratio = 0
                for section in self.tree.get_sections():
                    ratio = strings_similarity(section.name, heading)
                    if ratio >= max_ratio:
                        max_ratio = ratio
                        text_parent = section
                if text_parent is not None:
                    heading = re.sub(numbering_pattern, "", heading).strip()
                    if self.tree.root.name != heading:
                        Section(name=heading, text=text, parent=text_parent)

    def fill_sections_tree(self, headings_with_texts: dict):
        """
        Restores the sections tree structure expressed by nesting levels.
        """
        for heading, text in headings_with_texts.items():
            max_ratio = 0.5
            text_parent = None
            for section in self.tree.get_leaf_sections():
                ratio = strings_similarity(section.name, heading)
                if ratio >= max_ratio:
                    max_ratio = ratio
                    text_parent = section
            if text_parent is not None and text_parent.text == "":
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

    def does_contain_heading(self, p: Paragraph) -> bool:
        """
        Checks whether the paragraph contains a section heading.

        :return: True if the paragraph contains the heading, otherwise — False.
        """
        # a potential section title can be placed before a colon in a paragraph (e.g. 1.2 Условное обозначение: АИС
        # «Товарищество собственников жилья».)
        possible_heading = p.text.split(":", 1)[0]

        possible_heading = re.sub(numbering_pattern, "", possible_heading)

        if possible_heading == "":
            return False

        for leaf_section in self.tree.get_leaf_sections():
            if strings_similarity(leaf_section.name, possible_heading) >= 0.6:
                return True

        return False

    @staticmethod
    def is_heading(paragraph: Paragraph) -> bool:
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

    @staticmethod
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
