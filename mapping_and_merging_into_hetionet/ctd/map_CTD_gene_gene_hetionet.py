# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph#, authenticate
import datetime
import csv, sys

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# dictionary with hetionet genes with identifier as key and value node as dictionary
dict_genes_hetionet = {}

'''
load in all genes from hetionet in a dictionary
'''


def load_hetionet_genes_in():
    query = '''MATCH (n:Gene) RETURN n'''
    results = g.run(query)

    for node, in results:
        identifier=node['identifier']
        dict_genes_hetionet[identifier] = dict(node)

    print('number of gene nodes in hetionet:' + str(len(dict_genes_hetionet)))


# dictionary of genes which are not in hetionet with they properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_ctd_gene_not_in_hetionet = {}

# dictionary of ctd genes which are in hetionet with properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_ctd_gene_in_hetionet = {}

'''
check if gene id is in hetionet
check if name is equal
combine hetionet xrefs with pharmGKB, bioGRID and UniProt Ids
last step write information into file
and return found gene in hetionet True or false
'''
def search_for_id_and_write_into_file(gene_id,gene_node):
    if gene_id in dict_genes_hetionet:
        gene_name = gene_node['name']
        hetionet_node = dict_genes_hetionet[gene_id]
        if gene_name != dict_genes_hetionet[gene_id]['name']:
            print(gene_id)
            print('not the same name')

        # gather all xrefs information and add to dictionary
        pharmGKBIDs = gene_node['pharmGKBIDs'] if 'pharmGKBIDs' in gene_node else []
        pharmGKBIDs = ['pharmGKB:'+id for id in pharmGKBIDs]
        bioGRIDIDs = gene_node['bioGRIDIDs'] if 'bioGRIDIDs' in gene_node else []
        bioGRIDIDs = ['bioGRID:'+id for id in bioGRIDIDs]
        # uniProtIDs = gene_node['uniProtIDs'] if 'uniProtIDs' in gene_node else []
        xrefs = set(pharmGKBIDs).union(hetionet_node['xrefs']) if 'xrefs' in hetionet_node else set(pharmGKBIDs)
        xrefs = xrefs.union(bioGRIDIDs)
        # xrefs = xrefs.union(uniProtIDs)
        xrefs = '|'.join(xrefs)
        writer.writerow([gene_id, gene_id, xrefs])
        return True
    else:
        return False
'''
load all ctd genes and check if they are in hetionet or not
'''


def load_ctd_genes_in():
    # take only human genes
    # query = '''MATCH (n:CTDgene) Where ()-[:associates_CG{organism_id:'9606'}]->(n)  RETURN n'''
    #because ncbi only the human genes are in hetionet it is ok to take all ctd genes
    query='''MATCH (n:CTDgene) RETURN n'''
    results = g.run(query)

    counter = 0
    for gene_node, in results:
        gene_id = gene_node['gene_id']
        altGeneIDs = gene_node['altGeneIDs'] if 'altGeneIDs' in gene_node else []
        if not search_for_id_and_write_into_file(gene_id,gene_node):
            for alternative_id in altGeneIDs:
                if search_for_id_and_write_into_file(alternative_id,gene_node):
                    print(gene_id)
                    print(alternative_id)
                    print('alternative is human')
        else:
            counter+=1

    print('number of ctd genes which are also in hetionet: '+str(counter))



'''
Generate cypher and csv for generating the new nodes and the relationships
'''


def generate_files():
    #generate cyoher file
    cypher_file = open('gene/cypher.cypher', 'w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ctd/gene/mapping.csv" As line Match (c:Gene{ identifier:line.GeneIDHetionet}), (n:CTDgene{gene_id:line.GeneIDCTD}) Create (c)-[:equal_to_CTD_gene]->(n) Set c.ctd="yes", c.resource=c.resource+"CTD", c.xrefs=split(line.xrefs,'|'), c.url_ctd=" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n'''
    cypher_file.write(query)

    global writer
    csvfile= open('gene/mapping.csv', 'w')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GeneIDCTD', 'GeneIDHetionet','xrefs'])

    # add query to update disease nodes with do='no'
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = ''':begin\n MATCH (n:Gene) Where not exists(n.ctd) Set n.ctd="no";\n :commit\n '''
    cypher_general.write(query)
    cypher_general.close()

# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map generate csv and cypher file ')

    generate_files()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all genes from hetionet into a dictionary')

    load_hetionet_genes_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all ctd genes from neo4j into a dictionary')

    load_ctd_genes_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
