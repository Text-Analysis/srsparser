from typing import List

import emoji
from gensim.corpora.dictionary import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.utils import simple_preprocess
from numpy import around
from pullenti.Sdk import Sdk
from pullenti.ner.ProcessorService import ProcessorService
from pullenti.ner.SourceOfAnalysis import SourceOfAnalysis
from pullenti.ner.keyword.KeywordAnalyzer import KeywordAnalyzer
from pullenti.ner.keyword.KeywordReferent import KeywordReferent
from pullenti.ner.keyword.KeywordType import KeywordType
from pymorphy2 import MorphAnalyzer

from srsparser import configs
from srsparser.sections_tree import SectionsTree
from srsparser.database import get_mongo_obj_with_structure_idx


class NLProcessor:
    """
    A class containing natural language processing methods, such as getting keywords, building a TF-IDF model,
    determining the similarity of strings, and others.
    """

    def __init__(self, init_pullenti=True):
        """
        :param init_pullenti: is it necessary to initialize the pullenti SDK.
        """
        self.morph = MorphAnalyzer()

        if init_pullenti:
            Sdk.initialize_all()

    @staticmethod
    def remove_ru_stop_words(words: List[str]) -> List[str]:
        """
        Removes russian stopwords from word list.

        :param words: word list.
        :return: word list without russian stopwords.
        """
        return list(filter(lambda token: token not in configs.STOPWORDS_RU, words))

    def get_normal_form(self, word: str) -> str:
        """
        Return a word normal form.
        """
        return self.morph.normal_forms(word)[0]

    def lemmatize(self, words: List[str]) -> List[str]:
        """
        Converts word list to lemma list.

        :param words: word list.
        :return: lemma list.
        """
        return list(map(lambda token: self.get_normal_form(token), words))

    def exclude_all_except(self, words: List[str], part_of_speech: str) -> List[str]:
        """
        Excludes all parts of speech except `part_of_speech` from word list.

        :param words: word list.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: word list containing only words belonging to part_of_speech.
        """
        return list(filter(lambda word: self.morph.parse(word)[0].tag.POS == part_of_speech, words))

    def tokenize(self, text: str, part_of_speech='') -> List[str]:
        """
        Converts text to token list using NLP algorithms.

        If parameter `part_of_speech` is stated,
        then during text preprocessing all parts of speech, except `part_of_speech`, will be excluded.

        :param text: text.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: token list.
        """
        tokens = simple_preprocess(text, min_len=2, max_len=50, deacc=True)
        tokens = self.remove_ru_stop_words(tokens)
        tokens = self.lemmatize(tokens)
        if part_of_speech != '':
            tokens = self.exclude_all_except(tokens, part_of_speech)
        return tokens

    def strings_similarity(self, s1: str, s2: str) -> float:
        """
        Calculates strings similarity ratio for `s1` and `s2`.

        :return: 0.0 — completely separate, 1.0 — equals.
        """
        s1_list = self.tokenize(s1)
        s2_list = self.tokenize(s2)

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

    def get_tf_idf_weights(self, documents: List[str], part_of_speech='') -> list:
        """
        Builds TF-IDF model for the documents and returns TF-IDF weights.

        If parameter `part_of_speech` is stated, then during text preprocessing all parts of speech,
        except `part_of_speech`, will be excluded from the documents.

        :param documents: text units, for example, a word, phrase, sentence.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: TF-IDF weight list for the documents.
        """
        # tokenize the documents
        tokenized = [self.tokenize(document, part_of_speech) for document in documents]

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

    def get_structures_tf_idf_weights(self, mongo_documents: List[dict],
                                      section_name=configs.ROOT_SRS_SECTION_NAME,
                                      part_of_speech='') -> list:
        """
        Builds TF-IDF model for the SRS structures content and returns TF-IDF weights. Structures are contained in
        MongoDB collection objects (`mongo_documents`) and are accessible by the key `structure`.

        :param mongo_documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param section_name: the name of the section of the SRS structure,
            relative to which the content will be selected from each SRS structure from mongo_documents.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: TF-IDF weight list for the SRS structures.
        """
        structures_contents: List[str] = []

        for document in mongo_documents:
            structure = SectionsTree(document['structure'])
            structure_content = structure.get_content(section_name)
            structures_contents.append(structure_content)

        return self.get_tf_idf_weights(structures_contents, part_of_speech)

    def get_structure_tf_idf_weights(self, mongo_documents: List[dict], structure_doc_name: str,
                                     section_name=configs.ROOT_SRS_SECTION_NAME, part_of_speech='') -> list:
        """
        Returns TF-IDF weights for the SRS structure that is contained among the objects of the MongoDB collection
        (`mongo_documents`) and has the name `structure_doc_name` (the name of the document from which the structure
        was derived).

        :param mongo_documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param structure_doc_name: the name of the document from which the SRS structure was extracted.
        :param section_name: the name of the section of the SRS structure, relative to which the content will be
            selected from each SRS structure from mongo_documents.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: TF-IDF weight list for the SRS structure corresponding to the MongoDB document with name
            structure_doc_name.
        """
        structure_doc_idx = next(
            (i for i, item in enumerate(mongo_documents) if item['document_name'] == structure_doc_name),
            -1
        )
        if structure_doc_idx < 0:
            raise ValueError(f'there are no objects named {structure_doc_name} in the MongoDB collection')

        all_structures_weights = self.get_structures_tf_idf_weights(mongo_documents, section_name, part_of_speech)
        return all_structures_weights[structure_doc_idx]

    def get_structure_keywords_tf_idf(self, mongo_documents: List[dict], structure_doc_name: str,
                                      section_name=configs.ROOT_SRS_SECTION_NAME, part_of_speech='') -> List[str]:
        """
        Returns keywords obtained from analyzing the contents of a structure with the name `structure_doc_name`
        relative to all transmitted `mongo_documents` by constructing a TF-IDF model and obtaining TF-IDF weights.

        :param mongo_documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param structure_doc_name: the name of the document from which the SRS structure was extracted.
        :param section_name: the name of the section of the SRS structure, relative to which the content will be
            selected from each SRS structure from mongo_documents.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: keyword list.
        """
        return [tf_idf_weight for tf_idf_weight in
                self.get_structure_tf_idf_weights(mongo_documents, structure_doc_name, section_name, part_of_speech)]

    def get_structure_keywords_pullenti(self, mongo_documents: List[dict], structure_doc_name: str,
                                        section_name=configs.ROOT_SRS_SECTION_NAME) -> List[str]:
        """
        Returns keywords obtained from analyzing the contents of a `structure` by using pullenti package
        (KeywordAnalyzer).

        :param mongo_documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param structure_doc_name: the name of the document from which the SRS structure was extracted.
        :param section_name: the name of the section of the SRS structure, relative to which the content will be
            selected from each SRS structure from mongo_documents.
        :return: keyword list.
        """
        structure_doc_idx = get_mongo_obj_with_structure_idx(mongo_documents, structure_doc_name)
        sections_structure = SectionsTree(mongo_documents[structure_doc_idx]['structure'])
        content = sections_structure.get_content(section_name)
        return self.get_keywords_pullenti(content)

    def get_keywords_pullenti(self, text: str) -> List[str]:
        """
        Returns keywords obtained from analyzing the contents of a `text`
        by using pullenti package (KeywordAnalyzer).

        :param text: processing text.
        :return: keyword list.
        """
        text_without_emoji = emoji.get_emoji_regexp().sub(u'', text)

        keywords: List[str] = []
        with ProcessorService.create_specific_processor(KeywordAnalyzer.ANALYZER_NAME) as proc:
            ar = proc.process(SourceOfAnalysis(text_without_emoji), None, None)
            for e0_ in ar.entities:
                if isinstance(e0_, KeywordReferent) and e0_.typ != KeywordType.ANNOTATION:
                    keywords.append(e0_.to_string(short_variant=True))
        return keywords

    def get_structure_keywords_with_ratios(self, mongo_documents: List[dict],
                                           structure_doc_name: str,
                                           section_name=configs.ROOT_SRS_SECTION_NAME,
                                           part_of_speech='') -> list:
        """
        Returns a list of keywords extracted from the SRS structure and the TF-IDF weights corresponding to them.

        :param mongo_documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param structure_doc_name: the name of the document from which the SRS structure was extracted.
        :param section_name: the name of the section of the SRS structure, relative to which the content will be
            selected from each SRS structure from mongo_documents.
        :param part_of_speech: part of speech acronym (see notation for grammem in pymorphy2 package).
        :return: list of pairs "keyword-ratio".
        """
        structure_doc_idx = get_mongo_obj_with_structure_idx(mongo_documents, structure_doc_name)
        sections_structure = SectionsTree(mongo_documents[structure_doc_idx]['structure'])
        content = sections_structure.get_content(section_name)

        structure_keywords = self.get_keywords_pullenti(content)

        all_structures_weights = self.get_structures_tf_idf_weights(mongo_documents, section_name, part_of_speech)
        structure_weights = all_structures_weights[structure_doc_idx]

        keywords_with_ratios = []
        for keyword in structure_keywords:
            # проверка, элемент является словом или словосочетанием
            keyphrase_words = keyword.split()
            if len(keyphrase_words) > 1:  # словосочетание
                tf_idf_sum = 0.0
                # проход по словам ключевого словосочетания
                for word in keyphrase_words:
                    # лемматизируем слово (получаем его нормальную форму)
                    normal_word = self.get_normal_form(word)
                    for tf_idf_weight in structure_weights:
                        # если для ключевого слова нашёлся его TF-IDF вес
                        if normal_word == tf_idf_weight[0]:
                            tf_idf_sum += tf_idf_weight[1]
                            break
                if tf_idf_sum > 0.0:
                    keywords_with_ratios.append([keyword, tf_idf_sum])
            else:  # слово
                # лемматизируем слово (получаем его нормальную форму)
                normal_word = self.get_normal_form(keyword)
                # проход по TF-IDF весам слов всех комментариев
                # (список, в котором каждый элемент представлен списком пар "слово-вес")
                for tf_idf_weight in structure_weights:
                    # если для ключевого слова нашёлся его TF-IDF вес
                    if normal_word == tf_idf_weight[0]:
                        keywords_with_ratios.append([keyword, tf_idf_weight[1]])
                        break

        keywords_with_ratios.sort(key=lambda item: item[1], reverse=True)

        return keywords_with_ratios
