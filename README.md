<h1>Semi-structured document parser</h1>

srsparser is a library that translates semi-structured text documents (files with .docx extension) into a structured
form in accordance with JSON templates and contains natural language processing algorithms to analyze the resulting
structures.

## The main idea

Let's consider the application of this library on the example of the technical assignment for developing of automated
system.

Based on the structure of the technical assignment described in
the [GOST standard 34.602-89](http://protect.gost.ru/default.aspx/document1.aspx?control=31&baseC=6&page=0&month=4&year=-1&search=&id=241754)
the necessary sections are selected, and on their basis the tree structure of sections is compiled in JSON format. Each
section is represented by name and content (children — if it has subsections, otherwise — text). This step is done
manually.

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
      "text": "Полное наименование системы и ее условное обозначение: Конфигурация «Бухгалтерия предприятия» в среде «1С: Предприятие 8.1»....",
      "name": "Общие сведения"
    },
    {
      "text": "Подсистема оперативного учета должна содержать механизмы...",
      "name": "Назначение и цели создания (развития) системы"
    },
    {
      "text": "Объектом автоматизации является процесс учета расчетов с работниками по оплате труда в организации...",
      "name": "Характеристика объектов автоматизации"
    },
    {
      "name": "Требования к системе",
      "children": [
        {
          "name": "Требования к системе в целом",
          "children": [
            {
              "text": "Для наиболее эффективного функционирования системы помимо пользователя...",
              "name": "Требования к численности и квалификации персонала системы и режиму его работы"
            },
            {
              "text": "Система должна предусматривать возможность масштабирования по производительности...",
              "name": "Показатели назначения"
            },
            {
              "text": "Система должна сохранять работоспособность и обеспечивать восстановление своих функций при возникновении следующих внештатных ситуаций...",
              "name": "Требования к защите от влияния внешних воздействий"
            }
          ]
        },
        {
          "text": "Подсистема оперативного учета должна осуществлять ввод и хранение оперативных данных системы...",
          "name": "Требования к функциям (задачам)"
        },
        {
          "name": "Требования к видам обеспечения",
          "children": [
            {
              "text": "Не предъявляются;",
              "name": "Требования к математическому обеспечению"
            },
            {
              "text": "Уровень хранения данных в системе должен быть построен на основе современных СУБД...",
              "name": "Требования к информационному обеспечению"
            },
            {
              "text": "Система создана на основе языка программирования «1С 8.1»;",
              "name": "Требования к лингвистическому обеспечению"
            },
            {
              "text": "Для эффективного функционирования системы помимо пользователя необходим специалист по технической поддержке...",
              "name": "Требования к метрологическому обеспечению"
            },
            {
              "text": "Для эффективного функционирования системы помимо пользователя необходим специалист по технической поддержке...",
              "name": "Требования к организационному обеспечению"
            },
            {
              "text": "Для обеспечения целостности данных должны использоваться встроенные механизмы СУБД...",
              "name": "Требования к методическому обеспечению"
            }
          ]
        }
      ]
    },
    {
      "text": "Перечень стадий и этапов работ, а так же сроки их исполнения представлены в Таблице 2...",
      "name": "Состав и содержание работ по созданию системы"
    },
    {
      "text": "Приемочные испытания должны включать проверку: полноты и качества реализации необходимых функций...",
      "name": "Порядок контроля и приемки системы"
    },
    {
      "text": "Для подготовки объекта автоматизации к вводу системы в действие необходимо при помощи специалиста технической поддержки...",
      "name": "Требования к составу и содержанию работ по подготовке объекта автоматизации к вводу системы в действие"
    },
    {
      "text": "Разработке подлежит следующая документация: Инструкция пользователю; Инструкция программисту.",
      "name": "Требования к документированию"
    }
  ]
}
```

The last step is to save the filled template in JSON format in order to access the necessary sections of the technical
assignment without spending time searching for relevant information.

## Preparing

Create the tree structure of sections in JSON format. The created JSON will act as a template. The required element is
the root element, so make sure that the entire structure is contained inside the children field of the root element.

```
{
  "root element name": "root",
  "children": [
    *here is the sections*
  ]
}
```

## Installation

To install srsparser:

`pip install srsparser`

To update srsparser:

`pip install srsparser --upgrade`

## Usage

### Parser

```python
import json

from srsparser import Parser

TEMPLATE_PATH = "/path/to/template.json"

# read the template (a JSON file created at the preparation stage)
with open(TEMPLATE_PATH, encoding="UTF-8") as f:
    template = json.load(f)

DOCX_PATH = "/path/to/doc1.docx"

parser = Parser(template)
structure = parser.parse_docx(DOCX_PATH)

