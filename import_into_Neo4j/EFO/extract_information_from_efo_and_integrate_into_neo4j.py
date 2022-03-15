# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:46:22 2018

@author: Cassandra
"""

import sys
import datetime,csv
from itertools import groupby


# EFO:0000408 ist disease

# use to delimit between the blocks
def is_data(line):
    return True if line.strip() else False


# file path to HPO data source
file_name = 'efo.obo'

# dictionary with all efo identifier and a dictionary for all information of this identifier
dict_all_efo_entries = {}

#all properties
set_all_properties_in_efo=set([])

#list of all properties which are lists
set_list_properties=set([])

#set list of all parent-child pairs
set_parent_child_pair=set([])

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

                #take only the information from the terms
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
                        set_parent_child_pair.add((parent_id,dict_all_info['id'][0]))

                    else:
                        # for som properties more than one value appears
                        if not key_term in dict_all_info:
                            dict_all_info[key_term] = value.replace('"', '').replace("'", "").replace("\\", "")
                        else:
                            dict_all_info[key_term]+='|'+value.replace('"', '').replace("'", "").replace("\\", "")
                            set_list_properties.add(key_term)
                        set_all_properties_in_efo.add(key_term)



                dict_all_efo_entries[dict_all_info['id'][0]] = dict_all_info


'''
generate cypher file
'''


def generate_cypher_file(all_child_of_disease):
    #create cypher file
    cypher_file=open('cypher.cypher','w')
    cypher_file.write('begin\n')
    query=''' Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/aeolus/node.csv" As line Create (:EFOdisease{'''
    for property in set_all_properties_in_efo:
        if not property in set_list_properties :
            query+=property+':line.'+property+', '
        else:
            query += property + ':split(line.' + property + ',"|"), '
    query=query[:-2]+'});\n'
    cypher_file.write(query)
    cypher_file.write('commit\nbegin\n')
    cypher_file.write('Create Constraint On (node:EFOdisease) Assert node.id Is Unique; \n')
    cypher_file.write('commit')

    # create node csv
    file=open('node.csv','w')
    csv_writer=csv.DictWriter(file,fieldnames=list(set_all_properties_in_efo))
    csv_writer.fieldnames()

    for disease_id, dict_value in dict_all_efo_entries.items():
        # add all properties of a node into csv file
        csv_writer.writerow(dict_value)
    file.close()

    #add query for relationship integration
    cypher_file.write('begin')
    query = ''' Match (a:EFOdisease{id:line.child_id}), (b:EFOdisease{id:line.parent_id}) 
                     Create (a)-[:is_a_efo]->(b); \n'''
    cypher_file.write(query)
    cypher_file.write('commit')

    #create csv for relationships
    # create node csv
    file = open('node.csv', 'w')
    csv_writer = csv.writer(file)
    csv_writer.writerow(['child_id','parent_id'])

    for (parent_id,child_id) in set_parent_child_pair:
        csv_writer.writerow([child_id,parent_id])
    file.close()



def main():
    print(datetime.datetime.now())

    print('##########################################################hierachical################')

    print(datetime.datetime.now())
    print('gather symptoms information ')

    get_efo_information_and_map_to_umls()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('put all relationship and node information into a csv and create a cypher file')

    generate_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
