from typing import List

from gensim.corpora.dictionary import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.utils import simple_preprocess
from numpy import around
from pymorphy2 import MorphAnalyzer

from srsparser import configs
from srsparser.sections_tree import SectionsTree

morph = MorphAnalyzer()


def remove_stop_words(words: List[str]) -> List[str]:
    """
    Removes stopwords from word list.

    :param words: word list.
    :return: word list without stopwords.
    """
    return list(filter(lambda token: token not in configs.STOPWORDS_RU, words))


def lemmatize(words: List[str]) -> List[str]:
    """
    Converts word list to lemma list.

    :param words: word list.
    :return: lemma list.
    """
    return list(map(lambda token: morph.normal_forms(token)[0], words))


def exclude_all_except(words: List[str], part_of_speech: str) -> List[str]:
    """
    Excludes all parts of speech except `part_of_speech` from word list.

    :param words: word list.
    :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
    :return: word list containing only words belonging to part_of_speech.
    """
    return list(filter(lambda word: morph.parse(word)[0].tag.POS == part_of_speech, words))


def tokenize(text: str, part_of_speech='') -> List[str]:
    """
    Converts text to token list using NLP algorithms.

    If parameter `part_of_speech` is stated,
    then during text preprocessing all parts of speech, except `part_of_speech`, will be excluded.

    :param text: text.
    :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
    :return: token list.
    """
    tokens = simple_preprocess(text, min_len=2, max_len=50, deacc=True)
    tokens = remove_stop_words(tokens)
    tokens = lemmatize(tokens)
    if part_of_speech != '':
        tokens = exclude_all_except(tokens, part_of_speech)
    return tokens


def get_tf_idf_weights(documents: List[str], part_of_speech='') -> list:
    """
    Builds TF-IDF model for the documents and returns TF-IDF weights.

    If parameter `part_of_speech` is stated,
    then during text preprocessing all parts of speech, except `part_of_speech`, will be excluded from the documents.

    :param documents: text units, for example, a word, phrase, sentence.
    :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
    :return: TF-IDF weight list for the documents.
    """
    # tokenize the documents
    tokenized = [tokenize(document, part_of_speech) for document in documents]

    # make dictionary (unique token list)
    dictionary = Dictionary(tokenized)

    # convert the dictionary to bag of words
    bow_corpus = [dictionary.doc2bow(doc, allow_update=True) for doc in tokenized]

    tf_idf = TfidfModel(bow_corpus, smartirs='ntc')

    tf_idf_weights = []
    for structure in tf_idf[bow_corpus]:
        structure.sort(key=lambda item: item[1], reverse=True)

        tf_idf_weight = []
        for id, freq in structure:
            tf_idf_weight.append([dictionary[id], around(freq, decimals=3)])

        tf_idf_weights.append(tf_idf_weight)

    return tf_idf_weights


def get_sections_tf_idf_weights(structures: List[dict], section_name='Техническое задание', part_of_speech='') -> list:
    """
    Builds TF-IDF model for the software requirements specifications (SRS) structures content
    and returns TF-IDF weights.

    If parameter `part_of_speech` is stated, then during text preprocessing all parts of speech,
    except `part_of_speech`, will be excluded from the structures content.

    :param structures: the SRS structure list, which were filled relevant text documents content.
    :param section_name: the name of the section of the SRS structure,
        relative to which the content will be allocated from each SRS structures.
    :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
    :return: TF-IDF weight list for the SRS structures.
    """
    documents: List[str] = []
    for structure in structures:
        doc_structure = SectionsTree(structure)
        structure_content = doc_structure.get_content(section_name)

        documents.append(structure_content)

    return get_tf_idf_weights(documents, part_of_speech)


def strings_similarity(s1: str, s2: str) -> float:
    """
    Calculates strings similarity ratio for `s1` and `s2`.

    :return: 0.0 — completely separate, 1.0 — equals.
    """
    s1_list = tokenize(s1)
    s2_list = tokenize(s2)

    if not s1_list or not s2_list:
        return 0.0

    l1 = []
    l2 = []

    s1_set = {w for w in s1_list}
    s2_set = {w for w in s2_list}

    rvector = s1_set.union(s2_set)
    for w in rvector:
        if w in s1_set:
            l1.append(1)
        else:
            l1.append(0)
        if w in s2_set:
            l2.append(1)
        else:
            l2.append(0)

    c = 0
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine_similarity_ratio = c / float((sum(l1) * sum(l2)) ** 0.5)

    return cosine_similarity_ratio
