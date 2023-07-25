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
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary with pharmebinet genes with identifier as key and value node as dictionary
dict_genes_pharmebinet = {}
# dictionary hgnc id to gene ids
dict_hgnc_to_gene_id = {}


def load_pharmebinet_genes_in():
    '''
    load in all genes from pharmebinet in a dictionary
    '''
    query = '''MATCH (n:Gene) RETURN n'''
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_genes_pharmebinet[identifier] = dict(node)
        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('HGNC:'):
                hgnc_id = int(xref.rsplit(':', 1)[1])
                pharmebinetutils.add_entry_to_dict_to_set(dict_hgnc_to_gene_id, hgnc_id, identifier)

    print('number of gene nodes in pharmebinet:' + str(len(dict_genes_pharmebinet)))


def generate_files():
    '''
    Generate cypher and tsv for generating the new nodes and the relationships
    '''
    global writer
    file_name = 'gene/mapping_gene.tsv'
    csvfile = open(file_name, 'w', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['id', 'id_refseq'])

    # generate cypher file
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = ''' Match (c:Gene{ identifier:line.id}), (n:refSeq_Gene{ id:line.id_refseq})  Create (c)-[:equal_to_gene_refseq]->(n) Set c.refseq="yes", c.resource=c.resource+"RefSeq"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/refseq/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def load_and_map_RefSeq_genes():
    """
    Load all human genes and try to map with entrez id and name. All mapped are written into a TSV file.
    :return:
    """
    query = '''MATCH (n:refSeq_Gene) RETURN n.id, n.name, n.xrefs'''
    results = g.run(query)

    counter = 0
    mapped = 0
    for record in results:
        counter += 1
        [gene_id, name, xrefs] = record.values()
        if xrefs:
            for xref in xrefs:
                if xref.startswith('GeneID'):
                    id = xref.split(':')[1]
                    if id in dict_genes_pharmebinet:
                        writer.writerow([id, gene_id])
                        mapped += 1
                        continue

    print('number of existing genes', counter)
    print('number of mapped genes', mapped)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

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
    print('Load all ctd genes from neo4j into a dictionary')

    load_and_map_RefSeq_genes()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
