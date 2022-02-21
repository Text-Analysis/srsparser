<h1 align="center">Software requirements specifications (SRS) parser</h1>

srsparser is a command-line application written in Python that parses unstructured text documents (files with .docx
extension) with SRS in accordance
with [GOST standard 34.602-89](http://protect.gost.ru/default.aspx/document1.aspx?control=31&baseC=6&page=0&month=4&year=-1&search=&id=241754)
and saves the structured results to the MongoDB database.

## The main idea

Based on the structure described in the GOST standard, the necessary sections are selected, and on their basis the tree
structure of sections is compiled in JSON format. Each section is represented by name and content (children — if it has
subsections, otherwise — text).

The compiled section structure is transferred to the parser as a *template*. Example of the template:

```json
{
  "name": "Техническое задание",
  "children": [
    {
      "text": "",
      "name": "Общие сведения"
    },
    {
      "text": "",
      "name": "Назначение и цели создания (развития) системы"
    },
    {
      "text": "",
      "name": "Характеристика объектов автоматизации"
    },
    {
      "name": "Требования к системе",
      "children": [
        {
          "name": "Требования к системе в целом",
          "children": [
            {
              "text": "",
              "name": "Требования к структуре и функционированию системы"
            },
            {
              "text": "",
              "name": "Требования к численности и квалификации персонала системы и режиму его работы"
            },
            {
              "text": "",
              "name": "Показатели назначения"
            },
            {
              "text": "",
              "name": "Требования к надежности"
            },
            {
              "text": "",
              "name": "Требования к безопасности"
            },
            {
              "text": "",
              "name": "Требования к эргономике и технической эстетике"
            },
            {
              "text": "",
              "name": "Требования к транспортабельности для подвижных АС"
            },
            {
              "text": "",
              "name": "Требования к эксплуатации, техническому обслуживанию, ремонту и хранению компонентов системы"
            },
            {
              "text": "",
              "name": "Требования к защите информации от несанкционированного доступа"
            },
            {
              "text": "",
              "name": "Требования по сохранности информации при авариях"
            },
            {
              "text": "",
              "name": "Требования к защите от влияния внешних воздействий"
            },
            {
              "text": "",
              "name": "Требования к патентной чистоте"
            },
            {
              "text": "",
              "name": "Требования по стандартизации и унификации"
            },
            {
              "text": "",
              "name": "Дополнительные требования"
            }
          ]
        },
        {
          "text": "",
          "name": "Требования к функциям (задачам)"
        },
        {
          "name": "Требования к видам обеспечения",
          "children": [
            {
              "text": "",
              "name": "Требования к математическому обеспечению"
            },
            {
              "text": "",
              "name": "Требования к информационному обеспечению"
            },
            {
              "text": "",
              "name": "Требования к лингвистическому обеспечению"
            },
            {
              "text": "",
              "name": "Требования к программному обеспечению"
            },
            {
              "text": "",
              "name": "Требования к техническому обеспечению"
            },
            {
              "text": "",
              "name": "Требования к метрологическому обеспечению"
            },
            {
              "text": "",
              "name": "Требования к организационному обеспечению"
            },
            {
              "text": "",
              "name": "Требования к методическому обеспечению"
            }
          ]
        }
      ]
    },
    {
      "text": "",
      "name": "Состав и содержание работ по созданию системы"
    },
    {
      "text": "",
      "name": "Порядок контроля и приемки системы"
    },
    {
      "text": "",
      "name": "Требования к составу и содержанию работ по подготовке объекта автоматизации к вводу системы в действие"
    },
    {
      "text": "",
      "name": "Требования к документированию"
    },
    {
      "text": "",
      "name": "Источники разработки"
    }
  ]
}
```

The parser reads the contents of a text document and tries to detect in it exactly those sections that are present in
the template. If the text document contains content corresponding to a section of the template, then it is entered in
the "text" field of the corresponding section of the template.

After filling the template with the contents of a text document, sections with empty "text" fields are removed from it,
and the filled template is converted to JSON format. Example of the filled template in JSON format:

```json
{
  "name": "Техническое задание",
  "children": [
    {
      "text": "Полное наименование системы: Станция технического обслуживания автомобилей. Условное обозначение – СТО автомобилей.\nШифр темы или шифр (номер) договора: данный программный продукт разрабатывался в рамках выполнения должностных обязанностей в компании-заказчике...",
      "name": "Общие сведения"
    },
    {
      "text": "Автоматизация работы станции технического обслуживания;\nпредоставление удобных механизмов для работы мастеров-приемщиков и оформителей на станции;\nВозможность получения точной информации о работе станции, расчет прибыли (убытков) от работы станции...",
      "name": "Назначение и цели создания (развития) системы"
    },
    {
      "text": "Возможность модификации конфигурации предусмотрена самой платформой.\nСроки и порядок комплектования и обучения персонала...",
      "name": "Характеристика объектов автоматизации"
    },
    {
      "name": "Требования к системе",
      "children": [
        {
          "name": "Требования к системе в целом",
          "children": [
            {
              "text": "Перечень подсистем:\nОформление документов\nРабота с клиентами\nОтчетность\nПодсистема оформления документов должна представлять собой совокупность документов, оформляемых в процессе работы по каждой заявке...",
              "name": "Требования к структуре и функционированию системы"
            },
            {
              "text": "Пользователями разрабатываемой системы должны выступать:\nОформители\nМастер-приемщик\nМенеджер по работе с персоналом\nНачальник СТО...",
              "name": "Требования к численности и квалификации персонала системы и режиму его работы"
            },
            {
              "text": "Данная система должна быть гибкой в отношении изменения отчетов  и легко модернизироваться под изменяющиеся нужды станции технического обслуживания...",
              "name": "Показатели назначения"
            }
          ]
        },
        {
          "text": "Перечень подлежащих автоматизации задач:\nФиксирование заявок на ремонт, поступающих от клиентов.\nУчет данных о клиентах...",
          "name": "Требования к функциям (задачам)"
        },
        {
          "name": "Требования к видам обеспечения",
          "children": [
            {
              "text": "Реквизиты документов должны соответствовать требованиям, установленным Стандартом предприятия...",
              "name": "Требования к информационному обеспечению"
            },
            {
              "text": "Должен использоваться язык программирования «1С v8.1»...",
              "name": "Требования к лингвистическому обеспечению"
            },
            {
              "text": "Нет требований к данному виду обеспечения...",
              "name": "Требования к метрологическому обеспечению"
            },
            {
              "text": "Для функционирования системы необходимо минимум 2 человека: мастер-приемщик, осуществляющий ввод первичных данных в документы...",
              "name": "Требования к организационному обеспечению"
            }
          ]
        }
      ]
    },
    {
      "text": "Работы по созданию системы должны проводиться инженером-программистом...",
      "name": "Состав и содержание работ по созданию системы"
    },
    {
      "text": "Проверку каждой команды меню, панели инструментов и каждой операции, которую выполняет система...",
      "name": "Порядок контроля и приемки системы"
    },
    {
      "text": "Особых требований не предъявляется, поскольку все подготовки к вводу системы в действие были реализованы на этапе внедрения...",
      "name": "Требования к составу и содержанию работ по подготовке объекта автоматизации к вводу системы в действие"
    },
    {
      "text": "В состав программной документации должны входить следующие документы:\n- техническое задание...",
      "name": "Требования к документированию"
    },
    {
      "text": "Источниками разработки являются документы «Стандарт предприятия» для автосалонов...",
      "name": "Источники разработки"
    }
  ]
}
```

The last step is to save the filled template in JSON format in the MongoDB database in order to access the necessary
sections of the SRS without spending time searching for relevant information.

For convenience, the unfilled templates in JSON format are also saved into the MongoDB database, so as not to waste time
on their recreation.

## Preparing

1. Create [MongoDB](https://docs.mongodb.com/) database.

2. Create the tree structure of sections in JSON format based on GOST standard 34.602-89 and save it into separate
   MongoDB collection (see [the main idea block](https://github.com/Text-Analysis/srsparser/tree/master#the-main-idea)):

```
{
  "name": "default",
  "structure": {
  *here is the unfilled template*
  }
}
```

One collection is for the unfilled templates, and another is for the results.

## Installation

To install srsparser:

`pip install srsparser`

To update srsparser:

`pip install srsparser --upgrade`

Alternatively, you can clone the project and run the following command to install:

`git clone https://github.com/Text-Analysis/srsparser.git`

`python setup.py install`

*NOTE: Make sure you cd into the srsparser folder before performing the command above.*

## Usage

The parser has 2 modes of use: **parse** and **keywords**

### Parse mode

In this mode, the parser reads the contents of text documents with the SRS, structures it based on the structure
templates and stores it in the MongoDB database.

To structure the contents of a text document with the SRS:

`srsparser "parse" <MongoDB connection string (includes the name of the db)> <name of collection with the results> -tc <name of collection with the templates> -t <the template name> -dp <the text document path>`

*NOTE: Before using, make sure that the necessary template is in the MongoDB collection with templates.*

For example:

`srsparser "parse" "mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/documentsAnalysis?retryWrites=true&w=majority" "results" -tc "templates" -t "default" -dp "./data/srs_1.docx"`

The command above means that a text document with path `./data/srs_1.docx` will be analyzed according to the `default`
template taken from the `templates` collection, and the results will be placed in the `results` collection of the
database with connection string
equals `mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/documentsAnalysis?retryWrites=true&w=majority`.

*NOTE: srsparser processes only text documents with the .docx extension.*

### Keywords mode

In this mode, the parser uses some natural language processing methods (TF-IDF model
from [gensim](https://github.com/RaRe-Technologies/gensim) library, KeywordAnalyzer
from [pullenti](https://github.com/pullenti/PullentiPython) library, etc.) to get keywords of structured content from a
collection with results. The output is this table:

```
+---------------+--------------+
|     TF-IDF    |   Pullenti   |
+---------------+--------------+
|      узел     |   рабочий    |
|     заказ     |   система    |
|   справочник  |   заказчик   |
|    продавец   | программный  |
|   фотоуслуга  | пользователь |
|  центральный  |  выполнение  |
|     салон     |   операция   |
|     выдать    |   продавец   |
|    паролей    |  справочник  |
| производиться | консультант  |
+---------------+--------------+
```

To get a table of keywords of the section structure content:

`srsparser "keywords" <MongoDB connection string (includes the name of the db)> <name of collection with the results> -dn <document name from the resulting collection> -s <section name (if not explicitly specified, the contents of the root section ('Техническое задание') will be taken)>`

For example:

`srsparser "keywords" "mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/documentsAnalysis?retryWrites=true&w=majority" "results" -dn "srs_1" -s "Общие требования"`

The command above means that keywords will be obtained from the structure of sections with the name `srs_1` and from the
section `"Общие сведения"` using NLP algorithms and displayed in the form of a table. The structure is taken from the
resulting collection `results` of the database, which is available on the following connection
string: `mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/documentsAnalysis?retryWrites=true&w=majority`.

*NOTE: Before using, make sure that the necessary section structure is in the MongoDB collection with results.*

To show help message:

`srsparser --help`

## Usage as library

### Parse mode

```python
from os.path import basename, splitext

from pymongo import MongoClient

from srsparser import SRSParser

DOCX_PATH = './data/srs_1.docx'
MONGODB_URL = 'mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/documentsAnalysis?retryWrites=true&w=majority'
TMPL_COLL_NAME = 'templates'
TMPL_NAME = 'default'
RESULTS_COLL_NAME = 'results'

client = MongoClient(MONGODB_URL)
db = client.get_default_database()

tmpl_coll = db[TMPL_COLL_NAME]
template = tmpl_coll.find_one({'name': TMPL_NAME})['structure']

parser = SRSParser(template)
docx_structure = parser.parse_docx(DOCX_PATH)

document_name = splitext(basename(DOCX_PATH))[0]  # srs_1

results_coll = db[RESULTS_COLL_NAME]
results_coll.insert_one({'document_name': document_name, 'structure': docx_structure})

client.close()
```

### Keywords mode

```python
import sys

from pymongo import MongoClient
from prettytable import PrettyTable

from srsparser import NLProcessor

MONGODB_URL = 'mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/documentsAnalysis?retryWrites=true&w=majority'
RESULTS_COLL_NAME = 'results'
DOCX_NAME = 'srs_1'
SECTION_NAME = 'Техническое задание'

client = MongoClient(MONGODB_URL)
db = client.get_default_database()
results_coll = db[RESULTS_COLL_NAME]

results = list(results_coll.find({}))

docx_structure_idx = -1
for idx in range(len(results)):
   if results[idx]['document_name'] == DOCX_NAME:
      docx_structure_idx = idx
      break
if docx_structure_idx < 0:
   sys.exit(f'there is no such document in the results collection with document name "{DOCX_NAME}"')

nlp = NLProcessor(init_pullenti=True)

tf_idf_keywords = nlp.get_structure_keywords_tf_idf(
   structures=[result['structure'] for result in results],
   structure_idx=docx_structure_idx,
   section_name=SECTION_NAME
)

print(tf_idf_keywords)
# Output:
# ['бухгалтерский', 'подсистема', 'учёт', 'полнота', 'содержаться', 'рекомендоваться', 'элемент', 'восстановление',
# 'экранный', 'сумма', ...]

pullenti_keywords = nlp.get_structure_keywords_pullenti(
   structure=results[docx_structure_idx]['structure'],
   section_name=SECTION_NAME
)

print(pullenti_keywords)
# Output:
# ['система', 'операция', 'работа', 'пользователь', 'учет', 'intel (интел)', 'дать', 'подсистема', 'функционирование',
# 'элемент', ...]

keywords_table = PrettyTable()
keywords_table.add_column('TF-IDF', tf_idf_keywords)
keywords_table.add_column('Pullenti', pullenti_keywords)

print(keywords_table)
# Output:
# +-----------------+------------------+
# |      TF-IDF     |     Pullenti     |
# +-----------------+------------------+
# |  бухгалтерский  |     система      |
# |    подсистема   |     операция     |
# |       учёт      |      работа      |
# |     полнота     |   пользователь   |
# |   содержаться   |       учет       |
# | рекомендоваться |  intel (интел)   |
# |     элемент     |       дать       |
# |  восстановление |    подсистема    |
# |     экранный    | функционирование |
# |      сумма      |     элемент      |
# |      ...        |       ...        |
# +-----------------+------------------+
```