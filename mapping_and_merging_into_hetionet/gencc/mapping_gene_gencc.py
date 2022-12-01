import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j():
    # create connection with neo4j
    global g
    g = create_connection_to_databases.database_connection_neo4j()


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

    for identifier, resource, xrefs, gene_symbols, in results:
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

'''
load all gencc genes and check if they are in pharmebinet or not
'''


def load_gencc_genes_in():
    # take only human genes
    query = '''MATCH (n:gencc_gene_curie) RETURN n'''
    results = g.run(query)

    counter = 0
    counter_mapped=0
    for gene_node, in results:
        counter+=1
        gene_id = gene_node['gene_curie']
        gene_symbols = gene_node['gene_symbol'] if 'gene_symbol' in gene_node else []
        if gene_id in dict_hgnc_id_to_gene_ids:
            counter_mapped+=1
            for identifier in dict_hgnc_id_to_gene_ids[gene_id]:
                resource=pharmebinetutils.resource_add_and_prepare(dict_gene_to_resource[identifier],'GENCC')
                writer.writerow([gene_id,identifier,resource,'hgnc'])

        else:
            for gene_symbol in gene_symbols:
                if gene_symbol in dict_gene_symbol_to_set_of_ids:
                    counter_mapped+=1
                    for identifier in dict_gene_symbol_to_set_of_ids[gene_symbol]:
                        resource = pharmebinetutils.resource_add_and_prepare(dict_gene_to_resource[identifier], 'GENCC')
                        writer.writerow([gene_id, identifier, resource, 'symbol'])

    print('number of gencc genes which are also in pharmebinet: ' + str(counter_mapped))
    print('number of gencc genes : ' + str(counter))


'''
Generate cypher and tsv for generating the new nodes and the relationships
'''


def generate_files():
    # generate cypher file
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/gencc/gene/mapping.tsv" As line  FIELDTERMINATOR '\\t' Match (c:Gene{ identifier:line.GeneIDPharmebinet}), (n:gencc_gene_curie{gene_curie:line.GeneIDGencc}) Create (c)-[:equal_to_GENCC_gene{how_mapped:line.how_mapped}]->(n) Set c.gencc="yes", c.resource=split(line.resource,"|");\n'''
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

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()