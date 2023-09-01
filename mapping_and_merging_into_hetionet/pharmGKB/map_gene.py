import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary of all gene ids to resource
dict_gene_to_resource = {}

# dictionary gene symbol to gene id
dict_gene_symbol_to_gene_id = {}

# dictionary hgnc id to gene id
dict_hgnc_id_to_gene_id = {}

# dictionary synonym to gene id
dict_synonym_to_gene_id = {}

# dictionary gene id to xrefs
dict_gene_id_to_xrefs = {}


def load_db_genes_in():
    """
    load in all genes from pharmebinet in a dictionary
    :return:
    """
    query = '''MATCH (n:Gene) RETURN n.identifier,n.gene_symbols, n.gene_symbol, n.resource, n.synonyms, n.xrefs'''
    results = g.run(query)

    for record in results:
        [identifier, gene_symbols, gene_symbol, resource, synonyms, xrefs] = record.values()
        dict_gene_to_resource[identifier] = resource if resource else []
        dict_gene_id_to_xrefs[identifier] = xrefs if xrefs else []

        if xrefs:
            for xref in xrefs:
                if xref.startswith('HGNC'):
                    hgnc_id = xref.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_hgnc_id_to_gene_id, hgnc_id, identifier)

        if gene_symbols:
            for gene_symbol in gene_symbols:
                gene_symbol = gene_symbol.lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_gene_id, gene_symbol, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_gene_id, synonym, identifier)

    print('length of gene in db:' + str(len(dict_gene_to_resource)))


def add_information_to_file(gene_id, identifier, csv_writer, how_mapped):
    """
    Prepare the resource and xrefs and write match into tsv file.
    :param gene_id: string
    :param identifier: string
    :param csv_writer:csv writer
    :param how_mapped: string
    :return:
    """

    xrefs = dict_gene_id_to_xrefs[gene_id]
    xrefs.append('PharmGKB:' + identifier)
    # print(xrefs)
    xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, 'Gene')
    # print(xrefs)

    csv_writer.writerow(
        [gene_id, identifier, pharmebinetutils.resource_add_and_prepare(dict_gene_to_resource[gene_id], "PharmGKB"),
         how_mapped, '|'.join(xrefs)])


def load_pharmgkb_genes_in():
    """
    generate mapping file and cypher file
    mapp gene pharmgkb to gene
    :return:
    """
    # tsv_file
    file_name = 'gene/mapping.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['gene_id', 'pharmgkb_id', 'resource', 'how_mapped', 'xrefs'])

    # generate cypher file
    generate_cypher_file(file_name)

    query = '''MATCH (n:PharmGKB_Gene) RETURN n'''
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    for record in results:
        result = record.data()['n']
        identifier = result['id']
        ncbi_gene_ids = result['ncbi_gene_ids'] if 'ncbi_gene_ids' in result else []

        found_a_mapping = False
        for ncbi_gene_id in ncbi_gene_ids:
            if ncbi_gene_id in dict_gene_to_resource:
                found_a_mapping = True
                add_information_to_file(ncbi_gene_id, identifier, csv_writer, 'id')

        if found_a_mapping:
            counter_map += 1
            continue

        hgnc_ids = result['hgnc_ids'] if 'hgnc_ids' in result else []
        for hgnc_id in hgnc_ids:
            if hgnc_id in dict_hgnc_id_to_gene_id:
                found_a_mapping = True
                for gene_id in dict_hgnc_id_to_gene_id[hgnc_id]:
                    add_information_to_file(gene_id, identifier, csv_writer, 'hgnc')

        if found_a_mapping:
            counter_map += 1
            continue

        symbol = result['symbol'].lower() if 'symbol' in result else ''

        if len(symbol) > 0 and symbol in dict_gene_symbol_to_gene_id:
            found_a_mapping = True
            for gene_id in dict_gene_symbol_to_gene_id[symbol]:
                add_information_to_file(gene_id, identifier, csv_writer, 'symbol')

        if found_a_mapping:
            counter_map += 1
            continue

        if len(symbol) > 0 and symbol in dict_synonym_to_gene_id:
            for gene_id in dict_synonym_to_gene_id[symbol]:
                add_information_to_file(gene_id, identifier, csv_writer, 'symbolSynonym')
            counter_map += 1

        else:
            counter_not_mapped += 1
    print('number of genes which mapped:', counter_map)
    print('number of genes which not mapped:', counter_not_mapped)


def generate_cypher_file(file_name):
    """
    perpare cypher file and add cypher query
    :param file_name:
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w')
    query = '''  MATCH (n:PharmGKB_Gene{id:line.pharmgkb_id}), (c:Gene{identifier:line.gene_id})  Set c.pharmgkb='yes', c.xrefs=split(line.xrefs,"|"), c.resource=split(line.resource,'|') Create (c)-[:equal_to_gene_pharmgkb{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in gene from pharmebinet')

    load_db_genes_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in gene from pharmgb in')

    load_pharmgkb_genes_in()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
