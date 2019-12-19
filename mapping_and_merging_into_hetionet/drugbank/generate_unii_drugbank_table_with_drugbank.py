# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 13:05:35 2017

@author: Cassandra
"""
from py2neo import Graph
import datetime
import sys, csv


'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))

'''
generate af file with only drugbank and unii IDs
'''

def generate_tsv_file():
    # generate csv file
    file_map = open('data/map_unii_to_drugbank_id.tsv', 'w')
    csv_writer=csv.writer(file_map,delimiter='\t')
    csv_writer.writerow(['unii','drugbank_id','inchikey'])

    # query for getting the information
    query='''MATCH (n:Compound_DrugBank) RETURN n.identifier, n.unii, n.inchikey '''
    result=g.run(query)

    # run through the results and fill file
    for unii, identifier, inchikey, in result:
        csv_writer.writerow([unii,identifier, inchikey])

    # file map close
    file_map.close()



def main():

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all properties of compound and drugbank compound and use the information to genreate csv files')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
