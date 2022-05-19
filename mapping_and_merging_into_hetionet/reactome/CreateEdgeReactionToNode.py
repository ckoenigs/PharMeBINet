
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
                                                  node_reactome_label,  node_hetionet_label):
    query = '''MATCH (p:Reaction)-[:equal_to_reactome_reaction]-(r:Reaction_reactome)-[v:%s]->(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''
    query = query % (new_relationship, node_reactome_label,  node_hetionet_label)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for failedreaction_id, node_id, order, stoichiometry, in results:
        if (failedreaction_id, node_id) in dict_failedReaction_hetionet_node_hetionet:
            print(failedreaction_id, node_id)
            sys.exit("Doppelte reaction-Disease Kombination")
        dict_failedReaction_hetionet_node_hetionet[(failedreaction_id, node_id)] = [stoichiometry, order]
        csv_file.writerow([failedreaction_id, node_id, order, stoichiometry])
    print('number of reaction-' + node_reactome_label + ' relationships in hetionet:' + str(
        len(dict_failedReaction_hetionet_node_hetionet)))


'''
generate new relationships between pathways of hetionet and FailedReaction of hetionet nodes that mapped to reactome 
'''


def create_cypher_file(directory, file_path, node_label, rela_name):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:Reaction{identifier:line.id_hetionet_Reaction}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)-[: %s{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes", license:"%s", source:"Reactome", url:"https://reactome.org/content/detail/"+line.id_hetionet_Reaction}]->(c);\n'''
    query = query % (path_of_directory, file_path, node_label, rela_name, license)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label,  node_hetionet_label,
                                          directory, rela_name):
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from hetionet_failedReaction and hetionet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/mapped_Reaction_to_' + node_reactome_label + '_' + rela_name + '.tsv'

    file_mapped_failedreaction_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_failedreaction_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_hetionet_Reaction', 'id_hetionet_node', 'order', 'stoichiometry'])

    dict_failedReaction_node = {}

    load_hetionet_failedreaction_hetionet_node_in(csv_mapped, dict_failedReaction_node, new_relationship,
                                                  node_reactome_label,
                                                   node_hetionet_label)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(directory, file_name, node_hetionet_label, rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path reactome reaction and license')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;        2: relationship equal to Hetionet-node
    # 3: name of node in Hetionet;   4: name of new relationship
    list_of_combinations = [
        ['disease', 'Disease_reactome',  'Disease', 'LEADS_TO_RLEltD'],
        ['compartment', 'GO_CellularComponent_reactome',  'CellularComponent',
         'IN_COMPARTMENT_RLEicCC'],
        ['precedingEvent', 'Pathway_reactome',  'Pathway', 'PRECEDING_REACTION_RLEprPW'],
        ['precedingEvent', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'PRECEDING_REACTION_RLEprRLE'],
        ['inferredTo', 'ReactionLikeEvent_reactome',  'ReactionLikeEvent', 'HAS_EFFECT_ON_RLEheoRLE'],
        ['normalReaction', 'ReactionLikeEvent_reactome',  'ReactionLikeEvent', 'IS_NORMAL_REACTION_RLEinrRLE'],
        ['reverseReaction', 'ReactionLikeEvent_reactome',  'ReactionLikeEvent', 'REVERSE_REACTION_RLErrRLE'],
        ['goBiologicalProcess', 'GO_BiologicalProcess_reactome',  'BiologicalProcess', 'OCCURS_IN_RLEoiBP']
    ]

    directory = 'FailedReactionEdges'
    cypher_file = open('output/cypher_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        node_hetionet_label = list_element[2]
        rela_name = list_element[3]
        check_relationships_and_generate_file(new_relationship, node_reactome_label,
                                              node_hetionet_label, directory,
                                              rela_name)
    cypher_file.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
