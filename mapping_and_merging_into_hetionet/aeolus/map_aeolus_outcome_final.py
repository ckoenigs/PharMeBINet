# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 12:14:16 2017

@author: Cassandra
"""

from py2neo import Graph
import datetime
import MySQLdb as mdb
import sys, csv

import xml.dom.minidom as dom


class SideEffect:
    """
    license: string
    identifier: string (umls cui)
    name: string
    source: string
    url: string
    meddraType: string
    conceptName: string
    umls_label: string
    resource: list of strings
    """

    def __init__(self, licenses, identifier, name, source, url, meddraType, conceptName, umls_label, resource):
        self.license = licenses
        self.identifier = identifier
        self.name = name
        self.source = source
        self.url = url
        self.meddraType = meddraType
        self.conceptName = conceptName
        self.umls_label = umls_label
        self.resource = resource


class SideEffect_Aeolus():
    """
    snomed_outcome_concept_id: string (snomed ct ID)
    vocabulary_id: string (defined the type of the concept_code wich is MedDRA)
    name: string
    outcome_concept_id: string (OHDSI ID)
    concept_code: string (MedDRA ID)
    cuis: string (umls cuis)
    """

    def __init__(self, snomed_outcome_concept_id, vocabulary_id, name, outcome_concept_id, concept_code):
        self.snomed_outcome_concept_id = snomed_outcome_concept_id
        self.vocabulary_id = vocabulary_id
        self.name = name
        self.outcome_concept_id = outcome_concept_id
        self.concept_code = concept_code
        self.cuis = None

    def set_cuis_id(self, cuis):
        self.cuis = cuis


# dictionary with all side effects from hetionet with umls cui as key and as value a class SideEffect
dict_all_side_effect = {}


'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))

    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')


'''
load in all side effects from hetionet into a dictionary
has properties:
    license
    identifier
    name
    source
    url
    meddraType
    conceptName
    umls_label
    resource
'''


def load_side_effects_from_hetionet_in_dict():
    query = '''MATCH (n:SideEffect) RETURN n '''
    results = g.run(query)
    for result, in results:
        sideEffect = SideEffect(result['license'], result['identifier'], result['name'], result['source'],
                                result['url'], result['meddraType'], result['conceptName'], result['umls_label'],
                                result['resource'])
        dict_all_side_effect[result['identifier']] = sideEffect
    print('size of side effects before the aeolus is add:' + str(len(dict_all_side_effect)))


# dictionary with all aeolus side effects outcome_concept_id (OHDSI ID) as key and value is the class SideEffect_Aeolus
dict_side_effects_aeolus = {}

'''
load all aeolus side effects in a dictionary
has properties:
    snomed_outcome_concept_id
    vocabulary_id: defined the type of the concept_code
    name
    outcome_concept_id: OHDSI ID
    concept_code: MedDRA ID
'''


def load_side_effects_aeolus_in_dictionary():
    query = '''MATCH (n:AeolusOutcome) RETURN n'''
    results = g.run(query)
    for result, in results:
        sideEffect = SideEffect_Aeolus(result['snomed_outcome_concept_id'], result['vocabulary_id'], result['name'],
                                       result['outcome_concept_id'], result['concept_code'])
        dict_side_effects_aeolus[result['outcome_concept_id']] = sideEffect

    print('Size of Aoelus side effects:' + str(len(dict_side_effects_aeolus)))


# dictionary with for every key outcome_concept a list of umls cuis as value
dict_aeolus_SE_with_CUIs = {}

# generate file with meddra and a list of umls cuis and where there are from
multiple_cuis = open('aeolus_multiple_cuis.tsv', 'w')
multiple_cuis.write('MedDRA id \t cuis with | as seperator \t where are it from \n')

'''
find for every aeolus side effect a least one umls Cui and save them in a dictionary
'''


def find_cuis_for_aeolus_side_effects():
    for key, sideEffect in dict_side_effects_aeolus.items():
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where SAB = 'MDR' and CODE= %s ;")
        rows_counter = cur.execute(query, (sideEffect.concept_code,))
        if rows_counter > 0:
            list_cuis = []
            for (cui, lat, code, sab) in cur:
                list_cuis.append(cui)
            dict_aeolus_SE_with_CUIs[key] = list(set(list_cuis))
            if len(list(set(list_cuis))) > 1:
                cuis = "|".join(list(set(list_cuis)))
                multiple_cuis.write(key + '\t' + cuis + '\t from umls \n')


# list with all outcome_concept from aeolus that did not map direkt
list_not_mapped_to_hetionet = []

# list with all mapped outcome_concept
list_map_to_hetionet = []

# list with all mapped cuis:
dict_mapped_cuis_hetionet = {}

'''
add cui information into aeolus se class
'''
def add_cui_information_to_class(key,cui):
    if dict_side_effects_aeolus[key].cuis == None:
        dict_side_effects_aeolus[key].set_cuis_id([cui])
    else:
        dict_side_effects_aeolus[key].cuis.append(cui)

'''
map direct to hetionet and remember which did not map in list
'''


def map_first_round():
    for key, cuis in dict_aeolus_SE_with_CUIs.items():
        has_one = False
        for cui in cuis:
            if cui in dict_all_side_effect:

                list_map_to_hetionet.append(key)

                # check if the mapping appears multiple time
                # also set the mapped cui into the class aeolus
                if cui in dict_mapped_cuis_hetionet:

                    dict_mapped_cuis_hetionet[cui].append(key)
                    add_cui_information_to_class(key,cui)
                else:
                    dict_mapped_cuis_hetionet[cui] = [key]
                    add_cui_information_to_class(key,cui)

                has_one = True
        # remember not mapped aeolus se
        if has_one == False:
            list_not_mapped_to_hetionet.append(key)

    print('length of list which are mapped to hetionet:' + str(len(list_map_to_hetionet)))
    print('lenth of list whichhas a cui but are not mapped to hetionet:' + str(len(list_not_mapped_to_hetionet)))
    print('the number of nodes to which they are mapped:' + str(len(dict_mapped_cuis_hetionet)))


'''
integrate aeolus in hetiont, by map generate a edge from hetionet to the mapped aeolus node
if no hetionet node is found, then generate a new node for side effects
'''


def integrate_aeolus_into_hetionet():
    #file for already existing se
    file_existing=open('output/se_existing.tsv','w',encoding='utf-8')
    csv_existing=csv.writer(file_existing,delimiter='\t')
    csv_existing.writerow(['aSE','SE','cuis'])

    #query for mapping
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/aeolus/output/%s.tsv" As line FIELDTERMINATOR '\\t' Match (a:AeolusOutcome{outcome_concept_id:line.aSE})'''
    cypher_file= open('cypher_se.cypher','w')

    # query for the update nodes and relationship
    query_update= query_start+' , (n:SideEffect{identifier:line.SE}) Set a.cuis=split(line.cuis,"|"), n.resource=n.resource+"AEOLUS", n.aeolus="yes" Create (n)-[:equal_to_Aeolus_SE]->(a); \n'
    query_update= query_update %("se_existing")
    cypher_file.write(query_update)

    # update and generate connection between mapped aeolus outcome and hetionet side effect
    for outcome_concept in list_map_to_hetionet:
        cuis=dict_side_effects_aeolus[outcome_concept].cuis
        cuis_string='|'.join(cuis)
        for cui in cuis:
            csv_existing.writerow([outcome_concept,cui, cuis_string])

    # close file
    file_existing.close()

    # open new file for new se
    file_new=open('output/se_new.tsv','w',encoding='utf-8')
    csv_new=csv.writer(file_new,delimiter='\t')
    csv_new.writerow(['aSE','SE','cuis'])

    # query for the update nodes and relationship
    query_new = query_start + ' Create (n:SideEffect{identifier:line.SE, {licenses:"CC0 1.0", name:a.name , source:"UMLS via AEOLUS", url:"http://identifiers.org/umls/"+line.SE , resource:["AEOLUS"],  aeolus:"yes" }}) Set a.cuis=split(line.cuis,"|") Create (n)-[:equal_to_Aeolus_SE]->(a); \n'
    query_new = query_update % ("se_new")
    cypher_file.write(query_new)

    # generate new hetionet side effects and connect the with the aeolus outcome
    for outcome_concept in list_not_mapped_to_hetionet:
        csv_new.writerow([outcome_concept,dict_aeolus_SE_with_CUIs[outcome_concept][0], '|'.join(dict_aeolus_SE_with_CUIs[outcome_concept])])

    # search for all side effect that did not mapped with aeolus and give them the property aeolus:'no'
    # add query to update disease nodes with do='no'
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = '''begin\n Match (n:SideEffect) Where not exists(n.aeolus) Set n.aeolus="no";\n commit\n '''
    cypher_general.write(query)
    cypher_general.close()



def main():

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path aeolus se')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in all Side effects from hetionet in a dictionary')

    load_side_effects_from_hetionet_in_dict()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in all Side effects from AEOLUS in a dictionary')

    load_side_effects_aeolus_in_dictionary()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find cuis for aeolus side effects')

    find_cuis_for_aeolus_side_effects()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map round one')

    map_first_round()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('intergarte aeolus outcome to hetionet(+Sider)')

    integrate_aeolus_into_hetionet()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
