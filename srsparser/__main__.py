import argparse as ap
from os.path import basename, splitext

from docx.opc.exceptions import PackageNotFoundError
from pymongo import MongoClient

from srsparser import Parser


def setup_args_parser():
    parser = ap.ArgumentParser(
        description="Пакет для анализа и загрузки текстовых документов в NoSQL СУБД MongoDB"
    )

    parser.add_argument(
        "connection_string",
        type=str,
        help="строка подключения используется для подключения к MongoDB"
    )

    parser.add_argument(
        "doc_path",
        type=str,
        help="путь к текстовому документу в формате .docx, содержащему ТЗ"
    )

    parser.add_argument(
        "-db",
        dest="db",
        type=str,
        default="documentsAnalysis",
        help="название базы данных MongoDB, "
             "которая содержит в себе коллекции с шаблонами структур ТЗ и результатами парсинга"
    )

    parser.add_argument(
        "-tc",
        dest="tmpl_coll",
        type=str,
        default="sectionTreeTemplates",
        help="название коллекции MongoDB, в которой хранятся шаблоны структур ТЗ, "
             "в соответствии с которыми проводится парсинг текстового документа с ТЗ"
    )

    parser.add_argument(
        "-t",
        dest="tmpl",
        type=str,
        default="default",
        help="название шаблона структуры ТЗ, хранящегося в коллекции tmpl_coll, "
             "в соответствии с которым проводится парсинг текстового документа с ТЗ"
    )

    parser.add_argument(
        "-rc",
        dest="results_coll",
        type=str,
        default="requirementsSpecifications",
        help="название коллекции MongoDB, в которой хранятся результаты анализа текстовых документов с ТЗ "
             "(структуры, заполненные содержанием текстовых документов с ТЗ, "
             "в соответствии с шаблоном и самим документом)"
    )

    return parser


def run(connection_string: str, doc_path: str, db_name: str, tmpl_coll_name: str, tmpl_name: str,
        results_coll_name: str):
    client = MongoClient(connection_string)
    db = client[db_name]

    coll = db[tmpl_coll_name]
    tree_template = coll.find_one({"name": tmpl_name})["structure"]

    parser = Parser(tree_template)
    document_structure = parser.parse_docx(doc_path)

    doc_name = splitext(basename(doc_path))[0]

    coll = db[results_coll_name]
    coll.insert_one({"document_name": doc_name, "structure": document_structure})


def main():
    parser = setup_args_parser()
    args = parser.parse_args()
    try:
        run(args.connection_string, args.doc_path, args.db, args.tmpl_coll, args.tmpl, args.results_coll)
    except PackageNotFoundError:
        print(f"файл не найден по пути: {args.doc_path}")
    except Exception:
        print("неизвестная ошибка")


if __name__ == "__main__":
    main()
