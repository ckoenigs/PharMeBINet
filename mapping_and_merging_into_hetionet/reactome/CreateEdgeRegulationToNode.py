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


# dictionary with pharmebinet failedReaction with identifier as key and value the name
dict_regulation_pharmebinet_node_pharmebinet = {}

'''
load in all pathways from pharmebinet in a dictionary
'''


def load_pharmebinet_regulation_pharmebinet_node_in(csv_file, dict_regulation_pharmebinet_node_pharmebinet,
                                                    new_relationship,
                                                    node_reactome_label, node_pharmebinet_label, direction1,
                                                    direction2):
    query = '''MATCH (p:Regulation)-[:equal_to_reactome_regulation]-(r:Regulation_reactome)%s[v:%s]%s(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, r.schemaClass, n.stId'''
    query = query % (
        direction1, new_relationship, direction2, node_reactome_label, node_pharmebinet_label)
    print(query)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for record in results:
        [regulation_id, node_id, order, stoichiometry, knownAction, stid] = record.values()
        if (regulation_id, node_id) in dict_regulation_pharmebinet_node_pharmebinet:
            print(regulation_id, node_id)
            sys.exit("Doppelte Kombination")
        dict_regulation_pharmebinet_node_pharmebinet[(regulation_id, node_id)] = [stoichiometry, order]
        csv_file.writerow([regulation_id, node_id, order, stoichiometry, knownAction, stid])
    print('number of regulation-' + node_reactome_label + ' relationships in pharmebinet:' + str(
        len(dict_regulation_pharmebinet_node_pharmebinet)))


'''
generate new relationships between pathways of pharmebinet and Regulation of pharmebinet nodes that mapped to reactome 
'''


def create_cypher_file(file_path, node_label, rela_name, direction1, direction2):
    query = ''' MATCH (d:Regulation{identifier:line.id_pharmebinet_Regulation}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, knownAction:line.knownAction, resource: ['Reactome'], source:"Reactome", reactome: "yes", license:"%s", url:"https://reactome.org/content/detail/"+line.stid}]%s(c)'''
    query = query % (node_label, direction1, rela_name, license, direction2)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/{file_path}',
                                              query)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label, node_pharmebinet_label,
                                          directory, rela_name, direction1, direction2):
    print(
        '___(o\'-\'o)___°( ^.^ )°___°(.,.)°___~°(o\'.\'o)°___`(o^.^o)´___(o\'-\'o)___°( ^.^ )°___°(.,.)°___~°(o\'.\'o)°___`(o^.^o)´___')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet_Regulation and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/mapped_Regulation_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'

    file_mapped_regulation_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_regulation_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(
        ['id_pharmebinet_Regulation', 'id_pharmebinet_node', 'order', 'stoichiometry', 'knownAction', 'stid'])

    dict_Regulation_node = {}

    load_pharmebinet_regulation_pharmebinet_node_in(csv_mapped, dict_Regulation_node, new_relationship,
                                                    node_reactome_label,
                                                    node_pharmebinet_label, direction1, direction2)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, node_pharmebinet_label, rela_name, direction1, direction2)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license reactome edge regulation')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;    1: name of node in Reactome; 2 : name of node in pharmebinet;  3: name of new relationship
    # 4: direction left; 5: direction right;
    list_of_combinations = [
        ['regulatedBy', 'ReactionLikeEvent_reactome', 'ReactionLikeEvent', 'IS_REGULATED_BY_RGirbRLE', '<-',
         '-'],
        # ['regulator', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'equal_to_reactome_drug', 'Chemical', 'HAS_REGULATOR_RGirCH', '-', '->'], do not exists anymore
        ['activeUnit', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'Chemical',
         'HAS_ACTIVE_UNIT_RGiauCH', '-', '->'],
        ['goBiologicalProcess', 'GO_BiologicalProcess_reactome', 'BiologicalProcess',
         'OCCURS_IN_GO_BIOLOGICAL_PROCESS_RGoigbpBP', '-', '->'],
        ['activity', 'GO_MolecularFunction_reactome', 'MolecularFunction',
         'HAS_ACTIVITY_RGhaMF', '-', '->'],
        ['activeUnit', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'Protein',
         'HAS_ACTIVE_UNIT_RGhauP', '-', '->'],
        ['regulator', 'PhysicalEntity_reactome)--(:ReferenceEntity_reactome', 'Protein',
         'HAS_REGULATOR_RGhrP', '-', '->']
    ]

    directory = 'RegulationEdges'
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
    driver.close()

    print(
        '___(o\'-\'o)___°( ^.^ )°___°(.,.)°___~°(o\'.\'o)°___`(o^.^o)´___(o\'-\'o)___°( ^.^ )°___°(.,.)°___~°(o\'.\'o)°___`(o^.^o)´___')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
