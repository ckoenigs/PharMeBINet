# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv
import sys

sys.path.append('../../drugbank/')
from add_information_from_a_not_existing_node_to_existing_node import merge_information_from_one_node_to_another

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
dict_name_to_pc_or_wp_identifier = {}


'''
load in all pathway with the way himmelstein construct the identifier
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
    -/8:own id
    8/9:coding_genes
all with / is the second for pathwaycommons version9
'''


def load_in_all_pathways_from_himmelsteins_construction():
    with open('pathways.tsv') as tsvfile:
        print()
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            identifier = row[0]
            name = row[1]
            source = row[5]
            if name in dict_name_to_pc_or_wp_identifier:
                # print(identifier)
                # print(source)
                # print(name)
                # print(dict_name_to_pc_or_wp_identifier[name])
                dict_name_to_pc_or_wp_identifier[name].append([identifier, source])
            else:
                dict_name_to_pc_or_wp_identifier[name] = [[identifier, source]]
    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))

# dictionary with own id from pc to name, pcid and sourc
dict_own_id_to_pcid_and_other={}

# pc maximal number for pc id
pc_maximal_number_for_id=0

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


def load_in_all_pathways_from_himmelsteins_construction_version9():
    global pc_maximal_number_for_id
    with open('pathways_v9.tsv') as tsvfile:
        print()
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            identifier = row[0]
            if identifier[0:2]=='PC' and int(identifier.split('_')[1])> pc_maximal_number_for_id  :
                pc_maximal_number_for_id=int(identifier.split('_')[1])
            name = row[1]
            source = row[5]
            own_id=row[8]
            if name in dict_name_to_pc_or_wp_identifier:
                dict_name_to_pc_or_wp_identifier[name].append([identifier, source, own_id])
            else:
                dict_name_to_pc_or_wp_identifier[name] = [[identifier, source, own_id]]
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
            identifiers = dict_name_to_pc_or_wp_identifier[name][0][0]
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
            own_ids = [x[2] for x in dict_name_to_pc_or_wp_identifier[name]]
            own_source= [x[1] for x in dict_name_to_pc_or_wp_identifier[name]]
            own_ids= [x for x in own_ids if x]
            own=[i+':'+j for i,j in zip(own_source,own_ids)]
            own = ','.join(own)
            counter_exists+=1
            if identifier[0:2]=='WP':
                counter_wp+=1
            #     if identifiers==identifier or identifiers[0:2]=='PC':
            #         continue
            # if identifier != identifiers:

            xrefs=own+'","'+identifier if own != '' else identifier
            query='''Match (c:Pathway{ identifier:"%s"}) Set c.identifier="%s", c.xrefs=["%s"];'''
            query= query %(identifier, identifiers,xrefs)
            g.run(query)


        else:
            counter_not_exists += 1
            if identifier[0:2] == 'WP':
                continue
            pc_maximal_number_for_id += 1
            new_identifier='PC9_' + str(pc_maximal_number_for_id)
            query = '''Match (c:Pathway{ identifier:"%s"}) Set c.identifier="%s" , c.xrefs=[];'''
            query = query % (identifier, new_identifier)
            g.run(query)
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

    # load_in_all_pathways_from_himmelsteins_construction()
    load_in_all_pathways_from_himmelsteins_construction_version9()

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