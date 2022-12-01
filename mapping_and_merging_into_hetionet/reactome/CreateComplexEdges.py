
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


# dictionary with pharmebinet failedReaction with identifier as key and value the name
dict_complex_pharmebinet_node_pharmebinet = {}

'''
load in all complex-data from pharmebinet in a dictionary
'''


def load_pharmebinet_complex_pharmebinet_node_in(csv_file, dict_complex_pharmebinet_node_pharmebinet,
                                           new_relationship,
                                           node_reactome_label,  node_pharmebinet_label, direction1,
                                           direction2):
    query = '''MATCH (p:MolecularComplex)-[:equal_to_reactome_complex]-(r:Complex_reactome)%s[v:%s]%s(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, n.displayName'''
    query = query % (
        direction1, new_relationship, direction2, node_reactome_label,  node_pharmebinet_label)
    results = graph_database.run(query)
    print(query)
    # for id1, id2, order, stoichiometry, in results:
    for complex_id, node_id, order, stoichiometry, displayName, in results:
        if "ReferenceEntity" in query:
            displayName = displayName.split("[")
            compartment = displayName[1]
            compartment = compartment.replace("]", "")
            if (complex_id, node_id) not in dict_complex_pharmebinet_node_pharmebinet:
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)] = [stoichiometry, order, set([compartment])]
                continue
            else:
                # print(complex_id, node_id)
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)][2].add(compartment)
                # print(compartment)

        else:
            # if (complex_id, node_id) in dict_complex_pharmebinet_node_pharmebinet:
            #     print(complex_id, node_id)
            #     sys.exit("Doppelte Kombination")
            dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)] = [stoichiometry, order]
            csv_file.writerow([complex_id, node_id, order, stoichiometry])

    if "ReferenceEntity" in query:
        for (complex_id, node_id), [stoichiometry, order, compartment] in dict_complex_pharmebinet_node_pharmebinet.items():
            csv_file.writerow([complex_id, node_id, order, stoichiometry, "|".join(compartment)])
    print('number of complex-' + node_reactome_label + ' relationships in pharmebinet:' + str(
        len(dict_complex_pharmebinet_node_pharmebinet)))


'''
generate new relationships between complex of pharmebinet and complex of pharmebinet nodes that mapped to reactome 
'''


def create_cypher_file(file_path, node_label, rela_name, direction1, direction2):
    if node_label == "Protein" or node_label == "Chemical":
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:MolecularComplex{identifier:line.id_pharmebinet_Complex}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, source:'Reactome', url:"https://reactome.org/content/detail/"+line.id_pharmebinet_Complex, compartments: split(line.compartment, "|"), resource: ['Reactome'], reactome: "yes", license:"CC BY 4.0"}]%s(c);\n'''
    else:
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:MolecularComplex{identifier:line.id_pharmebinet_Complex}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes", source:'Reactome', url:"https://reactome.org/content/detail/"+line.id_pharmebinet_Complex, license:"CC BY 4.0"}]%s(c);\n'''
    query = query % (path_of_directory, file_path, node_label, direction1, rela_name, direction2)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label,  node_pharmebinet_label,
                                          directory, rela_name, direction1, direction2):
    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet_Complex and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/mapped_Complex_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'

    file_mapped_complex_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_complex_to_node, delimiter='\t', lineterminator='\n')

    if "Chemical" in node_pharmebinet_label or "Protein" in node_pharmebinet_label:
        csv_mapped.writerow(['id_pharmebinet_Complex', 'id_pharmebinet_node', 'order', 'stoichiometry', 'compartment'])
    else:
        csv_mapped.writerow(['id_pharmebinet_Complex', 'id_pharmebinet_node', 'order', 'stoichiometry'])
    dict_Complex_node = {}

    load_pharmebinet_complex_pharmebinet_node_in(csv_mapped, dict_Complex_node, new_relationship,
                                           node_reactome_label, node_pharmebinet_label, direction1, direction2)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, node_pharmebinet_label, rela_name, direction1, direction2)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome reaction')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;
    # 2: name of node in PharMeBINet;       3: name of new relationship  4: relationship direction left
    # 5: relationship direction right
    list_of_combinations = [
        ['input', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'IS_INPUT_RLEiiMC', '<-', '-'],

        ['output', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'IS_OUTPUT_RLEioMC', '<-', '-'],

        ['requiredInputComponent', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent',
         'IS_REQUIRED_INPUT_COMPONENT_RLEiricMC', '<-', '-'],

        ['compartment', 'GO_CellularComponent_reactome', 'CellularComponent',
         'IS_IN_COMPARTMENT_CCiicMC', '-', '->'],
        ['includedLocation', 'GO_CellularComponent_reactome', 'CellularComponent',
         'IS_INCLUDED_LOCATION_CCiilMC', '-', '->'],
        ['goCellularComponent', 'GO_CellularComponent_reactome', 'CellularComponent',
         'IS_CELLULAR_COMPONENT_CCiccMC', '-', '->'],

        ['hasComponent', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'Chemical',
         'HAS_COMPONENT_MChcCH', '-', '->'],
        ['hasComponent', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'Protein',
         'HAS_COMPONENT_MChcP', '-', '->'],
        ['hasComponent', 'Complex_reactome', 'MolecularComplex',
         'HAS_COMPONENT_MChcMC', '-', '->'],

        ['inferredTo', 'Complex_reactome', 'MolecularComplex',
         'HAS_EFFECT_ON_MCheMC', '-', '->'],

        ['regulator', 'Regulation_reactome', 'Regulation', 'HAS_REGULATOR_RGhrMC', '<-', '-'],
        ['activeUnit', 'Regulation_reactome', 'Regulation', 'HAS_ACTIVE_UNIT_RGhauMC', '<-', '-'],

        ['disease', 'Disease_reactome', 'Disease', 'LEADS_TO_MCltD', '-', '->'],
    ]

    directory = 'ComplexEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        node_pharmebinet_label = list_element[2]
        rela_name = list_element[3]
        direction1 = list_element[4]
        direction2 = list_element[5]
        check_relationships_and_generate_file(new_relationship, node_reactome_label,
                                              node_pharmebinet_label, directory,
                                              rela_name, direction1, direction2)
    cypher_file.close()

    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
