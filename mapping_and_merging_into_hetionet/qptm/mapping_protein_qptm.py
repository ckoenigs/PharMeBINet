import csv
import datetime
import os, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary protein id to resource
dict_identifier_to_resource = {}

# dictionary protein name to identifier
dict_protein_name_to_identifier = {}

# dictionary for alternative id to protein main identifier
dict_identifier_to_alternative_ids = {}

# dictionary for gene_symbol to protein identifier
dict_gene_symbol_to_identifer = {}

def load_proteins_from_database_and_add_to_dict():
    """
    Load all Proteins from pharmebinet and add them into a dictionary
    """
    query = "MATCH (n:Protein) RETURN n.identifier, n.name, n.resource, n.alternative_ids"
    results = g.run(query)

    for identifier, name, resource, alternative_ids in results:
        dict_identifier_to_resource[identifier] = resource
        name = name.lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_to_identifier, name, identifier)
        if alternative_ids is not None:
            dict_identifier_to_alternative_ids[identifier] = alternative_ids

    query2 = "MATCH (g:Gene)--(p:Protein) RETURN g.gene_symbol, g.gene_symbols, p.identifier"
    results2 = g.run(query2)

    for gene_symbol, gene_symbols, identifier, in results2:
        dict_gene_symbol_to_identifer[gene_symbol.lower()] = identifier
        if gene_symbols:
            for gene_symbol in gene_symbols:
                if gene_symbol not in dict_gene_symbol_to_identifer:
                    dict_gene_symbol_to_identifer[gene_symbol.lower()] = identifier


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'qptm_protein_to_Protein'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['qptm_identifier', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/qptm/
    query = f' Match (n:qPTM_Protein{{uniprot_id:line.qptm_identifier}}), (v:Protein{{identifier:line.identifier}}) Set v.qptm="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_qPTM_protein{{mapped_with:line.mapping_method}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, 'w', encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def load_all_qptm_proteins_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:qPTM_Protein)--(o:qPTM_Organism) WHERE o.ncbi_taxid = 9606 RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    counter_mapped_id = 0
    counter_mapped_alternative_id = 0
    counter_gene_names = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node.get('uniprot_id', None)
        gene_names = node.get('gene_name', [])
        mapped = False

        # mapping
        if identifier in dict_identifier_to_resource:
            csv_mapping.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier], "qPTM"),
                 'uniprot_id'])
            counter_mapped_id += 1
            mapped = True
        if not mapped and gene_names:
            for gene_name in gene_names:
                lower_gene_name = gene_name.lower()
                if lower_gene_name in dict_gene_symbol_to_identifer:
                    main_id = dict_gene_symbol_to_identifer[lower_gene_name]
                    csv_mapping.writerow(
                        [identifier, main_id,
                         pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[main_id],
                                                                   "qPTM"),
                         'gene_symbol'])
                    mapped = True
                    counter_gene_names += 1
                    break
        if not mapped:
            # if identifier not in dict_identifier_to_alternative_ids:
            for main_id, alternatives in dict_identifier_to_alternative_ids.items():
                if identifier in alternatives:
                    csv_mapping.writerow(
                        [identifier, main_id,
                         pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[main_id], "qPTM"),
                         'alternative_id'])
                    counter_mapped_alternative_id += 1
                    mapped = True
                    break

        if not mapped:
            counter_not_mapped += 1
            print(identifier)

    print('number of mapped id protein:', counter_mapped_id)
    print('number of mapped alternative id protein:', counter_mapped_alternative_id)
    print('number of mapped gene name protein:', counter_gene_names)
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
    print('Load all qPTM proteins from database')
    load_all_qptm_proteins_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    main()
