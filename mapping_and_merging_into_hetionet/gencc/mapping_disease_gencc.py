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
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


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
dict_disease_id_to_omim_count={}

# dictionary from source to source id to set of disease ids
dict_xref_to_xref_id_to_disease_ids={'OMIM':{},'Orphanet':{}}


'''
load in all disease from pharmebinet in a dictionary
'''


def load_pharmebinet_labels_in(label, dict_label_id_to_resource, dict_name_to_ids):
    query = '''MATCH (n:%s) RETURN n.identifier, n.name, n.xrefs, n.synonyms, n.resource''' % label
    results = graph_database.run(query)

    #  run through results
    for identifier, name, xrefs, synonyms, resource, in results:
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

# file for mapped or not mapped identifier
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_disease, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])

'''
generate connection between mapping disease of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file(label, file_name):
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/gencc/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.id_own_db}),(c:gencc_disease_mondo_dict{disease_curie:line.id}) CREATE (d)-[: equal_to_gencc_disease{how_mapped:line.how_mapped}]->(c) SET d.resource = split(line.resource, '|'), d.gencc = "yes";\n'''
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



'''
load all gencc disease and check if they are in pharmebinet or not
'''


def load_gencc_disease_and_map():
    query = '''MATCH (n:gencc_disease_mondo_dict) RETURN n'''
    results = graph_database.run(query)

    csv_writer_disease= create_files('Disease')

    # count for the different mapping methods
    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_synonym_mapping = 0
    counter_not_mapped = 0
    for disease_node, in results:
        disease_id = disease_node['disease_curie']
        disease_names = disease_node['disease_title']

        # boolean for mapping
        is_mapped = False

        if disease_id in dict_disease_id_to_resource:
            is_mapped = True
            counter_map_with_id+=1
            csv_writer_disease.writerow([disease_id, disease_id,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_disease_id_to_resource[disease_id], 'GENCC'), 'id'])
        if is_mapped:
            continue

        # mapping with name
        if disease_names:
            for disease_name in disease_names:
                disease_name=disease_name.lower()
                if disease_name in dict_disease_name_to_disease_ids:
                    counter_map_with_name += 1
                    is_mapped = True

                    for database_identifier in dict_disease_name_to_disease_ids[disease_name]:
                        csv_writer_disease.writerow([disease_id, database_identifier,
                                             pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[database_identifier],'GENCC'), 'name'])

        if is_mapped:
            continue


        xrefs=disease_node['disease_original_curie']
        omim_ids=set()
        orphanet_ids=set()
        for xref in xrefs:
            if xref.startswith('OMIM:'):
                omim_id = xref.split(':')[1]
                omim_ids.add(omim_id)
            elif xref.startswith('Orphanet:'):
                orphanet_id = xref.split(':')[1]
                orphanet_ids.add(orphanet_id)

        if len(orphanet_ids)>0:
            for ref in orphanet_ids:
                if ref in dict_xref_to_xref_id_to_disease_ids['Orphanet']:
                    counter_map_with_name += 1
                    is_mapped = True

                    for database_identifier in dict_xref_to_xref_id_to_disease_ids['Orphanet'][ref]:
                        csv_writer_disease.writerow([disease_id, database_identifier,
                                                     pharmebinetutils.resource_add_and_prepare(
                                                         dict_disease_id_to_resource[database_identifier], 'GENCC'),
                                                     'orphanet'])

        if is_mapped:
            continue

        if len(omim_ids)>0:
            for ref in omim_ids:
                if ref in dict_xref_to_xref_id_to_disease_ids['OMIM']:
                    counter_map_with_name += 1
                    is_mapped = True

                    for database_identifier in dict_xref_to_xref_id_to_disease_ids['OMIM'][ref]:
                        csv_writer_disease.writerow([disease_id, database_identifier,
                                                     pharmebinetutils.resource_add_and_prepare(
                                                         dict_disease_id_to_resource[database_identifier], 'GENCC'),
                                                     'omim'])

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
    print('Load all gencc disease from neo4j into a dictionary')

    load_gencc_disease_and_map()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
