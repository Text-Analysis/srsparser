from anytree import AnyNode, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter
from anytree.importer import DictImporter

importer = DictImporter()
exporter = DictExporter()


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
    A class representing a sections_tree_skeleton of sections of a text document.
    """

    def __init__(self, tree_template: dict):
        """
        :param tree_template: section tree template.
        """
        self.root = importer.import_(tree_template)

    def get_leaf_sections(self) -> list:
        return [node for node in PreOrderIter(self.root, filter_=lambda n: hasattr(n, "text"))]

    def get_dict_from_root(self) -> dict:
        # exclude sections from the result for which there were no matches
        for children in LevelOrderGroupIter(self.root):
            for node in children:
                if hasattr(node, "text") and node.text == "":
                    node.parent = None
        return exporter.export(self.root)
