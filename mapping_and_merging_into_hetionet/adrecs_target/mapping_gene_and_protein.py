import csv
import sys
import datetime

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def integrate_information_into_dict(dict_node_id_to_resource, label):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:%s) RETURN n.identifier, n.resource'''
    query = query % (label)
    results = g.run(query)

    for identifier, resource, in results:
        dict_node_id_to_resource[identifier] = resource

    print('number of', label, 'in database', len(dict_node_id_to_resource))


def prepare_query(file_name, db_label, adrecs_label, adrecs_id):
    cypher_file = open(db_label.lower() + '/cypher.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/%s/%s" As line MATCH (n:%s{identifier:line.identifier}), (g:%s{%s:line.identifier}) Set n.resource=split(line.resource,"|") Create (n)-[:equal_adrecs_target_%s}]->(g);\n'''
    query = query % (director, file_name, db_label, adrecs_label, adrecs_id, db_label.lower())
    cypher_file.write(query)


def get_all_adrecs_target_and_map(db_label, adrecs_label, adrecs_id, dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.csv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['identifier', 'resource'])

    prepare_query(file_name, db_label, adrecs_label, adrecs_id)

    # get data
    query = '''MATCH (n:%s) RETURN n'''
    query = query % (adrecs_label)
    results = g.run(query)

    for node, in results:
        identifier = node[adrecs_id]
        if identifier in dict_node_id_to_resource:
            resource = dict_node_id_to_resource[identifier]
            resource.append('ADReCS-Target')
            resource = sorted(resource)
            csv_mapping.writerow([identifier, '|'.join(resource)])
        else:
            print(db_label, ' not in database :O')
            print(identifier)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory, director
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        director = sys.argv[2]
    else:
        sys.exit('need a path adrecs-target and directory')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('prepare for each label the files')

    dict_label_to_at_label = {
        'Gene': ['gene_ADReCSTarget', 'GENE_ID'],
        'Protein': ['protein_ADReCSTarget', 'UNIPROT_AC']
    }

    for db_label, adrecs_target_label_and_identifier_name in dict_label_to_at_label.items():
        # dict node id to resource
        dict_node_id_to_resource = {}

        print('##########################################################################')

        print(datetime.datetime.utcnow())
        print('get all genes from database')

        integrate_information_into_dict(dict_node_id_to_resource, db_label)

        print('##########################################################################')

        print(datetime.datetime.utcnow())
        print('prepare file and write information of mapping in it')

        get_all_adrecs_target_and_map(db_label,adrecs_target_label_and_identifier_name[0],adrecs_target_label_and_identifier_name[1],dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
