from anytree import AnyNode, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter


class Section(AnyNode):
    """
    A class representing a section of a text document.
    """

    def __init__(self, name: str, idx=0, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.idx = idx
        self.parent = parent
        if children:
            self.children = children


class SectionsTree:
    """
    A class representing a sections_tree_skeleton of sections of a text document.
    """

    def __init__(self):
        self.root = Section("Техническое задание", idx=0, children=[
            Section("Общие сведения", idx=1, text=""),
            Section("Назначение и цели создания (развития) системы", idx=2, text=""),
            Section("Характеристика объектов автоматизации", idx=3, text=""),
            Section("Требования к системе", idx=4, children=[
                Section("Требования к системе в целом", idx=1, children=[
                    Section("Требования к структуре и функционированию системы", idx=1, text=""),
                    Section("Требования к численности и квалификации персонала системы и режиму его работы", idx=2,
                            text=""),
                    Section("Показатели назначения", idx=3, text=""),
                    Section("Требования к надежности", idx=4, text=""),
                    Section("Требования к безопасности", idx=5, text=""),
                    Section("Требования к эргономике и технической эстетике", idx=6, text=""),
                    Section("Требования к транспортабельности для подвижных АС", idx=7, text=""),
                    Section(
                        "Требования к эксплуатации, техническому обслуживанию, ремонту и хранению компонентов системы",
                        idx=8, text=""),
                    Section("Требования к защите информации от несанкционированного доступа", idx=9, text=""),
                    Section("Требования по сохранности информации при авариях", idx=10, text=""),
                    Section("Требования к защите от влияния внешних воздействий", idx=11, text=""),
                    Section("Требования к патентной чистоте", idx=12, text=""),
                    Section("Требования по стандартизации и унификации", idx=13, text=""),
                    Section("Дополнительные требования", idx=14, text="")
                ]),
                Section("Требования к функциям (задачам)", idx=2, text=""),
                Section("Требования к видам обеспечения", idx=3, children=[
                    Section("Требования к математическому обеспечению", idx=1, text=""),
                    Section("Требования к информационному обеспечению", idx=2, text=""),
                    Section("Требования к лингвистическому обеспечению", idx=3, text=""),
                    Section("Требования к программному обеспечению", idx=4, text=""),
                    Section("Требования к техническому обеспечению", idx=5, text=""),
                    Section("Требования к метрологическому обеспечению", idx=6, text=""),
                    Section("Требования к организационному обеспечению", idx=7, text=""),
                    Section("Требования к методическому обеспечению", idx=8, text="")
                ])
            ]),
            Section("Состав и содержание работ по созданию системы", idx=5, text=""),
            Section("Порядок контроля и приемки системы", idx=6, text=""),
            Section("Требования к составу и содержанию работ по подготовке объекта автоматизации к вводу системы в "
                    "действие", idx=7, text=""),
            Section("Требования к документированию", idx=8, text=""),
            Section("Источники разработки", idx=9, text="")
        ])

    def get_leaf_sections(self) -> list:
        return [node for node in PreOrderIter(self.root, filter_=lambda n: hasattr(n, "text"))]

    def get_dict_from_root(self) -> dict:
        # exclude sections from the result for which there were no matches
        for children in LevelOrderGroupIter(self.root):
            for node in children:
                if hasattr(node, "text") and node.text == "":
                    node.parent = None

        exporter = DictExporter()
        return exporter.export(self.root)
