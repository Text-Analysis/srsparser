import sys
from docx import Document
from os.path import basename, splitext, abspath
from os import getenv
from docx.opc.exceptions import PackageNotFoundError
from word import DocxAnalyzer
from pymongo import MongoClient
from dotenv import load_dotenv
from json import dump

load_dotenv()

if __name__ == "__main__":
    try:
        path = sys.argv[1]
        if path.endswith(".doc"):
            doc_abspath = abspath(path)
            path = DocxAnalyzer.save_as_docx(doc_abspath)

        client = MongoClient(getenv("CONNECTION_STRING"))
        db = client["documentsAnalysis"]

        coll = db["treeTemplates"]
        tree_template = coll.find_one({"name": "default"})

        document = Document(path)
        analyzer = DocxAnalyzer(document, tree_template["structure"])
        document_structure = analyzer.get_docx_structure()

        with open(f"out/{splitext(basename(path))[0]}.json", "w", encoding='UTF8') as file:
            dump(document_structure, file, ensure_ascii=False)

        coll = db["techSpecifications"]
        coll.insert_one({"document_name": splitext(basename(path))[0], "structure": document_structure})
    except PackageNotFoundError:
        print(f"File not found at {sys.argv[1]}")
        exit(1)
