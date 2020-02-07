# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 12:14:16 2017

@author: Cassandra
"""

from py2neo import Graph
import datetime
import sys, csv
import urllib.request, urllib.error, urllib.parse
import json
from api_key import *

import xml.dom.minidom as dom


REST_URL = "http://data.bioontology.org"

#http://bioportal.bioontology.org/ontologies/MEDDRA?p=classes&conceptid=10059299



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
Create cache file or open and load mapping results
'''

def cache_api():
    # header of cache file
    header=['meddra_id','umls_cuis']
    global csv_writer
    try:
        cache_file=open('cache_api_results.tsv','r', encoding='utf-8')
        csv_reader=csv.DictReader(cache_file,delimiter='\t')
        for row in csv_reader:
            dict_aeolus_SE_with_CUIs[row['meddra_id']]=list(set(row['umls_cuis'].split('|')))
        cache_file.close()
        cache_file = open('cache_api_results.tsv', 'a', encoding='utf-8')
        csv_writer = csv.writer(cache_file, delimiter='\t')

    except:
        cache_file=open('cache_api_results.tsv','w',encoding='utf-8')
        csv_writer=csv.writer(cache_file,delimiter='\t')
        csv_writer.writerow(header)




'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j():
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))


'''
get from api results from url
'''
def get_json(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())


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

#dictionary disease name to identifier
dict_disease_name_to_id={}

#dictionary disease umls cui to identifier
dict_disease_cui_to_id={}

# dictionary meddra to mondo
dict_meddra_to_mondo={}

#ditionary mondo to xrefs and resource
dict_mondo_to_xrefs_and_resource={}


'''
Load all disease with umls, identifier and name (,synonyms?)
'''
def load_disease_infos():
    query='''Match (n:Disease) Return n.identifier, n.name, n.umls_cuis, n.xrefs, n.resource'''
    results=g.run(query)

    for identifier, name, umls_cuis, xrefs, resource, in results:
        dict_mondo_to_xrefs_and_resource[identifier]=[xrefs,resource]
        if name:
            name=name.lower()
            if name in dict_disease_name_to_id:
                print('name is double')
                dict_disease_name_to_id[name].append(identifier)
                print(dict_disease_name_to_id[name])

            else:
                dict_disease_name_to_id[name]=[identifier]
        if umls_cuis:
            for umls_cui in umls_cuis:
                cui=umls_cui.split(':')[1]
                if cui in dict_disease_cui_to_id:
                    dict_disease_cui_to_id[cui].append(identifier)
                else:
                    dict_disease_cui_to_id[cui]=[identifier]
        if xrefs:
            for xref in xrefs:
                if xref.startswith('MedDRA'):
                    meddra_id=xref.split(':')[1]
                    if meddra_id in dict_meddra_to_mondo:
                        dict_meddra_to_mondo[meddra_id].add(identifier)
                    else:
                        dict_meddra_to_mondo[meddra_id]=set([identifier])




# dictionary with all aeolus side effects outcome_concept_id (OHDSI ID) as key and value is the class SideEffect_Aeolus
dict_side_effects_aeolus = {}

# list of list with all meddra cuis in groups of 100
list_of_list_of_meddra_ids=[]

# number of group size
number_of_group_size=200

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
    # list of_meddra ids
    list_of_ids=[]
    #counter
    counter=0
    for result, in results:
        sideEffect = SideEffect_Aeolus(result['snomed_outcome_concept_id'], result['vocabulary_id'], result['name'],
                                       result['outcome_concept_id'], result['concept_code'])
        dict_side_effects_aeolus[result['concept_code']] = sideEffect
        #add all meddra ids where no cui is nown in list of a given size
        # the list should be not to big because it will be asked with api
        if result['concept_code'] not in dict_aeolus_SE_with_CUIs:
            list_of_ids.append(result['concept_code'])
            counter+=1
            if counter % number_of_group_size==0:
                list_of_list_of_meddra_ids.append(list_of_ids)
                list_of_ids=[]

    list_of_list_of_meddra_ids.append(list_of_ids)

    print('Size of Aoelus side effects:' + str(len(dict_side_effects_aeolus)))


# dictionary with for every key outcome_concept a list of umls cuis as value
dict_aeolus_SE_with_CUIs = {}

# generate file with meddra and a list of umls cuis and where there are from
multiple_cuis = open('aeolus_multiple_cuis.tsv', 'w')
csv_multiple_cuis=csv.writer(multiple_cuis,delimiter='\t')
csv_multiple_cuis.writerow(['MedDRA id','cuis with | as seperator ','where are it from'])

#list of concept codes which do not have a cui
list_aeolus_outcome_without_cui=[]

'''
search for cui with api from bioportal
'''
def search_with_api_bioportal():
    global csv_writer
    #counter for not equal names
    counter_for_not_equal_names=0

    #counter for meddra ids which has no cui
    counter_meddra_id_without_cui=0

    #search for cui id in bioportal
    for list_ids in list_of_list_of_meddra_ids:
        string_ids=' '.join(list_ids)
        part="/search?q="+urllib.parse.quote(string_ids)+"&include=cui,prefLabel&pagesize=250&ontology=MEDDRA"
        url=REST_URL+part
        results_all=get_json(url)
        if results_all['totalCount']>250:
            sys.exit('more results thant it can show')
        results=results_all['collection']

        dict_all_inside={}
        #check if this api got an result
        if results:
            for result in results:
                # print(results)
                all_infos=result['@id'].split('/')
                meddra_id=all_infos[-1]
                if meddra_id=='10052551':
                    print('test')
                # filter out all results which are not from meddra
                if all_infos[-2]!='MEDDRA':
                    continue

                # check if the result has a cui
                if 'cui' in result:
                    cuis=result['cui']
                else:
                    print('no cui')
                    print(meddra_id)          
                    continue
                pref_name=result['prefLabel']

                # check if the the id is really in this list
                if not meddra_id in list_ids:
                    print('ohje')
                    print(meddra_id)
                    print(url)
                    print(list_ids)
                    print(result)
                    print('What did happend')
                    continue

                # if it contains more than one cui write it into an extra file
                if len(list(set(cuis))) > 1:
                    cuis_string = "|".join(list(set(cuis)))
                    csv_multiple_cuis.writerow([meddra_id , cuis_string ,'from bioportal'])
                dict_all_inside[meddra_id]=cuis
                sideEffect_name=dict_side_effects_aeolus[meddra_id].name
                dict_aeolus_SE_with_CUIs[meddra_id] = list(set(cuis))
                csv_writer.writerow([meddra_id,'|'.join(cuis)])
                #check if names are equal
                if pref_name!=sideEffect_name:
                    counter_for_not_equal_names+=1

            # check if some do not have a cui and if so add the to the list without cui
            if len(list_ids)!= len(dict_all_inside):
                set_list=set(list_ids)
                set_keys=set(dict_all_inside.keys())
                not_mapped_list=list(set_list.difference(set_keys))
                counter_meddra_id_without_cui+=len(not_mapped_list)
                list_aeolus_outcome_without_cui.extend(not_mapped_list)
        else:
            print('not in bioportal')
            print(list_ids)
            list_aeolus_outcome_without_cui.extend(list_ids)

    print('Size of Aoelus side effects:' + str(len(dict_side_effects_aeolus)))
    print('number of not equal names:'+str(counter_for_not_equal_names))
    print('number of not mapped meddra ids:'+str(counter_meddra_id_without_cui))




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
    print('lenth of list which has a cui but are not mapped to hetionet:' + str(len(list_not_mapped_to_hetionet)))
    print('the number of nodes to which they are mapped:' + str(len(dict_mapped_cuis_hetionet)))

#dictionary mapped aeolus outcomet to disease ids
dict_outcome_to_disease={}

# new nodes  dictionary from umls cui to aeolus outcome
dict_new_node_cui_to_concept={}

'''
get the mapped thins and add them to the dictionary and also write all mappings into the csv file
'''
def generate_csv_file(list_of_delet_index, list_not_mapped, concept_code, diseases, mapping_method, csv_writer):
    list_of_delet_index.append(list_not_mapped.index(concept_code))
    dict_outcome_to_disease[concept_code] = list(diseases)
    for disease_id in diseases:

        resource_disease=dict_mondo_to_xrefs_and_resource[disease_id][1] if dict_mondo_to_xrefs_and_resource[disease_id][1] is not None else []
        resource_disease.append("AEOLUS")
        resource_disease=list(set(resource_disease))
        resource_string='|'.join(resource_disease)

        xref_disease = dict_mondo_to_xrefs_and_resource[disease_id][0] if \
        dict_mondo_to_xrefs_and_resource[disease_id][0] is not None else []
        xref_disease.append("MedDRA:" + concept_code)
        xref_disease = list(set(xref_disease))
        xref_string  = '|'.join(xref_disease)

        csv_writer.writerow([concept_code, disease_id, mapping_method, resource_string, xref_string])

'''
Try to map the not mapped to disease
'''
def mapping_to_disease():
    # open file for mapping with disease
    file=open('output/se_disease_mapping.tsv','w')
    csv_writer=csv.writer(file, delimiter='\t')
    csv_writer.writerow(['aSE','disease_id','mapping_method','resource','xrefs'])

    # open file for not mapping with anything
    file_not_mapped=open('output/se_not_mapping.tsv','w')
    csv_writer_not_mapped=csv.writer(file_not_mapped, delimiter='\t')
    csv_writer_not_mapped.writerow(['aSE','name'])

    #list of delete indeces
    list_of_delete_index_with_cui=[]
    list_of_delete_index_without_cui = []

    counter_of_mapping_tries=0
    counter_of_not_mapped=0
    #fist outcome with cui but did not mapped
    for concept_code in list_not_mapped_to_hetionet:
        counter_of_mapping_tries+=1
        if concept_code in dict_meddra_to_mondo:
            generate_csv_file(list_of_delete_index_with_cui, list_not_mapped_to_hetionet, concept_code, dict_meddra_to_mondo[concept_code], 'meddra mapping',
                              csv_writer)

        else:
            if concept_code=='10062075':
                print('test')
            cuis= dict_aeolus_SE_with_CUIs[concept_code]
            name=dict_side_effects_aeolus[concept_code].name.lower()
            mapped_cuis_disease=set()
            for cui in cuis:
                if cui in dict_disease_cui_to_id:
                    mapped_cuis_disease=mapped_cuis_disease.union(dict_disease_cui_to_id[cui])

            mapped_name_disease=set()
            if name in dict_disease_name_to_id:
                mapped_name_disease=set(dict_disease_name_to_id[name])

            find_intersection=mapped_name_disease.intersection(mapped_cuis_disease)
            if len(find_intersection)>0:
                generate_csv_file(list_of_delete_index_with_cui, list_not_mapped_to_hetionet, concept_code, find_intersection, 'intersection name and cui mapping',
                                  csv_writer)
                if len(find_intersection)>1:
                    print('intersection is greater than one')
            elif len(mapped_cuis_disease)>0 and len(mapped_name_disease)==0:
                generate_csv_file(list_of_delete_index_with_cui, list_not_mapped_to_hetionet, concept_code, mapped_cuis_disease, 'cui mapping',
                                  csv_writer)
            elif len(mapped_cuis_disease) == 0 and len(mapped_name_disease) >0:
                generate_csv_file(list_of_delete_index_with_cui, list_not_mapped_to_hetionet, concept_code, mapped_name_disease, 'name mapping',
                                  csv_writer)

            elif len(mapped_cuis_disease) > 0 and len(mapped_name_disease) >0:
                # take the name mapping because this is better
                generate_csv_file(list_of_delete_index_with_cui, list_not_mapped_to_hetionet, concept_code, mapped_name_disease, 'name mapping, but both did mapped',
                                  csv_writer)
                print(concept_code)
                print(mapped_cuis_disease)
                print(mapped_name_disease)
                print('mapped with name and cui but no intersection')
            else:
                # print('no mapping to disease possible')
                counter_of_not_mapped+=1
                for cui in cuis:
                    if cui in dict_new_node_cui_to_concept:
                        dict_new_node_cui_to_concept[cui].append(concept_code)
                    else:
                        dict_new_node_cui_to_concept[cui]=[concept_code]

    list_of_delete_index_with_cui=sorted(list_of_delete_index_with_cui, reverse= True)
    for index in list_of_delete_index_with_cui:
        list_not_mapped_to_hetionet.pop(index)


    print('number of mapping tries:'+str(counter_of_mapping_tries))
    print('number of not mapped:' + str(counter_of_not_mapped))


    # try mapping of the outcomes without umls cui with name mapping
    for concept_code in list_aeolus_outcome_without_cui:
        counter_of_mapping_tries+=1
        name=dict_side_effects_aeolus[concept_code].name.lower()
        if concept_code in dict_meddra_to_mondo:
            generate_csv_file(list_of_delete_index_without_cui, list_aeolus_outcome_without_cui, concept_code, dict_meddra_to_mondo[concept_code], 'meddra mapping',
                                  csv_writer)

        if name in dict_disease_name_to_id:
            generate_csv_file(list_of_delete_index_without_cui, list_aeolus_outcome_without_cui, concept_code, mapped_name_disease, 'meddra mapping',
                                  csv_writer)

            if len(mapped_name_disease)>1:
                print('multiple mapping with name')
                print(concept_code)
                print(mapped_name_disease)
        else:
            # print('no mapping is possible')
            counter_of_not_mapped+=1
            csv_writer_not_mapped.writerow([concept_code, dict_side_effects_aeolus[concept_code].name])


    print('number of mapping tries:'+str(counter_of_mapping_tries))
    print('number of not mapped:' + str(counter_of_not_mapped))

'''
integrate aeolus in hetiont, by map generate a edge from hetionet to the mapped aeolus node
if no hetionet node is found, then generate a new node for side effects
'''


def integrate_aeolus_into_hetionet():
    #file for already existing se
    file_existing=open('output/se_existing.tsv','w',encoding='utf-8')
    csv_existing=csv.writer(file_existing,delimiter='\t')
    csv_existing.writerow(['aSE','SE','cuis', 'resources'])

    #query for mapping
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/aeolus/output/%s.tsv" As line FIELDTERMINATOR '\\t' Match (a:AeolusOutcome{concept_code:line.aSE})'''
    cypher_file= open('cypher_se.cypher','w')

    # query for the update nodes and relationship
    query_update= query_start+' , (n:SideEffect{identifier:line.SE}) Set a.cuis=split(line.cuis,"|"), n.resource=split(line.resources,"|") , n.aeolus="yes", n.xrefs=n.xrefs+("MedDRA:"+line.aSE) Create (n)-[:equal_to_Aeolus_SE{mapping_method:line.mapping_method}]->(a); \n'
    query_update= query_update %("se_existing")
    cypher_file.write(query_update)

    # query for mapping disease
    query_update = query_start + ''' , (n:Disease{identifier:line.disease_id}) Set  n.resource=split(line.resource,"|") , n.aeolus="yes", n.xrefs=split(line.xrefs,"|") Create (n)-[:equal_to_Aeolus_SE{mapping_method:line.mapping_method}]->(a); \n'''
    query_update = query_update % ("se_disease_mapping")
    cypher_file.write(query_update)

    # update and generate connection between mapped aeolus outcome and hetionet side effect
    for outcome_concept in list_map_to_hetionet:
        cuis=dict_side_effects_aeolus[outcome_concept].cuis
        cuis_string='|'.join(cuis)
        for cui in cuis:
            resource=dict_all_side_effect[cui].resource
            resource.append("AEOLUS")
            resource=list(set(resource))
            resources='|'.join(resource)

            csv_existing.writerow([outcome_concept,cui, cuis_string, resources])

    # close file
    file_existing.close()

    # open new file for new se
    file_new=open('output/se_new.tsv','w',encoding='utf-8')
    csv_new=csv.writer(file_new,delimiter='\t')
    csv_new.writerow(['aSE','SE','cuis'])

    # query for the update nodes and relationship
    query_new = query_start + ' Create (n:SideEffect{identifier:line.SE, licenses:"CC0 1.0", name:a.name , source:"UMLS via AEOLUS", url:"http://identifiers.org/umls/"+line.SE , resource:["AEOLUS"],  aeolus:"yes", xrefs:[line.aSE] }) Set a.cuis=split(line.cuis,"|") Create (n)-[:equal_to_Aeolus_SE]->(a); \n'
    query_new = query_new % ("se_new")
    cypher_file.write(query_new)

    # generate new hetionet side effects and connect the with the aeolus outcome
    for cui, outcome_concepts in dict_new_node_cui_to_concept.items():
        if len(outcome_concepts)==1:
            csv_new.writerow([outcome_concepts[0],cui, '|'.join(dict_aeolus_SE_with_CUIs[outcome_concepts[0]])])
        else:
            print(cui)
            print(outcome_concepts)
            print('multi concept for one cui')

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

    create_connection_with_neo4j()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load already mapped from api cache')

    cache_api()

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
    print('Load in all disease from hetionet in a dictionary')

    load_disease_infos()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find cuis for aeolus side effects')

    search_with_api_bioportal()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map round one')

    map_first_round()
    search_with_api_bioportal()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map round two to disease')

    mapping_to_disease()

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
