# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:49:17 2018

@author: Cassandra
"""
from py2neo import Graph, authenticate
import datetime
import sys
from itertools import groupby


# use to delimit between the blocks
def is_data(line):
    return True if line.strip() else False


# file path to MonDO data source
file_name = 'mondo.obo'

# dict of all is_a relationships wit tuple (parent,child) and value is the resource
dict_of_all_is_a_relationship = {}

# dictionary with all mondo identifier and a dictionary for all information of this identifier
dict_all_mondo_entries = {}

'''
group the mondo terms together and get the information from the different terms and gather all term information in a dictionary
further fill the dictionary for the hierarchical set
'''


def get_mondo_information_and_map_to_umls():
    with open(file_name) as f:
        for (key, group) in groupby(f, is_data):
            #            print(key)
            if key:
                # for python 2.*
                header = group.next().rstrip('\n')
                # for python 3.*
                #                print(group.__next__())
                # header = group.__next__().rstrip('\n')

                if header.find('[Term]') == -1:
                    continue

                # dictionary for all values
                dict_all_info = {}
                # go through all properties of the hpo id
                for info in group:
                    (key_term, value) = [element.strip() for element in info.split(":", 1)]
                    # check if the id is part of at least one relationship
                    #                    if key_term == 'id':
                    #                        if (not value in list_symptoms_ids) and (not value in dict_hpo_frequency):
                    #                            use_full_hpo_id = False
                    #                            break
                    #                        elif value in dict_hpo_frequency:
                    #                            is_a_frequency_information = True
                    if key_term == 'is_a':
                        parent_id = value.split('!')[0].split(' ')[0]

                        if (parent_id, dict_all_info['id'][0]) not in dict_of_all_is_a_relationship:
                            dict_of_all_is_a_relationship[(parent_id, dict_all_info['id'][0])] = \
                            value.split('!')[0].split(' ')[1]

                    # for som properties more than one value appears
                    if not key_term in dict_all_info:
                        dict_all_info[key_term] = [value]
                    else:
                        dict_all_info[key_term].append(value)

                dict_all_mondo_entries[dict_all_info['id'][0]] = dict_all_info


# file counter
file_counter = 1
# maximal number of queries for a commit block
constrain_number = 20000
# maximal number of queries in a file
creation_max_in_file = 1000000

'''
generate cypher file
'''


def generate_cypher_file():
    global file_counter
    counter_create = 0

    #
    cypher_file = open('integrate_mondo_disease_into_neo4j_' + str(file_counter) + '.cypher', 'w')
    file_counter += 1
    cypher_file.write('begin \n')
    for identifier, dict_information in dict_all_mondo_entries.items():
        create_text = 'Create (:MonDOdisease{'
        # add all properties to node which hpo has
        for key, list_information in dict_information.items():
            modify_list_information = []
            for info in list_information:
                info = info.replace('"', '').replace("'", "").replace("\\", "")
                modify_list_information.append(info)
            create_text = create_text + key + ": '" + "|".join(modify_list_information) + "' ,"
        create_text = create_text + 'license:"CC BY 4.0"});\n'
        counter_create += 1
        cypher_file.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            cypher_file.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                cypher_file.close()
                cypher_file = open('integrate_mondo_disease_into_neo4j_' + str(file_counter) + '.cypher', 'w')
                cypher_file.write('begin \n')
                file_counter += 1
            else:
                cypher_file.write('begin \n')
    print('number of nodes:' + str(counter_create))
    number_of_nodes = counter_create
    cypher_file.write('commit \n begin \n')
    cypher_file.write('Create Constraint On (node:MonDOdisease) Assert node.id Is Unique; \n')
    cypher_file.write('commit \n begin \n')

    for (parent_id, child_id), source in dict_of_all_is_a_relationship.items():
        query = ''' Match (a:MonDOdisease{id:"%s"}), (b:MonDOdisease{id:"%s"}) 
         Create (a)-[:is_a_mondo{source:'%s'}]->(b); \n'''
        query = query % (child_id, parent_id, source)
        counter_create += 1
        cypher_file.write(query)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            cypher_file.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                cypher_file.close()
                cypher_file = open('integrate_mondo_disease_into_neo4j_' + str(file_counter) + '.cypher', 'w')
                cypher_file.write('begin \n')
                file_counter += 1
            else:
                cypher_file.write('begin \n')
    cypher_file.write('commit')
    print(counter_create)
    print('number of relationships:' + str(counter_create - number_of_nodes))


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################hierachical################')

    print(datetime.datetime.utcnow())
    print('gather MonDO information ')

    get_mondo_information_and_map_to_umls()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all nodes and relationship information into a cypher file')

    generate_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
