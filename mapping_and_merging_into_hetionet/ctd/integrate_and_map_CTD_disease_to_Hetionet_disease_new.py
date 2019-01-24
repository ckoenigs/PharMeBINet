# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys
import csv


class DiseaseHetionet:
    """
    identifier: string (mondo)
    umls_cuis: list
    xrefs: list (different other identifier like omim or mesh)
    synonyms: list (synonym names)
    resource: list (all different sources which include this disease)
    """

    def __init__(self, identifier, synonyms, umls_cuis, xrefs, resource):
        self.identifier = identifier
        self.umls_cuis = umls_cuis
        self.xrefs = xrefs
        self.synonyms = synonyms
        self.resource = resource


class DiseaseCTD:
    """
    idType: string (can be omim or mesh)
    name: string
    altDiseaseIDs: list (can be mesh, omim or do)
    doids: list with doids
    disease_id: sting (the mesh or omim ID)
    cuis: list (umls cuis of this disease)
    mondos:list (mapped mondos)
    how_mapped: string
    """

    def __init__(self, idType, name, altDiseaseIDs, disease_id, doids):
        self.idType = idType
        self.name = name
        self.altDiseaseIDs = altDiseaseIDs
        self.disease_id = disease_id
        self.doids = doids
        self.mondos = []
        self.cuis = []
        self.mapping = []

    def set_cuis(self, cuis):
        self.cuis = cuis

    def set_mondos(self, mondos):
        mondo_set = set(self.mondos)
        self.mondos = list(mondo_set.union(mondos))

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped

    def set_mapping_id(self, identifier):
        self.mapping.append(identifier)
        self.mapping = list(set(self.mapping))


# dictionary with all CTD diseases, which has a relationship  treats or induces with a drug
dict_CTD_disease = {}

# dictionary for hetionet diseases with mondo as key and value is class DiseaseHetionet
dict_diseases_hetionet = {}

# dictionary mesh to mondos, information from Monarch Disease Ontology
dict_mesh_to_mondo = {}

# dictionary omim to mondos, information from Monarch Disease Ontology
dict_omim_to_mondo = {}

# dictionary umls cui to mondos, information from Monarch Disease Ontology
dict_umls_cui_to_mondo = {}

# dictionary DOID to mondos, information from Monarch Disease Ontology
dict_doid_to_mondo = {}

# dictionary with name/synonyms to mondo
dict_name_synonym_to_mondo_id = {}

# dictionary for hetionet identifier with name as value
dict_hetionet_id_to_name = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')


'''
load in all diseases from hetionet in a dictionary
'''


def load_hetionet_diseases_in():
    query = '''MATCH (n:Disease) RETURN n.identifier,n.name, n.synonyms, n.xrefs, n.umls_cuis, n.resource, n.doids'''
    results = g.run(query)

    for identifier, name, synonyms, xrefs, umls_cuis, resource, doids, in results:
        # if identifier=='MONDO:0002165':
        #     print('BLUB')
        # add name with mondo to dictionary
        name_formed = name.lower().split(' exact ')[0]
        dict_hetionet_id_to_name[identifier] = name
        if name_formed not in dict_name_synonym_to_mondo_id:
            dict_name_synonym_to_mondo_id[name_formed] = [identifier]
        else:
            dict_name_synonym_to_mondo_id[name_formed].append(identifier)
            part_list = set(dict_name_synonym_to_mondo_id[name_formed])
            dict_name_synonym_to_mondo_id[name_formed] = list(part_list)

        # add the differnt synonyms with mondo to dictionary
        if not synonyms is None:
            for synonym in synonyms:
                synonym = synonym.split(':')[0].lower().split(' exact ')[0]
                additional_synonym_names = synonym.split(';')
                if len(additional_synonym_names) > 1:
                    synonym = additional_synonym_names[0]
                    if additional_synonym_names[1] not in dict_name_synonym_to_mondo_id:
                        dict_name_synonym_to_mondo_id[additional_synonym_names[1]] = [identifier]
                    else:
                        dict_name_synonym_to_mondo_id[additional_synonym_names[1]].append(identifier)
                        part_list = set(dict_name_synonym_to_mondo_id[additional_synonym_names[1]])
                        dict_name_synonym_to_mondo_id[additional_synonym_names[1]] = list(part_list)
                if synonym not in dict_name_synonym_to_mondo_id:
                    dict_name_synonym_to_mondo_id[synonym] = [identifier]
                else:
                    dict_name_synonym_to_mondo_id[synonym].append(identifier)
                    part_list = set(dict_name_synonym_to_mondo_id[synonym])
                    dict_name_synonym_to_mondo_id[synonym] = list(part_list)
        else:
            synonyms = []

        # list of the umls cuis without the label 'UMLS_CUI:'
        umls_cuis_without_label = []

        for umls_cui in umls_cuis:
            if len(umls_cui) > 0:
                cui = umls_cui.split(':')[1]
                umls_cuis_without_label.append(cui)
                if cui in dict_umls_cui_to_mondo:
                    dict_umls_cui_to_mondo[cui].append(identifier)
                else:
                    dict_umls_cui_to_mondo[cui] = [identifier]

        # generate dictionary with doid to mondo
        if not doids is None:
            for doid in doids:
                if doid in dict_doid_to_mondo:
                    dict_doid_to_mondo[doid].append(identifier)
                else:
                    dict_doid_to_mondo[doid] = [identifier]

        # add all mondo  with mesh and omim in the dictionaries
        for xref in xrefs:
            if xref.split(':')[0] == 'MESH':
                if not xref.split(':')[1] in dict_mesh_to_mondo:
                    dict_mesh_to_mondo[xref.split(':')[1]] = [identifier]
                else:
                    dict_mesh_to_mondo[xref.split(':')[1]].append(identifier)
                    dict_mesh_to_mondo[xref.split(':')[1]] = list(set(dict_mesh_to_mondo[xref.split(':')[1]]))
            elif xref.split(':')[0] == 'OMIM':
                if not xref.split(':')[1] in dict_omim_to_mondo:
                    dict_omim_to_mondo[xref.split(':')[1]] = [identifier]
                else:
                    dict_omim_to_mondo[xref.split(':')[1]].append(identifier)
                    dict_omim_to_mondo[xref.split(':')[1]] = list(set(dict_omim_to_mondo[xref.split(':')[1]]))

        # generate class DiseaseHetionet and add to dictionary
        disease = DiseaseHetionet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_diseases_hetionet[identifier] = disease
    print('length of disease in hetionet:' + str(len(dict_diseases_hetionet)))
    print('number of different MESH in mondo:' + str(len(dict_mesh_to_mondo)))
    print('number of different OMIM in mondo:' + str(len(dict_omim_to_mondo)))
    print('number of different UMLS CUI in mondo' + str(len(dict_umls_cui_to_mondo)))


# list of MESH/OMIM IDs which are not mapped to a mondo
list_not_mapped_to_mondo = []

# list of MESH/OMIM  IDs which are mapped
list_mapped_to_mondo = set([])

'''
load in all ctd disease from neo4j 
properties:
    idType
    altDiseaseIDs
    disease_id	
    synonyms
    parentIDs
    name
    parentTreeNumbers
    definition
    tree
    slimMappings
add all disease to a dictionary
then search if the disease has in CTD mondo as alternative ID 
'''


def load_disease_CTD():
    query = ''' MATCH (n:CTDdisease) RETURN n'''
    results = g.run(query)

    # go through all results from the query
    for result, in results:
        idType = result['idType']
        name = result['name']
        disease_id = result['disease_id']
        altDiseaseIDs = result['altDiseaseIDs'] if 'altDiseaseIDs' in result else []

        has_mondo = False
        list_dos = []
        for altDiseaseId in altDiseaseIDs:
            if altDiseaseId[0:2] == 'DO':
                list_dos.append(altDiseaseId[3:])

        disease = DiseaseCTD(idType, name, altDiseaseIDs, disease_id, list_dos)
        dict_CTD_disease[disease_id] = disease

    print('size of disease in neo4j:' + str(len(dict_CTD_disease)))
    # print('number of mapped ctd disease:' + str(len(list_mapped_to_mondo)))
    # print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
map with use of mesh and omim ID to Monarch Disease Ontology
'''


def map_disease_with_mesh_omim_to_monarch_disease_ontology():
    counter = 0
    for disease_id, disease in dict_CTD_disease.items():
        if disease_id == 'D007007':
            print('blu')
        counter += 1
        # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
        if disease.idType == 'MESH':
            if disease_id in dict_mesh_to_mondo:
                mondos_ids = dict_mesh_to_mondo[disease_id]
                dict_CTD_disease[disease_id].set_mondos(mondos_ids)
                dict_CTD_disease[disease_id].set_mapping_id(disease_id)
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id')
                list_mapped_to_mondo.add(disease_id)
                continue

        elif disease.idType == 'OMIM':
            if disease_id in dict_omim_to_mondo:
                mondos_ids = dict_omim_to_mondo[disease_id]
                dict_CTD_disease[disease_id].set_mondos(mondos_ids)
                dict_CTD_disease[disease_id].set_mapping_id(disease_id)
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id')
                list_mapped_to_mondo.add(disease_id)
                continue
        # else:
        #     print('geht es hier rein?')
        #     if disease_id in dict_omim_to_mondo:
        #         dict_CTD_disease[disease_id].set_mondos(dict_omim_to_mondo[disease_id])
        #         dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id')
        #         list_mapped_to_mondo.append(disease_id)
        #         continue
        #     elif disease_id in dict_mesh_to_mondo:
        #         dict_CTD_disease[disease_id].set_mondos(dict_mesh_to_mondo[disease_id])
        #         dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM tomondo id')
        #         list_mapped_to_mondo.append(disease_id)
        #         continue

        list_not_mapped_to_mondo.append(disease_id)

    print('number of mapped ctd disease after mesh/omim map:' + str(counter - len(list_not_mapped_to_mondo)))
    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
try to mapped the alternative mesh and omim ids
'''


def try_mapping_with_alternativ(altDiseaseID, disease_id, delete_map_mondo):
    mapped=False
    # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
    if altDiseaseID[0:4] == 'MESH':
        if altDiseaseID[5:] in dict_mesh_to_mondo:
            dict_CTD_disease[disease_id].set_mondos(dict_mesh_to_mondo[altDiseaseID[5:]])
            dict_CTD_disease[disease_id].set_mapping_id(altDiseaseID[5:])
            dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id with alternativ id')
            delete_map_mondo.add(list_not_mapped_to_mondo.index(disease_id))
            list_mapped_to_mondo.add(disease_id)
            mapped=True


    elif altDiseaseID[0:4] == 'OMIM':
        if altDiseaseID[5:] in dict_omim_to_mondo:
            omim_id = altDiseaseID[5:]
            mondos = dict_omim_to_mondo[altDiseaseID[5:]]
            dict_CTD_disease[disease_id].set_mondos(mondos)
            dict_CTD_disease[disease_id].set_mapping_id(altDiseaseID[5:])
            dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id with alternativ id')
            delete_map_mondo.add(list_not_mapped_to_mondo.index(disease_id))
            list_mapped_to_mondo.add(disease_id)
            mapped = True

    return delete_map_mondo, mapped


'''
map with us of mesh and omim of alternative ids to Monarch Disease Ontology
'''


def map_disease_with_mesh_omim_alternativ_ids_to_monarch_disease_ontology():
    counter = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = set([])
    for disease_id in list_not_mapped_to_mondo:
        if disease_id == 'D007239':
            print('blub')
        counter += 1
        altDiseaseIDs = dict_CTD_disease[disease_id].altDiseaseIDs
        mapped_something=False

        if type(altDiseaseIDs) == list:
            for altDiseaseID in altDiseaseIDs:
                delete_map_mondo,mapped = try_mapping_with_alternativ(altDiseaseID, disease_id, delete_map_mondo)
                if mapped:
                    mapped_something
        else:
            delete_map_mondo,mapped = try_mapping_with_alternativ(altDiseaseIDs, disease_id, delete_map_mondo)
            mapped_something=mapped

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo = list(delete_map_mondo)
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease after mesh/omim alternativ id map:' + str(
        counter - len(list_not_mapped_to_mondo)))
    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
