#!/usr/bin/env python3

import os.path
import urllib.request
import zipfile
import io
import csv
from model.circrna import CircRNA
from model.edge import Edge
from model.erna import ERNA
from model.gene import Gene
from model.lncrna import LncRNA
from model.mirna import MiRNA
from model.mrna import MRNA
from model.ncrna import NcRNA
from model.network import Network
from model.pirna import PiRNA
from model.pseudogene import Pseudogene
from model.ribozyme import Ribozyme
from model.rna import RNA
from model.rrna import RRNA
from model.scarna import ScaRNA
from model.scrna import ScRNA
from model.snorna import SnoRNA
from model.snrna import SnRNA


def get_mirna_id(mirna_name):
    mirna_rnacentral_id = 'None'
    with io.open(mirna_mapping_file, 'r', encoding='utf-8', newline='') as mf:
        mapping_reader = csv.reader(mf, delimiter='\t', quotechar='"')
        next(mapping_reader, None)
        for mapping_row in mapping_reader:
            if mapping_row[2] == mirna_name:
                mirna_rnacentral_id = mapping_row[0]
                break
    return mirna_rnacentral_id  # can be None


def get_rna_ids(name):
    rnacentral_id = 'None'
    hgnc_id = 'None'
    with io.open(rna_mapping_file, 'r', encoding='utf-8', newline='') as mf:
        mapping_reader = csv.reader(mf, delimiter='\t', quotechar='"')
        next(mapping_reader, None)
        for mapping_row in mapping_reader:
            if mapping_row[5] == name:
                rnacentral_id = mapping_row[0]
                hgnc_id = 'HGNC:' + name
                break
    return rnacentral_id, hgnc_id  # can be None


def check_hgnc_id(name):
    hgnc_id = 'None'
    with io.open(hgnc_ids_file, 'r', encoding='utf-8', newline='') as h:
        reader = csv.reader(h)
        next(reader, None)
        for row in reader:
            if name in row:
                hgnc_id = 'HGNC:' + name
    return hgnc_id  # can be None


def add_rna(name, type, node_lookup):
    key = name + '$' + type
    if key in node_lookup.keys():
        node = node_lookup[key]
        return node
    else:
        if type == 'mRNA' or type == 'DNA' or type == 'TF' or type == 'protein' or type == 'RBP':
            interactor_id = check_hgnc_id(name)
        elif type == 'miRNA':
            interactor_id = get_mirna_id(name)
        else:
            rnacentral_id, interactor_id = get_rna_ids(name)
            if rnacentral_id == 'None':
                interactor_id = check_hgnc_id(name)

        if interactor_id != 'None':
            if type == 'DNA' or type == 'TF' or type == 'protein' or type == 'RBP':
                node = Gene([interactor_id], [])
                network.add_node(node)
            elif type == 'miRNA':
                node = MiRNA([interactor_id], [name])
                network.add_node(node)
            elif type == 'mRNA':
                node = MRNA([interactor_id], [])
                network.add_node(node)
            else:
                if rnacentral_id == 'None':
                    if type == 'circRNA':
                        node = CircRNA([interactor_id], [])
                    elif type == 'eRNA':
                        node = ERNA([interactor_id], [])
                    elif type == 'lncRNA':
                        node = LncRNA([interactor_id], [])
                    elif type == 'ncRNA':
                        node = NcRNA([interactor_id], [])
                    elif type == 'piRNA':
                        node = PiRNA([interactor_id], [])
                    elif type == 'pseudo':
                        node = Pseudogene([interactor_id], [])
                    elif type == 'ribozyme':
                        node = Ribozyme([interactor_id], [])
                    elif type == 'rRNA':
                        node = RRNA([interactor_id], [])
                    elif type == 'scaRNA':
                        node = ScaRNA([interactor_id], [])
                    elif type == 'scRNA':
                        node = ScRNA([interactor_id], [])
                    elif type == 'snoRNA':
                        node = SnoRNA([interactor_id], [])
                    elif type == 'snRNA':
                        node = SnRNA([interactor_id], [])
                    else:
                        node = RNA([interactor_id], [])
                    network.add_node(node)
                else:
                    if type == 'circRNA':
                        node = CircRNA([rnacentral_id, interactor_id], [])
                    elif type == 'eRNA':
                        node = ERNA([rnacentral_id, interactor_id], [])
                    elif type == 'lncRNA':
                        node = LncRNA([rnacentral_id, interactor_id], [])
                    elif type == 'ncRNA':
                        node = NcRNA([rnacentral_id, interactor_id], [])
                    elif type == 'piRNA':
                        node = PiRNA([rnacentral_id, interactor_id], [])
                    elif type == 'pseudo':
                        node = Pseudogene([rnacentral_id, interactor_id], [])
                    elif type == 'ribozyme':
                        node = Ribozyme([rnacentral_id, interactor_id], [])
                    elif type == 'rRNA':
                        node = RRNA([rnacentral_id, interactor_id], [])
                    elif type == 'scaRNA':
                        node = ScaRNA([rnacentral_id, interactor_id], [])
                    elif type == 'scRNA':
                        node = ScRNA([rnacentral_id, interactor_id], [])
                    elif type == 'snoRNA':
                        node = SnoRNA([rnacentral_id, interactor_id], [])
                    elif type == 'snRNA':
                        node = SnRNA([rnacentral_id, interactor_id], [])
                    else:
                        node = RNA([rnacentral_id, interactor_id], [])
                    network.add_node(node)
            node_lookup[key] = node
            return node
        else:
            return None


