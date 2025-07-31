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


# dictionary with pharmebinet failedReaction with identifier as key and value the name
dict_complex_pharmebinet_node_pharmebinet = {}

'''
load in all complex-data from pharmebinet in a dictionary
'''


def load_pharmebinet_complex_pharmebinet_node_in(csv_file, dict_complex_pharmebinet_node_pharmebinet,
                                                 new_relationship,
                                                 node_reactome_label, node_pharmebinet_label, direction1,
                                                 direction2):
    query = '''MATCH (p:CellType)-[]-(r:CellType_reactome)%s[v:%s]%s(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, n.displayName, n.stId'''
    query = query % (
        direction1, new_relationship, direction2, node_reactome_label, node_pharmebinet_label)
    results = graph_database.run(query)
    print(query)
    # for id1, id2, order, stoichiometry, in results:
    for record in results:
        [complex_id, node_id, order, stoichiometry, displayName, stId] = record.values()
        if "ReferenceEntity" in query:
            displayName = displayName.split("[")
            compartment = displayName[1]
            compartment = compartment.replace("]", "")
            if (complex_id, node_id) not in dict_complex_pharmebinet_node_pharmebinet:
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)] = [stoichiometry, order,
                                                                                    set([compartment]), stId]
                continue
            else:
                # print(complex_id, node_id)
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)][2].add(compartment)
                # print(compartment)

        else:
            # if (complex_id, node_id) in dict_complex_pharmebinet_node_pharmebinet:
            #     print(complex_id, node_id)
            #     sys.exit("Doppelte Kombination")
            dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)] = [stoichiometry, order, stId]
            csv_file.writerow([complex_id, node_id, order, stoichiometry,stId])

    if "ReferenceEntity" in query:
        for (complex_id, node_id), [stoichiometry, order,
                                    compartment, stId] in dict_complex_pharmebinet_node_pharmebinet.items():
            csv_file.writerow([complex_id, node_id, order, stoichiometry, "|".join(compartment), stId])
    print('number of complex-' + node_reactome_label + ' relationships in pharmebinet:' + str(
        len(dict_complex_pharmebinet_node_pharmebinet)))


'''
generate new relationships between complex of pharmebinet and complex of pharmebinet nodes that mapped to reactome 
'''


def create_cypher_file(file_path, node_label, rela_name, direction1, direction2):
    if node_label == "Protein" or node_label == "Chemical":
        query = ''' MATCH (d:CellType{identifier:line.id_pharmebinet}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, source:'Reactome', url:"https://reactome.org/content/detail/"+line.stId, compartments: split(line.compartment, "|"), resource: ['Reactome'], reactome: "yes", license:"CC BY 4.0"}]%s(c)'''
    else:
        query = ''' MATCH (d:CellType{identifier:line.id_pharmebinet}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, resource: ['Reactome'], reactome: "yes", source:'Reactome', url:"https://reactome.org/content/detail/"+line.stId, license:"CC BY 4.0"}]%s(c)'''
    query = query % (node_label, direction1, rela_name, direction2)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/{file_path}',
                                              query)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label, node_pharmebinet_label,
                                          directory, rela_name, direction1, direction2, direction1_integration,
                                          direction2_integration):
    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet_Complex and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/mapped_CellType_to_' + node_pharmebinet_label + '_' + rela_name + '.tsv'

    file_mapped_complex_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_complex_to_node, delimiter='\t', lineterminator='\n')

    if "Chemical" in node_pharmebinet_label or "Protein" in node_pharmebinet_label:
        csv_mapped.writerow(['id_pharmebinet', 'id_pharmebinet_node', 'order', 'stoichiometry', 'compartment', 'stId'])
    else:
        csv_mapped.writerow(['id_pharmebinet', 'id_pharmebinet_node', 'order', 'stoichiometry', 'stId'])
    dict_Complex_node = {}

    load_pharmebinet_complex_pharmebinet_node_in(csv_mapped, dict_Complex_node, new_relationship,
                                                 node_reactome_label, node_pharmebinet_label, direction1, direction2)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, node_pharmebinet_label, rela_name, direction1_integration, direction2_integration)


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

        ['cellType', 'PhysicalEntity_reactome)--(a:ReferenceEntity_reactome', 'Chemical',
         'IS_IN_CELL_TYPE_CHiictCT', '<-', '-', '<-', '-'],
        ['cellType', 'PhysicalEntity_reactome)--(a:ReferenceEntity_reactome', 'Protein',
         'IS_IN_CELL_TYPE_CHiictP', '<-', '-', '<-', '-'],

    ]

    directory = 'CellType'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        node_pharmebinet_label = list_element[2]
        rela_name = list_element[3]
        direction1 = list_element[4]
        direction2 = list_element[5]
        direction1_integration = list_element[6]
        direction2_integration = list_element[7]
        check_relationships_and_generate_file(new_relationship, node_reactome_label, node_pharmebinet_label, directory,
                                              rela_name, direction1, direction2, direction1_integration,
                                              direction2_integration)
    cypher_file.close()
    driver.close()

    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
