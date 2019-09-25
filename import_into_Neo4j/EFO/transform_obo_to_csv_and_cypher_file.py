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

if len(sys.argv)!=4:
    sys.exit('need the obo file, directory, neo4j label')
    

# file path to data source
file_name = sys.argv[1]

# directory
directory=sys.argv[2]

#neo4j label
neo4j_label=sys.argv[3]

# dictionary with all identifier and a dictionary for all information of this identifier
dict_all_entries = {}

#all properties
set_all_properties_in_database=set([])

#list of all properties which are lists
set_list_properties=set([])

#set list of all parent-child pairs
set_parent_child_pair=set([])

# list other relationships
list_other_rela=[]

# dictionary with list of the other relationships
dict_other_rela_parent_child={}



'''
group the terms together and get the information from the different terms and gather all term information in a dictionary
further fill the dictionary for the hierachical set
'''


def gather_information_from_obo():
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
                        parent_id = value.split('!')[0].strip().split(' {')[0]
                        set_parent_child_pair.add((parent_id,dict_all_info['id']))
                    elif key_term=='relationship':
                        rela_info=value.split('!')[0].split(' ')
                        rela_type=rela_info[0]
                        parent_id=rela_info[1]
                        if rela_type in list_other_rela:
                            dict_other_rela_parent_child[rela_type].add((parent_id,dict_all_info['id']))
                        else:
                            list_other_rela.append(rela_type)
                            dict_other_rela_parent_child[rela_type]={(parent_id,dict_all_info['id'])}


                    else:
                        # for some properties more than one value appears
                        if key_term=='xref':
                            key_term='xrefs'
                        if not key_term in dict_all_info:
                            dict_all_info[key_term] = value.replace('"', '').replace("'", "").replace("\\", "")
                        else:
                            dict_all_info[key_term]+='|'+value.replace('"', '').replace("'", "").replace("\\", "")
                            set_list_properties.add(key_term)
                        set_all_properties_in_database.add(key_term)



                dict_all_entries[dict_all_info['id']] = dict_all_info


'''
generate cypher file
'''


def generate_cypher_file():
    #create cypher file
    cypher_file=open('cypher.cypher','w')
    query=''' Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/'''+directory+'''/node.csv" As line Create (:'''+neo4j_label+'''{'''
    for property in set_all_properties_in_database:
        if not property in set_list_properties :
            query+=property+':line.'+property+', '
        else:
            query += property + ':split(line.' + property + ',"|"), '
    query=query[:-2]+'});\n'
    cypher_file.write(query)
    cypher_file.write(':begin\n')
    cypher_file.write('Create Constraint On (node:'+neo4j_label+') Assert node.id Is Unique; \n')
    cypher_file.write(':commit\n')

    # create node csv
    file=open('node.csv','w')
    csv_writer=csv.DictWriter(file,fieldnames=list(set_all_properties_in_database))
    csv_writer.writeheader()

    for disease_id, dict_value in dict_all_entries.items():
        # add all properties of a node into csv file
        csv_writer.writerow(dict_value)
    file.close()

    #add query for relationship integration
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/'''+directory+'''/rela.csv" As line  Match (a:%s{id:line.child_id}), (b:%s{id:line.parent_id}) Create (a)-[:is_a]->(b); \n''' %(neo4j_label,neo4j_label)
    cypher_file.write(query)

    #create csv for relationships
    file = open('rela.csv', 'w')
    csv_writer = csv.writer(file)
    csv_writer.writerow(['child_id','parent_id'])

    for (parent_id,child_id) in set_parent_child_pair:
        csv_writer.writerow([child_id,parent_id])
    file.close()

    print(list_other_rela)

    #generate cypher query and csv for all other rela types
    for rela_type, list_parent_child in dict_other_rela_parent_child.items():
        file_name='rela_'+rela_type+'.csv'
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/%s/%s" As line  Match (a:%s{id:line.child_id}), (b:%s{id:line.parent_id}) Create (a)-[:%s]->(b); \n'''
        query= query %  (directory, file_name, neo4j_label, neo4j_label,rela_type)
        cypher_file.write(query)

        # create csv for relationships
        file = open(file_name, 'w')
        csv_writer = csv.writer(file)
        csv_writer.writerow(['child_id', 'parent_id'])

        for (parent_id, child_id) in set_parent_child_pair:
            csv_writer.writerow([child_id, parent_id])
        file.close()


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################hierachical################')

    print(datetime.datetime.utcnow())
    print('gather symptoms information ')

    gather_information_from_obo()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship and node information into a csv and create a cypher file')

    generate_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
