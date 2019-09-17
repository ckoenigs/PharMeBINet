# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 11:55:50 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import sys, time, csv
from collections import defaultdict

sys.path.append('../drugbank/')

# from is to combine two nodes and delete the old one
import add_information_from_a_not_existing_node_to_existing_node


'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

#dictionary with all chemicals which are not mapped
dict_chemical_which_are_not_mapped={}

#list of all identifier of chemicals which are not mapped
list_chemical_identifier=[]



'''
First find all Chemical which have no equal connection after new mapping 
this relationship (equal_to_CTD_chemical) is only between chemical and ctd
for chemical/compound is the rela equal_chemical_CTD
{identifier:'C014081'}
'''
def find_all_chemicals_which_did_not_mapped():
    query='''Match (d:Chemical) Where not (d)-[:equal_to_CTD_chemical]-() and not 'Compound' in labels(d) Return d'''
    result=g.run(query)
    for chemical, in result:
        node=dict(chemical)
        not_mapped_id = node['identifier']
        if not_mapped_id == 'C014081':
            print('ok')
        dict_chemical_which_are_not_mapped[node['identifier']]=node
        list_chemical_identifier.append(node['identifier'])

    print('number of not mapped chemicals:'+str(len(list_chemical_identifier)))

# remember all chemicals which are now mapped to db ids
dict_chemical_to_drugbank_id=defaultdict(list)

# file for the new combination
file_matching=open('chemical/new_matched.csv','w')
csv_matching=csv.writer(file_matching)
csv_matching.writerow(['old chemical id','old chemical name','new chemical id','new chemical name'])

'''
find out all the chemicals which are now mapped to drugbank ids 
{identifier:'C014081'}
'''
def find_not_mapped_chemicals_which_are_mapped_to_DB_id():
    query = '''Match (d:Chemical), p=(b:CTDchemical)<-[]-(e:Chemical) Where d.identifier=b.chemical_id and not (d)-[]-(b)  Return d, e '''
    result = g.run(query)

    list_of_mapped_to_drugbank_ids=set([])
    for chemical_not_mapped, compound , in result:
        node = dict(chemical_not_mapped)

        index=list_chemical_identifier.index(node['identifier'])

        list_of_mapped_to_drugbank_ids.add(index)

        dict_chemical_to_drugbank_id[node['identifier']].append(compound['identifier'])
        csv_matching.writerow([node['identifier'],node['name'],compound['identifier'],compound['name']])

    list_of_mapped_to_drugbank_ids=list(list_of_mapped_to_drugbank_ids)
    list_of_mapped_to_drugbank_ids.sort()
    list_of_mapped_to_drugbank_ids = list(reversed(list_of_mapped_to_drugbank_ids))
    for index in list_of_mapped_to_drugbank_ids:

        list_chemical_identifier.pop(index)


    print('number of not mapped chemicals and not to db ids:'+str(len(list_chemical_identifier)))
    print(list_chemical_identifier[0:10])

#dictionary name to ctd chemical mesh
dict_name_to_ctd_chemical_mesh_id={}

'''
gather all CTD chemicals and generate a name/synonym dictionary to the mapped chemical identifier.
'''

def load_drugs_from_CTD():
    query = 'MATCH (n:CTDchemical)<-[]-(b:Chemical) RETURN n, b.identifier'

    file_not_same_cas=open('chemical/not_same_cas.tsv','w')
    file_not_same_cas.write('mesh\tcas-mesh\tdurgbank\tcas-db\tmapping_with_cas\n')

    results = g.run(query)

    for result, mapped_identifier, in results:
        chemical_id = result['chemical_id']
        synonyms = result['synonyms'] if 'synonyms' in result else []
        for synonym in synonyms:
            synonym=synonym.lower()
            if not synonym in dict_name_to_ctd_chemical_mesh_id:
                dict_name_to_ctd_chemical_mesh_id[synonym]=[mapped_identifier]
            else:
                dict_name_to_ctd_chemical_mesh_id[synonym].append(mapped_identifier)
                # print(synonym.encode('utf-8'))
                # print(chemical_id)
                # print(mapped_identifier)
                # print(dict_name_to_ctd_chemical_mesh_id[synonym])
        name = result['name'].lower()
        if not name in dict_name_to_ctd_chemical_mesh_id:
            dict_name_to_ctd_chemical_mesh_id[name]=[mapped_identifier]
        else:
            dict_name_to_ctd_chemical_mesh_id[name].append(mapped_identifier)
            # print(name)
            # print(chemical_id)
            # print(mapped_identifier)
            # print(dict_name_to_ctd_chemical_mesh_id[name])



