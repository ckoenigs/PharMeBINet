import datetime
import csv
from collections import defaultdict
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
    graph_database = driver.session(database='graph')


def load_edge_into_dictionary():
    """Load existing interaction pairs between chemical nodes from Pharmebinet"""

    query = f'''MATCH (n:Chemical)-[r:INTERACTS_CiC]->(m:Chemical) RETURN n.identifier,m.identifier, r.resource, r.descriptions'''
    results = graph_database.run(query)

    dict_pair_to_resource_description = {}
    for record in results:
        [node_1_id, node_2_id, resource, descriptions] = record.values()

        pair = (node_1_id, node_2_id)
        descriptions = set(descriptions) if descriptions is not None else set()
        dict_pair_to_resource_description[pair] = [resource, descriptions]
    return dict_pair_to_resource_description


# generate cypher file
cypher_file = open('output/cypher_edge.cypher', 'a', encoding='utf-8')


def prepare_tsv_and_cypher():
    """
    prepare tsv file and add cypher query to cypher file
    :return:
    """
    file_name = f'edge/interaction.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id1', 'id2', 'source', 'risk', 'descriptions', 'resource'])

    url = '"https://drugcentral.org/"'

    query = f'''Match (n:Chemical{{identifier:line.id1}}),(o:Chemical{{identifier:line.id2}}) Merge (n)-[m:INTERACTS_CiC]->(o) On Match Set m.dc_source=line.source, m.risk=line.risk, m.descriptions=split(line.descriptions,"|"), m.resource=split(line.resource,"|"), m.drugcentral='yes' On Create Set m.resource=['DrugCentral'], m.source='DrugCentral', m.url={url}, m.license="Creative Commons Attribution-ShareAlike 4.0 International Public License", m.drugcentral='yes', m.dc_source=line.source, m.risk=line.risk, m.descriptions=split(line.descriptions,"|") '''
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     'mapping_and_merging_into_hetionet/drugcentral/' + file_name,
                                                     query)
    cypher_file.write(query_create)

    return csv_writer


def load_and_map_DC_ATC_edges(dict_pair_to_resource):
    tsv_writer = prepare_tsv_and_cypher()
    query = f'''MATCH (n:Chemical)--(a:DC_DrugClass)-[r:DC_INTERACTS]->(b:DC_DrugClass)--(m:Chemical) RETURN n.identifier,m.identifier, r '''
    results = graph_database.run(query)

    set_of_pairs = set()

    for record in results:
        [node_1_id, node_2_id, rela] = record.values()
        if (node_1_id, node_2_id) in set_of_pairs:
            continue
        # avoid self-loops
        if node_1_id == node_2_id:
            print('selfloops :O')
            continue

        set_of_pairs.add((node_1_id, node_2_id))
        if (node_1_id, node_2_id) in dict_pair_to_resource:
            descriptions = dict_pair_to_resource[(node_1_id, node_2_id)][1]
            descriptions.add(rela['description'])
            tsv_writer.writerow([node_1_id, node_2_id, rela['source'], rela['risk'], '|'.join(descriptions),
                                 pharmebinetutils.resource_add_and_prepare(
                                     dict_pair_to_resource[(node_1_id, node_2_id)][0], 'DrugCentral')])
        else:
            tsv_writer.writerow([node_1_id, node_2_id, rela['source'], rela['risk'], rela['description']])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral atc edge')

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')
    create_connection_with_neo4j()

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('load pairs')

    dict_pair_to_resource = load_edge_into_dictionary()

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('map')

    load_and_map_DC_ATC_edges(dict_pair_to_resource)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
