import io
import json
from model.node import Node
from model.edge import Edge
from model.circrna import CircRNA
from model.erna import ERNA
from model.lncrna import LncRNA
from model.mirna import MiRNA
from model.mrna import MRNA
from model.ncrna import NcRNA
from model.pirna import PiRNA
from model.pseudogene import Pseudogene
from model.ribozyme import Ribozyme
from model.rna import RNA
from model.rrna import RRNA
from model.scarna import ScaRNA
from model.scrna import ScRNA
from model.snorna import SnoRNA
from model.snrna import SnRNA
from typing import List, Dict, Iterator


class Network:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[int, Edge] = {}
        self.edge_lookup: Dict[str, Dict[int, Edge]] = {}
        self.edge_source_lookup: Dict[str, Dict[int, Edge]] = {}
        self.edge_target_lookup: Dict[str, Dict[int, Edge]] = {}

    def add_node(self, node: Node):
        label_ids = [self.get_node_label_id(node, _id) for _id in node.ids]
        matches = [self.nodes[x] for x in label_ids if x in self.nodes]
        for match in matches:
            node.merge(match)
        label_ids = [self.get_node_label_id(node, _id) for _id in node.ids]
        for x in label_ids:
            self.nodes[x] = node

    def get_node_by_id(self, _id: str, label: str) -> Node:
        label_id = '%s|%s' % (label, _id)
        return self.nodes[label_id] if label_id in self.nodes else None

    def get_nodes(self) -> Iterator[Node]:
        for node in set(self.nodes.values()):
            yield node

    def get_nodes_by_label(self, label: str) -> List[Node]:
        result = set()
        for node in self.nodes.values():
            if label in node.label.split(';'):
                result.add(node)
        return list(result)

    def node_labels(self) -> List[str]:
        return sorted({node.label for node in self.get_nodes()})

    def edge_labels(self) -> List[str]:
        return sorted(self.edge_lookup.keys())

    def add_edge(self, edge: Edge):
        self.edges[edge.id] = edge
        if edge.label not in self.edge_lookup:
            self.edge_lookup[edge.label] = {}
        self.edge_lookup[edge.label][edge.id] = edge
        if edge.source_label_id not in self.edge_source_lookup:
            self.edge_source_lookup[edge.source_label_id] = {}
        self.edge_source_lookup[edge.source_label_id][edge.id] = edge
        if edge.target_label_id not in self.edge_target_lookup:
            self.edge_target_lookup[edge.target_label_id] = {}
        self.edge_target_lookup[edge.target_label_id][edge.id] = edge

    def get_edges_by_label(self, label: str) -> List[Edge]:
        return list(self.edge_lookup[label].values()) if label in self.edge_lookup else []

    def get_node_edges_by_label(self, node: Node, label: str) -> List[Edge]:
        result = []
        if label in self.edge_lookup:
            for _id in node.ids:
                if _id in self.edge_source_lookup:
                    result.extend([e for e in self.edge_source_lookup[_id].values() if e.label == label])
                if _id in self.edge_target_lookup:
                    result.extend([e for e in self.edge_target_lookup[_id].values() if e.label == label])
        return result

    def get_edges_from_to(self, node_from: Node, node_to: Node, label: str) -> List[Edge]:
        result = []
        if label in self.edge_lookup:
            for _id in node_from.ids:
                if _id in self.edge_source_lookup:
                    result.extend([e for e in self.edge_source_lookup[_id].values()
                                   if e.label == label and e.target_node_id in node_to.ids])
        return result

    def delete_node(self, node: Node):
        edges = []
        for _id in node.ids:
            _id = self.get_node_label_id(node, _id)
            del self.nodes[_id]
            if _id in self.edge_source_lookup:
                edges.extend(self.edge_source_lookup[_id].values())
                del self.edge_source_lookup[_id]
            if _id in self.edge_target_lookup:
                edges.extend(self.edge_target_lookup[_id].values())
                del self.edge_target_lookup[_id]
        for edge in edges:
            if edge.id in self.edges:
                del self.edges[edge.id]
            if edge.id in self.edge_lookup[edge.label]:
                del self.edge_lookup[edge.label][edge.id]

    @staticmethod
    def get_node_label_id(node: Node, _id: str or None = None) -> str:
        return '%s|%s' % (node.label, _id if _id else node.id)

    def delete_edge(self, edge: Edge):
        del self.edges[edge.id]
        del self.edge_lookup[edge.label][edge.id]
        del self.edge_source_lookup[edge.source_label_id][edge.id]
        del self.edge_target_lookup[edge.target_label_id][edge.id]

    def prune(self):
        '''
        # Remove genes of no interest
        targeted_genes_id = {x.target for x in self.edge_lookup['TARGETS'].values()}
        for gene in set(self.get_nodes_by_label('Gene')):
            if targeted_genes_id.isdisjoint(gene.ids):
                self.delete_node(gene)
        # Remove variants of no interest
        coded_variants_id = {x.target for x in self.edge_lookup['CODES'].values()}
        for variant in set(self.get_nodes_by_label('Variant')):
            if coded_variants_id.isdisjoint(variant.ids):
                self.delete_node(variant)
        '''
        # Remove singletons
        for node in set(self.nodes.values()):
            label_ids = [self.get_node_label_id(node, _id) for _id in node.ids]
            if not any([_id in self.edge_source_lookup or _id in self.edge_target_lookup for _id in label_ids]):
                self.delete_node(node)

    def merge_duplicate_edges(self):
        for label in self.edge_lookup:
            edges = list(self.edge_lookup[label].values())
            edge_source_target_lookup = {}
            for edge in edges:
                key = '%s$%s' % (self.get_node_label_id(self.nodes[edge.source_label_id]),
                                 self.get_node_label_id(self.nodes[edge.target_label_id]))
                if key not in edge_source_target_lookup:
                    edge_source_target_lookup[key] = []
                edge_source_target_lookup[key].append(edge)
            for source_target_key in edge_source_target_lookup:
                edges_subset = edge_source_target_lookup[source_target_key]
                for i in range(0, len(edges_subset) - 1):
                    edge_a = edges_subset[i]
                    for j in range(i + 1, len(edges_subset)):
                        edge_b = edges_subset[j]
                        identical = len(edge_a.attributes.keys()) == len(edge_b.attributes.keys())
                        if identical:
                            for key in edge_a.attributes.keys():
                                if key not in edge_b.attributes or edge_a.attributes[key] != edge_b.attributes[key]:
                                    identical = False
                                    break
                        if identical:
                            self.delete_edge(edge_a)
                            break

    def to_dict(self) -> {}:
        result = {
            'node_types': {},
            'nodes': [],
            'edges': []
        }
        for node in set(self.nodes.values()):
            n = {
                'ids': sorted(node.ids),
                'names': sorted(node.names),
                '_id': node.id,
                '_label': node.label
            }
            n.update(node.attributes)
            if node.label not in result['node_types']:
                result['node_types'][node.label] = node.__module__
            result['nodes'].append(n)
        for edge in self.edges.values():
            e = {
                '_label': edge.label,
                '_source_id': edge.source_node_id,
                '_source_label': edge.source_node_label,
                '_target_id': edge.target_node_id,
                '_target_label': edge.target_node_label
            }
            for key in edge.attributes:
                e[key] = edge.attributes[key]
            result['edges'].append(e)
        return result

    def load_from_dict(self, source: {}):
        py_class_map = {}
        for label in source['node_types']:
            if ';' not in label:
                module_name = source['node_types'][label]
                module = __import__(module_name)
                for package in module_name.split('.')[1:]:
                    module = getattr(module, package)
                py_class_map[label] = getattr(module, label)
        for node in source['nodes']:
            node_instance: Node
            if ';' not in node['_label']:
                class_ = py_class_map[node['_label']]
                node_instance = class_(node['ids'], node['names'])
            elif 'RNA' in node['_label']:
                label = node['_label']
                if 'CircRNA' in label:
                    node_instance = CircRNA(node['ids'], node['names'])
                elif 'ERNA' in label:
                    node_instance = ERNA(node['ids'], node['names'])
                elif 'LncRNA' in label:
                    node_instance = LncRNA(node['ids'], node['names'])
                elif 'MiRNA' in label:
                    node_instance = MiRNA(node['ids'], node['names'])
                elif 'MRNA' in label:
                    node_instance = MRNA(node['ids'], node['names'])
                elif 'NcRNA' in label:
                    node_instance = NcRNA(node['ids'], node['names'])
                elif 'PiRNA' in label:
                    node_instance = PiRNA(node['ids'], node['names'])
                elif 'Pseudogene' in label:
                    node_instance = Pseudogene(node['ids'], node['names'])
                elif 'Ribozyme' in label:
                    node_instance = Ribozyme(node['ids'], node['names'])
                elif 'RRNA' in label:
                    node_instance = RRNA(node['ids'], node['names'])
                elif 'ScaRNA' in label:
                    node_instance = ScaRNA(node['ids'], node['names'])
                elif 'ScRNA' in label:
                    node_instance = ScRNA(node['ids'], node['names'])
                elif 'SnoRNA' in label:
                    node_instance = SnoRNA(node['ids'], node['names'])
                elif 'SnRNA' in label:
                    node_instance = SnRNA(node['ids'], node['names'])
                else:
                    node_instance = RNA(node['ids'], node['names'])
            else:
                print('[Err ] Failed to load node with multiple labels', node)
                continue
            for key in node.keys():
                if key not in ['_id', 'ids', 'names', '_label']:
                    node_instance.attributes[key] = node[key]
            self.add_node(node_instance)

        for edge in source['edges']:
            params = dict(edge)
            del params['_source_id']
            del params['_source_label']
            del params['_target_id']
            del params['_target_label']
            del params['_label']
            source_node = self.get_node_by_id(edge['_source_id'], edge['_source_label'])
            if source_node is None:
                print('Failed to load edge: could not find source node with label %s and id %s' % (
                    edge['_source_label'], edge['_source_id']))
            target_node = self.get_node_by_id(edge['_target_id'], edge['_target_label'])
            if target_node is None:
                print('Failed to load edge: could not find target node with label %s and id %s' % (
                    edge['_target_label'], edge['_target_id']))
            self.add_edge(Edge(source_node, target_node, edge['_label'], params))

    def save(self, file_path: str, indent: bool = False):
        with io.open(file_path, 'w', encoding='utf-8', newline='') as f:
            if indent:
                f.write(json.dumps(self.to_dict(), indent=2))
            else:
                f.write(json.dumps(self.to_dict()))
