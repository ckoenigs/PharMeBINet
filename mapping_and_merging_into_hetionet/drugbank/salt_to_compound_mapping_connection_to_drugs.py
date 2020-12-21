# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:07:43 2019

@author: ckoenigs
"""

import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases  # , authenticate

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of not mapped compound inchikey to node
dict_not_mapped_compound = {}

# dictionary not mapped compound names to node
dict_not_mapped_compound_name = {}

'''
Load all compounds which did not mapped and upload them into a dictionary with inchikey as key
and also in a dictionary where the name is the key
'''


def find_not_mapped_compounds_and_add_to_dict():
    query = '''MATCH (n:Compound) WHere not exists(n.drugbank) RETURN n'''
    result = g.run(query)
    for node, in result:
        # print(node)
        inchikey = node['inchikey'] if 'inchikey' in node else ''
        # print(inchikey)
        inchikey = inchikey.split('=')[1] if '=' in inchikey else inchikey
        dict_not_mapped_compound[inchikey] = dict(node)
        if 'name' in node:
            dict_not_mapped_compound_name[node['name'].lower()] = dict(node)
    print(len(dict_not_mapped_compound))


# label of salt
label_of_salt = 'Salt_DrugBank'

# name of the csv file
file_node = 'salt_compound'

# name rela file
file_rela = 'salt_compound_rela'

'''
Create cypher and csv files for nodes and relationships
'''


def create_cypher_and_csv_files():
    # open cypher file
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    # get properties of salt nodes
    query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    query = query % (label_of_salt)
    result = g.run(query)
    header = []
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/drugbank/salts/%s.csv" As line Fieldterminator '\\t' Match '''
    part = query_start + '''(a:%s {identifier:line.identifier}) Create (b:Compound :Salt{'''
    part = part % (file_node, label_of_salt)
    for property, in result:
        part += property + ':line.' + property + ', '
        header.append(property)
    query = part + ' source:"DrugBank", license:"%s" ,drugbank:"yes", resource:["DrugBank"], url:"https://www.drugbank.ca/salts/"+line.identifier}) Create (b)-[:equal_to_drugbank]->(a);\n'
    query = query % (license)

    cypher_file.write(query)
    cypher_file.close()
    node_file = open('salts/' + file_node + '.csv', 'w')
    rela_file = open('salts/' + file_rela + '.csv', 'w')
    global csv_node, csv_rela
    csv_node = csv.DictWriter(node_file, fieldnames=header, delimiter='\t')
    csv_node.writeheader()
    cypher_rela = open('output/cypher_rela.csv', 'a', encoding='utf-8')
    rela_header = ['salt_id', 'compound_id']
    query_rela = query_start + ' (b:Compound :Salt{identifier:line.salt_id}), (a:Compound {identifier:line.compound_id}) Create (a)-[r:PART_OF_CpS{license:"%s", source:"DrugBank", resource:["DrugBank"], drugbank:"yes" }]->(b);\n'
    query_rela = query_rela % (file_rela, license)
    cypher_rela.write(query_rela)
    cypher_rela.close()
    csv_rela = csv.writer(rela_file, delimiter='\t')
    csv_rela.writerow(rela_header)

    # delete compound nodes which are whether drugbank compound nor salt
    # this must be the last step of the compound integration, because else the merge nodes are also removed and this would be a problem
    cypher_delete_file = open('cypher_delete_compound.cypher', 'w')
    query = '''Match (c:Compound) Where not exists(c.drugbank) Detach Delete c;'''
    cypher_delete_file.write(query)
    cypher_delete_file.close()


# bash shell for merge doids into the mondo nodes
bash_shell = open('merge_nodes_salt.sh', 'w')
bash_shell.write('#!/bin/bash\n')

# the new table for unii drugbank pairs
unii_drugbank_table_file = open('data/map_unii_to_drugbank_id.tsv', 'a')
csv_unii_drugbank_table = csv.writer(unii_drugbank_table_file, delimiter='\t')

'''
Add a merge to the bash file
'''


def add_merge_to_sh_file(dict_not_mapped, mapped_value, node_id):
    compound = dict_not_mapped[mapped_value]
    print(compound)
    compound_id = compound['identifier']
    # if it mapped to a not mapped compound
    text = 'python3 ../add_information_from_a_not_existing_node_to_existing_node.py %s %s %s\n' % (
        compound_id, node_id, 'Compound')
    bash_shell.write(text)
    text = '''now=$(date +"%F %T")\n echo "Current time: $now"\n'''
    bash_shell.write(text)


'''
Gather all salt and make a new csv to integrate them as compound into neo4j
also check if a salt is on of the not mapped compounds 
Prepare the csv for salt integration, because they are not in hetionet they can be directly integrated
also check on the drugs which did not mapped, because some of them might be now salts

{identifier:"DBSALT002847"}
'''


def prepare_node_csv():
    query = '''MATCH (n:Salt_DrugBank) RETURN n'''
    result = g.run(query)
    for node, in result:
        csv_node.writerow(node)
        node_id = node['identifier']
        inchikey = node['inchikey']
        name = node['name'].lower()
        if 'unii' in node:
            unii = node['unii']
            csv_unii_drugbank_table.writerow([unii, node_id])
        # check if this salt is as a drugbank id  already included
        # if so merge this nodes together
        if inchikey in dict_not_mapped_compound:
            add_merge_to_sh_file(dict_not_mapped_compound, inchikey, node_id)
        elif name in dict_not_mapped_compound_name:
            add_merge_to_sh_file(dict_not_mapped_compound_name, name, node_id)


'''
Generate fill the rela csv file
'''


def fill_rela_csv():
    query = '''MATCH (n:Salt_DrugBank)-[:has_ChS]-(b:Compound_DrugBank) RETURN n.identifier, b.identifier'''
    result = g.run(query)
    for salt_id, compound_id, in result:
        csv_rela.writerow([salt_id, compound_id])


def main():
    # path to directory of project
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need a license')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]
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
