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


def get_iptmnet_information():
    '''
    Load all iPTMnet ptm-protein and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)
    columns = ['ptm_id','protein_id','relationshipId','pmids','ptm_source','note']

    # Create tsv for ptm-protein edges
    file_name_not_mapped_protein = 'new_ptm_protein_edges.tsv'
    not_mapped_path_protein = os.path.join(path_of_directory, file_name_not_mapped_protein)
    mode = 'w' if os.path.exists(not_mapped_path_protein) else 'w+'
    file_protein = open(not_mapped_path_protein, mode, encoding='utf-8')
    writer_protein = csv.writer(file_protein, delimiter='\t')
    writer_protein.writerow(columns)

    counter_protein = 0
    counter_not_mapped = 0
    counter_all = 0
    all_edges = []
    dict_all_mappings = {}

    query = ("Match (n:PTM)--(p:iPTMnet_PTM)-[r]-(:iPTMnet_Protein)--(m:Protein) Return n.identifier as ptm_id, "
             "m.identifier as protein_id, id(r) AS relationshipId, r.pmids as pmids, r.source as ptm_source, r.note as note")
    results = g.run(query)

    for record in results:
       # [ptm_id, protein_id, relationshipId, pmids, source, note] = record.values()
        ptm_id = record.get("ptm_id")
        protein_id = record.get("protein_id")
        relationshipId = record.get("relationshipId")
        pmids = record.get("pmids", None)
        ptm_source = record.get("ptm_source", None)
        note = record.get("note", None)
        counter_all += 1

        # mapping of new edges
        if relationshipId not in all_edges:
            #dict_all_mappings[(ptm_id, protein_id)] = "Protein"
            all_edges.append(relationshipId)
            writer_protein.writerow(
                [ptm_id, protein_id, relationshipId, pmids, ptm_source, note])
            counter_protein += 1

        # when edge is already integrated
        else:
            #print("Already mapped edge:", ptm_id, protein_id, relationshipId)
            counter_not_mapped += 1
    file_protein.close()

    print('number of protein edges:', counter_protein)
    print('number of not mapped edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w'
    file_cypher = open(cypher_path, mode, encoding='utf-8')

    # Create new edges, write cypher queries
    query = (f' Match (p:PTM{{identifier:line.ptm_id}}), (d:Protein{{identifier:line.protein_id}}) MERGE ('
             f'p)-[:HAS_PhPTM{{resource:["iPTMnet"],iptmnet:"yes",pmids:line.pmids, source:line.ptm_source,'
             f' note:line.note}}]->(d)')
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
    print('gather all information of the iPTMnet ptms/protein')

    get_iptmnet_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    main()
