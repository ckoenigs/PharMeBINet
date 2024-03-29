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
list_bindingdb_pharmebinet_labels = [['bindingDB_polymer_and_names', 'Protein'],
                                     ['bindingDB_mono_struct_names', 'Chemical']]


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

    query = f'Match (n:bindingDB_complex_and_names{{complexid:line.complexid}}) Create (m:MolecularComplex) Set m=n, m.identifier=line.complexid, m.url="https://www.bindingdb.org/rwd/jsp/dbsearch/PrimarySearch_ki.jsp?tag=com&submit=Search&complexid="+line.complexid, m.name=n.display_name, m.bindingdb="yes", m.resource=["BindingDB"], m.source="BindingDB", m.license="CC BY 3.0 US Deed" Remove m.complexid, m.display_name Create (m)-[:equal]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(query)

    return csv_mapping


def load_complex_id():
    """
      load complexids that correspond to human polymer and chemicals which were already mapped
    """
    csv_writer = prepare_tsv_file_and_cypher_query_for_node()
    query = f"MATCH (n:bindingDB_complex_component) where (n)--(:{list_bindingdb_pharmebinet_labels[0][0]})--(:{list_bindingdb_pharmebinet_labels[0][1]}) or (n)--(:{list_bindingdb_pharmebinet_labels[1][0]})--(:{list_bindingdb_pharmebinet_labels[1][1]}) RETURN Distinct n.complexid"
    print(query)
    results = g.run(query)

    for record in results:
        [complexid] = record.values()
        csv_writer.writerow([complexid])


def generate_tsv_file_and_cypher_query_for_edge(label):
    file_name = f'Complex_{label}_edge'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    header2 = ['complexid', 'identifier', 'type', 'componentid']
    csv_mapping.writerow(header2)

    query = f'Match (n:MolecularComplex{{identifier:line.complexid}}), (m:{label}{{identifier:line.identifier}}) Create (n)-[:HAS_COMPONENT_{pharmebinetutils.dictionary_label_to_abbreviation["MolecularComplex"]}hc{pharmebinetutils.dictionary_label_to_abbreviation[label]}{{type:line.type, componentid:line.componentid, bindingdb:"yes", url:"https://www.bindingdb.org/rwd/jsp/dbsearch/PrimarySearch_ki.jsp?tag=com&submit=Search&complexid="+line.complexid, license:"CC BY 3.0 US Deed", source:"BindingDB", resource:["BindingDB"]}}] -> (m)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(query)

    return csv_mapping


def load_ids_complex_protein_chemical_edge(tuple_labels):
    """
        creates a set of lists containing complexid, protein/chemical identifier, type, and componentid
    """
    csv_edge = generate_tsv_file_and_cypher_query_for_edge(tuple_labels[1])
    query = f"MATCH (n:bindingDB_complex_component)--(:{tuple_labels[0]})--(p:{tuple_labels[1]}) RETURN n, p.identifier"
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
