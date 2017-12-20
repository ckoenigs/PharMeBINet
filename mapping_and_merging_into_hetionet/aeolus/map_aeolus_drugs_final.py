# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 08:40:47 2017

@author: ckoenigs
"""
from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys
import synonyms_cuis

import xml.dom.minidom as dom
import get_drugbank_information


class DrugHetionet:
    """
    license: string
    identifier: string (Drugbank ID)
    inchikey: string
    inchi: string
    name: string
    source: string
    url: string
    """

    def __init__(self, licenses, identifier, inchikey, inchi, name, source, url):
        self.license = licenses
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name
        self.source = source
        self.url = url


class Drug_Aeolus:
    """
    vocabulary_id: string (defined the type of the concept_code which is rxnorm)
    name: string
    outcome_concept_id: string (OHDSI ID )
    concept_code: string (RxNorm ID [rxcui])
    drugbank_id: string
    how_mapped: string
    """

    def __init__(self, vocabulary_id, name, drug_concept_id, concept_code):
        self.vocabulary_id = vocabulary_id
        self.name = name
        self.drug_concept_id = drug_concept_id
        self.concept_code = concept_code

    def set_drugbank_id(self, drugbank_id):
        self.drugbank_id = drugbank_id

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all compounds with id (drugbank id) as key and class DrugHetionet as value
dict_all_drug = {}

# dictionary with all aeolus drugs with key drug_concept_id (OHDSI ID) and value is class Drug_Aeolus
dict_aeolus_drugs = {}

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
load in all compounds from hetionet in dictionary
properties:
    license
    identifier
    inchikey
    inchi
    name
    source
    url
'''


def load_compounds_from_hetionet():
    query = 'MATCH (n:Compound) RETURN n '
    results = g.run(query)

    for result, in results:
        licenses = result['license']
        identifier = result['identifier']
        inchikey = result['inchikey']
        inchi = result['inchi']
        name = result['name']
        source = result['source']
        url = result['url']

        drug = DrugHetionet(licenses, identifier, inchikey, inchi, name, source, url)

        dict_all_drug[identifier] = drug

    print('In hetionet:' + str(len(dict_all_drug)) + ' drugs')


# dictionary to translate rxnorm id to drug_concept_id
dict_rxnorm_to_drug_concept_id = {}

'''
load a part of aeolus drugs, which are not integrated, in a dictionary and set the property integrated='yes'
has properties:
    vocabulary_id: defined the type of the concept_code
    name
    drug_concept_id: OHDSI ID
    concept_code: RxNorm CUI
'''


def load_drug_aeolus_in_dictionary():
    query = '''MATCH (n:AeolusDrug) Where not exists(n.integrated) Set n.integrated='yes' RETURN n'''

    results = g.run(query)
    for result, in results:
        if result['vocabulary_id'] != 'RxNorm':
            print('ohje')
        drug = Drug_Aeolus(result['vocabulary_id'], result['name'], result['drug_concept_id'], result['concept_code'])
        dict_aeolus_drugs[result['drug_concept_id']] = drug
        if not result['concept_code'] in dict_rxnorm_to_drug_concept_id:
            dict_rxnorm_to_drug_concept_id[result['concept_code']] = result['drug_concept_id']
    print('Size of Aoelus drug:' + str(len(dict_aeolus_drugs)))
    print('number of rxnorm ids in aeolus drug:' + str(len(dict_rxnorm_to_drug_concept_id)))


# list of all concept_id where no drugbank id is found, only save the rxnorm ids
list_aeolus_drugs_without_drugbank_id = []

# dictionary with key drug_concept_id and value is a list of drugbank ids
dict_aeolus_drug_drugbank_ids = {}

'''
map rxnorm to drugbank with use of the RxNorm database
'''


def map_rxnorm_to_drugbank_use_rxnorm_database():
    for rxnorm_id, drug_concept_id in dict_rxnorm_to_drug_concept_id.items():
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = 'DRUGBANK' and RXCUI= %s ;")
        rows_counter = cur.execute(query, (rxnorm_id,))
        name = dict_aeolus_drugs[drug_concept_id].name.lower()
        if rows_counter > 0:
            # list of all founded drugbank ids for the rxcui
            drugbank_ids = []
            # list of all drugbank ids with the same name as in aeolus
            drugbank_ids_same_name = []
            has_same_name = False
            # check if their are drugbank ids where the name is the same as in aeolus
            for (rxcui, lat, code, sab, label,) in cur:
                label = label.lower().decode('utf-8')
                drugbank_ids.append(code)
                if label == name:
                    has_same_name = True
                    drugbank_ids_same_name.append(code)

            if has_same_name:
                drugbank_ids_same_name = list(set(drugbank_ids_same_name))
                dict_aeolus_drug_drugbank_ids[drug_concept_id] = drugbank_ids_same_name
                dict_aeolus_drugs[drug_concept_id].set_how_mapped('rxcui map to drugbank')
            else:
                drugbank_ids = list(set(drugbank_ids))
                dict_aeolus_drug_drugbank_ids[drug_concept_id] = drugbank_ids
                dict_aeolus_drugs[drug_concept_id].set_how_mapped('rxcui map to drugbank')
        else:
            list_aeolus_drugs_without_drugbank_id.append(rxnorm_id)

    print('all that are map to drugbank id:' + str(len(dict_aeolus_drug_drugbank_ids)))
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
map with use of map rxcui-drugbank id table with inchikeys and unii
idea form himmelstein
prioperties:
    0:rxcui
    1:drugbank ids seperated with |
'''


def map_rxnorm_to_drugbank_with_use_inchikeys_and_unii():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey_4.tsv', 'r')
    next(f)
    # list with all positions of the rxcuis which are  mapped in this step
    delete_list_without_DB = []
    for line in f:
        splitted = line.split('\t')
        rxnorm_id = splitted[0]
        drugbank_ids = splitted[1].split('\n')[0].split('\r')[0].split('|')
        if rxnorm_id in list_aeolus_drugs_without_drugbank_id:
            delete_list_without_DB.append(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))
            drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]

            dict_aeolus_drugs[drug_concept_id].set_how_mapped(
                'map rxnorm to drugbank with use of dhimmel inchikey and unii')

            dict_aeolus_drug_drugbank_ids[drug_concept_id] = drugbank_ids

    # delete the new mapped rxnorm cuis from not mapped list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))

    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('length of mapped OHDSI ID and rxnorm cui:' + str(len(dict_aeolus_drug_drugbank_ids)))
    print('length of list with rxcui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
use file where rxnorm mapped to drugbank
used name mapping
'''


def map_name_rxnorm_to_drugbank():
    f = open('../RxNorm_to_DrugBank/results/name_map_drugbank_to_rxnorm_2.tsv', 'r')
    next(f)
    # list with all positions of the rxcuis which are  mapped in this step
    delete_list_without_DB = []
    for line in f:
        splitted = line.split('\t')
        drugbank_id = splitted[0]
        rxnorm_id = splitted[1].split('\n')[0]
        if rxnorm_id in list_aeolus_drugs_without_drugbank_id:
            delete_list_without_DB.append(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))
            drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]

            dict_aeolus_drugs[drug_concept_id].set_how_mapped('map rxnorm to drugbank with use of name mapping')

            if not drug_concept_id in dict_aeolus_drug_drugbank_ids:
                dict_aeolus_drug_drugbank_ids[drug_concept_id] = [drugbank_id]
            else:
                if not drugbank_id in dict_aeolus_drug_drugbank_ids[drug_concept_id]:
                    dict_aeolus_drug_drugbank_ids[drug_concept_id].append(drugbank_id)

    # delete the new mapped rxnorm cuis from not map list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))
    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('length of mapped rxnorm:' + str(len(dict_aeolus_drug_drugbank_ids)))
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


# list of drug_concept_ids which are map to hetionet
list_map_to_hetionet = []
# list of al drug_concept_ids that has a drugbank id but not mapped to hetionet
list_not_mapped = []

# genertate file for the different map methods
map_rxcui = open('drug/aeolus_map_with_use_of_rxcui.tsv', 'w')
map_rxcui.write('rxnorm_cui \t drugbank_ids with | as seperator  \n')

map_name = open('drug/aeolus_map_with_use_of_table_of_name_mapping.tsv', 'w')
map_name.write('rxnorm_cui \t drugbank_ids with | as seperator  \n')

map_with_inchikey_unii = open('drug/aeolus_map_with_use_of_unii_and_inchikey.tsv', 'w')
map_with_inchikey_unii.write('rxnorm_cui \t drugbank_ids with | as seperator  \n')

# dictionary with for every how_mapped has a different file
dict_how_mapped_files = {
    'map rxnorm to drugbank with use of name mapping': map_name,
    'rxcui map to drugbank': map_rxcui,
    'map rxnorm to drugbank with use of dhimmel inchikey and unii': map_with_inchikey_unii}

# generate file with rxnom and a list of drugbank ids and wheere there are from
multiple_drugbankids = open('aeolus_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('rxnorm_cui \t drugbank_ids with | as seperator \t where are it from \n')

'''
map aeolus drug in hetionet compound
'''


def map_aeolus_drugs_to_hetionet():
    for drug_concept_id, drugbank_ids in dict_aeolus_drug_drugbank_ids.items():
        has_one = False
        has_two = False
        list_double_map_drugbank_ids = []
        string_list_drugbank_ids = "|".join(drugbank_ids)
        rxnorm_cui = dict_aeolus_drugs[drug_concept_id].concept_code
        how_mapped = dict_aeolus_drugs[drug_concept_id].how_mapped
        dict_how_mapped_files[how_mapped].write(rxnorm_cui + '\t' + string_list_drugbank_ids + '\n')

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(rxnorm_cui + '\t' + string_list_drugbank_ids + '\t' + how_mapped + '\n')

        for drug_id in drugbank_ids:
            if drug_id in dict_all_drug:
                list_double_map_drugbank_ids.append(drug_id)

                if has_one:
                    has_two = True
                    dict_aeolus_drugs[drug_concept_id].drugbank_id.append(drug_id)
                else:
                    dict_aeolus_drugs[drug_concept_id].set_drugbank_id([drug_id])
                has_one = True
        if has_two:
            list_map_to_hetionet.append(drug_concept_id)
        elif has_one:
            list_map_to_hetionet.append(drug_concept_id)
        else:
            list_not_mapped.append(drug_concept_id)
    print('Mapped to hetionet:' + str(len(list_map_to_hetionet)))
    print('Will generate new nodes:' + str(len(list_not_mapped)))

    #generate file of not mapped aeolus drugs
    g = open('drug/not_mapped_rxcuis.tsv', 'w')
    g.write('drug_concept_id \t rxcui \t name \n')
    for drug_concept_id, drug in dict_aeolus_drugs.items():
        if not drug_concept_id in dict_aeolus_drug_drugbank_ids:
            g.write(drug_concept_id + '\t' + drug.concept_code + '\t' + drug.name + '\n')
    g.close()


# dictionary count deleted drugbank ids fro the different mapping methods
dict_how_mapped_delete_counter = {}

'''
integrate aeolus drugs in hetiont, by map generate a edge from hetionet to the mapped aeolus node
if no hetionet node is found, then generate a new node for compound
'''


def intigrate_aeolus_drugs_into_hetionet():
    # count all possible mapped aeolus drug
    counter = 0
    # count all qeolus which are only mapped to illegal drugbank ids
    counter_with_one_which_is_removed = 0
    get_drugbank_information.load_all_drugbank_ids_in_dictionary()

    for drug_concept_id, drugbank_ids in dict_aeolus_drug_drugbank_ids.items():
        counter += 1
        index = 0
        how_mapped = dict_aeolus_drugs[drug_concept_id].how_mapped
        delete_index = []
        alternative_ids = []
        for drugbank_id in drugbank_ids:
            index += 1
            query = ''' MATCH (n:Compound{identifier:"%s"}) RETURN n '''
            query = query % (drugbank_id)
            results = g.run(query)
            result = results.evaluate()
            if result == None:
                [name, inchi, inchikey] = get_drugbank_information.get_drugbank_inforamtion(drugbank_id)
                if name == '':
                    delete_index.append(index - 1)
                    continue

                # check if not this drug is in hetionet with an other drugbank id
                query = '''Match (c:Compound) Where lower(c.name)="%s" Return c'''
                query = query % (name.lower())
                results = g.run(query)
                first_entry = results.evaluate()
                if first_entry != None:
                    delete_index.append(index - 1)
                    alternative_ids.append(first_entry['identifier'])
                    resource = first_entry['resource'] if 'resource' in first_entry else []
                    resource.append("AEOLUS")
                    rxcui = dict_aeolus_drugs[drug_concept_id].concept_code + ',' + first_entry[
                        'rxnorm_cuis'] if 'rxnorm_cuis' in first_entry else dict_aeolus_drugs[
                        drug_concept_id].concept_code
                    resource = list(set(resource))
                    string_resource = '","'.join(resource)
                    query = '''Match (a:AeolusDrug),(n:Compound)  Where a.drug_concept_id="%s" and n.identifier="%s"
                    Set a.drugbank_id="%s", a.how_mapped='%s',  n.aeolus="yes",n.resource=["%s"], n.rxnorm_cuis="%s"
                    Create (n)-[:equal_to_Aeolus_drug]->(a); \n'''
                    query = query % (drug_concept_id, first_entry['identifier'], first_entry['identifier'],
                                     dict_aeolus_drugs[drug_concept_id].how_mapped, string_resource, rxcui)

                else:
                    url = 'http://www.drugbank.ca/drugs/' + drugbank_id
                    query = '''Match (a:AeolusDrug)  Where a.drug_concept_id="%s" 
                    Set a.drugbank_id="%s", a.how_mapped='%s'
                    CREATE (n:Compound{licenses:'CC0 1.0', identifier:"%s",inchikey:"%s", inchi:"%s", pubChem_id:"" , name:"%s" , source:"DrugBank via AEOLUS", url:"%s",  resource:["AEOLUS"], hetionet:"no", sider:"no", aeolus:"yes", ndf_rt:"no", rxnorm_cuis:"%s" }) 
                    Create (n)-[:equal_to_Aeolus_drug]->(a); \n'''

                    query = query % (
                    drug_concept_id, drugbank_id, dict_aeolus_drugs[drug_concept_id].how_mapped, drugbank_id, inchikey,
                    inchi, name, url, dict_aeolus_drugs[drug_concept_id].concept_code)
            else:
                resource = result['resource'] if 'resource' in result else []
                resource.append("AEOLUS")
                resource = list(set(resource))
                rxcui = dict_aeolus_drugs[drug_concept_id].concept_code + ',' + result[
                    'rxnorm_cuis'] if 'rxnorm_cuis' in result else dict_aeolus_drugs[drug_concept_id].concept_code
                string_resource = '","'.join(resource)
                query = '''Match (a:AeolusDrug),(n:Compound)  Where a.drug_concept_id="%s" and n.identifier="%s"
               Set a.drugbank_id="%s", a.how_mapped='%s',  n.aeolus="yes",n.resource=["%s"], n.rxnorm_cuis="%s"
               Create (n)-[:equal_to_Aeolus_drug]->(a); \n'''
                query = query % (
                drug_concept_id, drugbank_id, drugbank_id, dict_aeolus_drugs[drug_concept_id].how_mapped,
                string_resource, rxcui)

            g.run(query)

        # delete not existing drugbank ids
        delete_index = list(reversed(delete_index))
        if len(delete_index) == len(drugbank_ids) and len(alternative_ids) == 0:
            counter_with_one_which_is_removed += 1
            if how_mapped in dict_how_mapped_delete_counter:
                dict_how_mapped_delete_counter[how_mapped] += 1
            else:
                dict_how_mapped_delete_counter[how_mapped] = 1
        for index in delete_index:
            dict_aeolus_drug_drugbank_ids[drug_concept_id].pop(index)
        dict_aeolus_drug_drugbank_ids[drug_concept_id].extend(alternative_ids)

    # all compounds which are not mapped from aeolus get as property aeolus='no'
    query = ''' Match (n:Compound)  Where not exists(n.aeolus)
               Set n.aeolus="no",  n.rxnorm_cuis="" '''
    g.run(query)

    print('number of one mapped with illegal drugbank id:' + str(counter_with_one_which_is_removed))
    print('all aeolus drug which are map to drugbank, where some drugbank id are not existing:' + str(counter))
    print(dict_how_mapped_delete_counter)


'''       
dictionary connection (drug ID , SE) and list of information
0:countA	
1:prr_95_percent_upper_confidence_limit	
2:prr	
3:countB	
4:prr_95_percent_lower_confidence_limit	
5:ror	
6:ror_95_percent_upper_confidence_limit	
7:ror_95_percent_lower_confidence_limit	
8:countC	
9:drug_outcome_pair_count	
10.countD
'''
dict_connection_information = {}

'''
go through all connection of the mapped aeolus drugs and remember all information in a dictionary
'''


def get_aeolus_connection_information_in_dict():
    for drug_concept_id, drugbank_ids in dict_aeolus_drug_drugbank_ids.items():
        for drugbank_id in drugbank_ids:
            #            drugbank_id=dict_aeolus_drugs[drug_concept_id].drugbank_id
            query = '''Match (n:AeolusDrug{drug_concept_id:'%s'})-[l:Causes]->(r) Return l,r.cui '''
            query = query % (drug_concept_id)
            results = g.run(query)

            for connection, cui, in results:
                countA = int(connection['countA']) if connection['countA'] != '\N' else 0
                prr_95_percent_upper_confidence_limit = float(connection['prr_95_percent_upper_confidence_limit']) if \
                connection['prr_95_percent_upper_confidence_limit'] != '\N' else 0
                prr = float(connection['prr']) if connection['prr'] != '\N' else 0
                countB = float(connection['countB']) if connection['countB'] != '\N' else 0
                prr_95_percent_lower_confidence_limit = float(connection['prr_95_percent_lower_confidence_limit']) if \
                connection['prr_95_percent_lower_confidence_limit'] != '\N' else 0
                ror = float(connection['ror']) if connection['ror'] != '\N' else 0
                ror_95_percent_upper_confidence_limit = float(connection['ror_95_percent_upper_confidence_limit']) if \
                connection['ror_95_percent_upper_confidence_limit'] != '\N' else 0
                ror_95_percent_lower_confidence_limit = float(connection['ror_95_percent_lower_confidence_limit']) if \
                connection['ror_95_percent_lower_confidence_limit'] != '\N' else 0
                countC = float(connection['countC']) if connection['countC'] != '\N' else 0
                drug_outcome_pair_count = float(connection['drug_outcome_pair_count']) if connection[
                                                                                              'drug_outcome_pair_count'] != '\N' else 0
                countD = float(connection['countD']) if connection['countD'] != '\N' else 0

                if not (drugbank_id, cui) in dict_connection_information:
                    dict_connection_information[(drugbank_id, cui)] = [[countA],
                                                                       [prr_95_percent_upper_confidence_limit], [prr],
                                                                       [countB],
                                                                       [prr_95_percent_lower_confidence_limit], [ror],
                                                                       [ror_95_percent_upper_confidence_limit],
                                                                       [ror_95_percent_lower_confidence_limit],
                                                                       [countC], [drug_outcome_pair_count], [countD]]
                else:
                    dict_connection_information[(drugbank_id, cui)][0].append(countA)
                    dict_connection_information[(drugbank_id, cui)][1].append(prr_95_percent_upper_confidence_limit)
                    dict_connection_information[(drugbank_id, cui)][2].append(prr)
                    dict_connection_information[(drugbank_id, cui)][3].append(countB)
                    dict_connection_information[(drugbank_id, cui)][4].append(prr_95_percent_lower_confidence_limit)
                    dict_connection_information[(drugbank_id, cui)][5].append(ror)
                    dict_connection_information[(drugbank_id, cui)][6].append(ror_95_percent_upper_confidence_limit)
                    dict_connection_information[(drugbank_id, cui)][7].append(ror_95_percent_lower_confidence_limit)
                    dict_connection_information[(drugbank_id, cui)][8].append(countC)
                    dict_connection_information[(drugbank_id, cui)][9].append(drug_outcome_pair_count)
                    dict_connection_information[(drugbank_id, cui)][10].append(countD)


# counter for the cypher files
global file_number
file_number = 1

'''
update and generate the relationship CAUSES_CcSE.
go through all drugbank ID CUI pairs anf combine the information of multiple drugbank Id cui pairs
Next step is to check if this connection already exists in Hetionet, if true then update the relationship
if false generate the connection with the properties licence, unbiased, source, url, the other properties that aeolus has
countA	
prr_95_percent_upper_confidence_limit	
prr	
prr_min
prr_max
countB	
prr_95_percent_lower_confidence_limit	
ror	
ror_min
ror_max
ror_95_percent_upper_confidence_limit	
ror_95_percent_lower_confidence_limit	
countC	
drug_outcome_pair_count	
countD
'''


def integrate_connection_from_aeolus_in_hetionet():
    number_of_new_connection = 0
    number_of_updated_connection = 0

    global file_number

    h = open('cypher_map/map_connection_of_aeolus_in_hetionet_' + str(file_number) + '.cypher', 'w')
    h.write('begin \n')
    file_number += 1

    counter_connection = 0

    constrain_number = 20000
    creation_max = 1000000

    for (drugbank_id, cui), information_lists in dict_connection_information.items():
        # average of count A
        countA = str(sum(information_lists[0]) / float(len(information_lists[0])))
        # average prr 95% upper
        prr_95_percent_upper_confidence_limit = str(sum(information_lists[1]) / float(len(information_lists[1])))
        # average prr
        prr = str(sum(information_lists[2]) / float(len(information_lists[2])))
        # minmum prr
        prr_min = str(min(information_lists[2]))
        # maximu prr
        prr_max = str(max(information_lists[2]))
        # average of count B
        countB = str(sum(information_lists[3]) / float(len(information_lists[3])))
        # average prr 95 % lower
        prr_95_percent_lower_confidence_limit = str(sum(information_lists[4]) / float(len(information_lists[4])))
        # average ror
        ror = str(sum(information_lists[5]) / float(len(information_lists[5])))
        # minmum ror
        ror_min = str(min(information_lists[5]))
        # maximum ror
        ror_max = str(max(information_lists[5]))
        # average of ror 95% lower
        ror_95_percent_upper_confidence_limit = str(sum(information_lists[6]) / float(len(information_lists[6])))
        # average of ror 95% lower
        ror_95_percent_lower_confidence_limit = str(sum(information_lists[7]) / float(len(information_lists[7])))
        # average of count C
        countC = str(sum(information_lists[8]) / float(len(information_lists[8])))
        # average of drug outcome pair
        drug_outcome_pair_count = str(sum(information_lists[9]) / float(len(information_lists[9])))
        # average of count D
        countD = str(sum(information_lists[10]) / float(len(information_lists[10])))
        query = '''Match (c:Compound{identifier:"%s"})-[l:CAUSES_CcSE]-(r:SideEffect{identifier:"%s"}) Return l '''
        query = query % (drugbank_id, cui)
        connections_exist = g.run(query)
        first_connection = connections_exist.evaluate()
        if first_connection == None:
            # todo add the other properties to create
            query = '''Match (c:Compound{identifier:"%s"}),(r:SideEffect{identifier:"%s"}) 
            Create (c)-[:CAUSES_CcSE{license:"CC0 1.0",unbiased:"false",source:'AEOLUS',url:"",countA:"%s", prr_95_percent_upper_confidence_limit:"%s", prr:"%s", countB:"%s", prr_95_percent_lower_confidence_limit:"%s", ror:"%s", ror_95_percent_upper_confidence_limit:"%s", ror_95_percent_lower_confidence_limit:"%s", countC:"%s", drug_outcome_pair_count:"%s", countD:"%s", ror_min:"%s", ror_max:"%s", prr_min:"%s", prr_max:"%s",hetionet:'no', ctd:'no', aeolus:'yes', sider:'no',  how_often_appears:"1", resource:['AEOLUS'],upperFrequency:"", placebo:"", frequency:"", lowerFrequency:"",  placeboFrequency: "", placeboLowerFrequency: "", placeboUpperFrequency: ""}]->(r); \n'''
            query = query % (drugbank_id, cui, countA, prr_95_percent_upper_confidence_limit, prr, countB,
                             prr_95_percent_lower_confidence_limit, ror, ror_95_percent_upper_confidence_limit,
                             ror_95_percent_lower_confidence_limit, countC, drug_outcome_pair_count, countD, ror_min,
                             ror_max, prr_min, prr_max)
            number_of_new_connection += 1
        else:
            resource = first_connection['resource'] if first_connection['resource'] != None else []
            if not 'AEOLUS' in resource:
                resource.append('AEOLUS')
            resource = '","'.join(resource)
            how_often = str(int(first_connection['how_often_appears']) + 1) if first_connection['how_often_appears'] != None else '1'
            query = '''Match (c:Compound{identifier:"%s"})-[l:CAUSES_CcSE]-(r:SideEffect{identifier:"%s"})
            Set l.countA="%s", l.prr_95_percent_upper_confidence_limit="%s", l.prr="%s", l.countB="%s", l.prr_95_percent_lower_confidence_limit="%s", l.ror="%s", l.ror_95_percent_upper_confidence_limit="%s", l.ror_95_percent_lower_confidence_limit="%s", l.countC="%s", l.drug_outcome_pair_count="%s", l.countD="%s", l.hetionet='yes', l.aeolus='yes', l.how_often_appears="%s", l.resource=["%s"], l.ror_min="%s", l.ror_max="%s", l.prr_min="%s", l.prr_max="%s"; \n'''
            query = query % (drugbank_id, cui, countA, prr_95_percent_upper_confidence_limit, prr, countB,
                             prr_95_percent_lower_confidence_limit, ror, ror_95_percent_upper_confidence_limit,
                             ror_95_percent_lower_confidence_limit, countC, drug_outcome_pair_count, countD, how_often,
                             resource, ror_min, ror_max, prr_min, prr_max)
            number_of_updated_connection += 1
        counter_connection += 1
        h.write(query)
        if counter_connection % constrain_number == 0:
            h.write('commit \n')
            if counter_connection % creation_max == 0:
                h.close()
                h = open('cypher_map/map_connection_of_aeolus_in_hetionet_' + str(file_number) + '.cypher', 'w')
                h.write('begin \n')
                file_number += 1
                continue
            h.write('begin \n')
    h.write('commit ')
    h.close()

    print('number of new connection:' + str(number_of_new_connection))
    print('number of update connection:' + str(number_of_updated_connection))


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in all drugs from hetionet (+Sider) in a dictionary')

    load_compounds_from_hetionet()

    # because every aeolus drug has so many relationships only part for part can be integrated
    for x in range(0, 22):

        # dictionary with all aeolus drugs with key drug_concept_id and value is class Drug_Aeolus
        global dict_aeolus_drugs
        dict_aeolus_drugs = {}

        # dictionary to translate rxnorm id to drug_concept_id
        global dict_rxnorm_to_drug_concept_id
        dict_rxnorm_to_drug_concept_id = {}

        # list with rxnorm ids which are not mapped to DurgBank ID
        global list_aeolus_drugs_without_drugbank_id
        list_aeolus_drugs_without_drugbank_id = []

        # dictionary with key drug_concept_id and value is a list of drugbank ids
        global dict_aeolus_drug_drugbank_ids
        dict_aeolus_drug_drugbank_ids = {}

        '''       
        dictionary connection (drug ID , SE) and list of information
        0:countA	
        1:prr_95_percent_upper_confidence_limit	
        2:prr	
        3:countB	
        4:prr_95_percent_lower_confidence_limit	
        5:ror	
        6:ror_95_percent_upper_confidence_limit	
        7:ror_95_percent_lower_confidence_limit	
        8:countC	
        9:drug_outcome_pair_count	
        10.countD
        '''
        global dict_connection_information
        dict_connection_information = {}


        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('Load in all drugs from aeolus in a dictionary')

        load_drug_aeolus_in_dictionary()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('Find drugbank ids with use of the rxcuis and save them in a dictionary')

        map_rxnorm_to_drugbank_use_rxnorm_database()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('map with use of rxnorm_to drugbank with mapping using unii and inchikey')

        map_rxnorm_to_drugbank_with_use_inchikeys_and_unii()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('map with rxnorm to drugbank with use of mapping file with name')

        map_name_rxnorm_to_drugbank()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('Map the drugbank id from the aeolus drug to the drugbank ids in hetionet')

        map_aeolus_drugs_to_hetionet()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('integrate aeolus drugs into hetionet')

        intigrate_aeolus_drugs_into_hetionet()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('get the aeolus information')

        get_aeolus_connection_information_in_dict()

        print(
        '###########################################################################################################################')

        print (datetime.datetime.utcnow())
        print('Integrate connection into hetionet')

        integrate_connection_from_aeolus_in_hetionet()

    # all the cuases relationship which are not in aeolus get the property aeolus='no'
    h = open('cypher_map/map_connection_of_aeolus_in_hetionet_' + str(file_number - 1) + '.cypher', 'a')
    h.write('begin \n')

    query = ''' Match ()-[l:CAUSES_CcSE]-() Where not exists(l.aeolus)
        Set l.aeolus='no'; \n '''
    h.write(query)
    h.write('commit')
    h.close()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
