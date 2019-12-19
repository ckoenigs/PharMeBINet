# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 15:10:41 2017

@author: ckoenigs
"""

import datetime, csv
import MySQLdb as mdb

'''
map drugbank with name to rxnorm
'''

# generate connection to mysql
con = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'RxNorm')

# dictionary with drugbank as key and value is a list of rxcuis
dict_drugbank_to_rxnorm = {}

print(datetime.datetime.utcnow())

'''
go through all drugbank entries and search for the name in rxnorm 
properties of the file:
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
f = open('drugbank/drugbank_with_synonyms_uniis_extern_ids_molecular_seq_formular.tsv', 'r')
next(f)

count_drugbank_ids = 0
list_rxnorm_id = []
j = 0

g = open('name_map_drugbank_to_rxnorm_2.tsv', 'w')
g.write('drugbank_id \t rxnorm_cui\n')
for line in f:
    splitted = line.split('\t')
    if splitted[0][0:2] == 'DB':
        count_drugbank_ids += 1

        drugbank_id = splitted[0]
        name = splitted[1]
        name = name.replace("'", "")
        synonyms = splitted[9]
        extra_names = splitted[13]
        brands = splitted[14]
        if len(synonyms) > 2:
            synonyms = synonyms.replace('[', '').replace(']', '')
            synonyms = synonyms.replace("'", "")
            synonyms = synonyms.replace("|", "','")
            all_name = name + "','" + synonyms
        else:
            all_name = name
        if len(extra_names) > 2:
            extra_names = extra_names.replace('[', '').replace(']', '')
            extra_names = extra_names.replace("'", "")
            extra_names = extra_names.replace("|", "','")
            all_name = all_name + "','" + extra_names
        if len(brands) > 2:
            brands = brands.replace('[', '').replace(']', '')
            brands = brands.replace("'", "")
            brands = brands.replace("|", "','")
            all_name = all_name + "','" + brands
        all_name = all_name.lower()
        cur = con.cursor()
        query = ("SELECT RXCUI FROM RXNCONSO WHERE STR in ('%s'); ")
        query = query % (all_name)
        cur.execute(query)
        rxcui_list = []
        for (rxcui,) in cur:
            rxcui_list.append(rxcui)
        rxcui_list = list(set(rxcui_list))
        for rxcui in rxcui_list:
            g.write(drugbank_id + '\t' + rxcui + '\n')
            if not rxcui in list_rxnorm_id:
                list_rxnorm_id.append(rxcui)

        j += 1

print('number of drugbank ids:' + str(j - 1))
print('number of differnt rxnorm ids:' + str(len(list_rxnorm_id)))

print(datetime.datetime.utcnow())
