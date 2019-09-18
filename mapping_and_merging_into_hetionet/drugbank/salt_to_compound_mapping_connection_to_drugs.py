# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 16:07:43 2019

@author: ckoenig
"""

from py2neo import Graph, authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# dictionary of not mapped compound
dict_not_mapped_compound={}

'''
Load all compounds which did not mapped and upload them into da dictionary
'''
def find_not_mapped_compounds_and_add_to_dict():
    query='''MATCH (n:Compound) WHere not exists(n.drugbank) RETURN n'''
    result=g.run(query)
    for node, in result:
        id=node['identifier']
        dict_not_mapped_compound[id]=dict(node)

'''
Create cypher and csv files for nodes and relationships
'''
def create_cypher_and_csv_files():
    # get properties of salt nodes
    query='''MATCH (p:Salt_DrugBank) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    result=g.run(query)
    header=[]
    query_start=''''''
    for property, in result:
        header.append(property)

'''
Gather all salt and make a new csv to integrate them as compound into neo4j
also check if a salt is on of the not mapped compounds 
Prepare the csv for salt integration, because they are not in hetionet they can be directly integrated
also check on the drugs which did not mapped, because some of them might be now salts
'''
def prepare_node_csv():
    query='''MATCH (n:Salt_DrugBank) RETURN n'''
    result=g.run(query)

def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('get compound which are not ind drugbank drugs')

    find_not_mapped_compounds_and_add_to_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all hetionet compound in dictionary')

    load_all_hetionet_compound_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all DrugBank compounds in dictionary')

    load_all_DrugBank_compound_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all connection in dictionary')

    load_in_all_interaction_connection_from_drugbank_in_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('integrate drugbank into hetionet')

    integrate_DB_compound_information_into_hetionet()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('create cypher queries and cypher file')

    create_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('generate cypher file for interaction')

    genration_of_interaction_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()