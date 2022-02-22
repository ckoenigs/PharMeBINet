# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:43 2018

@author: ckoenigs
"""

import sys, csv
import datetime
from types import *

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases


# reload(sys)
# sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():
    # authenticate("localhost:7474", )
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary monarch DO to information: name
dict_monDO_info = {}

# dictionary external ids to monDO id
dict_external_ids_monDO = {}

# dict of xrefs from monDO which has multiple monDO IDs with counter
dict_source_mapped_to_multiple_monDOs = {}

# dictionary disease ontology to external ids
dict_DO_to_xref = {}

# dictionary do to information: name
dict_DO_to_info = {}

# dictionary do to alternative doid
dict_do_to_alternative_do = {}

# dictionary monDO to DOIDs
dict_monDo_to_DO = {}

# dictionary monDO to DOIDs with only doid mapping
dict_monDo_to_DO_only_doid = {}

# dictionary Do to monDos
dict_DO_to_monDOs = {}

# dictionary Do to monDos
dict_DO_to_monDOs_only_DO = {}

# list of not mapped doids
list_of_not_mapped_doids = []

# mondo properties
mondo_prop = []

# set of excluded mondo ids which are not human ids
set_of_non_human_ids=set()

def get_all_non_human_ids():
    """
    Get all non human disease (MONDO:0005583) nodes and add them to a set
    :return:
    """
    # disease with id MONDO:0005583  is "non-human animal disease"
    query='''Match p=(n:disease{identifier:'MONDO:0005583'})<-[:is_a*]-(a:disease) Return Distinct a.identifier '''
    set_of_non_human_ids.add('MONDO:0005583')
    results= g.run(query)
    for identifier, in results:
        set_of_non_human_ids.add(identifier)


# list of excluded properties from mondo
list_exclude_properties = ['related', 'creation_date', 'created_by', 'seeAlso']

'''
Get all properties of the mondo disease and create the csv files
'''


def get_mondo_properties_and_generate_csv_files():
    query = '''MATCH (p:disease) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''
    result = g.run(query)
    for property, in result:
        mondo_prop.append(property)

    # mondo get an additional property
    mondo_prop.append('umls_cuis')

    # generate csv files
    global csv_new_nodes, csv_map_nodes, csv_rela
    # csv with new nodes
    new_node_file = open('output/new_nodes.csv', 'w', encoding='utf-8')
    csv_new_nodes = csv.DictWriter(new_node_file, delimiter='\t', fieldnames=mondo_prop)
    csv_new_nodes.writeheader()

    # csv with nodes which needs to be updated
    map_node_file = open('output/map_nodes.csv', 'w', encoding='utf-8')
    mondo_prop_mapped = mondo_prop[:]
    mondo_prop_mapped.append('doid')
    mondo_prop_mapped.append('doids')
    csv_map_nodes = csv.DictWriter(map_node_file, delimiter='\t', fieldnames=mondo_prop_mapped)
    csv_map_nodes.writeheader()

    # csv with relatioships
    rela_file = open('output/rela.csv', 'w', encoding='utf-8')
    csv_rela = csv.writer(rela_file, delimiter='\t')
    csv_rela.writerow(['id_1', 'id_2'])


'''
fill the dictionary with external identifier 
'''


def fill_dict_with_external_identifier_to_mondo(xrefs, monDo_id):
    # check if the xrefs are a list or not and extract then the information
    if type(xrefs) == list:
        for external_id in xrefs:
            if external_id in dict_external_ids_monDO:
                if external_id.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                    dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] = 1

                else:
                    dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] += 1

                dict_external_ids_monDO[external_id].append(monDo_id)
            else:
                dict_external_ids_monDO[external_id] = [monDo_id]
    else:
        if xrefs in dict_external_ids_monDO:
            if xrefs.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                dict_source_mapped_to_multiple_monDOs[xrefs.split(':')[0]] = 1

            else:
                dict_source_mapped_to_multiple_monDOs[xrefs.split(':')[0]] += 1

            dict_external_ids_monDO[xrefs].append(monDo_id)
        else:
            dict_external_ids_monDO[xrefs] = [monDo_id]

# dictionary mondo id to mondo name
dict_mondo_id_to_name={}

def add_entry_to_dict(dictionary, key, value):
    """
    add entry in dictionary
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key]=set()
    dictionary[key].add(value)