'''
check how many of the chemical now has a new mesh id
'''
def map_to_new_mesh_id_with_name_mapping():
    delete_index_list=set([])

    for counter, mesh_id in enumerate(list_chemical_identifier):
        old_chemical_node=dict_chemical_which_are_not_mapped[mesh_id]
        if mesh_id == 'C014081':
            print('ok')
        name=old_chemical_node['name'].lower()
        if name in dict_name_to_ctd_chemical_mesh_id:
            new_meshs=dict_name_to_ctd_chemical_mesh_id[name]
            new_meshs=list(set(new_meshs))
            if len(new_meshs)>1:
                print('ohje')
                print(name)
                print(new_meshs)
            dict_chemical_to_drugbank_id[mesh_id].extend(new_meshs)
            for mesh in new_meshs:
                csv_matching.writerow([mesh_id, name, mesh, name])
            delete_index_list.add(counter)

    delete_index_list=list(delete_index_list)
    delete_index_list.sort()
    delete_index_list = list(reversed(delete_index_list))
    for index in delete_index_list:
        list_chemical_identifier.pop(index)

    print('number of not mapped chemicals and not to db ids:' + str(len(list_chemical_identifier)))
    print('number of mapped:'+str(len(dict_chemical_to_drugbank_id)))
    print(list_chemical_identifier[0:10])



'''
generate delete file of the chemical which has no connection  or were delete from ctd
'''
def generat_csv_with_delete_chemicals():
    file=open('chemical/delete_chemical.csv','w')
    csv_write=csv.writer(file)
    csv_write.writerow(['identifier'])
    number_of_deleted_nodes=len(list_chemical_identifier)
    delete_cypher=open('chemical/delete_cypher.cypher','w')
    query='''Match (d:Chemical) Where not (d)-[:equal_to_CTD_chemical]-() and not 'Compound' in labels(d) With d Limit 100 Detach Delete d;\n'''
    for x in range(0,number_of_deleted_nodes/100 +1):
        delete_cypher.write('begin\n')
        delete_cypher.write(query)
        delete_cypher.write('commit\n')
    for chemical_id in list_chemical_identifier:
        csv_write.writerow([chemical_id])

'''
merge the old ctd chemiclas to the new ones
'''
def merge_old_nodes_into_new_one():
    counter_all_new_combinder=len(dict_chemical_to_drugbank_id)
    every_tenth_counter=int(counter_all_new_combinder/10)+1
    counter=0
    print(every_tenth_counter)
    for old_ctd, list_of_new_identifier in dict_chemical_to_drugbank_id.items():
        for new_id in list_of_new_identifier:
            add_information_from_a_not_existing_node_to_existing_node.merge_information_from_one_node_to_another(old_ctd,new_id,'Chemical')
        counter+=1
        if counter % every_tenth_counter==0:
            print('one / ten')
            print(counter)
            print(datetime.datetime.utcnow())

def main():
    global exists_chemicals
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all chemicals without mapping from hetionet into a dictionary')

    find_all_chemicals_which_did_not_mapped()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load allchemicals which are now also compounds ')

    find_not_mapped_chemicals_which_are_mapped_to_DB_id()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    ################################################################################################################################
    # check how chemicals has changed
    print('load all ctd chemicals')

    load_drugs_from_CTD()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map with name')

    map_to_new_mesh_id_with_name_mapping()
    ###################################################################################################################################
    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Generate delete file')

    generat_csv_with_delete_chemicals()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Generate merge nodes')

    merge_old_nodes_into_new_one()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
