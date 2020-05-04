# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph#, authenticate
import datetime
import csv, sys

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", )
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


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
dict_process = {
    "Biological Process": bp_writer,
    "Molecular Function": mf_writer,
    "Cellular Component": cc_writer
}

#dictionary counter for bp, cc, mf
dict_process_counter = {
    "Biological Process": 0,
    "Molecular Function": 0,
    "Cellular Component": 0
}

#dict of labels of the go in hetionet to file names
dict_labels_go_to_file_name={
    'BiologicalProcess':'bp',
    'MolecularFunction': 'mf',
    'CellularComponent':'cc'
}


'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_go():
    # generate cypher file
    cypherfile = open('gene_go/cypher.cypher', 'w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ctd/gene_go/%s.csv" As line Match (n:Gene{identifier:toInteger(line.GeneID)}), (b:%s{identifier:line.GOID}) Merge (n)-[r:PARTICIPATES_Gp%s]->(b) On Create Set r.hetionet='no', r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false', r.resource=['CTD'] On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID, r.resource=r.resource+'CTD';\n '''
    for label, file_name in dict_labels_go_to_file_name.items():
        label_query=query %(file_name,label,file_name.upper())
        cypherfile.write(label_query)
    cypherfile.close()

    #the general cypher file to update all chemicals and relationship which are not from aeolus
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    cypher_general.write(':begin\n')
    cypher_general.write('Match (n:Gene)-[r:PARTICIPATES_GpBP]->(b:BiologicalProcess) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypher_general.write(':commit\n')
    cypher_general.write(':begin\n')
    cypher_general.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpMF]->(b:MolecularFunction) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypher_general.write(':commit\n')
    cypher_general.write(':begin\n')
    cypher_general.write(
        'Match (n:Gene)-[r:PARTICIPATES_GpCC]->(b:CellularComponent) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypher_general.write(':commit')
    cypher_general.close()

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
            dict_process_counter[ontology]+=1
            writer= dict_process[ontology]
            writer.writerow([gene_id, go_id])
            count_possible_relas += 1
        else:
            count_multiple_pathways += 1
        if count_possible_relas%1000==0:
            print(count_possible_relas)


    print('number of new rela:'+str(count_possible_relas))
    print('number of relationships which appears multiple time:'+str(count_multiple_pathways))
    print(dict_process_counter)





# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

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
