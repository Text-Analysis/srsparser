from anytree import AnyNode, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from anytree.search import find_by_attr

importer = DictImporter()
exporter = DictExporter()


class Section(AnyNode):
    """
    A class representing a section of the text document.
    """

    def __init__(self, name: str, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.parent = parent
        if children:
            self.children = children


class SectionsTree:
    """
    A class representing the sections tree of the text document.
    """

    def __init__(self, template: dict):
        """
        :param template: sections tree template.
        """
        self.root = importer.import_(template)

    def to_dict(self) -> dict:
        # exclude sections from the result for which there were no matches
        for children in LevelOrderGroupIter(self.root):
            for node in children:
                if hasattr(node, "text") and node.text == "":
                    node.parent = None
        return exporter.export(self.root)

    def get_leaf_sections(self, section_name="Техническое задание") -> list:
        """
        Returns leaf elements of the whole sections tree (from root). If the parameter section_name is specified,
        it returns leaf elements that are nested in the section of the same name with section_name.
        """
        search_from_node = find_by_attr(self.root, name="name", value=section_name)
        if search_from_node:
            return [node for node in PreOrderIter(search_from_node, filter_=lambda n: hasattr(n, "text"))]
        return []

    def get_content(self, section_name="Техническое задание") -> str:
        """
        Returns the content of the section tree (the totality of all text fields). If the parameter section_name is
        specified, it returns the content that is inside the section named section_name.
        """
        return "".join([node.text for node in self.get_leaf_sections(section_name)])
