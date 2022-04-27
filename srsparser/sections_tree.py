from typing import List

from anytree import AnyNode, PreOrderIter, LevelOrderGroupIter
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from anytree.search import find_by_attr

importer = DictImporter()
exporter = DictExporter()


class Section(AnyNode):
    """
    Class representing section of text document.
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
        :param template: section tree structure template.
        """
        self.root = importer.import_(template)
        self.root_section_name = self.get_root_value(template)

    def to_dict(self) -> dict:
        # excludes leaf sections with empty text fields
        for children in LevelOrderGroupIter(self.root):
            for node in children:
                if hasattr(node, 'text') and node.text == '':
                    node.parent = None
        return exporter.export(self.root)

    def get_all_sections(self) -> list:
        """
        Returns element list of the :py:class:`Section` tree structure.
        """
        return [node for node in PreOrderIter(self.root)]

    def get_leaf_sections(self, section_name='') -> list:
        """
        Returns leaf element list of the :py:class:`Section` tree structure.

        If the parameter `section_name` is explicitly specified,
        then the list of leaf elements relative to the section of the same name is returned.
        """
        if section_name == '':
            section_name = self.root_section_name

        search_from_node = find_by_attr(self.root, name='name', value=section_name)
        if search_from_node:
            return [node for node in PreOrderIter(search_from_node, filter_=lambda n: hasattr(n, 'text'))]
        return []

    def get_section_names(self) -> List[str]:
        """
        Returns list of section names of the :py:class:`Section` tree structure.
        """
        return [node.name for node in PreOrderIter(self.root)]

    def get_content(self, section_name='') -> str:
        """
        Returns :py:class:`Section` tree structure text content.

        If the parameter `section_name` is explicitly specified,
        then the list of leaf elements relative to the section of the same name is returned.
        """
        if section_name == '':
            section_name = self.root_section_name

        return ". ".join([node.text for node in self.get_leaf_sections(section_name)])

    def validate(self) -> bool:
        """
        Checks the section structure for validity.

        :return: True - if valid, otherwise - False.
        """
        for node in PreOrderIter(self.root):
            if not hasattr(node, 'name'):
                return False
            if hasattr(node, 'text') and node.children:
                return False
            if not (hasattr(node, 'text') or node.children):
                return False
        return True

    @staticmethod
    def get_root_value(structure: dict) -> str:
        """
        Returns the name of the root value of the structure.
        """
        return list(structure.values())[0]
