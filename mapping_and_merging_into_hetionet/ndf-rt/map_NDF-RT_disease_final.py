# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:15:37 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys

sys.path.append('../ersatz_aeolus/')
from synonyms_cuis import search_for_synonyms_cuis

import xml.dom.minidom as dom


class DiseaseHetionet:
    """
    identifier: string (doid)
    umls_cuis: list
    xrefs: list (external identifier like mesh or omim)
    synonyms: list (synonym names) 
    resource: list
    """

    def __init__(self, identifier, synonyms, umls_cuis, xrefs, resource):
        self.identifier = identifier
        self.umls_cuis = umls_cuis
        self.xrefs = xrefs
        self.synonyms = synonyms
        self.resource = resource


class DiseaseNDF_RT:
    """
    code: string 
    name: string
    properties: list (like identifier or synonyms
    umls_cuis: list
    diseaseOntology_id: strin
    """

    def __init__(self, code, name, properties, umls_cuis):
        self.code = code
        self.name = name
        self.properties = properties
        self.umls_cuis = umls_cuis

    def set_diseaseOntology_id(self, diseaseOntology_id):
        self.diseaseOntology_id = diseaseOntology_id

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with DO_id as key and class DiseaseHetionet as value
dict_diseases_hetionet = {}

# dictionary with code as key and value is class DiseaseNDF_RT
dict_diseases_NDF_RT = {}

# dictionary with name/synonyms to doid
dict_name_synonym_to_do_id = {}

# list with all names and synonyms of disease ontology
list_name_synonyms = []

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')


'''
load in all diseases from hetionet in a dictionary in a dictionary and  generate dictionary and list with all names and synonyms
'''


def load_hetionet_diseases_in():
    query = '''MATCH (n:Disease) RETURN n.identifier,n.name, n.synonyms, n.xrefs, n.umls_cuis, n.resource'''
    results = g.run(query)

    for identifier, name, synonyms, xrefs, umls_cuis, resource, in results:
        umls_cuis_without_label = []
        dict_name_synonym_to_do_id[name.lower()] = identifier
        list_name_synonyms.append(name)
        for umls_cui in umls_cuis:
            if len(umls_cui) > 0:
                umls_cuis_without_label.append(umls_cui.split(':')[1])
        for synonym in synonyms:
            synonym = synonym.split(':')[0].lower()
            dict_name_synonym_to_do_id[synonym] = identifier
            list_name_synonyms.append(synonym)
        disease = DiseaseHetionet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_diseases_hetionet[identifier] = disease
    print('length of disease in hetionet:' + str(len(dict_diseases_hetionet)))


'''
load in all diseases from ndf-rt in a dictionary and get all umls cuis
'''


def load_ndf_rt_diseases_in():
    query = '''MATCH (n:NDF_RT_disease) RETURN n'''
    results = g.run(query)
    i = 0
    for result, in results:
        code = result['code']
        properties = result['properties']
        name = result['name'].lower()
        properties = properties.split(',')
        umls_cuis = []
        for prop in properties:
            if prop[0:8] == 'UMLS_CUI':
                cui = prop
                umls_cuis.append(cui.split(':')[1])
        disease = DiseaseNDF_RT(code, name, properties, umls_cuis)
        dict_diseases_NDF_RT[code] = disease
        i += 1
    print('length of disease in ndf-rt:' + str(len(dict_diseases_NDF_RT)))


# dictionary with code as key and value is a list of disease ontology ids
dict_mapped = {}
# list of codes which are not mapped to disease ontology ids
list_code_not_mapped = []

# files for the how_mapped
map_direct_cui_cui = open('disease/ndf_rt_disease_cui_cui_map.tsv', 'w')
map_direct_cui_cui.write('code in NDF-RT \t name in NDF-RT \t DO ids with | as seperator  \n')

map_direct_name = open('disease/ndf_rt_disease_name_name_synonym_map.tsv', 'w')
map_direct_name.write('code in NDF-RT \t name in NDF-RT \t DO ids with | as seperator  \n')

