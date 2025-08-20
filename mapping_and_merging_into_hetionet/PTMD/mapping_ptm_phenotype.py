import datetime
import json
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


def generate_tsv_file(label, columns, file_cypher, rela_type):
    """
    Prepare TSV file and add cypher query to file
    :param label:
    :param columns:
    :return:
    """
    file_name_not_mapped = f'new_ptm_{label}_{rela_type}_edges.tsv'
    not_mapped_path = os.path.join(path_of_directory, file_name_not_mapped)
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(columns)
    prepare_query(label, file_name_not_mapped, file_cypher, rela_type)

    return writer, file


dict_type_to_rela = {
    "disruption": 'DISRUPTS',
    "creation": 'CREATES',
    "up-regulation": 'UPREGULATES',
    "down-regulation": 'DOWNREGULATES',
    "presence": 'IS_PRESENT_IN',
    "absence": 'IS_ABSENT_IN'
}


def prepare_query(label, file_name, file_cypher, rela_type):
    """
    Prepare query and add information
    :param label:
    :param file_name:
    :return:
    """
    if rela_type not in ["up-regulation", "down-regulation",'presence','absence']:
        rela_type_query=pharmebinetutils.prepare_rela_great(dict_type_to_rela[rela_type], "PTM", label)

        query = (f' Match (p:PTM{{identifier:line.ptm_id}}), (d:{label} {{identifier:line.phenotype_id}}) Create ('
                 f'p)-[:{rela_type_query} {{resource:["PTMD"],ptmd:"yes", '
                 f'is_experimental_verification:line.is_experimental_verification, license:"ONLY freely available for academic research", '
                 f'mutation_site_impacts:split(line.mutation_site_impacts,"|"), url:"https://ptmd.biocuckoo.cn/index.php", source:"PTMD", '
                 f'mutation_sites:split(line.mutation_sites,"|"), pubMed_ids:split(line.pmids,"|"), regulation:line.regulation, '
                 f'sources:split(line.sources,"|"), ptmd_properties:split(line.ptmd_properties,"|"), url:"https://ptmd.biocuckoo.cn/index.php", license:"ONLY freely available for academic research"}}]->(d)')
    else:
        rela_type_query = pharmebinetutils.prepare_rela_great(dict_type_to_rela[rela_type], label, "PTM" )

        query = (f' Match (p:PTM{{identifier:line.ptm_id}}), (d:{label} {{identifier:line.phenotype_id}}) Create ('
                 f'p)<-[:{rela_type_query} {{resource:["PTMD"],ptmd:"yes", '
                 f'is_experimental_verification:line.is_experimental_verification, license:"ONLY freely available for academic research", '
                 f'mutation_site_impacts:split(line.mutation_site_impacts,"|"), url:"https://ptmd.biocuckoo.cn/index.php", source:"PTMD", '
                 f'mutation_sites:split(line.mutation_sites,"|"), pubMed_ids:split(line.pmids,"|"), regulation:line.regulation, '
                 f'sources:split(line.sources,"|"), ptmd_properties:split(line.ptmd_properties,"|"), url:"https://ptmd.biocuckoo.cn/index.php", license:"ONLY freely available for academic research"}}]-(d)')
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

    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    # query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    file_cypher = open(cypher_path, 'w', encoding='utf-8')
    columns = ['ptm_id', 'phenotype_id', 'is_experimental_verification', 'mutation_site_impacts',
               'mutation_sites', 'sources', 'pmids', 'ptmd_properties', 'regulation']

    dict_label_to_type_to_tsv = {}

    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_not_mapped = 0
    counter_all = 0
    # Where not r.pmids is Null or "
    #              "r.is_experimental_verification
    query = ("Match (n:PTM)--(p:PTMD_PTM)-[r]-(:PTMD_Disease)--(m:Phenotype) With n, m, collect(r) as hu Return n.identifier, m.identifier, "
             "labels(m),hu")
    results = g.run(query)

    for ptm_id, phenotype_id, labels, relationships, in results:
        counter_all += 1

        general_label = ''
        # mapping of new edges
        if "Disease" in labels:
            general_label = 'Disease'
            counter_disease += 1
        elif "SideEffect" in labels:
            general_label = 'SideEffect'
            counter_sideEffect += 1
        elif "Symptom" in labels:
            general_label = 'Symptom'
            counter_symptom += 1
            # when label is only phenotype
        else:
            general_label = 'Phenotype'
            counter_phenotype += 1
        dict_type_to_properties = {}

        if not general_label in dict_label_to_type_to_tsv:
            dict_label_to_type_to_tsv[general_label] = {}
        for rela in relationships:
            rela=dict(rela)
            regulation = rela['regulation']
            if not regulation in dict_label_to_type_to_tsv[general_label]:
                tsv_writer, tsv_file = generate_tsv_file(general_label, columns, file_cypher, regulation)
                dict_label_to_type_to_tsv[general_label][regulation] = [tsv_writer, tsv_file]
            if regulation not in dict_type_to_properties:
                dict_type_to_properties[regulation] = {'ptmd_properties': [dict(rela)], 'mutation_site_impacts': rela[
                    'mutation_site_impacts'][:] if 'mutation_site_impacts' in rela else [],
                                                       'mutation_sites': rela[
                                                           'mutation_sites'][:] if 'mutation_sites' in rela else [],
                                                       'sources': set(rela['sources']),
                                                       'is_experimental_verification': rela[
                                                           'is_experimental_verification'],
                                                       'pmids': set(rela['pmids']) if 'pmids' in rela else set()}
            else:
                source_mutation = False
                dict_type_to_properties[regulation]['ptmd_properties'].append(dict(rela))
                if 'pmids' in rela:
                    dict_type_to_properties[regulation]['pmids'] = dict_type_to_properties[regulation]['pmids'].union(
                        rela['pmids'])
                dict_type_to_properties[regulation]['is_experimental_verification'] = \
                dict_type_to_properties[regulation]['is_experimental_verification'] or rela[
                    'is_experimental_verification']
                dict_type_to_properties[regulation]['sources'] = dict_type_to_properties[regulation]['sources'].union(
                    rela['sources'])
                if 'mutation_site_impacts' in rela:
                    for counter_new in range(len(rela['mutation_site_impacts'])):
                        found_new = False
                        for counter_added in range(len(dict_type_to_properties[regulation]['mutation_site_impacts'])):
                            if rela['mutation_site_impacts'][counter_new] == \
                                    dict_type_to_properties[regulation]['mutation_site_impacts'][counter_added] and \
                                    rela['mutation_sites'][counter_new] == \
                                    dict_type_to_properties[regulation]['mutation_sites'][counter_added]:
                                found_new = True
                        if not found_new:
                            dict_type_to_properties[regulation]['mutation_site_impacts'].append(
                                rela['mutation_site_impacts'][counter_new])
                            dict_type_to_properties[regulation]['mutation_sites'].append(
                                rela['mutation_sites'][counter_new])

        for regulation, dict_prop in dict_type_to_properties.items():
            dict_label_to_type_to_tsv[general_label][regulation][0].writerow(
                [ptm_id, phenotype_id, dict_prop['is_experimental_verification'],
                 '|'.join(dict_prop['mutation_site_impacts']),
                 '|'.join(dict_prop['mutation_sites']),
                 '|'.join(dict_prop['sources']), '|'.join([str(x) for x in dict_prop['pmids']]),
                 '|'.join([json.dumps(x).replace('"','\'') for x in dict_prop['ptmd_properties']]), regulation])

    file_cypher.close()
    for types in dict_label_to_type_to_tsv.values():
        for list_writer_file in types.values():
            list_writer_file[1].close()

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
