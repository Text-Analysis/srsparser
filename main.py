import sys
from docx import Document
from os.path import basename, splitext, abspath
from json import dump
from docx.opc.exceptions import PackageNotFoundError
from word import DocxAnalyzer

if __name__ == "__main__":
    try:
        path = sys.argv[1]
        if path.endswith(".doc"):
            doc_abspath = abspath(path)
            path = DocxAnalyzer.save_as_docx(doc_abspath)

        document = Document(path)
        analyzer = DocxAnalyzer(document)
        document_structure = analyzer.get_docx_structure()

        with open(f"out/{splitext(basename(path))[0]}.json", "w", encoding='UTF8') as file:
            dump(document_structure, file, ensure_ascii=False)
    except PackageNotFoundError:
        print(f"File not found at {sys.argv[1]}")
        exit(1)
