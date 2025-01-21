import datetime
import os
import sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary ptm id to resource
dict_identifier_to_resource = {}

# dictionary ptm name to identifier
dict_protein_name_to_identifier = {}

def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

def load_ptms_from_database_and_add_to_dict():
    """
    Load all Proteins from pharmebinet and add them into a dictionary
    """
    query = "MATCH (n:PTM) RETURN n.identifier, n.resource"
    results = g.run(query)

    for identifier, resource in results:
        dict_identifier_to_resource[identifier] = resource
        #name = name.lower()
        #pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_to_identifier, name, identifier)
    #print(identifier)

def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'iPTMnet_ptms_to_PTM'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['nodeId', 'ptm_identifier', 'resource', 'mapping_method', 'score']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping_existing = csv.writer(file, delimiter='\t')
    csv_mapping_existing.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    new_file_name = 'new_PTMs'
    new_file_path = os.path.join(path_of_directory, new_file_name) + '.tsv'
    new_file = open(new_file_path, 'w+', encoding='utf-8')
    csv_mapping_new = csv.writer(new_file, delimiter='\t')
    csv_mapping_new.writerow(['nodeId','identifier', 'resource', 'score', 'type', 'residue', 'position', 'protein_id'])

    if not os.path.exists(source):
        os.mkdir(source)


    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/iPTMnet/
    query = f' Match (n:iPTMnet_PTM), (v:PTM{{identifier:line.ptm_identifier}}) WHERE id(n) = toInteger(line.nodeId) Set v.iptmnet="yes", v.resource=split(line.resource,"|"), v.score=line.score Create (v)-[:equal_to_iPTMnet_ptm{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    # overwrite exiting queries
    cypher_file = open(cypher_file_path, 'w', encoding='utf-8')
    cypher_file.write(query)

    query = f' Match (n:iPTMnet_PTM) WHERE id(n) = toInteger(line.nodeId) MERGE (v:PTM{{identifier:line.identifier}}) On Create Set v.iptmnet="yes", v.url="https://research.bioinformatics.udel.edu/iptmnet/entry/"+ line.protein_id, v.license="CC BY-NC-SA 4.0 Deed", v.source="iPTMnet", v.resource=split(line.resource,"|"), v.residue=line.residue, v.position=line.position, v.type=line.type, v.score=line.score Create (v)-[:equal_to_iPTMnet_ptm]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, new_file_name + '.tsv', query)
    # append second query
    cypher_file = open(cypher_file_path, 'a', encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping_existing, csv_mapping_new


def load_all_iptmnet_ptms_and_finish_the_files(csv_mapping_existing, csv_mapping_new):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = ("MATCH (n:iPTMnet_PTM)--(v:iPTMnet_Protein)--(p:Protein) RETURN Distinct id(n) AS nodeId, n.score,"
             "n.position, n.residue, n.type AS ptm_type, p.identifier")
    results = g.run(query)
    counter_not_mapped = 0
    counter_mapped = 0
    counter_all = 0
    for nodeId, score, position, residue, ptm_type, protein_id in results:
        counter_all += 1
        identifier = f"{protein_id}_{position}_{residue}_{ptm_type}"
        # mapping
        if identifier in dict_identifier_to_resource:
            csv_mapping_existing.writerow(
                [nodeId, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier], "iPTMnet"),
                 'ptm_identifier', score])
            counter_mapped += 1
        else:
            csv_mapping_new.writerow([
                nodeId, identifier, "iPTMnet", score, ptm_type, residue, position, protein_id
            ])
            counter_not_mapped += 1
            print(identifier)

    print('number of new ptms:', counter_not_mapped)
    print('number of all ptms:', counter_all)




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
    path_of_directory = os.path.join(home, 'ptm/')

    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all PTMs from database')
    load_ptms_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping_existing, csv_mapping_new = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all iPTMnet ptms from database')
    load_all_iptmnet_ptms_and_finish_the_files(csv_mapping_existing, csv_mapping_new)

    driver.close()

if __name__ == "__main__":
    main()
