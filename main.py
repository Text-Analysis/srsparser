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


if __name__ == '__main__':
    try:
        doc = docx.Document(sys.argv[1])
    except PackageNotFoundError:
        print(f'File not found at "{sys.argv[1]}"')
        exit(1)
    except ValueError:
        # ValueError means that input file with .doc extension
        doc_abspath = os.path.abspath(sys.argv[1])
        # Converts .doc to .docx
        docx_path = save_as_docx(doc_abspath)
        doc = docx.Document(docx_path)

    for paragraph in doc.paragraphs:
        print(paragraph.text)

    exit(0)
