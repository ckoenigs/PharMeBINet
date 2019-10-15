# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv
import sys

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with hetionet pathways with identifier as key and value the name
dict_pathway_hetionet = {}

# dictionary with hetionet pathways with identifier as key and value the xrefs
dict_pathway_hetionet_xrefs = {}

# dictionary with hetionet pathways with name as key and value the identifier
dict_pathway_hetionet_names = {}

#dictionary from own id to new identifier
dict_own_id_to_identifier={}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    results = g.run(query)

    for identifier, names, source, idOwns, in results:
        dict_pathway_hetionet[identifier] = names
        dict_pathway_hetionet_xrefs[identifier] = idOwns
        if idOwns:
            for id in idOwns:
                if not id in dict_own_id_to_identifier:
                    dict_own_id_to_identifier[id]=identifier
        if names:
            for name in names:
                dict_pathway_hetionet_names[name] = identifier
        else:
            print('has no name')
            print(identifier)

    print('number of pathway nodes in hetionet:' + str(len(dict_pathway_hetionet)))

# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w')
csv_not_mapped=csv.writer(file_not_mapped_pathways,delimiter='\t')
csv_not_mapped.writerow(['id','name','source'])

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w')
csv_mapped=csv.writer(file_mapped_pathways,delimiter='\t')
csv_mapped.writerow(['id','id_hetionet','mapped'])

file_multiple_mapped_pathways = open('pathway/multiple_mapped_pathways.tsv', 'w')
csv_mapped_multi=csv.writer(file_multiple_mapped_pathways,delimiter='\t')
csv_mapped_multi.writerow(['id_s','name','source_sources','id_hetionet','source_himmelstein'])


# dictionary where a ctd pathway mapped to multiple pc or wp ids
dict_ctd_to_multiple_pc_or_wp_ids = {}

'''
load all ctd pathways and check if they are in hetionet or not
'''


def load_ctd_pathways_in():
    query = '''MATCH (n:CTDpathway) RETURN n'''
    results = g.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    for pathways_node, in results:
        pathways_id = pathways_node['pathway_id']
        pathways_name = pathways_node['name']
        pathways_id_type = pathways_node['id_type']

        # check if the ctd pathway id is part in the himmelstein xref
        if pathways_id in dict_own_id_to_identifier:
            counter_map_with_id += 1
            # if len(dict_own_id_to_pcid_and_other[pathways_id]) > 1:
            #     print('multiple für identifier')
            csv_mapped.writerow([pathways_id,dict_own_id_to_identifier[pathways_id]],'id')


        elif pathways_name in dict_pathway_hetionet_names:
            counter_map_with_name += 1
            print(pathways_id)
            print('mapped with name')
            csv_mapped.writerow([pathways_id,dict_pathway_hetionet_names[pathways_name]],'name')


        else:
            csv_not_mapped.writerow([pathways_id, pathways_name, pathways_id_type])
            # file_not_mapped_pathways.write(pathways_id+ '\t' +pathways_name+ '\t' + pathways_id_type+ '\n' )

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    # print(dict_mapped_source)



'''
generate connection between mapping pathways of ctd and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file=open('pathway/cypher.cypher','w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/pathway/mapped_pathways.csv" As line Match (d:Pathway{identifier:line.id_hetionet}),(c:CTDpathway{pathway_id:line.id}) Create (d)-[:equal_to_CTD_pathway]->(c) Set d.xrefs= d.xrefs+'CTD', d.ctd="yes", d.ctd_url="http://ctdbase.org/detail.go?type=pathway&acc=%"+line.id;\n'''
    cypher_file.write(query)
    cypher_file.write('begin\n')
    query='''Match (d:Pathway) Where not  exists(d.ctd) Set d.ctd="no";\n '''
    cypher_file.write(query)
    cypher_file.write('commit')



def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from hetionet into a dictionary')

    load_hetionet_pathways_in()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all ctd pathways from neo4j into a dictionary')

    load_ctd_pathways_in()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate new pathways and connect them to ctd ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
