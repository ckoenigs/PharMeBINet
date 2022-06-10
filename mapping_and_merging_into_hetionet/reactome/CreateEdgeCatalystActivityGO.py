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
dict_catAct_id_to_catActRef_info = {}

'''
load in all complex-data from hetionet in a dictionary
'''


def load_hetionet_complex_hetionet_node_in(csv_file, dict_complex_hetionet_node_hetionet,
                                              start_label, new_relationship,
                                              node_reactome_label,  node_hetionet_label, direction1,
                                              direction2):
    #list = ["(p:MolecularComplex)-[:equal_to_reactome_complex]-(r:Complex_reactome)", "(p:Protein)-[:equal_to_reactome_uniprot]-(:ReferenceEntity_reactome)--(:PhysicalEntity_reactome)"]
    #for item in list:
    query2 = '''MATCH (a:CatalystActivity_reactome)--(f:CatalystActivityReference_reactome) RETURN a.dbId, f.displayName, f.pubMed_ids, f.books'''
    query = '''MATCH %s%s[v:%s]%s(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, f.displayName, f.dbId'''


    query = query % (start_label, direction1, new_relationship, direction2, node_reactome_label,  node_hetionet_label)
    results = graph_database.run(query)
    print(query)

    results2 = graph_database.run(query2)
    for catAct_id, displayName, pubMed_ids, books, in results2:
        displayName = displayName.split("]")
        name = displayName[0] + "]"
        description = displayName[1]
        pubMed_ids = pubMed_ids if pubMed_ids else []
        books = books if books else []
        if len(pubMed_ids) == 0 and len(books) == 0:
            sys.exit('both empty')
        dict_catAct_id_to_catActRef_info[catAct_id] = [name, description, pubMed_ids, books]

    # for id1, id2, order, stoichiometry, in results:
    for complex_id, node_id, order, stoichiometry, displayName, catACT_id, in results:
        if catACT_id in dict_catAct_id_to_catActRef_info:
            name = dict_catAct_id_to_catActRef_info[catACT_id][0]
            description = dict_catAct_id_to_catActRef_info[catACT_id][1]
            pubMed_ids = dict_catAct_id_to_catActRef_info[catACT_id][2]
            books = dict_catAct_id_to_catActRef_info[catACT_id][3]
            if (complex_id, node_id) not in dict_complex_hetionet_node_hetionet:
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)] = [stoichiometry, order, set([name]),
                                                                              set([description]), set(pubMed_ids), set(books)]
                continue
            else:
                #print(complex_id, node_id)
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)][2].add(name)
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)][3].add(description)
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)][4].union(pubMed_ids)
                dict_complex_hetionet_node_hetionet[(complex_id, node_id)][5].union(books)


    for (complex_id,node_id),[stoichiometry, order, name, description, pubMed_ids, books] in dict_complex_hetionet_node_hetionet.items():
        csv_file.writerow([complex_id, node_id, order, stoichiometry, "|".join(name), "|".join(description), "|".join(pubMed_ids), "|".join(books)])

    print('number of complex-' + node_reactome_label + ' relationships in hetionet:' + str(
        len(dict_complex_hetionet_node_hetionet)))


'''
generate new relationships between complex of hetionet and complex of hetionet nodes that mapped to reactome 
'''


def create_cypher_file(directory, file_path, node_label, rela_name, direction1, direction2, start_label):
    if "Complex" in start_label:
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:MolecularComplex{identifier:line.id_hetionet_Complex}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, name:split(line.displayName,"|"), description:split(line.description,"|"), pubMed_ids:split(line.pubMed_ids,"|"), books:split(line.books,"|"), resource: ['Reactome'], reactome: "yes"}]%s(c);\n'''
    else:
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:Protein{identifier:line.id_hetionet_Complex}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)%s[:%s{order:line.order, stoichiometry:line.stoichiometry, name:split(line.displayName,"|"), description:split(line.description,"|"), pubMed_ids:split(line.pubMed_ids,"|"), books:split(line.books,"|"), resource: ['Reactome'], reactome: "yes"}]%s(c);\n'''

    query = query % (path_of_directory, file_path, node_label, direction1, rela_name, direction2)
    cypher_file.write(query)


def check_relationships_and_generate_file(start_label, new_relationship, node_reactome_label,  node_hetionet_label,
                                          directory, rela_name, direction1, direction2):
    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.utcnow())
    print('Load all relationships from hetionet_Complex and hetionet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    if "Complex" in start_label:
        file_name = directory + '/mapped_Complex_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'
    else:
        file_name = directory + '/mapped_Protein_to_' + node_reactome_label[0:24] + '_' + rela_name + '.tsv'

    file_mapped_complex_to_node = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_complex_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_hetionet_Complex', 'id_hetionet_node', 'order', 'stoichiometry', 'displayName' ,'description', 'pubMed_ids', 'books'])

    dict_Complex_node = {}

    load_hetionet_complex_hetionet_node_in(csv_mapped, dict_Complex_node, start_label, new_relationship,
                                              node_reactome_label, node_hetionet_label, direction1, direction2)

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file(directory, file_name, node_hetionet_label, rela_name, direction1, direction2, start_label)


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

    # 0: query start;   1: rela in reactome; 2: node(s) in reactome     3: label in PharMeBINet;
    # 4: relationship PharMeBINet;  5: direction left;  6: direction left
    list_of_combinations = [

        [
            '(p:MolecularComplex)-[:equal_to_reactome_complex]-(r:Complex_reactome)-[:activeUnit]-(f:CatalystActivity_reactome)',
            'activity', 'GO_MolecularFunction_reactome',  'MolecularFunction',
            'HAS_MOLECULAR_FUNCTION_MChmfMF', '-', '->'],
        [
            '(p:Protein)-[:equal_to_reactome_uniprot]-(:ReferenceEntity_reactome)--(:PhysicalEntity_reactome)-[:activeUnit]-(f:CatalystActivity_reactome)',
            'activity',
            'GO_MolecularFunction_reactome',  'MolecularFunction',
            'HAS_MOLECULAR_FUNCTION_PhmfMF', '-', '->'],
    ]

    directory = 'CatalystActivityGOEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        start_label = list_element[0]
        new_relationship = list_element[1]
        node_reactome_label = list_element[2]
        node_hetionet_label = list_element[3]
        rela_name = list_element[4]
        direction1 = list_element[5]
        direction2 = list_element[6]
        check_relationships_and_generate_file(start_label, new_relationship, node_reactome_label,
                                              node_hetionet_label, directory,
                                              rela_name, direction1, direction2)
    cypher_file.close()

    print(
        '___~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~_____~(  )(°^)o_o(^°)(  )~__')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
