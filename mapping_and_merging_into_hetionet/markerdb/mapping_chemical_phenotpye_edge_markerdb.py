import datetime
import os
import sys
import csv


import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary pairs to info
dict_pairs_to_info = {}


def load_edges_from_database_and_add_to_dict():
    '''
    Load all Gene-Variant edges from Graph-DB and add rela-info into a dictionary
    '''
    print("query_started--------")
    query = "MATCH (n:Metabolite)-[r]-(p:Phenotype) RETURN n.identifier,r.resource,p.identifier"
    results = g.run(query)
    print("query_ended----------")

    count = 0
    print(datetime.datetime.now())
    for record in results:
        [chemical_id, resource, phenotype_id] = record.values()
        count += 1
        if count % 50000 == 0:
            print(f"process: {count}")
            print(datetime.datetime.now())
        if (chemical_id, phenotype_id) in dict_pairs_to_info and dict_pairs_to_info[(chemical_id, phenotype_id)] != resource:
            print('------ohje------')
            print(chemical_id, phenotype_id)
            print(resource)
            print(dict_pairs_to_info[(chemical_id, phenotype_id)])
        dict_pairs_to_info[(chemical_id, phenotype_id)] = resource







def get_MarkerDB_information():
    '''
    Load all MarkerDB chemical-variant-phenotype and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)
    # Create tsv for existing edges

    file_name = 'metabolite_phenotype_edges.tsv'
    file_path = os.path.join(path_of_directory, file_name)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file_chemical_phenotype = open(file_path, mode)
    csv_chemical_phenotype = csv.writer(file_chemical_phenotype, delimiter='\t')
    csv_chemical_phenotype.writerow(['chemical_id', 'phenotype_id','sources'])

    # Create tsv for NON-existing edges
    file_name_not_mapped = 'new_metabolite_phenotype_edges.tsv'
    not_mapped_path = os.path.join(path_of_directory, file_name_not_mapped)
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['chemical_id', 'phenotype_id'])

    counter_not_mapped = 0
    counter_all = 0

    query = "Match (n:Metabolite)--(:MarkerDB_Chemical)-[r]-(:MarkerDB_Condition)--(m:Phenotype) Return n.identifier, r, m.identifier"
    results = g.run(query)

    for record in results:
        [chemical_id, rela, phenotype_id] = record.values()
        counter_all += 1
        # mapping of existing edges

        if (chemical_id, phenotype_id) in dict_pairs_to_info:
            if dict_pairs_to_info[(chemical_id, phenotype_id)] is None:
                dict_pairs_to_info[(chemical_id, phenotype_id)] = []


            csv_chemical_phenotype.writerow(
                [chemical_id, phenotype_id,
                 pharmebinetutils.resource_add_and_prepare(dict_pairs_to_info[(chemical_id, phenotype_id)], "MarkerDB")])
        else:
            counter_not_mapped += 1
            writer.writerow([chemical_id, phenotype_id])
    file.close()
    file_chemical_phenotype.close()
    print('number of new edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    # 2 cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w'
    file_cypher = open(cypher_path, mode, encoding='utf-8')
    # 1. Set…
    query = f' Match (n:Metabolite{{identifier:line.chemical_id}})-[r]-(p:Phenotype{{identifier:line.phenotype_id}}) Set r.markerdb="yes", r.sources = split(line.sources,"|")'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    file_cypher.write(query)

    # 2. Create… (finde beide KNOTEN)
    # url:"https://www.disgenet.org/browser/2/1/0/"+line.variant_id
    query = f' Match (n:Metabolite{{identifier:line.chemical_id}}), (p:Phenotype{{identifier:line.phenotype_id}}) Create (p)-[:BIOMARKER_DbM{{source:"MarkerDB", resource:["MarkerDB"],markerdb:"yes"}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped,
                                              query)
    file_cypher.write(query)
    file_cypher.close()


######### MAIN #########
def main():
    global home
    global path_of_directory
    global source

    path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test/"

    #os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/markerdb')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'chemical_phenotype_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all information of the chemicals/phenotypes')

    load_edges_from_database_and_add_to_dict()

    print('##########################################################################')
    print('gather all information of the MarkerDB chemicals/phenotypes')

    get_MarkerDB_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()