import csv
import datetime
import os
import time
import neo4j

import pharmebinetutils
import create_connection_to_database_metabolite

# dictionary chemical id to resource
dict_metabolite_id_to_resource = {}

# dictionary from chemical id to metabolite id (hmdb)
dict_chemical_id_to_metabolite_id = {}

# dictionary metabolite name to chemical id
dict_metabolite_name_to_chemical_id = {}

def load_metabolites_from_database_and_add_to_dict():
    """
    Load all Genes from my database and add them into a dictionary
    """
    query = "MATCH (n:Metabolite) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_metabolite_id_to_resource[identifier] = node['resource']
        metabolite_name = node['name']
        dict_metabolite_name_to_chemical_id[metabolite_name] = {"identifier": node['identifier'], "resource": node['resource']}


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'MarkerDB_Chemical_to_Metabolite'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['MarkerDB_chemical_id', 'metabolite_id', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'a' if os.path.exists(file_path) else 'w'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f' Match (n:MarkerDB_Chemical{{id:toInteger(line.MarkerDB_chemical_id)}}), (v:Metabolite{{identifier:line.metabolite_id}}) Set v.markerdb="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_MarkerDB_chemical{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'w' if os.path.exists(cypher_file_path) else 'w+'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping

def load_all_MarkerDB_chemicals_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:MarkerDB_Chemical) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node.get('hmdb_id',None)
        unique_id = node['id']
        name_chemical = node['name']

        # mapping
        if identifier in dict_metabolite_id_to_resource:
            csv_mapping.writerow(
                [unique_id, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_metabolite_id_to_resource[identifier], "MarkerDB"),
                 'id'])
        elif name_chemical in dict_metabolite_name_to_chemical_id:
            csv_mapping.writerow(
                [unique_id, dict_metabolite_name_to_chemical_id[name_chemical]["identifier"],
                 pharmebinetutils.resource_add_and_prepare(dict_metabolite_name_to_chemical_id[name_chemical]["resource"],"MarkerDB"),
                'name'])
        else:
            counter_not_mapped += 1
            print(identifier, name_chemical)


    print('number of not-mapped chemicals:', counter_not_mapped)
    print('number of all chemicals:', counter_all)

def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_database_metabolite.database_connection_neo4j_driver()
    g = driver.session(database='graph')

def main():
    global path_of_directory
    global source
    global home

    path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test"
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'chemical/')


    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Metabolites from database')
    load_metabolites_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all MarkerDB chemicals from database')
    load_all_MarkerDB_chemicals_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()
