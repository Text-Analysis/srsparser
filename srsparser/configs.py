import string

from nltk import download, corpus

# regular expression for detection numbering elements
NUMBERING_PATTERN = '^([а-я\d][.) ])+'

# minimal strings similarity ratio
MIN_SIMILARITY_RATIO = 0.5

download('stopwords', quiet=True)
STOPWORDS_RU = corpus.stopwords.words('russian')

EXCESS_CHARS = f'[\w\d{string.punctuation}]+'
