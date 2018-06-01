# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with all pairs and properties as value
dict_gene_go = {}

# csv files for bp. mf, cc
bp_file=open('gene_go/bp.csv','w')
bp_writer = csv.writer(bp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
bp_writer.writerow(['GeneID', 'GOID'])

mf_file=open('gene_go/mf.csv','w')
mf_writer = csv.writer(mf_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
mf_writer.writerow(['GeneID', 'GOID'])

cc_file=open('gene_go/cc.csv','w')
cc_writer = csv.writer(cc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
cc_writer.writerow(['GeneID', 'GOID'])


# dictionary with for biological_process, cellular_component, molecular_function the right file
dict_processe = {
    "Biological Process": bp_writer,
    "Molecular Function": mf_writer,
    "Cellular Component": cc_writer
}

#dictionary counter for bp, cc, mf
dict_processe_counter = {
    "Biological Process": 0,
    "Molecular Function": 0,
    "Cellular Component": 0
}

'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_go():
    # generate cypher file
    cypherfile = open('gene_go/cypher.cypher', 'w')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpBP]->(b:BiologicalProcess)  Where not exists(r.hetionet) Set r.hetionet="yes";\n')
    cypherfile.write('commit\n')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpMF]->(b:MolecularFunction)  Where not exists(r.hetionet) Set r.hetionet="yes";\n')
    cypherfile.write('commit\n')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpCC]->(b:CellularComponent)  Where not exists(r.hetionet) Set r.hetionet="yes";\n')
    cypherfile.write('commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/gene_go/bp.csv" As line Match (n:Gene{identifier:toInteger(line.GeneID)}), (b:BiologicalProcess{identifier:line.GOID}) Merge (n)-[r:PARTICIPATES_GpBP]->(b) On Create Set r.hetionet='no', r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/gene_go/mf.csv" As line Match (n:Gene{identifier:toInteger(line.GeneID)}), (b:MolecularFunction{identifier:line.GOID}) Merge (n)-[r:PARTICIPATES_GpMF]->(b) On Create Set r.hetionet='no', r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/gene_go/cc.csv" As line Match (n:Gene{identifier:toInteger(line.GeneID)}), (b:CellularComponent{identifier:line.GOID}) Merge (n)-[r:PARTICIPATES_GpCC]->(b) On Create Set r.hetionet='no', r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n '''
    cypherfile.write(query)
    cypherfile.write('begin\n')
    cypherfile.write('Match (n:Gene)-[r:PARTICIPATES_GpBP]->(b:BiologicalProcess) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypherfile.write('commit\n')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpMF]->(b:MolecularFunction) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypherfile.write('commit\n')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpCC]->(b:CellularComponent) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypherfile.write('commit')

    query = '''MATCH (gene:CTDgene)-[r:associates_GGO]->(go:CTDGO) Where ()-[:equal_to_CTD_gene]->(gene)  RETURN gene.gene_id, r, go.go_id, go.ontology'''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    for gene_id, rela, go_id, ontology in results:
        rela = dict(rela)
        if len(rela) > 1:
            print('change integration of properties')
        if not (gene_id, go_id) in dict_gene_go:
            dict_gene_go[(gene_id, go_id)] = rela
            dict_processe_counter[ontology]+=1
            writer= dict_processe[ontology]
            writer.writerow([gene_id, go_id])
            count_possible_relas += 1
        else:
            count_multiple_pathways += 1
        if count_possible_relas%1000==0:
            print(count_possible_relas)


    print('number of new rela:'+str(count_possible_relas))
    print('number of relationships which appears multiple time:'+str(count_multiple_pathways))
    print(dict_processe_counter)




def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Take all gene-go relationships and generate csv files and cypher file')

    take_all_relationships_of_gene_go()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
