import csv
import datetime
import os, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# import create_connection_to_database_metabolite


# dictionary disease name to resource
dict_phenotype_id_to_resource = {}


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver, con
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


def load_disease_from_database_and_add_to_dict(label, condition=''):
    """
    Load all Genes from my database and add them into a dictionary
    """
    query = f"MATCH (n:{label}) {condition} RETURN n.identifier, n.name, n.synonyms, n.xrefs, n.resource"
    results = g.run(query)

    dict_different_mappings_for_a_label = {'name': {}, 'synonyms': {}, 'umls': {}, 'omim': {}, 'ncit': {}}

    for identifier, name, synonyms, xrefs, resource, in results:
        dict_phenotype_id_to_resource[identifier] = resource
        name = name.lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_different_mappings_for_a_label['name'], name, identifier)
        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_different_mappings_for_a_label['synonyms'], synonym,
                                                          identifier)

        if xrefs:
            for xref in xrefs:
                if xref.startswith('UMLS'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_different_mappings_for_a_label['umls'],
                                                              xref.split(':')[1],
                                                              identifier)
                elif xref.startswith('OMIM'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_different_mappings_for_a_label['omim'],
                                                              xref.split(':')[1],
                                                              identifier)
                elif xref.startswith('NCIT:'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_different_mappings_for_a_label['ncit'],
                                                              xref.split(':')[1],
                                                              identifier)
    return dict_different_mappings_for_a_label
        

