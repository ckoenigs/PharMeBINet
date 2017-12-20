# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 10:55:05 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys

sys.path.append('../aeolus/')
from synonyms_cuis import search_for_synonyms_cuis


class Symptom:
    """
    identifier:string (MESH id/ umls cui)
    name:string
    cuis:list of strings (umls cuis)
    """

    def __init__(self, identifier, name, cuis):
        self.identifier = identifier
        self.name = name
        self.cuis = cuis

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


class SideEffect:
    """
    identifier:string (umls cui)
    name:string
    how_mapped:string
    """

    def __init__(self, identifier, name):
        self.identifier = identifier
        self.name = name


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


# dictionary of all symptoms from hetionet, with mesh_id/ umls cui as key and value is class Symptom
dict_symptoms = {}

# list with all mesh id which has no umls cui
list_mesh_without_cui = []

# dictionary with all side effects from hetionet with umls cui as key and class SideEffect as value
dict_side_effects = {}

'''
function that load all symptoms in a dictionary and check if it has a umls cui or not
if not find a cui with us of umls via mysql. Take preferred the umls cui wwhere the name is the same.
'''


def load_all_symptoms_in_a_dict():
    query = "MATCH (n:Symptom) RETURN n"
    results = g.run(query)
    counter_with_name = 0
    counter_without_name = 0
    for result, in results:
        name = result['name'].lower()
        identifier = result['identifier']
        # only the symptoms with a umls cui as identifier has property type
        typ = result['type'] if 'type' in result else ''
        # some symptoms with Mesh id has already a umls cui
        cui= result['cui'] if 'cui' in result else ''
        if len(typ) == 0 and len(cui)==0:
            cuis = []
            cur = con.cursor()
            query = ("Select CUI,LAT,STR From MRCONSO Where SAB='MSH' and CODE= '%s';")
            query = query % (identifier)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                # list of all umls cuis which has the mesh id
                list_cuis = []
                same_name = False
                # list of all umls cuis with the same name
                list_cuis_with_same_name = []
                for (cui, lat, label,) in cur:
                    label = label.lower().decode('utf-8')
                    list_cuis.append(cui)
                    if label == name:
                        same_name = True
                        list_cuis_with_same_name.append(cui)
                if same_name:
                    cuis = list(set(list_cuis_with_same_name))
                    counter_with_name += 1
                else:
                    cuis = list(set(list_cuis))
                    counter_without_name += 1

            else:
                list_mesh_without_cui.append(identifier)
                print(identifier)
        elif len(typ) == 0:
            cuis=[cui]
        else:
            cuis = [identifier]
        symptom = Symptom(identifier, name, cuis)
        dict_symptoms[identifier] = symptom

    print(list_mesh_without_cui)
    print('Number od symptoms in hetionet:' + str(len(dict_symptoms)))
    print('mapped with mesh and name:' + str(counter_with_name))
    print('mapped only with mesh:' + str(counter_without_name))


'''
function that load all side effects in a dictionary 
'''


def load_all_sideEffects_in_a_dict():
    query = '''MATCH (n:SideEffect) RETURN n.name, n.identifier '''
    results = g.run(query)
    for name, cui, in results:
        side_effect = SideEffect(cui, name)
        dict_side_effects[cui] = side_effect

    print('size of side effects in hetionet:' + str(len(dict_side_effects)))


# dictionary with all mesh ids/umls cui that are mapped to side effect, key is mesh id/ umls cui and value is a list of mapped cuis
dict_mesh_map_to_cui = {}

'''
go through all symptoms and check if the umls cuis are in the side effects dictionary.
If not get further umls cuis by search for more umls cui for a mesh id or find the synonym cuis.
'''


