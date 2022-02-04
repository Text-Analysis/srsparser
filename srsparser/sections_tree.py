from anytree import AnyNode, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from anytree.search import find_by_attr

importer = DictImporter()
exporter = DictExporter()


class Section(AnyNode):
    """
    Class representing section of text document with software requirements specification (SRS).
    """

    def __init__(self, name: str, parent=None, children=None, **kwargs):
        super().__init__(parent, children, **kwargs)
        self.name = name
        self.parent = parent
        if children:
            self.children = children


class SectionsTree:
    """
    Class representing :py:class:`Section` tree structure.
    """

    def __init__(self, template: dict):
        """
        :param template: section tree structure template. It can be found in MongoDB template collection.
        """
        self.root = importer.import_(template)

    def to_dict(self) -> dict:
        # excludes leaf sections with empty text fields from the result
        for children in LevelOrderGroupIter(self.root):
            for node in children:
                if hasattr(node, 'text') and node.text == '':
                    node.parent = None
        return exporter.export(self.root)

    def get_leaf_sections(self, section_name='Техническое задание') -> list:
        """
        Returns leaf element list of the :py:class:`Section` tree structure.

        If the parameter `section_name` is explicitly specified,
        then the list of leaf elements relative to the section of the same name is returned.
        """
        search_from_node = find_by_attr(self.root, name='name', value=section_name)
        if search_from_node:
            return [node for node in PreOrderIter(search_from_node, filter_=lambda n: hasattr(n, 'text'))]
        return []

    def get_content(self, section_name='Техническое задание') -> str:
        """
        Returns :py:class:`Section` tree structure text content.

        If the parameter `section_name` is explicitly specified,
        then the list of leaf elements relative to the section of the same name is returned.
        """
        return "".join([node.text for node in self.get_leaf_sections(section_name)])
