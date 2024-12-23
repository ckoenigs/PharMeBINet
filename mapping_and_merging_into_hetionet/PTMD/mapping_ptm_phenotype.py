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

def generate_tsv_file(label, columns, file_cypher):
    """
    Prepare TSV file and add cypher query to file
    :param label:
    :param columns:
    :return:
    """
    file_name_not_mapped = f'new_ptm_{label}_edges.tsv'
    not_mapped_path = os.path.join(path_of_directory, file_name_not_mapped)
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(columns)
    prepare_query(label, file_name_not_mapped)

    return  writer, file

def prepare_query(label, file_name, file_cypher):
    """
    Prepare query and add information
    :param label:
    :param file_name:
    :return:
    """
    query = (f' Match (p:PTM{{identifier:line.ptm_id}}), (d:{label} {{identifier:line.phenotype_id}}) Create ('
             f'p)-[:ASSOCIATES_PTMa{pharmebinetutils.dictionary_label_to_abbreviation[label]} {{resource:["PTMD"],ptmd:"yes", '
             f'is_experimental_verification:line.is_experimental_verification, license:"ONLY freely available for academic research", '
             f'mutation_site_impacts:line.mutation_site_impacts, url:"https://ptmd.biocuckoo.cn/index.php", source:"PTMD", '
             f'mutation_sites:line.mutation_sites, regulation:line.regulation, sources:line.sources, url:"", license:"ONLY freely available for academic research"}}]->(d)')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    file_cypher.write(query)

def get_PTMD_information():
    '''
    Load all PTMD ptm-variant-phenotype and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)
    columns = ['ptm_id', 'phenotype_id', 'is_experimental_verification', 'mutation_site_impacts', 'mutation_sites',
               'regulation', 'sources']


    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    # query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    file_cypher = open(cypher_path, 'w', encoding='utf-8')
    # Create tsv for ptm-disease edges and add cypher query
    writer_disease, file_disease = generate_tsv_file('Disease', columns, file_cypher)
    # Create tsv for ptm-symptom edges and add cypher query
    writer_symptom, file_symptom = generate_tsv_file('Symptom', columns, file_cypher)
    # Create tsv for ptm-SE edges and add cypher query
    writer_sideEffect, file_sideEffect = generate_tsv_file('SideEffect', columns, file_cypher)
    # Create tsv for ptm-phenotype edges and add cypher query
    writer_phenotype, file_phenotype = generate_tsv_file('Phenotype', columns, file_cypher)
    file_cypher.close()


    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_not_mapped = 0
    counter_all = 0
    dict_all_mappings = {}

    query = ("Match (n:PTM)--(p:PTMD_PTM)-[r]-(:PTMD_Disease)--(m:Phenotype) Return n.identifier, m.identifier, "
             "labels(m), r.is_experimental_verification, r.mutation_site_impacts, r.mutation_sites, "
             "r.regulation, r.sources")
    results = g.run(query)

    for record in results:
        [ptm_id, phenotype_id, labels, is_experimental_verification, mutation_site_impacts, mutation_sites, regulation,
         sources] = record.values()
        counter_all += 1

        # mapping of new edges
        if "Disease" in labels and (ptm_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(ptm_id, phenotype_id)] = "Disease"
            writer_disease.writerow(
                [ptm_id, phenotype_id, is_experimental_verification, mutation_site_impacts, mutation_sites, regulation,
                 sources])
            counter_disease += 1
        elif "SideEffect" in labels and (ptm_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(ptm_id, phenotype_id)] = "SideEffect"
            writer_sideEffect.writerow(
                [ptm_id, phenotype_id, is_experimental_verification, mutation_site_impacts, mutation_sites, regulation,
                 sources])
            counter_sideEffect += 1
        elif "Symptom" in labels and (ptm_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(ptm_id, phenotype_id)] = "Symptom"
            writer_symptom.writerow(
                [ptm_id, phenotype_id, is_experimental_verification, mutation_site_impacts, mutation_sites, regulation,
                 sources])
            counter_symptom += 1
            # when label is only phenotype
        elif (ptm_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(ptm_id, phenotype_id)] = "Phenotype"
            writer_phenotype.writerow(
                [ptm_id, phenotype_id, is_experimental_verification, mutation_site_impacts, mutation_sites, regulation,
                 sources])
            counter_phenotype += 1
        # when edge is already integrated
        else:
            print("Already mapped edge:", ptm_id, phenotype_id, dict_all_mappings[(ptm_id, phenotype_id)])
            counter_not_mapped += 1

        file_disease.close()
        file_symptom.close()
        file_sideEffect.close()
        file_phenotype.close()

    print('number of disease edges:', counter_disease)
    print('number of sideEffect edges:', counter_sideEffect)
    print('number of symptom edges:', counter_symptom)
    print('number of phenotype edges:', counter_phenotype)
    print('number of not mapped (already mapped) edges:', counter_not_mapped)
    print('number of all edges:', counter_all)



######### MAIN #########
def main():
    global path_of_directory
    global source
    global home

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'ptm_phenotype_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')
    print('gather all information of the PTMD ptms/phenotypes')

    get_PTMD_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
