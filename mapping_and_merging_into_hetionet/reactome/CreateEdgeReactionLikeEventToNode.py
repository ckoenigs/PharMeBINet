import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary with pharmebinet reactionLikeEvent with identifier as key and value the name
dict_reactionLikeEvent_pharmebinet_node_pharmebinet = {}

'''
load in all pathways from pharmebinet in a dictionary
'''


def load_pharmebinet_reactionLikeEvent_pharmebinet_node_in(csv_file,
                                                           dict_reactionLikeEvent_pharmebinet_node_pharmebinet,
                                                           new_relationship, node_reactome_label,
                                                           node_pharmebinet_label):
    query = '''MATCH (p:ReactionLikeEvent)-[]-(r:ReactionLikeEvent_reactome)-[v:%s]->(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry'''
    query = query % (new_relationship, node_reactome_label, node_pharmebinet_label)
    print(query)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for record in results:
        [reactionLikeEvent_id, node_id, order, stoichiometry] = record.values()
        if (reactionLikeEvent_id, node_id) in dict_reactionLikeEvent_pharmebinet_node_pharmebinet:
            print(reactionLikeEvent_id, node_id)
            print(dict_reactionLikeEvent_pharmebinet_node_pharmebinet[(reactionLikeEvent_id, node_id)])
            print(order, stoichiometry)
            print("Doppelte reactionLikeEvent-" + node_pharmebinet_label + " Kombination")
            if node_pharmebinet_label == 'Disease':
                continue
            else:
                sys.exit("Doppelte reactionLikeEvent-" + node_pharmebinet_label + " Kombination")
        dict_reactionLikeEvent_pharmebinet_node_pharmebinet[(reactionLikeEvent_id, node_id)] = [stoichiometry, order]
        csv_file.writerow([reactionLikeEvent_id, node_id, order, stoichiometry])
    print('number of reactionLikeEvent-' + node_reactome_label + ' relationships in pharmebinet:' + str(
        len(dict_reactionLikeEvent_pharmebinet_node_pharmebinet)))


'''
generate new relationships between pathways of pharmebinet and reactionLikeEvent of pharmebinet nodes that mapped to reactome 
'''


def create_cypher_file(directory, file_path, node_label, rela_name):
    query = ''' MATCH (d:ReactionLikeEvent{identifier:line.id_pharmebinet_reactionLikeEvent}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)-[: %s{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes", license:"%s", url:"https://reactome.org/content/detail/"+line.id_pharmebinet_reactionLikeEvent, source:"Reactome"}]->(c)'''
    query = query % (node_label, rela_name, license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/{file_path}',
                                              query)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label, node_pharmebinet_label,
                                          directory, rela_name):
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet_reactionLikeEvent and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/mapped_reactionLikeEvent_to_' + node_reactome_label + '_' + rela_name + '.tsv'

    file_mapped_reactionLikeEvent_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_reactionLikeEvent_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_pharmebinet_reactionLikeEvent', 'id_pharmebinet_node', 'order', 'stoichiometry'])

    dict_reactionLikeEvent_node = {}

    load_pharmebinet_reactionLikeEvent_pharmebinet_node_in(csv_mapped, dict_reactionLikeEvent_node, new_relationship,
                                                           node_reactome_label,
                                                           node_pharmebinet_label)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(directory, file_name, node_pharmebinet_label, rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license reactome edge')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;
    # 2: name of node in pharmebinet;   3: name of new relationship
    list_of_combinations = [
        ['disease', 'Disease_reactome', 'Disease', 'LEADS_TO_RLEltdD'],
        ['compartment', 'GO_CellularComponent_reactome', 'CellularComponent', 'IN_COMPARTMENT_RLEicCC'],
        ['precedingEvent', 'Pathway_reactome', 'Pathway', 'PRECEDING_REACTION_RLEprPW'],
        ['normalReaction', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'IS_NORMAL_REACTION_RLEinrRLE'],
        ['precedingEvent', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'PRECEDING_REACTION_RLEprRLE'],
        ['inferredTo', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'HAS_EFFECT_ON_RLEheoRLE'],
        ['reverseReaction', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'REVERSE_REACTION_RLErrRLE'],
        ['inferredTo', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'HAS_EFFECT_ON_RLEheoRLE'],
        ['goBiologicalProcess', 'GO_BiologicalProcess_reactome', 'BiologicalProcess', 'OCCURS_IN_RLEoiBP']
    ]

    directory = 'reactionLikeEventEdge'
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        node_pharmebinet_label = list_element[2]
        rela_name = list_element[3]
        check_relationships_and_generate_file(new_relationship, node_reactome_label, node_pharmebinet_label, directory,
                                              rela_name)
    cypher_file.close()
    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
