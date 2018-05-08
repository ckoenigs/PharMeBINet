# -*- coding: utf-8 -*-
"""
Created on Fri Feb 2 07:23:43 2018
@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import string
import sys
import csv
from ete3 import Tree

reload(sys)
sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


'''
First prepare mondo-disease, because some has multiple subClassOf from the different  source and this information are 
combined in one relationship
'''


def prepare_subClassOf_relationships():
    # get all nodes with multiple subClassOf relationship
    query = '''Match p=(a:disease)-[r:subClassOf]->(b:disease) With a,b,type(r) as t, count(r) as coun Where coun >1 Return a.`http://www.geneontology.org/formats/oboInOwl#id` ,b.`http://www.geneontology.org/formats/oboInOwl#id` '''
    result = g.run(query)

    #count the pairs of multiple subClass relationships
    counter_pairs_with_multiple_sub_class_rela=0
    for mondo_id_a, mondo_id_b, in result:
        counter_pairs_with_multiple_sub_class_rela+=1
        query = '''Match p=(a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[r:subClassOf]->(b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:'%s'}) Return r '''
        query= query %(mondo_id_a,mondo_id_b)
        defined = 'http://purl.obolibrary.org/obo/upheno/monarch.owl'
        result = g.run(query)

        dict_orginal_source_target = []

        number_rela=0
        for rela, in result:
            number_rela+=1
            original_source = rela['equivalentOriginalNodeSource'] if 'equivalentOriginalNodeSource' in rela else ''
            original_target = rela['equivalentOriginalNodeTarget'] if 'equivalentOriginalNodeTarget' in rela else ''
            combined = '(' + original_source + ',' + original_target + ')'
            dict_orginal_source_target.append(combined)
            if rela['isDefinedBy'] != defined:
                print(rela['isDefinedBy'])
                break

        # print(datetime.datetime.utcnow())
        # print(mondo_id_a, mondo_id_b)
        query = '''Match (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[r:subClassOf]->(b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:'%s'}) Delete r '''
        query= query%(mondo_id_a,mondo_id_b)
        g.run(query)
        query = '''Match (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"}),(b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:'%s'}) Create (a)-[:subClassOf{lbl:'%s', isDefinedBy:"%s", equivalentOriginalNodeSourceTarget:["%s"]  }]->(b)  '''
        query = query % (mondo_id_a, mondo_id_b, rela['lbl'], rela['isDefinedBy'], '","'.join(dict_orginal_source_target))

        g.run(query)
        if counter_pairs_with_multiple_sub_class_rela % 1000==0:
            print(counter_pairs_with_multiple_sub_class_rela)
            print(datetime.datetime.utcnow())
    print('total number of pairs with multiple connection:'+str(counter_pairs_with_multiple_sub_class_rela))


# dictionary with all levels and two lists the first contains the class element and the second the leafs and each has a
# dict with parent id as key with id name and parent
dict_levels = {}

# dictionary with disease as id and list of levels
dict_disease_levels = {}

'''
generate for each level two files one with classes and one with elements from the node disease (MONDO:0000001)
'''


def generate_files():
    query_start = ''' Match (a:disease)'''
    query_add_part = '''-[:subClassOf]->('''
    query_end_match = '''-[:subClassOf]->(b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:'MONDO:0000001'}) Where '''
    query_where_level_element = '''not ()-[:subClassOf]->(a) Return a.`http://www.geneontology.org/formats/oboInOwl#id`, a.label, '''
    query_where_level_class = ''' ()-[:subClassOf]->(a) Return a.`http://www.geneontology.org/formats/oboInOwl#id`, a.label, '''
    count_level = 1
    letter_of_parent = 0

    while count_level <= 25:
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
                letter_of_parent] + '.`http://www.geneontology.org/formats/oboInOwl#id`, ' + string.ascii_lowercase[
                                    letter_of_parent] + '.label '
            query_level_element = query_start + query_end_match + query_where_level_element + string.ascii_lowercase[
                letter_of_parent] + '.`http://www.geneontology.org/formats/oboInOwl#id`, ' + string.ascii_lowercase[
                                      letter_of_parent] + '.label '

        else:
            letter_of_parent = count_level + 1
            query_level_class = query_start + query_end_match + query_where_level_class + string.ascii_lowercase[
                letter_of_parent - 1] + '.`http://www.geneontology.org/formats/oboInOwl#id`, ' + string.ascii_lowercase[
                                    letter_of_parent - 1] + '.label '
            query_level_element = query_start + query_end_match + query_where_level_element + string.ascii_lowercase[
                letter_of_parent - 1] + '.`http://www.geneontology.org/formats/oboInOwl#id`, ' + string.ascii_lowercase[
                                      letter_of_parent - 1] + '.label '

        dict_levels[count_level] = []

        dict_class_entry = {}
        results_classes = g.run(query_level_class)
        # collect the information for classes
        for id, name, parent_id, parent_name, in results_classes:
            if parent_id not in dict_class_entry:
                dict_class_entry[parent_id] = {id: [name, parent_id]}
            else:
                dict_class_entry[parent_id][id]=[ name, parent_id]

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

            if id not in dict_disease_levels:
                dict_disease_levels[id] = set([count_level])
            else:
                dict_disease_levels[id].add(count_level)
                # print(id, dict_disease_levels[id])

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
                dict_class_entry[parent_id] = {id: [name, parent_id]}
            else:
                dict_class_entry[parent_id][id]=[ name, parent_id]

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

            if id not in dict_disease_levels:
                dict_disease_levels[id] = set([count_level])
            else:
                dict_disease_levels[id].add(count_level)
                # print(id, dict_disease_levels[id])

            for parent_id in parent_ids:
                name_parent_string = name_parent_string + dict_parent[parent_id] + '|'
            entry_file.write(id + '\t' + name + '\t' + parent_ids_string + '\t' + name_parent_string[0:-1] + '\n')

        entry_file.close()
        print(datetime.datetime.utcnow())
        print(count_level)
        count_level += 1


'''
generate cypher file for integration of levels in nodes
'''


def generate_cypher_file():
    cypher_file_to_integrate_level = open('integrate_level.cypher', 'w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/mondo/levels.csv" As line Match (n:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.ID}) Set n.level=split(line.level,'|');\n'''
    cypher_file_to_integrate_level.write(query)
    with open('levels.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ID', 'level'])
        for id, levels in dict_disease_levels.items():
            writer.writerow([id, '|'.join(map(str, list(levels)))])
            # query = ''' MATCH (n:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})
            #                         Set n.level=[%s]; \n'''
            # query = query % (id, ','.join(map(str, list(levels))))
            # cypher_file_to_integrate_level.write(query)
    #cypher_file_to_integrate_level.write('commit')


'''
recursive get the tree structure
'''


def recursion_tree_generation(parent_id, count_level, maximal_level, with_leaves):
    part_tree_string = ''
    if count_level <= maximal_level:
        if parent_id in dict_levels[count_level][1] and with_leaves:
            for id, [name, parent] in dict_levels[count_level][1][parent_id].items():
                part_tree_string = part_tree_string + id.replace(':', '_') + "-" + str(
                    count_level) + '-' + name.replace('(',
                                                      '').replace(
                    ')', '').replace(';', ' ').replace(
                    ':', '').replace(',', '')[0:20] + "-" + ","

        if parent_id in dict_levels[count_level][0]:
            for id, [name, parent] in dict_levels[count_level][0][parent_id].items():
                part_tree_string = part_tree_string + recursion_tree_generation(id,
                                                                                count_level + 1,
                                                                                maximal_level,
                                                                                with_leaves) + "-" + id.replace(':',
                                                                                                                '_') + "-" + str(
                    count_level) + '-' + name.replace('(',
                                                      '').replace(
                    ')', '').replace(';', ' ').replace(':', '').replace(',', '')[0:20] + ","
        if len(part_tree_string) > 0:
            part_tree_string = "(" + part_tree_string[0:-1] + ")"

    return part_tree_string


''' generate part tree for given parent'''


def generate_part_tree(parent_id, name):
    datatree = "("
    levels = dict_disease_levels[parent_id]
    for tree_level in list(levels):
        datatree += recursion_tree_generation(parent_id, tree_level + 1, len(dict_levels), True)
    datatree += ")" + parent_id.replace(':', '_') + "-" + '_'.join(map(str, levels))+"-" + name  + ";"
    rooted_tree = Tree(datatree, format=8)
    print rooted_tree.get_ascii(show_internal=True)


'''
generate tree 
'''


def generate_tree():
    count_level = 1
    datatree = recursion_tree_generation("MONDO:0000001", count_level, 2, False) + "disease-MONDO_0000001;"
    # print(datatree)

    rooted_tree = Tree(datatree, format=8)
    print rooted_tree.get_ascii(show_internal=True)

    asthma_id = 'MONDO:0004979'
    # datatree_asthma="("
    # levels=dict_disease_levels[asthma_id]
    # for tree_level in list(levels):
    #     datatree_asthma+= recursion_tree_generation(asthma_id, tree_level+1, len(dict_levels))
    # datatree_asthma+=")Asthma-"+asthma_id.replace(':','_')+";"
    # rooted_tree=Tree(datatree_asthma, format=8)
    # print rooted_tree.get_ascii(show_internal=True)

    # generate_part_tree(asthma_id, 'Asthma')
    print(dict_levels[7][1]['MONDO:0018956'])

    generate_part_tree('MONDO:0001358', 'bronchial disease')

    hypotension_id = 'MONDO:0005044'
    generate_part_tree(hypotension_id, 'Hypertension')


def main():
    print(datetime.datetime.utcnow())
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('prepare subClassOf relationships')

    prepare_subClassOf_relationships()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    generate_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate cypher file to integrate level into nodes')

    generate_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    # generate_tree()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()