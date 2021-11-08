import docx
from docx.opc.exceptions import PackageNotFoundError
import sys
import re
import os
import win32com.client as win32
from win32com.client import constants


# Converts .doc file to a file with the .docx extension
def save_as_docx(doc_path: str) -> str:
    # Opening MS Word
    word = win32.gencache.EnsureDispatch('Word.Application')
    word_doc = word.Documents.Open(doc_path)
    word_doc.Activate()

    # Rename doc_path file with .docx
    new_file_abs = os.path.abspath(doc_path)
    new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

    # Save and Close
    word.ActiveDocument.SaveAs(new_file_abs, FileFormat=constants.wdFormatXMLDocument)
    word_doc.Close(False)

    return new_file_abs


# Checks whether the paragraph is a header
def is_heading(paragraph) -> bool:
    if paragraph.text == '':
        return False

    if 'Heading' in paragraph.style.name:
        return True

    # Start of by initializing an empty string to store bold words inside a run
    run_bold_text = ''

    # Iterate over all runs of the curr paragraph and collect all the words which are bold
    for run in paragraph.runs:
        if run.bold:
            run_bold_text += run.text

    # Now check if run_bold_text matches the entire paragraph text.
    # If it matches, it means all the words in the current paragraph are bold and can be considered as a heading
    return run_bold_text != '' and run_bold_text == str(paragraph.text) and run_bold_text.lstrip()[0].isdigit()


def display_doc_content(path: str):
    doc = docx.Document(path)
    heading_with_paragraphs = {}
    heading = ''
    paragraphs = []
    for paragraph in doc.paragraphs:
        if is_heading(paragraph):
            if heading != '' and len(paragraphs) > 0:
                heading_with_paragraphs[heading] = '\n'.join(paragraphs)
            heading = paragraph.text
            paragraphs.clear()
        else:
            paragraphs.append(paragraph.text)

    for heading, paragraph in heading_with_paragraphs.items():
        print(f'--------------------\nHeading: {heading}\nIt\'s paragraph:\n{paragraph}--------------------')
        print()


if __name__ == '__main__':
    try:
        doc_path = 'doc/tz_08.docx'
        if doc_path.endswith('.doc'):
            doc_abspath = os.path.abspath(doc_path)
            doc_path = save_as_docx(doc_abspath)

        display_doc_content(doc_path)
        exit(0)
    except PackageNotFoundError:
        print(f'File not found at "{sys.argv[1]}"')
        exit(1)
