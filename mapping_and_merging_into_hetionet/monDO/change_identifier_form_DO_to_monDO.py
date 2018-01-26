# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
import threading


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary external ids to monDO id
dict_external_ids_monDO = {}

'''
Load MonDO disease in dictionary
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:MonDOdisease) RETURN n Limit 10'''
    results = g.run(query)
    for disease, in results:
        monDo_id = disease['id']
        xrefs = disease['xref'] if 'xref' in disease else ''
        for external_id in xrefs.split('|'):
            external_id = external_id.split(' ')[0]
            if external_id in dict_external_ids_monDO:
                dict_external_ids_monDO[external_id].append(monDo_id)
            else:
                dict_external_ids_monDO[external_id]=[monDo_id]


# dictionary disease ontology to external ids
dict_DO_to_xref={}
'''
Load in all disease ontology ids with external identifier and alternative id
'''
def load_in_all_DO_in_dictionary():
    query = ''' MATCH (n:Disease) RETURN n Limit 10'''
    results = g.run(query)
    for disease, in results:
        Do_id = disease['identifier']
        alternative_id= [disease['identifier']]
        xrefs = disease['xref'] if 'xref' in disease else []
        print(alternative_id)
        alternative_id=alternative_id.extend(xrefs)
        dict_DO_to_xref[Do_id]=alternative_id
    print(dict_DO_to_xref)



def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in DO diseases ')

    load_in_all_DO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
