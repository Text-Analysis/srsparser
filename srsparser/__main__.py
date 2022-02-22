import argparse as ap
import logging
import logging.config
from os.path import basename, splitext

from prettytable import PrettyTable
from pymongo import MongoClient

from srsparser import SRSParser
from srsparser import configs
from srsparser.nlp import NLProcessor


def init_logger() -> logging.Logger:
    logging.config.dictConfig(configs.LOGGING_CONFIG)
    logger = logging.getLogger('default')
    return logger


def init_args_parser() -> ap.ArgumentParser:
    parser = ap.ArgumentParser(
        description='A command-line application written in Python that parses unstructured text documents '
                    '(files with .docx extension) with SRS in accordance with GOST standard 34.602-89 and '
                    'saves the structured results to the MongoDB database'
    )

    parser.add_argument(
        'mode',
        type=str,
        help='"parse" — analyzes the input documents and saves the parsing '
             'results (as structures) to MongoDB database; '
             '"keywords" — searches for keywords in the content of the document structure, '
             'which is stored in the resulting MongoDB collection',
    )

    parser.add_argument(
        'mongodb_url',
        type=str,
        help='MongoDB connection string (with the name of the database)'
    )

    parser.add_argument(
        'results_coll',
        type=str,
        help='name of MongoDB collection with parsing results '
             '(contains software requirements specifications structures '
             'filled according to the templates of the SRS structures)'
    )

    parser.add_argument(
        '-tc',
        '--tmpl-coll',
        dest='tmpl_coll',
        type=str,
        help='name of MongoDB collection with templates of software requirements specifications structures'
    )

    parser.add_argument(
        '-t',
        '--tmpl',
        dest='tmpl',
        type=str,
        help='template name of software requirements specification structure '
             'according to which the parsing is performed'
    )

    parser.add_argument(
        '-dp',
        '--docx-path',
        dest='docx_path',
        type=str,
        help='path to .docx file containing software requirements specification'
    )

    parser.add_argument(
        '-dn',
        '--docx-name',
        dest='docx_name',
        type=str,
        help='the name of document that is stored in the resulting collection as structure'
    )

    parser.add_argument(
        '-s',
        '--section',
        dest='section',
        default='Техническое задание',
        help='the name of the section of the SRS structure, '
             'relative to which the content will be selected from SRS structure of the document'
    )

    parser.add_argument(
        '-r',
        '--results',
        dest='results',
        action='store_true',
        help='show a list of document names that are stored in the resulting collection as structures'
    )

    return parser


def main():
    parser = init_args_parser()
    args = parser.parse_args()
    logger = init_logger()

    client = MongoClient(args.mongodb_url)
    db = client.get_default_database()
    logger.info('the connection to the database ("%s") is established', db.name)

    results_coll = db[args.results_coll]
    logger.info('the connection to the results collection ("%s") is established', results_coll.name)

    if args.results:
        logger.info('documents in results collection:\n%s',
                    [structure['document_name'] for structure in results_coll.find({})])
        return

    mode = args.mode.lower()
    logger.info('operating mode: %s', mode)

    if mode == 'parse':
        tmpl_coll = db[args.tmpl_coll]
        logger.info('the connection to the templates collection ("%s") is established', tmpl_coll.name)

        structure_template = tmpl_coll.find_one({'name': args.tmpl})['structure']
        logger.info('a structure template ("%s") was obtained from the collection with the templates', args.tmpl)

        parser = SRSParser(structure_template)
        document_structure = parser.parse_docx(args.docx_path)
        logger.info('based on the content of the document ("%s"), a section structure was created', args.docx_path)

        document_name = splitext(basename(args.docx_path))[0]

        results_coll.insert_one({'document_name': document_name, 'structure': document_structure})
        logger.info('the created section structure is loaded into the results collection')
    elif mode == 'keywords':
        results = list(results_coll.find({}))

        docx_structure_idx = -1
        for idx in range(len(results)):
            if results[idx]['document_name'] == args.docx_name:
                docx_structure_idx = idx
                logger.info('the document "%s" was found in the results collection under the sequence number %s',
                            args.docx_name, docx_structure_idx + 1)
                break
        if docx_structure_idx < 0:
            logger.error('there is no such document in the results collection with document name "%s"', args.docx_name)
            return

        logger.info('initializing SDK pullenti...')
        nlp = NLProcessor()
        logger.info('done')

        logger.info('parsing section of the document content is "%s"', args.section)

        logger.info('collecting keywords using TF-IDF model...')
        tf_idf_keywords = nlp.get_structure_keywords_tf_idf(
            structures=[result['structure'] for result in results],
            structure_idx=docx_structure_idx,
            section_name=args.section
        )
        logger.info('done')

        logger.info('collecting keywords using pullenti...')
        pullenti_keywords = nlp.get_structure_keywords_pullenti(
            structure=results[docx_structure_idx]['structure'],
            section_name=args.section
        )
        logger.info('done')

        keywords_table = PrettyTable()

        if len(pullenti_keywords) >= len(tf_idf_keywords):
            keywords_table.add_column('TF-IDF', tf_idf_keywords)
            keywords_table.add_column('Pullenti', pullenti_keywords[:len(tf_idf_keywords)])
        else:
            keywords_table.add_column('TF-IDF', tf_idf_keywords[:len(pullenti_keywords)])
            keywords_table.add_column('Pullenti', pullenti_keywords)

        logger.info('below are the keywords of the "%s" section of the "%s" document:\n%s',
                    args.section, args.docx_name, keywords_table)
    else:
        logger.error('the mode "%s" does not exist', mode)

    client.close()


if __name__ == '__main__':
    main()