Map with use of doids
'''


def map_disease_with_doids_to_monarch_disease_ontology():
    counter = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    for disease_id in list_not_mapped_to_mondo:
        if disease_id == 'D007239':
            print('blub')
        counter += 1
        doids = dict_CTD_disease[disease_id].doids
        if type(doids) == list:
            for doid in doids:
                if doid in dict_doid_to_mondo:
                    dict_CTD_disease[disease_id].set_mondos(dict_doid_to_mondo[doid])
                    dict_CTD_disease[disease_id].set_mapping_id(doid)
                    dict_CTD_disease[disease_id].set_how_mapped('map with DOID to mondo id')
                    delete_map_mondo.append(list_not_mapped_to_mondo.index(disease_id))
                    list_mapped_to_mondo.add(disease_id)
        else:
            if doids in dict_doid_to_mondo:
                dict_CTD_disease[disease_id].set_mondos(dict_doid_to_mondo[doids])
                dict_CTD_disease[disease_id].set_mapping_id(doids)
                dict_CTD_disease[disease_id].set_how_mapped('map with DOID to mondo id')
                delete_map_mondo.append(list_not_mapped_to_mondo.index(disease_id))
                list_mapped_to_mondo.add(disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease after mesh/omim alternativ id map:' + str(
        counter - len(list_not_mapped_to_mondo)))
    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
mapping with cui?
'''


