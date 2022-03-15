from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()



def load_pathway_node_edge_info(csv_file, dict_pathway_node_to_rela_info,
                                                  node_smpdb_label, node_pharmebinet_label):
    """
    Load all pairs and relationship information from Pathway over smpdb to protein/metabolite and write information into file
    :param csv_file: csv writer
    :param dict_pathway_node_to_rela_info: dictionary
    :param node_smpdb_label: string
    :param node_pharmebinet_label: string
    :return: 
    """
    query = '''MATCH (p:Pathway)-[]-(r:pathway_smpdb)-[v]-(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v, r.smpdb_id'''
    query = query % ( node_smpdb_label, node_pharmebinet_label)
    print(query)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for pathway_id, node_id, edge, smpdb_pathway_id,   in results:
        if (pathway_id, node_id) in dict_pathway_node_to_rela_info:
            print(pathway_id, node_id)
            # sys.exit("Doppeltepathway-edge Kombination")
            continue
        dict_pathway_node_to_rela_info[(pathway_id, node_id)] = edge
        csv_file.writerow([pathway_id, node_id, smpdb_pathway_id])
    print('number of pathway-'+node_smpdb_label+' relationships in hetionet:' + str(
        len(dict_pathway_node_to_rela_info)))


'''
generate new relationships between pathways and nodes that have edges in smpdb 
'''


def create_cypher_file( file_path, node_label, rela_name):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/smpdb/%s" As line FIELDTERMINATOR "\\t" MATCH (d:Pathway{identifier:line.pathway_id}),(c:%s{identifier:line.node_id}) CREATE (d)-[: %s{ resource: ['SMPDB'], smpdb: "yes", license:"SMPDB is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (SMPDB) and the original publication", url:"https://smpdb.ca/view/"+line.smpdb_pathway_id, source:"SMPDB"}]->(c);\n'''
    query = query % (path_of_directory, file_path, node_label, rela_name)
    cypher_file.write(query)


def check_relationships_and_generate_file( node_smpdb_label, node_pharmebinet_label,
                                          directory, rela_name):
    """prepare different edges"""

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from pathway-node and hetionet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name= directory + '/edge_pathway_to_'+node_smpdb_label+'_'+rela_name+'.tsv'

    file_edge_pathway_to_node = open(file_name,'w', encoding="utf-8")
    csv_edge = csv.writer(file_edge_pathway_to_node, delimiter='\t', lineterminator='\n')
    csv_edge.writerow(['pathway_id', 'node_id','smpdb_pathway_id'])

    dict_pathway_node = {}

    load_pathway_node_edge_info(csv_edge, dict_pathway_node, node_smpdb_label, node_pharmebinet_label)


    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file( file_name, node_pharmebinet_label, rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path smpdb pathway_edge')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: smpdb label           1: label in database        2: relationship to create
    list_of_combinations = [
        ['metabolite_smpdb', 'Metabolite', 'ASSOCIATES_PWaM'],
        ['protein_smpdb', 'Protein', 'ASSOCIATES_PWaP'],
    ]

    directory = 'edge_pathways'
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding="utf-8")

    for list_element in list_of_combinations:
        smpdb_label = list_element[0]
        node_label = list_element[1]
        relationship_name = list_element[2]
        check_relationships_and_generate_file(smpdb_label, node_label, directory, relationship_name)
    cypher_file.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