'''
Load MonDO disease in dictionary
Where n.`http://www.geneontology.org/formats/oboInOwl#id` ='MONDO:0010168'
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:disease)  RETURN n'''
    results = g.run(query)
    for disease, in results:
        monDo_id = disease['identifier']
        if monDo_id in set_of_non_human_ids:
            continue
        name= disease['name'].lower()
        add_entry_to_dict(dict_mondo_id_to_name,monDo_id,name)
        synonyms= disease['synonyms']
        if synonyms:
            for synonym in synonyms:
                synonym=synonym.rsplit(' [')[0].lower()
                add_entry_to_dict(dict_mondo_id_to_name, monDo_id, synonym)
        disease_info = dict(disease)
        dict_monDO_info[monDo_id] = disease_info
        xrefs = disease_info['xrefs'] if 'xrefs' in disease_info else []
        fill_dict_with_external_identifier_to_mondo(xrefs, monDo_id)


# cypher file to integrate mondo
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

# a cypher file to add the merged id to the other doids
cypher_file_end = open('output/cypher_end.cypher', 'w', encoding='utf-8')

# list_properties in mondo
list_of_list_prop = set([])

'''
generate cypher queries to integrate and merge disease nodes and create the subclass relationships
'''


def generate_cypher_queries():
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/monDO/output/%s.csv" As line FIELDTERMINATOR '\\t' Match (a:disease{identifier:line.identifier}) '''

    query_end = '''Create (n)-[:equal_to_monDO]->(a); \n'''
    query_update = ''
    query_new = ''
    for property in mondo_prop:
        if property not in list_of_list_prop:
            if property == 'iri':
                query_new += 'url:line.' + property + ', '
                query_update += 'n.url=line.' + property + ', '
                continue
            query_new += property + ':line.' + property + ', '
            query_update += 'n.' + property + '=line.' + property + ', '
        else:
            query_new += property + ':split(line.' + property + ', "|"), '
            query_update += 'n.' + property + '=split(line.' + property + ', "|"), '
    query_update = query_start + ', (n:Disease{identifier:line.doid}) Set ' + query_update + 'n.mondo="yes", n.license=" CC-BY-SA 3.0", n.resource=n.resource+"MonDO", n.doids=split(line.doids,"|") ' + query_end
    query_update = query_update % ('map_nodes')
    cypher_file.write(query_update)
    query_new = query_start + 'Create (n:Disease{' + query_new + 'mondo:"yes", resource:["MonDO"], url:"https://monarchinitiative.org/disease/"+ line.identifier , license:"CC-BY-SA 3.0", source:"MonDO"}) ' + query_end
    query_new = query_new % ('new_nodes')
    cypher_file.write(query_new)
    query_rela = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/monDO/output/%s.csv" As line FIELDTERMINATOR '\\t' Match (a:Disease{identifier:line.id_1}),(b:Disease{identifier:line.id_2}) Merge (a)-[r:IS_A_DiD]->(b) On CREATE Set r.unbiased=false, r.url="https://monarchinitiative.org/disease/"+ line.id_1,  r.source="Monarch Disease Ontology", r.resource=['MonDO'] , r.mondo='yes', r.license="CC-BY-SA 3.0" On Match Set r.resource=['MonDO'], r.mondo='yes' ;\n'''
    query_rela = query_rela % ('rela')
    cypher_file.write(query_rela)

    # query to delete disease which are not in Mondo
    query = '''Match (d:Disease) Where not exists(d.mondo) Detach Delete d;\n'''
    cypher_file.write(query)

    # add the disease ontology property to the nodes without
    query = '''Match (d:Disease) Where not exists(d.diseaseOntology) Set d.diseaseOntology='no' ;\n'''
    cypher_file.write(query)

    # combin merged id with doids
    query = '''MATCH (n:Disease) Where exists(n.merged_identifier) Set n.doids=n.doids+ n.merged_identifier Remove n.merged_identifier;\n'''
    cypher_file_end.write(query)

