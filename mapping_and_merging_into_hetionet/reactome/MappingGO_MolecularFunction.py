from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary with pharmebinet gomolfunc with identifier as key and value the name
dict_gomolfunc_pharmebinet_identifier = {}

# dictionary with pharmebinet gomolfunc with identifier as key and value the xrefs
dict_gomolfunc_pharmebinet_identifier_xrefs = {}

# dictionary with pharmebinet gomolfunc with name as key and value the identifier
dict_gomolfunc_pharmebinet_alt_ids = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary from gomolfuncId_id to resource
dict_gomolfunc_to_resource = {}

'''
load in all gomolfunc from pharmebinet in a dictionary
'''


def load_pharmebinet_gomolfunc_in():
    query = '''MATCH (n:MolecularFunction) RETURN n.identifier, n.alternative_ids, n.resource'''
    # query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    results = graph_database.run(query)

    #
    for record in results:
        [identifier, alt_ids, resource] = record.values()
        dict_gomolfunc_to_resource[identifier] = resource
        identifier = identifier.replace("GO:", "")
        dict_gomolfunc_pharmebinet_identifier[identifier] = 1
        if alt_ids:
            for alt_id in alt_ids:
                dict_gomolfunc_pharmebinet_alt_ids[alt_id.replace("GO:", "")] = identifier

    print('number of gomolfunc nodes in pharmebinet:' + str(len(dict_gomolfunc_pharmebinet_identifier)))


# file for mapped or not mapped identifier
file_not_mapped_gomolfunc = open('gomolfunc/not_mapped_gomolfunc.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_gomolfunc, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id'])

file_mapped_gomolfunc = open('gomolfunc/mapped_gomolfunc.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_gomolfunc, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_pharmebinet', 'resource'])

'''
load all reactome gomolfunc and check if they are in pharmebinet or not
'''


def load_reactome_gomolfunc_in():
    query = '''MATCH (n:GO_MolecularFunction_reactome) RETURN n'''
    results = graph_database.run(query)

    counter_map_with_id = 0
    for gomolfunc_node in results:
        gomolfunc_node = gomolfunc_node.data()['n']
        gomolfunc_id = gomolfunc_node['accession']

        # check if the reactome pathway id is part in the pharmebinet idOwn
        if gomolfunc_id in dict_gomolfunc_pharmebinet_identifier:
            counter_map_with_id += 1
            csv_mapped.writerow([gomolfunc_id, "GO:" + gomolfunc_id, pharmebinetutils.resource_add_and_prepare(
                dict_gomolfunc_to_resource["GO:" + gomolfunc_id], 'Reactome')])
        elif gomolfunc_id in dict_gomolfunc_pharmebinet_alt_ids:
            real_go_identifier = "GO:" + dict_gomolfunc_pharmebinet_alt_ids[gomolfunc_id]
            csv_mapped.writerow([gomolfunc_id, real_go_identifier, pharmebinetutils.resource_add_and_prepare(
                dict_gomolfunc_to_resource[real_go_identifier], 'Reactome')])
        else:
            csv_not_mapped.writerow([gomolfunc_id])

    print('number of mapping with id:' + str(counter_map_with_id))


'''
generate connection between mapping gomolfunc of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    query = '''Match (d: MolecularFunction {identifier: line.id_pharmebinet}),(c:GO_MolecularFunction_reactome{accession:line.id}) Create (d)-[:equal_to_reactome_gomolfunc]->(c)  SET d.resource = split(line.resource, '|'), d.reactome = "yes"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/gomolfunc/mapped_gomolfunc.tsv',
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome mf')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all MolecularFunction from pharmebinet into a dictionary')

    load_pharmebinet_gomolfunc_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all reactome GO_MolecularFunction from neo4j into a dictionary')

    load_reactome_gomolfunc_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate new GO_MolecularFunction and connect them to reactome ')

    create_cypher_file()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
