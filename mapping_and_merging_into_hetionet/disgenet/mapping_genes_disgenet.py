
import datetime
import sys, os
import csv
sys.path.append("../..")
import create_connection_to_databases

def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary gene id to resource
dict_gene_id_to_resource = {}

#dictionary from gene id to gene id
dict_gene_id_to_gene_id = {}

def load_genes_from_database_and_add_to_dict():
    """
    Load all Genes from my database  and add them into a dictionary
    """
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)

    for node, in results:
        identifier = node['identifier']
        dict_gene_id_to_resource[identifier] = node['resource']


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
    # master_database_change/mapping_and_merging_into_hetionet/DisGeNet/
    query = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{file_path}" As line FIELDTERMINATOR "\\t" \
        Match (n:gene_DisGeNet{{geneId:line.DisGeNet_gene_id}}), (v:Gene{{identifier:line.gene_id}}) Set v.disgenet="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DisGeNet_gene{{mapped_with:line.mapping_method}}]->(n);\n'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def resource(identifier):
    resource = set(dict_gene_id_to_resource[identifier])
    resource.add('DisGeNet')
    return '|'.join(resource)


def load_all_DisGeNet_genes_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:gene_DisGeNet) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for node, in results:
        counter_all += 1
        identifier = node['geneId']
        # mapping
        if identifier in dict_gene_id_to_resource:
            csv_mapping.writerow(
                [identifier, identifier, resource(identifier), 'id'])
        else:
            counter_not_mapped += 1
            print(identifier)
    print('number of not-mapped genes:', counter_not_mapped)
    print('number of all genes:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.utcnow())

    global home
    global path_of_directory
    global source


    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet gene')

    os.chdir(path_of_directory + 'master_database_change/mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene/')


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all Genes from database')
    load_genes_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all DisGeNet genes from database')
    load_all_DisGeNet_genes_and_finish_the_files(csv_mapping)


if __name__ == "__main__":
    # execute only if run as a script
    main()
