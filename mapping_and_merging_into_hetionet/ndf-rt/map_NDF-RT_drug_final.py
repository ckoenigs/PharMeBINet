# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:15:37 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys

# sys.path.append('../Aeolus/')
sys.path.append('../aeolus/')

# from synonyms_cuis import search_for_synonyms_cuis
import get_drugbank_information

import xml.dom.minidom as dom


class DrugHetionet:
    """
    identifier: string (Drugbank ID)
    name: string
    resource: list
    """

    def __init__(self, identifier, name, resource):
        self.identifier = identifier
        self.name = name
        self.resource = resource


class DrugNDF_RT():
    """
    code: string
    name: string
    properties: list (like synonyms)
    umls_cuis: list
    drugbank_ids: list
    uniis: list
    association:string
    how_mapped: string
    """

    def __init__(self, code, properties, umls_cuis, name, rxnorm_cuis, association, nui):
        self.code = code
        self.properties = properties
        self.umls_cuis = umls_cuis
        self.drugbank_ids = []
        self.name = name
        self.rxnorm_cuis = rxnorm_cuis
        self.uniis = []
        self.association = association
        self.nui = nui

    def set_drugbank_ids(self, drugbank_ids):
        self.drugbank_ids = drugbank_ids

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with compound_id as key and class DrugHetionet as value
dict_drug_hetionet = {}

# dictionary with code as key and value is class DrugNDF_RT
dict_drug_NDF_RT = {}

# dictionary with rxcui as key and value is list of codes
dict_drug_NDF_RT_rxcui_to_code = {}

# dictionary with code as key and value is class DrugNDF_RT
dict_drug_NDF_RT_without_rxcui = {}

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

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = mdb.connect('localhost', 'root', 'Za8p7Tf', 'RxNorm')


'''
load in all compound from hetionet in a dictionary
'''


def load_hetionet_drug_in():
    query = '''MATCH (n:Compound) RETURN n.identifier,n.name, n.resource'''
    results = g.run(query)

    for identifier, name, resource, in results:
        resource = resource if resource != None else []
        drug = DrugHetionet(identifier, name, resource)
        dict_drug_hetionet[identifier] = drug
    print('length of compound in hetionet:' + str(len(dict_drug_hetionet)))


'''
load in all compound from ndf-rt in a dictionary and get the  umls cui, rxcui 
'''


def load_ndf_rt_drug_in():
    query = '''MATCH (n:NDF_RT_drug) RETURN n'''
    results = g.run(query)
    count = 0
    i = 0
    count_name_map = 0

    for result, in results:
        count += 1
        code = result['code']
        properties = result['properties']
        name = result['name']
        properties = properties.split(',')
        association = result['association'] if result['association'] != '' else ''
        umls_cuis = []
        rxnorm_cuis = []
        nui = ''
        for prop in properties:
            if prop[0:8] == 'UMLS_CUI':
                cui = prop
                umls_cuis.append(cui.split(':')[1])
            elif prop[0:10] == 'RxNorm_CUI':
                cui = prop
                rxnorm_cuis.append(cui.split(':')[1])
            elif prop[0:4] == 'NUI':
                nui = prop.split(':')[1]
        drug = DrugNDF_RT(code, properties, umls_cuis, name, rxnorm_cuis, association, nui)
        dict_drug_NDF_RT[code] = drug
        # generate dictionary with rxnorm cui as key and value list of codes
        if len(rxnorm_cuis) == 1:
            if not rxnorm_cuis[0] in dict_drug_NDF_RT_rxcui_to_code:
                dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]] = [code]
            else:
                dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]].append(code)
            i += 1
        elif len(rxnorm_cuis) == 0:
            cur = conRxNorm.cursor()
            # search for rxcui with name
            query = ("Select Distinct RXCUI From RXNCONSO Where lower(STR) = '%s' ;")
            query = query % (name.lower())
            #        print(query)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                count_name_map += 1
                rxnorm_cuis = []
                for cui, in cur:
                    rxnorm_cuis.append(cui)
                drug = DrugNDF_RT(code, properties, umls_cuis, name, rxnorm_cuis)
                if len(rxnorm_cuis) == 1:
                    if not rxnorm_cuis[0] in dict_drug_NDF_RT_rxcui_to_code:
                        dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]] = [code]
                    else:
                        dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]].append(code)
                elif len(rxnorm_cuis) == 0:
                    dict_drug_NDF_RT_without_rxcui[code] = drug
                else:
                    print('multiple rxnomrs')
            else:
                dict_drug_NDF_RT_without_rxcui[code] = drug

    print('number of all drugs from ndf-rt:' + str(count))
    print('length of compound in ndf-rt with rxcui:' + str(len(dict_drug_NDF_RT_rxcui_to_code)))
    a = True if count != len(dict_drug_NDF_RT_rxcui_to_code) else False
    print('is multiple mapping:' + str(a))
    print('length of compound in ndf-rt without rxcui:' + str(len(dict_drug_NDF_RT_without_rxcui)))
    print('number of name mapped rxcuis:' + str(count_name_map))


