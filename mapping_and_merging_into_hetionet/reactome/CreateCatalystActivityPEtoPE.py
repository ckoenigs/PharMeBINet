from py2neo import Graph
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


'''
load in all connected PE from Pharmebinet which are connected through CA where a reference exists
'''


def load_pharmebinet_complex_pharmebinet_node_in(csv_file, set_node1_node2_pharmebinet, start_label, end_label):
    query = '''MATCH (%s)--(:PhysicalEntity_reactome)-[:activeUnit]-(m:CatalystActivity_reactome)-[:physicalEntity]-(:PhysicalEntity_reactome)--(%s) Where (m)--(:CatalystActivityReference_reactome) RETURN p.identifier, b.identifier'''

    query = query % (start_label, end_label)
    results = graph_database.run(query)
    print(query)
    # for id1, id2, order, stoichiometry, in results:
    for record in results:
        [node_id1, node_id2] = record.values()
        if not (node_id1, node_id2) in set_node1_node2_pharmebinet:
            csv_file.writerow([node_id1, node_id2])
            set_node1_node2_pharmebinet.add((node_id1, node_id2))

    print('number of CatalystActivity_reactome relationships in pharmebinet:' + str(
        len(set_node1_node2_pharmebinet)))


'''
generate new relationships between complex of pharmebinet and complex of pharmebinet nodes that mapped to reactome 
'''


def create_cypher_file(file_name, node_label_pharmebinet1, node_label_pharmebinet2, rela_name, direction1, direction2,
                       rela_note_exists):
    query = ''' MATCH (d:%s{identifier:line.id_1}),(c:%s{identifier:line.id_2}) Where not (d)-[:%s]-(c) CREATE (d)%s[:%s{resource: ['Reactome'], url:"https://reactome.org/content/detail/"+line.id_2, reactome: "yes", source:"Reactome", type:"has_component", license:"%s"}]%s(c)'''

    query = query % (node_label_pharmebinet1, node_label_pharmebinet2, rela_note_exists, direction1,
                     rela_name, license, direction2)

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/{file_name}',
                                              query)
    cypher_file.write(query)


def check_relationships_and_generate_file(start_label, end_label, node_label_pharmebinet1,
                                          node_label_pharmebinet2, directory,
                                          rela_name, direction1, direction2, rela_note_exists):
    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet_Complex and pharmebinet_nodes into a dictionary')
    file_name = directory + '/edge_' + rela_name + '.tsv'

    file_mapped_complex_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_complex_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(
        ['id_1', 'id_2'])

    set_pairs = set()
    load_pharmebinet_complex_pharmebinet_node_in(csv_mapped, set_pairs, start_label, end_label)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, node_label_pharmebinet1, node_label_pharmebinet2, rela_name, direction1, direction2,
                       rela_note_exists)


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

    # 0: query start;   1: rela in reactome; 2: node(s) in reactome     3: label in PharMeBINet;
    # 4: relationship PharMeBINet;  5: direction left;  6: direction left
    list_of_combinations = [
        ['p:MolecularComplex', 'b:MolecularComplex',
         'MolecularComplex', 'MolecularComplex',
         'ASSOCIATES_MCaMC', '<-', '-', 'HAS_COMPONENT_MChcMC'],
        ['p:Protein)-[:equal_to_reactome_uniprot]-(:ReferenceEntity_reactome', 'b:MolecularComplex',
         'Protein', 'MolecularComplex',
         'ASSOCIATES_MCaP', '<-', '-', 'HAS_COMPONENT_MChcP'],
    ]

    directory = 'CatalystActivityEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        start_label = list_element[0]
        end_label = list_element[1]
        node_label_pharmebinet1 = list_element[2]
        node_label_pharmebinet2 = list_element[3]
        rela_name = list_element[4]
        direction1 = list_element[5]
        direction2 = list_element[6]
        rela_note_exists = list_element[7]
        check_relationships_and_generate_file(start_label, end_label, node_label_pharmebinet1,
                                              node_label_pharmebinet2, directory,
                                              rela_name, direction1, direction2, rela_note_exists)
    cypher_file.close()
    driver.close()

    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
