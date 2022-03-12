from typing import List


def get_mongo_obj_with_structure_idx(mongo_documents: List[dict], structure_doc_name: str) -> int:
    """
    Returns the index of the parsed MongoDB collection document by the name of its corresponding structure.

    :param mongo_documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
    :param structure_doc_name: the name of the document from which the SRS structure was extracted.
    :return: index of the parsed MongoDB collection document.
    """
    mongo_obj_idx = next(
        (i for i, item in enumerate(mongo_documents) if item['document_name'] == structure_doc_name),
        -1
    )
    if mongo_obj_idx < 0:
        raise ValueError(f'there are no objects named {structure_doc_name} in the MongoDB collection')
    return mongo_obj_idx
