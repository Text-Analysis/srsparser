from pymorphy2 import MorphAnalyzer
from gensim.utils import simple_preprocess
from gensim.corpora.dictionary import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from numpy import around

from srsparser import configs
from srsparser.sections_tree import SectionsTree

morph = MorphAnalyzer()


def remove_stop_words(words: list) -> list:
    """
    Удаляет стоп-слова из списка слов.

    :param words: список слов.
    :return: список слов без стоп-слов.
    """
    return list(filter(lambda token: token not in configs.STOPWORDS_RU, words))


def lemmatize(words: list) -> list:
    """
    Приводит каждое слово из списка слов к его лемме.

    :param words: список слов.
    :return: список лемм.
    """
    return list(map(lambda token: morph.normal_forms(token)[0], words))


def exclude_all_except(words: list, part_of_speech: str) -> list:
    """
    Исключает из списка слов все части речи, кроме заданной.

    :param words: список слов.
    :param part_of_speech: сокращённое название части речи на английском языке
        (см. Обозначения для граммем в pymorphy2).
    :return: список слов, содержащий слова одной части речи (part_of_speech).
    """
    return list(filter(lambda word: morph.parse(word)[0].tag.POS == part_of_speech, words))


def tokenize(text: str, part_of_speech="") -> list:
    """
    Предобработка текста: приводит текст к списку токенов.

    Если указан параметр part_of_speech, то при предобработке текста будут исключены все части речи,
    кроме part_of_speech.

    :param text: текст.
    :param part_of_speech: сокращённое название части речи на английском языке
        (см. Обозначения для граммем в pymorphy2).
    :return: список токенов.
    """
    tokens = simple_preprocess(text, min_len=2, max_len=50, deacc=True)
    tokens = remove_stop_words(tokens)
    tokens = lemmatize(tokens)
    if part_of_speech != "":
        tokens = exclude_all_except(tokens, part_of_speech)
    return tokens


# take second element for sort
def takeSecond(elem):
    return elem[1]


def get_tf_idf_weights(structures: list, section_name="Техническое задание", part_of_speech="") -> list:
    """
    Возвращает TF-IDF веса слов для содержимого структур: для каждой структуры "вытаскивает" из разделов текстовое
    содержимое, предобрабатывает его, строит модель TF-IDF и возвращает веса.

    :param structures: список структур ТЗ, листовые разделы которых заполнены содержимым соответствующих текстовых
        документов с ТЗ, взятых из коллекции с результатами парсинга.
    :param section_name: название раздела структуры ТЗ, относительно которого будет выделяться содержимое из каждой
        структуры ТЗ. По умолчанию имеет значение "Техническое задание", так как этот раздел является корневым и
        содержит в себе все разделы структуры ТЗ, но если указать другой раздел, то для анализа будет использоваться
        информация, содержащаяся только в этих разделах данных структур (structures).
    :param part_of_speech: сокращённое название части речи на английском языке (см. Обозначения для граммем в
        pymorphy2). По умолчанию является пустой строкой, поэтому при анализе учитываются все части речи содержимого
        структур с ТЗ, но если указать аббревиатуру конкретной части речи, то из содержимого при предобработке текста
        будут исключены все части речи, кроме данной.
    :return: TF-IDF веса слов для данных структур.
    """
    tokenized = []
    for structure in structures:
        # получаем наполнение структуры (совокупность содержимого всех полей text)
        doc_structure = SectionsTree(structure)
        structure_contents = doc_structure.get_content(section_name)

        # преобразование каждого наполнения структуры в список токенов
        tokenized.append(tokenize(structure_contents, part_of_speech))

    # сохранение извлеченных токенов в словарь
    dictionary = Dictionary(tokenized)

    # преобразование словаря в корпус (собрание документов в виде мешка слов)
    bow_corpus = [dictionary.doc2bow(doc, allow_update=True) for doc in tokenized]

    # TF-IDF веса слов для всех документов (слова, которые часто встречаются в документах, будут понижены в весе)
    tf_idf = TfidfModel(bow_corpus, smartirs="ltc")
    result = []
    for structure in tf_idf[bow_corpus]:
        structure.sort(key=takeSecond, reverse=True)
        weight_tf_idf = []
        for id, freq in structure:
            weight_tf_idf.append([dictionary[id], around(freq, decimals=3)])
        result.append(weight_tf_idf)
    return result


def strings_similarity(s1: str, s2: str) -> float:
    """
    Возвращает коэффициент сходимости строк `s1` и `s2`.

    :return: 0.0 — полностью раздичны, 1.0 — одинаковы.
    """
    s1_list = tokenize(s1)
    s2_list = tokenize(s2)

    if not s1_list or not s2_list:
        return 0.0

    l1 = []
    l2 = []

    s1_set = {w for w in s1_list}
    s2_set = {w for w in s2_list}

    # формируется словарь
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
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine
