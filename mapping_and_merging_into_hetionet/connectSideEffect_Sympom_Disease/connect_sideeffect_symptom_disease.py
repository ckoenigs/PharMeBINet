# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 10:55:05 2017

@author: ckoenigs
"""

import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases


class Symptom:
    """
    identifier:string (MESH id/ umls cui)
    name:string
    """

    def __init__(self, identifier, name, cuis):
        self.identifier = identifier
        self.name = name

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
    global g
    g = create_connection_to_databases.database_connection_neo4j()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


# dictionary of all symptoms from hetionet, with mesh_id/ umls cui as key and value is class Symptom
dict_symptoms = {}

# list with all mesh id which has no umls cui
list_mesh_without_cui = []

# dictionary with all side effects from hetionet with umls cui as key and class SideEffect as value
dict_side_effects = {}

# dictionary name/umls_id/meddra_id to set of sideeffects id
dict_name_ids_to_sideeffect_ids = {}

# set of pairs of symptom side effect
set_symptom_side_effect = set()

# set of pairs of disease side effect
set_disease_side_effect = set()

# set of pairs of disease symptom
set_disease_symptom = set()

# generate cypher file
cypher = open('cypher.cypher', 'w', encoding='utf-8')


def add_element_to_dictionary(property, identifier, dictionary):
    """
    Add a key (property), value (identifier) to a dictionary
    :param property: string
    :param identifier:  string
    :param dictionary: dictionary
    :return: 
    """
    if not property in dictionary:
        dictionary[property] = set()
    dictionary[property].add(identifier)


def mapping(from_mapper, from_identifier, dictionary, map_file, how_mapped, set_of_pairs):
    """
    Map from one name/id of on label to the dictionary of the other label
    if mapped write into  the file the mapping pairs and how they mapped
    else return that it did not mapped
    :param from_mapper: string
    :param from_identifier: string
    :param dictionary: dictionary
    :param map_file: csv.writer
    :param how_mapped: string
    :param set_of_pairs: set of tuple pairs
    :return: if it mapped or not
    """
    if from_mapper in dictionary:
        for to_identifier in dictionary[from_mapper]:
            if not (from_identifier, to_identifier) in set_of_pairs:
                map_file.writerow([from_identifier, to_identifier, how_mapped])
                set_of_pairs.add((from_identifier, to_identifier))
        return True
    return False


def create_cypher_query(header, from_label, to_label, file_name):
    if to_label == 'SideEffect':
        short_second = 'SE'
    else:
        short_second = to_label[0]
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/connectSideEffect_Sympom_Disease/%s" As line FIELDTERMINATOR '\\t' 
                Match (first:%s {identifier:line.%s}), (second:%s {identifier:line.%s})  Create (first)-[:EQUAL_%se%s{how_mapped:line.%s}]->(second);\n'''
    query = query % (file_name, from_label, header[0], to_label, header[1], from_label[0], short_second, header[2])
    cypher.write(query)


def create_mapping_file(directory, file_name, header, from_label, to_label):
    """
    generate the csv writer for the mapping file and additionaly also the
    :param directory:
    :param file_name:
    :param header:
    :param from_label:
    :param to_label:
    :return:
    """
    path = directory + '/' + file_name
    map_file = open(path, 'w', encoding='utf-8')
    csv_writer = csv.writer(map_file, delimiter='\t')
    csv_writer.writerow(header)

    create_cypher_query(header, from_label, to_label, path)
    return csv_writer


'''
function that load all side effects in a dictionary 
'''


def load_all_sideEffects_in_a_dict():
    query = '''MATCH (n:SideEffect) RETURN n.name, n.identifier, n.xrefs '''
    results = g.run(query)
    for name, cui, xrefs, in results:
        name = name.lower()
        side_effect = SideEffect(cui, name)
        dict_side_effects[cui] = side_effect

        add_element_to_dictionary(name, cui, dict_name_ids_to_sideeffect_ids)
        add_element_to_dictionary(cui, cui, dict_name_ids_to_sideeffect_ids)

        if xrefs:
            for xref in xrefs:
                add_element_to_dictionary(xref, cui, dict_name_ids_to_sideeffect_ids)

    print('size of side effects in hetionet:' + str(len(dict_side_effects)))


# dictionary name/mesh_id to set of symptom ids
dict_name_ids_to_symptom_ids = {}

'''
function that load all symptoms in a dictionary and check if it has a umls cui or not
if not find a cui with us of umls via mysql. Take preferred the umls cui wwhere the name is the same.
'''


def load_all_symptoms_in_a_dict():
    query = "MATCH (n:Symptom) RETURN n"
    results = g.run(query)
    counter_with_name = 0
    counter_without_name = 0

    # create mapping file to side effect and cypher query
    csv_mapping_s_to_se = create_mapping_file('mapping_symptom_sideeffect', 'map_s_to_se.tsv',
                                              ['symptom_id', 'side_effect_id', 'how_mapped'], 'Symptom', 'SideEffect')
    for result, in results:
        name = result['name'].lower()
        identifier = result['identifier']

        symptom = Symptom(identifier, name, [])
        add_element_to_dictionary(name, identifier, dict_name_ids_to_symptom_ids)
        add_element_to_dictionary(identifier, identifier, dict_name_ids_to_symptom_ids)

        mapped_with_name = mapping(name, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_s_to_se,
                                   'mapped with name', set_symptom_side_effect)
        if mapped_with_name:
            counter_with_name += 1

        cuis = []

        # manual checked with wrong mapping with umls
        if identifier in ['D004881']:
            list_mesh_without_cui.append(identifier)
            print(identifier)
            continue
        cur = con.cursor()
        query = ("Select CUI,LAT,STR From MRCONSO Where SAB='MSH' and CODE= '%s';")
        query = query % (identifier)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            # list of all umls cuis which has the mesh id
            list_cuis = []
            same_name = False
            # list of all umls cuis with the same name
            list_cuis_with_same_name = set()
            for (cui, lat, label,) in cur:
                label = label.lower()
                list_cuis.append(cui)
                if label == name:
                    same_name = True
                    list_cuis_with_same_name.add(cui)
            if same_name:
                cuis = list(list_cuis_with_same_name)
                counter_with_name += 1
            else:
                cuis = list(list_cuis)
                counter_without_name += 1
            for cui in cuis:
                list_cuis_mapped = set()
                mapping(cui, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_s_to_se,
                        'mapped with umls cui', set_symptom_side_effect)
                if cui in dict_side_effects:
                    list_cuis_mapped.add(cui)
                if len(list_cuis_mapped) > 0:
                    # dict_mesh_map_to_cui[identifier] = list_cuis_mapped
                    symptom.set_how_mapped('map with all cuis of mesh id')
        else:
            list_mesh_without_cui.append(identifier)
            print(identifier)

        dict_symptoms[identifier] = symptom

    print(list_mesh_without_cui)
    print('Number of symptoms in hetionet:' + str(len(dict_symptoms)))
    print('mapped with mesh and name:' + str(counter_with_name))
    print('mapped only with mesh:' + str(counter_without_name))


def load_and_map_disease():
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)

    # create mapping file to side effect and cypher query
    csv_mapping_d_to_se = create_mapping_file('mapping_disease_mapping', 'map_d_to_se.tsv',
                                              ['disease_id', 'side_effect_id', 'how_mapped'], 'Disease', 'SideEffect')

    csv_mapping_d_to_s = create_mapping_file('mapping_disease_mapping', 'map_d_to_s.tsv',
                                             ['disease_id', 'symptom_id', 'how_mapped'], 'Disease', 'Symptom')

    counter_mapped_se = 0
    counter_mapped_symp = 0

    for disease, in results:
        name = disease['name'].lower() if 'name' in disease else ''
        identifier = disease['identifier']

        mapped_to_sideeffect = False
        mapped_to_symptom = False
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        for xref in xrefs:
            if xref.lower().startswith('umls'):
                umls = xref.split(':')[1]
                mapped = mapping(umls, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se,
                                 'mapped with UMLS ID', set_disease_side_effect)
                if mapped:
                    mapped_to_sideeffect = True
                    counter_mapped_se += 1
            elif xref.lower().startswith('meddra'):
                mapped = mapping(xref, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se,
                                 'mapped with MedDRA ID', set_disease_side_effect)
                if mapped:
                    mapped_to_sideeffect = True
                    counter_mapped_se += 1
            elif xref.lower().startswith('mesh'):
                mesh = xref.split(':')[1]
                mapped = mapping(mesh, identifier, dict_name_ids_to_symptom_ids, csv_mapping_d_to_s,
                                 'mapped with MESH ID', set_disease_symptom)
                if mapped:
                    mapped_to_symptom = True
                    counter_mapped_symp += 1

        if not mapped_to_sideeffect:
            mapped = mapping(name, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se, 'mapped with name',
                             set_disease_side_effect)

            # if not map try with disease synonyms
            if not mapped:
                synonyms = disease['synonyms'] if 'synonyms' in disease else []
                for synonym in synonyms:
                    if '[' in synonym:
                        synonym = synonym.rsplit(' [', 1)[0]
                    synonym = synonym.lower()
                    mapped_syn = mapping(synonym, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se,
                                         'mapped with synonyms', set_disease_side_effect)
                    if mapped_syn:
                        mapped = True

            if not mapped:
                cur = con.cursor()
                query = ('Select CUI,LAT,STR From MRCONSO Where  STR= "%s";')
                query = query % (name)
                rows_counter = cur.execute(query)
                mapped_with_umls = False
                if rows_counter > 0:
                    for (cui, lat, label,) in cur:
                        mapped_with_umls = mapping(cui, identifier, dict_name_ids_to_sideeffect_ids,
                                                   csv_mapping_d_to_se,
                                                   'mapped with cui from umls', set_disease_side_effect)
                        if mapped_with_umls:
                            mapped = True
            if mapped:
                counter_mapped_se += 1

        if not mapped_to_symptom:
            mapped = mapping(name, identifier, dict_name_ids_to_symptom_ids, csv_mapping_d_to_s, 'mapped with name',
                             set_disease_symptom)
            if mapped:
                counter_mapped_symp += 1

    print('number of mapped disease to se:', counter_mapped_se)
    print('number of mapped disease to symptom:', counter_mapped_symp)


def main():
    global path_of_directory

    # path to to project
    if len(sys.argv) == 2:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path for connection of se,s,d')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in side effects from hetionet')

    load_all_sideEffects_in_a_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in symptoms from hetionet and map to se')

    load_all_symptoms_in_a_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load disease an map to se and symptom')

    load_and_map_disease()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
