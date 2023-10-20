import datetime
import os, sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# list of bindingDB labels and pharmebinet labels in a list
list_bindingdb_pharmebinet_labels = [['bindingDB_POLYMER_AND_NAMES', 'Protein'],
                                     ['bindingDB_MONO_STRUCT_NAMES', 'Chemical']]


def prepare_tsv_file_and_cypher_query_for_node():
    """
    prepare tsv file for the new complex nodes and create the cypher query and add it to the cypher file
    :return:
    """
    file_name = 'Complexid_to_mapped_polymers_and_monomers'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['complexid']
    csv_mapping.writerow(header)

    query = f'Match (n:bindingDB_COMPLEX_AND_NAMES{{complexid:line.complexid}}) Create (m:Complex) Set m=n, m.identifier=line.complexid, m.resource=["bindingDB"], m.source="bindingDB", m.url="" Create (m)-[:equal]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    query = query.replace("/", "")
    cypher_file.write(query)

    return csv_mapping


def load_complex_id():
    """
      load complexids that correspond to human polymer and chemicals which were already mapped
    """
    csv_writer = prepare_tsv_file_and_cypher_query_for_node()
    query = f"MATCH (n:bindingDB_COMPLEX_COMPONENT) where (n)--(:{list_bindingdb_pharmebinet_labels[0][0]})--(:{list_bindingdb_pharmebinet_labels[0][1]}) or (n)--(:{list_bindingdb_pharmebinet_labels[1][0]})--(:{list_bindingdb_pharmebinet_labels[1][1]}) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        complexid = node['complexid']
        csv_writer.writerow([complexid])


def generate_tsv_file_and_cypher_query_for_edge(label):
    file_name = f'Complex_{label}_edge'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    header2 = ['complexid', 'identifier', 'type', 'componentid']
    csv_mapping.writerow(header2)

    query = f'Match (n:Complex{{identifier:line.complexid}}), (m:{label}{{identifier:line.identifier}}) Create (n)-[:has_component{{type:line.type, componentid:line.componentid, source:"bindingDB", resource:["bindingDB"]}}] -> (m)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(query)

    return csv_mapping


def load_ids_complex_protein_chemical_edge(tuple_labels):
    """
        creates a set of lists containing complexid, protein/chemical identifier, type, and componentid
    """
    csv_edge = generate_tsv_file_and_cypher_query_for_edge(tuple_labels[1])
    query = f"MATCH (n:bindingDB_COMPLEX_COMPONENT)--(:{tuple_labels[0]})--(p:{tuple_labels[1]}) RETURN n, p.identifier"
    results = g.run(query)

    for record in results:
        l_ids = []
        [node_cc, identifier] = record.values()

        complexid = node_cc['complexid']
        l_ids.append(complexid)
        l_ids.append(identifier)

        if 'type' in node_cc:
            type = node_cc['type']
            l_ids.append(type)
        else:
            l_ids.append('')
        if 'componentid' in node_cc:
            componentid = node_cc['componentid']
            l_ids.append(componentid)
        else:
            l_ids.append('')
        csv_edge.writerow(l_ids)


def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source, cypher_file

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path bindingdb complex')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bindingDB/')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'complex/')

    cypher_file = open(os.path.join(source, 'cypher_edge.cypher'), 'w', encoding='utf-8')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load Complex corresponding to mapped polymers')
    load_complex_id()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare edges')

    for tuple_labels in list_bindingdb_pharmebinet_labels:
        load_ids_complex_protein_chemical_edge(tuple_labels)

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
