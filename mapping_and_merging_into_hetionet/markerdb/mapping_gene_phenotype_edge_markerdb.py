import datetime
import os
import sys
import csv

sys.path.append("../..")
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
    Load all MarkerDB gene-variant-phenotype and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    # Create tsv for gene-disease edges
    file_name_not_mapped_disease = 'new_gene_disease_edges.tsv'
    not_mapped_path_disease = os.path.join(path_of_directory, file_name_not_mapped_disease)
    mode = 'w' if os.path.exists(not_mapped_path_disease) else 'w+'
    file_disease = open(not_mapped_path_disease, mode, encoding='utf-8')
    writer_disease = csv.writer(file_disease, delimiter='\t')
    writer_disease.writerow(['gene_id', 'phenotype_id'])
    # Create tsv for gene-sideEffects edges
    file_name_not_mapped_sideEffect = 'new_gene_sideEffect_edges.tsv'
    not_mapped_path_sideEffect = os.path.join(path_of_directory, file_name_not_mapped_sideEffect)
    mode = 'w' if os.path.exists(not_mapped_path_sideEffect) else 'w+'
    file_sideEffect = open(not_mapped_path_sideEffect, mode, encoding='utf-8')
    writer_sideEffect = csv.writer(file_sideEffect, delimiter='\t')
    writer_sideEffect.writerow(['gene_id', 'phenotype_id'])
    # Create tsv for gene-symptoms edges
    file_name_not_mapped_symptom = 'new_gene_symptom_edges.tsv'
    not_mapped_path_symptom = os.path.join(path_of_directory, file_name_not_mapped_symptom)
    mode = 'w' if os.path.exists(not_mapped_path_symptom) else 'w+'
    file_symptom = open(not_mapped_path_symptom, mode, encoding='utf-8')
    writer_symptom = csv.writer(file_symptom, delimiter='\t')
    writer_symptom.writerow(['gene_id', 'phenotype_id'])

    # Create tsv for gene-phenotype edges
    file_name_not_mapped_phenotype = 'new_gene_phenotype_edges.tsv'
    not_mapped_path_phenotype = os.path.join(path_of_directory, file_name_not_mapped_phenotype)
    mode = 'w' if os.path.exists(not_mapped_path_phenotype) else 'w+'
    file_phenotype = open(not_mapped_path_phenotype, mode, encoding='utf-8')
    writer_phenotype = csv.writer(file_phenotype, delimiter='\t')
    writer_phenotype.writerow(['gene_id', 'phenotype_id'])

    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_not_mapped = 0
    counter_all = 0
    dict_all_mappings = {}

    query = "Match (n:Gene)--(p:MarkerDB_Gene)-[r]-(:MarkerDB_Condition)--(m:Phenotype) Return p.id, n.identifier, r, m.identifier, labels(m)"
    results = g.run(query)

    for record in results:
        [markerdb_id, gene_id, rela, phenotype_id, labels] = record.values()
        counter_all += 1

        # mapping of new edges
        if "Disease" in labels and (gene_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(gene_id, phenotype_id)] = "Disease"
            writer_disease.writerow([gene_id, phenotype_id])
            counter_disease += 1
        elif "SideEffect" in labels and (gene_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(gene_id, phenotype_id)] = "SideEffect"
            writer_sideEffect.writerow([gene_id, phenotype_id])
            counter_sideEffect += 1
        elif "Symptom" in labels and (gene_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(gene_id, phenotype_id)] = "Symptom"
            writer_symptom.writerow([gene_id, phenotype_id])
            counter_symptom += 1
            # when label is only phenotype
        elif (gene_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(gene_id, phenotype_id)] = "Phenotype"
            writer_phenotype.writerow([gene_id, phenotype_id])
            counter_phenotype += 1
        # when edge is already integrated
        else:
            print("Already mapped:", gene_id, phenotype_id, dict_all_mappings[(gene_id, phenotype_id)])
            counter_not_mapped += 1
    file_disease.close()
    file_symptom.close()
    file_sideEffect.close()
    file_phenotype.close()


    print('number of disease edges:', counter_disease)
    print('number of sideEffect edges:', counter_sideEffect)
    print('number of symptom edges:', counter_symptom)
    print('number of phenotype edges:', counter_phenotype)
    print('number of not_mapped edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w+'
    file_cypher = open(cypher_path, mode, encoding='utf-8')


    # 2. Create new edges, write cypher queries
    query = f' Match (g:Gene{{identifier:line.gene_id}}), (d:Disease{{identifier:line.phenotype_id}}) Create (g)-[:is_BIOMARKER_GibD{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_disease,
                                              query)
    file_cypher.write(query)
    query = f' Match (g:Gene{{identifier:line.gene_id}}), (d:SideEffect{{identifier:line.phenotype_id}}) Create (g)-[:is_BIOMARKER_GibSE{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_sideEffect,
                                              query)
    file_cypher.write(query)
    query = f' Match (g:Gene{{identifier:line.gene_id}}), (d:Symptom{{identifier:line.phenotype_id}}) Create (g)-[:is_BIOMARKER_GibS{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_symptom,
                                              query)
    file_cypher.write(query)
    query = f' Match (g:Gene{{identifier:line.gene_id}}), (d:Phenotype{{identifier:line.phenotype_id}}) Create (g)-[:is_BIOMARKER_GibP{{resource:["MarkerDB"],markerdb:"yes"}}]->(d)'
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

    # path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test/"
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    #os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/markerdb')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene_phenotype_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')
    print('gather all information of the MarkerDB genes/phenotypes')

    get_MarkerDB_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()