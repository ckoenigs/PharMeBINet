#!/usr/bin/env python3

import os.path
import urllib.request
import io
import csv
import re
from model.network import Network
from model.gene import Gene
from model.mirna import MiRNA
from model.edge import Edge
from model.go_class import GOClass

network = Network()

file = 'data/EBI-GOA-miRNA/query.txt'
url = 'http://www.ebi.ac.uk/Tools/webservices/psicquic/view/binaryDownload?&serviceURL=https://www.ebi.ac.uk/QuickGO/psicquic-rna/webservices/current/search/&query=*&format=tab27&conversationContext=2'
if not os.path.exists(file):
    print('Database does not exist. Trying to download...')
    with urllib.request.urlopen(url) as response, open(file, 'wb') as f:
        f.write(response.read())
gene_mapping_file = 'data/EBI-GOA-miRNA/ensembl.txt'
gene_mapping_url = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=md_ensembl_id&status=Approved&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
if not os.path.exists(gene_mapping_file):
    print('Gene mapping table does not exist. Trying to download...')
    with urllib.request.urlopen(gene_mapping_url) as response, open(gene_mapping_file, 'wb') as f:
        f.write(response.read())
mirna_mapping_file = 'data/EBI-GOA-miRNA/hgnc.tsv'
mirna_mapping_url = 'ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/hgnc.tsv'
if not os.path.exists(mirna_mapping_file):
    print('MiRNA mapping table does not exist. Trying to download...')
    with urllib.request.urlopen(mirna_mapping_url) as response, open(mirna_mapping_file, 'wb') as f:
        f.write(response.read())

edge_source_target_lookup = []
with io.open(file, 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f, delimiter='\t', quotechar='"')
    next(reader, None)
    for row in reader:
        taxid_interactor_a = row[9]
        taxid_interactor_b = row[10]
        if taxid_interactor_a == 'taxid:9606(Homo sapiens)' and taxid_interactor_b == 'taxid:9606(Homo sapiens)':
            # miRNAs
            mirna_rnacentral = re.split('[:_]', row[0])
            mirna_rnacentral_id = mirna_rnacentral[1]
            mirna_hgnc_id = 'None'
            with io.open(mirna_mapping_file, 'r', encoding='utf-8', newline='') as mm:
                mirna_mapping_reader = csv.reader(mm, delimiter='\t')
                next(mirna_mapping_reader, None)
                for mirna_mapping_row in mirna_mapping_reader:
                    if mirna_mapping_row[0] == mirna_rnacentral_id:
                        mirna_hgnc_id = mirna_mapping_row[2]
                        break
            mirna_name = re.split('[" ]', row[4])
            mirna_name = mirna_name[4]
            if mirna_hgnc_id != 'None':
                mirna = MiRNA([mirna_rnacentral_id, mirna_hgnc_id], [mirna_name])
                network.add_node(mirna)
            else:
                mirna = MiRNA([mirna_rnacentral_id], [mirna_name])
                network.add_node(mirna)
            # genes
            gene_ensembl = row[1].split(':')
            gene_ensembl_id = gene_ensembl[1]
            gene_hgnc_id = 'None'
            with io.open(gene_mapping_file, 'r', encoding='utf-8', newline='') as gm:
                gene_mapping_reader = csv.reader(gm, delimiter='\t')
                next(gene_mapping_reader, None)
                for gene_mapping_row in gene_mapping_reader:
                    if gene_mapping_row[2] == gene_ensembl_id:
                        gene_hgnc_id = 'HGNC:' + gene_mapping_row[1]
                        break
            if gene_hgnc_id != 'None' and 'gene' in row[21]:
                gene_uniprotkb_id = re.split('[:(]', row[5])
                gene_uniprotkb_id = 'UniProtKB:' + gene_uniprotkb_id[1]
                gene_ensembl_id = 'Ensembl:' + gene_ensembl_id
                gene = Gene([gene_hgnc_id, gene_uniprotkb_id, gene_ensembl_id], [])
                network.add_node(gene)
                pmid = row[8].split(':')
                pmid = pmid[1]
                source_database = row[12]
                source_database = source_database.replace('\"', '')
                if (mirna_rnacentral_id + '$' + gene_hgnc_id) in edge_source_target_lookup:
                    reg_edges = network.get_edges_from_to(mirna, gene, 'REGULATES')
                    for reg_edge in reg_edges:
                        if reg_edge.attributes['source'] == ('EBI-GOA-miRNA, ' + source_database):
                            pmid = reg_edge.attributes['pmid'] + ', ' + pmid
                            network.delete_edge(reg_edge)
                            e = Edge(mirna, gene, 'REGULATES',
                                     {'source': 'EBI-GOA-miRNA, ' + source_database, 'pmid': pmid})
                            network.add_edge(e)
                            edge_source_target_lookup.append(mirna_rnacentral_id + '$' + gene_hgnc_id)
                else:
                    e = Edge(mirna, gene, 'REGULATES', {'source': 'EBI-GOA-miRNA, ' + source_database, 'pmid': pmid})
                    network.add_edge(e)
                    edge_source_target_lookup.append(mirna_rnacentral_id + '$' + gene_hgnc_id)
                # GOs
                go = re.split('[:(]', row[22])
                go_id = go[2].replace('"', '')
                go_id = 'GO:' + go_id
                go_name = go[3].replace(')', '')
                go_class = GOClass([go_id], [go_name])
                network.add_node(go_class)
                if go_id == 'GO:0035195' or go_id == 'GO:0035278':
                    label = 'BELONGS_TO_BIOLOGICAL_PROCESS'
                elif go_id == 'GO:1903231':
                    label = 'HAS_MOLECULAR_FUNCTION'
                if (mirna_rnacentral_id + '$' + go_id) in edge_source_target_lookup:
                    edges = network.get_edges_from_to(mirna, go_class, label)
                    for edge in edges:
                        if edge.attributes['source'] == ('EBI-GOA-miRNA, ' + source_database):
                            pmid = edge.attributes['pmid'] + ', ' + pmid
                            network.delete_edge(edge)
                            e_go = Edge(mirna, go_class, label,
                                        {'source': 'EBI-GOA-miRNA, ' + source_database, 'pmid': pmid})
                            network.add_edge(e_go)
                            edge_source_target_lookup.append(mirna_rnacentral_id + '$' + go_id)
                else:
                    e_go = Edge(mirna, go_class, label, {'source': 'EBI-GOA-miRNA, ' + source_database, 'pmid': pmid})
                    network.add_edge(e_go)
                    edge_source_target_lookup.append(mirna_rnacentral_id + '$' + go_id)

network.save('data/EBI-GOA-miRNA/graph.json')
