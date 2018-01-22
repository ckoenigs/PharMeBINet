# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:46:22 2018

@author: Cassandra
"""

import sys
import datetime
from itertools import groupby


# EFO:0000408 ist disease

# use to delimit between the blocks
def is_data(line):
    return True if line.strip() else False


# file path to HPO data source
file_name = 'efo.obo'

# dictionary with hierarchical upper identifier and all of the leafs
dict_hierarchical_set = {}

# dictionary with all efo identifier and a dictionary for all information of this identifier
dict_all_efo_entries = {}

'''
group the epo terms together and get the information from the different terms and gather all term information in a dictionary
further fill the dictionary for the hierachical set
'''


def get_efo_information_and_map_to_umls():
    # counter of queries
    counter_create = 0

    global cypher_file
    global file_counter
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
                        parent_id = value.split('!')[0].strip()

                        if parent_id in dict_hierarchical_set:
                            dict_hierarchical_set[parent_id].add(dict_all_info['id'][0])
                        else:
                            dict_hierarchical_set[parent_id] = set([dict_all_info['id'][0]])

                    # for som properties more than one value appears
                    if not key_term in dict_all_info:
                        dict_all_info[key_term] = [value]
                    else:
                        dict_all_info[key_term].append(value)

                dict_all_efo_entries[dict_all_info['id'][0]] = dict_all_info


'''
complete the leaves of the  with recursion
'''


def get_all_leaves_and_internal_nodes(node_id):
    all_nodes = dict_hierarchical_set[node_id]
    for node in all_nodes:
        if node in dict_hierarchical_set:
            dict_hierarchical_set[node_id] = dict_hierarchical_set[node_id].union(
                get_all_leaves_and_internal_nodes(node))
    return dict_hierarchical_set[node_id]

    #                    print(key_term)
    #                    print(value)


#                # only for useful hpo ids
#                if use_full_hpo_id:
#                    if not is_a_frequency_information:
#                        create_text = 'Create (:HPOsymptom{'
#                        # add all properties to node which hpo has
#                        for key, list_information in dict_all_info.items():
#                            modify_list_informationan = []
#                            for info in list_information:
#                                info = info.replace('"', '').replace("'", "").replace("\\", "")
#                                modify_list_informationan.append(info)
#                            create_text = create_text + key + ": '" + "|".join(modify_list_informationan) + "' ,"
#                        create_text = create_text[0:-1] + '});\n'
#                        counter_create += 1
#                        cypher_file.write(create_text)
#                        # test if a new commit block or new file need to be generated
#                        if counter_create % constrain_number == 0:
#                            cypher_file.write('commit \n')
#                            if counter_create % creation_max_in_file == 0:
#                                cypher_file.close()
#                                cypher_file = open('integrate_hpo_into_neo4j_' + str(file_counter) + '.cypher', 'w')
#                                cypher_file.write('begin \n')
#                                file_counter += 1
#                            else:
#                                cypher_file.write('begin \n')
#                    else:
#                        identifier = dict_all_info['id'][0]
#                        name = dict_all_info['name'][0]
#                        definition = dict_all_info['def'][0]
#                        dict_hpo_frequency[identifier] = [name, definition]
#    print(counter_create)
#    cypher_file.write('commit \n begin \n')
#    cypher_file.write('Create Constraint On (node:HPOsymptom) Assert node.id Is Unique; \n')
#    cypher_file.write('commit \n begin \n')


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################hierachical################')

    print(datetime.datetime.utcnow())
    print('gather symptoms information ')

    get_efo_information_and_map_to_umls()

    print(dict_hierarchical_set['EFO:0000408'])
    print(len(list(dict_hierarchical_set['EFO:0000408'])))

    print('##########################################################################')

    get_all_leaves_and_internal_nodes('EFO:0000408')

    print(dict_hierarchical_set['EFO:0000408'])
    print(len(list(dict_hierarchical_set['EFO:0000408'])))
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship information into a cypher file')

    #    add_connection_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
