import datetime
import sys, os
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary gene id to resource
dict_gene_id_to_resource = {}


def load_genes_from_database_and_add_to_dict():
    """
    Load all Genes from my database  and add them into a dictionary
    """
    query = "MATCH (n:Gene) RETURN n.identifier, n.resource "
    results = g.run(query)

    for record in results:
        [identifier, resource] = record.values()
        dict_gene_id_to_resource[identifier] = resource


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'DisGeNet_gene_to_Gene'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['DisGeNet_gene_id', 'gene_id', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f' Match (n:gene_DisGeNet{{geneId:line.DisGeNet_gene_id}}), (v:Gene{{identifier:line.gene_id}}) Set v.disgenet="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DisGeNet_gene{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def load_all_DisGeNet_genes_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:gene_DisGeNet) RETURN n.geneId"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        [identifier] = record.values()
        counter_all += 1

        if identifier in dict_gene_id_to_resource:
            csv_mapping.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[identifier], "DisGeNet"),
                 'id'])
        else:
            counter_not_mapped += 1
            print(identifier)
    print('number of not-mapped genes:', counter_not_mapped)
    print('number of all genes:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet gene')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/disgenet')
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
    print('Load all DisGeNet genes from database')
    load_all_DisGeNet_genes_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