print(structure)
# Output:
# {
#   'name': 'Техническое задание',
#   'children': [
#     {
#       'text': 'Полное наименование системы и ее условное обозначение...',
#       'name': 'Общие сведения'
#     },
#     {
#       'name': 'Требования к системе',
#       'children': [
#         {
#           'name': 'Требования к системе в целом',
#           'children': [
#             {
#               'text': 'Для наиболее эффективного функционирования системы помимо пользователя...',
#               'name': 'Требования к численности и квалификации персонала системы и режиму его работы'
#             },
#             ...
#           ]
#         },
#         ...
#       ]
#     },
#     ...
#   ]
# }
```

### LanguageProcessor

```python
import json

from srsparser import Parser, LanguageProcessor, SectionsTree

TEMPLATE_PATH = "/path/to/template.json"  # see the main idea section (README.md) for example

# read the template (a JSON file created at the preparation stage)
with open(TEMPLATE_PATH, encoding="UTF-8") as f:
    template = json.load(f)

parser = Parser(template)

parsed_documents = []
for docx_path in ["/path/to/doc1.docx", "/path/to/doc2.docx", "/path/to/doc2.docx"]:
    structure = parser.parse_docx(docx_path)
    parsed_documents.append({
        "document_name": docx_path,
        "structure": structure
    })

# a class that contains NLP methods.
# when reused, you may not initialize pullenti: LanguageProcessor(init_pullenti=False)
langproc = LanguageProcessor()

# KEYWORD EXTRACTION (using the pullenti library)
# ======================================================================================================================
# 1. extract keywords from a specific section of the selected structure
keywords = langproc.get_structure_keywords_pullenti(documents=parsed_documents,
                                                    document_name=parsed_documents[1]["document_name"],
                                                    section_name="Общие сведения")  # default: root section
print(keywords)
# Output:
# ['РАБОЧИЙ', 'ПОЛНОЕ НАИМЕНОВАНИЕ СИСТЕМЫ', 'АВТОМАТИЗИРОВАННОЕ РАБОЧЕЕ МЕСТО', 'ОКОНЧАНИЕ РАБОТ', 'СИСТЕМА',
# 'ПЛАНОВЫЙ СРОК НАЧАЛА', 'Ульяновск', 'ЗАКАЗЧИК', 'ПОЛНОЕ НАИМЕНОВАНИЕ', 'ПРОДАВЕЦ-КОНСУЛЬТАНТ',
# 'НАИМЕНОВАНИЕ', 'ШИФР ТЕМЫ', 'ПРЕДПРИЯТИЕ', 'НАИМЕНОВАНИЕ ПРЕДПРИЯТИЯ', 'ЗАКАЗЧИК СИСТЕМЫ', 'ПЛАНОВЫЙ СРОК', ...]

# 2. extract keywords from the text (to read the contents of the structure, the SectionsTree data structure is used)
tree = SectionsTree(parsed_documents[1]["structure"])
structure_contents = tree.get_content(section_name="Характеристика объектов автоматизации")  # default: root section
keywords = langproc.get_keywords_pullenti(structure_contents)
print(keywords)
# Output:
# ['ТОРГОВЫЙ ЗАЛ САЛОНА', 'СИСТЕМА', 'ОБЪЕКТ АВТОМАТИЗАЦИИ', 'ТОРГОВЫЙ ЗАЛ', 'ПРОДАЖА ФОТОТОВАРОВ', 'РЕАЛИЗАЦИЯ УСЛУГ',
# 'ТРЕБОВАНИЕ', 'ФУНКЦИОНИРОВАНИЕ СИСТЕМЫ', 'ПРОГРАММНЫЙ ПРОДУКТ', 'ЕДИНАЯ СИСТЕМА', 'МОНОПОЛЬНЫЙ РЕЖИМ', 'ОБЪЕКТ',
# 'АВТОМАТИЗАЦИЯ', 'ТОРГОВЫЙ', 'ЗАЛ', 'САЛОН', 'ФОТОУСЛУГА', 'ОСУЩЕСТВЛЯТЬ', 'ПРОДАЖА', 'ФОТОТОВАРЫ', ...]
# ======================================================================================================================

# TF-IDF PAIRS EXTRACTION (using the gensim library)
# ======================================================================================================================
# 1. extract pairs of words and their corresponding TF-IDF weights from a specific section of the selected structure
pairs = langproc.get_structure_tf_idf_pairs(documents=parsed_documents,
                                            document_name=parsed_documents[0]["document_name"],
                                            section_name="Требования к функциям (задачам)",  # default: root section
                                            part_of_speech="NOUN",  # default: all parts of speech
                                            smartirs="ntc")  # default: ntc (see: SMART Information Retrieval System)