# #dictionary doid to multiple remove not fitting mondo
# # manual checked
dict_doid_to_multi_remove={
    'DOID:0080626':['MONDO:0020489'],
    'DOID:0111365': ['MONDO:0006450'],
    'DOID:0111649': ['MONDO:0021849'],
    'DOID:0111564': ['MONDO:0018052','MONDO:0020306'],
    'DOID:0050608': ['MONDO:0012817'], # map to MONDO:0006094
    'DOID:0060536': ['MONDO:0100224'], # map to MONDO:0100133
    'DOID:0110305': ['MONDO:0018098'], # map to MONDO:0021018
    'DOID:1799': ['MONDO:0019954'], # map to MONDO:0005815
    'DOID:688': ['MONDO:0005040'], # map to MONDO:0005564
    'DOID:707': ['MONDO:0004949'], # map to MONDO:0004095
    'DOID:7188': ['MONDO:0005623'], # map to MONDO:0007699
    'DOID:9212': ['MONDO:0008251'], # map to MONDO:0100017
    'DOID:0080130': ['MONDO:0014959'], # map to MONDO:0014175
    'DOID:676': ['MONDO:0005185'], # map to MONDO:0011429

}

'''
Load in all disease ontology ids with external identifier and alternative id
also check for mapping between do and mondo
'''


