import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases


sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of all gene ids to resource
dict_gene_to_resource = {}

# dictionary gene symbol to gene id
dict_gene_symbol_to_gene_id = {}

# dictionary synonym to gene id
dict_synonym_to_gene_id = {}

# dictionary gene id to xrefs
dict_gene_id_to_xrefs = {}

'''
load in all compound from hetionet in a dictionary
'''


def load_db_genes_in():
    query = '''MATCH (n:Gene) RETURN n.identifier,n.geneSymbol, n.resource, n.synonyms, n.xrefs'''
    results = g.run(query)

    for identifier, gene_symbols, resource, synonyms, xrefs, in results:
        dict_gene_to_resource[identifier] = resource if resource else []
        dict_gene_id_to_xrefs[identifier] = xrefs if xrefs else []

        if gene_symbols:
            for gene_symbol in gene_symbols:
                gene_symbol = gene_symbol.lower()
                if gene_symbol not in dict_gene_symbol_to_gene_id:
                    dict_gene_symbol_to_gene_id[gene_symbol] = set()
                dict_gene_symbol_to_gene_id[gene_symbol].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym=synonym.lower()
                if synonym not in dict_synonym_to_gene_id:
                    dict_synonym_to_gene_id[synonym] = set()
                dict_synonym_to_gene_id[synonym].add(identifier)


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
    resource = dict_gene_to_resource[gene_id]
    resource.append("PharmGKB")
    resource = "|".join(sorted(resource))

    xrefs = dict_gene_id_to_xrefs[gene_id]
    xrefs.append('PharmGKB:'+identifier)
    # print(xrefs)
    xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, 'Gene')
    # print(xrefs)

    csv_writer.writerow([gene_id, identifier, resource, how_mapped, '|'.join(xrefs)])

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

    for result, in results:
        identifier = result['id']
        ncbi_gene_ids = result['ncbi_gene_ids'] if 'ncbi_gene_ids' in result else []

        found_a_mapping = False
        for ncbi_gene_id in ncbi_gene_ids:
            if ncbi_gene_id in dict_gene_to_resource:
                found_a_mapping = True
                add_information_to_file(ncbi_gene_id, identifier, csv_writer,'id')

        symbol = result['symbol'].lower() if 'symbol' in result else ''
        if not found_a_mapping:

            if len(symbol) > 0 and symbol in dict_gene_symbol_to_gene_id:
                found_a_mapping=True
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
    cypher_file = open('output/cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:PharmGKB_Gene{id:line.pharmgkb_id}), (c:Gene{identifier:line.gene_id})  Set c.pharmgkb='yes', c.xrefs=split(line.xrefs,"|"), c.resource=split(line.resource,'|') Create (c)-[:equal_to_gene_pharmgkb{how_mapped:line.how_mapped}]->(n); \n'''
    query = query % (file_name)
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
    print('Load in gene from hetionet')

    load_db_genes_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in gene from pharmgb in')

    load_pharmgkb_genes_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()