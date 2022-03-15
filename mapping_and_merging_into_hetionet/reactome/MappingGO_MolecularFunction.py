from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
'''
create connection to neo4j
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet gomolfunc with identifier as key and value the name
dict_gomolfunc_hetionet_identifier = {}

# dictionary with hetionet gomolfunc with identifier as key and value the xrefs
dict_gomolfunc_hetionet_identifier_xrefs = {}

# dictionary with hetionet gomolfunc with name as key and value the identifier
dict_gomolfunc_hetionet_alt_ids = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

#dictionary from gomolfuncId_id to resource
dict_gomolfunc_to_resource = {}

'''
load in all gomolfunc from hetionet in a dictionary
'''


def load_hetionet_gomolfunc_in():
    query = '''MATCH (n:MolecularFunction) RETURN n.identifier, n.alternative_ids, n.resource'''
    # query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    results = graph_database.run(query)

    #
    for identifier,  alt_ids, resource, in results:
        dict_gomolfunc_to_resource[identifier] = resource
        identifier = identifier.replace("GO:", "")
        dict_gomolfunc_hetionet_identifier[identifier] = 1
        if alt_ids:
            for alt_id in alt_ids:
                dict_gomolfunc_hetionet_alt_ids[alt_id.replace("GO:","")] = identifier

    print('number of gomolfunc nodes in hetionet:' + str(len(dict_gomolfunc_hetionet_identifier)))


# file for mapped or not mapped identifier
file_not_mapped_gomolfunc = open('gomolfunc/not_mapped_gomolfunc.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_gomolfunc, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id'])

file_mapped_gomolfunc = open('gomolfunc/mapped_gomolfunc.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_gomolfunc, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_hetionet', 'resource'])

'''
load all reactome gomolfunc and check if they are in hetionet or not
'''


def load_reactome_gomolfunc_in():
    query = '''MATCH (n:GO_MolecularFunction_reactome) RETURN n'''
    results = graph_database.run(query)

    counter_map_with_id = 0
    for gomolfunc_node, in results:
        gomolfunc_id = gomolfunc_node['accession']
        resource = gomolfunc_node['resource']

        # check if the reactome pathway id is part in the hetionet idOwn
        if gomolfunc_id in dict_gomolfunc_hetionet_identifier:
            counter_map_with_id += 1
            resource = set(dict_gomolfunc_to_resource["GO:" + gomolfunc_id])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            csv_mapped.writerow([gomolfunc_id, "GO:" + gomolfunc_id, resource])
        elif gomolfunc_id in dict_gomolfunc_hetionet_alt_ids:
            real_go_identifier = "GO:" + dict_gomolfunc_hetionet_alt_ids[gomolfunc_id]
            resource = set(dict_gomolfunc_to_resource[real_go_identifier])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            csv_mapped.writerow([gomolfunc_id, real_go_identifier, resource])
        else:
            csv_not_mapped.writerow([gomolfunc_id, resource])

    print('number of mapping with id:' + str(counter_map_with_id))


'''
generate connection between mapping gomolfunc of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/gomolfunc/mapped_gomolfunc.tsv" As line FIELDTERMINATOR "\\t"
     Match (d: MolecularFunction {identifier: line.id_hetionet}),(c:GO_MolecularFunction_reactome{accession:line.id}) Create (d)-[:equal_to_reactome_gomolfunc]->(c)  SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query = query %(path_of_directory)
    cypher_file.write(query)
    # cypher_file.write(':begin\n')
    # query = '''Match (d:MolecularFunction) Where not  exists(d.reactome) Set d.reactome="no";\n '''
    # cypher_file.write(query)
    # cypher_file.write(':commit')


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
    print('Load all MolecularFunction from hetionet into a dictionary')

    load_hetionet_gomolfunc_in()

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

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
