import datetime
import csv
from collections import defaultdict
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''

def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


pc_pair_dict = defaultdict(set)
pc_atc_pair_dict = defaultdict(set)

atc_pair_from_dict = defaultdict()
atc_pc_from_dict = defaultdict()
pc_atc_to_dict = defaultdict()

updateEdge = []
createEdge = []


def load_atc_in():
    query = '''MATCH (n:DC_ATC)-[r:DC_HAS_PARENT]->(m:DC_ATC) RETURN id(n),id(m) '''
    results = graph_database.run(query)


    for record in results:
        node_1_id = record.data()['id(n)']
        node_2_id = record.data()['id(m)']

        atc_pair_from_dict[node_1_id] = node_2_id



def load_pc_atc_connection():
    query = '''MATCH (n:PharmacologicClass)-[r:equal_to_atc_drugcentral]->(m:DC_ATC) RETURN id(n), id(m) '''
    results = graph_database.run(query)

    for record in results:
        node_pc_id = record.data()['id(n)']
        node_atc_id = record.data()['id(m)']

        pc_atc_pair_dict[node_pc_id].add(node_atc_id)
        pair = (node_pc_id, node_atc_id)

        pc_atc_to_dict[node_pc_id] = node_atc_id
        atc_pc_from_dict[node_atc_id] = node_pc_id



def load_pharmacological_class_in():
    query = '''MATCH (n:PharmacologicClass)-[r:BELONGS_TO_PCbtPC]->(m:PharmacologicClass) RETURN id(n),id(m), r.resource'''
    results = graph_database.run(query)

    for record in results:
        node_1_id = record.data()['id(n)']
        node_2_id = record.data()['id(m)']

        resource = set(record.data()['r.resource'])

        pair = (node_1_id, node_2_id)
        pc_pair_dict[pair] = resource

    # edge mapping
    for pc_pair in pc_pair_dict:
        start_node = pc_pair[0]
        if start_node in pc_atc_to_dict:
            atc_node_1 = pc_atc_to_dict[start_node]
            atc_node_2 = atc_pair_from_dict[atc_node_1]
            if atc_node_2 in atc_pc_from_dict:
                pc_node = atc_pc_from_dict[atc_node_2]
                endPair = (start_node, pc_node)
                if endPair not in pc_pair_dict:
                    print('*******')
                    createEdge.append(endPair)
                else:
                    updateEdge.append(endPair)

    # save mappings in csv files
    for pair in createEdge:
        resource = set(pc_pair_dict[pair])
        resource.add('DrugCentral')
        resource = '|'.join(resource)
        csv_createEdge.writerow([pair[0], pair[1], resource])

    for pair in updateEdge:
        resource = set(pc_pair_dict[pair])
        resource.add('DrugCentral')
        resource = '|'.join(resource)
        csv_updateEdge.writerow([pair[0], pair[1], resource])


file_updateEdge = open('atc/update_edge.tsv', 'w', encoding="utf-8")
csv_updateEdge = csv.writer(file_updateEdge,delimiter='\t', lineterminator='\n')
csv_updateEdge.writerow(['node_1_id','node_2_id', 'resource'])

file_createEdge = open('atc/create_edge.tsv', 'w', encoding="utf-8")
csv_createEdge = csv.writer(file_createEdge,delimiter='\t', lineterminator='\n')
csv_createEdge.writerow(['node_1_id','node_2_id', 'resource'])



def generate_cyper_file(file_namePharma, file_nameCompound):
    cypher_file = open('output/cypher_edge.cypher', 'w')

    query_update = '''MATCH (n:DC_ATC), (c:PharmacologicClass{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_atc_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query_update = pharmebinetutils.get_query_import(path_of_directory, file_namePharma, query_update)
    cypher_file.write(query_update)


    query_create = '''MATCH (n:DC_ATC), (c:Compound{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_atc_drugcentral{how_mapped:line.how_mapped}]->(n);'''
    query_create = pharmebinetutils.get_query_import(path_of_directory, file_nameCompound, query_create)
    cypher_file.write(query_create)

    cypher_file.close()



def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral atc edge')
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')
    create_connection_with_neo4j()

    print("load atc in")
    load_atc_in()
    print("load pc to atc connection")
    load_pc_atc_connection()
    print("load pharmacological Class in")
    load_pharmacological_class_in()


    print(
        '###########################################################################################################################')


    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()