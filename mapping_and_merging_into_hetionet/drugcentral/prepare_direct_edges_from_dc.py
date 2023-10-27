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


def load_edge_into_dictionary(label1, labels2, edge_type):
    """Load existing pairs between ATC nodes from Pharmebinet"""

    query = f'''MATCH (n:{label1})-[r:{edge_type}]->(m:{labels2}) RETURN n.identifier,m.identifier, r.resource'''
    results = graph_database.run(query)

    dict_pair_to_resource = {}
    for record in results:
        [node_1_id, node_2_id, resource] = record.values()

        pair = (node_1_id, node_2_id)
        dict_pair_to_resource[pair] = resource
    return dict_pair_to_resource


# generate cypher file
cypher_file = open('output/cypher_edge.cypher', 'w')


def prepare_tsv_and_cypher(label1, label2, dc_label_1, dc_label_2, edge_type):
    """
    prepare tsv file and add cypher query to cypher file
    :param label1:
    :param label2:
    :param edge_type:
    :return:
    """
    file_name = f'edge/{label1}_{label2}_{edge_type}_{dc_label_1}_{dc_label_2}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id1', 'id2', 'resource', 'id'])

    if dc_label_1 == 'DC_Structure' or dc_label_2 == 'DC_Structure':
        url = '"https://drugcentral.org/drugcard/"+line.id'
    else:
        url = '"https://drugcentral.org/"'

    query = f'''Match (n:{label1}{{identifier:line.id1}}),(o:{label2}{{identifier:line.id2}}) Merge (n)-[m:{edge_type}]->(o) On Match Set m.resource=split(line.resource,"|"), m.drugcentral='yes' On Create Set m.resource=['DrugCentral'], m.source='DrugCentral', m.url={url}, m.license="Creative Commons Attribution-ShareAlike 4.0 International Public License", m.drugcentral='yes' '''
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     'mapping_and_merging_into_hetionet/drugcentral/' + file_name,
                                                     query)
    cypher_file.write(query_create)

    return csv_writer


def load_and_map_DC_ATC_edges(label1, label2, dc_label_1, dc_label_2, edge_type_dc, edge_type, dict_pair_to_resource):
    tsv_writer = prepare_tsv_and_cypher(label1, label2, dc_label_1, dc_label_2, edge_type)
    query = f'''MATCH (n:{label1})--(a:{dc_label_1})-[r:{edge_type_dc}]->(b:{dc_label_2})--(m:{label2}) RETURN n.identifier,m.identifier, a.id, b.id '''
    print(query)
    results = graph_database.run(query)

    set_of_pairs = set()

    for record in results:
        [node_1_id, node_2_id, id_dc_1, id_dc_2] = record.values()
        if (node_1_id, node_2_id) in set_of_pairs:
            continue
        # avoid self-loops
        if label1 == label2 and node_1_id == node_2_id:
            continue

        id_dc = ''
        if dc_label_1 == 'DC_Structure':
            id_dc = id_dc_1
        elif dc_label_2 == 'DC_Structure':
            id_dc = id_dc_2

        set_of_pairs.add((node_1_id, node_2_id))
        if (node_1_id, node_2_id) in dict_pair_to_resource:
            tsv_writer.writerow([node_1_id, node_2_id, pharmebinetutils.resource_add_and_prepare(
                dict_pair_to_resource[(node_1_id, node_2_id)], 'DrugCentral'), id_dc])
        else:
            tsv_writer.writerow([node_1_id, node_2_id, id_dc])


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
    print('start edges')

    list_of_list_with_edge_information = [
        ['PharmacologicClass', 'PharmacologicClass', 'DC_ATC', 'DC_ATC', 'DC_HAS_PARENT', 'BELONGS_TO_PCbtPC'],
        ['Chemical', 'PharmacologicClass', 'DC_Structure', 'DC_ATC', 'DC_HAS_ATC', 'BELONGS_TO_CHbtPC'],
        ['Chemical', 'Chemical', 'DC_Structure', 'DC_ParentDrugMolecule', 'DC_HAS_PARENT', 'HAS_PARENT_CHhpCH'],
        ['Chemical', 'Chemical', 'DC_Structure', 'DC_DrugClass', 'DC_BELONGS_TO', 'BELONGS_TO_CHbtCH'],
        ['Chemical', 'PharmacologicClass', 'DC_Structure', 'DC_PharmaClass', 'DC_BELONGS_TO', 'BELONGS_TO_CHbtPC'],
        ['Chemical', 'Disease', 'DC_Structure', 'DC_OMOPConcept', 'DC_INDICATION', 'TREATS_CHtD'],
        ['Chemical', 'Disease', 'DC_Structure', 'DC_OMOPConcept', 'DC_CONTRAINDICATION', 'CONTRAINDICATES_CHcD'],
        ['Chemical', 'Disease', 'DC_Structure', 'DC_OMOPConcept', 'DC_OFF_LABEL_USE', 'IS_OFF_LABEL_USE_CHioluD'],
        ['Chemical', 'Symptom', 'DC_Structure', 'DC_OMOPConcept', 'DC_INDICATION', 'TREATS_CHtS'],
        ['Chemical', 'Symptom', 'DC_Structure', 'DC_OMOPConcept', 'DC_CONTRAINDICATION', 'CONTRAINDICATES_CHcS'],
        ['Chemical', 'Symptom', 'DC_Structure', 'DC_OMOPConcept', 'DC_OFF_LABEL_USE', 'IS_OFF_LABEL_USE_CHioluS']
        # Have only one or two edge
        # ['Chemical', 'Disease', 'DC_Structure', 'DC_OMOPConcept', 'DC_SYMPTOMATIC_TREATMENT',
        # 'TREATS_SYMPTOMATIC_CHtsD'],
        # ['Chemical', 'Disease', 'DC_Structure', 'DC_OMOPConcept', 'DC_DIAGNOSIS', 'DIAGNOSES_CHdD'],
        # ['Chemical', 'Symptom', 'DC_Structure', 'DC_OMOPConcept', 'DC_SYMPTOMATIC_TREATMENT',
        # 'TREATS_SYMPTOMATIC_CHtsS'],
        # ['Chemical', 'Symptom', 'DC_Structure', 'DC_OMOPConcept', 'DC_DIAGNOSIS', 'DIAGNOSES_CHdS'] #
        # it is only one edge and I'm not sure what the real definition is
        # ['Chemical', 'PharmacologicClass', 'DC_Structure', 'DC_OMOPConcept', 'DC_REDUCE_RISK', ''],

    ]

    for edge_info in list_of_list_with_edge_information:
        load_and_map_DC_ATC_edges(edge_info[0], edge_info[1], edge_info[2], edge_info[3], edge_info[4], edge_info[5],
                                  load_edge_into_dictionary(edge_info[0], edge_info[1], edge_info[5]))

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
