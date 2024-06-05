import csv
import datetime
import os
import re
from collections import defaultdict

import pharmebinetutils
import create_connection_to_database_metabolite


# dictionary variant id to resource
dict_variant_id_to_resource = {}

# dictionary from gene id to gene id
dict_snp_id_to_identifier = defaultdict(str)

dbsnp_identifier_map = {}

def load_variants_from_database_and_add_to_dict():


    # Define the Cypher query to fetch dbSNP IDs and identifiers
    cypher_query = (
        "MATCH (n:Variant) UNWIND n.xrefs AS xref WITH n, xref WHERE xref CONTAINS 'dbSNP:' RETURN n.identifier AS identifier, xref AS dbsnp_id, n.resource AS resource" )
    results = g.run(cypher_query)
    for record in results:
        identifier = record['identifier']
        resource = record["resource"]
        dict_variant_id_to_resource[identifier] = resource
        dbsnp_id = record["dbsnp_id"].split(":")[1]  # Extract dbSNP ID
        dbsnp_identifier_map[dbsnp_id] = identifier



def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'MarkerDB_variant_to_Variant'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['MarkerDB_variant_id', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/MarkerDB/
    query = (f' Match (n:MarkerDB_SequenceVariant{{id:toInteger(line.MarkerDB_variant_id)}}), (v:Variant{{'
             f'identifier:line.identifier}}) Set v.markerdb="yes", v.resource=split(line.resource,"|") Create (v)-['
             f':equal_to_MarkerDB_variant{{mapped_with:line.mapping_method}}]->(n)')
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping

def load_all_MarkerDB_variants_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "Match (n:MarkerDB_SequenceVariant) Where n.variation contains 'rs' Return n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    pattern = r'rs\d+'
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['variation']
        match = re.search(pattern, identifier)
        rs_id = match.group()
        unique_id = node['id']
        # mapping
        #if rs_id == "rs368270856":
            #print(rs_id, dict_variant_id_to_resource[rs_id])
        if rs_id in dbsnp_identifier_map:
            variant_id = dbsnp_identifier_map[rs_id]
            csv_mapping.writerow(
                [unique_id, variant_id,
                 pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[variant_id], "MarkerDB"),
                 'external_references'])
        else:
            counter_not_mapped += 1
            print(identifier)

    print('number of not-mapped variants:', counter_not_mapped)
    print('number of all variants:', counter_all)

def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_database_metabolite.database_connection_neo4j_driver()
    g = driver.session(database='graph')

def main():
    global path_of_directory
    global source
    global home

    path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test"
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'variant/')


    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Variants from database')
    load_variants_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all MarkerDB variants from database')
    load_all_MarkerDB_variants_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()
