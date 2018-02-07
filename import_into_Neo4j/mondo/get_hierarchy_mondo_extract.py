# -*- coding: utf-8 -*-
"""
Created on Fri Feb 2 07:23:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import string
import sys
from ete3 import Tree


reload(sys)
sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# dictionary with all levels and two lists the first contains the class element and the second the leafs and each has a
# dict with parent id as key with id name and parent
dict_levels = {}


'''
generate for each level two files one with classes and one with elements from the node disease (MONDO:0000001)
'''


def generate_files():
    query_start = ''' Match (a:MonDOdisease)'''
    query_add_part = '''-[:is_a_mondo]->('''
    query_end_match = '''-[:is_a_mondo]->(b:MonDOdisease{id:'MONDO:0000001'}) Where '''
    query_where_level_element = '''not ()-[:is_a_mondo]->(a) Return a.id, a.name, '''
    query_where_level_class = ''' ()-[:is_a_mondo]->(a) Return a.id, a.name, '''
    count_level = 1
    letter_of_parent = 0
    while count_level <= 17:
        class_file = open('hierarchical_levels/level_' + str(count_level) + '_class.txt', 'w')
        class_file.write('MonDO_id \t MonDO_name \t parent_id \t parent_name \n')
        entry_file = open('hierarchical_levels/level_' + str(count_level) + '_entry.txt', 'w')
        entry_file.write('MonDO_id \t MonDO_name \t parent_id \t parent_name  \n')

        # key parent id and value parent name
        dict_parent = {}
        # key level value and value name
        dict_level = {}
        # key class and value list of parents
        dict_level_class_parent = {}
        # key entry and value list of parents
        dict_level_entries_parent = {}

        if count_level != 1:
            query_start = query_start + query_add_part + string.ascii_lowercase[count_level] + ')'
            query_level_class = query_start + query_end_match + query_where_level_class + string.ascii_lowercase[
                letter_of_parent] + '.id, ' + string.ascii_lowercase[letter_of_parent] + '.name '
            query_level_element = query_start + query_end_match + query_where_level_element + string.ascii_lowercase[
                letter_of_parent] + '.id, ' + string.ascii_lowercase[letter_of_parent] + '.name '

        else:
            letter_of_parent = count_level + 1
            query_level_class = query_start + query_end_match + query_where_level_class + string.ascii_lowercase[
                letter_of_parent - 1] + '.id, ' + string.ascii_lowercase[letter_of_parent - 1] + '.name '
            query_level_element = query_start + query_end_match + query_where_level_element + string.ascii_lowercase[
                letter_of_parent - 1] + '.id, ' + string.ascii_lowercase[letter_of_parent - 1] + '.name '

        dict_levels[count_level] = []

        dict_class_entry = {}
        results_classes = g.run(query_level_class)
        # collect the information for classes
        for id, name, parent_id, parent_name, in results_classes:
            if parent_id not in dict_class_entry:
                dict_class_entry[parent_id] = [[id, name, parent_id]]
            else:
                dict_class_entry[parent_id].append([id, name, parent_id])

            if id not in dict_level:
                dict_level[id] = name
                dict_level_class_parent[id] = set([parent_id])
            else:
                dict_level_class_parent[id].add(parent_id)
            if parent_id not in dict_parent:
                dict_parent[parent_id] = parent_name

        dict_levels[count_level].append(dict_class_entry)

        # integrate the information into a file
        for id, set_of_parent_ids in dict_level_class_parent.items():
            name = dict_level[id]
            parent_ids = list(set_of_parent_ids)
            parent_ids_string = '|'.join(parent_ids)
            name_parent_string = ''
            for parent_id in parent_ids:
                name_parent_string = name_parent_string + dict_parent[parent_id] + '|'
            class_file.write(id + '\t' + name + '\t' + parent_ids_string + '\t' + name_parent_string[0:-1] + '\n')
        class_file.close()

        print(query_level_element)
        dict_class_entry = {}
        results_elements = g.run(query_level_element)
        # collect the information for entities
        for id, name, parent_id, parent_name, in results_elements:
            if parent_id not in dict_class_entry:
                dict_class_entry[parent_id] = [[id, name, parent_id]]
            else:
                dict_class_entry[parent_id].append([id, name, parent_id])

            if id not in dict_level:
                dict_level[id] = name
                dict_level_entries_parent[id] = set([parent_id])
            else:
                dict_level_entries_parent[id].add(parent_id)
            if parent_id not in dict_parent:
                dict_parent[parent_id] = parent_name

        dict_levels[count_level].append(dict_class_entry)

        # integrate the information into a file
        for id, set_of_parent_ids in dict_level_entries_parent.items():
            name = dict_level[id]
            parent_ids = list(set_of_parent_ids)
            parent_ids_string = '|'.join(parent_ids)
            name_parent_string = ''
            for parent_id in parent_ids:
                name_parent_string = name_parent_string + dict_parent[parent_id] + '|'
            entry_file.write(id + '\t' + name + '\t' + parent_ids_string + '\t' + name_parent_string[0:-1] + '\n')

        entry_file.close()
        print(datetime.datetime.utcnow())
        print(count_level)
        count_level += 1


'''
recursive get the tree structure
'''


def recursion_tree_generation(parent_id, count_level):
    part_tree_string = ''
    # if count_level in dict_levels:
    if count_level < 3:
        # if parent_id in dict_levels[count_level][1]:
        #     for [id, name, parent] in dict_levels[count_level][1][parent_id]:
        #         part_tree_string = part_tree_string  + name.replace('(','').replace(')','').replace(';',' ').replace(':','').replace(',','') + "-" + id.replace(':','_') + ","

        if parent_id in dict_levels[count_level][0]:
            for [id, name, parent] in dict_levels[count_level][0][parent_id]:

                part_tree_string = part_tree_string + recursion_tree_generation(id,
                                                                                      count_level + 1)  + name.replace('(','').replace(')','').replace(';',' ').replace(':','').replace(',','') + "-" + id.replace(':','_') + ","
        if len(part_tree_string)>0:
            part_tree_string="("+part_tree_string[0:-1]+")"

    return part_tree_string


'''
generate tree 
'''


def generate_tree():
    count_level = 1
    datatree = recursion_tree_generation("MONDO:0000001", count_level) + "disease-MONDO_0000001;"
    print(datatree)

    rooted_tree = Tree(datatree, format=8)
    print rooted_tree.get_ascii(show_internal=True)

def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    generate_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    generate_tree()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
