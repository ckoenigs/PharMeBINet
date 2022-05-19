# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 15:10:41 2017

@author: ckoenigs
"""

import datetime, csv, sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    return create_connection_to_databases.database_connection_neo4j()


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


'''
map drugbank with name to rxnorm
'''

# generate connection to mysql
con = create_connection_to_databases.database_connection_RxNorm()

# dictionary with drugbank as key and value is a list of rxcuis
dict_drugbank_to_rxnorm = {}

print(datetime.datetime.now())

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
count_drugbank_ids = 0
list_rxnorm_id = set()

g = open('results/name_map_drugbank_to_rxnorm.tsv', 'w', encoding='utf-8')
csv_writer = csv.writer(g, delimiter='\t')
csv_writer.writerow(['drugbank_id', 'rxnorm_cui'])
graph = create_connection_with_neo4j()

synonym_to_drugbank_ids = {}

query = '''Match (c:Compound) Where not c:Product Return c.identifier, c.name, c.synonyms'''
result = graph.run(query)
for drugbank_id, name, synonyms, in result:
    count_drugbank_ids += 1

    name = name.replace("'", "").lower()
    if name not in synonym_to_drugbank_ids:
        synonym_to_drugbank_ids[name] = set()
    synonym_to_drugbank_ids[name].add(drugbank_id)

    if synonyms is not None:
        for synonym in synonyms:
            synonym = synonym.replace('[', '').replace(']', '')
            synonym = synonym.replace("'", "")
            for sub_synonym in synonym.split('|'):
                sub_synonym = sub_synonym.lower().strip()
                if sub_synonym not in synonym_to_drugbank_ids:
                    synonym_to_drugbank_ids[sub_synonym] = set()
                synonym_to_drugbank_ids[sub_synonym].add(drugbank_id)

synonym_chunks = list(chunks(list(synonym_to_drugbank_ids.keys()), 4000))
print('number of synonym chunks:', len(synonym_chunks))
set_of_rxcui_drug_bank_pairs = set()
for chunk in synonym_chunks:
    names = "','".join(chunk)
    cur = con.cursor()
    query = "SELECT Distinct STR, RXCUI FROM RXNCONSO WHERE LOWER(STR) COLLATE utf8_bin in ('%s');" % names
    cur.execute(query)

    for (synonym, rxcui) in cur:
        list_rxnorm_id.add(rxcui)
        synonym = synonym.lower().strip()
        for drugbank_id in synonym_to_drugbank_ids[synonym]:
            if (rxcui, drugbank_id) in set_of_rxcui_drug_bank_pairs:
                continue
            csv_writer.writerow([drugbank_id, rxcui])
            set_of_rxcui_drug_bank_pairs.add((rxcui, drugbank_id))

print('number of drugbank ids:', count_drugbank_ids)
print('number of differnt rxnorm ids:', len(list_rxnorm_id))

print(datetime.datetime.now())
