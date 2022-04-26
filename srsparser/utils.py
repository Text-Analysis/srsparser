from typing import List


def get_document_idx_by_name(documents: List[dict], name: str) -> int:
    """
    Returns the index of the parsed MongoDB collection document by the name.

    :param documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, name and structure).
    :param name: the name of the document.
    :return: index of the parsed MongoDB collection document.
    """
    document_idx = next(
        (i for i, item in enumerate(documents) if item['name'] == name),
        -1
    )
    if document_idx < 0:
        raise ValueError(f'there are no objects named {name} in the document collection')
    return document_idx