map_synonym_cuis = open('disease/ndf_rt_disease_synonyms_map.tsv', 'w')
map_synonym_cuis.write('code in NDF-RT \t name in NDF-RT \t DO ids with | as seperator  \n')

'''
first round of map:
go through all diseases from hetionet and check if the umls cuis  are the same to the 
ndf-rt diseases
'''


def map_with_cuis_go_through_all():
    for key, diseaseHetionet in dict_diseases_hetionet.items():
        cuis_hetionet = diseaseHetionet.umls_cuis
        if not cuis_hetionet == None:

            cuis_hetionet = set(cuis_hetionet)
            for code, diseaseNdf_rt in dict_diseases_NDF_RT.items():
                cuis_ndf_rt = diseaseNdf_rt.umls_cuis

                cuis_ndf_rt = set(cuis_ndf_rt)
                intersection = list(cuis_ndf_rt & cuis_hetionet)
                if len(intersection) > 0:
                    dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis from rdf-rt and hetionet')
                    if not code in dict_mapped:
                        dict_mapped[code] = [key]
                    else:
                        dict_mapped[code].append(key)

    print('number of mapped:' + str(len(dict_mapped)))
    for code in dict_diseases_NDF_RT.keys():
        if not code in dict_mapped:
            list_code_not_mapped.append(code)
        else:
            string_do_ids = '|'.join(dict_mapped[code])
            map_direct_cui_cui.write(code + '\t' + dict_diseases_NDF_RT[code].name + '\t' + string_do_ids + '\n')
    print('number of not mapped:' + str(len(list_code_not_mapped)))


'''
map the name of ndf-rt disease to name or synonym of disease ontology
'''


def map_with_name():
    delete_map_code = []
    for label in list_name_synonyms:
        for code in list_code_not_mapped:
            name = dict_diseases_NDF_RT[code].name.split(' [')[0]
            label = label.lower()
            label_split = label.split(' exact')[0]
            if name.lower() == label_split:
                dict_diseases_NDF_RT[code].set_how_mapped('direct map with name')
                delete_map_code.append(list_code_not_mapped.index(code))
                if not code in dict_mapped:
                    dict_mapped[code] = [dict_name_synonym_to_do_id[label]]
                else:
                    dict_mapped[code].append(dict_name_synonym_to_do_id[label])

    delete_map_code = list(set(delete_map_code))
    delete_map_code.sort()
    delete_map_code = list(reversed(delete_map_code))
    for index in delete_map_code:
        code = list_code_not_mapped.pop(index)
        string_do_ids = '|'.join(dict_mapped[code])
        map_direct_name.write(code + '\t' + dict_diseases_NDF_RT[code].name + '\t' + string_do_ids + '\n')

    print('number of mapped:' + str(len(dict_mapped)))
    print('number of not mapped:' + str(len(list_code_not_mapped)))


# dictionary with code as key and synonym cuis as value
dict_code_synonym_cuis = {}
'''
finde all synonym umls cuis from the one that did not map and save them in a dictionary
'''


def find_synonym_cuis_for_ndf_rt_not_mapped():
    for code in list_code_not_mapped:
        cuis = dict_diseases_NDF_RT[code].umls_cuis
        new_cuis = []
        for cui in cuis:
            new_cuis.append(cui)
        cuis = search_for_synonyms_cuis(new_cuis)
        dict_code_synonym_cuis[code] = cuis


'''
second round:
go through all disease from hetionet and check the synonym cuis from the one 
that did not mapped bevore
'''


