# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:07:43 2019

@author: ckoenig
"""

from py2neo import Graph, authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# dictionary of not mapped compound inchikey to node
dict_not_mapped_compound={}

'''
Load all compounds which did not mapped and upload them into da dictionary
'''
def find_not_mapped_compounds_and_add_to_dict():
    query='''MATCH (n:Compound) WHere not exists(n.drugbank) RETURN n'''
    result=g.run(query)
    for node, in result:
        inchikey=node['inchikey']
        dict_not_mapped_compound[inchikey]=dict(node)

#label of salt
label_of_salt='Salt_DrugBank'

# name of the csv file
file_node='salt_compound'

#name rela file
file_rela='salt_compound_rela'

'''
Create cypher and csv files for nodes and relationships
'''
def create_cypher_and_csv_files():
    # open cypher file
    cypher_file=open('cypher_salt.cypher','w')
    # get properties of salt nodes
    query='''MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    query=query %(label_of_salt)
    result=g.run(query)
    header=[]
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ncbi_gene/drugbank/output/%s.csv" As line Fieldterminator '\\t' Match (a:Salt_DrugBank {identifier:line.identifier}) Create (b:Compound :Salt{'''
    query_start=query_start %(file_node, label_of_salt)
    for property, in result:
        header.append(property)
        query_start+= property+':line.'+property+', '
    query=query_start+' source:"DrugBank", drugbank="yes", resource:["DrugBank"], url:"https://www.drugbank.ca/salts/"+line.identifier}) Create (b)-[:equal_to_drugbank]->(a)'

    cypher_file.write(query)
    node_file=open('output/'+file_node+'.csv', 'w')
    rela_file=open('output/'+file_rela+'.csv','w')
    global csv_node, csv_rela
    csv_node=csv.DictWriter(node_file,fieldnames=header,delimiter='\t')
    rela_header=['salt_id','compound_id']
    csv_rela=csv.writer(rela_file,delimiter='\t')
    csv_rela.writerow(rela_header)


#bash shell for merge doids into the mondo nodes
bash_shell=open('merge_nodes_salt.sh','w')
bash_shell.write('#!/bin/bash\n')

'''
Gather all salt and make a new csv to integrate them as compound into neo4j
also check if a salt is on of the not mapped compounds 
Prepare the csv for salt integration, because they are not in hetionet they can be directly integrated
also check on the drugs which did not mapped, because some of them might be now salts
'''
def prepare_node_csv():
    query='''MATCH (n:Salt_DrugBank) RETURN n'''
    result=g.run(query)
    for node, in result:
        csv_node.writerow(node)
        node_id=node['identifier']
        inchikey=node['inchikey']
        if inchikey in dict_not_mapped_compound:
            compound_id=dict_not_mapped_compound[inchikey]['identifier']
            #if it mapped to a not mapped compound
            text = 'python ../add_information_from_a_not_existing_node_to_existing_node.py %s %s %s\n' % (
                compound_id, node_id, 'Compound')
            bash_shell.write(text)
            text = '''now=$(date +"%F %T")\n echo "Current time: $now"\n'''
            bash_shell.write(text)

'''
Generate fill the rela csv file
'''
def fill_rela_csv():
    query = '''MATCH (n:Salt_DrugBank)-[:has_ChS]-(b:Compound_DrugBank) RETURN n.identifier, b.identifier'''
    result = g.run(query)
    for salt_id, compound_id, in result:
        csv_rela.writerow([salt_id, compound_id])

def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('get compound which are not ind drugbank drugs')

    find_not_mapped_compounds_and_add_to_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('open and create cypher and csv files')

    create_cypher_and_csv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('prepare node csv and make bash for merging not mapped compounds to salt')

    prepare_node_csv()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('create rela')

    fill_rela_csv()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()