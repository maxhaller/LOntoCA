from bs4 import PageElement
from typing_extensions import Self


class ContractualClause:

    def __init__(self, page_element: PageElement = None, node_id: int = None, root: bool = False, parent: Self = None,
                 previous_node: Self = None, next_node: Self = None, title: str = None, raw_text: str = None,
                 node_type: str = None):
        self.page_element = page_element        # Contains the HTML content
        self.node_id = node_id                  # Identifies node
        self.root = root                        # Marks root of tree
        self.parent = parent                    # Parent node
        self.previous_node = previous_node      # Previous node (sibling)
        self.next_node = next_node              # Next node     (sibling)
        self.children = []                      # List of children (ordered)
        self.title = title                      # Title of contractual clause
        self.raw_text = raw_text                # Text of contractual clause that is not contained by children
        self.node_type = node_type              # Type of clause (section, paragraph, enumeration, ...)

        # Initialize root with id=0
        if self.root:
            self.node_id = 0
        else:
            self.find_highest_id() + 1

        # Add node as child to its parent
        if self.parent is not None:
            self.parent.add_child(self)

        # Add previous node
        if self.previous_node is not None:
            self.previous_node.set_next_node(self)

        # Add next node
        if self.next_node is not None:
            self.next_node.set_previous_node(self)

    def remove_empty_nodes(self):
        is_empty = (len(self.title.strip()) + len(self.raw_text.strip())) < 1
        if is_empty and len(self.children) > 0 and not self.root:
            for child in self.children:
                child.set_parent(self.parent)
            self.parent.remove_child(self)
        for child in self.children:
            child.remove_empty_nodes()

    def get_root_node(self):
        ancestor = self.parent
        while ancestor is not None and ancestor.node_type is not 'root':
            ancestor = ancestor.parent
        return ancestor

    def get_highest_id(self):
        return max(max([c.get_highest_id() for c in self.children]), self.node_id)

    def find_highest_id(self):
        root = self.get_root_node()
        return root.get_highest_id()

    def get_children(self):
        return self.children

    def get_node_type(self):
        return self.node_type

    def set_node_type(self, node_type: str):
        self.node_type = node_type

    def get_previous_node(self):
        return self.previous_node

    def set_previous_node(self, previous_node: Self):
        self.previous_node = previous_node

    def get_next_node(self):
        return self.next_node

    def set_next_node(self, next_node: Self):
        self.next_node = next_node

    def get_parent(self):
        return self.parent

    def set_parent(self, parent: Self):
        if self.parent is not None:
            self.parent.remove_child(self)
        self.parent = parent
        if self.parent is not None:
            parent.add_child(self)

    def add_child(self, child: Self):
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child: Self):
        self.children.remove(child)

    def get_node_id(self):
        return self.node_id

    def set_node_id(self, node_id: int):
        self.node_id = node_id

    def get_page_element(self):
        return self.page_element

    def set_page_element(self, element: PageElement):
        self.page_element = element

    def set_title(self, title: str):
        self.title = title

    def get_title(self):
        return self.title

    def set_raw_text(self, raw_text: str):
        self.raw_text = raw_text

    def get_raw_text(self):
        return self.raw_text

    def get_nth_parent(self, n: int):
        if n < 1 or self.parent is None:
            return self
        else:
            return self.parent.get_nth_parent(n-1)

    def get_depth(self):
        depth = 0
        ancestor = self.parent
        while ancestor is not None and ancestor.node_type is not 'root':
            ancestor = ancestor.parent
            depth += 1
        return depth

'''
    def __init__(self, page_element: PageElement | None, clause_type: str, title=None, raw_text=None, parent=None,
                 root=False):
        self.root = root
        self.children = []
        self.page_element = page_element
        self.parent = parent

        if self.parent is not None:
            self.parent.add_child(self)

        self.title = title
        self.clause_type = clause_type
        self.raw_text = raw_text

    def set_parent(self, parent):
        self.parent = parent
        if self.parent is not None:
            self.parent.add_child(self)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def get_page_element(self) -> PageElement:
        return self.page_element

    def set_raw_text(self, raw_text: str):
        self.raw_text = raw_text

    def set_title(self, title: str):
        self.title = title

    def get_title(self):
        return self.title

    def get_children(self):
        return self.children

    def get_leaf_nodes(self, nodes):
        if len(self.children) < 1:
            nodes.append(self)
        else:
            for child in self.children:
                child.get_leaf_nodes(nodes)
        if self.root:
            return nodes

    def get_root(self):
        return self.root

    def get_parent(self):
        return self.parent

    def get_ancestor_path(self, path):
        path.append(self)
        node = self.get_parent()
        while node is not None and not node.get_root():
            path.append(node)
            node = node.get_parent()
        return path

    def remove_empty_nodes(self):
        if self.type == 'kopf1-ve':
            pass
        is_empty = (len(self.title.strip()) + len(self.raw_text.strip())) < 1
        if self.parent is not None:
            if is_empty and len(self.children) > 0:
                for child in self.children:
                    child.set_parent(self.parent)
            if is_empty:
                self.parent.get_children().remove(self)
        else:
            if is_empty:
                for child in self.children:
                    child.set_parent(None)
        for child in self.children:
            child.remove_empty_nodes()
'''