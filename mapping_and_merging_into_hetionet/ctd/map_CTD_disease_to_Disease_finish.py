# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys


class DiseaseHetionet:
    """
    identifier: string (DOID)
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
    altDiseaseIDs: list (can be mesh, omim or DOID)
    disease_id: sting (the mesh or omim ID)
    cuis: list (umls cuis of this disease)
    doids:list (mapped doids)
    how_mapped: string
    """

    def __init__(self, idType, name, altDiseaseIDs, disease_id):
        self.idType = idType
        self.name = name
        self.altDiseaseIDs = altDiseaseIDs
        self.disease_id = disease_id
        self.doids = []
        self.cuis = []

    def set_cuis(self, cuis):
        self.cuis = cuis

    def set_doids(self, doids):
        self.doids = doids

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all CTD diseases, which has a relationship  treats or induces with a drug
dict_CTD_disease = {}

# dictionary for hetionet diseases with DOID as key and value is class DiseaseHetionet
dict_diseases_hetionet = {}

# dictionary mesh to doids, information from Disease Ontology
dict_mesh_to_dois = {}

# dictionary omim to doids, information from Disease Ontology
dict_omim_to_dois = {}

# dictionary with name/synonyms to doid
dict_name_synonym_to_do_id = {}

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
    query = '''MATCH (n:Disease) RETURN n.identifier,n.name, n.synonyms, n.xrefs, n.umls_cuis, n.resource'''
    results = g.run(query)

    for identifier, name, synonyms, xrefs, umls_cuis, resource, in results:
        # add name with doid to dictionary
        dict_name_synonym_to_do_id[name.lower()] = identifier

        # add the differnt synonyms with doid to dictionary
        for synonym in synonyms:
            synonym = synonym.split(':')[0].lower()
            dict_name_synonym_to_do_id[synonym] = identifier

        # list of the umls cuis without the label 'UMLS_CUI:'
        umls_cuis_without_label = []

        for umls_cui in umls_cuis:
            if len(umls_cui) > 0:
                cui = umls_cui.split(':')[1]
                umls_cuis_without_label.append(cui)

        # add all doid  with mesh and omim in the dictionaries
        for xref in xrefs:
            if xref.split(':')[0] == 'MESH':
                if not xref.split(':')[1] in dict_mesh_to_dois:
                    dict_mesh_to_dois[xref.split(':')[1]] = [identifier]
                else:
                    dict_mesh_to_dois[xref.split(':')[1]].append(identifier)
                    dict_mesh_to_dois[xref.split(':')[1]] = list(set(dict_mesh_to_dois[xref.split(':')[1]]))
            elif xref.split(':')[0] == 'OMIM':
                if not xref.split(':')[1] in dict_omim_to_dois:
                    dict_omim_to_dois[xref.split(':')[1]] = [identifier]
                else:
                    dict_omim_to_dois[xref.split(':')[1]].append(identifier)
                    dict_omim_to_dois[xref.split(':')[1]] = list(set(dict_omim_to_dois[xref.split(':')[1]]))

        # generate class DiseaseHetionet and add to dictionary
        disease = DiseaseHetionet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_diseases_hetionet[identifier] = disease
    print('length of disease in hetionet:' + str(len(dict_diseases_hetionet)))
    print('number of different MESH in DO:' + str(len(dict_mesh_to_dois)))
    print('number of different OMIM in DO:' + str(len(dict_omim_to_dois)))
    print('number of different cui in DO:' + str(len(dict_cui_to_dois)))


# list of MESH/OMIM IDs which are not mapped to a DOID
list_not_mapped_to_DOID = []

# list of MESH/OMIM  IDs which are mapped
list_mapped_to_DOID = []

'''
load in all ctd disease from neo4j which has  a relationship with a drug (marker/mechanism Or therapeutic)
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
then search if the disease has in CTD DOID as alternative ID 
'''


def load_disease_CTD():
    query = ''' MATCH ()-[r:Association]->(n:CTDdisease) Where r.directEvidence='marker/mechanism' Or r.directEvidence='therapeutic'  RETURN Distinct n '''
    results = g.run(query)

    # go through all results from the query
    for result, in results:
        idType = result['idType']
        name = result['name']
        disease_id = result['disease_id']
        altDiseaseIDs = result['altDiseaseIDs'].split('|')

        disease = DiseaseCTD(idType, name, altDiseaseIDs, disease_id)
        dict_CTD_disease[disease_id] = disease
        has_DOID = False
        list_doids = []
        for altDiseaseId in altDiseaseIDs:
            if altDiseaseId[0:2] == 'DO':
                if altDiseaseId[3:] in dict_diseases_hetionet:
                    has_DOID = True
                    list_doids.append(altDiseaseId[3:])

        if not has_DOID:
            list_not_mapped_to_DOID.append(disease_id)
        else:
            list_doids = list(set(list_doids))
            dict_CTD_disease[disease_id].set_doids(list_doids)
            dict_CTD_disease[disease_id].set_how_mapped('map with alternativ ctd id DOID')
            list_mapped_to_DOID.append(disease_id)

    print('size of disease in neo4j:' + str(len(dict_CTD_disease)))
    print('number of mapped ctd disease:' + str(len(list_mapped_to_DOID)))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_DOID)))


