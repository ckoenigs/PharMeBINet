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


# dictionary with hetionet failedReaction with identifier as key and value the name
dict_reaction_hetionet_protein_hetionet = {}

'''
load in Reaction from hetionet in a dictionary
'''


def load_hetionet_reaction_hetionet_protein_in(csv_file, dict_reaction_hetionet_protein_hetionet,
                                                   rela_equal_name, node_hetionet_label):
    query = '''MATCH (p:Reaction)--(o:ReactionLikeEvent_reactome)--(m:PhysicalEntity_reactome)-[a:referenceEntity]-(r:ReferenceEntity_reactome)-[v:%s]-(n:%s) RETURN distinct p.identifier, n.identifier, v.order, v.stoichiometry'''
    query = query % (rela_equal_name, node_hetionet_label)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for reaction_id, protein_id, order, stoichiometry, in results:
        if (reaction_id, protein_id) in dict_reaction_hetionet_protein_hetionet:
            print(reaction_id, protein_id)
            sys.exit("Doppelte reaction-protein kombination")
        dict_reaction_hetionet_protein_hetionet[(reaction_id, protein_id)] = [stoichiometry, order]
        csv_file.writerow([reaction_id, protein_id, order, stoichiometry])
    print('relationships in hetionet:' + str(len(dict_reaction_hetionet_protein_hetionet)))


'''
generate new relationships between reaction of hetionet and protein of hetionet nodes that mapped to reactome
'''


def create_cypher_file( file_path, node_label, rela_name):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:Reaction{identifier:line.id_hetionet_Reaction}),(c:%s{identifier:line.id_hetionet_node}) CREATE (c)-[: %s{order:line.order, stoichiometry:line.stoichiometry, source:"Reactome", resource: ['Reactome'], reactome: "yes", license:"%s", url:"https://reactome.org/content/detail/"+line.id_hetionet_Reaction}]->(d);\n'''
    query = query % (path_of_directory, file_path, node_label, rela_name, license)
    cypher_file.write(query)


def check_relationships_and_generate_file(rela_equal_name, node_hetionet_label,
                                          directory, rela_name):
    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.utcnow())
    print('Load all relationships from hetionet_reaction and hetionet_protein into a dictionary')
    # file for mapped or not mapped identifier
    file_name= directory + '/mapped_Reaction_to_'+rela_name+'.tsv'

    file_mapped_reaction_to_node = open(file_name,'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_reaction_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_hetionet_Reaction', 'id_hetionet_node', 'order', 'stoichiometry'])

    dict_reaction_node = {}

    load_hetionet_reaction_hetionet_protein_in(csv_mapped, dict_reaction_node,
                                                  rela_equal_name, node_hetionet_label)

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file( file_name, node_hetionet_label, rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license reactome edge')

    global cypher_file
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;        2: relationship equal to Hetionet-node
    # 3: name of node in Hetionet;   4: name of directory                5: name of new relationship
    list_of_combinations = [
        ['equal_to_reactome_uniprot', 'Protein', 'IS_INPUT_OF_PiioR']
    ]

    directory = 'physikalEntityEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        rela_equal_name = list_element[0]
        node_hetionet_label = list_element[1]
        rela_name = list_element[2]
        check_relationships_and_generate_file(rela_equal_name,
                                              node_hetionet_label, directory,
                                              rela_name)
    cypher_file.close()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
