import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

# label definition
label='CellType'
reactome_label='CellType_reactome'



'''
create the tsv files
'''

def create_tsv_files():
    # prepare file and queries for new nodes
    file_name = 'output/map_ct.tsv'
    query = f'Match (d: {label} {{identifier: line.id_pharmebinet}}),(c:{reactome_label} {{dbId:toInteger(line.id)}}) Create (d)-[: equal_to_reactome_ct]->(c) SET d.resource = split(line.resource, "|"), d.reactome = "yes"'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/{file_name}',
                                              query)

    # cypher file
    with open('output/cypher.cypher', 'a', encoding='utf-8') as cypher_file:
        cypher_file.write(query)
    file = open(file_name, 'w')
    tsv_file = csv.writer(file, delimiter='\t')
    tsv_file.writerow(['id_pharmebinet', 'id', 'resource'])
    return tsv_file

# dictionary cell type to resource
dict_ct_to_resource={}

def go_through_co():
    """
    Go throug all cell type nodes and write information into dictionary
    :return:
    """
    query = '''Match (n:%s) Return n.identifier, n.resource''' % (label)
    results = g.run(query)
    for identifier, resource, in results:
        dict_ct_to_resource[identifier] = resource

def load_and_map_reactome_cell_type():
    """
    Load reactome ct from CL data source and map to CT of Pharmebinet with CL identifier
    :return:
    """
    tsv_mapping_file= create_tsv_files()
    query = f'''Match (n:{reactome_label})  Where n.databaseName='CL'  Return n.identifier, n.dbId'''
    for identifier, dbId, in g.run(query):
        with_string_identifier='CL:'+identifier
        if with_string_identifier in dict_ct_to_resource:
            tsv_mapping_file.writerow([with_string_identifier, dbId, pharmebinetutils.resource_add_and_prepare(dict_ct_to_resource[with_string_identifier],'Reactome')])


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('go through all cos in dictionary')

    go_through_co()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('map to pharmebinet')

    load_and_map_reactome_cell_type()


    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