def load_in_all_DO_in_dictionary():
    # file mapped doid but not the same name
    not_direct_name_matching_file = open('output/not_direct_name_matching_file.tsv', 'w', encoding='utf-8')
    csv_not_direct_name_matching_file = csv.writer(not_direct_name_matching_file, delimiter='\t')
    csv_not_direct_name_matching_file.writerow(['monDO', 'DOID', 'name monDO', 'name DOID'])
    counter_name_not_matching = 0

    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for disease, in results:
        doid = disease['identifier']
        # if doid == 'DOID:0060073':
        #     print('ok')
        name=disease['name'].lower()
        dict_DO_to_info[doid] = dict(disease)
        alternative_id = disease['alternative_ids'] if 'alternative_ids' in disease else []
        dict_do_to_alternative_do[doid] = alternative_id

        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        dict_DO_to_xref[doid] = xrefs
        if doid in dict_external_ids_monDO:
            if len(dict_external_ids_monDO[doid]) > 1:
                list_of_name_mapped_mondo_ids=[]
                for mondo_id in  dict_external_ids_monDO[doid]:
                    mondo_names=dict_mondo_id_to_name[mondo_id]
                    for mondo_name in mondo_names:
                        if mondo_name==name:
                            list_of_name_mapped_mondo_ids.append(mondo_id)
                if len(list_of_name_mapped_mondo_ids)==1:
                    dict_external_ids_monDO[doid]=list_of_name_mapped_mondo_ids
                else:
                    if doid  in dict_doid_to_multi_remove:
                        test=list(set(dict_external_ids_monDO[doid]).difference(dict_doid_to_multi_remove[doid]))
                        dict_external_ids_monDO[doid] = list(set(dict_external_ids_monDO[doid]).difference(dict_doid_to_multi_remove[doid]))
                if len(dict_external_ids_monDO[doid]) > 1:
                    print(doid)
                    print(dict_external_ids_monDO[doid])
                    print(list_of_name_mapped_mondo_ids)
                    print('multiple mondo map to the same ')
                    sys.exit('multiple mondo map to the same ')
            for monDO in dict_external_ids_monDO[doid]:
                # check if they have the same names
                monDOname = dict_monDO_info[monDO]['name'].lower() if 'name' in dict_monDO_info[monDO] else ''

                do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '') if 'name' in dict_DO_to_info[
                    doid] else ''
                if monDOname != do_name:
                    counter_name_not_matching += 1
                    csv_not_direct_name_matching_file.writerow([
                        monDO, doid, monDOname, do_name])

                # fill the dictionary monDo to DO
                if monDO in dict_monDo_to_DO:
                    dict_monDo_to_DO[monDO].add(doid)
                    if monDO in dict_monDo_to_DO_only_doid:
                        dict_monDo_to_DO_only_doid[monDO].add(doid)
                    else:
                        dict_monDo_to_DO_only_doid[monDO] = set([doid])
                else:
                    dict_monDo_to_DO[monDO] = set([doid])
                    dict_monDo_to_DO_only_doid[monDO] = set([doid])

                # fill mapping doid to mondo
                if doid in dict_DO_to_monDOs:
                    dict_DO_to_monDOs[doid].add(monDO)
                    dict_DO_to_monDOs_only_DO[doid].add(monDO)
                else:
                    dict_DO_to_monDOs[doid] = set([monDO])
                    dict_DO_to_monDOs_only_DO[doid] = set([monDO])
        # use of the alternative doids to map monDo and DO
        else:
            found_with_alternative = False
            for alternative_doid in dict_do_to_alternative_do[doid]:
                if alternative_doid in dict_external_ids_monDO:
                    found_with_alternative = True

                    for monDO in dict_external_ids_monDO[alternative_doid]:
                        monDOname = dict_monDO_info[monDO]['name'].lower()
                        do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '')
                        if monDOname != do_name:
                            counter_name_not_matching += 1
                            csv_not_direct_name_matching_file.writerow([
                                monDO, doid, dict_monDO_info[monDO]['name'],
                                dict_DO_to_info[doid]['name']])
                        # fill the dictionary monDo to DO
                        if monDO in dict_monDo_to_DO:
                            dict_monDo_to_DO[monDO].add(doid)
                            if monDO in dict_monDo_to_DO_only_doid:
                                dict_monDo_to_DO_only_doid[monDO].add(doid)
                            else:
                                dict_monDo_to_DO_only_doid[monDO] = set([doid])
                        else:
                            dict_monDo_to_DO[monDO] = set([doid])
                            dict_monDo_to_DO_only_doid[monDO] = set([doid])

                        # fill mapping doid to mondo
                        if doid in dict_DO_to_monDOs:
                            dict_DO_to_monDOs[doid].add(monDO)
                            dict_DO_to_monDOs_only_DO[doid].add(monDO)
                        else:
                            dict_DO_to_monDOs[doid] = set([monDO])
                            dict_DO_to_monDOs_only_DO[doid] = set([monDO])
            # if a doid is not mapped to mondo it is add to a list
            if not found_with_alternative:
                list_of_not_mapped_doids.append(doid)

    print('Number of DOIDs:' + str(len(dict_DO_to_xref)))
    print('number of not name matching mappes:' + str(counter_name_not_matching))
    print('number of mapped doids with only doids:' + str(len(dict_DO_to_monDOs_only_DO)))
    # print('number of mapped doids:' + str(len(dict_DO_to_monDOs_only_DO)))

    print('number of mapped monDO with only doids:' + str(len(dict_monDo_to_DO_only_doid)))
    # print('number of mapped monDO:' + str(len(dict_monDo_to_DO)))

    # generate file with not mapped doids
    file_not_mapped_doids = open('output/not_mapped_DOIDs.txt', 'w', encoding='utf-8')
    file_not_mapped_doids.write('doid \t name \n')
    for doid in list_of_not_mapped_doids:
        file_not_mapped_doids.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')

    file_not_mapped_doids.close()

    # file for multiple mapped monDO IDs
    file_mondo_to_multiple_doids = open('output/multiple_doids_for_monDO.tsv', 'w')
    file_mondo_to_multiple_doids.write('monDO\t monDO name\t doids \t doid names\n')
    for monDO, doids in dict_monDo_to_DO_only_doid.items():
        if len(doids) > 1:
            text = monDO + '\t' + dict_monDO_info[monDO]['name'] + '\t' + '|'.join(doids) + '\t'
            for doid in doids:
                text = text + dict_DO_to_info[doid]['name'] + '|'
            file_mondo_to_multiple_doids.write(text[0:-1] + '\n')


