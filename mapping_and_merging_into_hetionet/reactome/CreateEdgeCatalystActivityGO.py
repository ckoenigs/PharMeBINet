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


# dictionary with pharmebinetet failedReaction with identifier as key and value the name
dict_complex_pharmebinet_node_pharmebinet = {}
dict_catAct_id_to_catActRef_info = {}


def prepare_CA_with_reference_infos():
    """
    Get all CA which have reference information
    :return:
    """
    query2 = '''MATCH (a:CatalystActivity_reactome)--(f:CatalystActivityReference_reactome) RETURN a.dbId, f.displayName, f.pubMed_ids, f.books'''

    results2 = graph_database.run(query2)

    for record in results2:
        [catAct_id, displayName, pubMed_ids, books] = record.values()
        displayName = displayName.split("]")
        name = displayName[0] + "]"
        description = displayName[1]
        pubMed_ids = pubMed_ids if pubMed_ids else []
        books = books if books else []
        if len(pubMed_ids) == 0 and len(books) == 0:
            sys.exit('both empty')
        dict_catAct_id_to_catActRef_info[catAct_id] = [name, description, pubMed_ids, books]


'''
load in all complex-data from pharmebinet in a dictionary
'''


def load_pharmebinet_complex_pharmebinet_node_in(csv_file, dict_complex_pharmebinet_node_pharmebinet,
                                                 start_label, new_relationship,
                                                 node_reactome_label, node_pharmebinet_label, direction1,
                                                 direction2):
    query = '''MATCH %s%s[v:%s]%s(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, f.displayName, f.dbId, r.stId'''

    query = query % (start_label, direction1, new_relationship, direction2, node_reactome_label, node_pharmebinet_label)
    results = graph_database.run(query)
    print(query)

    # for id1, id2, order, stoichiometry, in results:
    for record in results:
        [complex_id, node_id, order, stoichiometry, displayName, catACT_id, physicalEntity_id] = record.values()
        if catACT_id in dict_catAct_id_to_catActRef_info:
            name = dict_catAct_id_to_catActRef_info[catACT_id][0]
            description = dict_catAct_id_to_catActRef_info[catACT_id][1]
            pubMed_ids = dict_catAct_id_to_catActRef_info[catACT_id][2]
            books = dict_catAct_id_to_catActRef_info[catACT_id][3]
            if (complex_id, node_id) not in dict_complex_pharmebinet_node_pharmebinet:
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)] = [stoichiometry, order, set([name]),
                                                                                    set([description]), set(pubMed_ids),
                                                                                    set(books), physicalEntity_id]
                continue
            else:
                # print(complex_id, node_id)
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)][2].add(name)
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)][3].add(description)
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)][4].union(pubMed_ids)
                dict_complex_pharmebinet_node_pharmebinet[(complex_id, node_id)][5].union(books)

    for (complex_id, node_id), [stoichiometry, order, name, description, pubMed_ids, books,
                                physicalEntity_id] in dict_complex_pharmebinet_node_pharmebinet.items():
        csv_file.writerow(
            [complex_id, node_id, order, stoichiometry, "|".join(name), "|".join(description), "|".join(pubMed_ids),
             "|".join(books), physicalEntity_id])

    print('number of complex-' + node_reactome_label + ' relationships in pharmebinet:' + str(
        len(dict_complex_pharmebinet_node_pharmebinet)))


'''
generate new relationships between complex of pharmebinet and complex of pharmebinet nodes that mapped to reactome 
'''


def create_cypher_file(directory, file_path, node_label, rela_name, direction1, direction2, start_label):
    if "Complex" in start_label:
        query = ''' MATCH (d:MolecularComplex{identifier:line.id_pharmebinet_Complex}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, name:split(line.displayName,"|"), description:split(line.description,"|"), pubMed_ids:split(line.pubMed_ids,"|"), books:split(line.books,"|"), resource: ['Reactome'], reactome: "yes", source:"Reactome", license:"CC BY 4.0", url:"https://reactome.org/content/detail/"+line.id_pharmebinet_Complex}]%s(c)'''
    else:
        query = ''' MATCH (d:Protein{identifier:line.id_pharmebinet_Complex}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, name:split(line.displayName,"|"), description:split(line.description,"|"), pubMed_ids:split(line.pubMed_ids,"|"), books:split(line.books,"|"), resource: ['Reactome'], reactome: "yes", source:"Reactome", license:"CC BY 4.0", url:"https://reactome.org/content/detail/"+line.physicalEntity_id}]%s(c)'''

    query = query % (node_label, direction1, rela_name, direction2)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/{file_path}',
                                              query)
    cypher_file.write(query)


def check_relationships_and_generate_file(start_label, new_relationship, node_reactome_label, node_pharmebinet_label,
                                          directory, rela_name, direction1, direction2):
    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.utcnow())
    print('Load all relationships from pharmebinet_Complex and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    if "Complex" in start_label:
        file_name = directory + '/mapped_Complex_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'
    else:
        file_name = directory + '/mapped_Protein_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'

    file_mapped_complex_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_complex_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(
        ['id_pharmebinet_Complex', 'id_pharmebinet_node', 'order', 'stoichiometry', 'displayName', 'description',
         'pubMed_ids', 'books', 'physicalEntity_id'])

    dict_Complex_node = {}

    load_pharmebinet_complex_pharmebinet_node_in(csv_mapped, dict_Complex_node, start_label, new_relationship,
                                                 node_reactome_label, node_pharmebinet_label, direction1, direction2)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file(directory, file_name, node_pharmebinet_label, rela_name, direction1, direction2, start_label)


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

    print(datetime.datetime.now())
    print('get all CA with references ')

    prepare_CA_with_reference_infos()

    # 0: query start;   1: rela in reactome; 2: node(s) in reactome     3: label in PharMeBINet;
    # 4: relationship PharMeBINet;  5: direction left;  6: direction left
    list_of_combinations = [

        [
            '(p:MolecularComplex)-[:equal_to_reactome_complex]-(r:Complex_reactome)-[:activeUnit]-(f:CatalystActivity_reactome)',
            'activity', 'GO_MolecularFunction_reactome', 'MolecularFunction',
            'HAS_MOLECULAR_FUNCTION_MChmfMF', '-', '->'],
        [
            '(p:Protein)-[:equal_to_reactome_uniprot]-(:ReferenceEntity_reactome)--(r:PhysicalEntity_reactome)-[:activeUnit]-(f:CatalystActivity_reactome)',
            'activity',
            'GO_MolecularFunction_reactome', 'MolecularFunction',
            'HAS_MOLECULAR_FUNCTION_PhmfMF', '-', '->'],
    ]

    directory = 'CatalystActivityEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        start_label = list_element[0]
        new_relationship = list_element[1]
        node_reactome_label = list_element[2]
        node_pharmebinet_label = list_element[3]
        rela_name = list_element[4]
        direction1 = list_element[5]
        direction2 = list_element[6]
        check_relationships_and_generate_file(start_label, new_relationship, node_reactome_label,
                                              node_pharmebinet_label, directory,
                                              rela_name, direction1, direction2)
    cypher_file.close()
    driver.close()

    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
