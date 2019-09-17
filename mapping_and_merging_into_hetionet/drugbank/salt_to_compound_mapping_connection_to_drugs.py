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


'''
Load all compounds which did not mapped and upload them into da dictionary
'''


'''
Prepare the csv for salt integration, because they are not in hetionet they can be directly integrated
also check on the drugs which did not mapped, because some of them might be now salts
'''

def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all properties of compound and drugbank compound and use the information to genreate csv files')

    get_mondo_properties_and_generate_csv_files()

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