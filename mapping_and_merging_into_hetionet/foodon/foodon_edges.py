import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

license='CC BY 4.0'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


def create_cypher_file(file_name, node_label, rela_name, to_CT):
    '''
    generate new relationships between pathways of pharmebinet and pharmebinet nodes that mapped to reactome
    '''
    if to_CT:
        rela= pharmebinetutils.prepare_rela_great(rela_name, node_label, 'Food')
        query = ''' MATCH (d:Food{identifier:line.node_id}),(c:%s{identifier:line.other_id}) CREATE (d)<-[: %s{resource: ['FoodOn'], foodon: "yes", source:"FoodOn", license:"%s", url:"https://www.ebi.ac.uk/ols4/ontologies/foodon/classes?obo_id="+line.node_id}]-(c)'''
    else:
        rela= pharmebinetutils.prepare_rela_great(rela_name, 'Food', node_label)
        query = ''' MATCH (d:Food{identifier:line.node_id}),(c:%s{identifier:line.other_id}) CREATE (d)-[: %s{resource: ['FoodOn'], foodon: "yes", source:"FoodOn", license:"%s", url:"https://www.ebi.ac.uk/ols4/ontologies/foodon/classes?obo_id="+line.node_id}]->(c)'''
    query = query % (node_label, rela, license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/foodon/{file_name}',
                                              query)
    cypher_file.write(query)

def create_tsv_file_and_cypher_query(label, rela_type, to_CT):
    """
    create tsv file and create cypher query
    :param label:
    :param rela_type:
    :param to_CT:
    :return:
    """
    file_name=f'edges/{label}_{rela_type}_{to_CT}.tsv'
    file= open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['node_id','other_id'])
    create_cypher_file(file_name, label, rela_type, to_CT)
    
    return csv_writer


def load_all_pair_and_add_to_files(label,equal_type):
    """
    Load for a given label all edges in both direction and write them into tsv files and generate cypher queries.
    :param label: 
    :return: 
    """

    for [direction_one, direction_two, to_cT] in [['','>',False], ['<','',True]]:
        dict_type_direction_to_tsv = {}
        query = f'''MATCH (p:Food)-[:equal_to_FO]-(r){direction_one}-[v]-{direction_two}(n)-[:{equal_type}]-(b:{label}) RETURN p.identifier, b.identifier, type(v)'''
        results = graph_database.run(query)
        counter=0
        set_edge_types=set()
        for record in results:
            counter+=1
            [celltype_id, node_id, rela_type] = record.values()
            if (label, rela_type, to_cT) not in dict_type_direction_to_tsv:
                set_edge_types.add(rela_type)
                # print(label, rela_type, to_cT)
                csv_writer=create_tsv_file_and_cypher_query(label, rela_type, to_cT)
                dict_type_direction_to_tsv[(label, rela_type, to_cT)] = csv_writer
            dict_type_direction_to_tsv[(label, rela_type, to_cT)].writerow([celltype_id, node_id])
        print(label, counter, ', '.join(set_edge_types))




def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path CL pathway edges')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')


    cypher_file = open('output/cypher_edge.cypher', 'a', encoding="utf-8")
    list_label_edge_type=[['Anatomy','equal_anatomy_fo']]

    for [label, equal_type] in list_label_edge_type:
        load_all_pair_and_add_to_files(label, equal_type)
    cypher_file.close()
    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
