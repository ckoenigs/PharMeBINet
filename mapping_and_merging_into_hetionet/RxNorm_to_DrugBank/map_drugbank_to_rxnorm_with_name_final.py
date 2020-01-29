# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 15:10:41 2017

@author: ckoenigs
"""

import datetime, csv
import MySQLdb as mdb
from py2neo import Graph


'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global graph
    graph = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))

'''
map drugbank with name to rxnorm
'''

# generate connection to mysql
con = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'RxNorm',use_unicode=True, charset="utf8")

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
count_drugbank_ids = 0
list_rxnorm_id = []
j = 0

g = open('results/name_map_drugbank_to_rxnorm.tsv', 'w',encoding='utf-8')
csv_writer=csv.writer(g,delimiter='\t')
csv_writer.writerow(['drugbank_id','rxnorm_cui'])
create_connection_with_neo4j()

query='''Match (c:Compound) Return c.identifier, c.name, c.synonyms'''
result=graph.run(query)
for drugbank_id, name, synonyms, in result:
    if drugbank_id=='DB08792':
        print('huhu')
    count_drugbank_ids += 1

    name = name.replace("'", "")
    all_name=name

    if synonyms is not None:
        for synonym in synonyms:
            synonym = synonym.replace('[', '').replace(']', '')
            synonym = synonym.replace("'", "")
            synonym = synonym.replace("|", "','")
            all_name = all_name+"','" + synonym


    all_name_utf=all_name.encode('utf-8')
    cur = con.cursor()
    query = ("SELECT RXCUI FROM RXNCONSO WHERE STR in ('%s'); ")
    query = query % (all_name)
    cur.execute(query)

    rxcui_list = []
    for (rxcui,) in cur:
        rxcui_list.append(rxcui)
    rxcui_list = list(set(rxcui_list))
    for rxcui in rxcui_list:
        csv_writer.writerow([drugbank_id,rxcui ])
        if not rxcui in list_rxnorm_id:
            list_rxnorm_id.append(rxcui)

    j += 1

print('number of drugbank ids:' + str(j - 1))
print('number of differnt rxnorm ids:' + str(len(list_rxnorm_id)))

print(datetime.datetime.utcnow())
