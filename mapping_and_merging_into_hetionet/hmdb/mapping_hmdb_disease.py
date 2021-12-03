# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


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


'''
load in all disease from hetionet in a dictionary
'''


def load_hetionet_labels_in(label, dict_label_id_to_resource, dict_name_to_ids, dict_synonyms_to_ids,
                            dict_xref_id_to_ids):
    query = '''MATCH (n:%s) RETURN n.identifier, n.name, n.xrefs, n.synonyms, n.resource''' % label
    results = graph_database.run(query)

    #  run through results
    for identifier, name, xrefs, synonyms, resource, in results:
        dict_label_id_to_resource[identifier] = set(resource)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('OMIM:'):
                    omim_id = xref.split(':')[1]
                    add_to_dictionary_with_set(dict_xref_id_to_ids, omim_id, identifier)

        if name:
            add_to_dictionary_with_set(dict_name_to_ids, name.lower(), identifier)

        if synonyms:
            for synonym in synonyms:
                synonym=synonym.rsplit(' [',1)[0]
                add_to_dictionary_with_set(dict_synonyms_to_ids, synonym.lower(), identifier)

    print('number of disease nodes in hetionet:' + str(len(dict_label_id_to_resource)))

# file for mapped or not mapped identifier
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_disease, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])

'''
generate connection between mapping disease of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file(label, file_name):
    cypher_file = open('output/cypher_part2.cypher', 'a', encoding="utf-8")
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.id_own_db}),(c:Disease_HMDB{identifier:line.id}) CREATE (d)-[: equal_to_hmdb_disease{how_mapped:line.how_mapped}]->(c) SET d.resource = split(line.resource, '|'), d.hmdb = "yes";\n'''
    query = query % (path_of_directory, file_name, label)
    cypher_file.write(query)

def create_files(label):
    """
    prepare mapping file for label and generate cypher query
    :param label: string
    :return: csv writer
    """
    file_name='disease/mapped_'+label+'.tsv'
    file_mapped_disease = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_disease, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id', 'id_own_db', 'resource', 'how_mapped'])

    create_cypher_file(label, file_name)
    return csv_mapped


def prepare_resource(set_of_resource):
    set_of_resource.add('HMDB')
    return '|'.join(sorted(set_of_resource))


'''
load all hmdb disease and check if they are in hetionet or not
'''


def load_hmdb_disease_and_map():
    query = '''MATCH (n:Disease_HMDB) RETURN n'''
    results = graph_database.run(query)

    csv_writer_disease= create_files('Disease')
    csv_writer_symptom = create_files('Symptom')

    # count for the different mapping methods
    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_synonym_mapping = 0
    counter_not_mapped = 0
    for disease_node, in results:
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
                                     prepare_resource(dict_disease_id_to_resource[database_identifier]), 'name'])

        if is_mapped:
            continue

        # mapping with name to synonyms
        if disease_name in dict_synonym_to_disease_id:
            counter_synonym_mapping += 1
            is_mapped = True

            for database_identifier in dict_synonym_to_disease_id[disease_name]:
                csv_writer_disease.writerow([disease_id, database_identifier,
                                     prepare_resource(dict_disease_id_to_resource[database_identifier]),
                                     'name_to_synonyms'])

        if is_mapped:
            continue

        # mapping with name
        if disease_name in dict_symptom_name_to_symptom_ids:
            counter_map_with_name += 1
            is_mapped = True

            for database_identifier in dict_symptom_name_to_symptom_ids[disease_name]:
                csv_writer_symptom.writerow([disease_id, database_identifier,
                                             prepare_resource(dict_symptom_id_to_resource[database_identifier]),
                                             'name'])

        if is_mapped:
            continue

        # mapping with name to synonyms
        if disease_name in dict_synonym_to_symptom_id:
            counter_synonym_mapping += 1
            is_mapped = True

            for database_identifier in dict_synonym_to_symptom_id[disease_name]:
                csv_writer_symptom.writerow([disease_id, database_identifier,
                                             prepare_resource(dict_symptom_id_to_resource[database_identifier]),
                                             'name_to_synonyms'])

        # mapping with omim identifier
        if disease_id in dict_omim_id_to_disease_ids:
            counter_map_with_id += 1
            is_mapped = True
            for database_identifier in dict_omim_id_to_disease_ids[disease_id]:
                csv_writer_disease.writerow([disease_id, database_identifier,
                                     prepare_resource(dict_disease_id_to_resource[database_identifier]), 'omim id'])

        if is_mapped:
            continue

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
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all disease and symptom from hetionet into a dictionary')

    load_hetionet_labels_in('Disease', dict_disease_id_to_resource, dict_disease_name_to_disease_ids,
                            dict_synonym_to_disease_id, dict_omim_id_to_disease_ids)

    load_hetionet_labels_in('Symptom', dict_symptom_id_to_resource, dict_symptom_name_to_symptom_ids,
                            dict_synonym_to_symptom_id, dict_omim_id_to_symptom_ids)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all hmdb disease from neo4j into a dictionary')

    load_hmdb_disease_and_map()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