def map_with_synonyms_from_code():
    # all ndf-rt codes which are mapped to doid in this step
    delete_list = []
    for key, diseaseHetionet in dict_diseases_hetionet.items():

        cuis_hetionet = diseaseHetionet.umls_cuis
        if not cuis_hetionet == None and len(cuis_hetionet) != 0:

            cuis_hetionet = set(cuis_hetionet)
            for code, cuis_ndf_rt in dict_code_synonym_cuis.items():
                if len(cuis_ndf_rt) > 0:
                    cuis_ndf_rt = set(cuis_ndf_rt)
                    intersection = list(cuis_ndf_rt & cuis_hetionet)
                    if len(intersection) > 0:
                        dict_diseases_NDF_RT[code].set_how_mapped('map synonyms cuis')
                        indice = list_code_not_mapped.index(code)
                        delete_list.append(indice)
                        if not code in dict_mapped:
                            dict_mapped[code] = [key]
                        else:
                            dict_mapped[code].append(key)

    print('number of mapped:' + str(len(dict_mapped)))
    # remove all mapped ndf-rt codes from the not map list
    delete_list.sort()
    delete_list = list(set(delete_list))
    delete_list = list(reversed(delete_list))
    for index in delete_list:
        code = list_code_not_mapped.pop(index)
        string_do_ids = '|'.join(dict_mapped[code])
        map_synonym_cuis.write(code + '\t' + dict_diseases_NDF_RT[code].name + '\t' + string_do_ids + '\n')
    print('number of not mapped:' + str(len(list_code_not_mapped)))
    print(list_code_not_mapped)


# generate file with code and a list of DO ids and where there are from
multiple_DO_ids = open('ndf_rt_multiple_DO_ids.tsv', 'w')
multiple_DO_ids.write('ndf-rt code \t DO_ids with | as seperator \t where are it from  \t name\n')

'''
this integrate only properties into hetionet for the one that are mapped,
because all data from disease ontology are integrated
all Disease which are not mapped with a ndf-rt disease get the propertie no
'''


def integrate_ndf_rt_disease_into_hetionet():
    for code, dO_ids in dict_mapped.items():
        do_id_string = "','".join(dO_ids)
        how_mapped = dict_diseases_NDF_RT[code].how_mapped
        if len(dO_ids) > 1:
            string_do_ids = "|".join(dO_ids)
            multiple_DO_ids.write(
                code + '\t' + string_do_ids + '\t' + how_mapped + '\t' + dict_diseases_NDF_RT[code].name + '\n')

        query = '''MATCH (n:NDF_RT_disease{code:'%s'}) Set n.DO_IDs=['%s'], n.how_mapped='%s', n.number_of_mapping='%s' '''
        query = query % (code, do_id_string, how_mapped, str(len(dO_ids)))
        g.run(query)
        for do_id in dO_ids:
            resource = dict_diseases_hetionet[do_id].resource
            resource.append('NDF-RT')
            resource = list(set(resource))
            resource = "','".join(resource)
            query = '''MATCH (n:NDF_RT_disease{code:'%s'}), (d:Disease{identifier:'%s'}) 
            Set d.resource=['%s'], d.ndf_rt='yes' 
            Create (d)-[:equal_to_Disease_NDF_RT]->(n);           
            '''
            query = query % (code, do_id, resource)
            g.run(query)

    # search for all disease that did not mapped with ndf-rt and give them the property ndf_rt:'no'
    query = '''MATCH (n:Disease) Where Not Exists(n.ndf_rt) RETURN n.identifier '''
    results = g.run(query)
    for cui, in results:
        query = '''MATCH (n:Disease{identifier:"%s"}) 
        Set n.ndf_rt='no' '''
        query = query % (cui)
        g.run(query)

    # search for all ndf-rt disease that did not mapped with DO and give them the property DO_IDs=[]
    query = '''MATCH (n:NDF_RT_disease) Where Not Exists(n.DO_IDs) 
        Set n.DO_IDs=[] '''
    g.run(query)


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in diseases from hetionet')

    load_hetionet_diseases_in()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in diseases from ndf-rt')

    load_ndf_rt_diseases_in()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map round one, check the cuis from disease ontology to cuis in ndf-rt')

    map_with_cuis_go_through_all()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map with name ndf-rt to name or synonym od DO')

    map_with_name()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('search for synonym cuis for ndf-rt diseases which did not mapped')

    find_synonym_cuis_for_ndf_rt_not_mapped()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map round two, check the cuis from disease ontology to synonym cuis in ndf-rt')

    map_with_synonyms_from_code()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('integrate ndf-rt into hetionet')

    integrate_ndf_rt_disease_into_hetionet()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
