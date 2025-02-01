import datetime
import os
import sys
import csv
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary ptm id to resource
dict_identifier_to_resource_pubmeds = {}


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
    query = "MATCH (n:PTM)-[r:HAS_PhPTM]-(p:Protein) RETURN n.identifier, r.resource, p.identifier, r.pubMed_ids "
    results = g.run(query)

    for ptm_identifier, resource, protein_identifer, pubMed_ids in results:
        pubMed_ids = set(pubMed_ids) if pubMed_ids else set()
        dict_identifier_to_resource_pubmeds[(ptm_identifier, protein_identifer)] = [resource, pubMed_ids]


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'qPTM_edges_to_edges'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['ptm_identifier', 'protein_identifer', 'resource', 'aggregated_properties', 'pmids']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping_existing = csv.writer(file, delimiter='\t')
    csv_mapping_existing.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    new_file_name = 'new_edges'
    new_file_path = os.path.join(path_of_directory, new_file_name) + '.tsv'
    new_file = open(new_file_path, 'w+', encoding='utf-8')
    csv_mapping_new = csv.writer(new_file, delimiter='\t')
    csv_mapping_new.writerow(['ptm_identifier', 'protein_identifier', 'resource', 'aggregated_properties', 'pmids'])

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher_edge.cypher')
    query = (f' MATCH (n:Protein {{identifier: line.protein_identifer}}), (v:PTM {{identifier: line.ptm_identifier}}) '
             f'MATCH (n)-[r:HAS_PhPTM]->(v) SET r.qptm = "yes", '
             f'r.resource = split(line.resource, "|"), r.properties_qptm = line.aggregated_properties, r.pubMed_ids =split(line.pmids,"|")')
    mode = 'w' if os.path.exists(file_path) else 'w+'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    query = ('MATCH (n:Protein {identifier: line.protein_identifier}), (v:PTM {identifier: line.ptm_identifier}) '
             'CREATE (n)-[:HAS_PhPTM {qptm : "yes", url:"https://qptm.omicsbio.info/", license:"ONLY freely available for academic research", '
             'resource : split(line.resource, "|"), source:"qPTM", properties_qptm : line.aggregated_properties, pubMed_ids :split(line.pmids,"|")}]->(v)')

    query = pharmebinetutils.get_query_import(path_of_directory, new_file_name + '.tsv', query)
    cypher_file.write(query)

    return csv_mapping_existing, csv_mapping_new


def load_all_qptm_ptms_and_finish_the_files(batch_size, csv_mapping_existing, csv_mapping_new):
    """
    Load all variation, sort the ids into the right tsv, generate the queries, and add relationships to the rela tsv.
    """

    counter_new_edges = 0
    counter_mapped = 0
    all_edges_qptm = {}

    counter = 1
    counter_total = 0

    # iterate over entries in batches and collect edges
    skip = 0
    while counter > 0:

        query = f"""
            MATCH (ptm:PTM)-[:equal_to_qPTM_ptm]-(n)-[r:qPTM_HAS_PTM]-(v)-[:equal_to_qPTM_protein]-(p:Protein) 
            WITH ptm, collect(r) as edge, p SKIP {skip} Limit {batch_size}
            RETURN p.identifier as protein_identifier, ptm.identifier as ptm_identifier, edge
            """
        print(query)

        results = g.run(query)

        counter = 0
        # condition, reliability, pmid, sample
        for protein_identifier, ptm_identifier, edge_info in results:
            counter += 1
            edge = (ptm_identifier, protein_identifier)
            clean = []
            pubmed_ids = set()
            for prop in edge_info:
                if 'pmid' in prop:
                    pubmed_ids.add(str(prop['pmid']))  # If it's a single value, convert it to a list
                if len(prop) > 0:
                    clean.append(json.dumps(dict(prop)))

            # Existing edge
            if edge in dict_identifier_to_resource_pubmeds:
                pubmed_ids = pubmed_ids.union(dict_identifier_to_resource_pubmeds[edge][1])
                csv_mapping_existing.writerow([
                    ptm_identifier, protein_identifier,
                    pharmebinetutils.resource_add_and_prepare(
                        dict_identifier_to_resource_pubmeds[edge][0], "qPTM"
                    ), "|".join(clean), "|".join(pubmed_ids)
                ])
                counter_mapped += 1
            else:
                # New edge
                csv_mapping_new.writerow(
                    [ptm_identifier, protein_identifier, "qPTM", "|".join(clean), "|".join(pubmed_ids)])
                counter_new_edges += 1

        skip += batch_size
        counter_total += counter
        if counter_total % 10000 == 0:
            print(counter_total, datetime.datetime.now())
    print("Finished edge_dictionary")

    print(f'Number of new ptm_protein edges: {counter_new_edges}')
    print(f'Number of extended ptm_protein edges: {counter_mapped}')


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
    print('Load all qPTM ptms from database')
    load_all_qptm_ptms_and_finish_the_files(10000, csv_mapping_existing, csv_mapping_new)

    driver.close()


if __name__ == "__main__":
    main()
