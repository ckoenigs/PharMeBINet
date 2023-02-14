import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary with pharmebinet genes with identifier as key and value node as dictionary
dict_genes_pharmebinet = {}

'''
load in all genes from pharmebinet in a dictionary
'''


def load_pharmebinet_genes_in():
    query = '''MATCH (n:Gene) RETURN n'''
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_genes_pharmebinet[identifier] = dict(node)

    print('number of gene nodes in pharmebinet:' + str(len(dict_genes_pharmebinet)))


# dictionary of genes which are not in pharmebinet with they properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_ctd_gene_not_in_pharmebinet = {}

# dictionary of ctd genes which are in pharmebinet with properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_ctd_gene_in_pharmebinet = {}

'''
check if gene id is in pharmebinet
check if name is equal
combine pharmebinet xrefs with pharmGKB, bioGRID and UniProt Ids
last step write information into file
and return found gene in pharmebinet True or false
'''


def search_for_id_and_write_into_file(gene_id, gene_node):
    if gene_id in dict_genes_pharmebinet:
        gene_name = gene_node['name'] if 'name' in gene_node else ''
        pharmebinet_node = dict_genes_pharmebinet[gene_id]
        if gene_name != dict_genes_pharmebinet[gene_id]['name']:
            print(gene_id)
            print('not the same name')

        # gather all xrefs information and add to dictionary
        pharmGKBIDs = gene_node['pharmGKBIDs'] if 'pharmGKBIDs' in gene_node else []
        pharmGKBIDs = ['PharmGKB:' + id for id in pharmGKBIDs]
        bioGRIDIDs = gene_node['bioGRIDIDs'] if 'bioGRIDIDs' in gene_node else []
        bioGRIDIDs = ['bioGRID:' + id for id in bioGRIDIDs]
        # uniProtIDs = gene_node['uniProtIDs'] if 'uniProtIDs' in gene_node else []
        xrefs = set(pharmGKBIDs).union(pharmebinet_node['xrefs']) if 'xrefs' in pharmebinet_node else set(pharmGKBIDs)
        xrefs = xrefs.union(bioGRIDIDs)
        # xrefs = xrefs.union(uniProtIDs)
        xrefs = '|'.join(xrefs)
        writer.writerow([gene_id, gene_id, xrefs])
        return True
    else:
        return False


'''
load all ctd genes and check if they are in pharmebinet or not
'''


def load_ctd_genes_in():
    # take only human genes
    # query = '''MATCH (n:CTD_gene) Where ()-[:associates_CG{organism_id:'9606'}]->(n)  RETURN n'''
    # because ncbi only the human genes are in pharmebinet it is ok to take all ctd genes
    query = '''MATCH (n:CTD_gene) RETURN n'''
    results = g.run(query)

    counter = 0
    for record in results:
        gene_node=record.data()['n']
        gene_id = gene_node['gene_id']
        altGeneIDs = gene_node['altGeneIDs'] if 'altGeneIDs' in gene_node else []
        if not search_for_id_and_write_into_file(gene_id, gene_node):
            for alternative_id in altGeneIDs:
                if search_for_id_and_write_into_file(alternative_id, gene_node):
                    print(gene_id)
                    print(alternative_id)
                    print('alternative is human')
        else:
            counter += 1

    print('number of ctd genes which are also in pharmebinet: ' + str(counter))


'''
Generate cypher and tsv for generating the new nodes and the relationships
'''


def generate_files():
    # generate cyoher file
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = ''' Match (c:Gene{ identifier:line.GeneIDpharmebinet}), (n:CTD_gene{gene_id:line.GeneIDCTD}) Create (c)-[:equal_to_CTD_gene]->(n) Set c.ctd="yes", c.resource=c.resource+"CTD", c.xrefs=split(line.xrefs,'|'), c.url_ctd=" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/gene/mapping.tsv',
                                              query)
    cypher_file.write(query)

    global writer
    csvfile = open('gene/mapping.tsv', 'w')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GeneIDCTD', 'GeneIDpharmebinet', 'xrefs'])


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
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

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

    load_ctd_genes_in()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
