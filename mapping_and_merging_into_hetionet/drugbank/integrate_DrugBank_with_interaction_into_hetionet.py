# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 16:07:43 2018

@author: ckoenig
"""

'''integrate the other diseases and relationships from disease ontology in hetionet'''
from py2neo import Graph, authenticate
import datetime
import sys

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# dictionary of all compounds with key the drugbank id and list of url, name, inchi, inchikey, food interaction
dict_compunds = {}

# list drugbank ids of all compounds which are already in Hetionet in hetionet
list_compounds_in_hetionet = []

'''
load all disease in the dictionary
has propeteries:
name 
identifier
source
license
url
'''


def load_all_hetionet_disease_in_dictionary():
    query = '''Match (n:Compound) RETURN n '''
    results = g.run(query)
    for compound, in results:
        list_compounds_in_hetionet.append(compound['identifier'])
        dict_compunds[compound['identifier']] = []
    print('size of diseases before the rest of disease ontology was add: ' + str(len(dict_compunds)))




def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all hetionet diseases in dictionary')

    load_all_hetionet_disease_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all disease ontology diseases in dictionary')

    load_disease_ontologie_in_hetionet()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all connection in dictionary')

    load_in_all_connection_from_diesease_ontology()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('integrate disease ontology into hetionet')

    integrate_DO_information_into_hetionet()

    print(
        '#################################################################################################################################################################')
    print(len(dict_diseases_in_hetionet))

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()