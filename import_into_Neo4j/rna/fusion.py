#!/usr/bin/env python3

import csv
import io
import os
import json
from typing import Dict

import mondo_mapper

from utils import name_utils
from utils import directory_utils

from model.disease import Disease
from model.network import Network


def merge_duplicate_node_names(network: Network):
    for node in network.nodes.values():
        node.names = name_utils.normalize_node_names(node.names)


def save_network(network: Network, config: Dict):
    output_path = config['output-path']
    # Save nodes
    node_import_files = []
    for label in network.node_labels():
        file_name = 'nodes_%s.csv' % label.replace(';', '_')
        nodes = set(network.get_nodes_by_label(label))
        if len(nodes) > 0:
            node_import_files.append(file_name)
            with io.open(os.path.join(output_path, file_name), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"')
                all_attribute_keys = set()
                for n in nodes:
                    all_attribute_keys.update(n.attributes.keys())
                all_attribute_keys = sorted(all_attribute_keys)
                writer.writerow(
                    ['label_id:ID(Node-ID)', '_id:string', 'ids:string[]', 'names:string[]'] +
                    ['%s:string' % x for x in all_attribute_keys] + [':LABEL'])
                for n in nodes:
                    row = [n.label_id, n.id, ';'.join(n.ids), ';'.join(n.names)]
                    for key in all_attribute_keys:
                        row.append(n.attributes[key] if key in n.attributes else None)
                    row.append(n.label)
                    writer.writerow(row)

    edge_metadata = {
        'HAS_MOLECULAR_FUNCTION': [['source:string', 'pmid:string'], ['source', 'pmid']],  # pmid int now not string
        'BELONGS_TO_BIOLOGICAL_PROCESS': [['source:string', 'pmid:string'], ['source', 'pmid']],
        'IN_CELLULAR_COMPONENT': [['source:string', 'pmid:string'], ['source', 'pmid']],
        'INDICATES': [['source:string'], ['source']],
        'REGULATES': [['source:string', 'pmid:string'], ['source', 'pmid']],
        'TRANSCRIBES': [['source:string'], ['source']],
        'CONTRAINDICATES': [['source:string'], ['source']],
        'INDUCES': [['source:string'], ['source']],
        'CODES': [['source:string', 'pmid:int'], ['source', 'pmid']],
        'EQTL': [
            ['source:string', 'pvalue:string', 'snp_chr:string', 'cis_trans:string'],
            ['source', 'pvalue', 'snp_chr', 'cis_trans']
        ],
        'INTERACTS': [['source:string', 'description:string'], ['source', 'description']],
        'TARGETS': [
            ['source:string', 'known_action:boolean', 'actions:string[]', 'simplified_action:string'],
            [
                'source',
                lambda attr: ('true' if attr['known_action'] else 'false') if 'known_action' in attr else None,
                lambda attr: ';'.join(attr['actions']),
                'simplified_action'
            ]
        ],
        'ASSOCIATES_WITH': [
            ['source:string', 'num_pmids:int', 'num_snps:int', 'score:string'],
            ['source', 'num_pmids', 'num_snps', 'score']
        ],
        'HAS_ADR': [['source:string'], ['source']],
        'ASSOCIATED_WITH_ADR': [['source:string'], ['source']]
    }

    # Save relationships
    for x in edge_metadata:
        with io.open(os.path.join(output_path, 'rel_%s.csv' % x), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"')
            writer.writerow([':START_ID(Node-ID)'] + edge_metadata[x][0] + [':END_ID(Node-ID)', ':TYPE'])
            for e in network.get_edges_by_label(x):
                values = []
                for l in edge_metadata[x][1]:
                    if isinstance(l, type(lambda: 0)):
                        values.append(l(e.attributes))
                    else:
                        values.append(e.attributes[l] if l in e.attributes else None)
                source_id = network.get_node_by_id(e.source_node_id, e.source_node_label).label_id
                target_id = network.get_node_by_id(e.target_node_id, e.target_node_label).label_id
                writer.writerow([source_id] + values + [target_id, e.label])

    with io.open(os.path.join(output_path, 'create_indices.cypher'), 'w', encoding='utf-8', newline='') as f:
        unique_labels = set()
        for node_label in network.node_labels():
            unique_labels.update(set(node_label.split(';')))
        for node_label in unique_labels:
            f.write('create constraint on (p:%s) assert p._id is unique;\n' % node_label)
    with io.open(os.path.join(output_path, 'import_admin.bat'), 'w', encoding='utf-8', newline='') as f:
        f.write('@echo off\n')
        f.write('net stop neo4j\n')
        f.write('rmdir /s "%s"\n' % os.path.join(config['Neo4j']['database-path'], config['Neo4j']['database-name']))
        f.write('CALL ' + os.path.join(config['Neo4j']['bin-path'], 'neo4j-admin'))
        f.write(' import ' +
                '--database %s ' % config['Neo4j']['database-name'] +
                ' '.join(['--nodes %s' % x for x in node_import_files]) + ' ' +
                ' '.join(['--relationships rel_%s.csv' % x for x in network.edge_labels()]) +
                ' > import.log\n')
        f.write('net start neo4j\n')
        f.write(os.path.join(config['Neo4j']['bin-path'], 'cypher-shell'))
        f.write(' -u %s -p %s --non-interactive < create_indices.cypher 1>> import.log 2>&1\n'
                % (config['Neo4j']['user'], config['Neo4j']['password']))
    with io.open(os.path.join(output_path, 'import_admin.sh'), 'w', encoding='utf-8', newline='') as f:
        f.write(os.path.join(config['Neo4j']['bin-path'], 'neo4j-admin'))
        f.write(' import ' +
                '--database %s ' % config['Neo4j']['database-name'] +
                ' '.join(['--nodes %s' % x for x in node_import_files]) + ' ' +
                ' '.join(['--relationships rel_%s.csv' % x for x in network.edge_labels()]) +
                ' > import.log\n')


if __name__ == '__main__':
    with io.open('../data/config.json', 'r', encoding='utf-8', newline='') as f:
        config = json.load(f)

    network = Network()
    # Import
    graphs = [
        '../data/EBI-GOA-miRNA/graph.json',
        '../data/miRTarBase/graph.json',
        '../data/RNAInter/graph.json',
        '../data/DisGeNet/graph.json',
        '../data/DrugBank/graph.json',
        '../data/DrugCentral/graph.json',
        '../data/GWAS-Catalog/graph.json',
        '../data/HGNC/graph.json',
        '../data/HPO/graph.json',
        '../data/MED-RT/graph.json',
        '../data/NDF-RT/graph.json',
        '../data/OMIM/graph.json',
        '../data/HuGE-Navigator/graph.json',
        '../data/SIDER/graph.json',
        '../data/DGIdb/graph.json',
        '../data/Westra_etal_2017/graph.json',
        '../data/SuperDrug2/graph.json',
        '../data/UniprotKB/graph.json',
        '../data/GO/graph.json',
        '../data/PharmGKB/graph.json',
        # '../data/PubMed/graph.json',
    ]
    # Fusion
    print('[INFO] Network fusion')
    for graph in graphs:
        print('[INFO] Add network', graph)
        with io.open(graph, 'r', encoding='utf-8', newline='') as f:
            g = json.loads(f.read())
            network.load_from_dict(g)
    # Mapping
    print('[INFO] Add disease mappings')
    all_disease_ids = set()
    for node in network.get_nodes_by_label('Disease'):
        all_disease_ids.update(node.ids)
    for disease_id in all_disease_ids:
        mapped_ids, mapped_names = mondo_mapper.map_from(disease_id)
        if mapped_ids:
            network.add_node(Disease(mapped_ids, mapped_names))
    # Cleanup
    print('[INFO] Prune network')
    network.prune()
    print('[INFO] Merge duplicate node names')
    merge_duplicate_node_names(network)
    print('[INFO] Merge duplicate edges')
    network.merge_duplicate_edges()
    # Export
    print('[INFO] Export network')
    directory_utils.create_clean_directory(config['output-path'])
    with io.open(os.path.join(config['output-path'], 'graph.json'), 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(network.to_dict(), separators=(',', ':')))
    save_network(network, config)
