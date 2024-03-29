import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def add_entry_to_dictionary(dictionary, key, value):
    """
    prepare entry in dictionary if not exists. Then add new value.
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


# dictionary metabolite id to resource
dict_metabolite_id_to_resource = {}

# dictionary from inchkey to metabolite ids
dict_inchi_key_to_metabolite_ids = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_metabolites_from_database_and_add_to_dict():
    query = "MATCH (n:Metabolite) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_metabolite_id_to_resource[identifier] = node['resource']
        inchi_key = node['inchikey'] if 'inchikey' in node else None
        if inchi_key:
            add_entry_to_dictionary(dict_inchi_key_to_metabolite_ids, inchi_key, identifier)
    print('number of metabolites:', len(dict_metabolite_id_to_resource))


def generate_files(path_of_directory, label):
    """
    generate cypher file and tsv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'metabolite/smpdb_metabolite_to_%s' % label
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['identifier', 'other_id', 'resource', 'mapped_with']
    csv_mapping.writerow(header)

    query = ''' Match (n:metabolite_smpdb{identifier:line.identifier}), (v:%s{identifier:line.other_id}) Set v.smpdb='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_smpdb_%s{how_mapped:line.mapped_with}]->(n)'''
    query = query % (label, label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/smpdb/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


'''
Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
'''


def load_all_smpdb_metabolite_and_finish_the_files(csv_mapping_metabolite, csv_not_mapped):
    query = "MATCH (n:metabolite_smpdb) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['identifier']
        hmdb_id = node['hmdb_id'] if 'hmdb_id' in node else ''
        inchi_key = node['inchi_key'] if 'inchi_key' in node else ''
        has_mapped = False
        if hmdb_id != '':
            if hmdb_id in dict_metabolite_id_to_resource:
                has_mapped = True
                csv_mapping_metabolite.writerow(
                    [identifier, hmdb_id,
                     pharmebinetutils.resource_add_and_prepare(dict_metabolite_id_to_resource[hmdb_id], 'SMPDB'),
                     'hmdb_id'])
        if has_mapped:
            continue

        if inchi_key != '':
            if inchi_key in dict_inchi_key_to_metabolite_ids:
                has_mapped = True
                for metabolite_id in dict_inchi_key_to_metabolite_ids[inchi_key]:
                    csv_mapping_metabolite.writerow(
                        [identifier, metabolite_id, pharmebinetutils.resource_add_and_prepare(dict_metabolite_id_to_resource[metabolite_id],'SMPDB'),
                         'inchi_key'])

        if has_mapped:
            continue
        csv_not_mapped.writerow([identifier, node['name'], hmdb_id])
        counter_not_mapped += 1
    print('number of not mapped metabolites:', counter_not_mapped)
    print('number of all metabolites:', counter_all)


def main():
    print(datetime.datetime.now())

    global path_of_directory, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path smpdb metabolite')

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Metabolite from database')

    load_metabolites_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping_metabolite = generate_files(path_of_directory, 'Metabolite')

    file = open('metabolite/not_mapped.tsv', 'w', encoding='utf-8')
    csv_not_mapped = csv.writer(file, delimiter='\t')
    csv_not_mapped.writerow(['identifier', 'name', 'hmdb_id'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all smpdb metabolite from database')

    load_all_smpdb_metabolite_and_finish_the_files(csv_mapping_metabolite, csv_not_mapped)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
