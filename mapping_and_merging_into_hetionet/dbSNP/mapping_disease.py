import sys
import datetime
import csv
from itertools import groupby

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def database_connection():
    '''
    create connection to neo4j
    '''
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary disease id to disease node
dict_disease_id_to_disease_node = {}

# dictionary xrefs to disease id
dict_xref_to_xref_id_to_disease_ids = {}

# dictionary disease names to set disease ids
dict_disease_name_to_ids = {}

# dictionary disease synonyms to set diease ids
dict_disease_synonyms_to_ids = {}

# dictionary disease id to resource
dict_disease_id_to_resource = {}


def add_to_dictionary_with_set(dictionary, key, value):
    """
    Add information to dictionary with set
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return: 
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def load_genes_from_database_and_add_to_dict():
    '''
    Load all Disease from my database  and add them into a dictionary
    '''
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)
    for disease, in results:
        identifier = disease['identifier']
        dict_disease_id_to_disease_node[identifier] = dict(disease)
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        dict_disease_id_to_resource[identifier] = set(disease['resource'])
        for xref in xrefs:
            split_xref = xref.split(':')
            xref_source = split_xref[0].lower()
            xref_id = split_xref[1]
            if xref_source not in dict_xref_to_xref_id_to_disease_ids:
                dict_xref_to_xref_id_to_disease_ids[xref_source] = {}
            add_to_dictionary_with_set(dict_xref_to_xref_id_to_disease_ids[xref_source], xref_id, identifier)

        if 'name' in disease:
            name = disease['name'].lower()
            add_to_dictionary_with_set(dict_disease_name_to_ids, name, identifier)

        if 'synonyms' in disease:
            synonyms = disease['synonyms']
            for synonym in synonyms:
                add_to_dictionary_with_set(dict_disease_synonyms_to_ids,
                                           pharmebinetutils.prepare_obo_synonyms(synonym).lower(), identifier)


cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/dbsnp/%s" As line FIELDTERMINATOR '\\t' 
    Match '''


def add_query_to_cypher_file(file_name):
    '''
    add query for a specific tsv to cypher file
    '''
    this_start_query = query_start + "(n:disease_dbSNP {identifier:line.identifier}), (m:Disease{identifier:line.disease_id}) Set m.dbSNP='yes', m.resource=split(line.resource,'|') Create (m)-[:equal_to_dbsnp_disease{how_mapped:split(line.how_mapped,'|')}]->(n);\n"
    query = this_start_query % (path_of_directory, file_name)
    cypher_file.write(query)


def generate_files():
    """
    Generate tsv mapping file and cypher query
    :return:
    """
    file_name = 'disease/mapping.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier', 'disease_id', 'resource', 'how_mapped'])

    add_query_to_cypher_file(file_name)
    return csv_writer


def add_resource(set_resource):
    """
    Add source to resource and prepare to string
    :param set_resource:
    :return:
    """
    set_resource.add('dbSNP')
    return '|'.join(set_resource)


# dictionary_clinvar_disease_id_to_node
dict_dbsnp_id_to_node = {}

# dictionary of mapping tuples
dict_of_mapped_tuples = {}

# set of not mapped clinvar disease ids
set_not_mapped_ids = set()

# set of all xref type used for mapping
set_of_all_xref_types_to_map = set()


def load_all_dbsnp_disease_and_map():
    """
    load all trait disease in and mapp with xref to the mondo diseases
    """
    query = "MATCH (n:disease_dbSNP) RETURN n"
    results = g.run(query)
    counter_mapped = 0
    csv_mapped = generate_files()
    file = open('disease/not_mapped.tsv', 'w', encoding='utf-8')
    csv_not_mapped = csv.writer(file, delimiter='\t')
    csv_not_mapped.writerow(['identifier', 'name'])
    for node, in results:
        identifier = node['identifier']

        dict_dbsnp_id_to_node[identifier] = dict(node)

        name = node['name'].lower()

        xrefs = node['xrefs'] if 'xrefs' in node else []

        found_at_least_one_mapping = False

        if ':' in identifier:
            split_id = identifier.split(':', 1)
            source_maybe = split_id[0].lower()
            if source_maybe in dict_xref_to_xref_id_to_disease_ids:
                source_id = split_id[1]
                if source_id in dict_xref_to_xref_id_to_disease_ids[source_maybe]:
                    set_of_all_xref_types_to_map.add(source_maybe)
                    for disease_id in dict_xref_to_xref_id_to_disease_ids[source_maybe][source_id]:
                        csv_mapped.writerow(
                            [identifier, disease_id, add_resource(dict_disease_id_to_resource[disease_id]),
                             'identifier'])
                    counter_mapped += 1
                    found_at_least_one_mapping = True

        if found_at_least_one_mapping:
            continue

        for xref in xrefs:
            split_id = xref.split(':', 1)
            source = split_id[0].lower()
            if source in dict_xref_to_xref_id_to_disease_ids:
                source_id = split_id[1]
                if source_id in dict_xref_to_xref_id_to_disease_ids[source]:
                    set_of_all_xref_types_to_map.add(source)
                    for disease_id in dict_xref_to_xref_id_to_disease_ids[source][source_id]:
                        csv_mapped.writerow(
                            [identifier, disease_id, add_resource(dict_disease_id_to_resource[disease_id]),
                             'identifier'])
                    counter_mapped += 1
                    found_at_least_one_mapping = True

        if found_at_least_one_mapping:
            continue

        if name:
            if name in dict_disease_name_to_ids:
                counter_mapped += 1
                found_at_least_one_mapping = True
                for disease_id in dict_disease_name_to_ids[name]:
                    csv_mapped.writerow(
                        [identifier, disease_id, add_resource(dict_disease_id_to_resource[disease_id]), 'name_name'])

        if found_at_least_one_mapping:
            continue

        if name:
            if name in dict_disease_synonyms_to_ids:
                counter_mapped += 1
                found_at_least_one_mapping = True
                for disease_id in dict_disease_synonyms_to_ids[name]:
                    csv_mapped.writerow(
                        [identifier, disease_id, add_resource(dict_disease_id_to_resource[disease_id]),
                         'name_synonyms'])

        if not found_at_least_one_mapping:
            set_not_mapped_ids.add(identifier)
            csv_not_mapped.writerow([identifier, name])

    print(dict_of_mapped_tuples)
    print('number of mapped disease:' + str(counter_mapped))
    print('number of not mapped disease:' + str(len(set_not_mapped_ids)))
    print('used xref:')
    print(set_of_all_xref_types_to_map)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path dbSNP')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all disease from database')

    load_genes_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all disease clinvar from database')

    load_all_dbsnp_disease_and_map()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
