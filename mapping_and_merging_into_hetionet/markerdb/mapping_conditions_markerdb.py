import csv
import datetime
import os, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# import create_connection_to_database_metabolite


# dictionary disease name to resource
dict_disease_id_to_resource = {}

dict_disease_id_to_name = {}

dict_disease_name_to_id = {}
# dictionary umls cui to disease id
dict_disease_umls_cui_to_id = {}
# dictionary omim id to disease id
dict_disease_omim_id_to_id = {}

# dictionary gene symbol to gene id
dict_synonym_to_ids = {}


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


def load_disease_from_database_and_add_to_dict():
    """
    Load all Genes from my database and add them into a dictionary
    """
    query = "MATCH (n:Phenotype) RETURN n.identifier, n.name, n.synonyms, n.xrefs, n.resource"
    results = g.run(query)

    for identifier, name, synonyms, xrefs, resource, in results:
        # node = record.data()['n']
        # identifier = node['identifier']
        # dict_disease_id_to_resource[identifier] = node['resource']
        dict_disease_id_to_resource[identifier] = resource
        # name = node['name'].lower()
        name = name.lower()
        dict_disease_id_to_name[identifier] = name
        dict_disease_name_to_id[name] = identifier
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, name, identifier)
        # synonyms = node['synonyms'] if 'synonyms' in node else []
        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, synonym, identifier)

        if xrefs:
            for xref in xrefs:
                if xref.startswith('UMLS'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_disease_umls_cui_to_id, xref.split(':')[1],
                                                              identifier)
                elif xref.startswith('OMIM'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_disease_omim_id_to_id, xref.split(':')[1],
                                                              identifier)


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

    return list_of_cuis


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'MarkerDB_condition_to_disease'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    # namen von der condition (markerdb), identifier von disease, resource, mapping_method
    header = ['MarkerDB_condition_name', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/MarkerDB/
    query = f' MATCH (n:MarkerDB_Condition) WHERE toLower(n.name) = toLower(line.MarkerDB_condition_name) MATCH (v:Phenotype{{identifier: line.identifier}}) SET v.markerdb = "yes", v.resource = split(line.resource, "|") CREATE (v)-[:equal_to_MarkerDB_condition {{mapped_with: line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def load_all_MarkerDB_conditions_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:MarkerDB_Condition) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        name = node['name'].lower()
        if '\xa0' in name:
            name = name.replace(u'\xa0', u' ')
        mapped = False
        # mapping
        if name in dict_disease_name_to_id:
            mapped = True
            identifier = dict_disease_name_to_id[name]
            csv_mapping.writerow(
                [name, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[identifier], "MarkerDB"),
                 'name'])
        elif name in dict_synonym_to_ids:
            mapped = True
            for identifier in dict_synonym_to_ids[name]:
                csv_mapping.writerow(
                    [name, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[identifier], "MarkerDB"),
                     'synonym'])

        if mapped:
            continue

        umls_cui_list = try_to_get_umls_ids_with_UMLS(name)
        for umls_cui in umls_cui_list:
            if umls_cui in dict_disease_umls_cui_to_id:
                mapped = True
                for disease_id in dict_disease_umls_cui_to_id[umls_cui]:
                    csv_mapping.writerow(
                        [name, disease_id,
                         pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[identifier], "MarkerDB"),
                         'umls'])

        if mapped:
            continue

        cur = con.cursor()
        query = ('Select Distinct STR From MRCONSO Where CUI in  ("%s");')
        query = query % ('","'.join(umls_cui_list))
        rows_counter = cur.execute(query)

        if rows_counter > 0:
            # add found cuis
            for (name_umls,) in cur:
                name_umls = name_umls.lower()
                if name_umls in dict_disease_name_to_id:
                    mapped = True
                    identifier = dict_disease_name_to_id[name_umls]
                    csv_mapping.writerow(
                        [name, identifier,
                         pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[identifier], "MarkerDB"),
                         'umls_name'])

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

    # path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test"
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'condition/')

    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all disease from database')
    load_disease_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all MarkerDB genes from database')
    load_all_MarkerDB_conditions_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()
