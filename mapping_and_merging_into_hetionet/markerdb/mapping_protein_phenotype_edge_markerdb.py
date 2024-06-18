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
    query = "MATCH (n:Protein)-[r]-(p:Phenotype) RETURN n.identifier,r.resource,p.identifier"
    results = g.run(query)
    print("query_ended----------")

    count = 0
    print(datetime.datetime.now())
    for record in results:
        [protein_id, resource, phenotype_id] = record.values()
        count += 1
        if count % 50000 == 0:
            print(f"process: {count}")
            print(datetime.datetime.now())
        if (protein_id, phenotype_id) in dict_pairs_to_info and dict_pairs_to_info[(protein_id, phenotype_id)] != resource:
            print('------ohje------')
            print(protein_id, phenotype_id)
            print(resource)
            print(dict_pairs_to_info[(protein_id, phenotype_id)])
        dict_pairs_to_info[(protein_id, phenotype_id)] = resource







def get_MarkerDB_information():
    '''
    Load all MarkerDB protein-variant-phenotype and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    # Create tsv for protein-disease edges
    file_name_not_mapped_disease = 'new_protein_disease_edges.tsv'
    not_mapped_path_disease = os.path.join(path_of_directory, file_name_not_mapped_disease)
    mode = 'w' if os.path.exists(not_mapped_path_disease) else 'w+'
    file_disease = open(not_mapped_path_disease, mode, encoding='utf-8')
    writer_disease = csv.writer(file_disease, delimiter='\t')
    writer_disease.writerow(['protein_id', 'phenotype_id', 'makerdb_id'])
    # Create tsv for protein-sideEffects edges
    file_name_not_mapped_sideEffect = 'new_protein_sideEffect_edges.tsv'
    not_mapped_path_sideEffect = os.path.join(path_of_directory, file_name_not_mapped_sideEffect)
    mode = 'w' if os.path.exists(not_mapped_path_sideEffect) else 'w+'
    file_sideEffect = open(not_mapped_path_sideEffect, mode, encoding='utf-8')
    writer_sideEffect = csv.writer(file_sideEffect, delimiter='\t')
    writer_sideEffect.writerow(['protein_id', 'phenotype_id', 'makerdb_id'])
    # Create tsv for protein-symptoms edges
    file_name_not_mapped_symptom = 'new_protein_symptom_edges.tsv'
    not_mapped_path_symptom = os.path.join(path_of_directory, file_name_not_mapped_symptom)
    mode = 'w' if os.path.exists(not_mapped_path_symptom) else 'w+'
    file_symptom = open(not_mapped_path_symptom, mode, encoding='utf-8')
    writer_symptom = csv.writer(file_symptom, delimiter='\t')
    writer_symptom.writerow(['protein_id', 'phenotype_id', 'makerdb_id'])

    # Create tsv for protein-phenotype edges
    file_name_not_mapped_phenotype = 'new_protein_phenotype_edges.tsv'
    not_mapped_path_phenotype = os.path.join(path_of_directory, file_name_not_mapped_phenotype)
    mode = 'w' if os.path.exists(not_mapped_path_phenotype) else 'w+'
    file_phenotype = open(not_mapped_path_phenotype, mode, encoding='utf-8')
    writer_phenotype = csv.writer(file_phenotype, delimiter='\t')
    writer_phenotype.writerow(['protein_id', 'phenotype_id', 'makerdb_id'])

    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_all = 0

    query = "Match (n:Protein)--(p:MarkerDB_Protein)-[r]-(:MarkerDB_Condition)--(m:Phenotype) Return p.id, n.identifier, r, m.identifier, labels(m)"
    results = g.run(query)

    for record in results:
        [markerdb_id, protein_id, rela, phenotype_id, labels] = record.values()
        counter_all += 1

        # mapping of new edges
        if "Disease" in labels:
            writer_disease.writerow([protein_id, phenotype_id, markerdb_id])
            counter_disease += 1
        elif "SideEffect" in labels:
            writer_sideEffect.writerow([protein_id, phenotype_id, markerdb_id])
            counter_sideEffect += 1
        elif "Symptom" in labels:
            writer_symptom.writerow([protein_id, phenotype_id, markerdb_id])
            counter_symptom += 1
            # when label is only phenotype
        else:
            writer_phenotype.writerow([protein_id, phenotype_id, markerdb_id])
            counter_phenotype += 1
    file_disease.close()
    file_symptom.close()
    file_sideEffect.close()
    file_phenotype.close()


    print('number of disease edges:', counter_disease)
    print('number of sideEffect edges:', counter_sideEffect)
    print('number of symptom edges:', counter_symptom)
    print('number of phenotype edges:', counter_phenotype)
    print('number of all edges:', counter_all)

    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w'
    file_cypher = open(cypher_path, mode, encoding='utf-8')


    # 2. Create new edges
    # url:"https://www.disgenet.org/browser/2/1/0/"+line.variant_id
    query = f' Match (p:Protein{{identifier:line.protein_id}}), (d:Disease{{identifier:line.phenotype_id}}) Create (p)-[:is_BIOMARKER_PbD{{resource:["MarkerDB"],markerdb:"yes", url:"https://markerdb.ca/proteins/"+line.markerdb_id}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_disease,
                                              query)
    file_cypher.write(query)
    query = f' Match (p:Protein{{identifier:line.protein_id}}), (d:SideEffect{{identifier:line.phenotype_id}}) Create (p)-[:is_BIOMARKER_PbSE{{resource:["MarkerDB"],markerdb:"yes", url:"https://markerdb.ca/proteins/"+line.markerdb_id}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_sideEffect,
                                              query)
    file_cypher.write(query)
    query = f' Match (p:Protein{{identifier:line.protein_id}}), (d:Symptom{{identifier:line.phenotype_id}}) Create (p)-[:is_BIOMARKER_PbS{{resource:["MarkerDB"],markerdb:"yes", url:"https://markerdb.ca/proteins/"+line.markerdb_id}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_symptom,
                                              query)
    file_cypher.write(query)
    query = f' Match (p:Protein{{identifier:line.protein_id}}), (d:Phenotype{{identifier:line.phenotype_id}}) Create (p)-[:is_BIOMARKER_PbP{{resource:["MarkerDB"],markerdb:"yes", url:"https://markerdb.ca/proteins/"+line.markerdb_id}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_phenotype,
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
    path_of_directory = os.path.join(home, 'protein_phenotype_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all information of the proteins/phenotypes')

    #load_edges_from_database_and_add_to_dict()

    print('##########################################################################')
    print('gather all information of the MarkerDB proteins/phenotypes')

    get_MarkerDB_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()