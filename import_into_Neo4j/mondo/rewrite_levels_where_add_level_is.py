# -*- coding: utf-8 -*-
"""
Created on Mon Mai 14 07:23:43 2018
@author: ckoenigs
"""

from py2neo import Graph#, authenticate
import datetime
import string
import sys
import csv

reload(sys)
sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))

'''
add new levels and also check if the nodes has other parent than the add onw
'''
def add_level_to_childs(parent_node_id, dict_child_node, add_level_list, add_number):
    # has all element for this function value parent_node and value new dict_child nodes
    dict_level_childs={}
    print(add_level_list)
    add_level_list_new = [str(int(x)+1) for x in add_level_list]
    for child_node, levels_child in dict_child_node.items():
        query = '''Match (d:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[:subClassOf]->(n:disease) Where not n.`http://www.geneontology.org/formats/oboInOwl#id`="%s"  Return n.level'''
        query = query % (child_node,parent_node_id)
        result = g.run(query)
        all_levels = []
        for levels, in result:
            print(levels)
            levels = [str(int(x)+1) for x in levels]
            all_levels.extend(levels)
        all_levels=set(all_levels)
        length_add_level = len(list(add_level_list))
        intersection = list(all_levels.intersection(add_level_list))
        if len(intersection) == length_add_level:
            print(child_node)
            print(all_levels)
            print(add_level_list)
            print('has all levels already')
            continue
        all_levels = list(all_levels.union(add_level_list))
        all_levels = '","'.join(all_levels)
        query = '''Match (d:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})<-[:subClassOf]-(n:disease) Set d.level=["%s"], d.level_add="%s"  Return n.`http://www.geneontology.org/formats/oboInOwl#id`, n.level'''
        query = query % (child_node, all_levels, add_number)
        print(query)
        their_are_childs = False

        results = g.run(query)
        dict_new_child_nodes = {}
        for new_child_node_id, new_child_node_level, in results:
            their_are_childs = True
            dict_new_child_nodes[new_child_node_id] = new_child_node_level

        if their_are_childs:
            dict_level_childs[child_node] = dict_new_child_nodes

    print('new level')
    for new_parent_node_id, new_dict_child_nodes in dict_level_childs.items():
        add_level_to_childs(new_parent_node_id,new_dict_child_nodes, add_level_list_new, add_number)





'''
go through all nodes with level_add as property and increase the level and go also down the tree
'''
def go_through_all_add_levels():
    # has all element for this function value parent_node and value new dict_child nodes
    dict_level_childs = {}
    # and n.`http://www.geneontology.org/formats/oboInOwl#id`='MONDO:0015447'
    query= '''MATCH (n:disease) Where exists(n.level_add)  RETURN n.`http://www.geneontology.org/formats/oboInOwl#id`, n.level, n.level_add'''
    results=g.run(query)
    for identifier, level, add_level in results:
        print(level)
        print(add_level)
        print(int(add_level))
        level=[str(int(x)+int(add_level)) for x in level]
        level_string='","'.join(level)
        query = '''Match (d:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})<-[:subClassOf]-(n:disease) Set d.level=["%s"]  Return n.`http://www.geneontology.org/formats/oboInOwl#id`, n.level'''
        query = query % (identifier, level_string)
        print(query)
        their_are_childs = False
        results = g.run(query)
        dict_child_nodes = {}
        for child_node_id, child_node_level, in results:
            their_are_childs = True
            dict_child_nodes[child_node_id] = child_node_level

        # add +1 for the next generation
        level=[str(int(x)+1) for x in level]
        if their_are_childs:
            dict_level_childs[identifier] = [dict_child_nodes,level,add_level]

    print('##########################################################################')
    print(datetime.datetime.utcnow())
    for parent_node_id, [dict_child_nodes,level,add_level] in dict_level_childs.items():
        print(parent_node_id)

        add_level_to_childs(parent_node_id,dict_child_nodes, level, add_level)
        print(datetime.datetime.utcnow())
        print('##########################################################################')





def main():
    print(datetime.datetime.utcnow())
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('find all nodes with level_add and add this to the level and do it also to all children')

    go_through_all_add_levels()


    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()