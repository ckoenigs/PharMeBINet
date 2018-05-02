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

# dictionary with hetionet pathways with identifier as key and value the xrefs
dict_pathway_hetionet_xrefs = {}

# dictionary with hetionet pathways with name as key and value the identifier
dict_pathway_hetionet_names = {}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.name, n.source, n.xrefs'''
    results = g.run(query)

    for identifier, name, source, xrefs, in results:
        dict_pathway_hetionet[identifier] = name
        dict_pathway_hetionet_xrefs[identifier] = xrefs
        dict_pathway_hetionet_names[name] = [identifier, source]

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

# dictionary transform the named source in ctd to the one in pathway himmelstein
dict_source_ctd_to_source_pc_or_wp = {
    "REACT": 'reactome',
    "KEGG": 'kegg'
}

# dictionary with own id from pc to name, pcid and source
dict_own_id_to_pcid_and_other = {}

# pc maximal number for pc id
pc_maximal_number_for_id = 999

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
    with open('pathways_hetionet_data/pathways_v9_changed_pc9_10.tsv') as tsvfile:
        print()
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            identifier = row[0]
            name = row[1]
            source = row[5]
            own_id = row[8]
            if name in dict_name_to_pc_or_wp_identifier:
                dict_name_to_pc_or_wp_identifier[name].append([identifier, source])
            else:
                dict_name_to_pc_or_wp_identifier[name] = [[identifier, source]]
            if own_id in dict_own_id_to_pcid_and_other and own_id != "":
                dict_own_id_to_pcid_and_other[own_id].append([identifier, source, name])
            elif own_id in dict_own_id_to_pcid_and_other:
                dict_own_id_to_pcid_and_other[identifier] = [[identifier, source, name]]
            else:
                dict_own_id_to_pcid_and_other[own_id] = [[identifier, source, name]]
    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))
    print('number of different pathway ids:' + str(len(dict_own_id_to_pcid_and_other)))


# dictionary which is mapped to which source
dict_mapped_source = {}

# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w')
file_not_mapped_pathways.write('id\tname\tsource\n')

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w')
file_mapped_pathways.write('id\tname\tsource\tid_hetionet\tsource_himmelstein\tmapping_method\n')

file_multiple_mapped_pathways = open('pathway/multiple_mapped_pathways.tsv', 'w')
file_multiple_mapped_pathways.write('id_s\tname\tsource_sources\tid_hetionet\tsource_himmelstein\n')

'''
check if another ctd pathway to same identifier or not and informtaion int to the dictionaries
'''


def check_ctd_pathway_mapped_multiple_or_not(pc_or_wp_id, pathways_id, pathways_name, pathways_id_type, pc_or_wp_source,
                                             file_multiple_mapped_pathways, mapping_method):
    # check if another ctd pathway also mapped to this identifier
    if pc_or_wp_id in dict_ctd_pathway_mapped_to_pc_or_wp:

        dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id].append(
            [pathways_id, pathways_name, pathways_id_type,
             pc_or_wp_source])
        pathways_ids = \
            dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                0] + '|' + pathways_id
        pathways_id_types = \
            dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                3] + '|' + pathways_id_type
        file_multiple_mapped_pathways.write(
            pathways_ids + '\t' + pathways_name + '\t' + pathways_id_types + '\t' +
            pc_or_wp_id + '\t' +
            pc_or_wp_source + '\n')
        file_mapped_pathways.write(
            pathways_id + '\t' + pathways_name + '\t' + pathways_id_type + '\t' +
            pc_or_wp_id + '\t' +
            pc_or_wp_source + '\t' + mapping_method + '\n')
    else:
        dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id] = [
            [pathways_id, pathways_name, pathways_id_type,
             pc_or_wp_source]]
        file_mapped_pathways.write(
            pathways_id + '\t' + pathways_name + '\t' + pathways_id_type + '\t' +
            pc_or_wp_id + '\t' +
            pc_or_wp_source + '\t' + mapping_method + '\n')
    if pc_or_wp_source in dict_mapped_source:
        dict_mapped_source[pc_or_wp_source].append(pathways_id_type)
    else:
        dict_mapped_source[pc_or_wp_source] = [pathways_id_type]


# dictionary where a ctd pathway mapped to multiple pc or wp ids
dict_ctd_to_multiple_pc_or_wp_ids = {}

'''
load all ctd pathways and check if they are in hetionet or not
'''


def load_ctd_pathways_in():
    query = '''MATCH (n:CTDpathway) RETURN n'''
    results = g.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    for pathways_node, in results:
        pathways_id = pathways_node['pathway_id']
        pathways_name = pathways_node['name']
        pathways_id_type = pathways_node['id_type']

        # check if the ctd pathway id is part in the himmelstein xref
        if pathways_id in dict_own_id_to_pcid_and_other:
            counter_map_with_id += 1
            if len(dict_own_id_to_pcid_and_other[pathways_id]) > 1:
                print('multiple für identifier')
            pc_or_wp_id = dict_own_id_to_pcid_and_other[pathways_id][0][0]
            pc_or_wp_source = dict_own_id_to_pcid_and_other[pathways_id][0][1]
            check_ctd_pathway_mapped_multiple_or_not(pc_or_wp_id, pathways_id, pathways_name, pathways_id_type,
                                                     pc_or_wp_source, file_multiple_mapped_pathways, 'id')

        elif pathways_name in dict_name_to_pc_or_wp_identifier:
            counter_map_with_name += 1

            pc_or_wp_id = dict_name_to_pc_or_wp_identifier[pathways_name][0][0]
            pc_or_wp_source = dict_name_to_pc_or_wp_identifier[pathways_name][0][1]

            if len(dict_name_to_pc_or_wp_identifier[pathways_name]) == 1:
                check_ctd_pathway_mapped_multiple_or_not(pc_or_wp_id, pathways_id, pathways_name, pathways_id_type,
                                                         pc_or_wp_source, file_multiple_mapped_pathways, 'name')

            else:
                list_pc_or_wc_ids = []
                one_is_in_hetionet = False
                best_identifier = ""
                for [pc_or_wp_id, source] in dict_name_to_pc_or_wp_identifier[pathways_name]:
                    if pc_or_wp_id in dict_pathway_hetionet and not one_is_in_hetionet:
                        best_identifier = pc_or_wp_id
                        one_is_in_hetionet = True
                    elif pc_or_wp_id in dict_pathway_hetionet:
                        print('multiple hetionet mapping')
                if not one_is_in_hetionet:
                    best_identifier = list_pc_or_wc_ids[0]

                check_ctd_pathway_mapped_multiple_or_not(best_identifier, pathways_id, pathways_name, pathways_id_type,
                                                         pc_or_wp_source, file_multiple_mapped_pathways, 'name')


        else:
            dict_ctd_pathways_not_mapped[pathways_id] = [pathways_name, pathways_id_type]
            # file_not_mapped_pathways.write(pathways_id+ '\t' +pathways_name+ '\t' + pathways_id_type+ '\n' )

    print('number of mapped nodes:' + str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))
    print('number of not existing nodes:' + str(len(dict_ctd_pathways_not_mapped)))
    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    # print(dict_mapped_source)


# list of all not mapped ctd pathway identifierswith himmelstein list and hetionet
list_not_mapped_ctd_pathway_ids = []

'''
try to map the ctd pathways to the hetionet pathways, because some has not an identifier from the new himmelstein list and got a new identifier
'''


def try_to_map_to_the_hetionet_pathway():
    counter_map_with_name = 0
    for pathway_id, [pathways_name, pathways_id_type] in dict_ctd_pathways_not_mapped.items():
        if pathways_name in dict_pathway_hetionet_names:
            counter_map_with_name += 1
            [hetionet_identifier, source] = dict_pathway_hetionet_names[pathways_name]
            check_ctd_pathway_mapped_multiple_or_not(hetionet_identifier, pathway_id, pathways_name, pathways_id_type,
                                                     source, file_multiple_mapped_pathways, 'name_hetionet')
        else:
            list_not_mapped_ctd_pathway_ids.append(pathway_id)
    print('number of mapped nodes:' + str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))
    print('number of not mapped nodes:' + str(len(list_not_mapped_ctd_pathway_ids)))
    print('number of mapping with name:' + str(counter_map_with_name))


# all that did not map to himmelsteins list or to the pathways in hetionet, but are human pathways get an new own identifier
own_identifier = 1

# dictionary with all human pathways
dict_human_pathways_reactom = {}

'''
Generate reactome list of all human pathways 
'''


def add_all_human_pathway_into_dictionary():
    reactome_pathways = open('pathways_hetionet_data/all_reactoms_human_pathway_ids.txt', 'r')
    for reactom_id in reactome_pathways:
        reactom_id = reactom_id.replace('\n', '')
        dict_human_pathways_reactom[reactom_id] = 'human'

    print('number of reactome human pathways:' + str(len(dict_human_pathways_reactom)))


'''
check all reactome identifier if the pathways are in humans and give them an own identifier
'''


def check_if_reactome_identifier_is_part_of_human_pathway():
    global own_identifier
    counter_of_not_mapped_reactome_identifier = 0
    # delete identifier from not mapped list
    delete_indices_from_not_map_list = []
    for identifier in list_not_mapped_ctd_pathway_ids:
        [name, source] = dict_ctd_pathways_not_mapped[identifier]
        if source == 'REACT':
            if identifier in dict_human_pathways_reactom:
                dict_ctd_pathway_mapped_to_pc_or_wp['CTD_' + str(own_identifier)] = [
                    [identifier, name, source,
                     '']]
                file_mapped_pathways.write(
                    identifier + '\t' + name + '\t' + source + '\t' +
                    'CTD_' + str(own_identifier) + '\t' +
                    '' + '\thuman_pathway_reactome\n')
                own_identifier += 1
                delete_indices_from_not_map_list.append(list_not_mapped_ctd_pathway_ids.index(identifier))

            else:
                counter_of_not_mapped_reactome_identifier += 1
                print(identifier)
                print(name)

    delete_indices_from_not_map_list.sort()
    delete_indices_from_not_map_list = list(reversed(delete_indices_from_not_map_list))
    for index in delete_indices_from_not_map_list:
        list_not_mapped_ctd_pathway_ids.pop(index)

    print('number of not mapped:' + str(len(list_not_mapped_ctd_pathway_ids)))
    print('number of not mapped reactome identifer:' + str(counter_of_not_mapped_reactome_identifier))
    print('number of mapped pathways:' + str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))


'''
try to map the rest of not mapped pathways from ctd with use of the relationship pathway-gene-chemical, because the relationship gene-pathway can say if the gene are from human
'''


def map_with_relationship_pathway_gene_chemical():
    global own_identifier

    # all pathway identifier which are mapped in this function
    delete_map_pathway = []
    for identifier in list_not_mapped_ctd_pathway_ids:
        [name, source] = dict_ctd_pathways_not_mapped[identifier]
        query = '''Match p=(c:CTDpathway{pathway_id:"%s"})-[:participates_GP]-(:CTDgene)-[:associates_CG{organism_id:'9606'}]-(:CTDchemical) Return p Limit 1'''
        query = query % (identifier)
        results = g.run(query)
        result = results.evaluate()
        if not result is None:
            # if source=='REACT':
            #     print(result)
            dict_ctd_pathway_mapped_to_pc_or_wp['own_' + str(own_identifier)] = [
                [identifier, name, source,
                 '']]
            file_mapped_pathways.write(
                identifier + '\t' + name + '\t' + source + '\t' +
                'own_' + str(own_identifier) + '\t' +
                '' + '\trelationship with human gene\n')
            own_identifier += 1
            delete_map_pathway.append(list_not_mapped_ctd_pathway_ids.index(identifier))
        else:
            file_not_mapped_pathways.write(identifier + '\t' + name + '\t' + source + '\n')

    # delete mapped pathway IDs from list with not mapped CTD identifiers
    delete_map_pathway.sort()
    delete_map_pathway = list(reversed(delete_map_pathway))
    for index in delete_map_pathway:
        list_not_mapped_ctd_pathway_ids.pop(index)

    print('number of mapped pathways:' + str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))
    print('number of not mapped:' + str(len(list_not_mapped_ctd_pathway_ids)))


# dictionary
dict_source_ctd_to_full_name = {
    "REACT": "Reactome",
    "KEGG": "KEGG"
}

'''
generate connection between mapping pathways of ctd and hetionet and generate new hetionet nodes for the not existing nodes
'''


def integration_into_hetionet():
    counter_new_nodes=0
    query= ''' Match (d:Pathway) Set d.hetionet="yes" '''
    g.run(query)
    for identifier_hetionet, list_of_mapped_ctds in dict_ctd_pathway_mapped_to_pc_or_wp.items():
        if not identifier_hetionet in dict_pathway_hetionet and len(list_of_mapped_ctds) == 1:
            counter_new_nodes+=1
            ctd_identifier, ctd_name, ctd_source, mapping_method = list_of_mapped_ctds[0]
            query = '''Create (d:Pathway{identifier:"%s" , name:"%s", xrefs:["%s"] ,source:"%s", ctd:"yes", hetionet:"no", ctd_url:"http://ctdbase.org/detail.go?type=pathway&acc=%s" , license:" 2002-2012 MDI Biological Laboratory. All rights reserved.  2012-2018 MDI Biological Laboratory & NC State University. All rights reserved."})'''

            xref = dict_source_ctd_to_full_name[ctd_source] + ':' + ctd_identifier
            query = query % (
            identifier_hetionet, ctd_name, xref, dict_source_ctd_to_full_name[ctd_source] + " via CTD", ctd_identifier)
            g.run(query)
        elif not identifier_hetionet in dict_pathway_hetionet:
            print('new id with multiple dings')
            print(identifier_hetionet)
            print(list_of_mapped_ctds)
        for [ctd_identifier, ctd_name, ctd_source, mapping_method] in list_of_mapped_ctds:
            xrefs = []
            if ctd_identifier in dict_pathway_hetionet_xrefs:
                xrefs = set(dict_pathway_hetionet_xrefs[ctd_identifier])
                xrefs.add(dict_source_ctd_to_full_name[ctd_source] + ':' + ctd_identifier)
                xrefs = list(xrefs)
            else:
                xrefs = [dict_source_ctd_to_full_name[ctd_source] + ':' + ctd_identifier]
            xrefs = '","'.join(xrefs)

            query = '''Match (d:Pathway{identifier:"%s"}),(c:CTDpathway{pathway_id:"%s"}) Create (d)-[:equal_to_CTD_pathway]->(c) Set c.hetionet_id="%s", d.xrefs= ["%s"], d.ctd="yes", d.ctd_url="http://ctdbase.org/detail.go?type=pathway&acc=%s" '''
            query = query % (identifier_hetionet, ctd_identifier, identifier_hetionet, xrefs, ctd_identifier)
            g.run(query)
        query='''Match (d:Pathway) Where not  exists(d.ctd) Set d.ctd="no", d.ctd_url='' '''
        g.run(query)

    print('number of new generated nodes in Hetionet:'+str(counter_new_nodes))


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
    print('Load all ctd pathways from neo4j into a dictionary')

    load_ctd_pathways_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map with hetionet pathways which are not in the new himmelstein list')

    try_to_map_to_the_hetionet_pathway()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in human pathways')

    add_all_human_pathway_into_dictionary()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('check all reactome pathway for human pathways')

    check_if_reactome_identifier_is_part_of_human_pathway()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('check all not mapped pathway if they have pathways which has relationship with a human gene')

    map_with_relationship_pathway_gene_chemical()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate new pathways and connect them to ctd ')

    integration_into_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
