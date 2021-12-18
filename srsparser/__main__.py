import argparse as ap
from os.path import basename, splitext

from docx.opc.exceptions import PackageNotFoundError
from pymongo import MongoClient

from srsparser import Parser


def setup_args_parser():
    parser = ap.ArgumentParser(
        description='System for analyzing and uploading text documents with SRS to MongoDB'
    )

    parser.add_argument(
        'connection_string',
        type=str,
        help='connection string used to connect to a MongoDB'
    )

    parser.add_argument(
        'doc_path',
        type=str,
        help='the path to the MS Word document to be analyzed'
    )

    parser.add_argument(
        '-db',
        dest='db',
        type=str,
        default='documentsAnalysis',
        help='the name of the database that stores collections of templates and parsing results'
    )

    parser.add_argument(
        '-tc',
        dest='tmpl_coll',
        type=str,
        default='sectionTreeTemplates',
        help='the name of the MongoDB collection where sections tree templates are stored'
    )

    parser.add_argument(
        '-t',
        dest='tmpl',
        type=str,
        default='default',
        help='the name of the template on the basis of which the parsing will be performed'
    )

    parser.add_argument(
        '-rc',
        dest='results_coll',
        type=str,
        default='requirementsSpecifications',
        help='the name of the MongoDB collection where the parsing results are stored'
    )

    return parser


def run(connection_string: str, doc_path: str, db_name: str, tmpl_coll_name: str, tmpl_name: str,
        results_coll_name: str):
    client = MongoClient(connection_string)
    db = client[db_name]

    coll = db[tmpl_coll_name]
    tree_template = coll.find_one({"name": tmpl_name})["structure"]

    parser = Parser(tree_template)
    document_structure = parser.parse_doc(doc_path)

    doc_name = splitext(basename(doc_path))[0]

    coll = db[results_coll_name]
    coll.insert_one({"document_name": doc_name, "structure": document_structure})


def main():
    parser = setup_args_parser()
    args = parser.parse_args()
    try:
        run(args.connection_string, args.doc_path, args.db, args.tmpl_coll, args.tmpl, args.results_coll)
    except PackageNotFoundError:
        print(f"File not found at {args.doc_path}")
    except Exception:
        print("Unknown error")


if __name__ == "__main__":
    main()
