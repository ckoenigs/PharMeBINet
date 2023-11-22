import datetime
import csv
import sys
import json

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
    """Load existing interaction pairs between chemical-product nodes from Pharmebinet"""

    query = f'''MATCH (n:Chemical)-[r:HAS_ChPR]->(m:Product) RETURN n.identifier,m.identifier, r.resource'''
    results = graph_database.run(query)

    dict_pair_to_resource = {}
    for record in results:
        [node_1_id, node_2_id, resource, ] = record.values()

        pair = (node_1_id, node_2_id)
        dict_pair_to_resource[pair] = resource
    return dict_pair_to_resource


# generate cypher file
cypher_file = open('output/cypher_edge.cypher', 'a', encoding='utf-8')


def prepare_tsv_and_cypher():
    """
    prepare tsv file and add cypher query to cypher file
    :return:
    """
    file_name = f'edge/edge_to_product.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id1', 'id2', 'resource', 'props'])

    url = '"https://drugcentral.org/"'

    query = f'''Match (n:Chemical{{identifier:line.id1}}),(o:Product{{identifier:line.id2}}) Merge (n)-[m:HAS_ChPR]->(o) On Match Set m.active_moiety_substance_list=split(line.props,"|"), m.resource=split(line.resource,"|"), m.drugcentral='yes' On Create Set m.resource=['DrugCentral'], m.source='DrugCentral', m.url={url}, m.license="Creative Commons Attribution-ShareAlike 4.0 International Public License", m.drugcentral='yes', m.active_moiety_substance_list=split(line.props,"|") '''
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     'mapping_and_merging_into_hetionet/drugcentral/' + file_name,
                                                     query)
    cypher_file.write(query_create)

    return csv_writer


def load_and_map_DC_chemical_product_edges(dict_pair_to_resource):
    tsv_writer = prepare_tsv_and_cypher()
    query = f'''MATCH (n:Chemical)--(a:DC_Structure)--(r:DC_ActiveIngredient)-[h]-(b:DC_Product)--(m:Product) RETURN n.identifier,m.identifier, r, h '''
    results = graph_database.run(query)

    dict_pair_to_properties = {}

    header = ['active_moiety_name', 'substance_name', 'quantity', 'quantity_denom_unit', 'quantity_denom_value', 'unit']

    for record in results:
        [node_1_id, node_2_id, rela_node, rela] = record.values()
        rela_node = dict(rela_node)
        rela = dict(rela)
        if (node_1_id, node_2_id) not in dict_pair_to_properties:
            dict_pair_to_properties[(node_1_id, node_2_id)] = set()
        dict_pair_to_properties[(node_1_id, node_2_id)].add((rela_node['active_moiety_name'],
                                                             rela_node['substance_name'], rela['quantity'],
                                                             rela['quantity_denom_unit'],
                                                             rela['quantity_denom_value'], rela['unit']))

    for (node_1_id, node_2_id), set_of_information in dict_pair_to_properties.items():
        list_of_info = []
        for tuple_info in set_of_information:
            index = 0
            dict_info = {}
            for head in header:
                dict_info[head] = tuple_info[index]
                index += 1
            list_of_info.append(json.dumps(dict_info))

        if (node_1_id, node_2_id) in dict_pair_to_resource:
            row = [node_1_id, node_2_id, pharmebinetutils.resource_add_and_prepare(
                dict_pair_to_resource[(node_1_id, node_2_id)], 'DrugCentral'), '|'.join(list_of_info)]
            tsv_writer.writerow(row)
        else:
            row = [node_1_id, node_2_id, '', '|'.join(list_of_info)]
            tsv_writer.writerow(row)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral chemical-product edge')

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

    load_and_map_DC_chemical_product_edges(dict_pair_to_resource)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
