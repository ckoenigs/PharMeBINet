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


def load_complex_id():
    """
      load complexids that correspond to human polymer which were already mapped
      """
    l = set()
    query = "MATCH (n:bindingDB_COMPLEX_COMPONENT) where (n)--(:bindingDB_POLYMER_AND_NAMES)--(:Protein) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        if 'complexid' in node:
            complexid = node['complexid']
            l.add(complexid)
    return l



def generate_files(path_of_directory, complexids):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    file_name = 'Complexid_to_mapped_polymers'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['complexid']
    csv_mapping.writerow(header)
    for id in complexids:
        csv_mapping.writerow([id])
    cypher_file = open(os.path.join(source, 'cypher_node.cypher'), 'w', encoding='utf-8')
    query = f'Match (n:bindingDB_COMPLEX_AND_NAMES{{complexid:line.complexid}}) Create (m:Complex) Set m=n, m.identifier=line.complexid, m.resource=["bindingDB"], m.source="bindingDB", m.url="" Create (m)-[:equal]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
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

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bindingDB/')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'complex/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load Complex corresponding to mapped polymers')
    list_complexid = load_complex_id()
    print('Create tsv file and write query')
    generate_files(path_of_directory, list_complexid)

    print('##########################################################################')

if __name__ == "__main__":
    # execute only if run as a script
    main()
