import sys
import datetime, time
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def database_connection():
    """
    Create connection to Neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def generate_cypher_queries_and_tsv_files():
    """
    generate cypher queries and tsv files
    :return: csv writer for mapping and new
    """
    set_header_for_files = ['node_id_1', 'node_id_2', 'resource']
    # tsv file for mapping disease
    file_name_mapped = 'output/disease_is_a_mapped.tsv'
    file_disease_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_mapped = csv.writer(file_disease_mapped, delimiter='\t')
    csv_mapped.writerow(set_header_for_files)

    file_name_not_mapped = 'output/not_existing_is_a.tsv'
    file = open(file_name_not_mapped, 'w', encoding='utf-8')
    csv_not_mapped = csv.writer(file, delimiter='\t')
    csv_not_mapped.writerow(['node_id_1', 'node_id_2', 'efo_id'])

    # cypher file for mapping and integration
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding='utf-8')

    query_match = '''Match (s:Disease{identifier:line.node_id_1 })-[r:IS_A_DiaD]->(m:Disease{identifier:line.node_id_2}) Set r.efo='yes',  r.resource=split(line.resource,"|") '''
    query_match = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/efo/{file_name_mapped}',
                                                    query_match)
    cypher_file.write(query_match)

    query_match = '''Match (s:Disease{identifier:line.node_id_1 }),(m:Disease{identifier:line.node_id_2}) Create (s)-[r:IS_A_DiaD{efo:'yes',  resource:["EFO"], source:"EFO", url:"http://www.ebi.ac.uk/efo/"+split(line.efo_id,":")[0]+"_"+split(line.efo_id,":")[1], license:"Apache-2.0"}]->(m) '''
    query_match = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/efo/{file_name_not_mapped}',
                                                    query_match)
    cypher_file.write(query_match)

    return csv_mapped, csv_not_mapped


## dictionary of disease id pair to resource
dict_of_pair_to_resource = {}


def get_all_disease_is_a_pairs():
    """
    Get al disease from pharmebinet and put this information into a dictionary
    :return:
    """
    query = '''MATCH (n:Disease)-[r:IS_A_DiaD]->(m:Disease) RETURN n.identifier, m.identifier, r.resource  '''
    results = g.run(query)

    # add all diseases to dictioanry
    for record in results:
        [node_1, node_2, resource] = record.values()

        dict_of_pair_to_resource[(node_1, node_2)] = resource


def map_efo_is_a_rela_to_pharmebinet(csv_mapped, csv_not_mapped):
    """
    Load first the first efo disease nod an map this. and then for each lower level map the node to disease.
    :return:
    """

    count_mapped = 0
    counter = 0

    query = 'Match (n:Disease)--(l:efo )-[:is_a]->(:efo)--(m:Disease)  RETURN n.identifier, m.identifier, l.id'
    results = g.run(query)
    for record in results:
        counter += 1
        [node_id1, node_id2, efo_id] = record.values()
        if (node_id1, node_id2) in dict_of_pair_to_resource:
            count_mapped += 1
            csv_mapped.writerow([node_id1, node_id2, pharmebinetutils.resource_add_and_prepare(
                dict_of_pair_to_resource[(node_id1, node_id2)], 'EFO')])
        else:
            csv_not_mapped.writerow([node_id1, node_id2, efo_id])

    print('number of mapped rela:', count_mapped)
    print('number of relas', counter)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate dictionary for disease pairs of pharmebinet')

    get_all_disease_is_a_pairs()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate files and cypher queries')

    csv_mapped, csv_not_mapped = generate_cypher_queries_and_tsv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('map hpo diseases to mesh or umls cui and integrated them into pharmebinet')

    map_efo_is_a_rela_to_pharmebinet(csv_mapped, csv_not_mapped)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
