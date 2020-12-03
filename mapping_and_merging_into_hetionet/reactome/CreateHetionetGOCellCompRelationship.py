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
dict_pathway_hetionet_cellcomp_hetionet = {}

#dictionary
dict_cellcomp_cellcomp = {}

'''
load in all pathways from hetionet in a dictionary
'''

def load_hetionet_pathways_hetionet_cellcomp_in(query, dict_pair, csv_file):
    #query, dict_pair, csv_file

    query = '''MATCH (p:Pathway)-[:equal_to_reactome_pathway]-(r:Pathway_reactome)-[v:compartment]-(n:GO_CellularComponent_reactome)-[:equal_to_reactome_gocellcomp]-(b:CellularComponent) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''

    # query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    #graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    results = graph_database.run(query)

    #results werden einzeln durchlaufen
    # for id1, id2, order, stoichiometry, in results:
    for pathway_id, gocellcomp_id, order, stoichiometry, in results:
        # if (id1,id2) in dict_pair:
        if (pathway_id, gocellcomp_id) in dict_pathway_hetionet_cellcomp_hetionet:
            print(pathway_id, gocellcomp_id)
            sys.exit("Doppelte cellcomp-Pathway Kombination")
        dict_pathway_hetionet_cellcomp_hetionet[(pathway_id, gocellcomp_id)] = gocellcomp_id
        csv_file.writerow([pathway_id, gocellcomp_id, order, stoichiometry])
    print('number of pathway-cellcomp relationships in hetionet:' + str(len(dict_pathway_hetionet_cellcomp_hetionet)))

# file for mapped or not mapped identifier

file_mapped_pathways_to_gocellcomp = open('GO_CellCompRelationships/mapped_pathways_to_gocellcomp.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_pathways_to_gocellcomp, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id_hetionet_cellcomp_1','id_hetionet_cellcomp_2','order','stoichiometry'])

'''
generate new relationships between pathways of hetionet and go_cellularComponent of hetionet nodes that mapped to reactome 
[:equal_to_reactome_pathway], [:equal_to_reactome_gocellcomp]
'''


def create_cypher_file():
    cypher_file = open('GO_CellCompRelationships/cypher.cypher','w', encoding="utf-8")
    #mappt die Knoten, die es in hetionet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/GO_CellCompRelationships/mapped_pathways_to_gocellcomp.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Pathway{identifier:line.id_hetionet_pathway}),(c:CellularComponent{identifier:line.id_hetionet_cellcomp}) CREATE (d)-[: has_GOCellularComponent{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes"}]->(c);\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)


    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/GO_CellCompRelationships/mapped_pathways_to_gocellcomp.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Pathway{identifier:line.id_hetionet_pathway}),(c:CellularComponent{identifier:line.id_hetionet_cellcomp}) CREATE (d)-[: has_GOCellularComponent{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes"}]->(c);\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)

def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all relationships from hetionet_pathway and hetionet_cellcomp into a dictionary')
    query = '''MATCH (p:Pathway)-[:equal_to_reactome_pathway]-(r:Pathway_reactome)-[v:compartment]-(n:GO_CellularComponent_reactome)-[:equal_to_reactome_gocellcomp]-(b:CellularComponent) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''

    query = '''MATCH (p:CellularComponent)-[:equal_to_reactome_gocellcomp]-(r:GO_CellularComponent_reactome)-[v:surroundedBy]->(n:GO_CellularComponent_reactome)-[:equal_to_reactome_gocellcomp]-(b:CellularComponent) Create (p)-[:surroundedBy{stoichiometry:v.stoichiometry, order:v.order, licence: "blub", resource:["Reactome"], source: "Reactom", reactom: "yes"}]->(b) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''

    load_hetionet_pathways_hetionet_cellcomp_in(query, dict_cellcomp_cellcomp, csv_mapped)


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
