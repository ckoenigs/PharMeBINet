import csv
import sys
import datetime
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def integrate_information_into_dict(dict_node_id_to_resource, label, dict_alternative_id_to_identifiers):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:%s) RETURN n.identifier, n.resource, n.alternative_ids'''
    query = query % (label)
    results = g.run(query)

    for record in results:
        [identifier, resource, alternative_ids] = record
        dict_node_id_to_resource[identifier] = resource
        if alternative_ids:
            for alternative_id in alternative_ids:
                dict_alternative_id_to_identifiers[alternative_id].add(identifier)

    print('number of', label, 'in database', len(dict_node_id_to_resource))


def prepare_query(file_name, db_label, adrecs_label, adrecs_id):
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = ''' MATCH (n:%s{identifier:line.identifier}), (g:%s{%s:line.identifier_adrecst_target}) Set n.resource=split(line.resource,"|"), n.adrecstarget='yes' Create (n)-[:equal_adrecs_target_%s{how_mapped:line.how_mapped}]->(g)'''
    query = query % (db_label, adrecs_label, adrecs_id, db_label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/{director}/{file_name}', query)
    cypher_file.write(query)


def get_all_adrecs_target_and_map(db_label, adrecs_label, adrecs_id, dict_node_id_to_resource,
                                  dict_alternative_ids_to_identifiers):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['identifier', 'identifier_adrecst_target', 'resource', 'how_mapped'])

    file_not_name = db_label.lower() + '/not_mapping.tsv'
    not_mapping_file = open(file_not_name, 'w', encoding='utf-8')
    csv_not_mapping = csv.writer(not_mapping_file, delimiter='\t')
    csv_not_mapping.writerow(['identifier', 'name'])

    prepare_query(file_name, db_label, adrecs_label, adrecs_id)

    # get data
    query = '''MATCH (n:%s) RETURN n'''
    query = query % (adrecs_label)
    results = g.run(query)

    counter_mapped = 0
    counter_not_mapped = 0

    for record in results:
        node = record.data()['n']
        identifier = node[adrecs_id]
        if identifier in dict_node_id_to_resource:
            counter_mapped += 1
            resource = dict_node_id_to_resource[identifier]
            resource.append('ADReCS-Target')
            resource = sorted(resource)
            csv_mapping.writerow([identifier, identifier, '|'.join(resource), 'identifier'])
        elif identifier in dict_alternative_ids_to_identifiers:
            counter_mapped += 1
            for real_id in dict_alternative_ids_to_identifiers[identifier]:
                resource = dict_node_id_to_resource[real_id]
                resource.append('ADReCS-Target')
                resource = sorted(resource)
                csv_mapping.writerow([real_id, identifier, '|'.join(resource), 'alternative identifier'])
        else:
            # print(db_label, ' not in database :O')
            # print(identifier)
            counter_not_mapped += 1
            gene_full_name=node['GENE_FULL_NAME'] if 'GENE_FULL_NAME' in node else ''
            csv_not_mapping.writerow([identifier, gene_full_name])
    print('number of mapped:', counter_mapped)
    print('number of not mapped:', counter_not_mapped)


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

    dict_label_to_at_label = {
        'Gene': ['gene_ADReCSTarget', 'GENE_ID'],
        'Protein': ['protein_ADReCSTarget', 'UNIPROT_AC']
    }

    for db_label, adrecs_target_label_and_identifier_name in dict_label_to_at_label.items():
        # dict node id to resource
        dict_node_id_to_resource = {}

        dict_alternative_ids_to_identifiers = defaultdict(set)

        print('##########################################################################')

        print(datetime.datetime.now())
        print('get all genes from database')

        integrate_information_into_dict(dict_node_id_to_resource, db_label, dict_alternative_ids_to_identifiers)

        print('##########################################################################')

        print(datetime.datetime.now())
        print('prepare file and write information of mapping in it')

        get_all_adrecs_target_and_map(db_label, adrecs_target_label_and_identifier_name[0],
                                      adrecs_target_label_and_identifier_name[1], dict_node_id_to_resource,
                                      dict_alternative_ids_to_identifiers)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
