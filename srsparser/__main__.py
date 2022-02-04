import argparse as ap
from os.path import basename, splitext

from pymongo import MongoClient

from srsparser import SRSParser


def init_args_parser() -> ap.ArgumentParser:
    parser = ap.ArgumentParser(
        description='A package for analyzing and uploading text documents '
                    'with software requirements specifications to NoSQL database MongoDB'
    )

    parser.add_argument(
        'docx_path',
        type=str,
        help='path to .docx file containing software requirements specification'
    )

    parser.add_argument(
        'mongodb_url',
        type=str,
        help='MongoDB database connection string'
    )

    parser.add_argument(
        'db_name',
        type=str,
        help='MongoDB database name'
    )

    parser.add_argument(
        'tmpl_coll_name',
        type=str,
        help='name of MongoDB collection with templates of software requirements specifications structures'
    )

    parser.add_argument(
        'tmpl_name',
        type=str,
        help='template name of software requirements specification structure '
             'according to which the parsing is performed'
    )

    parser.add_argument(
        'results_coll_name',
        type=str,
        help='name of MongoDB collection with parsing results '
             '(contains software requirements specifications structures '
             'filled according to the templates of the SRS structures)'
    )

    return parser


def main():
    parser = init_args_parser()
    args = parser.parse_args()

    client = MongoClient(args.mongodb_url)
    db = client[args.db_name]

    tmpl_coll = db[args.tmpl_coll_name]
    tree_template = tmpl_coll.find_one({'name': args.tmpl_name})['structure']

    parser = SRSParser(tree_template)
    document_structure = parser.parse_docx(args.docx_path)

    document_name = splitext(basename(args.docx_path))[0]

    results_coll = db[args.results_coll_name]
    results_coll.insert_one({'document_name': document_name, 'structure': document_structure})

    client.close()


if __name__ == '__main__':
    main()