def map_to_cui_and_try_to_map_to_hetionet():
    counter_map = 0
    counter_map_but_not = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    # number of not mapped mesh ids
    count_not_mapped = 0
    for identifier in list_not_mapped_to_mondo:
        idType = dict_CTD_disease[identifier].idType
        # this map to MONDO:0013267 but this is wrong
        if identifier=='607447':
            continue
        # this map to MONDO:0007803
        elif identifier=='D007024':
            dict_CTD_disease[identifier].set_mondos(['MONDO:0005469'])
            dict_CTD_disease[identifier].set_mapping_id('self mapped')
            delete_map_mondo.append(list_not_mapped_to_mondo.index(identifier))
            dict_CTD_disease[identifier].set_how_mapped('cui match')
            list_mapped_to_mondo.add(identifier)
            counter_map += 1
            continue

        sab = ''
        # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
        if idType == 'MESH':
            sab = 'MSH'
        elif idType == 'OMIM':
            sab = 'OMIM'
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB, STR From MRCONSO Where SAB in ('%s') and CODE= '%s';")
        query = query % (sab, identifier)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            found_some = False
            for (cui, lat, code, sab, label) in cur:
                if cui in dict_umls_cui_to_mondo:
                    found_some = True
                    dict_CTD_disease[identifier].set_mondos(dict_umls_cui_to_mondo[cui])
                    dict_CTD_disease[identifier].set_mapping_id(cui)
                    delete_map_mondo.append(list_not_mapped_to_mondo.index(identifier))
                    dict_CTD_disease[identifier].set_how_mapped('cui match')
                    list_mapped_to_mondo.add(identifier)
            if not found_some:
                counter_map_but_not += 1
            else:

                counter_map += 1
        else:
            count_not_mapped

    print('number of mapped:' + str(counter_map))
    print('number of mapped but not:' + str(counter_map_but_not))
    print('number of not mapped:' + str(count_not_mapped))

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo = list(set(delete_map_mondo))
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
map the name of ctd disease name to name or synonym of Monarch Disease Ontology
'''


def map_with_name():
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    for ctd_disease_id in list_not_mapped_to_mondo:
        name = dict_CTD_disease[ctd_disease_id].name.lower()

        if name.lower() in dict_name_synonym_to_mondo_id:
            dict_CTD_disease[ctd_disease_id].set_mondos(dict_name_synonym_to_mondo_id[name.lower()])
            dict_CTD_disease[ctd_disease_id].set_mapping_id('')
            delete_map_mondo.append(list_not_mapped_to_mondo.index(ctd_disease_id))
            dict_CTD_disease[ctd_disease_id].set_how_mapped('string match')
            list_mapped_to_mondo.add(ctd_disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


# files for the different map strategies
map_mesh_omim_to_mondo = open('disease_Disease/map_CTD_disease_mesh_omim_to_mondo.tsv', 'w')
map_mesh_omim_to_mondo.write(
    'CTD MESH/OMIM \t type\tname \t Monarch Disease Ontology divided by | \t mondo names \t map_id \n')

map_mesh_omim_to_mondo_with_alt = open('disease_Disease/map_CTD_disease_alternativ_mesh_omim_to_mondo.tsv', 'w')
map_mesh_omim_to_mondo_with_alt.write(
    'CTD MESH/OMIM \t type\tname \t Monarch Disease Ontology divided by | \t mondo names\t map_id \n')

map_mesh_omim_to_mondo_with_name = open('disease_Disease/map_CTD_disease_name_to_mondo_name_synonyms.tsv', 'w')
map_mesh_omim_to_mondo_with_name.write(
    'CTD MESH/OMIM \t type\tname  \t Monarch Disease Ontology divided by | \t mondo names\t map_id \n')

map_doid_to_mondo = open('disease_Disease/map_CTD_disease_doid_to_mondo.tsv', 'w')
map_doid_to_mondo.write(
    'CTD MESH/OMIM \t type\tname \t Monarch Disease Ontology divided by | \t mondo names\t map_id \n')

map_cui_to_mondo = open('disease_Disease/map_CTD_disease_map_to_cui_to_mondo.tsv', 'w')
map_cui_to_mondo.write(
    'CTD MESH/OMIM \t type\tname \t Monarch Disease Ontology divided by | \t mondo names\t map_id \n')

# multiple mapped ctd disease
multiple_mapped_ctd_disease = open('disease_Disease/multiple_mapped_ctd_disease.tsv', 'w')
multiple_mapped_ctd_disease.write(
    'CTD MESH/OMIM \t type\tname \t Monarch Disease Ontology divided by | \t mondo names\t mapping_strategy \n')

# dictionary map how_mapped to a file
dict_how_mapped_to_file = {
    'map with Mesh or OMIM to mondo id': map_mesh_omim_to_mondo,
    'map with Mesh or OMIM to mondo id with alternativ id': map_mesh_omim_to_mondo_with_alt,
    'string match': map_mesh_omim_to_mondo_with_name,
    'map with DOID to mondo id': map_doid_to_mondo,
    'cui match': map_cui_to_mondo
}

# dictionary multiple mapping ctd which mapping source
dict_how_mapped_to_multiple_mapping = {
    'map with Mesh or OMIM to mondo id': 0,
    'map with Mesh or OMIM to mondo id with alternativ id': 0,
    'string match': 0,
    'map with DOID to mondo id': 0,
    'cui match': 0
}

'''
integrate disease into hetionet:
The ctd disease in neo4j gett a connection to the hetionet disease.
Further they get the list of mondos as properties.
The mapped hetionet disease  will get additional properties.
'''


def integrate_disease_into_hetionet():
    counter_all = 0
    counter_not_mapped = 0

    counter_intersection = 0
    # count the number of mapped ctd disease
    counter_with_mondos = 0
    csvfile_ctd_hetionet_disease = open('disease_Disease/ctd_hetionet.csv', 'wb')
    writer = csv.writer(csvfile_ctd_hetionet_disease, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['ctdDiseaseID', 'HetionetDiseaseId'])

    cypher_file = open('disease_Disease/mapping.cypher', 'wb')
    cypher_file.write('begin\n')
    query='''Match (d)-[r:equal_to_D_Disease_CTD]->(n) Delete r;\n '''
    cypher_file.write(query)
    cypher_file.write('commit\n')
    # go through all ctd disease
    for ctd_disease_id, ctd_disease in dict_CTD_disease.items():
        counter_all += 1
        name = ctd_disease.name.lower()
        if ctd_disease_id == 'D004806':
            print('blub')
        mondos = ctd_disease.mondos
        if len(mondos) > 1 and type(mondos) == list:
            if name.lower() in dict_name_synonym_to_mondo_id:
                mondos_name = dict_name_synonym_to_mondo_id[name.lower()]
                mondos_intersection = list(set(mondos).intersection(mondos_name))
                if len(mondos_intersection) > 0:
                    counter_intersection += 1
                    mondos = mondos_intersection
                    print(ctd_disease_id)
        if len(mondos) > 0:
            counter_with_mondos += 1
            how_mapped = ctd_disease.how_mapped
            string_mondos = "|".join(mondos)
            names = ''

            mapping_ids = ctd_disease.mapping
            mapping_ids_string = '|'.join(mapping_ids)

            for mondo in mondos:
                names += dict_hetionet_id_to_name[mondo] + '|'
            idType = ctd_disease.idType
            if len(mondos) > 1:
                dict_how_mapped_to_multiple_mapping[how_mapped] += 1
                multiple_mapped_ctd_disease.write(
                    ctd_disease_id + '\t' + idType + '\t' + name + '\t' + string_mondos + '\t' + names[
                                                                                                 :-1] + '\t' + how_mapped + '\n')

            dict_how_mapped_to_file[how_mapped].write(
                ctd_disease_id + '\t' + idType + '\t' + name + '\t' + string_mondos + '\t' + names[
                                                                                             :-1] + '\t' + mapping_ids_string + '\n')
            string_mondos = "','".join(mondos)
            # set in neo4j the mondos for the ctd disease
            query = '''MATCH (n:CTDdisease{disease_id:'%s'}) SET n.mondos=['%s'] '''
            query = query % (ctd_disease_id, string_mondos)
            g.run(query)

            # generate for all mapped mondos a connection and add new properties to Hetionet disease
            for mondo in mondos:
                writer.writerow([ctd_disease_id, mondo])
        else:
            counter_not_mapped += 1
            if ctd_disease_id not in list_not_mapped_to_mondo:
                print(ctd_disease_id)
            #     print(ctd_disease.how_mapped)

    print('all steps:' + str(counter_all))
    print('not mapped:' + str(counter_not_mapped))
    print('number of mapped ctd disease:' + str(counter_with_mondos))
    print('counter intersection mondos:' + str(counter_intersection))
    print(dict_how_mapped_to_multiple_mapping)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/disease_Disease/ctd_hetionet.csv" As line MATCH (n:CTDdisease{disease_id:line.ctdDiseaseID}), (d:Disease{identifier:line.HetionetDiseaseId}) Merge (d)-[:equal_to_D_Disease_CTD]->(n) With line, d, n Where d.ctd='no' Set d.resource=d.resource+'CTD', d.ctd='yes', d.ctd_url='http://ctdbase.org/detail.go?type=disease&acc='+line.ctdDiseaseID;\n '''
    cypher_file.write(query)
    cypher_file.write('begin\n')
    #    search for all disease that did not mapped with ctd disease and give them the property ctd:'no'
    query = '''MATCH (n:Disease) Where Not Exists(n.ctd) SET n.ctd='no';\n '''
    cypher_file.write(query)
    cypher_file.write('commit\n')
    cypher_file.write('begin\n')
    # set all ctd disease which are not mapped the mondo as empty
    query = '''MATCH (n:CTDdisease) Where Not Exists(n.mondos) SET n.mondos=[];\n'''
    cypher_file.write(query)
    cypher_file.write('commit\n')

    # generate a file with all not mapped diseases from ctd
    file_not_map = open('disease_Disease/not_map_CTD_disease.tsv', 'w')
    file_not_map.write('CTD MESH/OMIM \t type  \t CTD names \n')
    for identifier_ctd in list_not_mapped_to_mondo:
        ctd_disease = dict_CTD_disease[identifier_ctd]
        idType = ctd_disease.idType
        name = ctd_disease.name
        file_not_map.write(identifier_ctd + '\t' + idType + '\t' + name + '\n')


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all disease from hetionet into a dictionary')

    load_hetionet_diseases_in()

    # print(dict_name_synonym_to_mondo_id['Combined Oxidative Phosphorylation Deficiency type 5'.lower()])

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all ctd diseases from neo4j into a dictionary')

    load_disease_CTD()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease mesh or Omim to Disease ')

    map_disease_with_mesh_omim_to_monarch_disease_ontology()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease alternative mesh or Omim to Disease ')

    map_disease_with_mesh_omim_alternativ_ids_to_monarch_disease_ontology()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease doid to Disease ')

    map_disease_with_doids_to_monarch_disease_ontology()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease cui to Disease ')

    map_to_cui_and_try_to_map_to_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease name to mondo name and synonyms')

    map_with_name()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('integrate disease into hetionet')

    integrate_disease_into_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
