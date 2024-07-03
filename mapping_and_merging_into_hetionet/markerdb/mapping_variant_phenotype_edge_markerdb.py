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





def get_MarkerDB_information():
    '''
    Load all MarkerDB variant-conditions and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    # Create tsv for variant-disease edges
    file_name_not_mapped_disease = 'new_variant_disease_edges.tsv'
    not_mapped_path_disease = os.path.join(path_of_directory, file_name_not_mapped_disease)
    mode = 'w' if os.path.exists(not_mapped_path_disease) else 'w+'
    file_disease = open(not_mapped_path_disease, mode, encoding='utf-8')
    writer_disease = csv.writer(file_disease, delimiter='\t')
    writer_disease.writerow(['variant_id', 'phenotype_id'])
    # Create tsv for variant-sideEffects edges
    file_name_not_mapped_sideEffect = 'new_variant_sideEffect_edges.tsv'
    not_mapped_path_sideEffect = os.path.join(path_of_directory, file_name_not_mapped_sideEffect)
    mode = 'w' if os.path.exists(not_mapped_path_sideEffect) else 'w+'
    file_sideEffect = open(not_mapped_path_sideEffect, mode, encoding='utf-8')
    writer_sideEffect = csv.writer(file_sideEffect, delimiter='\t')
    writer_sideEffect.writerow(['variant_id', 'phenotype_id'])
    # Create tsv for variant-symptoms edges
    file_name_not_mapped_symptom = 'new_variant_symptom_edges.tsv'
    not_mapped_path_symptom = os.path.join(path_of_directory, file_name_not_mapped_symptom)
    mode = 'w' if os.path.exists(not_mapped_path_symptom) else 'w+'
    file_symptom = open(not_mapped_path_symptom, mode, encoding='utf-8')
    writer_symptom = csv.writer(file_symptom, delimiter='\t')
    writer_symptom.writerow(['variant_id', 'phenotype_id'])

    # Create tsv for variant-phenotype edges
    file_name_not_mapped_phenotype = 'new_variant_phenotype_edges.tsv'
    not_mapped_path_phenotype = os.path.join(path_of_directory, file_name_not_mapped_phenotype)
    mode = 'w' if os.path.exists(not_mapped_path_phenotype) else 'w+'
    file_phenotype = open(not_mapped_path_phenotype, mode, encoding='utf-8')
    writer_phenotype = csv.writer(file_phenotype, delimiter='\t')
    writer_phenotype.writerow(['variant_id', 'phenotype_id'])

    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_all = 0
    counter_not_mapped = 0
    dict_all_mappings = {}

    query = "Match (n:Variant)--(p:MarkerDB_SequenceVariant)-[r]-(:MarkerDB_Condition)--(m:Phenotype) Return p.id, n.identifier, r, m.identifier, labels(m)"
    results = g.run(query)

    for record in results:
        [markerdb_id, variant_id, rela, phenotype_id, labels] = record.values()
        counter_all += 1

        # mapping of new edges
        if "Disease" in labels and (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = "Disease"
            writer_disease.writerow([variant_id, phenotype_id])
            counter_disease += 1
        elif "SideEffect" in labels and (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = "SideEffect"
            writer_sideEffect.writerow([variant_id, phenotype_id])
            counter_sideEffect += 1
        elif "Symptom" in labels and (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = "Symptom"
            writer_symptom.writerow([variant_id, phenotype_id])
            counter_symptom += 1
            # when label is only phenotype
        elif (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = "Phenotype"
            writer_phenotype.writerow([variant_id, phenotype_id])
            counter_phenotype += 1
        # Edge is already mapped
        else:
            print("Edge already mapped:", variant_id, phenotype_id, dict_all_mappings[(variant_id, phenotype_id)])
            counter_not_mapped += 1
    file_disease.close()
    file_symptom.close()
    file_sideEffect.close()
    file_phenotype.close()


    print('number of disease edges:', counter_disease)
    print('number of sideEffect edges:', counter_sideEffect)
    print('number of symptom edges:', counter_symptom)
    print('number of phenotype edges:', counter_phenotype)
    print('number of not mapped edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w+'
    file_cypher = open(cypher_path, mode, encoding='utf-8')


    # 2. Create new edges, write cypher queries
    query = f' Match (v:Variant{{identifier:line.variant_id}}), (d:Disease{{identifier:line.phenotype_id}}) Create (v)-[:is_BIOMARKER_VibD{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_disease,
                                              query)
    file_cypher.write(query)
    query = f' Match (v:Variant{{identifier:line.variant_id}}), (d:SideEffect{{identifier:line.phenotype_id}}) Create (v)-[:is_BIOMARKER_VibSE{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_sideEffect,
                                              query)
    file_cypher.write(query)
    query = f' Match (v:Variant{{identifier:line.variant_id}}), (d:Symptom{{identifier:line.phenotype_id}}) Create (v)-[:is_BIOMARKER_VibS{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_symptom,
                                              query)
    file_cypher.write(query)
    query = f' Match (v:Variant{{identifier:line.variant_id}}), (d:Phenotype{{identifier:line.phenotype_id}}) Create (v)-[:is_BIOMARKER_VibP{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
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
    path_of_directory = os.path.join(home, 'variant_phenotype_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')
    print('gather all information of the MarkerDB variants/phenotypes')

    get_MarkerDB_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()