def try_to_get_umls_ids_with_UMLS(name):
    """
    Try to get umls cuis be search with name in UMLS
    :param name:
    :return:
    """
    cur = con.cursor()
    query = ('Select Distinct CUI From MRCONSO Where STR = "%s";')
    query = query % (name)
    rows_counter = cur.execute(query)

    list_of_cuis = []

    if rows_counter > 0:
        # add found cuis
        for (cui,) in cur:
            list_of_cuis.append(cui)
    print(list_of_cuis)
    return list_of_cuis


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'PTMD_disease_to_disease'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['PTMD_disease_name', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'a'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    query = (f' MATCH (n:PTMD_Disease), (v:Phenotype{{identifier: line.identifier}}) WHERE id(n) = '
             f'toInteger(line.PTMD_disease_name) SET v.ptmd = "yes", v.resource = split(line.resource, "|") '
             f'CREATE (v)-[:equal_to_PTMD_disease {{mapped_with: line.mapping_method}}]->(n)')
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping

# dictionary_manual_mapping
dict_manual_mapping={
    "mitochondrial complex iv deficiency":'MONDO:0033885',
    'Biliary tract tumor':'MONDO:0005304',
    'Autosomal dominant nonsyndromic deafness':'MONDO:0019587',
    'Ovarian cancer/carcinoma':'MONDO:0005140',
    'Sensory ataxic neuropathy dysarthria and ophthalmoparesis':'MONDO:0011835'
}

set_not_map_with_disease=set(["lactate dehydrogenase b deficiency","pyrin-associated autoinflammatory disease", "keratosis follicularis"])

def load_all_PTMD_diseases_and_finish_the_files(csv_mapping, dict_disease, dict_symptom, dict_phenotype):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:PTMD_Disease) RETURN id(n) AS nodeId, n.name"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for neo4j_id, name, in results:
        counter_all += 1
        name = name.lower()


        mapped = False
        # mapping
        if name in dict_disease['name']:
            mapped = True
            for identifier in dict_disease['name'][name]:
                csv_mapping.writerow(
                    [neo4j_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier], "PTMD"),
                     'name'])

        if mapped:
            continue
        # mapping
        if name in dict_symptom['name']:
            mapped = True
            for identifier in dict_symptom['name'][name]:
                csv_mapping.writerow(
                    [neo4j_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier], "PTMD"),
                     'name'])

        if mapped:
            continue
        # mapping
        if name in dict_phenotype['name']:
            mapped = True
            for identifier in dict_phenotype['name'][name]:
                csv_mapping.writerow(
                    [neo4j_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier], "PTMD"),
                     'name'])

        if mapped:
            continue
        # manual mapping
        if name in dict_manual_mapping:
            print('manual')
            mapped = True
            csv_mapping.writerow(
                [neo4j_id, dict_manual_mapping[name],
                 pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[dict_manual_mapping[name]],
                                                           "PTMD"),
                 'manual'])

        if mapped:
            continue

        set_umls_names = set()
        umls_cui_list = try_to_get_umls_ids_with_UMLS(name)
        if not name in set_umls_names:
            for umls_cui in umls_cui_list:
                if umls_cui in dict_disease['umls']:
                    mapped = True
                    for identifier in dict_disease['umls'][umls_cui]:
                        csv_mapping.writerow(
                            [neo4j_id, identifier,
                             pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
                                                                       "PTMD"),
                             'umls'])

        if mapped:
            continue


        if name in dict_disease['synonyms']:
            mapped = True
            for identifier in dict_disease['synonyms'][name]:
                csv_mapping.writerow(
                    [neo4j_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier], "PTMD"),
                     'synonym'])

        if mapped:
            continue

        for umls_cui in umls_cui_list:
            if umls_cui in dict_symptom['umls']:
                mapped = True
                for identifier in dict_symptom['umls'][umls_cui]:
                    csv_mapping.writerow(
                        [neo4j_id, identifier,
                         pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
                                                                   "PTMD"),
                         'umls'])

        if mapped:
            continue

        if name in dict_symptom['synonyms']:
            mapped = True
            for identifier in dict_symptom['synonyms'][name]:
                csv_mapping.writerow(
                    [neo4j_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier], "PTMD"),
                     'synonym'])

        if mapped:
            continue

        for umls_cui in umls_cui_list:
            if umls_cui in dict_phenotype['umls']:
                mapped = True
                for identifier in dict_phenotype['umls'][umls_cui]:
                    csv_mapping.writerow(
                        [neo4j_id, identifier,
                         pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
                                                                   "PTMD"),
                         'umls'])

        if mapped:
            continue

        # if name in dict_phenotype['synonyms']:
        #     mapped = True
        #     for identifier in dict_phenotype['synonyms'][name]:
        #         csv_mapping.writerow(
        #             [neo4j_id, identifier,
        #              pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier], "PTMD"),
        #              'synonym'])
        #
        # if mapped:
        #     continue

        # if len(umls_cui_list) > 0:
        #     cur = con.cursor()
        #     query = ('Select Distinct CODE From MRCONSO Where CUI in  ("%s") and SAB="NCI" ;')
        #     query = query % ('","'.join(umls_cui_list))
        #     rows_counter = cur.execute(query)
        #
        #     if rows_counter > 0:
        #         # add found cuis
        #         for (nci_id,) in cur:
        #             if nci_id in dict_disease['ncit']:
        #                 mapped = True
        #                 for identifier in dict_disease['ncit'][nci_id]:
        #                     csv_mapping.writerow(
        #                         [neo4j_id, identifier,
        #                          pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
        #                                                                    "PTMD"),
        #                          'umls_nci'])
        #
        # if mapped:
        #     continue
        # if len(umls_cui_list) > 0:
        #     cur = con.cursor()
        #     query = ('Select Distinct STR From MRCONSO Where CUI in  ("%s");')
        #     query = query % ('","'.join(umls_cui_list))
        #     rows_counter = cur.execute(query)
        #
        #     if rows_counter > 0:
        #         # add found cuis
        #         for (name_umls,) in cur:
        #             name_umls = name_umls.lower()
        #             set_umls_names.add(name_umls)
        #             if name_umls in dict_disease['name']:
        #                 mapped = True
        #                 for identifier in dict_disease['name'][name_umls]:
        #                     csv_mapping.writerow(
        #                         [neo4j_id, identifier,
        #                          pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
        #                                                                    "PTMD"),
        #                          'umls_name'])
        #
        # if mapped:
        #     continue
        #
        #
        # if len(set_umls_names) > 0:
        #     for name_umls in set_umls_names:
        #         if name_umls in dict_symptom['name']:
        #             mapped = True
        #             for identifier in dict_symptom['name'][name_umls]:
        #                 csv_mapping.writerow(
        #                     [neo4j_id, identifier,
        #                      pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
        #                                                                "PTMD"),
        #                      'umls_name'])
        #
        # if mapped:
        #     continue
        #
        # if len(set_umls_names) > 0:
        #     for name_umls in set_umls_names:
        #         if name_umls in dict_phenotype['name']:
        #             mapped = True
        #             for identifier in dict_phenotype['name'][name_umls]:
        #                 csv_mapping.writerow(
        #                     [neo4j_id, identifier,
        #                      pharmebinetutils.resource_add_and_prepare(dict_phenotype_id_to_resource[identifier],
        #                                                                "PTMD"),
        #                      'umls_name'])

        if not mapped:
            counter_not_mapped += 1
            print(name)


    print('number of not-mapped conditions:', counter_not_mapped)
    print('number of all conditions:', counter_all)


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
    path_of_directory = os.path.join(home, 'disease/')

    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all disease from database')
    dict_disease = load_disease_from_database_and_add_to_dict('Disease')
    dict_symptom = load_disease_from_database_and_add_to_dict('Symptom')
    dict_phenotype = load_disease_from_database_and_add_to_dict('Phenotype', 'Where not ( n:Disease or n:Symptom)')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all PTMD diseases from database')
    load_all_PTMD_diseases_and_finish_the_files(csv_mapping, dict_disease, dict_symptom, dict_phenotype)

    driver.close()


if __name__ == "__main__":
    main()
