# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:52:43 2017

@author: ckoenig
"""


'''integrate the other diseases and relationships from disease ontology in hetionet'''
from py2neo import Graph, authenticate
import datetime
import sys,csv



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
    alternative_ids: list of strings (alternatives doids)
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
        self.alternative_ids = ''
        self.subset = ''
        self.resource = resource

    def set_other_properties(self, definition, synonyms, xrefs, umls_cuis, alternative_ids, subset):
        self.definition = definition
        self.synonyms = synonyms
        self.xrefs = xrefs
        self.umls_cuis = umls_cuis
        self.alternative_ids = alternative_ids
        self.subset = subset


# file to put all information in it
output = open('output_fusion.txt', 'w')

# disease ontology license
license='CC0 1.0 Universal'

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
    for disease, in results:
        list_diseases_in_hetionet.append(disease['identifier'])
        disease=dict(disease)
        print(disease['identifier'])
        dict_diseases_in_hetionet['huh']=disease
        print(type(disease['identifier']))
        dict_diseases_in_hetionet[disease['identifier']] = disease
    print('size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)))
    output.write(
        'size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)) + '\n')


# in hetionet is a alternative doid used: dictionary with alternative id as key and original id in disease ontology
#   as value
dict_alternative_id = {}

#dictionary from disease ontology properties name to hetionet properties names
dict_DO_prop_to_hetionet_prop={'id':'identifier',
                               "synonym":"synonyms",
                               "def":"definition",
                               "alt_id":"alternative_ids",
                               }

dict_hetionet_prop_to_DO_prop={y:x for x,y in dict_DO_prop_to_hetionet_prop.items()}

# diesease ontology_name_resource
do_name="Disease Ontology"

# disease ontology label
do_label='diseaseontology'


# generate csv files for integration
header_nodes=['identifier','name','definition',"synonyms","umls_cuis","subset","xrefs","alternative_ids"]
#csv file for DOID which are already in Hetionet
file_included=open('output/already_included.csv','w')
csv_writer_included=csv.DictWriter(file_included, delimiter='\t',fieldnames=header_nodes)
csv_writer_included.writeheader()

header_alt=header_nodes[:]
header_alt.append('alternative_id')
file_included_alt=open('output/already_included_but_mapped_with_alt.csv','w')
csv_writer_included_alt=csv.DictWriter(file_included_alt, delimiter='\t',fieldnames=header_alt)
csv_writer_included_alt.writeheader()


file_included=open('output/new_nodes.csv','w')
csv_writer_new=csv.DictWriter(file_included, delimiter='\t',fieldnames=header_nodes)
csv_writer_new.writeheader()

# csv for relationship
#header of rela
header_rela=['child','parent']
file_included=open('output/new_rela.csv','w')
csv_writer_rela=csv.DictWriter(file_included, delimiter='\t',fieldnames=header_rela)
csv_writer_rela.writeheader()


'''
Create cypher file to update and create new Disease nodes from csv.
Also create cypher query for generat is a relationships between Diseases
'''
def generate_cypher_file():
    cypher_file=open('cypher.cypher','w')
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/do/output/%s.csv" As line FIELDTERMINATOR '\\t' '''

    query_middel_set=''
    query_middel_create=''
    query_middel_set_alt=''
    for header in header_nodes:
        if header in ['synonyms','alternative_ids','umls_cuis',"xrefs"]:
            query_middel_create+= header+':split(line.'+header+',"|"), '
            query_middel_set += 'n.'+header + '=split(line.' + header + ',"|"), '
            query_middel_set_alt+= 'n.'+header + '=split(line.' + header + ',"|"), '
            continue
        query_middel_create += header + ':line.' + header + ', '
        query_middel_set_alt += 'n.'+header + '=line.' + header + ', '
        if not header in ['url','identifier']:
            query_middel_set += 'n.'+header + '=line.' + header + ', '

    query_set=query_start+' Match (n:Disease{identifier:line.identifier}), (b:%s{id:line.identifier}) Set '+query_middel_set+ 'n.resource=["Hetionet","%s"], n.hetionet="yes", n.diseaseOntology="yes", n.license="%s" Create (n)-[:equal_to]->(b);\n'
    query_set=query_set % ("already_included",do_label,do_name,license)
    cypher_file.write(query_set)
    query_set_alt = query_start + ' Match (n:Disease{identifier:line.alternative_id}), (b:%s{id:line.identifier}) Set ' + query_middel_set_alt + 'n.resource=["Hetionet","%s"], n.hetionet="yes", n.diseaseOntology="yes", n.license="%s", n.url="http://purl.obolibrary.org/obo/DOID_"+split(line.identifier,":")[1] Create (n)-[:equal_to]->(b);\n'
    query_set_alt =query_set_alt % ("already_included_but_mapped_with_alt", do_label, do_name, license)
    cypher_file.write(query_set_alt)
    query_create=query_start+' Match (b:%s{id:line.identifier}) Create (n:Disease{'+query_middel_create+ 'resource:["Hetionet","%s"], hetionet:"yes", diseaseOntology:"yes", license:"%s", source:"%s",  url:"http://purl.obolibrary.org/obo/DOID_"+split(line.identifier,":")[1]}) Create (n)-[:equal_to]->(b);\n'
    query_create=query_create % ("new_nodes",do_label,do_name, license, do_name)
    cypher_file.write(query_create)

    query_rela=query_start+ '''Match (d:Disease {identifier:line.child}), (d2:Disease {identifier:line.parent}) Create (d)-[:IS_A_DiD{license:"%s", source:"%s", unbiased:"false"}]->(d2);\n '''
    query_rela = query_rela %("new_rela", license,do_name)
    cypher_file.write(query_rela)
    cypher_file.close()

    # add query to update disease nodes with do='no'
    cypher_general=open('../cypher_general.cypher','a')
    query='''begin\n Match (d:Disease) Where not exists(d.diseaseOntology) Set d.diseaseOntology ='no';\n commit\n '''
    cypher_general.write(query)
    cypher_general.close()




'''
load the new and old information in the dictionary
test if not the alternativ doid is used in hetionet 
properties:
    definition
    synonyms
    xrefs: external identifier
    umls_cuis
    alt_id
    subset
    id
    name
vorher 137
nacher 8498
DOID:9917 war nur als alternative id da
'''


def load_disease_ontologie_in_hetionet():
    query = '''Match (n:%s) RETURN n''' %(do_label)
    results = g.run(query)
    for disease, in results:
        alternative_ids = disease['alt_id'] if disease['alt_id'] != None else []
        overlap=list(set(alternative_ids) & set(dict_diseases_in_hetionet.keys()))
        has_overlap_between_alternative_and_hetionet_id = True if len(overlap
            ) > 0 else False

        # add the other information to the disease
        xrefs = disease['xrefs'] if disease['xrefs'] != None else ''
        xref_umls_cuis = []
        xref_other = []
        for xref in xrefs:
            if xref.split(':')[0] == 'UMLS_CUI':
                xref_umls_cuis.append(xref)
            else:
                xref_other.append(xref)

        disease=dict(disease)

        # dictionary of integrated
        xref_umls_cuis='|'.join(xref_umls_cuis)
        dict_of_information = {'umls_cuis': xref_umls_cuis}

        for key, value in disease.items():
            if key in dict_DO_prop_to_hetionet_prop:
                key = dict_DO_prop_to_hetionet_prop[key]
            if key in header_nodes:
                if type(value) != list:
                    dict_of_information[key] = value.encode('utf-8')
                else:
                    dict_of_information[key] = '|'.join(value).encode('utf-8')
        dict_of_information['xrefs'] = '|'.join(xref_other)

        # hetionet has this doid not included
        if not disease['id'] in dict_diseases_in_hetionet and not has_overlap_between_alternative_and_hetionet_id:
            csv_writer_new.writerow(dict_of_information)

        # hetionet used the alternative doid
        elif has_overlap_between_alternative_and_hetionet_id:
            id_overlap = list(set(alternative_ids) & set(dict_diseases_in_hetionet.keys()))
            if len(id_overlap) == 1:
                dict_of_information['alternative_id']=overlap[0]
                csv_writer_included_alt.writerow(dict_of_information)
            else:
                print('sad')
        # doid is already in hetionet
        else:
            csv_writer_included.writerow(dict_of_information)

    print('size of disease after the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)))
    output.write(
        'size of disease after the rest of disease ontology was add: ' + str(len(dict_diseases_in_hetionet)) + '\n')

'''
load connection from Disease ontolegy in dictionary and check if the alternative is used in hetionet
'''


def load_in_all_connection_from_disease_ontology():
    counter = 0
    query = ''' Match (n:%s)-[r:is_a]->(p:%s) Return n.id,p.id ''' %(do_label,do_label)
    results = g.run(query)
    for child_id, parent_id, in results:
        #dictionary with relationship infos
        dict_rela_info={'child':child_id,'parent':parent_id}
        csv_writer_rela.writerow(dict_rela_info)
        counter += 1

    print('number of relationships:'+str(counter))



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
    print('generate cypher file')
    output.write('generate cypher file')

    generate_cypher_file()

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

    load_in_all_connection_from_disease_ontology()


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