print(pairs)
# Output:
# [['документ', 0.313], ['диск', 0.242], ['жесткия', 0.242], ['просмотр', 0.242], ['список', 0.242],
# ['удаление', 0.242], ['установка', 0.242], ['учёт', 0.205], ['мбаит', 0.179], ['основа', 0.16], ['процессор', 0.134],
# ['сервер', 0.134], ['субд', 0.134], ['бухгалтер', 0.121], ['версия', 0.121], ['главное', 0.121], ...]

# 2. extract pairs of words and their corresponding TF-IDF weights of all documents
documents = [
    "Подсистема оперативного учета должна содержать механизмы, позволяющие вводить в систему и хранить в ней "
    "информацию о текущей деятельности организации.",
    "Объектом автоматизации является процесс учета расчетов с работниками по оплате труда в организации, имеющей "
    "специфические принципы формирования расчетных сумм, в части расчета этих сумм и сбора данных из документов "
    "оперативного учета для проведения расчета.",
    "Система должна сохранять работоспособность и обеспечивать восстановление своих функций при возникновении "
    "внештатных ситуаций."
]
pairs = langproc.get_tf_idf_pairs(documents=documents,
                                  part_of_speech="ADJF",  # default: all parts of speech
                                  smartirs="lfc")  # default: ntc (see: SMART Information Retrieval System)
print(pairs)
# Output:
# [[['текущей', 0.887], ['должный', 0.327], ['оперативный', 0.327]], [['расчётный', 0.565], ['специфический', 0.565], 
# ['этот', 0.565], ['оперативный', 0.208]], [['внештатный', 0.684], ['свой', 0.684], ['должный', 0.253]]]

# 3. extract pairs of keywords and their corresponding TF-IDF weights
pairs = langproc.get_structure_rationized_keywords(documents=parsed_documents,
                                                   document_name=parsed_documents[2]["document_name"],
                                                   section_name="Требования к системе",  # default: root section
                                                   smartirs="dnu")  # default: ntc
print(pairs)
# Output:
# [['ЭФФЕКТИВНОЕ ФУНКЦИОНИРОВАНИЕ СИСТЕМЫ', 0.023], ['ИМЕЮЩИЙ НАВЫК РАБОТЫ', 0.023],
# ['ТЕХНИЧЕСКАЯ ХАРАКТЕРИСТИКА КОМПЬЮТЕРА', 0.022], ['СОСТАВ МЕТОДИЧЕСКОГО ОБЕСПЕЧЕНИЯ', 0.021],
# ['КОМПЬЮТЕР КОНЕЧНОГО ПОЛЬЗОВАТЕЛЯ', 0.0209], ['НЕСКОЛЬКО НЕЗАВИСИМЫЙ ПРОЕКТ', 0.02], ... ]
# ======================================================================================================================

# OTHER FEATURES
# ======================================================================================================================
# 1. string similarity
ratio = langproc.strings_similarity(documents[0], documents[1])
print(ratio)
# Output:
# 0.16151457061744964

# 2. sentence segmentation (using rusenttokenize)
sentences = langproc.sentenize(" ".join(documents))
print(sentences)
# Output:
# ['Подсистема оперативного учета должна содержать механизмы,
#   позволяющие вводить в систему и хранить в ней информацию о текущей деятельности организации',
#  'Объектом автоматизации является процесс учета расчетов с работниками по оплате труда в организации,
#   имеющей специфические принципы формирования расчетных сумм, в части расчета этих сумм и сбора данных из документов
#   оперативного учета для проведения расчета',
#  'Система должна сохранять работоспособность и обеспечивать восстановление своих функций при возникновении
#   внештатных ситуаций']

# 3. tokenization (using gensim)
tokens = langproc.tokenize(text=documents[0],
                           part_of_speech="NOUN")  # default: all parts of speech
print(tokens)
# Output:
# ['подсистема', 'учёт', 'механизм', 'система', 'нея', 'информация', 'деятельность', 'организация']

# 4. lemmatisation
words = ["Подсистема", "оперативного", "учета", "должна", "содержать", "механизмы", "позволяющие", "вводить", "систему",
         "хранить", "ней", "информацию", "текущей", "деятельности", "организации"]
lemmas = langproc.lemmatize(words)
print(lemmas)
# Output:
# ['подсистема', 'оперативный', 'учёт', 'должный', 'содержать', 'механизм', 'позволять', 'вводить', 'система', 
# 'хранить', 'она', 'информация', 'текущий', 'деятельность', 'организация']
# ======================================================================================================================
```

## References

- https://github.com/RaRe-Technologies/gensim
- https://github.com/pullenti/PullentiPython
- https://github.com/deepmipt/ru_sentence_tokenizer