import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary disease id to resource
dict_disease_id_to_resource = {}

# dictionary disease name to disease ids
dict_disease_name_to_disease_ids = {}


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

# dictionary from source to source id to set of disease ids
dict_xref_to_xref_id_to_disease_ids = {'OMIM': {}, 'Orphanet': {}}

# dictionary obsolete mondo id to replaced id
dict_obsolete_id_to_replace_id = {}


def load_pharmebinet_labels_in(label, dict_label_id_to_resource, dict_name_to_ids):
    """
    load in all disease from pharmebinet in a dictionary
    :param label:
    :param dict_label_id_to_resource:
    :param dict_name_to_ids:
    :return:
    """
    query = '''MATCH (n:%s) RETURN n.identifier, n.name, n.xrefs, n.synonyms, n.resource''' % label
    results = graph_database.run(query)

    #  run through results
    for record in results:
        [identifier, name, xrefs, synonyms, resource] = record.values()
        dict_label_id_to_resource[identifier] = set(resource)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('OMIM:'):
                    omim_id = xref.split(':')[1]
                    add_to_dictionary_with_set(dict_xref_to_xref_id_to_disease_ids['OMIM'], omim_id, identifier)
                elif xref.startswith('Orphanet:'):
                    xref_id = xref.split(':')[1]
                    add_to_dictionary_with_set(dict_xref_to_xref_id_to_disease_ids['Orphanet'], xref_id, identifier)

        if name:
            add_to_dictionary_with_set(dict_name_to_ids, name.lower(), identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym)
                add_to_dictionary_with_set(dict_name_to_ids, synonym.lower(), identifier)

    print('number of disease nodes in pharmebinet:' + str(len(dict_label_id_to_resource)))

    # use the obsolete mondo information for mapping
    query = 'Match (n:disease) Where n.is_obsolete="true" and not n.replaced_by is null Return n.id, n.replaced_by '
    results = graph_database.run(query)

    #  run through results
    for record in results:
        [identifier, replaced_by] = record.values()
        dict_obsolete_id_to_replace_id[identifier] = replaced_by


# file for mapped or not mapped identifier
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_disease, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])


def create_cypher_file(label, file_name):
    """
    prepare cypher query for mapping the disease to gencc disease
    :param label:
    :param file_name:
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    query = ''' MATCH (d:%s{identifier:line.id_own_db}),(c:GenCC_Disease{id:line.id}) CREATE (d)-[: equal_to_gencc_disease{how_mapped:line.how_mapped}]->(c) SET d.resource = split(line.resource, '|'), d.gencc = "yes"'''
    query = query % (label)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/gencc/{file_name}',
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


# dictionary node id to synonyms
dict_node_id_to_synonyms = {}

# dictionary from node id to xref to identifier
dict_node_id_to_resource_to_ids = {}


def load_extensions_information_from_gencc_edges():
    """
    Load all disease-gene gencc edges and qrite disease and edge information into a dictionary
    :return:
    """
    query = 'MATCH p=(n:GenCC_Disease)-[r]-(:GenCC_Gene)  Return ID(n), r.disease_original_curie, r.disease_original_title'
    results = graph_database.run(query)
    for record in results:
        [node_id, xref, synonym] = record.values()
        pharmebinetutils.add_entry_to_dict_to_set(dict_node_id_to_synonyms, node_id, synonym)
        source_id = xref.split(':', 1)
        if node_id not in dict_node_id_to_resource_to_ids:
            dict_node_id_to_resource_to_ids[node_id] = {}
        if source_id[0] not in dict_node_id_to_resource_to_ids[node_id]:
            dict_node_id_to_resource_to_ids[node_id][source_id[0]] = set()
        dict_node_id_to_resource_to_ids[node_id][source_id[0]].add(source_id[1])


def load_gencc_disease_and_map():
    """
    load all gencc disease and check if they are in pharmebinet or not
    :return:
    """
    query = '''MATCH (n:GenCC_Disease) RETURN n, ID(n)'''
    results = graph_database.run(query)

    csv_writer_disease = create_files('Disease')

    # count for the different mapping methods
    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_synonym_mapping = 0
    counter_not_mapped = 0
    for record in results:
        [disease_node, node_id] = record.values()
        disease_id = disease_node['id']
        disease_name = disease_node['title']

        # boolean for mapping
        is_mapped = False

        if disease_id in dict_disease_id_to_resource:
            is_mapped = True
            counter_map_with_id += 1
            csv_writer_disease.writerow([disease_id, disease_id,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_disease_id_to_resource[disease_id], 'GenCC'), 'id'])
        if is_mapped:
            continue

        if disease_id in dict_obsolete_id_to_replace_id:
            replaced_id = dict_obsolete_id_to_replace_id[disease_id]
            if replaced_id in dict_disease_id_to_resource:
                is_mapped = True
                counter_map_with_id += 1
                csv_writer_disease.writerow([disease_id, replaced_id,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_disease_id_to_resource[replaced_id], 'GenCC'), 'obsolete'])
        if is_mapped:
            continue

        # mapping with name
        if disease_name:
            disease_name = disease_name.lower()
            if disease_name in dict_disease_name_to_disease_ids:
                counter_map_with_name += 1
                is_mapped = True

                for database_identifier in dict_disease_name_to_disease_ids[disease_name]:
                    csv_writer_disease.writerow([disease_id, database_identifier,
                                                 pharmebinetutils.resource_add_and_prepare(
                                                     dict_disease_id_to_resource[database_identifier], 'GenCC'),
                                                 'name'])

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
        sys.exit('need a path gencc disease')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all disease and symptom from pharmebinet into a dictionary')

    load_pharmebinet_labels_in('Disease', dict_disease_id_to_resource, dict_disease_name_to_disease_ids)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all gencc disease extension information from the gencc edge')

    load_extensions_information_from_gencc_edges()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all gencc disease from neo4j into a dictionary')

    load_gencc_disease_and_map()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
