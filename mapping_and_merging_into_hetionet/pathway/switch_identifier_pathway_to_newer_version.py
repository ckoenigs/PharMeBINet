# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv
import sys
from collections import  defaultdict

# sys.path.append('../../drugbank/')
# from add_information_from_a_not_existing_node_to_existing_node import merge_information_from_one_node_to_another

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with hetionet pathways with identifier as key and value the name
dict_pathway_hetionet = {}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_pathway_hetionet[identifier] = name

    print('number of pathway nodes in hetionet:' + str(len(dict_pathway_hetionet)))

# dictionary of pathways which are not in hetionet with they properties: name
dict_ctd_pathway_not_in_hetionet = {}

# dictionary of ctd pathways which are in hetionet with properties: name
dict_ctd_pathway_in_hetionet = {}

# dictionary with all pathways which are mapped to pc or wp with propertie wp, pc id and propertie pathway identifier, name, source
dict_ctd_pathway_mapped_to_pc_or_wp = {}

# dictionary with all pathways which are not mapped to pc or wp with pathway identifier and properties name, source
dict_ctd_pathways_not_mapped = {}

# dictionary pathway name from pathway list an the identifier plus the source
dict_name_to_pc_or_wp_identifier = defaultdict(list)


# dictionary with own id from pc to name, pcid and sourc
dict_own_id_to_pcid_and_other={}

# pc maximal number for pc id
pc_maximal_number_for_id=0

#dictionary of identifier to nodes information
dict_id_to_node={}

'''
load in all pathway with the way himmelstein construct of the identifier but for version 9
https://github.com/dhimmel/pathways
properties:
    0: identifier	
    1:name	
    2:url	
    3:n_genes	
    4:n_coding_genes	
    5:source	
    6:license	
    7:genes	
    8:own id
    9:coding_genes
'''


def load_in_all_pathways_from_himmelsteins_construction():
    # search for the macimal pc number
    global pc_maximal_number_for_id

    #
    query = '''MATCH (n:pathway_multi) RETURN n, n.identifier,n.name, n.source,n.own_id '''
    results = g.run(query)

    for node,identifier, name, source, own_id, in results:
        dict_id_to_node[identifier]=dict(node)
        # find the highest number of pc
        if identifier[0:2]=='PC' and int(identifier.split('_')[1])> pc_maximal_number_for_id  :
            pc_maximal_number_for_id=int(identifier.split('_')[1])

        # fill dictionary with name to rest
        dict_name_to_pc_or_wp_identifier[name].append(dict(node))

        # this is a little bit weird
        if own_id in dict_own_id_to_pcid_and_other and own_id!="":
            dict_own_id_to_pcid_and_other[own_id].append([identifier,source, name])
        elif own_id in dict_own_id_to_pcid_and_other :
            dict_own_id_to_pcid_and_other[identifier] = [[identifier, source, name]]
        else:
            dict_own_id_to_pcid_and_other[own_id]=[[identifier, source, name]]
    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))
    print('number of different pathway ids:'+str(len(dict_own_id_to_pcid_and_other)))

#list of all new identifier which are mapped
list_mapped_to=[]

# dictionary with multiple mapped new identifier
dict_old_id_to_multiple_new_id={}

# version string pc
version_string='PC11_'

'''
che old version pathway from hetionet map to new version
'''
def switch_id_for_pathways():
    global pc_maximal_number_for_id
    counter_exists=0
    counter_not_exists=0
    counter_wp=0
    counter_not_mapped_wp=0
    for identifier, name in dict_pathway_hetionet.items():


        if name in dict_name_to_pc_or_wp_identifier:
            list_of_dict= dict_name_to_pc_or_wp_identifier[name]
            if len(list_of_dict)>1:
                print(list_of_dict)
            for dict_node in list_of_dict:
                identifiers =dict_node['identifier']
                if identifiers=='PC9_2504':
                    print('blub')
                if identifiers in list_mapped_to:
                #     if identifiers[0:2]==identifier[0:2] or identifiers[0:2]=='WP':
                    print('multiple mapped new identifier')
                    print(identifiers)
                    print(identifier)
                    dict_old_id_to_multiple_new_id[identifier]=identifiers
                    continue
                else:
                    # if identifiers[0:2] == identifier[0:2] or identifiers[0:2] == 'WP':
                    list_mapped_to.append(identifiers)
                #     else:
                #         continue
                # own_ids = [x[2] for x in dict_name_to_pc_or_wp_identifier[name]]
                # own_source= [x[1] for x in dict_name_to_pc_or_wp_identifier[name]]
                # own_ids= [x for x in own_ids if x]
                # own=[i+':'+j for i,j in zip(own_source,own_ids)]
                # own = ','.join(own)
                # counter_exists+=1
                if identifier[0:2]=='WP':
                    counter_wp+=1
                #     if identifiers==identifier or identifiers[0:2]=='PC':
                #         continue
                # if identifier != identifiers:

                # xrefs=own+'","'+identifier if own != '' else identifier
                query='''Match (c:Pathway{ identifier:"%s"}) Set c.identifier="%s", c.xrefs=["%s"];'''



        else:
            counter_not_exists += 1
            # if it has not the PC id the id can be the same
            if identifier[0:2] == 'WP':
                continue
            #else it hast to be updated to the newest version (or should be delete?)
            pc_maximal_number_for_id += 1
            new_identifier=version_string + str(pc_maximal_number_for_id)
            query = '''Match (c:Pathway{ identifier:"%s"}) Set c.identifier="%s" , c.xrefs=[];'''
    #
    print('number of mapped:' + str(counter_exists))
    print('number not exists:' + str(counter_not_exists))
    print(counter_not_mapped_wp)
    print(counter_wp)
    print('xrefs for all')
    query='''  Match (c:Pathway) Where not exists(c.xrefs) Set c.xrefs=[];'''
    g.run(query)

    print('merge')
    for old_id, multiple_new_id in dict_old_id_to_multiple_new_id.items():
        print(old_id, multiple_new_id)
        merge_information_from_one_node_to_another(old_id, multiple_new_id, 'Pathway')


    
    
def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from hetionet into a dictionary')

    load_hetionet_pathways_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from d. himmelstein into a dictionary')

    load_in_all_pathways_from_himmelsteins_construction()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Generate csv for switch identifier and ')

    switch_id_for_pathways()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()