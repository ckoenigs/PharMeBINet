from py2neo import Graph
import sys
import datetime
import csv

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


def database_connection():
    """
    create connection to neo4j
    :return:
    """
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


cypher_file = open('output/cypher_gene_phenotype.cypher', 'w', encoding='utf-8')

query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/omim/%s" As line FIELDTERMINATOR '\\t' 
    Match '''

# dictionary_omim_gene_id_to_node
dict_omim_id_to_node = {}

# dictionary of mapping tuples
dict_of_mapped_tuples = {}

# set of not mapped omim gene ids
set_not_mapped_ids = set()

# file header
file_header = ['identifier', 'database_id', 'resource', 'xrefs']


def prepare_csv_files(file_name, file_header):
    """
    generate a csv file in a given path with a given header
    :param file_name: string
    :param file_header: string
    :return:
    """
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(file_header)

    return csv_writer


# dictionary gene-disease: rela info
dict_gene_disease = {}


def load_all_omim_gene_and_start_mapping():
    """
    load all trait gene in and mapp with xref to the mondo genes
    """
    query = "MATCH (g:Gene)--(n:gene_omim)-[r]-(h)--(p) Where 'Disease' in labels(p) or 'Phenotype' in labels(p) RETURN g.identifier, r, p.identifier, labels(p)"
    results = g.run(query)
    counter_mapped = 0
    # csv file
    file_name = "gene/mapping.tsv"
    csv_writer = prepare_csv_files(file_name, file_header)

    file_name_not_mapped = "gene/not_mapping.tsv"
    csv_writer_not = prepare_csv_files(file_name_not_mapped, ['identifier', 'name'])
    # generate query
    add_query_to_cypher_file('gene_omim', 'Gene', 'gene', file_name, is_gene=True,
                             additional_labels=['phenotype_omim', 'predominantly_phenotypes_omim'])

    counter_different_symbol = 0
    for node, labels, in results:
        identifier = node['identifier']

        dict_omim_id_to_node[identifier] = dict(node)
        symbol = node['symbol'].lower() if 'symbol' in node else ''
        alternati_symbols = [x.lower() for x in node['alternative_symbols']] if 'alternative_symbols' in node else []

        xrefs = node['xrefs'] if 'xrefs' in node else []

        found_at_least_one_mapping = False
        for xref in xrefs:
            if xref.startswith('NCBI_GENE:'):
                ncbi_id = xref.split(':')[1]
                if ncbi_id in dict_gene_id_to_gene_node:
                    gene_symbol = [x.lower() for x in
                                   dict_gene_id_to_gene_node[ncbi_id]['geneSymbol']] if 'geneSymbol' in \
                                                                                        dict_gene_id_to_gene_node[
                                                                                            ncbi_id] else []
                    if symbol not in gene_symbol and len(set(gene_symbol).intersection(alternati_symbols)) == 0:
                        # print('different gene symbols')
                        # print(symbol)
                        # print(gene_symbol)
                        # print((identifier, ncbi_id))
                        counter_different_symbol += 1
                    if (identifier, ncbi_id) not in dict_of_mapped_tuples:
                        add_mapped_one_to_csv_file(dict_gene_id_to_gene_node, identifier, ncbi_id, csv_writer,
                                                   dict_of_mapped_tuples, is_gene=True)
                        found_at_least_one_mapping = True

        if found_at_least_one_mapping:
            counter_mapped += 1
        else:
            set_not_mapped_ids.add(identifier)
            csv_writer_not.writerow([identifier, node['name']])

    # print(dict_of_mapped_tuples)
    print('number of mapped gene:' + str(counter_mapped))
    print('number of not mapped gene:' + str(len(set_not_mapped_ids)))
    print(counter_different_symbol)

    return csv_writer
    # print(set_not_mapped_ids)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path omim')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Gene mapping')

    gene_writer = mapping_genes()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all disease from database')

    load_disease_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all omim phenotypes from database and map')

    load_phenotype_from_omim_and_map(gene_writer)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