'''
Generate mapping files
'''


def mapping_files():
    multi_mondo_for_do = open('mapping/multi_mondo_for_a_doid.tsv', 'w', encoding='utf-8')
    csv_multi_mondp_for_do=csv.writer(multi_mondo_for_do, delimiter='\t')
    csv_multi_mondp_for_do.writerow(['doid','name','mondos','mondo_names'])
    for doid, mondos in dict_DO_to_monDOs_only_DO.items():
        f = open('mapping/Do_to_monDO/' + doid + '.txt', 'w', encoding='utf-8')
        name = dict_DO_to_info[doid]['name'] if 'name' in dict_DO_to_info[doid] else ''
        f.write(doid + '\t' + name + '\n')
        f.write('monDO ID \t name \n')
        if len(mondos) > 1:
            string_mondos = ",".join(mondos)
            line = doid + '\t' + name + '\t' + string_mondos + '\t'
            liste_names = []
            for mondo in mondos:
                liste_names.append(dict_monDO_info[mondo]['name'])
            list_name_string = ",".join(liste_names)
            csv_multi_mondp_for_do.writerow([line , list_name_string ])
        for mondo in mondos:
            mondo_name = dict_monDO_info[mondo]['name'] if 'name' in dict_monDO_info[mondo] else ''
            f.write(mondo + '\t' + mondo_name + '\n')
        f.close()

    for monDo, doids in dict_monDo_to_DO_only_doid.items():
        g = open('mapping/monDO_to_DO/without_xref/' + monDo + '.txt', 'w', encoding='utf-8')
        mondo_name = dict_monDO_info[mondo]['name'] if 'name' in dict_monDO_info[mondo] else ''
        g.write(monDo + '\t' + mondo_name + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + name + '\n')
        g.close()


# dictionary of the doids which are merged  into one, key is the merged id and value are the nodes which are integrated
# into the merged node
dict_merged_nodes = {}

# dictionary of self decision which doid is the merged node
dict_self_decision_mondo_multiple_doid = {
    'MONDO:0001561': 'DOID:12639',
    'MONDO:0010626': 'DOID:6620',
    'MONDO:0003061': 'DOID:461',
    'MONDO:0006639': 'DOID:660'
}

'''
This get an dictionary and preperate this that it can be integrated into the csv file
'''


def prepare_dict_for_csv_file(info):
    # dictionary of the integrated information
    dict_info_csv = {}

    for key, property in info.items():

        # if key in list_properties_which_should_be_an_array:
        if type(property) == list:
            list_of_list_prop.add(key)
            property_string = '|'.join(property)
            dict_info_csv[key] = property_string

            if len(property) > 0 and type(property[0]) == int:
                print('int list')
                print(property)
        else:
            # query = query + ''' n.%s="%s",'''
            # query = query % (key, property)
            if type(property) == int:
                print('int')
                print(key)
            dict_info_csv[key] = property
    return dict_info_csv


'''
divide list of external identifier into general and umls
'''


def divide_external_list(monDO_xref):
    umls_cuis_monDO = set()
    other_xrefs_monDO = set()
    if type(monDO_xref) == list:
        for ref in monDO_xref:
            if ref[0:4] == 'UMLS':
                umls_cuis_monDO.add(ref)
            other_xrefs_monDO.add(ref)
    else:
        if monDO_xref[0:4] == 'UMLS':
            umls_cuis_monDO.add(monDO_xref)
        other_xrefs_monDO.add(monDO_xref)

    umls_cuis_monDO.remove('') if '' in umls_cuis_monDO else umls_cuis_monDO

    other_xrefs_monDO.remove('') if '' in other_xrefs_monDO else other_xrefs_monDO

    return umls_cuis_monDO, other_xrefs_monDO


