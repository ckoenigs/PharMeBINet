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


def load_chemical_SE_edge_info(csv_file, ):
    """
    Load all pairs and relationship information from chemical over ADReCS to SE and write information into file
    :param csv_file: csv writer
    :return:
    """

    dict_pair_to_edge = {}
    query = '''MATCH (p:Chemical)-[]-(r:ADReCS_Drug)-[v]-(n:ADReCS_ADR)-[]-(b:SideEffect) RETURN p.identifier, b.identifier, v, r.id'''
    print(query)
    results = graph_database.run(query)
    for record in results:
        [chemical_id, node_id, edge, adrecs_drug_id] = record.values()
        if (chemical_id, node_id) in dict_pair_to_edge:
            print(chemical_id, node_id)
            continue
        dict_pair_to_edge[(chemical_id, node_id)] = dict(edge)
        csv_file.writerow([chemical_id, node_id, adrecs_drug_id])
    print('number of drug-SE relationships in adrecs:' + str(
        len(dict_pair_to_edge)))


'''
generate relationships between drug-se that have edges in adrecs 
'''


def create_cypher_file(file_path, rela):
    query = ''' MATCH (d:Chemical{identifier:line.chemical_id}),(c:SideEffect{identifier:line.se_id}) Merge (d)-[l: %s]->(c) On Create Set l.resource= ['ADReCS'], l.adrecs= "yes", l.license="CC BY-NC-SA 4.0", l.url="http://bioinf.xmu.edu.cn/ADReCS/drugSummary.jsp?drug_id="+line.adr_id, l.source="ADReCS" On Match Set l.adrecs="yes", l.resource="ADReCS"+l.resource'''
    query = query % (rela)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/adrecs/{file_path}', query)
    cypher_file.write(query)


def main():
    global path_of_directory, license
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path adrecs edge')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j ')

    create_connection_with_neo4j()

    directory = 'edge'
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding="utf-8")
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from pathway-node and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/edge.tsv'

    file = open(file_name, 'w', encoding="utf-8")
    csv_edge = csv.writer(file, delimiter='\t', lineterminator='\n')
    csv_edge.writerow(['chemical_id', 'se_id', 'adr_id'])

    load_chemical_SE_edge_info(csv_edge)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, 'CAUSES_CHcSE')
    cypher_file.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
