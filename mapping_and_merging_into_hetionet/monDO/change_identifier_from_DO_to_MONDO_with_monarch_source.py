# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import sys, csv
import datetime
from types import *

reload(sys)
sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


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

#mondo properties
mondo_prop=[]

# dictionary of properties which are named different in mondo in comparision to hetionet

dict_switch_mondo_prop_to_hetionet = {'hasDbXref': 'xrefs', 'synonym': 'synonyms','label':'name','id':'identifier'}

#list of excluded properties from mondo
list_exclude_properties=['related','creation_date','created_by','seeAlso']



'''
Get all properties of the mondo disease and create the csv files
'''
def get_mondo_properties_and_generate_csv_files():
    query='''MATCH (p:disease) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''
    result=g.run(query)
    for property , in result:
        if property[0:4]=='http':
            if '#' in property:
                property=property.split('#',-1)[1]
            else:
                continue
        if property in dict_switch_mondo_prop_to_hetionet:
            property=dict_switch_mondo_prop_to_hetionet[property]
        # exclude the properties from csv files
        elif property in list_exclude_properties:
            continue
        mondo_prop.append(property)

    #mondo get an additional property
    mondo_prop.append('umls_cuis')

    # generate csv files
    global csv_new_nodes, csv_map_nodes, csv_rela
    # csv with new nodes
    new_node_file=open('output/new_nodes.csv','w')
    csv_new_nodes=csv.DictWriter(new_node_file, delimiter='\t',fieldnames=mondo_prop)
    csv_new_nodes.writeheader()

    #csv with nodes which needs to be updated
    map_node_file=open('output/map_nodes.csv','w')
    mondo_prop_mapped=mondo_prop[:]
    mondo_prop_mapped.append('doid')
    mondo_prop_mapped.append('doids')
    csv_map_nodes=csv.DictWriter(map_node_file, delimiter='\t',fieldnames=mondo_prop_mapped)
    csv_map_nodes.writeheader()

    #csv with relatioships
    rela_file=open('output/rela.csv','w')
    csv_rela=csv.writer(rela_file,delimiter='\t')
    csv_rela.writerow(['id_1','id_2','equivalentOriginalNodeSourceTarget'])


'''
fill the dictionary with external identifier 
'''
def fill_dict_with_external_identifier_to_mondo(xrefs,monDo_id):
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


'''
Load MonDO disease in dictionary
Where n.`http://www.geneontology.org/formats/oboInOwl#id` ='MONDO:0010168'
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:disease)  RETURN n'''
    results = g.run(query)
    for disease, in results:
        monDo_id = disease['http://www.geneontology.org/formats/oboInOwl#id']
        if monDo_id=='MONDO:0006464':
            print('ohje')
        # if monDo_id == 'MONDO:0007062':
        #     print('blub')
        disease_info={}
        for key,property in dict(disease).items():
            if key[0:4]=='http':
                if '#' in key:
                    key=key.split('#',-1)[1]
                else:
                    continue
            disease_info[key]=property
        dict_monDO_info[monDo_id] = disease_info
        xrefs = disease_info['hasDbXref'] if 'hasDbXref' in disease_info else []
        print(monDo_id)
        fill_dict_with_external_identifier_to_mondo(xrefs,monDo_id)

        possible_xref = disease_info['hasAlternativeId'] if 'hasAlternativeId' in disease_info else []
        fill_dict_with_external_identifier_to_mondo(possible_xref,monDo_id)



# cypher file to integrate mondo
cypher_file=open('cypher.cypher','w')


# a cypher file to add the merged id to the other doids
cypher_file_end=open('cypher_end.cypher','w')


# list_properties in mondo
list_of_list_prop=set([])


'''
generate cypher queries to integrate and merge disease nodes and create the subclass relationships
'''
def generate_cypher_queries():
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/monDO/output/%s.csv" As line FIELDTERMINATOR '\\t' Match (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.identifier}) '''

    query_end='''Create (n)-[:equal_to_monDO]->(a); \n'''
    query_update=''
    query_new=''
    for property in mondo_prop:
        if property not in list_of_list_prop:
            query_new+= property+':line.'+property+', '
            query_update += 'n.'+property + '=line.' + property + ', '
        else:
            query_new += property + ':split(line.' + property + ', "|"), '
            query_update += 'n.'+property + '=split(line.' + property + ', "|"), '
    query_update=query_start+ ', (n:Disease{identifier:line.doid}) Set '+ query_update+ 'n.mondo="yes", n.license=" CC-BY-SA 3.0", n.resource=n.resource+"MonDo", n.doids=split(line.doids,"|") '+ query_end
    query_update=query_update %('map_nodes')
    cypher_file.write(query_update)
    query_new=query_start+ 'Create (n:Disease{'+query_new+'mondo:"yes", resource:["MonDO"], url:"http://bioportal.bioontology.org/ontologies/MONDO/"+line.id, license:" CC-BY-SA 3.0", source:"MonDO"}) '+query_end
    query_new=query_new %('new_nodes')
    cypher_file.write(query_new)
    query_rela = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/monDO/output/%s.csv" As line FIELDTERMINATOR '\\t' Match (a:Disease{identifier:line.id_1}), (b:Disease{identifier:line.id_2}) Create (a)-[:SUBCLASS_OF_DsoD{unbiased:"false", source:"Monarch Disease Ontology", resource:['MonDO'] , mondo:'yes', license:" CC-BY-SA 3.0", equivalentOriginalNodeSourceTarget:split(line.equivalentOriginalNodeSourceTarget,'|')}]->(b);\n'''
    query_rela= query_rela %('rela')
    cypher_file.write(query_rela)

    #query to delete disease which are not in Mondo
    query = '''Match (d:Disease) Where not exists(d.mondo) Detach Delete d;\n'''
    cypher_file.write(query)

    # add the disease ontology property to the nodes without
    query = '''Match (d:Disease) Where not exists(d.diseaseOntology) Set d.diseaseOntology='no' ;\n'''
    cypher_file.write(query)

    #combin merged id with doids
    query = '''MATCH (n:Disease) Where exists(n.merged_identifier) Set n.doids=n.doids+ n.merged_identifier Remove n.merged_identifier;\n'''
    cypher_file_end.write(query)