'''
First gather the do and mondo information and combine them to one
then prepare the dictionary for putting the combined data of mondo and do into the csv file 
'''


def gather_information_of_mondo_and_do_then_prepare_dict_for_csv(monDo, info, monDO_xref):
    doid = list(dict_monDo_to_DO_only_doid[monDo])[0]
    # if doid =='DOID:0060073':
    #     print('ohe')
    if monDo == 'MONDO:0006883':
        print('fjfjfjf')
    monDO_synonyms = info['synonyms'] if 'synonyms' in info else []
    monDo_def = info['definition'] if 'definition' in info else ''

    umls_cuis_monDO, other_xrefs_monDO = divide_external_list(monDO_xref)

    # combined information from monDO and DO
    do_synonyms = dict_DO_to_info[doid]['synonyms'] if 'synonyms' in dict_DO_to_info[doid] else []
    if type(monDO_synonyms) == list:

        monDO_synonyms.extend(do_synonyms)
    else:
        do_synonyms.append(monDO_synonyms)
        monDO_synonyms = dict_DO_to_info[doid]['synonyms'] if 'synonyms' in dict_DO_to_info[doid] else []
    info['synonyms'] = monDO_synonyms

    # prepare definition
    info['definition'] = dict_DO_to_info[doid]['definition'] + '[FROM DOID]. ' + monDo_def if 'definition' in \
                                                                                              dict_DO_to_info[
                                                                                                  doid] else monDo_def
    info['definition'] = info['definition'].replace('\t',' ')

    alternative_ids = dict_DO_to_info[doid]['alternative_ids'] if 'alternative_ids' in dict_DO_to_info[doid] else []
    alternative_ids.append(doid)

    # the alternative id get at least a ''  if their exist no alternative id, that's why they had to be
    # removed from the list
    if alternative_ids[0] == '':
        alternative_ids.remove('')
    info['doids'] = alternative_ids

    other_xrefs_monDO= other_xrefs_monDO.union(dict_DO_to_xref[doid])
    other_xrefs_monDO.remove('') if '' in other_xrefs_monDO else other_xrefs_monDO

    other_xrefs_monDO = go_through_xrefs_and_change_if_needed_source_name(
        other_xrefs_monDO, 'Disease')
    info['xrefs'] = list(other_xrefs_monDO)

    doid_umls = dict_DO_to_info[doid]['umls_cuis'] if 'umls_cuis' in dict_DO_to_info[doid] else []
    umls_cuis_monDO.union(doid_umls)
    umls_cuis_monDO.remove('') if '' in umls_cuis_monDO else umls_cuis_monDO
    info['umls_cuis'] = list(umls_cuis_monDO)


    dict_info_csv = prepare_dict_for_csv_file(info)
    dict_info_csv['doid'] = doid
    csv_map_nodes.writerow(dict_info_csv)


# bash shell for merge doids into the mondo nodes
bash_shell = open('merge_nodes.sh', 'w', encoding='utf-8')
bash_start='''#!/bin/bash
#define path to neo4j bin
path_neo4j=$1\n\n'''
bash_shell.write(bash_start)

'''
integrate mondo into hetionet and change identifier
'''


