# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 08:40:47 2017

@author: ckoenigs
"""
from py2neo import Graph#, authenticate
import datetime
import MySQLdb as mdb
import sys, csv
from typing import Dict


class DrugHetionet:
    """
    license: string
    identifier: string (Drugbank ID)
    inchikey: string
    inchi: string
    name: string
    resource: list string
    xrefs: list string
    """

    def __init__(self, licenses, identifier, inchikey, inchi, name, resource, xrefs):
        self.license = licenses
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name
        self.resource=resource
        self.xrefs=xrefs


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
dict_all_drug = Dict[str, DrugHetionet]

# dictionary with all aeolus drugs with key drug_concept_id (OHDSI ID) and value is class Drug_Aeolus
dict_aeolus_drugs = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))

    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'umls')

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'RxNorm')


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
    query = 'MATCH (n:Chemical) RETURN n '
    results = g.run(query)

    for result, in results:
        licenses = result['license']
        identifier = result['identifier']
        inchikey = result['inchikey'] if 'inchikey' in result else ''
        inchi = result['inchi'] if 'inchi' in result else ''
        name = result['name']
        resource=result['resource'] if 'resource' in result else []
        xrefs=results['xrefs'] if 'xrefs' in result else []

        drug = DrugHetionet(licenses, identifier, inchikey, inchi, name,resource, xrefs )

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
    query = '''MATCH (n:AeolusDrug)  RETURN n'''

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
dict_aeolus_drug_mapped_ids = {}

'''
Search in RxNorm for mapping
'''
def search_for_mapping_in_rxnorm(sab,rxnorm_id,drug_concept_id, mapping_string):
    cur = conRxNorm.cursor()
    query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = '%s' and RXCUI= %s ;")
    rows_counter = cur.execute(query, (sab,rxnorm_id,))
    name = dict_aeolus_drugs[drug_concept_id].name.lower()
    found_a_mapping=False
    if rows_counter > 0:
        # list of all founded mapped identifier ids for the rxcui
        mapped_ids = []
        # list of all drugbank ids with the same name as in aeolus
        mapped_ids_same_name = []
        has_same_name = False
        # check if their are drugbank ids where the name is the same as in aeolus
        for (rxcui, lat, code, sab, label,) in cur:
            label = label.lower().decode('utf-8')
            if code in dict_all_drug:
                dict_all_drug[code].xrefs.append('RxNorm_Cui:'+rxcui)
                mapped_ids.append(code)
                found_a_mapping=True
                if label == name:
                    has_same_name = True
                    mapped_ids_same_name.append(code)

        if has_same_name:
            mapped_ids_same_name = list(set(mapped_ids_same_name))
            dict_aeolus_drug_mapped_ids[drug_concept_id] = mapped_ids_same_name
            dict_aeolus_drugs[drug_concept_id].set_how_mapped(mapping_string)
        else:
            mapped_ids = list(set(mapped_ids))
            dict_aeolus_drug_mapped_ids[drug_concept_id] = mapped_ids
            dict_aeolus_drugs[drug_concept_id].set_how_mapped(mapping_string)
    return found_a_mapping

'''
map rxnorm to drugbank with use of the RxNorm database
'''


def map_rxnorm_to_drugbank_use_rxnorm_database():
    for rxnorm_id, drug_concept_id in dict_rxnorm_to_drug_concept_id.items():
        if not search_for_mapping_in_rxnorm('DRUGBANK',rxnorm_id,drug_concept_id,'rxcui map to drugbank'):
            list_aeolus_drugs_without_drugbank_id.append(rxnorm_id)

    print('all that are map to drugbank id:' + str(len(dict_aeolus_drug_mapped_ids)))
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
map with use of map rxcui-drugbank id table with inchikeys and unii
idea form himmelstein
prioperties:
    0:rxcui
    1:drugbank ids seperated with |
'''


def map_rxnorm_to_drugbank_with_use_inchikeys_and_unii():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv', 'r')
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

            dict_aeolus_drug_mapped_ids[drug_concept_id] = drugbank_ids
            #add to all mapped chemical the rxnorm cui as xref
            for drugbank_id in drugbank_ids:
                dict_all_drug[drugbank_id].xrefs.append('RxNorm_Cui:'+rxnorm_id)

    # delete the new mapped rxnorm cuis from not mapped list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))

    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('length of mapped OHDSI ID and rxnorm cui:' + str(len(dict_aeolus_drug_mapped_ids)))
    print('length of list with rxcui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
use file where rxnorm mapped to drugbank
used name mapping
'''


def map_name_rxnorm_to_drugbank():
    f = open('../RxNorm_to_DrugBank/results/name_map_drugbank_to_rxnorm.tsv', 'r')
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
            dict_all_drug[drugbank_id].xrefs.append('RxNorm_Cui:'+rxnorm_id)

            if not drug_concept_id in dict_aeolus_drug_mapped_ids:
                dict_aeolus_drug_mapped_ids[drug_concept_id] = [drugbank_id]
            else:
                if not drugbank_id in dict_aeolus_drug_mapped_ids[drug_concept_id]:
                    dict_aeolus_drug_mapped_ids[drug_concept_id].append(drugbank_id)

    # delete the new mapped rxnorm cuis from not map list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))
    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('length of mapped rxnorm:' + str(len(dict_aeolus_drug_mapped_ids)))
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
Map aeolus to chemicals with mesh id
'''
def map_to_mesh_chemical():
    # list with all positions of the rxcuis which are  mapped in this step
    delete_list_without_DB = []
    for rxnorm_id in list_aeolus_drugs_without_drugbank_id:
        drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]
        if not search_for_mapping_in_rxnorm('MSH', rxnorm_id, drug_concept_id, 'rxcui map to MESH'):
            list_aeolus_drugs_without_drugbank_id.append(rxnorm_id)
        else:
            delete_list_without_DB.append(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))

    # delete the new mapped rxnorm cuis from not map list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))
    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)


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

# generate file of not mapped aeolus drugs
not_mapped = open('drug/not_mapped_rxcuis.tsv', 'w')
not_mapped.write('drug_concept_id \t rxcui \t name \n')

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
    for drug_concept_id, mapped_ids in dict_aeolus_drug_mapped_ids.items():
        has_one = False
        has_two = False
        list_double_map_mapped_ids = []
        string_list_mapped_ids = "|".join(mapped_ids)
        rxnorm_cui = dict_aeolus_drugs[drug_concept_id].concept_code
        how_mapped = dict_aeolus_drugs[drug_concept_id].how_mapped
        dict_how_mapped_files[how_mapped].write(rxnorm_cui + '\t' + string_list_mapped_ids + '\n')

        if len(mapped_ids) > 1:
            multiple_drugbankids.write(rxnorm_cui + '\t' + string_list_mapped_ids + '\t' + how_mapped + '\n')

        for drug_id in mapped_ids:
            if drug_id in dict_all_drug:
                list_double_map_mapped_ids.append(drug_id)

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

    for drug_concept_id, drug in dict_aeolus_drugs.items():
        if not drug_concept_id in dict_aeolus_drug_mapped_ids:
            not_mapped.write(drug_concept_id + '\t' + drug.concept_code + '\t' + drug.name + '\n')


# dictionary count deleted drugbank ids fro the different mapping methods
dict_how_mapped_delete_counter = {}


'''
Generate cypher file to update or create the relationships in hetionet
'''
def generate_cypher_file():
    cypher_file=open('cypher.cypher','w',encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ctd/drug/mapped.csv" As line Match (a:AeolusDrug{drug_concept_id:line.aeolus_id}),(n:Compound{identifier:line.chemical_id}) Set a.mapped_id=split(line.mapped_ids,'|'), a.how_mapped=line.how_mapped ,  n.aeolus="yes",n.resource= split(line.resource,'|') , n.xrefs=split(line.xrefs,'|') Create (n)-[:equal_to_Aeolus_drug]->(a); \n'''

    cypher_file.write(query)

    cypher_file.close()

    #relationship queries
    cypher_file = open('cypher.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ctd/drug/mapped_rela_se.csv" As line Match (c:Compound{identifier:line.chemical_id}),(r:SideEffect{identifier:line.disease_sideeffect_id})  Create (c)-[:CAUSES_CcSE{license:"CC0 1.0",unbiased:"false",source:'AEOLUS',countA:line.countA, prr_95_percent_upper_confidence_limit:line.prr_95_percent_upper_confidence_limit, prr:line.prr, countB:line.countB, prr_95_percent_lower_confidence_limit:line.prr_95_percent_lower_confidence_limit, ror:line.ror, ror_95_percent_upper_confidence_limit:line.ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit:line.ror_95_percent_lower_confidence_limit, countC:line.countC, drug_outcome_pair_count:line.drug_outcome_pair_count, countD:line.countD, ror_min:line.ror_min, ror_max:line.ror_max, prr_min:line.prr_min, prr_max:line.prr_max,  aeolus:'yes', how_often_appears:"1", resource:['AEOLUS']}]->(r); \n'''
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ctd/drug/mapped_rela_se.csv" As line Match (c:Compound{identifier:line.chemical_id})-[l:CAUSES_CcSE]-(r:SideEffect{identifier:line.disease_sideeffect_id}) Set l.countA=line.countA, l.prr_95_percent_upper_confidence_limit=line.prr_95_percent_upper_confidence_limit, l.prr=line.prr, l.countB=line.countB, l.prr_95_percent_lower_confidence_limit=line.prr_95_percent_lower_confidence_limit, l.ror=line.ror, l.ror_95_percent_upper_confidence_limit=line.ror_95_percent_upper_confidence_limit, l.ror_95_percent_lower_confidence_limit=line.ror_95_percent_lower_confidence_limit, l.countC=line.countC, l.drug_outcome_pair_count=line.drug_outcome_pair_count, l.countD=line.countD, l.aeolus='yes', l.how_often_appears=line., l.resource=split(line.,"|"), l.ror_min=line.ror_min, l.ror_max=line.ror_max, l.prr_min=line.prr_min, l.prr_max=line.prr_max; \n'''
    cypher_file.write(query)

    cypher_file = open('cypher.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ctd/drug/mapped_rela_se.csv" As line Match (c:Compound{identifier:line.chemical_id}),(r:Disease{identifier:line.disease_sideeffect_id})  Create (c)-[:INDICATES_CiD{license:"CC0 1.0",unbiased:"false",source:'AEOLUS',countA:line.countA, prr_95_percent_upper_confidence_limit:line.prr_95_percent_upper_confidence_limit, prr:line.prr, countB:line.countB, prr_95_percent_lower_confidence_limit:line.prr_95_percent_lower_confidence_limit, ror:line.ror, ror_95_percent_upper_confidence_limit:line.ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit:line.ror_95_percent_lower_confidence_limit, countC:line.countC, drug_outcome_pair_count:line.drug_outcome_pair_count, countD:line.countD, ror_min:line.ror_min, ror_max:line.ror_max, prr_min:line.prr_min, prr_max:line.prr_max,  aeolus:'yes', how_often_appears:"1", resource:['AEOLUS']}]->(r); \n'''
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ctd/drug/mapped_rela_se.csv" As line Match (c:Compound{identifier:line.chemical_id})-[l:INDICATES_CiD]-(r:Disease{identifier:line.disease_sideeffect_id}) Set l.countA=line.countA, l.prr_95_percent_upper_confidence_limit=line.prr_95_percent_upper_confidence_limit, l.prr=line.prr, l.countB=line.countB, l.prr_95_percent_lower_confidence_limit=line.prr_95_percent_lower_confidence_limit, l.ror=line.ror, l.ror_95_percent_upper_confidence_limit=line.ror_95_percent_upper_confidence_limit, l.ror_95_percent_lower_confidence_limit=line.ror_95_percent_lower_confidence_limit, l.countC=line.countC, l.drug_outcome_pair_count=line.drug_outcome_pair_count, l.countD=line.countD, l.aeolus='yes', l.how_often_appears=line., l.resource=split(line.,"|"), l.ror_min=line.ror_min, l.ror_max=line.ror_max, l.prr_min=line.prr_min, l.prr_max=line.prr_max; \n'''
    cypher_file.write(query)
    cypher_file.close()

    #the general cypher file to update all chemicals and relationship which are not from aeolus
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')


    # all compounds which are not mapped from aeolus get as property aeolus='no'
    query = '''begin\n Match (n:Chemical)  Where not exists(n.aeolus) Set n.aeolus="no";\n commit\n '''
    cypher_general.write(query)

    # all the cuases relationship which are not in aeolus get the property aeolus='no'
    query = '''begin\n Match (a:Chemical)-[l:CAUSES_CcSE]-(:SideEffect) Where not exists(l.aeolus) Set l.aeolus='no'; \n commit\n  '''
    cypher_general.write(query)

    cypher_general.close()

# csv for mapped aeolus pairs
file=open('drug/mapped.csv','w',encoding='utf-8')
csv_writer=csv.writer(file)
header=['aeolus_id','chemical_id','mapped_ids','how_mapped','resource','xrefs']
csv_writer.writerow(header)

'''
integrate aeolus drugs in hetiont, by map generate a edge from hetionet to the mapped aeolus node
if no hetionet node is found, then generate a new node for compound
'''


def integrate_aeolus_drugs_into_hetionet():
    # count all possible mapped aeolus drug
    counter = 0
    # count all qeolus which are only mapped to illegal drugbank ids
    counter_with_one_which_is_removed = 0

    for drug_concept_id, mapped_ids in dict_aeolus_drug_mapped_ids.items():
        counter += 1
        index = 0
        how_mapped = dict_aeolus_drugs[drug_concept_id].how_mapped
        delete_index = []
        alternative_ids = []
        mapped_ids_string='|'.join(mapped_ids)
        for mapped_id in mapped_ids:
            index += 1
            xrefs=list(set(dict_all_drug[mapped_id].xrefs))
            xrefs_string='|'.join(xrefs)
            resource=dict_all_drug[mapped_id].resource
            resource.append('AEOLUS')
            resource=list(set(resource))
            resource='|'.join(resource)
            csv_writer.writerow([drug_concept_id,mapped_id,mapped_ids_string,how_mapped, resource , xrefs_string])




    print('all aeolus drug which are map to drugbank, where some drugbank id are not existing:' + str(counter))
    print(dict_how_mapped_delete_counter)




def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in all drugs from hetionet (+Sider) in a dictionary')

    load_compounds_from_hetionet()


    # dictionary with all aeolus drugs with key drug_concept_id and value is class Drug_Aeolus
    global dict_aeolus_drugs
    dict_aeolus_drugs = {}

    # dictionary to translate rxnorm id to drug_concept_id
    global dict_rxnorm_to_drug_concept_id
    dict_rxnorm_to_drug_concept_id = {}

    # list with rxnorm ids which are not mapped to DurgBank ID
    global list_aeolus_drugs_without_mapped_id
    list_aeolus_drugs_without_mapped_id = []

    # dictionary with key drug_concept_id and value is a list of drugbank ids
    global dict_aeolus_drug_mapped_ids
    dict_aeolus_drug_mapped_ids = {}


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


if __name__ == "__main__":
    # execute only if run as a script
    main()
