#!/usr/bin/env python3

import os.path
import urllib.request
import io
import csv
import xlrd
from model.network import Network
from model.gene import Gene
from model.mirna import MiRNA
from model.edge import Edge

file = 'data/miRTarBase/hsa_MTI.xlsx'
url = 'http://mirtarbase.mbc.nctu.edu.tw/cache/download/7.0/hsa_MTI.xlsx'
if not os.path.exists(file):
    print('Database does not exist. Trying to download...')
    with urllib.request.urlopen(url) as response, open(file, 'wb') as f:
        f.write(response.read())

mirna_to_URS_mapping_file = 'data/miRTarBase/tarbase.tsv'
mapping_url = 'ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/tarbase.tsv'
if not os.path.exists(mirna_to_URS_mapping_file):
    print('Mapping table does not exist. Trying to download...')
    with urllib.request.urlopen(mapping_url) as response, open(mirna_to_URS_mapping_file, 'wb') as f:
        f.write(response.read())

network = Network()
edge_source_target_lookup = []
wb = xlrd.open_workbook(file)
sh = wb.sheet_by_name('miRTarBase')
for rownum in range(sh.nrows):
    row = sh.row_values(rownum)
    if 'Weak' not in row[7] and row[2] == 'Homo sapiens' and row[5] == 'Homo sapiens':
        mirna_name = row[1]
        gene_hgnc_id = 'HGNC:' + row[3]
        gene_entrez_id = int(row[4])
        gene_entrez_id = 'Entrez:' + str(gene_entrez_id)
        pmid = int(row[8])
        pmid = str(pmid)

        with io.open(mirna_to_URS_mapping_file, 'r', encoding='utf-8', newline='') as mapping_file:
            mapping_reader = csv.reader(mapping_file, delimiter='\t')
            next(mapping_reader, None)
            for mapping_row in mapping_reader:
                if mirna_name == mapping_row[2]:
                    mirna_rnacentral_id = mapping_row[0]
                    mirna = MiRNA([mirna_rnacentral_id], [mirna_name])
                    network.add_node(mirna)
                    gene = Gene([gene_hgnc_id, gene_entrez_id], [])
                    network.add_node(gene)
                    if (mirna_rnacentral_id + '$' + gene_hgnc_id) in edge_source_target_lookup:
                        edges = network.get_edges_from_to(mirna, gene, 'REGULATES')
                        for edge in edges:
                            pmid = edge.attributes['pmid'] + ', ' + str(pmid)
                            network.delete_edge(edge)
                            e = Edge(mirna, gene, 'REGULATES', {'source': 'miRTarBase', 'pmid': pmid})
                            network.add_edge(e)
                            edge_source_target_lookup.append(mirna_rnacentral_id + '$' + gene_hgnc_id)
                    else:
                        e = Edge(mirna, gene, 'REGULATES', {'source': 'miRTarBase', 'pmid': pmid})
                        network.add_edge(e)
                        edge_source_target_lookup.append(mirna_rnacentral_id + '$' + gene_hgnc_id)
                    break
network.save('data/miRTarBase/graph.json')
