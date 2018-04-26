# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv
import sys

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
    with open('pathways_hetionet_data/pathways.tsv') as tsvfile:
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
pc_maximal_number_for_id=999

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
    with open('pathways_hetionet_data/pathways_v9.tsv') as tsvfile:
        print()
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            identifier = row[0]
            name = row[1]
            source = row[5]
            own_id=row[8]
            if name in dict_name_to_pc_or_wp_identifier:
                dict_name_to_pc_or_wp_identifier[name].append([identifier, source])
            else:
                dict_name_to_pc_or_wp_identifier[name] = [[identifier, source]]
            if own_id in dict_own_id_to_pcid_and_other and own_id!="":
                dict_own_id_to_pcid_and_other[own_id].append([identifier,source, name])
            elif own_id in dict_own_id_to_pcid_and_other :
                dict_own_id_to_pcid_and_other[identifier] = [[identifier, source, name]]
            else:
                dict_own_id_to_pcid_and_other[own_id]=[[identifier, source, name]]
    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))
    print('number of different pathway ids:'+str(len(dict_own_id_to_pcid_and_other)))


# csv to switch the old hetionet identifier
csv_switch_old_identifier=open('pathways_hetionet_data/switch_identifier.csv','w')
writer = csv.writer(csv_switch_old_identifier, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['oldID', 'newID'])


'''
che old version pathway from hetionet map to new version
'''
def check_old_to_new_version():
    global pc_maximal_number_for_id
    counter_exists=0
    counter_not_exists=0
    counter_wp=0
    counter_not_mapped_wp=0
    for identifier, name in dict_pathway_hetionet.items():
        if name in dict_name_to_pc_or_wp_identifier:
            identifiers=dict_name_to_pc_or_wp_identifier[name][0][0]
            counter_exists+=1
            if identifier[0:2]=='WP':
                counter_wp+=1
                if identifiers==identifier:
                    continue
            writer.writerow([ identifier, identifiers])


        else:
            if identifier[0:2] == 'WP':
                continue
            pc_maximal_number_for_id += 1
            writer.writerow([identifier, 'PC9_' + str(pc_maximal_number_for_id)])
            counter_not_exists+=1

    csv_switch_old_identifier.close()

    print('number of mapped:'+str(counter_exists))
    print('number not exists:'+str(counter_not_exists))
    print(counter_not_mapped_wp)
    print(counter_wp)