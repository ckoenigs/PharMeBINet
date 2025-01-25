import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils



def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


def load_chemical_SE_edge_info(csv_file ):
    """
    Load all pairs and relationship information from chemical over ADReCS to SE and write information into file
    :param csv_file: csv writer
    :return:
    """

    dict_pair_to_edge = {}
    query = '''MATCH (p:Chemical)-[:equal_adrecs_chemical]-(r)-[v]-(n)-[:equal_to_adrecs_adr]-(b:SideEffect) Where not v.frequency_faers is null RETURN p.identifier, b.identifier, v, r.id'''
    print(query)
    results = graph_database.run(query)
    for record in results:
        [chemical_id, node_id, edge, adrecs_drug_id] = record.values()
        edge = dict(edge)
        if (chemical_id, node_id) in dict_pair_to_edge :
            dict_pair_to_edge[(chemical_id, node_id)][0].append(edge)
            continue
        dict_pair_to_edge[(chemical_id, node_id)] = [[edge],adrecs_drug_id]


    print('number of drug-SE relationships in adrecs:' + str(
        len(dict_pair_to_edge)))

    for (chemical_id, node_id), list_of_edge_and_adr_id in dict_pair_to_edge.items():
        adrecs_drug_id=list_of_edge_and_adr_id[1]
        frequencies=set()
        grades=set()
        for edge in list_of_edge_and_adr_id[0]:
            grade= edge['severity_grade_faers']
            grades.add(grade)
            frequencies.add(edge['frequency_faers']+' for ' + grade)
        csv_file.writerow([chemical_id, node_id, adrecs_drug_id, '|'.join(frequencies),'|'.join(grades)])


def create_cypher_file(file_path, rela):
    """
    generate relationships between drug-se that have edges in adrecs
    :param file_path:
    :param rela:
    :return:
    """
    query = ''' MATCH (d:Chemical{identifier:line.chemical_id}),(c:SideEffect{identifier:line.se_id}) Merge (d)-[l: %s]->(c) On Create Set l.resource= ['ADReCS'], l.fears_frequencies=split(line.fears_frequencies,"|"), l.fears_severity_grades=split(line.fears_severity_grades, "|"), l.adrecs= "yes", l.license="CC BY-NC-SA 4.0", l.url="http://bioinf.xmu.edu.cn/ADReCS/drugSummary.jsp?drug_id="+line.adr_id, l.source="ADReCS" On Match Set l.adrecs="yes", l.resource="ADReCS"+l.resource, l.fears_frequencies=split(line.fears_frequencies,"|"), l.fears_severity_grades=split(line.fears_severity_grades, "|")'''
    query = query % (rela)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/adrecs/{file_path}', query)
    cypher_file.write(query)


def main():
    global path_of_directory
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
    csv_edge.writerow(['chemical_id', 'se_id', 'adr_id', 'fears_frequencies', 'fears_severity_grades'])

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
