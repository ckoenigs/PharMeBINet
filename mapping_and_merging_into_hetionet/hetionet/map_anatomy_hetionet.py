import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def get_properties_and_generate_tsv_files_and_cypher_file():
    """
    Create TSV files for new nodes and update nodes. Prepare the additional cypher queries for the nodes and the is-a
    relationship.
    :return:
    """
    # generate csv files
    global csv_update

    file_name_mapped = 'output/update_nodes.tsv'
    update_nodes = open(file_name_mapped, 'w', encoding='utf-8')
    csv_update = csv.writer(update_nodes, delimiter='\t')
    csv_update.writerow(['id', 'resource'])

    query_start = ''' Match (a:Anatomy_hetionet{identifier:line.id})'''
    query_match = query_start + ' , (l:Anatomy{identifier:line.id}) Set l.hetionet="yes", l.resource=split(line.resource,"|") Create (l)-[:equal_anatomy_hetionet]->(a)'

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query_match = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/hetionet/{file_name_mapped}',
                                                    query_match)
    cypher_file.write(query_match)

    cypher_file.close()


# dictionary anatomy id to resource
dict_anatomy_id_to_resource = {}


def load_all_pharmebinet_anatomy_in_dictionary():
    """
    Load all existing Anatomy nodes into dictionaries
    :return:
    """
    query = '''Match (n:Anatomy) RETURN n '''
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_anatomy_id_to_resource[identifier] = set(node['resource'])

    print('size of anatomies in pharmebinet before the rest of DrugBank is added: ', len(dict_anatomy_id_to_resource))


def map_hetionet_anatomy():
    """
    Load all hetionet anatomy nodes and try to map to anatomy with the identifier
    :return:
    """

    counter = 0
    counter_mapped = 0
    query = 'Match (n:Anatomy_hetionet) Return n.identifier'
    results = g.run(query)
    for record in results:
        [node_id] = record.values()
        counter += 1

        if node_id in dict_anatomy_id_to_resource:
            counter_mapped += 1
            resource = dict_anatomy_id_to_resource[node_id]
            csv_update.writerow(
                [node_id,
                 pharmebinetutils.resource_add_and_prepare(resource, 'Hetionet')])

    print('number of nodes in uberon: ', counter)
    print('number of mapped nodes in uberon: ', counter_mapped)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path uberon')
    print(path_of_directory)
    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all properties of compound and drugbank compound and use the information to generate tsv files')

    get_properties_and_generate_tsv_files_and_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all pharmebinet anatomy in dictionary')

    load_all_pharmebinet_anatomy_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('Map anatomy nodes of hetionet')

    map_hetionet_anatomy()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
