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
dict_disease_pathway = {}

'''
get all relationships between gene and pathway, take the hetionet identifier and gaather all information in a dictionary 
'''


def take_all_relationships_of_gene_disease():
   

    query = '''MATCH (disease)-[r:associates_DP]->(pathway) RETURN pathway.hetionet_id, r, disease.mondos '''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    counter_all=0
    for pathway_id, rela, disease_mondos, in results:
        counter_all+=1
        rela = dict(rela)
        inferenceGeneSymbol = rela['inferenceGeneSymbol'] if 'inferenceGeneSymbol' in rela else ''
        for mondo in disease_mondos:

            if not (pathway_id, mondo) in dict_disease_pathway:
                dict_disease_pathway[(pathway_id, mondo)] = [inferenceGeneSymbol]
                
                count_possible_relas += 1
            else:
                count_multiple_pathways += 1
                dict_disease_pathway[(pathway_id, mondo)].append(inferenceGeneSymbol)
        if count_possible_relas%1000==0:
            print(count_possible_relas)

    print(counter_all)
    print('number of new rela:'+str(count_possible_relas))
    print('number of relationships which appears multiple time:'+str(count_multiple_pathways))



'''
Generate the csv and cypher file
'''


def generate_csv_and_cypher_file():
    # generate cypher file
    cypherfile = open('disease_pathway/cypher.cypher', 'w')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/disease_pathway/relationships.csv" As line Match (n:Pathway{identifier:line.PathwayID}), (b:Disease{identifier:line.DiseaseID}) Merge (b)-[r:ASSOCIATES_DaP]->(n) On Create Set r.hetionet='no', r.inferenceGeneSymbol=split(line.inferenceGeneSymbol,'|') , r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID, r.inferenceGeneSymbol=split(line.inferenceGeneSymbol,'|') ;\n '''
    cypherfile.write(query)

    csvfile = open('disease_pathway/relationships.csv', 'wb')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['PathwayID', 'DiseaseID', 'inferenceGeneSymbol'])

    for (pathway_id, mondo), inferenceGeneSymbols in dict_disease_pathway.items():
        inferenceGeneSymbol='|'.join(inferenceGeneSymbols)
        writer.writerow([pathway_id, mondo, inferenceGeneSymbol])
        


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Take all gene-pathway relationships and generate csv and cypher file')

    take_all_relationships_of_gene_disease()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('generate csv and cypher file')

    generate_csv_and_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
