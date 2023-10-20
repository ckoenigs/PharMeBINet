import datetime
import os, sys
import csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary protein id to resource
dict_protein_id_to_resource = {}
# dictionary from gene symbol to protein id
dict_gene_symbol_to_id = {}
# dict for alternative_ids
dict_alternativeId_to_identifiers = defaultdict(set)


def load_protein_from_database_and_add_to_dict():
    '''
    Load all Proteins from Graph-DB and add them into a dictionary
    '''
    query = "MATCH (n:Protein) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_protein_id_to_resource[identifier] = node['resource']
        gene_symbols = node['gene_name'] if 'gene_name' in node else []
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for gene_symbol in gene_symbols:
            if gene_symbol not in dict_gene_symbol_to_id:
                dict_gene_symbol_to_id[gene_symbol] = set()
            dict_gene_symbol_to_id[gene_symbol].add(identifier)
        # create dict for alternative_ids
        for alternative_id in alternative_ids:
            # if alternative_id not in dict_alternativeId_to_identifiers:
            #     dict_alternativeId_to_identifiers[alternative_id] = set()
            dict_alternativeId_to_identifiers[alternative_id].add(identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    file_name = 'DisGeNet_protein_to_protein'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['DisGeNet_uniprot_id', 'uniprot_id', 'resource', 'mapping_method']
    csv_mapping.writerow(header)
    cypher_file = open(os.path.join(source, 'cypher.cypher'), 'w', encoding='utf-8')

    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f' Match (n:protein_DisGeNet{{UniProtKB:line.DisGeNet_uniprot_id}}), (v:Protein{{identifier:line.uniprot_id}}) Set v.disgenet="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DisGeNet_protein{{mapped_with:line.mapping_method}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name+'.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


def load_all_DisGeNet_protein_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:protein_DisGeNet) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['UniProtKB']
        # mapping
        if identifier in dict_protein_id_to_resource:
            csv_mapping.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_protein_id_to_resource[identifier], "DisGeNet"),
                 'id'])
        elif identifier in dict_alternativeId_to_identifiers:
            for uniprot_id in dict_alternativeId_to_identifiers[identifier]:
                csv_mapping.writerow([identifier, uniprot_id,
                                      pharmebinetutils.resource_add_and_prepare(dict_protein_id_to_resource[uniprot_id],
                                                                                "DisGeNet"),
                                      'alternative_id'])
        else:
            counter_not_mapped += 1
            print(identifier)
    print('number of not-mapped proteins:', counter_not_mapped)
    print('number of all proteins:', counter_all)


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
    path_of_directory = os.path.join(home, 'protein/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Proteins from database')
    load_protein_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all DisGeNet proteins from database')
    load_all_DisGeNet_protein_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