'''
map with use of mesh and omim ID to Disease Ontology
'''


def map_disease_with_mesh_omim_to_disease_ontology():
    counter = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_doid = []
    for disease_id in list_not_mapped_to_DOID:
        counter += 1
        disease = dict_CTD_disease[disease_id]
        # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
        if disease.idType == 'MESH':
            if disease_id in dict_mesh_to_dois:
                dict_CTD_disease[disease_id].set_doids(dict_mesh_to_dois[disease_id])
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to DO id')
                delete_map_doid.append(list_not_mapped_to_DOID.index(disease_id))
                list_mapped_to_DOID.append(disease_id)

        elif disease.idType == 'OMIM':
            if disease_id in dict_omim_to_dois:
                dict_CTD_disease[disease_id].set_doids(dict_omim_to_dois[disease_id])
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to DO id')
                delete_map_doid.append(list_not_mapped_to_DOID.index(disease_id))
                list_mapped_to_DOID.append(disease_id)
        else:
            if disease_id in dict_omim_to_dois:
                dict_CTD_disease[disease_id].set_doids(dict_omim_to_dois[disease_id])
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to DO id')
                delete_map_doid.append(list_not_mapped_to_DOID.index(disease_id))
                list_mapped_to_DOID.append(disease_id)
            elif disease_id in dict_mesh_to_dois:
                dict_CTD_disease[disease_id].set_doids(dict_mesh_to_dois[disease_id])
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to DO id')
                delete_map_doid.append(list_not_mapped_to_DOID.index(disease_id))
                list_mapped_to_DOID.append(disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifier
    delete_map_doid.sort()
    delete_map_doid = list(reversed(delete_map_doid))
    for index in delete_map_doid:
        list_not_mapped_to_DOID.pop(index)

    print('number of mapped ctd disease after mesh/omim map:' + str(counter - len(list_not_mapped_to_DOID)))
    print('number of mapped ctd disease:' + str(len(list_mapped_to_DOID)))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_DOID)))


'''
map with us of mesh and omim of alternative ids to Disease Ontology
'''


def map_disease_with_mesh_omim_alternativ_ids_to_disease_ontology():
    counter = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_doid = []
    for disease_id in list_not_mapped_to_DOID:
        counter += 1
        altDiseaseIDs = dict_CTD_disease[disease_id].altDiseaseIDs
        for altDiseaseID in altDiseaseIDs:
            # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
            if altDiseaseID[0:4] == 'MESH':
                if altDiseaseID[5:] in dict_mesh_to_dois:
                    dict_CTD_disease[disease_id].set_doids(dict_mesh_to_dois[altDiseaseID[5:]])
                    dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to DO id with alternativ id')
                    delete_map_doid.append(list_not_mapped_to_DOID.index(disease_id))
                    list_mapped_to_DOID.append(disease_id)


            elif altDiseaseID[0:4] == 'OMIM':
                if altDiseaseID[5:] in dict_omim_to_dois:
                    dict_CTD_disease[disease_id].set_doids(dict_omim_to_dois[altDiseaseID[5:]])
                    dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to DO id with alternativ id')
                    delete_map_doid.append(list_not_mapped_to_DOID.index(disease_id))
                    list_mapped_to_DOID.append(disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_doid.sort()
    delete_map_doid = list(reversed(delete_map_doid))
    for index in delete_map_doid:
        list_not_mapped_to_DOID.pop(index)

    print('number of mapped ctd disease after mesh/omim alternativ id map:' + str(
        counter - len(list_not_mapped_to_DOID)))
    print('number of mapped ctd disease:' + str(len(list_mapped_to_DOID)))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_DOID)))



'''
map the name of ctd disease name to name or synonym of disease ontology
'''


def map_with_name():
    # all mesh and omim identifier which are mapped in this function
    delete_map_doid = []
    for label in dict_name_synonym_to_do_id.keys():
        for ctd_disease_id in list_not_mapped_to_DOID:
            name = dict_CTD_disease[ctd_disease_id].name.lower()
            label = label.lower()
            # some terms has some definition for their names
            label_split = label.split(' exact')[0]
            if name.lower() == label_split:
                dict_CTD_disease[ctd_disease_id].doids.append(dict_name_synonym_to_do_id[label])
                delete_map_doid.append(list_not_mapped_to_DOID.index(ctd_disease_id))
                dict_CTD_disease[ctd_disease_id].set_how_mapped('string match')
                list_mapped_to_DOID.append(ctd_disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_doid.sort()
    delete_map_doid = list(reversed(delete_map_doid))
    for index in delete_map_doid:
        list_not_mapped_to_DOID.pop(index)

    print('number of mapped ctd disease:' + str(len(list_mapped_to_DOID)))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_DOID)))