'''
Load in all disease ontology ids with external identifier and alternative id
also check for mapping between do and mondo
'''


def load_in_all_DO_in_dictionary():
    # file mapped doid but not the same name
    not_direct_name_matching_file = open('not_direct_name_matching_file.tsv', 'w')
    not_direct_name_matching_file.write('monDO \t DOID \t name monDO \t name DOID \n')
    counter_name_not_matching = 0

    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for disease, in results:
        doid = disease['identifier']
        # if doid == 'DOID:0060073':
        #     print('ok')
        dict_DO_to_info[doid] = dict(disease)
        alternative_id = disease['alternative_ids'] if 'alternative_ids' in disease else []
        dict_do_to_alternative_do[doid] = alternative_id

        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        # i do not know why I did this??????
        # xrefs = xrefs[0].replace("'","").split(',')
        dict_DO_to_xref[doid] = xrefs
        if doid in dict_external_ids_monDO:
            if len(dict_external_ids_monDO[doid])>1:
                print(doid)
                print(dict_external_ids_monDO[doid])
                sys.exit('multiple mondo map to the same ')
            for monDO in dict_external_ids_monDO[doid]:
                # check if they have the same names
                monDOname = dict_monDO_info[monDO]['label'].lower() if 'label' in dict_monDO_info[monDO] else ''

                do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '') if 'name' in dict_DO_to_info[doid] else ''
                if monDOname != do_name:
                    counter_name_not_matching += 1
                    not_direct_name_matching_file.write(
                        monDO + '\t' + doid + '\t' + monDOname + '\t' + do_name + '\n')

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
            for alternativ_doid in dict_do_to_alternative_do[doid]:
                if alternativ_doid in dict_external_ids_monDO:
                    found_with_alternative = True

                    for monDO in dict_external_ids_monDO[alternativ_doid]:
                        monDOname = dict_monDO_info[monDO]['label'].lower()
                        do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '')
                        if monDOname != do_name:
                            counter_name_not_matching += 1
                            not_direct_name_matching_file.write(
                                monDO + '\t' + doid + '\t' + dict_monDO_info[monDO]['label'] + '\t' +
                                dict_DO_to_info[doid][
                                    'name'] + '\n')
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
    file_not_mapped_doids = open('not_mapped_DOIDs.txt', 'w')
    file_not_mapped_doids.write('doid \t name \n')
    for doid in list_of_not_mapped_doids:
        file_not_mapped_doids.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')

    file_not_mapped_doids.close()

    # file for multiple mapped monDO IDs
    file_mondo_to_multiple_doids = open('multiple_doids_for_monDO.tsv', 'w')
    file_mondo_to_multiple_doids.write('monDO\t monDO name\t doids \t doid names\n')
    for monDO, doids in dict_monDo_to_DO_only_doid.items():
        if len(doids) > 1:
            text = monDO + '\t' + dict_monDO_info[monDO]['label'] + '\t' + '|'.join(doids) + '\t'
            for doid in doids:
                text = text + dict_DO_to_info[doid]['name'] + '|'
            file_mondo_to_multiple_doids.write(text[0:-1] + '\n')