def map_symptoms_to_sideEffects():
    for identifier, symptom in dict_symptoms.items():
        identifier_cuis = symptom.cuis
        mapped = []
        for cui in identifier_cuis:
            if cui in dict_side_effects:
                mapped.append(cui)
        # if direct a match is found
        if len(mapped) > 0:
            dict_mesh_map_to_cui[identifier] = mapped
            dict_symptoms[identifier].set_how_mapped('direct map with cui')
        else:
            # only for symptoms with mesh id (somtimes on mesh id has multiple umls cuis)
            if identifier!= identifier_cuis[0]:
                cur = con.cursor()
                query = ("Select CUI,LAT From MRCONSO Where SAB='MSH' and CODE= '%s';")
                query = query % (identifier)
                rows_counter = cur.execute(query)
                if rows_counter > 0:
                    list_cuis_mapped = []
                    for (cui, lat,) in cur:
                        if cui in dict_side_effects:
                            list_cuis_mapped.append(cui)
                else:
                    continue
                if len(list_cuis_mapped) > 0:
                    dict_mesh_map_to_cui[identifier] = list_cuis_mapped
                    dict_symptoms[identifier].set_how_mapped('map with all cuis of mesh id')
            else:
                # use symonym umls cuis
                new_cuis = search_for_synonyms_cuis(identifier_cuis)
                for cui in new_cuis:
                    if cui in dict_side_effects:
                        mapped.append(cui)
                if len(mapped) > 0:
                    dict_mesh_map_to_cui[identifier] = mapped
                    dict_symptoms[identifier].set_how_mapped('map with synonym cuis')
    #            else:
    #                print(identifier)
    #                print(symptom.name)
    #                print('not found')

    print('number of mapped mesh_ids:' + str(len(dict_mesh_map_to_cui)))


# files for the different mapping types
map_cui_to_cui = open('map/map_symptom_cui_to_side_effect_cui.tsv', 'w')
map_cui_to_cui.write('Symptome Mesh/cui \t Symptom cuis divided with | \t Side effect cui divided with | \n')

map_synonym_cuis_to_cui = open('map/map_symptom_synonym_cuis_to_side_effect_cui.tsv', 'w')
map_synonym_cuis_to_cui.write('Symptome Mesh/cui \t Symptom cuis divided with | \t Side effect cuis divided with | \n')

map_all_mesh_cuis_to_cui = open('map/map_symptom_all_mesh_cuis_to_side_effect_cui.tsv', 'w')
map_all_mesh_cuis_to_cui.write('Symptome Mesh/cui \t Symptom cuis divided with | \t Side effect cuis divided with | \n')

# dictionary for the different how_mapped  to file
dict_how_mapped_file = {
    'direct map with cui': map_cui_to_cui,
    'map with synonym cuis': map_synonym_cuis_to_cui,
    'map with all cuis of mesh id': map_all_mesh_cuis_to_cui}

'''
integrate connection between symptoms and side effects for mapped symptoms/side effects
maybe better a cypher file if it has mor symptoms
'''


def integrate_connection_into_hetionet():
    for identifier, cuis in dict_mesh_map_to_cui.items():
        how_mapped = dict_symptoms[identifier].how_mapped
        cuis = list(set(cuis))
        string_cuis = "|".join(cuis)
        string_identifier_cuis = '|'.join(dict_symptoms[identifier].cuis)
        dict_how_mapped_file[how_mapped].write(identifier + '\t' + string_identifier_cuis + '\t' + string_cuis + '\n')
        for cui in cuis:
            query = '''Match (n:SideEffect{identifier:"%s"}), (s:Symptom{identifier:"%s"}) 
            Create (n)-[:SHARES_SEsS{umls:'yes',how_mapped:'%s'}]->(s)            
            '''
            query = query % (cui, identifier, how_mapped)
            #            print(query)
            g.run(query)


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in symptoms from hetionet')

    load_all_symptoms_in_a_dict()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in side effects from hetionet')

    load_all_sideEffects_in_a_dict()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map symptoms to side effects direct')

    map_symptoms_to_sideEffects()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Intigrate symptoms to side effects direct')

    integrate_connection_into_hetionet()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
