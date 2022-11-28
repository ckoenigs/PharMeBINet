import datetime
import sys, os
import csv
import general_function_bioGrid

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary gene id to resource
dict_gene_id_to_resource = {}

# dictionary gene_symbol to gene id
dict_gene_symbol_to_gene_ids = {}

# dictionary synonym to gene id
dict_gene_synonym_to_gene_ids = {}


def load_genes_from_database_and_add_to_dict():
    """
    Load all Genes from my database  and add them into a dictionary
    """
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)

    for node, in results:
        identifier = node['identifier']
        dict_gene_id_to_resource[identifier] = node['resource']
        gene_symbols = node['gene_symbols']
        for gene_symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_gene_ids, gene_symbol, identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_synonym_to_gene_ids, synonym, identifier)


def load_all_bioGrid_genes_and_finish_the_files(csv_mapping):
    """
    Load all bioGrid gene map to gene and write into file
    """

    query = "MATCH (n:bioGrid_gene) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for node, in results:
        counter_all += 1
        identifier = node['gene_id']

        # this gene was withdrawn and would mapp to multiple nodes
        if identifier=='389036':
            continue
        gene_id_entrez = node['gene_id_entrez']
        gene_symbol = node['gene_symbol']

        # mapping
        found_mapping = False
        if gene_id_entrez in dict_gene_id_to_resource:
            found_mapping = True
            csv_mapping.writerow(
                [identifier, gene_id_entrez,
                 pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id_entrez], "bioGrid"), 'id'])
        elif gene_symbol in dict_gene_symbol_to_gene_ids:
            found_mapping = True
            for gene_id in dict_gene_symbol_to_gene_ids[gene_symbol]:
                csv_mapping.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], "bioGrid"),
                     'gene_symbol'])

        if found_mapping:
            continue

        if gene_symbol in dict_gene_synonym_to_gene_ids:
            for gene_id in dict_gene_synonym_to_gene_ids[gene_symbol]:
                csv_mapping.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], "bioGrid"),
                     'gene_symbol_synonyms'])


        else:
            counter_not_mapped += 1
            print('not mapped')
            print(identifier)
            print(gene_id_entrez)
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
        sys.exit('need a path biogrid gene')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bioGrid')
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

    csv_mapping = general_function_bioGrid.generate_files(path_of_directory, 'mapping_gene.tsv', source, 'bioGrid_gene',
                                                          'Gene', ['gene_id'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all DisGeNet genes from database')
    load_all_bioGrid_genes_and_finish_the_files(csv_mapping)


if __name__ == "__main__":
    # execute only if run as a script
    main()
