import csv
import sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary name to ids
dict_name_to_id = {}


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.synonyms, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, resource] = record.values()
        dict_node_id_to_resource[identifier] = resource

        name = name.lower()
        if name not in dict_name_to_id:
            dict_name_to_id[name] = set()
        dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if synonym not in dict_name_to_id:
                    dict_name_to_id[synonym] = set()
                dict_name_to_id[synonym].add(identifier)

    print('number of Chemical in database', len(dict_node_id_to_resource))


def prepare_query(file_name, db_label, adrecs_label, db_id, adrecs_id_internal, adrecs_id):
    """
    prepare query for integration
    :param file_name:string
    :param db_label: string
    :param adrecs_label: string
    :param db_id: string
    :param adrecs_id_internal:string
    :param adrecs_id: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = ''' MATCH (n:%s{identifier:line.%s}), (g:%s{%s:line.%s}) Set n.resource=split(line.resource,"|"), n.adrecs_target='yes' Create (n)-[:equal_adrecs_target_%s{how_mapped:line.how_mapped}]->(g)'''
    query = query % (db_label, db_id, adrecs_label, adrecs_id_internal, adrecs_id, db_label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/{director}/{file_name}', query)
    cypher_file.write(query)


def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id, csv_mapping, how_mapped):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    csv_mapping.writerow([identifier_db, identifier_act_id,
                          pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier_db],
                                                                    'ADReCS-Target'), how_mapped])


def get_all_adrecs_target_and_map(db_label, dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'act_id', 'resource', 'how_mapped'])

    prepare_query(file_name, db_label, 'drug_ADReCSTarget', 'db_id', 'Drug_Name', 'act_id')

    # get data
    query = '''MATCH (n:drug_ADReCSTarget) RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    for record in results:
        node = record.data()['n']
        # rs or a name
        identifier = node['Drug_Name'].lower()
        drugbank_id = node['DrugBank_ID'] if 'DrugBank_ID' in node else ''
        found_mapping = False
        if drugbank_id != '':
            if drugbank_id in dict_node_id_to_resource:
                counter_mapping += 1
                found_mapping = True
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'drugbank id')

        if found_mapping:
            continue

        if identifier in dict_name_to_id:
            counter_mapping += 1
            for drugbank_id in dict_name_to_id[identifier]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'name mapping')

        else:
            counter_not_mapped += 1
            print(' not in database :O')
            print(identifier)
    print('mapped:', counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


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
    print('get all drugs from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_adrecs_target_and_map('Chemical', dict_node_id_to_resource)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
