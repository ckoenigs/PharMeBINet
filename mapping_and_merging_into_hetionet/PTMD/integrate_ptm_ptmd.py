import csv
import datetime
import os, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'PTMD_ptm_to_ptm'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['nodeId', 'identifier', 'resource', 'position', 'residue', 'type']
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/PTMD/
    query = (f' Match (n:PTMD_PTM) WHERE id(n) = toInteger(line.nodeId) MERGE (v:PTM{{identifier:line.identifier}})'
             f' Set v.ptmd="yes", v.resource=split(line.resource,"|"), v.identifier=line.identifier, '
             f'v.residue=line.residue, v.position=line.position, v.type=line.type Create (v)-[:equal_to_PTMD_ptm]->(n)')
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def load_all_PTMD_ptms_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = ("MATCH (n:PTMD_PTM)--(v:PTMD_Protein)--(p:Protein) RETURN id(n) AS nodeId, n.position, n.residue, "
             "n.type AS ptm_type, v.uniprot_accession, p.identifier")
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for nodeId, position, residue, ptm_type, uniprot_accession, identifier in results:
        if position is not None and residue is not None:
            unique_identifier = str(identifier) + "_" + str(position) + "_" + str(residue) + "_" + str(ptm_type)
            csv_mapping.writerow(
                [nodeId, unique_identifier, "PTMD", position, residue, ptm_type])
            counter_all += 1
        else:
            print(nodeId, position, residue, ptm_type)
            counter_not_mapped += 1

    print('number of all pmts:', counter_all)
    print('number of not_mapped pmts:', counter_not_mapped)


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


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
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all PTMD ptms from database')
    load_all_PTMD_ptms_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()