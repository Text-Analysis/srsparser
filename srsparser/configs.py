from nltk import download, corpus

# regular expression for detection numbering elements
NUMBERING_PATTERN = '^([а-я0-9][.) ])+'

# minimal strings similarity ratio
MIN_SIMILARITY_RATIO = 0.5

download('stopwords', quiet=True)
STOPWORDS_RU = corpus.stopwords.words('russian')

SPECIAL_CHARS = "!#$%&'()*+,/;<=>?@[\]^_`{|}~—\"\-."
EXCESS_CHARS = f'[A-Za-z0-9{SPECIAL_CHARS}]+'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
    },

    'loggers': {
        'default': {
            'handlers': ['stream_handler'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

ROOT_SRS_SECTION_NAME = 'Техническое задание'
