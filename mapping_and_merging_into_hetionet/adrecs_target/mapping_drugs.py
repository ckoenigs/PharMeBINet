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

# dictionary name to ids
dict_name_to_id={}

def integrate_information_into_dict(dict_node_id_to_resource, label):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) Where not n:Product RETURN n.identifier, n.name, n.synonyms, n.resource'''
    query = query % (label)
    results = g.run(query)

    for identifier, name, synonyms, resource, in results:
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


    print('number of', label, 'in database', len(dict_node_id_to_resource))


def prepare_query(file_name, db_label, adrecs_label, db_id,adrecs_id_internal, adrecs_id):
    """
    prepare query fro integration
    :param file_name:string
    :param db_label: string
    :param adrecs_label: string
    :param db_id: string
    :param adrecs_id_internal:string
    :param adrecs_id: string
    :return:
    """
    cypher_file = open(db_label.lower() + '/cypher.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/%s/%s" As line MATCH (n:%s{identifier:line.%s}), (g:%s{%s:line.%s}) Set n.resource=split(line.resource,"|"), n.adrecs_target='yes' Create (n)-[:equal_adrecs_target_%s}]->(g);\n'''
    query = query % (director, file_name, db_label, db_id,adrecs_label, adrecs_id_internal, adrecs_id, db_label.lower())
    cypher_file.write(query)

def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id,csv_mapping):
    """
    add resource and write mapping pair in csv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    resource = set(dict_node_id_to_resource[identifier_db])
    resource.add('ADReCS-Target')
    resource = sorted(resource)
    csv_mapping.writerow([identifier_db, identifier_act_id, '|'.join(resource)])

def get_all_adrecs_target_and_map(db_label,  dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.csv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'act_id', 'resource'])

    prepare_query(file_name, db_label, 'drug_ADReCSTarget','db_id','Drug_Name','act_id')

    # get data
    query = '''MATCH (n:drug_ADReCSTarget) RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping=0
    for node, in results:
        #rs or a name
        identifier = node['Drug_Name'].lower()
        drugbank_id= node['DrugBank_ID'] if 'DrugBank_ID' in node else ''
        if drugbank_id!='':
            if drugbank_id in dict_node_id_to_resource:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping)
                continue
        if identifier  in dict_name_to_id:
            counter_mapping+=1
            for drugbank_id in dict_name_to_id[identifier]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping)

        else:
            print(' not in database :O')
            print(identifier)
    print('mapped:',counter_mapping)


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


    # dict node id to resource
    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all drugs from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('prepare file and write information of mapping in it')

    get_all_adrecs_target_and_map('Chemical',dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