# files for the different map strategies
map_mesh_omim_to_doid = open('disease_Disease/map_CTD_disease_mesh_omim_to_DO_DOID.tsv', 'w')
map_mesh_omim_to_doid.write('CTD MESH/OMIM \t type  \t Disease ontology divided by | \t cui names \n')

map_cui_to_doid = open('disease_Disease/map_CTD_disease_mesh_omim_to_cui_to_DO_DOID.tsv', 'w')
map_cui_to_doid.write('CTD MESH/OMIM \t type \t Disease ontology divided by | \t cui names \n')

map_synonym_cuis_to_doid = open('disease_Disease/map_CTD_disease_synonym_cuis_to_DO_DOID.tsv', 'w')
map_synonym_cuis_to_doid.write(
    'CTD MESH/OMIM \t type \t  Disease ontology divided by | \t cui names \n')

map_cdt_doid = open('disease_Disease/map_CTD_DOID.tsv', 'w')
map_cdt_doid.write('CTD MESH/OMIM \t type \t Disease ontology divided by | \t cui names \n')

map_mesh_omim_to_doid_with_alt = open('disease_Disease/map_CTD_disease_alternativ_mesh_omim_to_DO_DOID.tsv', 'w')
map_mesh_omim_to_doid_with_alt.write(
    'CTD MESH/OMIM \t type  \t Disease ontology divided by | \t cui names \n')

map_mesh_omim_to_doid_with_name = open('disease_Disease/map_CTD_disease_name_to_DO_name_synonyms.tsv', 'w')
map_mesh_omim_to_doid_with_name.write(
    'CTD MESH/OMIM \t type  \t Disease ontology divided by | \t cui names \n')

# dictionary map how_mapped to a file
dict_how_mapped_to_file = {
    'map with Mesh or OMIM to DO id': map_mesh_omim_to_doid,
    'map ctd cui to DO cui': map_cui_to_doid,
    'map ctd synonym cuis to DO cui': map_synonym_cuis_to_doid,
    'map with alternativ ctd id DOID': map_cdt_doid,
    'map with Mesh or OMIM to DO id with alternativ id': map_mesh_omim_to_doid_with_alt,
    'string match': map_mesh_omim_to_doid_with_name}

'''
integrate disease into hetionet:
The ctd disease in neo4j gett a connection to the hetionet disease.
Further they get the list of DOIDs as properties.
The mapped hetionet disease  will get additional properties.
'''


def integrate_disease_into_hetionet():
    # count the number of mapped ctd disease
    counter_with_doids = 0
    # go through all ctd disease
    for ctd_disease_id, ctd_disease in dict_CTD_disease.items():
        doids = ctd_disease.doids
        if len(doids) > 0:
            counter_with_doids += 1
            how_mapped = ctd_disease.how_mapped
            string_doids = "|".join(doids)
            idType = ctd_disease.idType
            names = ''

            dict_how_mapped_to_file[how_mapped].write(
                ctd_disease_id + '\t' + idType + '\t' + string_doids + '\t' + names[:-1] + '\n')
            string_doids = "','".join(doids)
            #set in neo4j the doids for the ctd disease
            query = '''MATCH (n:CTDdisease{disease_id:'%s'}) SET n.doids=['%s'] '''
            query = query % (ctd_disease_id, string_doids)
            g.run(query)

            # generate for all mapped doids a connection and add new properties to Hetionet disease
            for doid in doids:
                resource = dict_diseases_hetionet[doid].resource
                resource.append('CTD')
                resource = list(set(resource))
                resource = "','".join(resource)
                query = '''MATCH (n:CTDdisease{disease_id:'%s'}), (d:Disease{identifier:'%s'}) 
                Set d.resource=['%s'], d.ctd='yes', d.ctd_url='http://ctdbase.org/detail.go?type=disease&acc=%s'
                Create (d)-[:equal_to_D_Disease_CTD]->(n);           
                '''
                query = query % (
                    ctd_disease_id, doid, resource, dict_CTD_disease[ctd_disease_id].idType + ':' + ctd_disease_id)
                g.run(query)

    print('number of mapped ctd disease:' + str(counter_with_doids))

    #    search for all disease that did not mapped with ctd disease and give them the property ctd:'no'
    query = '''MATCH (n:Disease) Where Not Exists(n.ctd) SET n.ctd='no' '''
    g.run(query)
    # set all ctd disease which are not mapped the doid as empty
    query = '''MATCH (n:CTDdisease) Where Not Exists(n.doids) SET n.doids=[]'''
    g.run(query)

    # generate a file with all not mapped diseases from ctd
    file_not_map = open('disease_Disease/not_map_CTD_disease.tsv', 'w')
    file_not_map.write('CTD MESH/OMIM \t type  \t CTD names \n')
    for identifier_ctd in list_not_mapped_to_DOID:
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

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all ctd diseases from neo4j into a dictionary')

    load_disease_CTD()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease mesh or Omim to Disease ')

    map_disease_with_mesh_omim_to_disease_ontology()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease alternative mesh or Omim to Disease ')

    map_disease_with_mesh_omim_alternativ_ids_to_disease_ontology()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd disease name to DO name and synonyms')

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
