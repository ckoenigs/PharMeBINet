import csv
import datetime
import os, sys


sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
# import create_connection_to_database_metabolite


# dictionary protein id to resource
dict_identifier_to_resource = {}


# dictionary protein name to identifier
dict_protein_name_to_identifier = {}

#dictionary for gene_symbol to protein gene_name
dict_gene_symbol_to_gene_name = {}

def load_proteins_from_database_and_add_to_dict():
    """
    Load all Proteins from pharmebinet and add them into a dictionary
    """
    query = "MATCH (n:Protein) RETURN n.identifier, n.name, n.resource, n.synonyms"
    results = g.run(query)

    for identifier, name, resource , synonyms, in results:
        dict_identifier_to_resource[identifier] = resource
        name = name.lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_to_identifier, name, identifier)
        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_to_identifier, synonym, identifier)

    query2 = "MATCH (g:Gene)--(p:Protein) RETURN g.gene_symbol ,p.identifier"
    results2 = g.run(query2)

    for gene_symbol, identifier, in results2:
        # for gene_symbol in node['gene_symbols']:
        pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_gene_name, gene_symbol.lower(), identifier)

def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'MarkerDB_protein_to_Protein'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['MarkerDB_id', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/MakerDB/
    query = f' Match (n:MarkerDB_Protein{{id:toInteger(line.MarkerDB_id)}}), (v:Protein{{identifier:line.identifier}}) Set v.markerdb="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_MarkerDB_protein{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping

def load_all_MarkerDB_proteins_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:MarkerDB_Protein) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node.get('uniprot_id', None)
        unique_id = node['id']
        protein_name = node['name'].lower()
        if 'gene_name' in node:
            gene_name = node['gene_name'].lower()
        ignored_id = ["P01860", "Q969X2"]
        # mapping
        if identifier not in ignored_id:
            if identifier in dict_identifier_to_resource:
                csv_mapping.writerow(
                    [unique_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier], "MarkerDB"),
                        'id'])
            elif protein_name in dict_protein_name_to_identifier:
                identifier = dict_protein_name_to_identifier[protein_name].pop()
                csv_mapping.writerow(
                    [unique_id, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier],"MarkerDB"),
                    'name'])
            elif gene_name in dict_gene_symbol_to_gene_name and dict_gene_symbol_to_gene_name[gene_name]:
                identifier = dict_gene_symbol_to_gene_name[gene_name].pop()
                csv_mapping.writerow(
                    [unique_id, identifier,
                    pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier],"MarkerDB"),
                    'gene_symbol'])
            else:
                counter_not_mapped += 1
                print(unique_id, protein_name, gene_name)
        else:
            counter_not_mapped += 1
            print(identifier, protein_name)


    print('number of not-mapped proteins:', counter_not_mapped)
    print('number of all proteins:', counter_all)

def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    # driver = create_connection_to_database_metabolite.database_connection_neo4j_driver()
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
    path_of_directory = os.path.join(home, 'protein/')


    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Proteins from database')
    load_proteins_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all MarkerDB proteins from database')
    load_all_MarkerDB_proteins_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()