'''
Generate mapping files
'''


def mapping_files():
    multi_mondo_for_do = open('mapping/multi_mondo_for_a_doid.txt', 'w')
    multi_mondo_for_do.write('doid\t name\t mondos\t mondo_names\n')
    for doid, mondos in dict_DO_to_monDOs_only_DO.items():
        f = open('mapping/Do_to_monDO/' + doid + '.txt', 'w')
        name=dict_DO_to_info[doid]['name'] if 'name' in dict_DO_to_info[doid] else ''
        f.write(doid + '\t' + name + '\n')
        f.write('monDO ID \t name \n')
        if len(mondos) > 1:
            string_mondos = ",".join(mondos)
            line = doid + '\t' + name + '\t' + string_mondos + '\t'
            liste_names = []
            for mondo in mondos:
                liste_names.append(dict_monDO_info[mondo]['label'])
            list_name_string = ",".join(liste_names)
            multi_mondo_for_do.write(line + list_name_string + '\n')
        for mondo in mondos:
            mondo_name=dict_monDO_info[mondo]['label'] if 'label' in dict_monDO_info[mondo] else ''
            f.write(mondo + '\t' + mondo_name + '\n')
        f.close()

    for monDo, doids in dict_monDo_to_DO_only_doid.items():
        g = open('mapping/monDO_to_DO/without_xref/' + monDo + '.txt', 'w')
        mondo_name = dict_monDO_info[mondo]['label'] if 'label' in dict_monDO_info[mondo] else ''
        g.write(monDo + '\t' + mondo_name + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + name + '\n')
        g.close()


# dictionary of the doids which are merged  into one, key is the merged id and value are the nodes which are integrated
# into the merged node
dict_merged_nodes = {
    'MONDO:0001504': ['DOID:1233']
# DOID:1233 (transvestism) is sub class of  fetishism and contains relationships -> merged together
}

# dictionary of self decision which doid is the merged node
dict_self_decision_mondo_multiple_doid = {
    'MONDO:0004398': 'DOID:7922',
    'MONDO:0001561': 'DOID:12639',
    'MONDO:0010626': 'DOID:6620',
    'MONDO:0003061': 'DOID:461',
    'MONDO:0016021': 'DOID:0050709',
    'MONDO:0003345': 'DOID:4927',
    'MONDO:0006639': 'DOID:660'
}

# dictionary of mondo to doid where mondo has no doid as ref but an external identifier mapped manual
dict_mondo_xref_doid_mapping = {
    'MONDO:0009700': 'DOID:0080194',
    'MONDO:0009567': 'DOID:0080195',
    'MONDO:0010771': 'DOID:0080198',
    'MONDO:0003050': 'DOID:4556',
    'MONDO:0001071': 'DOID:1059',
    'MONDO:0021199': 'DOID:7'
# disease affecting anatomical system (mondo) is more  similar to disease of anatomical entity (DOID:7) than disease (DOID:4) also same subclasses like DOID:7
}

# list of doids which are not part of mondo and are removed
list_removed_doids = ['DOID:7267', 'DOID:0060017', 'DOID:946', 'DOID:6823', 'DOID:0050332', 'DOID:8150', 'DOID:5469',
                      'DOID:0080125', 'DOID:7571', 'DOID:0060517', 'DOID:9341', 'DOID:0080193', 'DOID:0080197',
                      'DOID:0080196', 'DOID:0050875', 'DOID:0050987', 'DOID:2468', 'DOID:854']