def integrate_mondo_change_identifier():
    counter_new_nodes = 0
    counter_switched_nodes = 0
    counter_merge_nodes = 0

    for monDo, info in dict_monDO_info.items():

        if monDo == 'MONDO:0006883':
            print('fjfjfjf')

        monDO_xref = info['xrefs'] if 'xrefs' in info else []
        # one to one mapping of mondo and do or specific mapped one-to-one from me
        if (monDo in dict_monDo_to_DO_only_doid and len(
                dict_monDo_to_DO_only_doid[monDo]) == 1):
            # print('one to one')
            counter_switched_nodes += 1

            gather_information_of_mondo_and_do_then_prepare_dict_for_csv(monDo, info, monDO_xref)

        # if has more than one doid than they have to be merge into one node
        elif monDo in dict_monDo_to_DO_only_doid:
            # print('one to many')
            counter_switched_nodes += 1
            counter_merge_nodes += 1

            dict_merged_nodes[monDo] = []

            doid_with_same_name = ''
            # get the different information from monDO which will be combined
            doids = list(dict_monDo_to_DO_only_doid[monDo])
            doid_1 = doids[0]
            doids.remove(doid_1)

            # for the other doids make a shell file

            found_doid_with_same_name = False
            for doid in doids:
                dict_merged_nodes[monDo].append(doid)
                text = 'python ../add_info_from_removed_node_to_other_node.py %s %s %s\n' % (
                doid, monDo, 'Disease')
                bash_shell.write(text)
                text = '$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher \n\n'
                bash_shell.write(text)
                text = '''now=$(date +"%F %T")
                    echo "Current time: $now"\n'''
                bash_shell.write(text)
                if dict_DO_to_info[doid]['name'] == info['name']:
                    doid_with_same_name = doid
                    found_doid_with_same_name = True
                elif monDo in dict_self_decision_mondo_multiple_doid:
                    if not found_doid_with_same_name:
                        doid_with_same_name = dict_self_decision_mondo_multiple_doid[monDo]
            # if doid_with_same_name == '':
            #     print(monDo)
            #     print(info['name'])
            #     print(doids)
            # continue

            gather_information_of_mondo_and_do_then_prepare_dict_for_csv(monDo, info, monDO_xref)


        # this is when a new node is generated
        else:
            # print('new')
            counter_new_nodes += 1

            umls_cuis_monDO, other_xrefs_monDO = divide_external_list(monDO_xref)
            info['umls_cuis'] = umls_cuis_monDO
            other_xrefs_monDO = go_through_xrefs_and_change_if_needed_source_name(
                other_xrefs_monDO, 'Disease')
            info['xrefs'] = other_xrefs_monDO

            dict_info_csv = {}

            for key, property in info.items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    list_of_list_prop.add(key)
                    property_string = '|'.join(property)
                    dict_info_csv[key] = property_string

                    if len(property) > 0 and type(property[0]) == int:
                        print('int list')
                        print(property)
                elif type(property) == set:
                    list_of_list_prop.add(key)
                    property = list(property)
                    property_string = '|'.join(property)
                    dict_info_csv[key] = property_string

                    if len(property) > 0 and type(property[0]) == int:
                        print('int list')
                        print(property)
                else:
                    if key == 'id':
                        continue
                    if type(property) == int:
                        print('int')
                        print(key)
                    dict_info_csv[key] = property
            csv_new_nodes.writerow(dict_info_csv)

    print('number of new nodes:' + str(counter_new_nodes))
    print('number of switched nodes:' + str(counter_switched_nodes))
    print(datetime.datetime.utcnow())

    print(dict_merged_nodes)
    print(len(dict_merged_nodes))


'''
add the rela information into
'''


def generate_csv_file_for_relationship():
    # query to get the rela information
    query = ''' Match (a)-[r:is_a]->(b) Return a.identifier, b.identifier, r'''
    results = g.run(query)

    # counter of relationship
    counter_of_relationships = 0

    # go through all rela and add the information into the csv file
    for child_id, parent_id, rela, in results:
        counter_of_relationships += 1
        csv_rela.writerow([child_id, parent_id])

    print('number of relationships:' + str(counter_of_relationships))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate list of non human disease')

    get_all_non_human_ids()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather all properties from mondo and put them as header into the csv files ')

    get_mondo_properties_and_generate_csv_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in DO diseases and map with DOID ')

    load_in_all_DO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate the mapping files ')

    mapping_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate and switch the nodes but ignore the multiple mapped monDO ids ')

    integrate_mondo_change_identifier()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate cypher file')

    generate_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate cypher file for subclassof relationship  ')

    generate_csv_file_for_relationship()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
