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
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


sys.path.append("../..")
import pharmebinetutils


def generate_files(path_of_directory, file_name, source, label_hgnc, label_pharmebinet, id_property_hgncs):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_path = os.path.join(path_of_directory, file_name)
    header = ['hgnc_id', 'pharmebinet_node_id', 'resource', 'gene_symbols', 'xrefs', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f' Match (n:{label_hgnc}{{ {id_property_hgncs}:line.hgnc_id}}), (v:{label_pharmebinet}{{identifier:line.pharmebinet_node_id}}) Set v.hgnc="yes", v.pubMed_ids=n.pubmed_ids ,v.resource=split(line.resource,"|"), v.gene_symbols=split(line.gene_symbols,"|"), v.xrefs=split(line.xrefs,"|") Create (v)-[:equal_to_hgnc_{label_pharmebinet.lower()}{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    cypher_file.write(query)
    return csv_mapping


# dictionary gene id to resource and gene symbols
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

    for record in results:
        node = record.data()['n']
        identifier = int(node['identifier'])
        gene_symbols = set(node['gene_symbols'])
        xrefs = set(node['xrefs']) if 'xrefs' in node else set()
        dict_gene_id_to_resource[identifier] = [node['resource'], gene_symbols, xrefs]
        for gene_symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_gene_ids, gene_symbol, identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_synonym_to_gene_ids, synonym, identifier)


def load_all_hgnc_genes_and_finish_the_files(csv_mapping):
    """
    Load all hgnc gene map to gene and write into file
    """

    query = "MATCH (n:hgnc_Gene) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1

        hgnc_id = node['hgnc_id']
        if not 'entrez_id' in node:
            print('no entrez id', hgnc_id)
        entrez_id = node['entrez_id'] if 'entrez_id' in node else ''

        symbol = node['symbol']
        alias_symbols = set(node['alias_symbols']) if 'alias_symbols' in node else set()
        prev_symbols = set(node['prev_symbols']) if 'prev_symbols' in node else set()

        # xref combination
        refseq_accessions = node['refseq_accessions'] if 'refseq_accessions' in node else []

        # mapping
        found_mapping = False
        if entrez_id in dict_gene_id_to_resource:
            found_mapping = True
            symbols_combination = dict_gene_id_to_resource[entrez_id][1]
            symbols_combination = symbols_combination.union(alias_symbols)
            symbols_combination = symbols_combination.union(prev_symbols)
            symbols_combination.add(symbol)
            gene_xrefs = dict_gene_id_to_resource[entrez_id][2]
            gene_xrefs.add('HGNC:'+hgnc_id)
            for refseq_accession in refseq_accessions:
                gene_xrefs.add(f'RefSeq:{refseq_accession}')
            csv_mapping.writerow(
                [hgnc_id, entrez_id,
                 pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[entrez_id][0], "HGNC"),
                 '|'.join(symbols_combination), '|'.join(gene_xrefs), 'id'])

        else:
            counter_not_mapped += 1
            print('not mapped')
            print(hgnc_id)
            print(entrez_id)
    print('number of not-mapped genes:', counter_not_mapped)
    print('number of all genes:', counter_all)


def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hgnc gene')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/hgnc')
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

    csv_mapping = generate_files(path_of_directory, 'mapping_gene.tsv', source, 'hgnc_Gene',
                                 'Gene', 'hgnc_id')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all DisGeNet genes from database')
    load_all_hgnc_genes_and_finish_the_files(csv_mapping)
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
