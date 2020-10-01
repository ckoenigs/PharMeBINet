# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", )
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary with all pairs and properties as value
dict_gene_pathway = {}

'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_pathway():
    # generate cypher file
    cypherfile = open('gene_pathway/cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ctd/gene_pathway/relationships.csv" As line Match (n:Gene{identifier:line.GeneID}), (b:Pathway{identifier:line.PathwayID}) Merge (n)-[r:PARTICIPATES_GpPW]->(b) On Create Set r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased=false, r.resource=["CTD"] On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID, r.resource=r.resource+"CTD";\n '''
    cypherfile.write(query)
    cypherfile.close()

    # the general cypher file to update all chemicals and relationship which are not from aeolus
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    cypher_general.write(':begin\n')
    cypher_general.write('Match (n:Gene)-[r:PARTICIPATES_GpPW]->(b:Pathway) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypher_general.write(':commit')
    cypher_general.close()

    csvfile = open('gene_pathway/relationships.csv', 'w')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GeneID', 'PathwayID'])

    query = '''MATCH (gene:CTDgene)-[r:participates_GP]->(pathway:CTDpathway) Where ()-[:equal_to_CTD_gene]->(gene)  RETURN gene.gene_id, r, pathway.hetionet_id'''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    for gene_id, rela, pathway_hetionet_id, in results:
        rela = dict(rela)
        if len(rela) > 1:
            print('change integration of properties')
        if not (gene_id, pathway_hetionet_id) in dict_gene_pathway:
            dict_gene_pathway[(gene_id, pathway_hetionet_id)] = rela
            writer.writerow([gene_id, pathway_hetionet_id])
            count_possible_relas += 1
        else:
            count_multiple_pathways += 1
        if count_possible_relas % 1000 == 0:
            print(count_possible_relas)

        # query='''MATCH p=(gene:Gene{identifier:%s})-[r:PARTICIPATES_GpPW]->(pathway:Pathway{identifier:"%s"}) Return p'''
        # query=query%(gene_id,pathway_hetionet_id)
        # match_result=g.run(query)
        # has_one_enty=match_result.evaluate()
        # if has_one_enty==None:
        #     print('no entry')
        #     print(gene_id,pathway_hetionet_id)

    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Take all gene-pathway relationships and generate csv and cypher file')

    take_all_relationships_of_gene_pathway()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
