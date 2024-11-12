import csv
import datetime
import os, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
# import create_connection_to_database_metabolite


# dictionary gene id to resource
dict_gene_id_to_resource = {}

# dictionary from gene id to gene id
dict_gene_id_to_gene_id = {}

# dictionary gene symbol to gene id
dict_gene_symbol_to_gene_id = {}

def load_genes_from_database_and_add_to_dict():
    """
    Load all Genes from my database and add them into a dictionary
    """
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_gene_id_to_resource[identifier] = node['resource']
        gene_symbol = node['gene_symbol']
        dict_gene_symbol_to_gene_id[gene_symbol] = {"identifier": node['identifier'], "resource": node['resource']}


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'MarkerDB_gene_to_Gene'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['MarkerDB_gene_id', 'gene_id', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f' Match (n:MarkerDB_Gene{{id:toInteger(line.MarkerDB_gene_id)}}), (v:Gene{{identifier:line.gene_id}}) Set v.markerdb="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_MarkerDB_gene{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping

def load_all_MarkerDB_genes_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:MarkerDB_Gene) RETURN n.entrez_gene_id, n.id, n.gene_symbol"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        [identifier, unique_id, gene_symbol] = record.values()
        counter_all += 1

        # mapping
        if identifier in dict_gene_id_to_resource:
            csv_mapping.writerow(
                [unique_id, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[identifier], "MarkerDB"),
                 'id'])
        elif gene_symbol in dict_gene_symbol_to_gene_id:
            csv_mapping.writerow(
                [unique_id, dict_gene_symbol_to_gene_id[gene_symbol]["identifier"],
                 pharmebinetutils.resource_add_and_prepare(dict_gene_symbol_to_gene_id[gene_symbol]["resource"],"MarkerDB"),
                'gene_symbol'])
        else:
            counter_not_mapped += 1
            print(identifier)


    print('number of not-mapped genes:', counter_not_mapped)
    print('number of all genes:', counter_all)

def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    # driver = create_connection_to_database_metabolite.database_connection_neo4j_driver()
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

def main():
    global path_of_directory
    global source
    global home

    # path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test"

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene/')


    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Genes from database')
    load_genes_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all MarkerDB genes from database')
    load_all_MarkerDB_genes_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()
