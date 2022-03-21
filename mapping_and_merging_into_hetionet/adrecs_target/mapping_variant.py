import csv
import sys
import datetime

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dict rs id to identifier
dict_rs_to_ids = {}

# dictionary name to ids
dict_name_to_id = {}


def add_identifier_to_dictionary(identifier, id):
    """
    Check if an entry existi or not and in case of not generate with an empty set. Then add the identifier to the set.
    :param identifier:
    :param id:
    :return:
    """
    if id not in dict_rs_to_ids:
        dict_rs_to_ids[id] = set()
    dict_rs_to_ids[id].add(identifier)


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    Where n.identifier Starts With 'rs'
    """
    query = '''MATCH (n:Variant)  RETURN n.identifier, n.name, n.synonyms, n.alternative_ids, n.resource'''
    results = g.run(query)

    print(datetime.datetime.now())

    for identifier, name, synonyms, alternative_ids, resource, in results:
        dict_node_id_to_resource[identifier] = resource

        name = name.lower() if name else ''
        if name:
            if name not in dict_name_to_id:
                dict_name_to_id[name] = set()
            dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if synonym not in dict_name_to_id:
                    dict_name_to_id[synonym] = set()
                dict_name_to_id[synonym].add(identifier)

        if identifier.startswith('rs'):
            add_identifier_to_dictionary(identifier, identifier)

        if alternative_ids:
            for alternative_id in alternative_ids:
                add_identifier_to_dictionary((identifier, alternative_id))

    print('number of Variant in database', len(dict_node_id_to_resource))


def prepare_query(file_name, file_name_new, db_label, adrecs_label):
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/%s/%s" As line Fieldterminator '\\t' MATCH (n:%s{identifier:line.variant_id}), (g:%s{Variation_ID:line.adr_variant_id}) Set n.resource=split(line.resource,"|"), n.adrecs_target='yes' Create (n)-[:equal_adrecs_target_variant{how_mapped:line.how_mapped}]->(g);\n'''
    query = query % (director, file_name, db_label, adrecs_label)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/%s/%s" As line Fieldterminator '\\t' MATCH (g:%s{Variation_ID:line.identifier}) Create (c:Variant :GeneVariant{identifier:line.identifier, adrecstarget:'yes', resource:["ADReCS-Target"], xrefs:["dbSNP:"+line.identifier] ,license:"%s" , source:"dbSNP from ADReCSV-Target"})-[:equal_adrecs_target_variant{how_mapped:'new'}]->(g);\n'''
    query = query % (director, file_name_new, adrecs_label, 'license')
    cypher_file.write(query)

    cypher_file.close()


def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id, csv_mapping, how_mapped):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string6
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    resource = dict_node_id_to_resource[identifier_db]
    resource.append('ADReCS-Target')
    resource = sorted(resource)
    csv_mapping.writerow([identifier_db, identifier_act_id, '|'.join(resource), how_mapped])


def get_all_adrecs_target_and_map(db_label, dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['variant_id', 'adr_variant_id', 'resource', 'how_mapped'])

    file_new_name = db_label.lower() + '/new_variants.csv'
    new_file = open(file_new_name, 'w', encoding='utf-8')
    csv_new = csv.writer(new_file, delimiter='\t')
    csv_new.writerow(['identifier'])

    file_not_name = db_label.lower() + '/not_mapping.tsv'
    not_mapping_file = open(file_not_name, 'w', encoding='utf-8')
    csv_not_mapping = csv.writer(not_mapping_file, delimiter='\t')
    csv_not_mapping.writerow(['identifier'])

    prepare_query(file_name, file_new_name, db_label, 'variant_ADReCSTarget')

    # get data
    query = '''MATCH (n:variant_ADReCSTarget) RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    # counter not mapped
    counter_not_mapped = 0
    for node, in results:
        # rs or a name
        identifier = node['Variation_ID'].lower()
        if identifier in dict_rs_to_ids:
            counter_mapping += 1
            for variant_id in dict_rs_to_ids[identifier]:
                add_to_file(dict_node_id_to_resource, variant_id, node['Variation_ID'], csv_mapping, 'id')
        elif identifier in dict_name_to_id:
            counter_mapping += 1
            for variant_id in dict_name_to_id[identifier]:
                add_to_file(dict_node_id_to_resource, variant_id, node['Variation_ID'], csv_mapping, 'name')

        else:
            counter_not_mapped += 1
            if identifier.startswith('rs'):
                csv_new.writerow([identifier])
            else:
                # print(' not in database :O')
                # print(identifier)
                csv_not_mapping.writerow([identifier])
    print('mapped:', counter_mapping)
    print('not mapped', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        director = sys.argv[2]
    else:
        sys.exit('need a path adrecs-target and directory')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')

    # dict node id to resource
    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all variant from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_adrecs_target_and_map('Variant', dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
