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
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with pharmebinet proteins with identifier as key and value node as dictionary
dict_protein_pharmebinet_to_resource = {}
# dictionary refseq id to protein ids
dict_refseq_to_protein_ids = {}
# dictionary gene symbol to protein ids
dict_gene_symbol_to_protein_ids = {}


def load_pharmebinet_node():
    '''
    load in all protein from pharmebinet in a dictionary
    '''
    query = '''MATCH (n:Protein) RETURN n'''
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_protein_pharmebinet_to_resource[identifier] = dict(node)
        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('RefSeq:'):
                refseq_id = xref.rsplit(':', 1)[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_refseq_to_protein_ids, refseq_id, identifier)

    # get the identifier of the protein using the connection between 'Gene' and 'Protein'
    query = "MATCH a=(m:Gene)--(b:Protein) RETURN m.identifier, m.gene_symbol,b.identifier"
    result = g.run(query)
    for record in result:
        [gene, gene_symbol, protein] = record.values()
        pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_protein_ids, gene_symbol, protein)

    print('number of protein nodes in pharmebinet:' + str(len(dict_protein_pharmebinet_to_resource)))


def generate_files():
    '''
    Generate cypher and tsv for generating the new nodes and the relationships
    '''
    global writer
    file_name = 'protein/mapping_protein.tsv'
    csvfile = open(file_name, 'w', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['id', 'id_refseq', 'how_mapped'])

    # generate cypher file
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = ''' Match (c:Protein{ identifier:line.id}), (n:refSeq_CDS{ id:line.id_refseq})  Create (c)-[:equal_to_protein_refseq{how_mapped:line.how_mapped}]->(n) Set c.refseq="yes", c.resource=c.resource+"RefSeq"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/refseq/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def load_and_map_RefSeq_cds():
    """
    Load all human cds and try to map with
    :return:
    """
    query = '''MATCH (n:refSeq_CDS) RETURN n.id, n.name, n.protein_id, n.gene'''
    results = g.run(query)

    counter = 0
    mapped = 0
    for record in results:
        counter += 1
        [cds_id, name, protein_id, gene_symbol] = record.values()

        is_mapped = False

        if gene_symbol in dict_gene_symbol_to_protein_ids:
            mapped += 1
            is_mapped = True
            for pharmebinet_id in dict_gene_symbol_to_protein_ids[gene_symbol]:
                writer.writerow([pharmebinet_id, cds_id, 'gene_symbol'])

        if is_mapped:
            continue

        if protein_id in dict_refseq_to_protein_ids:
            mapped += 1
            is_mapped = True
            for pharmebinet_id in dict_refseq_to_protein_ids[protein_id]:
                writer.writerow([pharmebinet_id, cds_id, 'refseq_id'])

    print('number of existing proteins', counter)
    print('number of mapped proteins', mapped)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path refseq')

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
    print('Load all proteins from pharmebinet into a dictionary')

    load_pharmebinet_node()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all ctd proteins from neo4j into a dictionary')

    load_and_map_RefSeq_cds()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
