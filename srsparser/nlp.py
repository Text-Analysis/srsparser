from pymorphy2 import MorphAnalyzer
from gensim.utils import simple_preprocess

from srsparser import configs

morph = MorphAnalyzer()


def remove_stop_words(words: list) -> list:
    """
    Remove stopwords from words.

    :param words: word list.
    :return: word list without stopwords.
    """
    return list(filter(lambda token: token not in configs.STOPWORDS_RU, words))


def lemmatize(words: list) -> list:
    """
    Brings each word to its normal dictionary form.

    :param words: word list.
    :return: lemmatized word list.
    """
    return list(map(lambda token: morph.normal_forms(token)[0], words))


def tokenize(doc: str) -> list:
    """
    Preprocessing of a text document to obtain a list of tokens.

    :param doc: some document.
    :return: token list.
    """

    tokens = simple_preprocess(doc, min_len=2, max_len=50, deacc=True)
    tokens = remove_stop_words(tokens)
    return lemmatize(tokens)


def strings_similarity(s1: str, s2: str) -> float:
    """
    Determines the similarity coefficient of strings `s1` and `s2`.

    :return: 0.0 — completely dissimilar, 1.0 — equal.
    """
    # tokenization
    s1_list = tokenize(s1)
    s2_list = tokenize(s2)

    if not s1_list or not s2_list:
        return 0.0

    l1 = []
    l2 = []

    s1_set = {w for w in s1_list}
    s2_set = {w for w in s2_list}

    # form a set containing keywords of both strings
    rvector = s1_set.union(s2_set)
    for w in rvector:
        if w in s1_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in s2_set:
            l2.append(1)
        else:
            l2.append(0)

    c = 0
    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine
