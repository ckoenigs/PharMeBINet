from model.node import Node


class RNA(Node):
    def __init__(self, ids: [str], names: [str]):
        super().__init__(ids, names)
        self.primary_id_prefix = ''