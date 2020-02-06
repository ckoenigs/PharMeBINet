from typing import Dict, Any, Tuple

from model.node import Node


class Edge:
    internal_id_counter = 1

    def __init__(self, source_node: Node, target_node: Node or Tuple[str, str], label: str, attributes: Dict[str, Any]):
        self.source_node_id = source_node.id
        self.source_node_label = source_node.label
        if isinstance(target_node, Node):
            self.target_node_id = target_node.id
            self.target_node_label = target_node.label
        else:
            self.target_node_id = target_node[0]
            self.target_node_label = target_node[1]
        self.label = label
        self.attributes = attributes
        self._id = Edge.internal_id_counter
        Edge.internal_id_counter += 1

    @property
    def id(self) -> int:
        return self._id

    @property
    def source_label_id(self) -> str:
        return '%s|%s' % (self.source_node_label, self.source_node_id)

    @property
    def target_label_id(self) -> str:
        return '%s|%s' % (self.target_node_label, self.target_node_id)

    def __str__(self) -> str:
        return 'Edge={label: %s, source: %s, target: %s}' % (self.label, self.source_label_id, self.target_label_id)
