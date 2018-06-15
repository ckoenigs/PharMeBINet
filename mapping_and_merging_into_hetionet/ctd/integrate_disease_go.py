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
    # authenticate("localhost:7474", "neo4j", "test")
    # global g
    # g = Graph("http://localhost:7474/db/data/")

    authenticate("bimi:7475", "ckoenigs", "test")
    global g
    g = Graph("http://bimi:7475/db/data/",bolt=False)


# dictionary with all pairs and properties as value
dict_gene_go = {}

# csv files for bp. mf, cc
bp_file = open('disease_go/bp.csv', 'w')
bp_writer = csv.writer(bp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
bp_writer.writerow(['DiseaseID', 'GOID', 'inferenceGeneQty', 'inferenceGeneSymbols'])

mf_file = open('disease_go/mf.csv', 'w')
mf_writer = csv.writer(mf_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
mf_writer.writerow(['DiseaseID', 'GOID', 'inferenceGeneQty', 'inferenceGeneSymbols'])

cc_file = open('disease_go/cc.csv', 'w')
cc_writer = csv.writer(cc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
cc_writer.writerow(['DiseaseID', 'GOID', 'inferenceGeneQty', 'inferenceGeneSymbols'])

# dictionary with for biological_process, cellular_component, molecular_function the right file
dict_processe = {
    "Biological Process": bp_writer,
    "Molecular Function": mf_writer,
    "Cellular Component": cc_writer
}

# dictionary counter for bp, cc, mf
dict_processe_counter = {
    "Biological Process": 0,
    "Molecular Function": 0,
    "Cellular Component": 0
}

'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_disease_go():
    query = '''MATCH (disease)-[r:affects_DGO]->(go:CTDGO)  RETURN disease.mondos, r, go.go_id, go.ontology '''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    for disease_mondos, rela, go_id, ontology in results:
        rela = dict(rela)
        inferenceGeneQty = rela['inferenceGeneQty'] if 'inferenceGeneQty' in rela else ''
        inferenceGeneSymbols = rela['inferenceGeneSymbols'] if 'inferenceGeneSymbols' in rela else ''
        for mondo in disease_mondos:
            if not (mondo, go_id) in dict_gene_go:
                dict_gene_go[(mondo, go_id)] = [[inferenceGeneQty], [inferenceGeneSymbols], [ontology]]
                dict_processe_counter[ontology] += 1

                count_possible_relas += 1
            else:
                count_multiple_pathways += 1
                dict_gene_go[(mondo, go_id)][0].append(inferenceGeneQty)
                dict_gene_go[(mondo, go_id)][1].append(inferenceGeneSymbols)
                dict_gene_go[(mondo, go_id)][2].append(ontology)
                list_rela=list(set(dict_gene_go[(mondo, go_id)][2]))
                if len(list_rela)>1:
                    print(mondo, go_id)
                    print(list_rela)
        if count_possible_relas % 1000 == 0:
            print(count_possible_relas)

    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))
    print(dict_processe_counter)


'''
Generate the csv and cypher file
'''


def generate_csv_and_cypher_file():
    # generate cypher file
    cypherfile = open('disease_go/cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/disease_go/bp.csv" As line Match (n:Disease{identifier:line.DiseaseID}), (b:BiologicalProcess{identifier:line.GOID}) Merge (n)-[r:ASSOCIATES_DaBP]->(b) On Create Set r.hetionet='no', r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/disease_go/mf.csv" As line Match (n:Disease{identifier:line.DiseaseID}), (b:MolecularFunction{identifier:line.GOID}) Merge (n)-[r:ASSOCIATES_DaMF]->(b) On Create Set r.hetionet='no', r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/disease_go/cc.csv" As line Match (n:Disease{identifier:line.DiseaseID}), (b:CellularComponent{identifier:line.GOID}) Merge (n)-[r:ASSOCIATES_DaCC]->(b) On Create Set r.hetionet='no', r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID;\n '''
    cypherfile.write(query)

    for (mondo, go_id), [inferenceGeneQty, inferenceGeneSymbols, ontology] in dict_gene_go.items():
        writer = dict_processe[ontology]
        writer.writerow([mondo, go_id, inferenceGeneQty, inferenceGeneSymbols])


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Take all disease-go relationships and generate csv files and cypher file')

    take_all_relationships_of_disease_go()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