if __name__ == '__main__':

    file = 'data/RNAInter/2804_res.txt'
    zip_file = 'data/RNAInter/Homo sapiens.zip'
    url = 'http://www.rna-society.org/rnainter/download/browse/Homo%20sapiens.zip'
    if not os.path.exists(file):
        print('Database does not exist. Trying to download and extract...')
        if not os.path.exists(zip_file):
            print('Downloading latest archive...')
            with urllib.request.urlopen(url) as response, open(zip_file, 'wb') as f:
                f.write(response.read())
        print('Extracting database file...')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('data/RNAInter/')

    rna_mapping_file = 'data/RNAInter/hgnc.tsv'
    rna_mapping_url = 'ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/hgnc.tsv'
    if not os.path.exists(rna_mapping_file):
        print('RNA mapping table does not exist. Trying to download...')
        with urllib.request.urlopen(rna_mapping_url) as response, open(rna_mapping_file, 'wb') as f:
            f.write(response.read())

    mirna_mapping_file = 'data/RNAInter/tarbase.tsv'
    mirna_mapping_url = 'ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/tarbase.tsv'
    if not os.path.exists(mirna_mapping_file):
        print('MiRNA mapping table does not exist. Trying to download...')
        with urllib.request.urlopen(mirna_mapping_url) as response, open(mirna_mapping_file, 'wb') as f:
            f.write(response.read())

    hgnc_ids_file = 'data/RNAInter/all_hgnc_ids.txt'
    hgnc_ids_url = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_app_sym&status=Approved&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
    if not os.path.exists(hgnc_ids_file):
        print('HGNC mapping table does not exist. Trying to download...')
        with urllib.request.urlopen(hgnc_ids_url) as response, open(hgnc_ids_file, 'wb') as f:
            f.write(response.read())

    network = Network()
    node_lookup = {}
    with io.open(file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t', quotechar='"')
        next(reader, None)
        for row in reader:
            if row[3] == 'Homo sapiens' and row[6] == 'Homo sapiens' and float(row[7]) > 0.9:
                interactor_a_name = row[1]
                interactor_a_type = row[2]
                interactor_b_name = row[4]
                interactor_b_type = row[5]
                interactor_a = add_rna(interactor_a_name, interactor_a_type, node_lookup)
                interactor_b = add_rna(interactor_b_name, interactor_b_type, node_lookup)

                if interactor_a is not None and interactor_b is not None:
                    if interactor_a_type == 'mRNA':
                        gene = Gene([interactor_a.id], [])
                        network.add_node(gene)
                        e = Edge(gene, interactor_a, 'TRANSCRIBES', {})
                        network.add_edge(e)
                    elif interactor_b_type == 'mRNA':
                        gene = Gene([interactor_b.id], [])
                        network.add_node(gene)
                        e = Edge(gene, interactor_b, 'TRANSCRIBES', {})
                        network.add_edge(e)
                    e = Edge(interactor_a, interactor_b, 'REGULATES', {'source': 'RNAInter'})
                    network.add_edge(e)

    network.save('data/RNAInter/graph.json')
