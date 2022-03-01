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
dict_complex_hetionet_node_hetionet = {}

'''
load in all complex-data from hetionet in a dictionary
'''


def load_hetionet_complex_hetionet_node_in(csv_file, dict_complex_hetionet_node_hetionet,
                                              new_relationship,
                                              node_reactome_label, rela_equal_name, node_hetionet_label, direction1,
                                              direction2):
    query = '''MATCH (p:MolecularComplex)-[:equal_to_reactome_complex]-(r:Complex_reactome)%s[v:%s]%s(n:%s)-[:%s]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, n.displayName'''
    query = query % (
    direction1, new_relationship, direction2, node_reactome_label, rela_equal_name, node_hetionet_label)
    results = graph_database.run(query)
    print(query)
    # for id1, id2, order, stoichiometry, in results:
    for complex_id, node_id, order, stoichiometry, displayName, in results:
        if "ReferenceEntity" in query:
            displayName = displayName.split("[")
            compartment = displayName[1]
            compartment = compartment.replace("]", "")
            if (complex_id, node_id) not in dict_complex_hetionet_node_hetionet:
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)] = [stoichiometry, order, set([compartment])]
                continue
            else:
                print(complex_id, node_id)
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)][2].add(compartment)
                print(compartment)

        else:
            # if (complex_id, node_id) in dict_complex_hetionet_node_hetionet:
            #     print(complex_id, node_id)
            #     sys.exit("Doppelte Kombination")
            dict_complex_hetionet_node_hetionet[(complex_id, node_id)] = [stoichiometry, order]
            csv_file.writerow([complex_id, node_id, order, stoichiometry])

    if "ReferenceEntity" in query:
        for (complex_id,node_id),[stoichiometry, order, compartment] in dict_complex_hetionet_node_hetionet.items():
            csv_file.writerow([complex_id, node_id, order, stoichiometry, "|".join(compartment)])
    print('number of complex-' + node_reactome_label + ' relationships in hetionet:' + str(
        len(dict_complex_hetionet_node_hetionet)))


'''
generate new relationships between complex of hetionet and complex of hetionet nodes that mapped to reactome 
'''


