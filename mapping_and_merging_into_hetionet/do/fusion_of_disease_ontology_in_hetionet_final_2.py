# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:52:43 2017

@author: ckoenig
"""
from itertools import count

'''integrate the other diseases and relationships from disease ontology in hetionet'''
from py2neo import Graph, authenticate
import datetime
import sys


class Disease:
    """
    source: string
    url: string
    license: string
    name: string
    identifier: string (DOID)
    definition: string
    synonyms: list of strings (names)
    xrefs: list of strings (like mesh or omim)
    umls_cuis: list of strings
    alternateIds: list of strings (alternatives doids)
    subset: list of strings
    resource: list of strings
    """

    def __init__(self, source, url, licenses, name, identifier, resource):
        self.source = source
        self.url = url
        self.license = licenses
        self.name = name
        self.identifier = identifier
        self.definition = ''
        self.synonyms = ''
        self.xrefs = ''
        self.umls_cuis = ''
        self.alternateIds = ''
        self.subset = ''
        self.resource = resource

    def set_other_properties(self, definition, synonyms, xrefs, umls_cuis, alternateIds, subset):
        self.definition = definition
        self.synonyms = synonyms
        self.xrefs = xrefs
        self.umls_cuis = umls_cuis
        self.alternateIds = alternateIds
        self.subset = subset


# file to put all information in it
output = open('output_fusion_10_8.txt', 'w')

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary of all diseases in hetionet with key the disease ontology and value class Disease
dict_diseases_in_hetionet = {}

# list doids of all disease in hetionet
list_diseases_in_hetionet = []

'''
load all disease in the dictionary
has properties:
name 
identifier
source
license
url
'''


def load_all_hetionet_disease_in_dictionary():
    query = '''Match (n:Disease) RETURN n '''
    results = g.run(query)
    for diseases, in results:
        list_diseases_in_hetionet.append(diseases['identifier'])
        disease = Disease(diseases['source'], diseases['url'], diseases['license'], diseases['name'],
                          diseases['identifier'], 'Hetionet","Disease Ontology')
        dict_diseases_in_hetionet[diseases['identifier']] = disease
    print('size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)))
    output.write(
        'size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)) + '\n')


# in hetionet is a alternative doid used: dictionary with alternative id as key and original id in disease ontology
#   as value
dict_alternative_id = {}

'''
load the new and old information in the dictionary
test if not the alternativ doid is used in hetionet 
properties:
    definition
    synonyms
    xrefs: external identifier
    umls_cuis
    alternateIds
    subset
    id
    name
vorher 137
nacher 8498
DOID:9917 war nur als alternative id da
'''


def load_disease_ontologie_in_hetionet():
    query = '''Match (n:DiseaseOntology) RETURN n'''
    results = g.run(query)
    for diseases, in results:
        alternateIDs = diseases['alternateIds'] if diseases['alternateIds'] != None else []
        has_overlap_between_alternative_and_hetionet_id = True if len(
            list(set(alternateIDs) & set(dict_diseases_in_hetionet.keys()))) > 0 else False
        # hetionet has this doid not included
        if not diseases['id'] in dict_diseases_in_hetionet and not has_overlap_between_alternative_and_hetionet_id:

            source = 'Disease Ontology'
            licenses = 'CC0'
            name = diseases['name']
            identifier = diseases['id']
            url = 'http://purl.obolibrary.org/obo/DOID_' + identifier.split(':')[1]
            disease = Disease(source, url, licenses, name, identifier, 'Disease Ontology')
            dict_diseases_in_hetionet[diseases['id']] = disease
        # hetionet used the alternative doid
        elif has_overlap_between_alternative_and_hetionet_id:
            id_overlap = list(set(alternateIDs) & set(dict_diseases_in_hetionet.keys()))
            if len(id_overlap) == 1:
                disease = dict_diseases_in_hetionet[id_overlap[0]]

                print('is a alternative doid in disease ontology: ' + id_overlap[0])
                output.write('is a alternative doid in disease ontology: ' + id_overlap[0] + '\n')
                dict_all_doid_that_is_in_alternative[id_overlap[0]] = diseases['id']
                alternateIDs.append(diseases['id'])
            else:
                print('sad')
        # doid is already in hetionet
        else:
            disease = dict_diseases_in_hetionet[diseases['id']]

        # add the other information to the diseases
        xrefs = diseases['xrefs'] if diseases['xrefs'] != None else ''
        xref_umls_cuis = []
        xref_other = []
        for xref in xrefs:
            if xref.split(':')[0] == 'UMLS_CUI':
                xref_umls_cuis.append(xref)
            else:
                xref_other.append(xref)

        xref_other = '","'.join(xref_other).replace('\\', '').replace('"', "'")
        xref_umls_cuis = '","'.join(xref_umls_cuis)
        definition = diseases['definition'].replace('"', "'").replace('\\', '') if diseases[
                                                                                       'definition'] != None else ''
        synonyms = '","'.join(diseases['synonyms']).replace('\\', '') if diseases['synonyms'] != None else ''
        subset = '","'.join(diseases['subsets']) if diseases['subsets'] != None else ''
        disease.set_other_properties(definition, synonyms, xref_other, xref_umls_cuis, '","'.join(alternateIDs), subset)

    print('size of diseases after the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)))
    output.write(
        'size of diseases after the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)) + '\n')


# dictionary which has doid as key -is_a-> values are a list of the doids
dict_is_a_relationship = {}

# dictionary with key a doid which is a alternative id, value is the correct doid in disease ontology
dict_all_doid_that_is_in_alternative = {}

# dictionary with key doid in disease ontology and the alternative doid as value 
# (the opposite of dict_is_a_relationship)
dict_not_alternative_to_alternative = {}

'''
load connection from Disease ontolegy in dictionary and check if the alternative is used in hetionet
'''


def load_in_all_connection_from_diesease_ontology():
    counter = 0
    query = ''' Match (n:DiseaseOntology)-[r:is_a]->(p:DiseaseOntology) Return n,p '''
    results = g.run(query)
    for n, p, in results:
        if not n['id'] in dict_diseases_in_hetionet:
            alternative_ids, = n['alternateIds']
            for alternative_id in alternative_ids:
                if alternative_id in dict_diseases_in_hetionet:
                    n_id = alternative_id
        else:
            n_id = n['id']

        if not p['id'] in dict_diseases_in_hetionet:
            alternative_ids, = p['alternateIds']
            for alternative_id in alternative_ids:
                if alternative_id in dict_diseases_in_hetionet:
                    p_id = alternative_id

        else:
            p_id = p['id']

        if not n_id in dict_is_a_relationship:
            dict_is_a_relationship[n_id] = [p_id]
        else:
            dict_is_a_relationship[n_id].append(p_id)

        counter += 1

    print(counter)


'''
Generate new nodes and connection and add new properties to nodes
the disease nodes in hetionet get new properties, a connection is_a form a disease node to another and a connection form
 the disease node to a diseaseOntology node it generate new disease node with the infomation from diseaseOntology and 
 also the same connection as by the other disease nodes
'''


def integrate_DO_information_into_hetionet():
    # update disease in hetionet and generate connection between do diseases and hetionet disease
    print('Update nodes and generate connection to the DiseaseOntology node')
    output.write('Update nodes and generate connection to the DiseaseOntology node \n')
    for disease_doid in list_diseases_in_hetionet:

        query = '''Match (n:Disease), (o:DiseaseOntology) Where n.identifier="%s" And o.id="%s"
        Set n.definition="%s", n.synonyms=["%s"], n.xrefs=["%s"], n.umls_cuis=["%s"], n.alternateIds=["%s"], n.subset=["%s"], n.resource=["%s"], n.hetionet="yes", n.diseaseOntology="yes"
        Create (n)-[:equal_to]->(o); \n'''

        if not disease_doid in dict_all_doid_that_is_in_alternative:
            query = query % (disease_doid, disease_doid, dict_diseases_in_hetionet[disease_doid].definition,
                             dict_diseases_in_hetionet[disease_doid].synonyms,
                             dict_diseases_in_hetionet[disease_doid].xrefs,
                             dict_diseases_in_hetionet[disease_doid].umls_cuis,
                             dict_diseases_in_hetionet[disease_doid].alternateIds,
                             dict_diseases_in_hetionet[disease_doid].subset,
                             dict_diseases_in_hetionet[disease_doid].resource)
        else:
            print(disease_doid)
            query = query % (disease_doid, dict_all_doid_that_is_in_alternative[disease_doid],
                             dict_diseases_in_hetionet[disease_doid].definition,
                             dict_diseases_in_hetionet[disease_doid].synonyms,
                             dict_diseases_in_hetionet[disease_doid].xrefs,
                             dict_diseases_in_hetionet[disease_doid].umls_cuis,
                             dict_diseases_in_hetionet[disease_doid].alternateIds,
                             dict_diseases_in_hetionet[disease_doid].subset,
                             dict_diseases_in_hetionet[disease_doid].resource)

        g.run(query)

    # create new new hetionet diseases and add a connection to the do diseases
    print('Create the new nodes and connect them with the DiseaseOntology node')
    output.write('Create the new nodes and connect tham with the DiseaseOntology node')
    for key, disease in dict_diseases_in_hetionet.items():
        if not key in list_diseases_in_hetionet:
            query = '''Match (o:DiseaseOntology) Where o.id="%s"
            Create ( n:Disease {source: "%s", url: "%s", license:"%s", name:"%s",identifier:"%s" ,definition:"%s", synonyms:["%s"], xrefs:["%s"], umls_cuis:["%s"], alternateIds:["%s"], subset:["%s"], resource:["%s"], hetionet:"no", diseaseOntology:"yes"})
            Create (n)-[:equal_to]->(o); \n'''
            query = query % (
                key, disease.source, disease.url, disease.license, disease.name, disease.identifier, disease.definition,
                disease.synonyms, disease.xrefs, disease.umls_cuis, disease.alternateIds, disease.subset,
                dict_diseases_in_hetionet[disease_doid].resource)

            g.run(query)

    # create the is_a connection between the hetionet diseases
    print('Create the is_a connection for the Diseases')  #
    output.write('Create the is_a connection for the Diseases')
    # counter of all is_a connections
    count = 0
    for key, list_doid in dict_is_a_relationship.items():
        key = key if key not in dict_all_doid_that_is_in_alternative else dict_all_doid_that_is_in_alternative[key]

        for is_a_doid in list_doid:
            count+=1
            is_a_doid = is_a_doid if is_a_doid not in dict_all_doid_that_is_in_alternative else dict_all_doid_that_is_in_alternative[is_a_doid]
            query ='''Match (d:Disease {identifier:"%s"}), (d2:Disease {identifier:"%s"}) 
                Create (d)-[:IS_A_DiD{license:"CC0", source:"Disease Ontology", unbiased:"false"}]->(d2) '''
            query= query %(key, is_a_doid)
            g.run(query)

    print('number of is_a relationships:'+str(count))


def main():
    print(datetime.datetime.utcnow())
    output.write(str(datetime.datetime.utcnow()))
    print('create connection with neo4j')
    output.write('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    output.write(str(datetime.datetime.utcnow()))
    print('load all hetionet diseases in dictionary')
    output.write('load all hetionet diseases in dictionary')

    load_all_hetionet_disease_in_dictionary()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    output.write(str(datetime.datetime.utcnow()))

    print('load all disease ontology diseases in dictionary')
    output.write('load all disease ontology diseases in dictionary')

    load_disease_ontologie_in_hetionet()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    output.write(str(datetime.datetime.utcnow()))

    print('load all connection in dictionary')
    output.write('load all connection in dictionary')

    load_in_all_connection_from_diesease_ontology()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    output.write(str(datetime.datetime.utcnow()))

    print('integrate disease ontology into hetionet')
    output.write('integrate disease ontology into hetionet')

    integrate_DO_information_into_hetionet()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')
    print(len(dict_diseases_in_hetionet))

    print(datetime.datetime.utcnow())
    output.write(str(datetime.datetime.utcnow()))
    output.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
