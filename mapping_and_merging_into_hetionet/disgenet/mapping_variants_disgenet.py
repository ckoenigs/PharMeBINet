import datetime
import sys
import os
import csv

sys.path.append("../..")
import create_connection_to_databases
from collections import defaultdict
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dict for alternative_ids
# dict_snp_id_to_identifier = set()

# dictionary variant id to resource
dict_variant_id_to_resource = {}


def load_variants_from_database_and_add_to_dict():
    '''
    Load all variants from Graph-DB and add them into a dictionary
    '''
    query = "MATCH (n:Variant) WHERE any(x in n.xrefs WHERE x =~ 'dbSNP:.*') RETURN n.identifier, n.resource, n.xrefs"
    results = g.run(query)

    for identifier, resource, xrefs, in results:
        dict_variant_id_to_resource[identifier] = resource

        # find index of xrefs "snp_id" entry
        # snp_id_idx = [i for i, item in enumerate(xrefs) if item.startswith('dbSNP:')]
        #
        # _, snp_id = xrefs[snp_id_idx[0]].split(':')
        # put snp_id as identifier if 'dbSNP' exists in xrefs
        # dict_snp_id_to_identifier.add(identifier)
        # dict_snp_id_to_identifier[identifier] = identifier


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'DisGeNet_variant_to_Variant'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['DisGeNet_snp_id', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f'Match (n:variant_DisGeNet{{snpId:line.DisGeNet_snp_id}}), (v:Variant{{identifier:line.identifier}}) Set v.disgenet="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DisGeNet_variant{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name + '.tsv',
                                              query)
    cypher_file.write(query)
    query = f' Match (n:variant_DisGeNet{{snpId:line.identifier}}) Create (p:Variant :GeneVariant{{identifier:n.snpId, chromosome:n.chromosome, position:n.position, resource:["DisGeNet"], xrefs:["dbSNP:"+n.snpId], disgenet:"yes", source:"dbSNP from DisGeNet" }}) Create (p)-[:equal_to_DisGeNet_variant{{mapped_with:"new"}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              'not_mapped.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


def load_all_DisGeNet_variants_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:variant_DisGeNet) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0

    not_mapped_path = os.path.join(path_of_directory, 'not_mapped.tsv')
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['identifier'])

    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['snpId']
        # mapping
        if identifier in dict_variant_id_to_resource:
            # variant_id = dict_snp_id_to_identifier[identifier]
            csv_mapping.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[identifier], "DisGeNet"),
                 'external_references'])
        else:
            counter_not_mapped += 1
            # print(identifier)
            writer.writerow([identifier])
    file.close()
    print('number of not-mapped variants:', counter_not_mapped)
    print('number of all variants:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet protein')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/disgenet')
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
    print('Load all DisGeNet variants from database')
    load_all_DisGeNet_variants_and_finish_the_files(csv_mapping)

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
