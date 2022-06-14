import csv
import sys
import datetime
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
from pharmebinetutils import *

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()



# dictionary name to ids
dict_name_to_id = defaultdict(set)

# dictionary synonyms to ids
dict_synonyms_to_id = defaultdict(set)


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.synonyms, n.resource'''
    results = g.run(query)

    for identifier, name, synonyms, resource, in results:
        dict_node_id_to_resource[identifier] = resource

        name = name.lower()
        dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_name_to_id[synonym].add(identifier)

    print('number of Chemical in database', len(dict_node_id_to_resource))


def prepare_query(file_name):
    """
    prepare query fro integration
    :param file_name:string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = get_query_start(path_of_directory+"mapping_and_merging_into_hetionet/DDinter",file_name)+ '''MATCH (n:Chemical{identifier:line.db_id}), (g:drug_ddinter{identifier:line.ddinter_id}) Set n.resource=split(line.resource,"|"), n.ddinter='yes' Create (n)-[:equal_ddinter_chemical{how_mapped:line.how_mapped}]->(g);\n'''
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
    csv_mapping.writerow([identifier_db, identifier_act_id, resource_add_and_prepare(dict_node_id_to_resource[identifier_db],"DDinter") , how_mapped])


def get_all_ddinter_and_map(dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = 'output/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'ddinter_id', 'resource', 'how_mapped'])

    prepare_query(file_name)

    # get data
    query = '''MATCH (n:drug_ddinter) RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    for node, in results:
        # rs or a name
        identifier = node['identifier']
        name = node['name'].lower()
        if name in dict_name_to_id:
            counter_mapping += 1
            for drugbank_id in dict_name_to_id[name]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping,'name_mapping')
        elif name in dict_synonyms_to_id:
            counter_mapping += 1
            for drugbank_id in dict_synonyms_to_id[name]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping,'synonyms_mapping')

        else:
            counter_not_mapped += 1
            print(' not in database :O')
            print(identifier, name)
    print('mapped:', counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ddinter')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')

    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all drugs from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_ddinter_and_map(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