# list of all rxcuis which are mapped to drugbankids
list_rxcuis_with_drugbank_ids = []

# list of cuis which has no drugbank id
list_rxcuis_without_drugbank_ids = []
# list_rxcuis_without_drugbank_ids=['1741407']


# list of code which are map to a drugbank id
list_codes_with_drugbank_ids = []

'''
map rxnorm to drugbank with use of the RxNorm database
'''


def map_rxnorm_to_drugbank_use_rxnorm_database():
    i = 0
    number_of_mapped = 0
    for rxnorm_cui in dict_drug_NDF_RT_rxcui_to_code.keys():
        i += 1
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB From RXNCONSO Where SAB = 'DRUGBANK' and RXCUI= %s ;")
        rows_counter = cur.execute(query, (rxnorm_cui,))
        if rows_counter > 0:
            drugbank_ids = []
            for (rxcui, lat, code, sab,) in cur:
                drugbank_ids.append(code)
            drugbank_ids = list(set(drugbank_ids))
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            for code in codes:
                dict_drug_NDF_RT[code].set_drugbank_ids(drugbank_ids)
                dict_drug_NDF_RT[code].set_how_mapped('use rxcui to drugbank ids with rxnorm')
                if not rxnorm_cui in list_rxcuis_with_drugbank_ids:
                    list_rxcuis_with_drugbank_ids.append(rxnorm_cui)
                if not code in list_codes_with_drugbank_ids:
                    number_of_mapped += 1
                    list_codes_with_drugbank_ids.append(code)
        else:
            if not rxnorm_cui in list_rxcuis_without_drugbank_ids:
                list_rxcuis_without_drugbank_ids.append(rxnorm_cui)

    print('new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(list_rxcuis_with_drugbank_ids)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))


'''
load map rxnorm id to drugbank _id from dhimmel inchikey and use this to map the rest
properties:
    0:rxcui
    1:drugbank ids seperated with |
'''


def map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey_4.tsv', 'r')
    next(f)
    number_of_mapped = 0
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = []
    for line in f:
        splitted = line.split('\t')
        rxnorm_cui = splitted[0]
        drugbank_ids = splitted[1].split('\r')[0].split('|')
        if rxnorm_cui in list_rxcuis_without_drugbank_ids:
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            for code in codes:
                dict_drug_NDF_RT[code].set_drugbank_ids(drugbank_ids)
                dict_drug_NDF_RT[code].set_how_mapped('use rxcui to drugbank ids with unii and inchikey to drugbank')
                if not rxnorm_cui in list_rxcuis_with_drugbank_ids:
                    list_rxcuis_with_drugbank_ids.append(rxnorm_cui)
                delete_list.append(list_rxcuis_without_drugbank_ids.index(rxnorm_cui))
                if not code in list_codes_with_drugbank_ids:
                    number_of_mapped += 1
                    list_codes_with_drugbank_ids.append(code)

    # remove all new mapped rxcuis from not mapped list
    delete_list = list(set(delete_list))
    delete_list.sort()
    delete_list = list(reversed(delete_list))
    for index in delete_list:
        list_rxcuis_without_drugbank_ids.pop(index)

    print('new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(list_rxcuis_with_drugbank_ids)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))


# dictionary for unii to code
dict_unii_to_code = {}

# list of codes without a unii
list_codes_without_unii = []

'''
make a dictionary for all not mapped codes a with unii as key 
'''


def generate_dict_unii_to_code():
    count_code_unii = 0
    for rxcui in list_rxcuis_without_drugbank_ids:
        codes = dict_drug_NDF_RT_rxcui_to_code[rxcui]
        for code in codes:
            properties = dict_drug_NDF_RT[code].properties
            properties = properties
            has_unii = False
            for prop in properties:
                if prop[0:8] == 'FDA_UNII':

                    has_unii = True
                    unii = prop.split(':')[1]
                    dict_drug_NDF_RT[code].uniis.append(unii)
                    if not unii in dict_unii_to_code:
                        dict_unii_to_code[unii] = [code]
                    else:
                        dict_unii_to_code[unii].append(code)
            if not has_unii:
                list_codes_without_unii.append(code)
            else:
                count_code_unii += 1

    print('number of codes which has a unii:' + str(count_code_unii))
    print('numner of unii:' + str(len(dict_unii_to_code)))
    print('number of codes which has no unii:' + str(len(list_codes_without_unii)))


'''
find drugbank map with use of unii, map is from drugbank (generate_unii_drugbank_table_with_drugbank.py)
properties:
    0:unii 	 
    1:drugbank_id 
'''


def map_with_unii_to_drugbank():
    f = open('../drugbank/data/map_unii_to_drugbank_id.tsv', 'r')
    next(f)
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = []
    number_of_mapped = 0
    for line in f:
        splitted = line.split('\t')
        unii = splitted[0]
        drugbank_id = splitted[1].split('\r')[0]
        if unii in dict_unii_to_code:
            codes = dict_unii_to_code[unii]
            for code in codes:
                dict_drug_NDF_RT[code].set_drugbank_ids([drugbank_id])
                dict_drug_NDF_RT[code].set_how_mapped('use unii of the ndf-rt code and map to drugbank id')
                rxnorm_cuis = dict_drug_NDF_RT[code].rxnorm_cuis
                for rxnorm_cui in rxnorm_cuis:
                    if not rxnorm_cui in list_rxcuis_with_drugbank_ids:
                        list_rxcuis_with_drugbank_ids.append(rxnorm_cui)
                        delete_list.append(list_rxcuis_without_drugbank_ids.index(rxnorm_cui))
                if not code in list_codes_with_drugbank_ids:
                    number_of_mapped += 1
                    list_codes_with_drugbank_ids.append(code)

    # delete all new mapped rxcuis from not mapped list
    delete_list = list(set(delete_list))
    delete_list.sort()
    delete_list = list(reversed(delete_list))
    for index in delete_list:
        list_rxcuis_without_drugbank_ids.pop(index)

    print('number of new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(list_rxcuis_with_drugbank_ids)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))


'''
load map rxnorm id to drugbank _id from drugbank name mapped to rxnorm 
properties:
    0:drugbank_id
    1:rxcui
'''


def map_use_name_mapped_rxnorm_drugbank():
    f = open('../RxNorm_to_DrugBank/results/name_map_drugbank_to_rxnorm_2.tsv', 'r')
    next(f)
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = []
    number_of_mapped = 0
    for line in f:
        splitted = line.split('\t')
        rxnorm_cui = splitted[1].split('\n')[0]
        if not len(splitted) > 1:
            continue
        drugbank_id = splitted[0]
        if rxnorm_cui in list_rxcuis_without_drugbank_ids:
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            for code in codes:
                if len(dict_drug_NDF_RT[code].drugbank_ids) == 0:
                    dict_drug_NDF_RT[code].set_drugbank_ids([drugbank_id])
                    dict_drug_NDF_RT[code].set_how_mapped('use rxcui to drugbank ids with name mapping')
                    if not rxnorm_cui in list_rxcuis_with_drugbank_ids:
                        list_rxcuis_with_drugbank_ids.append(rxnorm_cui)
                    delete_list.append(list_rxcuis_without_drugbank_ids.index(rxnorm_cui))
                    if not code in list_codes_with_drugbank_ids:
                        number_of_mapped += 1
                        list_codes_with_drugbank_ids.append(code)
                else:
                    dict_drug_NDF_RT[code].drugbank_ids.append(drugbank_id)

    # remove all new mapped rxcuis from not mapped list
    delete_list = list(set(delete_list))
    delete_list.sort()
    delete_list = list(reversed(delete_list))
    for index in delete_list:
        list_rxcuis_without_drugbank_ids.pop(index)

    print('number of new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(list_rxcuis_with_drugbank_ids)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))


'''
find drugbank id by using the ingredient from of drug_kind
this is define in the association with name:Product_Component
This can be used because drugbank is not so specific with the drugs.
'''


def map_to_drubank_id_with_ingredient_from():
    # write all drugs which are mapped with this technical in a file
    g = open('ingredients_with_no_drugbank_id_or_not_in_hetionet.tsv', 'w')
    g.write('code \t name \t associated code \t name of associated code \t why \n')
    number_of_mapped = 0
    for rxcui in list_rxcuis_without_drugbank_ids:
        codes = dict_drug_NDF_RT_rxcui_to_code[rxcui]
        # list of all codes which are mapped to drugbank id in this step
        delete_mapped_codes = []
        index = 0
        for code in codes:
            index += 1
            associations = dict_drug_NDF_RT[code].association.split(',')
            for association in associations:
                if association[0:17] == 'Product_Component':
                    associatied_code = association.split(':')[1]
                    if associatied_code in dict_drug_NDF_RT:
                        drugbank_ids = dict_drug_NDF_RT[associatied_code].drugbank_ids
                        if len(drugbank_ids) > 0:
                            dict_drug_NDF_RT[code].set_drugbank_ids(drugbank_ids)
                            dict_drug_NDF_RT[code].set_how_mapped('use association to the ingredient from')
                            if not code in list_codes_with_drugbank_ids:
                                number_of_mapped += 1
                                list_codes_with_drugbank_ids.append(code)
                            delete_mapped_codes.append(index - 1)
                        else:
                            g.write(code + '\t' + dict_drug_NDF_RT[code].name + '\t' + associatied_code + '\t' +
                                    dict_drug_NDF_RT[
                                        associatied_code].name + ' \t ingredient also not mapped to drugbank id')
                    else:
                        g.write(code + '\t' + dict_drug_NDF_RT[
                            code].name + '\t' + associatied_code + '\t \t ingredient not in hetionet')
        # remove all codes from the not mapped list of the rxcui
        delete_mapped_codes = list(set(delete_mapped_codes))
        delete_mapped_codes.sort()
        delete_mapped_codes = list(reversed(delete_mapped_codes))
        for index in delete_mapped_codes:
            dict_drug_NDF_RT_rxcui_to_code[rxcui].pop(index)

    print('number of new mapped:' + str(number_of_mapped))

    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))


# dictionary with all cuis that are not mapped
dict_cui_to_codes = {}

# list of rxnorms without a cui
list_rxnorm_without_cui = []


# dictionary umls cuis that are mapped to hetionet, as key umls cui and value is a list of drugbank ids
dict_map_cui_to_hetionet_drugbank_ids = {}

# list of cuis that are not mapped
list_not_map_to_hetionet_with_drugbank_ids = []

# files for the different how_mapped typs
map_rxcui = open('drug/ndf_rt_drugs_map_with_rxcui.tsv', 'w')
map_rxcui.write('ndf-rt code \t drugbank_ids with | as seperator  \t name\n')

map_with_name = open('drug/ndf_rt_drugs_map_with_name_table.tsv', 'w')
map_with_name.write('ndf-rt code \t drugbank_ids with | as seperator  \t name\n')

map_with_unii_inchikey = open('drug/ndf_rt_drugs_map_with_unii_inchikey_table.tsv', 'w')
map_with_unii_inchikey.write('ndf-rt code \t drugbank_ids with | as seperator  \t name\n')

map_with_unii = open('drug/ndf_rt_drugs_map_with_unii_table.tsv', 'w')
map_with_unii.write('ndf-rt code \t drugbank_ids with | as seperator  \t name\n')

map_with_association_to_ingredient = open('drug/ndf_rt_drugs_map_with_association_to_ingredient.tsv', 'w')
map_with_association_to_ingredient.write('ndf-rt code \t drugbank_ids with | as seperator  \t name\n')

# dictionary of how_mapped with file as value
dict_how_mapped_file = {
    'use rxcui to drugbank ids with rxnorm': map_rxcui,
    'use rxcui to drugbank ids with name mapping': map_with_name,
    'use rxcui to drugbank ids with unii and inchikey to drugbank': map_with_unii_inchikey,
    'use unii of the ndf-rt code and map to drugbank id': map_with_unii,
    'use association to the ingredient from': map_with_association_to_ingredient}

# generate file with rxnom and a list of drugbank ids and where there are from
multiple_drugbankids = open('ndf_rt_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('ndf-rt code \t drugbank_ids with | as seperator \t where are it from  \t name\n')

'''
map ndf-rt drug to hetionet drug by using drugbank id
'''


def map_drug_to_hetionet():
    for code in list_codes_with_drugbank_ids:
        drugbank_ids = dict_drug_NDF_RT[code].drugbank_ids
        one_has_mapped = False
        mapped_drugbanks = []
        name = dict_drug_NDF_RT[code].name
        string_drugbank_ids = "|".join(drugbank_ids)
        how_mapped = dict_drug_NDF_RT[code].how_mapped

        dict_how_mapped_file[how_mapped].write(code + '\t' + string_drugbank_ids + '\t' + name + '\n')

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(code + '\t' + string_drugbank_ids + '\t' + how_mapped + '\t' + name + '\n')

        for drugbank_id in drugbank_ids:
            if drugbank_id in dict_drug_hetionet:
                one_has_mapped = True
                mapped_drugbanks.append(drugbank_id)
        if one_has_mapped:
            dict_map_cui_to_hetionet_drugbank_ids[code] = mapped_drugbanks
        else:
            list_not_map_to_hetionet_with_drugbank_ids.append(code)

    print('number of map to hetionet:' + str(len(dict_map_cui_to_hetionet_drugbank_ids)))
    print('number with drugbank but not mapped to hetionet:' + str(len(list_not_map_to_hetionet_with_drugbank_ids)))

    # generate a file with all not mapped ndf-rt drugs
    g = open('drug/drugs_that_did_not_get_a_drugbank_id.tsv', 'w')
    g.write('ndf-rt code \t rxcuis \t uniis \t name\n')
    for code, drug in dict_drug_NDF_RT.items():
        if not code in list_codes_with_drugbank_ids:
            rxcuis = dict_drug_NDF_RT[code].rxnorm_cuis
            string_rxcui = '|'.join(rxcuis)
            uniis = dict_drug_NDF_RT[code].uniis
            string_uniis = '|'.join(uniis)
            g.write(code + '\t' + string_rxcui + '\t' + string_uniis + '\t' + drug.name + '\n')
    g.close()


# dictionary count of delete of drugbank id from different mapping methods
dict_how_mapped_delete_counter = {}

'''
integrate the ndf-rt drugs into hetionet for the drugs which are map to drugbank and generate a cypher file 
a connection between compounds in hetionet and ndf-rt drug.
'''


def integration_of_ndf_rt_drugs_into_hetionet():
    get_drugbank_information.load_all_drugbank_ids_in_dictionary()
    # count all possible mapped ndf-rt codes
    counter = 0
    # count all ndf-rt codes which has illegal drugbank ids
    counter_illegal_drugbank = 0
    # number of all connection
    counter_drugbank_connection = 0
    # list wiwth all codes which are mapped to only illegal drugbank ids
    delete_code = []
    for code in list_codes_with_drugbank_ids:
        counter += 1
        drugbank_ids = dict_drug_NDF_RT[code].drugbank_ids
        string_drugbank_ids = "','".join(drugbank_ids)
        how_mapped = dict_drug_NDF_RT[code].how_mapped

        query = '''MATCH (n:NDF_RT_drug{code:'%s'}) 
        Set n.drugbank_ids=['%s'], n.how_mapped='%s' '''
        query = query % (code, string_drugbank_ids, dict_drug_NDF_RT[code].how_mapped)
        g.run(query)

        index = 0
        delete_index = []

        for drugbank_id in drugbank_ids:
            index += 1
            query = '''MATCH (n:Compound{identifier:'%s'}) RETURN n '''
            query = query % (drugbank_id)
            results = g.run(query)

            first_result = results.evaluate()
            if first_result == None:
                [name, inchi, inchikey] = get_drugbank_information.get_drugbank_information(drugbank_id)
                if name == '':
                    delete_index.append(index - 1)
                    continue

                query = '''Match (c:Compound) Where lower(c.name)="%s" Return c'''
                query = query % (name.lower())
                results = g.run(query)
                first_entry = results.evaluate()
                if first_entry != None:
                    delete_index.append(index - 1)
                    continue
                resource = 'NDF-RT'
                url = 'http://www.drugbank.ca/drugs/' + drugbank_id
                query = '''MATCH (n:NDF_RT_drug{code:'%s'}) 
                Create (c:Compound{identifier:'%s',ndf_rt:'yes',resource:['%s'], pubChem:"", hetionet:'no',sider:'no', license:'CC BY-NC 4.0?', inchikey:"%s", inchi:"%s", name:"%s", source:'DrugBank via NDF-RT' ,url:'%s' })
                Create (c)-[:equal_to_drug_ndf_rt]->(n)
                '''
                query = query % (code, drugbank_id, resource, inchikey, inchi, name, url)
            else:
                resource = first_result['resource'] if 'resource' in first_result else []
                resource.append('NDF-RT')
                resource = list(set(resource))
                resource = "','".join(resource)
                query = '''MATCH (n:NDF_RT_drug{code:'%s'}), (c:Compound{identifier:'%s'}) 
                Set c.ndf_rt='yes', c.resource=['%s']   
                Create (c)-[:equal_to_drug_ndf_rt]->(n)
                '''
                query = query % (code, drugbank_id, resource)
            counter_drugbank_connection += 1
            g.run(query)

        # delete all illegal drugbank ids
        delete_index = list(set(delete_index))
        if len(delete_index) == len(drugbank_ids):
            counter_illegal_drugbank += 1
            delete_code.append(list_codes_with_drugbank_ids.index(code))
            # counte the strategy
            if how_mapped in dict_how_mapped_delete_counter:
                dict_how_mapped_delete_counter[how_mapped] += 1
            else:
                dict_how_mapped_delete_counter[how_mapped] = 1
        for index in delete_index:
            dict_drug_NDF_RT[code].drugbank_ids.pop(index)

    # all not mapped compound get as property ndf-rt='no'
    query = ''' Match (c:Compound) Where not exists(c.ndf_rt) 
            Set c.ndf_rt="no" '''
    g.run(query)

    # remove all codes which are only mapped to illegal drugbank ids
    delete_code.sort()
    delete_code = list(reversed(delete_code))
    for index in delete_code:
        list_codes_with_drugbank_ids.pop(index)
    print('number of illegal:' + str(counter_illegal_drugbank))
    print('all mapped drug to drugbank where so of the has not existing drugbank ids:' + str(counter))
    print('number of connection:' + str(counter_drugbank_connection))
    print(dict_how_mapped_delete_counter)


# list contra indicates pairs
list_contra_indicates_pairs = []

# list induces pairs
list_induces_pairs = []

'''
integrate the connection: contra_indication and induces into hetionet
get the information over the path in neo4j (c:Compound)-[:equal_to_drug_ndf_rt]->()-[:ContraIndicates]-(n:NDF_RT_disease)
or (c:Compound)-[:equal_to_drug_ndf_rt]->()-[:Induces]-(n:NDF_RT_disease)
the NDF_RT_disease contains the DO_IDs which are use to connect them.
All this information goes into a cypher file.
'''


def integrate_connection_into_hetionet():
    # count of integrated contra-indication relationship
    count_contra_indicate = 0
    # count of integrated induces relationships
    count_induces = 0
    # count all mapped codes
    count_code = 0
    # count of integrated contra-indication  from ndf-rt
    number_of_contra_indication_connection_used = 0
    # count of integrated induces from ndf-rt
    number_of_induces_connection_used = 0

    #file counter
    i = 1
    h = open('map_connection_of_ndf_rt_in_hetionet_' + str(i) + '.cypher', 'w')
    h.write('begin \n')
    i += 1

    counter_connection = 0

    constrain_number = 20000
    creation_max = 1000000

    counter_contraindication_double = 0
    counter_induces_double = 0

    for code in list_codes_with_drugbank_ids:
        count_code += 1
        drugbank_ids = dict_drug_NDF_RT[code].drugbank_ids
        nui = dict_drug_NDF_RT[code].nui
        umls_cuis = dict_drug_NDF_RT[code].umls_cuis
        umls_cuis = ','.join(umls_cuis)

        # get the do id from the contra indication connection
        query = '''Match (n:NDF_RT_drug{code:'%s'})-[:ContraIndicates]-(b:NDF_RT_disease)  Return b.DO_IDs'''
        query = query % (code)
        connections_exist = g.run(query)
        do_ids_list_contra_indication = []
        if connections_exist:
            for do_ids, in connections_exist:
                number_of_contra_indication_connection_used += 1
                for do_id in do_ids:
                    do_ids_list_contra_indication.append(do_id)

        # get do ids from induces connection
        query = '''Match (n:NDF_RT_drug{code:'%s'})-[:Induces]-(b:NDF_RT_disease)  Return b.DO_IDs'''
        query = query % (code)
        connections_exist = g.run(query)
        do_ids_list_induce = []
        if connections_exist:
            for do_ids, in connections_exist:
                number_of_induces_connection_used += 1
                for do_id in do_ids:
                    do_ids_list_induce.append(do_id)

        url = 'purl.bioontology.org/ontology/NDFRT/' + nui

        # go through all mapped frugbank ids and add the connection for this drug into the cypher file
        for drugbank_id in drugbank_ids:

            do_ids_list_contra_indication = list(set(do_ids_list_contra_indication))
            for do_id in do_ids_list_contra_indication:
                if not (drugbank_id, do_id) in list_contra_indicates_pairs:
                    count_contra_indicate += 1
                    query = ''' Match (c:Compound{identifier:'%s'}), (n:Disease{identifier:'%s'})
                    Create (c)-[:CONTRA_INDICATES_CcD{source:'NDF-RT',code:"%s", ndf_rt:'yes' ,licence:'UMLS',how_often:1,url:"%s",umls_cuis:"%s"}]->(n);
                    '''
                    query = query % (drugbank_id, do_id, code, url, umls_cuis)
                    list_contra_indicates_pairs.append((drugbank_id, do_id))
                else:
                    counter_contraindication_double += 1
                    continue
                counter_connection += 1
                h.write(query)
                if counter_connection % constrain_number == 0:
                    h.write('commit \n')
                    if counter_connection % creation_max == 0:
                        h.close()
                        h = open('map_connection_of_ndf_rt_in_hetionet_' + str(i) + '.cypher', 'w')
                        h.write('begin \n')
                        i += 1
                    else:
                        h.write('begin \n')

            do_ids_list_induce = list(set(do_ids_list_induce))
            for do_id in do_ids_list_induce:
                if not (drugbank_id, do_id) in list_induces_pairs:
                    count_induces += 1
                    query = ''' Match (c:Compound{identifier:'%s'}), (n:Disease{identifier:'%s'})
                    Create (c)-[:INDUCES_CiD{source:'NDF-RT',code:"%s", ndf_rt:'yes', licence:'UMLS',how_often:1,url:"%s",umls_cuis:"%s"}]->(n);
                    '''
                    query = query % (drugbank_id, do_id, code, url, umls_cuis)
                    counter_connection += 1
                    list_induces_pairs.append((drugbank_id, do_id))
                else:
                    counter_induces_double += 1
                    continue
                h.write(query)
                if counter_connection % constrain_number == 0:
                    h.write('commit \n')
                    if counter_connection % creation_max == 0:
                        h.close()
                        h = open('map_connection_of_ndf_rt_in_hetionet_' + str(i) + '.cypher', 'w')
                        h.write('begin \n')
                        i += 1
                    else:
                        h.write('begin \n')

    h.write('commit')
    h.close()
    print(count_code)
    print('number of contra indications connections:' + str(count_contra_indicate))
    print('number of induces connections:' + str(count_induces))
    print('double of contra indicates connection:' + str(counter_contraindication_double))
    print('double of induces connection:' + str(counter_induces_double))


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in diseases from hetionet')

    load_hetionet_drug_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in diseases from ndf-rt')

    load_ndf_rt_drug_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map rxcui to drugbank ids with use of rxnorm')

    map_rxnorm_to_drugbank_use_rxnorm_database()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map rxcui to drugbank ids with use of rxnorm-drugbank table with unii and inchikey from dhimmel')

    map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('generate dictionary unii to codes')

    generate_dict_unii_to_code()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map unii to drugbank ids with use of unii-drugbank table')

    map_with_unii_to_drugbank()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map rxcui to drugbank ids with use of rxnorm-drugbank table with name mapping')

    map_use_name_mapped_rxnorm_drugbank()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map with use of the ingredient')

    map_to_drubank_id_with_ingredient_from()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map to hetionet with use of drugbank id')

    map_drug_to_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('integrate ndf-rt drugs into hetionet')

    integration_of_ndf_rt_drugs_into_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('integrate ndf-rt connection into hetionet')

    integrate_connection_into_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
