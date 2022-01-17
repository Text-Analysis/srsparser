from nltk import download, corpus

# регулярное выражение для определения элемента нумерации в строке
NUMBERING_PATTERN = "^([а-я0-9][.) ])+"

# минимальный приемлимый коэффициент сходимости двух строк для того, чтобы считать их похожими
MIN_SIMILARITY_RATIO = 0.5

download("stopwords", quiet=True)
STOPWORDS_RU = corpus.stopwords.words("russian")

SPECIAL_CHARS = "!#$%&'()*+,/;<=>?@[\]^_`{|}~—\"\-."
EXCESS_CHARS = f"[A-Za-z0-9{SPECIAL_CHARS}]+"
