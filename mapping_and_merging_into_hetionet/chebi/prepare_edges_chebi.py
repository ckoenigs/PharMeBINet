import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

license = 'CC BY 4.0'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


def create_cypher_file(file_name,  rela_name):
    '''
    generate new relationships between pathways of pharmebinet and pharmebinet nodes that mapped to reactome
    '''
    rela = pharmebinetutils.prepare_rela_great(rela_name, 'Chemical', 'Chemical')
    query = ''' MATCH (d:Chemical{identifier:line.node_id}),(c:Chemical{identifier:line.other_id}) CREATE (d)-[: %s{resource: ['ChEBI'], chebi: "yes", source:"ChEBI", license:"%s", url:""+line.chebi_id}]->(c)'''
    query = query % ( rela, license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/chebi/{file_name}',
                                              query)
    cypher_file.write(query)


def create_tsv_file_and_cypher_query(rela_type):
    """
    create tsv file and create cypher query
    :param label:
    :param rela_type:
    :param to_CT:
    :return:
    """
    file_name = f'edges/{rela_type}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['node_id', 'other_id', 'chebi_id'])
    create_cypher_file(file_name,  rela_type)

    return csv_writer


def load_all_pair_and_add_to_files():
    """
    Load for a given label all edges in both direction and write them into tsv files and generate cypher queries.
    :param label:
    :return:
    """

    dict_type_direction_to_tsv = {}
    query = f'''MATCH (p:Chemical)-[:equal_chebi_chemical]-(r)-[v]->(n)-[:equal_chebi_chemical]-(b:Chemical) Where ID(p)<>ID(b) RETURN p.identifier, b.identifier, type(v), r.id'''
    results = graph_database.run(query)
    counter = 0
    for record in results:
        counter += 1
        [celltype_id, node_id, rela_type, chebi_id] = record.values()
        if rela_type not in dict_type_direction_to_tsv:
            csv_writer = create_tsv_file_and_cypher_query( rela_type)
            dict_type_direction_to_tsv[ rela_type] = csv_writer
        dict_type_direction_to_tsv[ rela_type].writerow([celltype_id, node_id, chebi_id])
    print( counter)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path Chebi edges')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    cypher_file = open('output/cypher_edge.cypher', 'a', encoding="utf-8")
    load_all_pair_and_add_to_files()
    cypher_file.close()
    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
