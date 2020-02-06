from typing import Set, Any, Dict


class Node:
    def __init__(self, ids: [str], names: [str]):
        self.ids: Set[str] = set(ids)
        self.names: Set[str] = set(names)
        self.hash = self.calculate_hash()
        self.attributes: Dict[str, Any] = {}
        self.primary_id_prefix = ''

    def __str__(self) -> str:
        sorted_ids_text = ','.join(sorted(self.ids))
        sorted_names_text = ','.join(['"%s"' % x for x in sorted(self.names)])
        return '%s={ids: [%s], names: [%s]}' % (self.label, sorted_ids_text, sorted_names_text)

    def __eq__(self, o: object) -> bool:
        if o is not None and isinstance(o, type(self)):
            return len(self.ids.intersection(o.ids)) > 0
        return False

    def __hash__(self) -> int:
        return self.hash

    @property
    def label(self) -> str:
        label = self.__class__.__name__
        for base in self.__class__.__bases__:
            if base.__name__ != 'Node':
                label += ';' + base.__name__
        return label

    @property
    def id(self) -> str:
        for x in self.ids:
            if x.startswith('%s:' % self.primary_id_prefix):
                return x
        return list(self.ids)[0]

    @property
    def label_id(self) -> str:
        return '%s|%s' % (self.label, self.id)

    def get_first_id_with_prefix(self, prefix: str) -> str or None:
        for x in self.ids:
            if x.startswith('%s:' % prefix):
                return x.split(':')[1]
        return None

    def merge(self, o):
        self.ids.update(o.ids)
        self.names.update(o.names)
        for key in o.attributes:
            if key in self.attributes and self.attributes[key] != o.attributes[key]:
                print('[WARN] merging nodes where both have the same attribute key "%s" and the values differ.' % key)
                print('\t', self.attributes[key])
                print('\t', o.attributes[key])
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return ','.join(self.ids).__hash__()
