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
dict_failedReaction_hetionet_node_hetionet = {}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_failedreaction_hetionet_node_in(csv_file, dict_failedReaction_hetionet_node_hetionet,
                                                  new_relationship,
                                                  node_reactome_label, rela_equal_name, node_hetionet_label):
    query = '''MATCH (p:FailedReaction)-[:equal_to_reactome_failedreaction]-(r:FailedReaction_reactome)-[v:%s]->(n:%s)-[:%s]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''
    query = query % (new_relationship, node_reactome_label, rela_equal_name, node_hetionet_label)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for failedreaction_id, node_id, order, stoichiometry, in results:
        if (failedreaction_id, node_id) in dict_failedReaction_hetionet_node_hetionet:
            print(failedreaction_id, node_id)
            sys.exit("Doppelte failedreaction-Disease Kombination")
        dict_failedReaction_hetionet_node_hetionet[(failedreaction_id, node_id)] = [stoichiometry, order]
        csv_file.writerow([failedreaction_id, node_id, order, stoichiometry])
    print('number of failedreaction-'+node_reactome_label+' relationships in hetionet:' + str(
        len(dict_failedReaction_hetionet_node_hetionet)))


'''
generate new relationships between pathways of hetionet and FailedReaction of hetionet nodes that mapped to reactome 
'''


def create_cypher_file(directory, file_path, node_label, rela_name):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:FailedReaction{identifier:line.id_hetionet_failedReaction}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)-[: %s{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes", license:"%s"}]->(c);\n'''
    query = query % (path_of_directory, file_path, node_label, rela_name, license)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label, rela_equal_name, node_hetionet_label,
                                          directory, rela_name):
    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all relationships from hetionet_failedReaction and hetionet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name= directory + '/mapped_failedReaction_to_'+node_reactome_label+'_'+rela_name+'.tsv'

    file_mapped_failedreaction_to_node = open(file_name,'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_failedreaction_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_hetionet_failedReaction', 'id_hetionet_node', 'order', 'stoichiometry'])

    dict_failedReaction_node = {}

    load_hetionet_failedreaction_hetionet_node_in(csv_mapped, dict_failedReaction_node, new_relationship,
                                                  node_reactome_label,
                                                  rela_equal_name, node_hetionet_label)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file(directory, file_name, node_hetionet_label, rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        license= sys.argv[1]
    else:
        sys.exit('need a path reactome protein')

    global cypher_file
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;        2: relationship equal to Hetionet-node
    # 3: name of node in Hetionet;   4: name of directory                5: name of new relationship
    list_of_combinations = [
        ['disease', 'Disease_reactome', 'equal_to_reactome_disease', 'Disease',
         'LEADS_TO_DISEASE_FltdD'],
        ['compartment', 'GO_CellularComponent_reactome', 'equal_to_reactome_gocellcomp', 'CellularComponent', 'IN_COMPARTMENT_FcCe'],
        ['normalReaction', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction', 'IS_NORMAL_REACTION_FnrR'],
        ['normalReaction', 'BlackBoxEvent_reactome', 'equal_to_reactome_blackBoxEvent', 'BlackBoxEvent', 'IS_NORMAL_REACTION_FnrB'],
        ['precedingEvent', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction', 'PRECEDING_REACTION_FprR'],
        ['inferredTo', 'FailedReaction_reactome', 'equal_to_reactome_failedreaction', 'FailedReaction', 'HAS_EFFECT_ON_FheoF']
    ]

    directory = 'FailedReactionEdges'
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        rela_equal_name = list_element[2]
        node_hetionet_label = list_element[3]
        rela_name = list_element[4]
        check_relationships_and_generate_file(new_relationship, node_reactome_label, rela_equal_name,
                                              node_hetionet_label, directory,
                                              rela_name)
    cypher_file.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
