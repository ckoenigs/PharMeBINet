# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 09:43:28 2017

@author: ckoenigs
"""

# dictionary with all drugbank ids and a list with name, inchi, inchi key
dict_drugbank = {}

'''
Load drugbank id, name, inchi, inchikey in a dictionary
properties:
    0:drugbank_id
    1:name	
    2:type	
    3:groups	
    4:atc_codes	
    5:categories	
    6:inchikey	
    7:inchi	
    8:inchikeys	
    9:synonyms	
    10:unii	
    11:uniis
    12:external_identifiers	
    13:extra_names
    14:brands
    15:molecular_forula	
    16:molecular_formular_experimental	
    17:gene_sequence	
    18:amino_acid_sequence	
    19:sequence
    20:description
'''


def load_all_drugbank_ids_in_dictionary(path):
    f = open(path + '../drugbank/data/durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv', 'r')
    for line in f:
        if line.split('\t')[0][0:2] == 'DB':
            drugbank_id = line.split('\t')[0]
            name = line.split('\t')[1]
            inchikey = line.split('\t')[6]
            inchi = line.split('\t')[7]
            dict_drugbank[drugbank_id] = [name, inchi, inchikey]

'''
return all name, inchi and inchikey if the drugbank is in the file
'''
def get_drugbank_information(drugbank_id):
    result = dict_drugbank[drugbank_id] if drugbank_id in dict_drugbank else ['', '', '']
    return result
