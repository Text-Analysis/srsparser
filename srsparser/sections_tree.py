from anytree import AnyNode, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from anytree.search import find_by_attr

importer = DictImporter()
exporter = DictExporter()


class Section(AnyNode):
    """
    Класс, представляющий раздел текстового документа с ТЗ.
    """

    def __init__(self, name: str, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.parent = parent
        if children:
            self.children = children


class SectionsTree:
    """
    Класс, представляющий дерево разделов текстового документа с ТЗ.
    """

    def __init__(self, template: dict):
        """
        :param template: шаблон дерева резделов текстового документа с ТЗ. Можно найти в коллекции MongoDB с шаблонами.
        """
        self.root = importer.import_(template)

    def to_dict(self) -> dict:
        # исключаем из результата листовые разделы, для которых при парсинге не заполнились поля text
        for children in LevelOrderGroupIter(self.root):
            for node in children:
                if hasattr(node, "text") and node.text == "":
                    node.parent = None
        return exporter.export(self.root)

    def get_leaf_sections(self, section_name="Техническое задание") -> list:
        """
        Возвращает список листовых элементов дерева разделов относительно корневого раздела. Если явно указан параметр
        `section_name`, то возвращается список листовых элементов относительно одноимённого раздела.
        """
        search_from_node = find_by_attr(self.root, name="name", value=section_name)
        if search_from_node:
            return [node for node in PreOrderIter(search_from_node, filter_=lambda n: hasattr(n, "text"))]
        return []

    def get_content(self, section_name="Техническое задание") -> str:
        """
        Возвращает содержимое дерева разделов (совокупность значений всех полей `text`) относительно корневого раздела.
        Если указан параметр `section_name`, то возвращается содержимое одноимённого раздела,
        а не всего дерева разделов.
        """
        return "".join([node.text for node in self.get_leaf_sections(section_name)])
