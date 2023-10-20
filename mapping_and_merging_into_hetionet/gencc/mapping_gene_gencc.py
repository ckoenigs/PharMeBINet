import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with pharmebinet genes with identifier as key and value node as dictionary
dict_gene_to_resource = {}

# dictionary gene symbol to set of ids
dict_gene_symbol_to_set_of_ids = {}

# dictionary hgnc id to gene ids
dict_hgnc_id_to_gene_ids = {}


def load_pharmebinet_genes_in():
    """
    Load all pharmebinet genes and prepare the different dictionaries for mapping.
    :return:
    """
    query = '''MATCH (n:Gene) RETURN n.identifier, n.resource, n.xrefs, n.gene_symbols'''
    results = g.run(query)

    for record in results:
        [identifier, resource, xrefs, gene_symbols] = record.values()
        dict_gene_to_resource[identifier] = resource
        for gene_symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_set_of_ids, gene_symbol, identifier)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('HGNC:'):
                    hgnc_id = xref.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_hgnc_id_to_gene_ids, hgnc_id, identifier)

    print('number of gene nodes in pharmebinet:' + str(len(dict_gene_to_resource)))


# dictionary of genes which are not in pharmebinet with they properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_gencc_gene_not_in_pharmebinet = {}

# dictionary of gencc genes which are in pharmebinet with properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_gencc_gene_in_pharmebinet = {}


def load_gencc_genes_in():
    """
    load all gencc genes and check if they are in pharmebinet or not
    :return:
    """
    # take only human genes
    query = '''MATCH (n:GenCC_Gene) RETURN n'''
    results = g.run(query)

    counter = 0
    counter_mapped = 0
    for record in results:
        gene_node = record.data()['n']
        counter += 1
        gene_id = gene_node['id']
        gene_symbol = gene_node['symbol']
        if gene_id in dict_hgnc_id_to_gene_ids:
            counter_mapped += 1
            for identifier in dict_hgnc_id_to_gene_ids[gene_id]:
                resource = pharmebinetutils.resource_add_and_prepare(dict_gene_to_resource[identifier], 'GenCC')
                writer.writerow([gene_id, identifier, resource, 'hgnc'])

        else:
            if gene_symbol in dict_gene_symbol_to_set_of_ids:
                counter_mapped += 1
                for identifier in dict_gene_symbol_to_set_of_ids[gene_symbol]:
                    resource = pharmebinetutils.resource_add_and_prepare(dict_gene_to_resource[identifier], 'GenCC')
                    writer.writerow([gene_id, identifier, resource, 'symbol'])

    print('number of gencc genes which are also in pharmebinet: ' + str(counter_mapped))
    print('number of gencc genes : ' + str(counter))


def generate_files():
    """
    Generate cypher and tsv for generating the new nodes and the relationships
    :return:
    """
    # generate cypher file
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = ''' Match (c:Gene{ identifier:line.GeneIDPharmebinet}), (n:GenCC_Gene{id:line.GeneIDGencc}) Create (c)-[:equal_to_GENCC_gene{how_mapped:line.how_mapped}]->(n) Set c.gencc="yes", c.resource=split(line.resource,"|")'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/gencc/gene/mapping.tsv',
                                              query)
    cypher_file.write(query)

    global writer
    csvfile = open('gene/mapping.tsv', 'w')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GeneIDGencc', 'GeneIDPharmebinet', 'resource', 'how_mapped'])


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path gencc gene')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map generate tsv and cypher file ')

    generate_files()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all genes from pharmebinet into a dictionary')

    load_pharmebinet_genes_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all gencc genes from neo4j into a dictionary')

    load_gencc_genes_in()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