'''
This get an dictionary and preperate this that it can be integrated into the csv file
'''
def prepare_dict_for_csv_file(info):
    # dictionary of the integrated information
    dict_info_csv = {}

    for key, property in info.items():
        # prepare key names
        if key[0:5] == 'http:':
            if '#' in key:
                key = key.split('#', -1)[1]
            else:
                continue
        if key in dict_switch_mondo_prop_to_hetionet:
            key = dict_switch_mondo_prop_to_hetionet[key]
        # the properties which are excluded from mondo
        elif key in list_exclude_properties:
            continue

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
    umls_cuis_monDO = []
    other_xrefs_monDO = []
    if type(monDO_xref) == list:
        for ref in monDO_xref:
            if ref[0:4] == 'UMLS':
                umls_cuis_monDO.append(ref)
            else:
                other_xrefs_monDO.append(ref)
    else:
        if monDO_xref[0:4] == 'UMLS':
            umls_cuis_monDO.append(monDO_xref)
        else:
            other_xrefs_monDO.append(monDO_xref)

    umls_cuis_monDO.remove('') if '' in umls_cuis_monDO else umls_cuis_monDO

    other_xrefs_monDO.remove('') if '' in other_xrefs_monDO else other_xrefs_monDO

    return umls_cuis_monDO, other_xrefs_monDO

'''
First gather the do and mondo information and combine them to one
then prepare the dictionary for putting the combined data of mondo and do into the csv file 
'''
def gather_information_of_mondo_and_do_then_prepare_dict_for_csv(monDo,info,monDO_xref):
    if not monDo in dict_mondo_xref_doid_mapping:
        doid = list(dict_monDo_to_DO_only_doid[monDo])[0]
    else:
        doid = dict_mondo_xref_doid_mapping[monDo]
    # if doid =='DOID:0060073':
    #     print('ohe')
    monDO_synonyms = info['synonym'] if 'synonym' in info else []
    monDo_def = info['definition'] if 'definition' in info else ''

    umls_cuis_monDO, other_xrefs_monDO = divide_external_list(monDO_xref)

    # combined information from monDO and DO
    do_synonyms = dict_DO_to_info[doid]['synonyms'] if 'synonyms' in dict_DO_to_info[doid] else []
    if type(monDO_synonyms) == list:

        monDO_synonyms.extend(do_synonyms)
    else:
        do_synonyms.append(monDO_synonyms)
        monDO_synonyms = dict_DO_to_info[doid]['synonyms'] if 'synonyms' in dict_DO_to_info[doid] else []
    info['synonym'] = monDO_synonyms

    info['definition'] = dict_DO_to_info[doid]['definition'] + '[FROM DOID]. ' + monDo_def if 'definition' in \
                                                                                              dict_DO_to_info[
                                                                                                  doid] else monDo_def

    alternative_ids = dict_DO_to_info[doid]['alternative_ids'] if 'alternative_ids' in dict_DO_to_info[doid] else []
    alternative_ids.append(doid)

    # the alternative id get at least a ''  if their exist no alternative id, that's why they had to be
    # removed from the list
    if alternative_ids[0] == '':
        alternative_ids.remove('')
    info['doids'] = alternative_ids

    other_xrefs_monDO.extend(dict_DO_to_xref[doid])
    other_xrefs_monDO.remove('') if '' in other_xrefs_monDO else other_xrefs_monDO
    info['hasDbXref'] = other_xrefs_monDO

    doid_umls=dict_DO_to_info[doid]['umls_cuis'] if 'umls_cuis' in dict_DO_to_info[doid] else []
    umls_cuis_monDO.extend(doid_umls)
    umls_cuis_monDO.remove('') if '' in umls_cuis_monDO else umls_cuis_monDO
    info['umls_cuis'] = list(set(umls_cuis_monDO))

    dict_info_csv = prepare_dict_for_csv_file(info)
    dict_info_csv['doid'] = doid
    csv_map_nodes.writerow(dict_info_csv)

#bash shell for merge doids into the mondo nodes
bash_shell=open('merge_nodes.sh','w')
bash_shell.write('#!/bin/bash\n')

'''
integrate mondo into hetionet and change identifier
'''


