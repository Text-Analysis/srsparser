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
    return run_bold_text != '' and run_bold_text == str(paragraph.text)


# Returns a regular expression to search for headers with a structure similar to the heading
def get_regex_from_heading(heading: str) -> str:
    # Divide the title into 2 parts to separate the numbering from the rest of the title text
    split_heading = heading.split(' ', 2)
    heading_numbering = split_heading[0]
    regex = '^'
    for character in heading_numbering:
        if character.isdigit():
            regex += '[0-9]'
        elif character.isalpha():
            regex += '[а-я]'
        else:
            regex += f'\{character}'
    regex += ' .*'
    return regex


# Returns a string representation of the first header that is specified in GOST standard, that is, "общие сведения"
def get_first_heading(doc) -> str:
    for paragraph in doc.paragraphs:
        if is_heading(paragraph) and re.match(r'.*общ[а-я]{2,3} сведен[а-я]{2,3}.*', paragraph.text,
                                              re.IGNORECASE | re.M):
            return paragraph.text
    return ''


def display_doc_content(path: str):
    doc = docx.Document(path)
    first_heading = get_first_heading(doc)
    heading_regex = get_regex_from_heading(first_heading)
    heading_with_paragraphs = {}
    curr_heading = ''
    paragraphs = []

    for paragraph in doc.paragraphs:
        if is_heading(paragraph) and re.match(fr'{heading_regex}', paragraph.text, re.I):
            if curr_heading != '' and len(paragraphs) > 0:
                heading_with_paragraphs[curr_heading] = '\n'.join(paragraphs)
            curr_heading = paragraph.text
            paragraphs.clear()
        else:
            paragraphs.append(paragraph.text)
    if curr_heading != '' and len(paragraphs) > 0:
        heading_with_paragraphs[curr_heading] = '\n'.join(paragraphs)

    for curr_heading, paragraph in heading_with_paragraphs.items():
        print(
            f'--------------------\nHeading: {curr_heading}\nIt\'s paragraph:\n{paragraph.rstrip()}\n--------------------')
        print()


if __name__ == '__main__':
    try:
        doc_path = sys.argv[1]
        if doc_path.endswith('.doc'):
            doc_abspath = os.path.abspath(doc_path)
            doc_path = save_as_docx(doc_abspath)

        display_doc_content(doc_path)
        exit(0)
    except PackageNotFoundError:
        print(f'File not found at "{sys.argv[1]}"')
        exit(1)
