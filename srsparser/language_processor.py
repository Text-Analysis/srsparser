from typing import List, Tuple

import numpy
from regex import regex as re
import string

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
from rusenttokenize import ru_sent_tokenize

from srsparser import configs
from srsparser.sections_tree import SectionsTree
from srsparser.utils import get_document_idx_by_name


class LanguageProcessor:
    """
    A class containing natural language processing methods, such as getting keywords, building a TF-IDF model,
    determining the similarity of strings, and others.
    """

    def __init__(self, init_pullenti=True):
        """
        :param init_pullenti: is it necessary to initialize the pullenti SDK.
        """
        self.morph = MorphAnalyzer()

        # regular expressions for text preprocessing
        self.newlines_pattern = re.compile(r'\n')  # search for newlines
        self.spaces_pattern = re.compile(r'\s{2,}')  # search for 2 or more spaces
        self.semicolons_pattern = re.compile(r'(;|\.+)')  # search for semicolons and dots

        # search for punctuation marks at the beginning and end of a line
        self.punct_on_sides_pattern = re.compile(fr'(^[{string.punctuation}–]+|[{string.punctuation}–]+$)')

        # search for punctuation marks that are not at the beginning and not at the end (between spaces)
        self.punct_in_middle_pattern = re.compile(fr'\s+[{string.punctuation}–]+\s+')

        # search for occurrences of a substring in which there is no space between the punctuation mark and
        # the next character after it ("...1С:Предприятия...")
        self.punct_solid_pattern = re.compile(fr'([.,:;–])([А-ЯЁа-яёA-Za-z])')

        # text with a punctuation mark at the end
        self.punct_at_end_pattern = re.compile(fr'.+[{string.punctuation}]$')

        if init_pullenti:
            Sdk.initialize_all()

    def sentenize(self, text: str) -> List[str]:
        """
        Segmentation of text into sentences using rusenttokenize.

        :return: sentence list.
        """
        text = self.newlines_pattern.sub('. ', text)
        text = self.spaces_pattern.sub(' ', text)
        text = self.semicolons_pattern.sub('.', text)

        sentences: List[str] = []

        for sentence in ru_sent_tokenize(text):
            # if there are at least 3 words in the sentence
            if len(re.findall(r'\w+', sentence)) >= 3:
                sentence = self.punct_on_sides_pattern.sub('', sentence)
                sentence = self.punct_in_middle_pattern.sub(' ', sentence)
                sentence = self.punct_solid_pattern.sub(r'\1 \2', sentence)
                sentences.append(sentence)

        return sentences

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
        Converts text to token list.

        If parameter `part_of_speech` is stated,
        then during text preprocessing all parts of speech, except `part_of_speech`, will be excluded.

        :param text: text.
        :param part_of_speech: part of speech acronym.
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

    def get_tf_idf_pairs(self, documents: List[str], part_of_speech='',
                         smartirs='ntc') -> List[List[List[Tuple[str, numpy.float64]]]]:
        """
        Builds TF-IDF model for the documents and returns TF-IDF pairs.

        If parameter `part_of_speech` is stated, then during text preprocessing all parts of speech,
        except `part_of_speech`, will be excluded from the documents.

        :param documents: text units, for example, a word, phrase, sentence.
        :param part_of_speech: part of speech acronym.
        :param smartirs: three letters represents the term weighting of the collection document vector
            (e.g. 'ntc', see smart term-weighting triple notation)
        :return: TF-IDF pair ([word: str, weight: float]) list for the documents.
        """
        # tokenize the documents
        tokenized = [self.tokenize(document, part_of_speech) for document in documents]

        # make dictionary (unique token list)
        dictionary = Dictionary(tokenized)

        # convert the dictionary to bag of words
        bow_corpus = [dictionary.doc2bow(doc, allow_update=True) for doc in tokenized]

        tf_idf = TfidfModel(bow_corpus, smartirs=smartirs)

        tf_idf_weights = []
        for structure in tf_idf[bow_corpus]:
            structure.sort(key=lambda item: item[1], reverse=True)

            tf_idf_weight = []
            for id, freq in structure:
                tf_idf_weight.append([dictionary[id], numpy.float64(around(freq, decimals=3))])

            tf_idf_weights.append(tf_idf_weight)

        return tf_idf_weights

    def get_structure_tf_idf_pairs(self, documents: List[dict], document_name: str, section_name='',
                                   part_of_speech='', smartirs='ntc') -> List[List[Tuple[str, numpy.float64]]]:
        """
        Returns TF-IDF pairs for the document structure that is contained among the objects of the MongoDB collection
        (`documents`) and has the name `document_name` (the name of the document from which the structure was derived).

        :param documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param document_name: the name of the document from which the structure was extracted.
        :param section_name: the name of the section of the structure, relative to which the content will be
            selected from each structure from documents.
        :return: TF-IDF pair list for the structure corresponding to the MongoDB document with name `document_name`.
        """
        structure_idx = get_document_idx_by_name(documents, document_name)

        contents: List[str] = []
        for document in documents:
            structure = SectionsTree(document['structure'])
            structure_content = structure.get_content(section_name)
            contents.append(structure_content)

        all_structures_pairs = self.get_tf_idf_pairs(contents, part_of_speech, smartirs)
        return all_structures_pairs[structure_idx]

    def get_structure_keywords_pullenti(self, documents: List[dict], document_name: str,
                                        section_name='') -> List[str]:
        """
        Returns keywords obtained from analyzing the contents of a `structure`.

        :param documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param document_name: the name of the document from which the structure was extracted.
        :param section_name: the name of the section of the structure, relative to which the content will be
            selected from each structure from documents.
        :return: keyword list.
        """
        structure_doc_idx = get_document_idx_by_name(documents, document_name)
        sections_structure = SectionsTree(documents[structure_doc_idx]['structure'])
        content = sections_structure.get_content(section_name)
        return self.get_keywords_pullenti(content)

    @staticmethod
    def get_keywords_pullenti(text: str) -> List[str]:
        """
        Returns keywords obtained from analyzing the contents of a `text`.

        :return: keyword list.
        """
        keywords: List[str] = []
        with ProcessorService.create_specific_processor(KeywordAnalyzer.ANALYZER_NAME) as proc:
            ar = proc.process(SourceOfAnalysis(text), None, None)
            for e0_ in ar.entities:
                if isinstance(e0_, KeywordReferent) and e0_.typ != KeywordType.ANNOTATION:
                    keywords.append(e0_.to_string(short_variant=True))
        return keywords

    def get_structure_rationized_keywords(self, documents: List[dict], document_name: str,
                                          section_name='', smartirs='ntc') -> List[List[Tuple[str, numpy.float64]]]:
        """
        Returns a list of keywords extracted from the structure and the TF-IDF weights corresponding to them.

        :param documents: list of the MongoDB collection objects, each of which is represented by the parsed
            document (dictionary with the keys: _id, document_name and structure).
        :param document_name: the name of the document from which the structure was extracted.
        :param section_name: the name of the section of the structure, relative to which the content will be
            selected from each structure from documents.
        :param smartirs: three letters represents the term weighting of the collection document vector
            (e.g. 'ntc', see smart term-weighting triple notation)
        :return: list of pairs "keyword-ratio".
        """
        tf_idf_pairs = self.get_structure_tf_idf_pairs(documents, document_name, section_name, smartirs=smartirs)
        keywords = self.get_structure_keywords_pullenti(documents, document_name, section_name)

        keywords_with_ratios = []
        for keyword in keywords:
            # the element is a word or phrase
            keyphrase_words = keyword.split()
            if len(keyphrase_words) > 1:  # phrase
                tf_idf_sum = 0.0
                # passage according to the keyword phrase
                for word in keyphrase_words:
                    normal_word = self.get_normal_form(word)
                    for tf_idf_pair in tf_idf_pairs:
                        if normal_word == tf_idf_pair[0]:
                            tf_idf_sum += tf_idf_pair[1]
                            break
                if tf_idf_sum > 0:
                    keywords_with_ratios.append([keyword, tf_idf_sum])
            else:  # word
                normal_word = self.get_normal_form(keyword)
                # passing through TF-IDF word weights of all documents
                for tf_idf_pair in tf_idf_pairs:
                    if normal_word == tf_idf_pair[0]:
                        keywords_with_ratios.append([keyword, tf_idf_pair[1]])
                        break
        keywords_with_ratios.sort(key=lambda item: item[1], reverse=True)
        return keywords_with_ratios
