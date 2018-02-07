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
import types


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with label as key and value is the constraint property
dict_label_to_unique_prop = {}

'''
Get for all label the unique property, after a : is the label and after a . is the property
'''


def generate_dictionary_for_labels():
    query = '''CALL db.constraints'''
    results = g.run(query)
    for constraint_string, in results:
        print(constraint_string)
        label = constraint_string.split(':')[1].split(' )')[0]
        unique_property = constraint_string.split('.')[1].split(' ')[0]
        dict_label_to_unique_prop[label] = unique_property
    print(dict_label_to_unique_prop)


# list from the specific node to the other with (rela_type,dict_rela,node_labels,dict_node)
list_node_to_other = []

# list from  the other with to the specific node  (rela_type,dict_rela,node_labels,dict_node)
list_other_to_node = []

'''
The DB13390 is revoked but DB06723 has this as ingredient and fit for the mapping of NDF-RT
So first get all edges and nodes with type
'''


def get_the_information_and_the_direction(identifier, label):
    query = '''Match (c:%s{identifier:"%s"})-[r]->(a) Return Type(r), r, labels(a), a '''
    query = query % (label, identifier)
    print(query)
    results = g.run(query)
    for rela_type, rela, node_labels, node, in results:
        dict_rela = {}
        for key, property in dict(rela).items():
            dict_rela[key] = property
        dict_node = {}
        for key, property in dict(node).items():
            dict_node[key] = property

        list_node_to_other.append([rela_type, dict_rela, node_labels, node])

    query = '''Match (c:%s{identifier:"%s"})<-[r]-(a) Return Type(r), r, labels(a), a '''
    query = query % (label, identifier)
    print(query)
    results = g.run(query)
    for rela_type, rela, node_labels, node, in results:
        dict_rela = {}
        for key, property in dict(rela).items():
            dict_rela[key] = property
        dict_node = {}
        for key, property in dict(node).items():
            dict_node[key] = property

        list_other_to_node.append([rela_type, dict_rela, node_labels, node])


'''
The node that get the information 
'''


def add_this_information_to_the_merged_node(identifier, label):
    count_new_relationships_from_this_node = 0
    for [rela_type, dict_rela, node_labels, node] in list_node_to_other:
        query = ''' Match (a:%s{identifier:"%s"}), (b:%s{%s:"%s"})
         Create (a)-[r:%s{ '''
        query = query % (label, identifier, node_labels[0], dict_label_to_unique_prop[node_labels[0]],
                         node[dict_label_to_unique_prop[node_labels[0]]], rela_type)

        for key, property in dict_rela.items():
            if type(property) != list:
                query = query + '''%s:"%s",'''
                query = query % (key, property)
            else:
                query = query + '''%s:%s,'''
                query = query % (key, property)

        query = query[0:-1] + '''}]->(b)'''
        print(query)
        count_new_relationships_from_this_node += 1
        g.run(query)

    count_new_relationships_to_this_node = 0
    for [rela_type, dict_rela, node_labels, node] in list_other_to_node:
        query = ''' Match (a:%s{identifier:"%s"}), (b:%s{identifier:"%s"})
         Create (a)<-[r:%s {'''
        query = query % (label, identifier, node_labels[0], node[dict_label_to_unique_prop[label]], rela_type)
        for key, property in dict_rela.items():
            if type(property) != list:
                query = query + '''%s:"%s",'''
                query = query % (key, property)
            else:
                query = query + '''%s:%s,'''
                query = query % (key, property)

        query = query[0:-1] + '''}]-(b)'''
        print(query)
        g.run(query)
        count_new_relationships_to_this_node += 1

    print('number of new relationships from this merged node:' + str(count_new_relationships_from_this_node))
    print('number of new relationships to this merged node:' + str(count_new_relationships_to_this_node))


'''
delete the merged node
'''


def delete_merged_node(identifier, label):
    query = ''' Match (n:%s{identifier:"%s"}) Detach Delete n'''
    query = query % (label, identifier)
    # g.run(query)


'''
function that start the right programs in the right order to merge information from one node to another
'''


def merge_information_from_one_node_to_another(delete_node_id, merged_node_id, node_label):
    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate dictionary for labels with unique property ')

    generate_dictionary_for_labels()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all information for the node that is merged into another node ')

    get_the_information_and_the_direction(delete_node_id, node_label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate this into Hetionet')

    add_this_information_to_the_merged_node(merged_node_id, node_label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete merged node')

    delete_merged_node(delete_node_id, node_label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate dictionary for labels with unique property ')

    generate_dictionary_for_labels()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all information for the node that is merged into another node ')

    get_the_information_and_the_direction('DB13390', 'Compound')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate this into Hetionet')

    add_this_information_to_the_merged_node('DB06723', 'Compound')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete merged node')

    delete_merged_node('DB13390', 'Compound')

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()