def integrate_mondo_change_identifier():
    counter_new_nodes = 0
    counter_switched_nodes = 0
    counter_merge_nodes = 0

    for monDo, info in dict_monDO_info.items():
        #problem not create
        if monDo == 'MONDO:0002087':
            print('ohje')

        #problem merge
        if monDo == 'MONDO:0001235':
            print('ohje')

        monDO_xref = info['hasDbXref'] if 'hasDbXref' in info else []
        # one to one mapping of mondo and do or specific mapped one-to-one from me
        if (monDo in dict_monDo_to_DO_only_doid and len(
                dict_monDo_to_DO_only_doid[monDo]) == 1) or monDo in dict_mondo_xref_doid_mapping:
            # print('one to one')
            counter_switched_nodes += 1

            gather_information_of_mondo_and_do_then_prepare_dict_for_csv(monDo,info,monDO_xref)

        # if has more than one doid than they have to be merge into one node
        elif monDo in dict_monDo_to_DO_only_doid:
            # print('one to many')
            counter_switched_nodes += 1
            counter_merge_nodes += 1

            dict_merged_nodes[monDo] = []

            doid_with_same_name = ''
            # get the different information from monDO which will be combined
            doids = list(dict_monDo_to_DO_only_doid[monDo])
            doid_1= doids[0]
            doids.remove(doid_1)

            #for the other doids make a shell file


            found_doid_with_same_name=False
            for doid in doids:
                dict_merged_nodes[monDo].append(doid)
                text='python ../add_information_from_a_not_existing_node_to_existing_node.py %s %s %s\n' %(doid, monDo, 'Disease')
                bash_shell.write(text)
                text='''now=$(date +"%F %T")
                    echo "Current time: $now"\n'''
                bash_shell.write(text)
                if dict_DO_to_info[doid]['name'] == info['label']:
                    doid_with_same_name = doid
                    found_doid_with_same_name=True
                elif monDo in dict_self_decision_mondo_multiple_doid:
                    if not found_doid_with_same_name:
                        doid_with_same_name = dict_self_decision_mondo_multiple_doid[monDo]
            # if doid_with_same_name == '':
            #     print(monDo)
            #     print(info['label'])
            #     print(doids)
                # continue

            gather_information_of_mondo_and_do_then_prepare_dict_for_csv(monDo,info,monDO_xref)


        # this is when a new node is generated
        else:
            # print('new')
            counter_new_nodes += 1

            umls_cuis_monDO, other_xrefs_monDO = divide_external_list(monDO_xref)
            info['umls_cuis'] = umls_cuis_monDO
            info['hasDbXref'] = other_xrefs_monDO

            dict_info_csv={}

            for key, property in info.items():
                # prepare key names
                if key[0:5] == 'http:':
                    if '#' in key:
                        key=key.split('#',-1)[1]
                    else:
                        continue

                if key in dict_switch_mondo_prop_to_hetionet:
                    key = dict_switch_mondo_prop_to_hetionet[key]
                elif key in list_exclude_properties:
                    continue

                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    list_of_list_prop.add(key)
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
    for merge_id, list_delete_nodes in dict_merged_nodes.items():

        for delete_node in list_delete_nodes:
            # one mapping is not ok from disease to disease of anatomical entity (DOID:7)
            if merge_id == 'MONDO:0000001' and delete_node == 'DOID:7':
                continue

            # merge_information_from_one_node_to_another(delete_node, merge_id, 'Disease')


    print('number of removed nodes with doid:' + str(len(list_removed_doids)))


'''
add the rela information into
'''


def generate_csv_file_for_relationship():
    # query to get the rela information
    query = ''' Match (a)-[r:subClassOf]->(b) Return a.`http://www.geneontology.org/formats/oboInOwl#id`, b.`http://www.geneontology.org/formats/oboInOwl#id`, r'''
    results = g.run(query)

    #counter of relationship
    counter_of_relationships=0

    #go through all rela and add the information into the csv file
    for child_id, parent_id, rela, in results:
        counter_of_relationships+=1
        equivalentOriginalNodeSourceTarget='|'.join(rela['equivalentOriginalNodeSourceTarget']) if 'equivalentOriginalNodeSourceTarget' in rela else ''
        csv_rela.writerow([child_id,parent_id,equivalentOriginalNodeSourceTarget])


    print('number of relationships:'+str(counter_of_relationships))



def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

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