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
the "
text" field of the corresponding section of the template.

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

2. Create the tree structure of sections in JSON format based on GOST standard 34.602-89 (
   see [the main idea block](https://github.com/Text-Analysis/srsparser/tree/master#the-main-idea))
   and save it into separate MongoDB collection:

```json
{
   "name": "default",
   "structure": "{here is the unfilled template}"
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

To structure the contents of a text document with the SRS:

`srsparser <text document path> <MongoDB connection string> <MongoDB database name> <name of MongoDB collection with the unfilled templates> <the unfilled template name> <name of MongoDB collection with the results>`

For example:

`srsparser "testdata\tz_10.docx" "mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/myFirstDatabase?retryWrites=true&w=majority" "documentsAnalysis" "templates" "default" "results"`

The command above means that a text document with path `testdata\tz_10.docx` will be analyzed according to the `default`
template taken from the `templates` collection, and the results will be placed in the `results` collection of the
database with connection string
equals `mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/myFirstDatabase?retryWrites=true&w=majority`.

*NOTE: srsparser processes only text documents with the .docx extension.*

## Usage as library

```python
from pymongo import MongoClient
from srsparser import SRSParser

MONGODB_URL = "mongodb+srv://tmrrwnxtsn:qwerty@srs.atqge.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
DB_NAME = "documentsAnalysis"
TMPL_COLL_NAME = "templates"
TMPL_NAME = "default"
RESULTS_COLL_NAME = "results"
DOCX_PATH = "testdata/tz_10.docx"

client = MongoClient(MONGODB_URL)
db = client[DB_NAME]

tmpl_coll = db[TMPL_COLL_NAME]
tree_template = tmpl_coll.find_one({'name': TMPL_NAME})['structure']

parser = SRSParser(tree_template)
document_structure = parser.parse_docx(DOCX_PATH)

results_coll = db[RESULTS_COLL_NAME]
results_coll.insert_one({'document_name': DOCX_PATH, 'structure': document_structure})

client.close()
```