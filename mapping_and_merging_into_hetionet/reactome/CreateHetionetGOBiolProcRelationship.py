# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet pathways with identifier as key and value the name
dict_pathway_hetionet_biolproc_hetionet = {}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_hetionet_biolproc_in():
    query = '''MATCH (p:Pathway)-[:equal_to_reactome_pathway]-(r:Pathway_reactome)-[v:goBiologicalProcess]-(n:GO_BiologicalProcess_reactome)-[:equal_to_reactome_gobiolproc]-(b:BiologicalProcess) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''
    # query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    # graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for pathway_id, gobiolproc_id, order, stoichiometry, in results:
        if (pathway_id, gobiolproc_id) in dict_pathway_hetionet_biolproc_hetionet:
            print(pathway_id, gobiolproc_id)
            sys.exit("Doppelte biolproc-Pathway Kombination")
        dict_pathway_hetionet_biolproc_hetionet[(pathway_id, gobiolproc_id)] = gobiolproc_id
        csv_mapped.writerow([pathway_id, gobiolproc_id, order, stoichiometry])
    print('number of pathway-biolproc relationships in hetionet:' + str(len(dict_pathway_hetionet_biolproc_hetionet)))


# file for mapped or not mapped identifier

file_mapped_pathways_to_gobiolproc = open('GO_BiolProcRelationships/mapped_pathways_to_gobiolproc.tsv', 'w',
                                          encoding="utf-8")
csv_mapped = csv.writer(file_mapped_pathways_to_gobiolproc, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id_hetionet_pathway', 'id_hetionet_biolproc', 'order', 'stoichiometry'])

'''
generate new relationships between pathways of hetionet and go_biologicalProcess of hetionet nodes that mapped to reactome 
[:equal_to_reactome_pathway], [:equal_to_reactome_gobiolproc]
'''


def create_cypher_file():
    cypher_file = open('GO_BiolProcRelationships/cypher.cypher', 'w', encoding="utf-8")
    # mappt die Knoten, die es in hetionet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/GO_BiolProcRelationships/mapped_pathways_to_gobiolproc.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Pathway{identifier:line.id_hetionet_pathway}),(c:BiologicalProcess{identifier:line.id_hetionet_biolproc}) CREATE (d)-[: has_GOBiologicalProcess{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes"}]->(c);\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all relationships from hetionet_pathway and hetionet_biolproc into a dictionary')

    load_hetionet_pathways_hetionet_biolproc_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
