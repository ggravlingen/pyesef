"""Define hierarchy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    """Node class."""

    name: str
    parent: Node | None = None


class Hierarchy:
    """Hierarchy class."""

    nodes: dict[str, Node]

    def __init__(self, hierarchy_dict: dict[str, str]) -> None:
        """Init class."""
        self.nodes = {}

        for child, parent in hierarchy_dict.items():
            self._add_node(child, parent)

    def _add_node(self, name: str, parent: str | None = None) -> None:
        """Add a node to the tree."""
        if name not in self.nodes:
            self.nodes[name] = Node(name)

        if parent and parent not in self.nodes:
            self.nodes[parent] = Node(parent)

        if parent and parent in self.nodes:
            self.nodes[name].parent = self.nodes[parent]

    def get_ultimate_parent(self, name: str) -> Node | None:
        """Get node's ultimate parent."""
        node = self.nodes.get(name)

        if not node:
            return None

        while node.parent is not None:
            node = node.parent

        return node
