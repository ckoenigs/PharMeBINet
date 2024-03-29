import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary disease id to resource
dict_disease_id_to_resource = {}

# dictionary omim id to set of disease ids
dict_omim_id_to_disease_ids = {}

# dictionary disease name to disease ids
dict_disease_name_to_disease_ids = {}

# dictionary synonyms to disease ids
dict_synonym_to_disease_id = {}

# dictionary symptom id to resource
dict_symptom_id_to_resource = {}

# dictionary omim id to set of symptom ids
dict_omim_id_to_symptom_ids = {}

# dictionary disease name to symptom ids
dict_symptom_name_to_symptom_ids = {}

# dictionary synonyms to symptom ids
dict_synonym_to_symptom_id = {}


def add_to_dictionary_with_set(dictionary, key, value):
    """
    add value to key in dictionary
    :param dictionary: dictionary
    :param key: string
    :param value:  string
    :return:
    """
    if not key in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


# dictionary disease identifier to omim counter
dict_disease_id_to_omim_count = {}

'''
load in all disease from pharmebinet in a dictionary
'''


def load_pharmebinet_labels_in(label, dict_label_id_to_resource, dict_name_to_ids, dict_synonyms_to_ids,
                               dict_xref_id_to_ids):
    query = '''MATCH (n:%s) RETURN n.identifier, n.name, n.xrefs, n.synonyms, n.resource''' % label
    results = graph_database.run(query)

    #  run through results
    for record in results:
        [identifier, name, xrefs, synonyms, resource] = record.values()
        dict_label_id_to_resource[identifier] = set(resource)
        dict_disease_id_to_omim_count[identifier] = 0
        if xrefs:
            for xref in xrefs:
                if xref.startswith('OMIM:'):
                    omim_id = xref.split(':')[1]
                    add_to_dictionary_with_set(dict_xref_id_to_ids, omim_id, identifier)
                    dict_disease_id_to_omim_count[identifier] += 1

        if name:
            add_to_dictionary_with_set(dict_name_to_ids, name.lower(), identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym)
                add_to_dictionary_with_set(dict_synonyms_to_ids, synonym.lower(), identifier)

    print('number of disease nodes in pharmebinet:' + str(len(dict_label_id_to_resource)))


# file for mapped or not mapped identifier
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_disease, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])

'''
generate connection between mapping disease of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file(label, file_name):
    cypher_file = open('output/cypher_part2.cypher', 'a', encoding="utf-8")
    query = ''' MATCH (d:%s{identifier:line.id_own_db}),(c:Disease_HMDB{identifier:line.id}) CREATE (d)-[: equal_to_hmdb_disease{how_mapped:line.how_mapped}]->(c) SET d.resource = split(line.resource, '|'), d.hmdb = "yes"'''
    query = query % (label)

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hmdb/{file_name}',
                                              query)
    cypher_file.write(query)


def create_files(label):
    """
    prepare mapping file for label and generate cypher query
    :param label: string
    :return: csv writer
    """
    file_name = 'disease/mapped_' + label + '.tsv'
    file_mapped_disease = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_disease, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id', 'id_own_db', 'resource', 'how_mapped'])

    create_cypher_file(label, file_name)
    return csv_mapped


'''
load all hmdb disease and check if they are in pharmebinet or not
'''


def load_hmdb_disease_and_map():
    query = '''MATCH (n:Disease_HMDB) RETURN n'''
    results = graph_database.run(query)

    csv_writer_disease = create_files('Disease')
    csv_writer_symptom = create_files('Symptom')

    # count for the different mapping methods
    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_synonym_mapping = 0
    counter_not_mapped = 0
    for record in results:
        disease_node = record.data()['n']
        disease_id = disease_node['identifier']
        disease_name = disease_node['name'].lower()

        # boolean for mapping
        is_mapped = False

        # mapping with name
        if disease_name in dict_disease_name_to_disease_ids:
            counter_map_with_name += 1
            is_mapped = True

            for database_identifier in dict_disease_name_to_disease_ids[disease_name]:
                csv_writer_disease.writerow([disease_id, database_identifier,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_disease_id_to_resource[database_identifier], 'HMDB'), 'name'])

        if is_mapped:
            continue

        # mapping with name to synonyms
        if disease_name in dict_synonym_to_disease_id:
            counter_synonym_mapping += 1
            is_mapped = True

            for database_identifier in dict_synonym_to_disease_id[disease_name]:
                csv_writer_disease.writerow([disease_id, database_identifier,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_disease_id_to_resource[database_identifier], 'HMDB'),
                                             'name_to_synonyms'])

        if is_mapped:
            continue

        # mapping with name
        if disease_name in dict_symptom_name_to_symptom_ids:
            counter_map_with_name += 1
            is_mapped = True

            for database_identifier in dict_symptom_name_to_symptom_ids[disease_name]:
                csv_writer_symptom.writerow([disease_id, database_identifier,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_symptom_id_to_resource[database_identifier], 'HMDB'),
                                             'name'])

        if is_mapped:
            continue

        # mapping with name to synonyms
        if disease_name in dict_synonym_to_symptom_id:
            counter_synonym_mapping += 1
            is_mapped = True

            for database_identifier in dict_synonym_to_symptom_id[disease_name]:
                csv_writer_symptom.writerow([disease_id, database_identifier,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_symptom_id_to_resource[database_identifier], 'HMDB'),
                                             'name_to_synonyms'])

        # mapping with omim identifier
        if disease_id in dict_omim_id_to_disease_ids:
            counter_map_with_id += 1
            is_mapped = True
            mondo_diseases = set()
            lowest_count = 100
            for database_identifier in dict_omim_id_to_disease_ids[disease_id]:
                omim_ids_of_the_id = dict_disease_id_to_omim_count[database_identifier]
                if lowest_count > omim_ids_of_the_id:
                    mondo_diseases = set([database_identifier])
                    lowest_count = omim_ids_of_the_id
                elif lowest_count == omim_ids_of_the_id:
                    mondo_diseases.add(database_identifier)

            for mondo_disease in mondo_diseases:
                csv_writer_disease.writerow([disease_id, mondo_disease,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_disease_id_to_resource[mondo_disease], 'HMDB'), 'omim_id'])
            if lowest_count != 1:
                print(lowest_count, mondo_diseases)
                print(dict_omim_id_to_disease_ids[disease_id])
                print(disease_id, disease_name)

        if is_mapped:
            continue

        counter_not_mapped += 1
        csv_not_mapped.writerow([disease_id, disease_name])

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with synonyms:' + str(counter_synonym_mapping))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('number of not mapped nodes:', counter_not_mapped)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hmdb disease')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all disease and symptom from pharmebinet into a dictionary')

    load_pharmebinet_labels_in('Disease', dict_disease_id_to_resource, dict_disease_name_to_disease_ids,
                               dict_synonym_to_disease_id, dict_omim_id_to_disease_ids)

    load_pharmebinet_labels_in('Symptom', dict_symptom_id_to_resource, dict_symptom_name_to_symptom_ids,
                               dict_synonym_to_symptom_id, dict_omim_id_to_symptom_ids)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all hmdb disease from neo4j into a dictionary')

    load_hmdb_disease_and_map()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
