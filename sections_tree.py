from anytree import AnyNode, PreOrderIter
from anytree.exporter import DictExporter


class Section(AnyNode):
    """
    A class representing a section of a text document.
    """

    def __init__(self, name: str, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.parent = parent
        if children:
            self.children = children


class SectionsTree:
    """
    A class representing a tree of sections of a text document.
    """

    def __init__(self):
        self.root = Section("Техническое задание", children=[
            Section("Общая информация", text=""),
            Section("Назначение и цели создания (развития) системы", text=""),
            Section("Характеристика объектов автоматизации", text=""),
            Section("Требования к системе", children=[
                Section("Требования к системе в целом", children=[
                    Section("Требования к структуре и функционированию системы", text=""),
                    Section("Требования к численности и квалификации персонала системы и режиму его работы", text=""),
                    Section("Показатели назначения", text=""),
                    Section("Требования к надежности", text=""),
                    Section("Требования безопасности", text=""),
                    Section("Требования к эргономике и технической эстетике", text=""),
                    Section("Требования к транспортабельности для подвижных АС", text=""),
                    Section(
                        "Требования к эксплуатации, техническому обслуживанию, ремонту и хранению компонентов системы",
                        text=""),
                    Section("Требования к защите информации от несанкционированного доступа", text=""),
                    Section("Требования по сохранности информации при авариях", text=""),
                    Section("Требования к защите от влияния внешних воздействий", text=""),
                    Section("Требования к патентной чистоте", text=""),
                    Section("Требования по стандартизации и унификации", text=""),
                    Section("Дополнительные требования", text="")
                ]),
                Section("Требования к функциям (задачам), выполняемым системой", text=""),
                Section("Требования к видам обеспечения", text="")
            ]),
            Section("Состав и содержание работ по созданию системы", text=""),
            Section("Порядок контроля и приемки системы", text=""),
            Section("Требования к составу и содержанию работ по подготовке объекта автоматизации к вводу системы в "
                    "действие", text=""),
            Section("Требования к документированию", text=""),
            Section("Источники разработки", text="")
        ])

    def get_leaf_sections(self) -> list:
        return [node for node in PreOrderIter(self.root, filter_=lambda n: hasattr(n, "text"))]

    def get_sections(self) -> list:
        return [node for node in PreOrderIter(self.root, filter_=lambda n: not hasattr(n, "text"))]

    def get_dict_from_root(self) -> dict:
        exporter = DictExporter()
        return exporter.export(self.root)
