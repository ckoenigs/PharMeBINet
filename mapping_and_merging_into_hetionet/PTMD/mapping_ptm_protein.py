import datetime
import os
import sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def get_PTMD_information(edge_type):
    '''
    Load all PTMD ptm-protein and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)
    columns = ['ptm_id', 'protein_id']

    # Create tsv for ptm-protein edges
    file_name_not_mapped_protein = f'new_ptm_protein_edges_{edge_type}.tsv'
    not_mapped_path_protein = os.path.join(path_of_directory, file_name_not_mapped_protein)
    mode = 'w' if os.path.exists(not_mapped_path_protein) else 'w+'
    file_protein = open(not_mapped_path_protein, mode, encoding='utf-8')
    writer_protein = csv.writer(file_protein, delimiter='\t')
    writer_protein.writerow(columns)

    counter_protein = 0
    counter_not_mapped = 0
    counter_all = 0
    dict_all_mappings = {}

    query = ("Match (n:PTM)--(p:PTMD_PTM)-[r]-(:PTMD_Protein)--(m:Protein) WHERE type(r) = $edge_type Return n.identifier, m.identifier")
    results = g.run(query, parameters={"edge_type": edge_type})

    for record in results:
        [ptm_id, protein_id] = record.values()
        counter_all += 1

        # mapping of new edges
        if (ptm_id, protein_id) not in dict_all_mappings:
            dict_all_mappings[(ptm_id, protein_id)] = "Protein"
            writer_protein.writerow(
                [ptm_id, protein_id])
            counter_protein += 1

        # when edge is already integrated
        else:
            print("Already mapped edge:", ptm_id, protein_id, dict_all_mappings[(ptm_id, protein_id)])
            counter_not_mapped += 1
    file_protein.close()

    print('Edge: ', edge_type)
    print('number of protein edges:', counter_protein)
    print('number of not mapped edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    file_cypher = open(cypher_path, 'a', encoding='utf-8')

    # Create new edges, write cypher queries
    query = ''
    if edge_type == 'PTMD_HAS_PTM':
        query = (f' Match (p:PTM{{identifier:line.ptm_id}}), (d:Protein{{identifier:line.protein_id}}) '
                 f'Create (d)-[:HAS_PhPTM{{resource:["PTMD"],ptmd:"yes", url:"https://ptmd.biocuckoo.cn/index.php",  source:"PTMD", license:"ONLY freely available for academic research"}}]->(p)')
    elif edge_type == 'PTMD_INVOLVES':
        query = (f' Match (p:PTM{{identifier:line.ptm_id}}), (d:Protein{{identifier:line.protein_id}}) '
             f'Create (p)-[:INVOLVES{{resource:["PTMD"],ptmd:"yes", url:"https://ptmd.biocuckoo.cn/index.php",  source:"PTMD", license:"ONLY freely available for academic research"}}]->(d)')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped_protein,
                                              query)
    file_cypher.write(query)
    file_cypher.close()


######### MAIN #########
def main():
    global path_of_directory
    global source
    global home

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'ptm_protein_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')
    print('gather all information of the PTMD ptms/protein')

    get_PTMD_information("PTMD_HAS_PTM")
    get_PTMD_information("PTMD_INVOLVES")

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    main()