def create_cypher_file(file_path, node_label, rela_name, direction1, direction2):
    if node_label == "Chemical":
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:MolecularComplex{identifier:line.id_hetionet_Complex}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, compartments: split(line.compartment, "|"), resource: ['Reactome'], source:'Reactome', url:"https://reactome.org/content/detail/"+line.id_hetionet_Complex, reactome: "yes"}]%s(c);\n'''
    else:
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:MolecularComplex{identifier:line.id_hetionet_Complex}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], source:'Reactome', url:"https://reactome.org/content/detail/"+line.id_hetionet_Complex, reactome: "yes"}]%s(c);\n'''
    query = query % (path_of_directory, file_path, node_label, direction1, rela_name, direction2)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label, rela_equal_name, node_hetionet_label,
                                          directory, rela_name, direction1, direction2):
    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.utcnow())
    print('Load all relationships from hetionet_Complex and hetionet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/mapped_Complex_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'

    file_mapped_complex_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_complex_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_hetionet_Complex', 'id_hetionet_node', 'order', 'stoichiometry'])

    dict_Complex_node = {}

    load_hetionet_complex_hetionet_node_in(csv_mapped, dict_Complex_node, new_relationship,
                                              node_reactome_label,
                                              rela_equal_name, node_hetionet_label, direction1, direction2)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file( file_name, node_hetionet_label, rela_name, direction1, direction2)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome reaction')

    global cypher_file
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;        2: relationship equal to Hetionet-node
    # 3: name of node in Hetionet;   4: name of directory                5: name of new relationship
    list_of_combinations = [
        ['input', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction', 'IS_INPUT_RiiCo', '<-', '-'],
        ['input', 'Polymerisation_reactome', 'equal_to_reactome_polymerisation', 'Polymerisation', 'IS_INPUT_PiiCo', '<-', '-'],
        ['input', 'BlackBoxEvent_reactome', 'equal_to_reactome_blackBoxEvent', 'BlackBoxEvent', 'IS_INPUT_BiiCo', '<-', '-'],
        ['input', 'FailedReaction_reactome', 'equal_to_reactome_failedreaction', 'FailedReaction', 'IS_INPUT_FiiCo', '<-', '-'],
        ['input', 'Depolymerisation_reactome', 'equal_to_reactome_depolymerisation', 'Depolymerisation', 'IS_INPUT_DiiCo', '<-', '-'],

        ['output', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction', 'IS_OUTPUT_RioCo', '<-', '-'],
        ['output', 'Polymerisation_reactome', 'equal_to_reactome_polymerisation', 'Polymerisation', 'IS_OUTPUT_PioCo', '<-', '-'],
        ['output', 'BlackBoxEvent_reactome', 'equal_to_reactome_blackBoxEvent', 'BlackBoxEvent', 'IS_OUTPUT_BioCo', '<-', '-'],
        ['output', 'Depolymerisation_reactome', 'equal_to_reactome_depolymerisation', 'Depolymerisation', 'IS_OUTPUT_DioCo', '<-', '-'],

        ['requiredInputComponent', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction', 'IS_REQUIRED_INPUT_COMPONENT_RiricCo', '<-', '-'],
        ['requiredInputComponent', 'Polymerisation_reactome', 'equal_to_reactome_polymerisation', 'Polymerisation', 'IS_REQUIRED_INPUT_COMPONENT_PiricCo', '<-', '-'],
        ['requiredInputComponent', 'BlackBoxEvent_reactome', 'equal_to_reactome_blackBoxEvent', 'BlackBoxEvent', 'IS_REQUIRED_INPUT_COMPONENT_BiricCo', '<-', '-'],
        ['requiredInputComponent', 'FailedReaction_reactome', 'equal_to_reactome_failedreaction', 'FailedReaction', 'IS_REQUIRED_INPUT_COMPONENT_FiricCo', '<-', '-'],

        ['compartment', 'GO_CellularComponent_reactome', 'equal_to_reactome_gocellcomp', 'CellularComponent',
         'IS_IN_COMPARTMENT_CoiicCe', '-', '->'],
        ['includedLocation', 'GO_CellularComponent_reactome', 'equal_to_reactome_gocellcomp', 'CellularComponent',
         'IS_INCLUDED_LOCATION_CoiiLCe', '-', '->'],
        ['goCellularComponent', 'GO_CellularComponent_reactome', 'equal_to_reactome_gocellcomp', 'CellularComponent',
         'IS_CELLULAR_COMPONENT_CoiccCe', '-', '->'],

        ['hasComponent', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'equal_to_reactome_drug', 'Chemical',
         'HAS_COMPONENT_CoirC', '-', '->'],
        ['hasComponent', 'Complex_reactome', 'equal_to_reactome_complex', 'MolecularComplex',
         'HAS_COMPONENT_CoirCo', '-', '->'],

        ['inferredTo', 'Complex_reactome', 'equal_to_reactome_complex', 'MolecularComplex',
         'HAS_EFFECT_ON_CoheoCo', '-', '->'],

        ['regulator', 'Regulation_reactome', 'equal_to_reactome_regulation', 'Regulation',
         'HAS_REGULATOR_RGhrCo', '<-', '-'],
        ['activeUnit', 'Regulation_reactome', 'equal_to_reactome_regulation', 'Regulation',
         'HAS_ACTIVE_UNIT_RGhauCo', '<-', '-'],

        ['disease', 'Disease_reactome', 'equal_to_reactome_disease', 'Disease', 'LEADS_TO_ColtD', '-', '->'],
    ]

    directory = 'ComplexEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        rela_equal_name = list_element[2]
        node_hetionet_label = list_element[3]
        rela_name = list_element[4]
        direction1 = list_element[5]
        direction2 = list_element[6]
        check_relationships_and_generate_file(new_relationship, node_reactome_label, rela_equal_name,
                                              node_hetionet_label, directory,
                                              rela_name, direction1, direction2)
    cypher_file.close()

    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
