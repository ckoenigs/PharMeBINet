# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with hetionet genes with identifier as key and value the name
dict_genes_hetionet = {}

'''
load in all genes from hetionet in a dictionary
'''


def load_hetionet_genes_in():
    query = '''MATCH (n:Gene) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_genes_hetionet[identifier] = name

    print('number of gene nodes in hetionet:' + str(len(dict_genes_hetionet)))


# dictionary of genes which are not in hetionet with they properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_ctd_gene_not_in_hetionet = {}

# dictionary of ctd genes which are in hetionet with properties: [gene_name,altGeneIDs,pharmGKBIDs,bioGRIDIDs,geneSymbol,synonyms,uniProtIDs]
dict_ctd_gene_in_hetionet = {}

'''
load all ctd genes and check if they are in hetionet or not
'''


def load_ctd_genes_in():
    query = '''MATCH (n:CTDgene) Where ()-[:associates_CG{organism_id:'9606'}]->(n)  RETURN n'''
    results = g.run(query)

    for gene_node, in results:
        gene_id = int(gene_node['gene_id'])
        gene_name = gene_node['name']
        altGeneIDs = '|'.join(gene_node['altGeneIDs']) if 'altGeneIDs' in gene_node else ''
        pharmGKBIDs = '|'.join(gene_node['pharmGKBIDs']) if 'pharmGKBIDs' in gene_node else ''
        bioGRIDIDs = '|'.join(gene_node['bioGRIDIDs']) if '' in gene_node else ''
        geneSymbol = '|'.join(gene_node['geneSymbol']) if '' in gene_node else ''
        synonyms = '|'.join(gene_node['synonyms']) if '' in gene_node else ''
        uniProtIDs = '|'.join(gene_node['uniProtIDs']) if '' in gene_node else ''

        if gene_id in dict_genes_hetionet:
            if gene_name == dict_genes_hetionet[gene_id]:
                dict_ctd_gene_in_hetionet[gene_id] = [gene_name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol,
                                                      synonyms, uniProtIDs]
            else:
                print('same id but different names')
                print(gene_name)
                print(dict_genes_hetionet[gene_id])
                dict_ctd_gene_in_hetionet[gene_id] = [gene_name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol,
                                                      synonyms, uniProtIDs]
        else:
            dict_ctd_gene_not_in_hetionet[gene_id] = [gene_name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol,
                                                      synonyms, uniProtIDs]

    print('number of existing nodes:' + str(len(dict_ctd_gene_in_hetionet)))
    print('number of not existing nodes:' + str(len(dict_ctd_gene_not_in_hetionet)))


'''
Generate cypher and csv for generating the new nodes and the realtionships
'''


def generate_files():
    # add the gene which are not in hetionet in a csv file
    with open('gene/new_genes.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['GeneID', 'GeneName', 'altGeneIDs', 'pharmGKBIDs', 'bioGRIDIDs', 'geneSymbol', 'synonyms', 'uniProtIDs'])
        # add the go nodes to cypher file
        for gene_id, [name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms,
                      uniProtIDs] in dict_ctd_gene_not_in_hetionet.items():
            writer.writerow([gene_id, name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms, uniProtIDs])

    cypher_file = open('gene/cypher.cypher', 'w')
    cypher_file.write('begin\n')
    cypher_file.write('Match (c:Gene) Set c.hetionet="yes", c.resource=["Hetionet"];\n')
    cypher_file.write('commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/gene/new_genes.csv" As line Create (c:Gene{ identifier:toInteger(line.GeneID), name:line.GeneName, altGeneIDs:split(line.altGeneIDs,'|'),pharmGKBIDs:split(line.pharmGKBIDs,'|'),bioGRIDIDs:split(line.bioGRIDIDs,'|'),geneSymbol:split(line.geneSymbol,'|'),synonyms:split(line.synonyms,'|'),uniProtIDs:split(line.uniProtIDs,'|') , url_ctd:" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID ,url: "http://identifiers.org/ncbigene/"+line.GeneID, source:"CTD" ,description:"", chromosome:"", license:"© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", hetionet:"no", ctd:"yes", resource:["CTD"]});\n'''
    cypher_file.write(query)

    with open('gene/mapping.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GeneIDCTD', 'GeneIDHetionet'])
        # add the go nodes to cypher file

        for gene_id, [name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms,
                      uniProtIDs] in dict_ctd_gene_in_hetionet.items():
            writer.writerow([gene_id, gene_id, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms, uniProtIDs])

        for gene_id, [name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms,
                      uniProtIDs] in dict_ctd_gene_not_in_hetionet.items():
            writer.writerow([gene_id, gene_id, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms, uniProtIDs])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/gene/mapping.csv" As line Match (c:Gene{ identifier:toInteger(line.GeneIDHetionet)}), (n:CTDgene{gene_id:line.GeneIDCTD}) Create (c)-[:equal_to_CTD_gene]->(n) With c,n, line Where c.hetionet="yes" Set c.ctd="yes", c.resource=c.resource+"CTD", c.altGeneIDs=split(line.altGeneIDs,'|'),c.pharmGKBIDs=split(line.pharmGKBIDs,'|'),c.bioGRIDIDs=split(line.bioGRIDIDs,'|'),c.geneSymbol=split(line.geneSymbol,'|'),c.synonyms=split(line.synonyms,'|'),c.uniProtIDs=split(line.uniProtIDs,'|') , c.url_ctd=" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n'''
    cypher_file.write(query)
    cypher_file.close()


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

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
    print('Map generate csv and cypher file ')

    generate_files()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
