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

#dictionary gene symbol to gene ids
dict_gene_symbol_to_ids={}
#dictionary gene symbol to gene ids
dict_gene_symbol_alternative_to_ids={}


def load_genes_from_database_and_add_to_dict():
    """
    Load all Genes from my database  and add them into a dictionary
    """
    query = "MATCH (n:Gene) RETURN n.identifier, n.gene_symbol, n.gene_symbols, n.xrefs, n.resource "
    results = g.run(query)

    for identifier, gene_symbol, gene_symbols, xrefs, resource, in results:
        dict_gene_id_to_resource[identifier] = resource
        pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_ids, gene_symbol, identifier)
        for symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_alternative_to_ids, symbol, identifier)



def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'DISEASES_gene_to_Gene'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['DISEASE_gene_id', 'gene_id', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    query = f' Match (n:DISEASES_Gene{{id:line.DISEASE_gene_id}}), (v:Gene{{identifier:line.gene_id}}) Set v.diseases="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DISEASES_gene{{how_mapped:line.mapping_method}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, 'w', encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def load_all_diseases_genes_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:DISEASES_Gene) Where  (n)-[:DISEASES_ASSOCIATED_WITH{evidence_type:'experiment'}]-() or (n)-[:DISEASES_ASSOCIATED_WITH{evidence_type:'data_source'}]-()  RETURN n.id, n.name"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for identifier, gene_symbol, in results:
        counter_all += 1
        is_mapped=False

        if gene_symbol in dict_gene_symbol_to_ids:
            is_mapped = True
            for gene_id in dict_gene_symbol_to_ids[gene_symbol]:
                csv_mapping.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], "DISEASES"),
                     'gene_symbol'])

        if is_mapped:
            continue

        if identifier in dict_gene_symbol_to_ids:
            is_mapped = True
            for gene_id in dict_gene_symbol_to_ids[identifier]:
                csv_mapping.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], "DISEASES"),
                     'id_gene_symbol'])

        if is_mapped:
            continue

        if gene_symbol in dict_gene_symbol_alternative_to_ids:
            is_mapped = True
            for gene_id in dict_gene_symbol_alternative_to_ids[gene_symbol]:
                csv_mapping.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], "DISEASES"),
                     'alt_gene_symbol'])

        if is_mapped:
            continue

        if identifier in dict_gene_symbol_alternative_to_ids:
            is_mapped = True
            for gene_id in dict_gene_symbol_alternative_to_ids[identifier]:
                csv_mapping.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], "DISEASES"),
                     'id_alt_gene_symbol'])

        if is_mapped:
            continue

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
        sys.exit('need a path diseases gene')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/diseases')
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
    print('Load all diseases genes from database')
    load_all_diseases_genes_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
