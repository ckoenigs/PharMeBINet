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
    g = driver.session()


def load_complex_id():
    """
      load complexids that correspond to human polymer and chemicals which were already mapped
    """
    l = set()

    query = "MATCH (n:bindingDB_COMPLEX_COMPONENT) where (n)--(:bindingDB_POLYMER_AND_NAMES)--(:Protein) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        if 'complexid' in node:
            complexid = node['complexid']
            l.add(complexid)
    query = "MATCH (n:bindingDB_COMPLEX_COMPONENT) where (n)--(:bindingDB_MONO_STRUCT_NAMES)--(:Chemical) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        if 'complexid' in node:
            complexid = node['complexid']
            l.add(complexid)

    return l


def load_ids_complex_protein_chemical_edge(node):
    """
        creates a set of lists containing complexid, protein/chemical identifier, type, and componentid
    """
    l = []
    if node == 'protein':
        query = "MATCH (n:bindingDB_COMPLEX_COMPONENT)--(:bindingDB_POLYMER_AND_NAMES)--(p:Protein) RETURN n, p"
    elif node == 'chemical':
        query = "MATCH (n:bindingDB_COMPLEX_COMPONENT)--(:bindingDB_MONO_STRUCT_NAMES)--(p:Chemical) RETURN n, p"
    results = g.run(query)

    for record in results:
        l_ids = []
        node_cc = record.data()['n']
        node_p = record.data()['p']

        complexid = node_cc['complexid']
        l_ids.append(complexid)
        identifier = node_p['identifier']
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
        l.append(l_ids)
    return l


def generate_files(path_of_directory, complexids, list_ids1, list_ids2):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    file_name = 'Complexid_to_mapped_polymers_and_monomers'
    file_name2 = 'Complex-protein_edge'
    file_name3 = 'Complex-chemical_edge'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    file2 = open(os.path.join(path_of_directory, file_name2) + '.tsv', 'w', encoding='utf-8', newline="")
    file3 = open(os.path.join(path_of_directory, file_name3) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping2 = csv.writer(file2, delimiter='\t')
    csv_mapping3 = csv.writer(file3, delimiter='\t')
    header = ['complexid']
    csv_mapping.writerow(header)
    header2 = ['complexid', 'identifier', 'type', 'componentid']
    csv_mapping2.writerow(header2)
    csv_mapping3.writerow(header2)

    for id in complexids:
        csv_mapping.writerow([id])
    for l in list_ids1:
        csv_mapping2.writerow(l)
    for l in list_ids2:
        csv_mapping3.writerow(l)

    cypher_file = open(os.path.join(source, 'cypher.cypher'), 'w', encoding='utf-8')
    query = f'Match (n:bindingDB_COMPLEX_AND_NAMES{{complexid:line.complexid}}) Create (m:Complex) Set m=n, m.identifier=line.complexid, m.resource=["bindingDB"], m.source="bindingDB", m.url="" Create (m)-[:equal]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    query = query.replace("/", "")
    cypher_file.write(query)
    query = f'Match (n:Complex{{identifier:line.complexid}}), (m:Protein{{identifier:line.identifier}}) Create (n)-[:has_component{{type:line.type, componentid:line.componentid, source:"bindingDB", resource:["bindingDB"]}}] -> (m)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name2 + '.tsv', query)
    query = query.replace("/", "")
    cypher_file.write(query)
    query = f'Match (n:Complex{{identifier:line.complexid}}), (m:Chemical{{identifier:line.identifier}}) Create (n)-[:has_component{{type:line.type, componentid:line.componentid, source:"bindingDB", resource:["bindingDB"]}}] -> (m)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name3 + '.tsv', query)
    query = query.replace("/", "")
    cypher_file.write(query)






def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path bindingdb complex')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet\\bindingDB\\')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'complex\\')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load Complex corresponding to mapped polymers')
    list_complexid = load_complex_id()
    list_ids1 = load_ids_complex_protein_chemical_edge('protein')
    list_ids2 = load_ids_complex_protein_chemical_edge('chemical')
    print('Create tsv file and write query')
    generate_files(path_of_directory, list_complexid, list_ids1, list_ids2)

    print('##########################################################################')

if __name__ == "__main__":
    # execute only if run as a script
    main()
