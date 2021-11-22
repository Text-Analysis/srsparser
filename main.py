import sys
from docx import Document
from os.path import basename, splitext, abspath
from os import getenv
from docx.opc.exceptions import PackageNotFoundError
from word import DocxAnalyzer
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    try:
        path = sys.argv[1]
        if path.endswith(".doc"):
            doc_abspath = abspath(path)
            path = DocxAnalyzer.save_as_docx(doc_abspath)

        document = Document(path)
        analyzer = DocxAnalyzer(document)
        document_structure = analyzer.get_docx_structure()

        client = MongoClient(getenv("CONNECTION_STRING"))
        db = client["documentsAnalysis"]
        coll = db["techSpecifications"]

        coll.insert_one({"document_name": splitext(basename(path))[0], "structure": document_structure})
    except PackageNotFoundError:
        print(f"File not found at {sys.argv[1]}")
        exit(1)
