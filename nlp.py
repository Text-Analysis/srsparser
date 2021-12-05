from re import sub
from pymorphy2 import MorphAnalyzer
from nltk import download, corpus

download("stopwords")

numbering_pattern = "^([а-я0-9][.) ])+"
special_characters = "!#$%&'()*+,/;<=>?@[\]^_`{|}~—\"\-."
strip_spec_char_pattern = f"(^[{special_characters} ]+)|([{special_characters} ]+$)"
patterns = f"[A-Za-z0-9{special_characters}]+"
stopwords_ru = corpus.stopwords.words("russian")
morph = MorphAnalyzer()


def lemmatize(s: str) -> list:
    """
    Replaces all the word forms in the string with the initial forms.
    """
    s = sub(patterns, "", s)
    tokens = []
    for token in s.split():
        if token and token not in stopwords_ru:
            token = token.strip()
            token = morph.normal_forms(token)[0]
            tokens.append(token)
    return tokens


def strings_similarity(s1: str, s2: str) -> float:
    """
    Determines the similarity coefficient of strings `s1` and `s2`.

    :return: 0.0 — completely dissimilar, 1.0 — equal.
    """
    # tokenization
    x_list = lemmatize(s1.lower())
    y_list = lemmatize(s2.lower())

    if not x_list or not y_list:
        return 0.0

    l1 = []
    l2 = []

    x_set = {w for w in x_list}
    y_set = {w for w in y_list}

    # form a set containing keywords of both strings
    rvector = x_set.union(y_set)
    for w in rvector:
        if w in x_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in y_set:
            l2.append(1)
        else:
            l2.append(0)

    c = 0
    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine
