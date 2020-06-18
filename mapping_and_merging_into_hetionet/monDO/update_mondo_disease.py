# -*- coding: utf-8 -*-
"""
Created on Mon May 07 13:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import sys
import datetime
from types import *


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append('../drugbank/')
from add_information_from_a_not_existing_node_to_existing_node import merge_information_from_one_node_to_another


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary do to information: name
dict_old_mondo_to_info = {}

# dictionary from new mondo to possible old mondos
dict_new_mondo_to_old_mondos={}
#the mondos which are mapped from new to old need to be known the other way around so i do not check the already mapped one
dict_old_to_new_mondo={}

# dictionary name to mondo
dict_name_to_mondo = {}

# dictionary name and synonym to mondo
dict_name_and_synonym_to_mondo = {}

#dictionary xrefs to Disease in hetionet
dict_xref_to_disease={}

#dictionary old name/label to old mondo id
dict_old_name_to_mondo={}

'''
Load in all disease ontology ids with external identifier and alternative id 
'''


def load_in_all_DO_in_dictionary():
    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for disease, in results:
        mondo_id = disease['identifier']
        # if Do_id == 'DOID:4606':
        #     print('ok')
        dict_old_mondo_to_info[mondo_id] = dict(disease)
        # get name and add to dictionary
        name= disease['name'] if 'name' in disease else ''
        if not name=='':
            dict_old_name_to_mondo[name.lower()]=mondo_id
        # get the label name and add to dictionary
        if 'label' in disease:
            label=disease['label']
        else:
            label=disease['http://www.w3.org/2000/01/rdf-schema#label'] if 'http://www.w3.org/2000/01/rdf-schema#label' in disease else ''


        xrefs= disease['xrefs']
        for xref in xrefs:
            if xref in dict_xref_to_disease:
                dict_xref_to_disease[xref].append(mondo_id)
            else:
                dict_xref_to_disease[xref]=[mondo_id]

    print('Number of old mondo disease:' + str(len(dict_old_mondo_to_info)))



'''
delete all subclass od Disease
'''


def delete_all_subclass_relationships():
    query = '''MATCH p=()-[r:SUBCLASS_OF_DsoD]->() Delete r '''
    g.run(query)


# dictionary monarch DO to information: name
dict_monDO_info = {}

# dictionary_merge_alternativ_ids key is new identifier and value ol id
dict_merge_alternative_ids={}

#list of all old mondos which will be merges
list_merged_modos=[]

'''
Load MonDO disease in dictionary
Where n.`http://www.geneontology.org/formats/oboInOwl#id` ='MONDO:0016682'
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:disease) RETURN n'''
    results = g.run(query)
    counter_mapped = 0
    counter_not_mapped = 0
    for disease, in results:
        monDo_id = disease['http://www.geneontology.org/formats/oboInOwl#id']
        if monDo_id == 'MONDO:0000253':
            print('blub')
        dict_monDO_info[monDo_id] = dict(disease)
        name = disease['label']  if 'label' in disease else ''
        synonyms = disease['synonym'] if 'synonym' in disease else []
        dict_name_to_mondo[name] = monDo_id
        dict_name_and_synonym_to_mondo[name.lower()]=monDo_id
        for synonym in synonyms:
            dict_name_and_synonym_to_mondo[synonym.lower()]=monDo_id
        if 'http://www.geneontology.org/formats/oboInOwl#hasAlternativeId' in disease:
            old_alternative_mondo_ids=[disease['http://www.geneontology.org/formats/oboInOwl#hasAlternativeId']] if type(disease['http://www.geneontology.org/formats/oboInOwl#hasAlternativeId'])!=list else disease['http://www.geneontology.org/formats/oboInOwl#hasAlternativeId']
            for old_alternative_mondo_id in old_alternative_mondo_ids:
                if old_alternative_mondo_id in dict_old_mondo_to_info:
                    dict_merge_alternative_ids[monDo_id]=old_alternative_mondo_id
                    list_merged_modos.append(old_alternative_mondo_id)
        # for synonym in synonyms:
        #     if not synonym == '':
        #         dict_name_to_mondo[synonym] = monDo_id
        if monDo_id in dict_old_mondo_to_info:
            counter_mapped += 1
        else:
            xrefs= disease['http://www.geneontology.org/formats/oboInOwl#hasDbXref'] if 'http://www.geneontology.org/formats/oboInOwl#hasDbXref' in disease else []

            label = disease[
                'http://www.w3.org/2000/01/rdf-schema#label'].lower() if 'http://www.w3.org/2000/01/rdf-schema#label' in disease else ''
            name = name.lower()
            found_a_map=False
            if name in dict_old_name_to_mondo:

                if not dict_old_name_to_mondo[name] in dict_monDO_info:
                    query='''MATCH (n:disease) Where n.`http://www.geneontology.org/formats/oboInOwl#id`='%s' RETURN n''' %(dict_old_name_to_mondo[name])
                    results=g.run(query)
                    result=results.evaluate()
                    if result is None:
                        dict_new_mondo_to_old_mondos[monDo_id] = dict_old_name_to_mondo[name]
                        dict_old_to_new_mondo[dict_old_name_to_mondo[name]]=monDo_id
                        found_a_map=True
                        print('name')
                        print(monDo_id)
                        print(dict_old_name_to_mondo[name])
            if label in dict_old_name_to_mondo and not found_a_map:

                if not dict_old_name_to_mondo[label] in dict_monDO_info:
                    query='''MATCH (n:disease) Where n.`http://www.geneontology.org/formats/oboInOwl#id`='%s' RETURN n''' %(dict_old_name_to_mondo[label])
                    results=g.run(query)
                    result=results.evaluate()
                    if result is None:
                        dict_new_mondo_to_old_mondos[monDo_id] = dict_old_name_to_mondo[label]
                        dict_old_to_new_mondo[dict_old_name_to_mondo[label]]=monDo_id
                        found_a_map=True
                        print('label')
                        print(monDo_id)
                        print(dict_old_name_to_mondo[label])
            if not found_a_map:
                found_mondos=set({})
                for xref in xrefs:
                    if xref in dict_xref_to_disease:
                        found_mondos.union(dict_xref_to_disease[xref])
                        found_a_map=True

                if found_a_map and len(found_mondos)==1:
                    print('xref')
                    print(xref)
                    print(monDo_id)
                    print(found_mondos)
                    dict_new_mondo_to_old_mondos[monDo_id]=list(found_mondos)[0]
                    for found_mondo in found_mondos:
                        dict_old_to_new_mondo[found_mondo]=monDo_id

                else:
                    found_a_map=False


            if not found_a_map:
                counter_not_mapped += 1

    print('number of mapped ones:' + str(counter_mapped))
    print('number of mapped with name(xref):'+str(len(dict_new_mondo_to_old_mondos)))
    print('number of not mapped:' + str(counter_not_mapped))
    print('number of new version mondo disease:' + str(len(dict_monDO_info)))
    print('number of merged nodes with alternative ids:'+str(len(dict_merge_alternative_ids)))
    print('##########################################################################')

    print(datetime.datetime.utcnow())



    dict_not_mapped_old_nodes = {}
    counter_all_with_multiple_soure=0
    counter_all_which_mapped=0
    for old_mondo_id, disease in dict_old_mondo_to_info.items():
        resource= disease['resource']

        if not old_mondo_id in dict_monDO_info and not old_mondo_id in list_merged_modos and not old_mondo_id in dict_old_to_new_mondo and len(resource)>1:
            # print('new mapping try')
            name = disease['name'].lower()
            counter_all_with_multiple_soure+=1
            print('should mapped')
            print(old_mondo_id)
            print(resource)
            if name in dict_name_to_mondo:
                counter_all_which_mapped+=1
                new_mondo=dict_name_to_mondo[name]
                if new_mondo in dict_new_mondo_to_old_mondos:
                    print('in new to old')
                elif new_mondo in old_alternative_mondo_ids:
                    print('in alternative')
                else:
                    dict_new_mondo_to_old_mondos[monDo_id]=old_mondo_id
                print('map with name')
                print(dict_name_to_mondo[name])
                print(old_mondo_id)
                continue
            elif 'CTD' in resource:
                if name in dict_name_and_synonym_to_mondo:
                    counter_all_which_mapped += 1
                    print('map with synonym')
                    print(dict_name_and_synonym_to_mondo[name])
                    print(old_mondo_id)
                    continue

            dict_not_mapped_old_nodes[old_mondo_id] = name

    print('old not mapped ids')
    print('number which should be mapped:'+str(counter_all_with_multiple_soure))
    print('number which are mapped:'+str(counter_all_which_mapped))
    print(len(dict_not_mapped_old_nodes))
    print(dict_not_mapped_old_nodes)

'''
prepare the different entries of the disease dictionary
'''
def prepare_values(monDo,disease_new, other_xrefs_monDO, umls_cuis_monDO):
    monDO_synonyms = disease_new['synonym'] if 'synonym' in disease_new else []
    if type(monDO_synonyms) != list:
        monDO_synonyms = [monDO_synonyms]
    monDo_def = disease_new['definition'] if 'definition' in disease_new else ''

    if dict_old_mondo_to_info[monDo]['diseaseOntology'] == 'yes':
        # combine the old xrefs with the new ones
        old_other_xrefs = dict_old_mondo_to_info[monDo]['xrefs']
        combination_xrefs = list(set(other_xrefs_monDO).union(set(old_other_xrefs)))
        combination_xrefs.remove('') if '' in combination_xrefs else combination_xrefs
        disease_new['http://www.geneontology.org/formats/oboInOwl#hasDbXref'] = combination_xrefs


        # combined the old umls with the new ones
        old_umls_cui = dict_old_mondo_to_info[monDo]['umls_cuis']
        combination_umls = list(set(umls_cuis_monDO).union(set(old_umls_cui)))
        combination_umls.remove('') if '' in combination_umls else combination_umls
        disease_new['umls_cuis'] = list(set(combination_umls))

        monDO_subset = []

        old_synonyms = dict_old_mondo_to_info[monDo]['synonyms'] if 'synonyms' in dict_old_mondo_to_info[
            monDo] else []
        combination_synonyms = list(set(monDO_synonyms).union(set(old_synonyms)))
        combination_synonyms.remove('') if '' in combination_synonyms else combination_synonyms
        disease_new['synonym'] = combination_synonyms

        old_definition = dict_old_mondo_to_info[monDo]['definition'] if 'definition' in dict_old_mondo_to_info[
            monDo] else ''
        if old_definition.find("[FROM DOID]") == -1:
            disease_new['definition'] = monDo_def
        else:
            disease_new['definition'] = old_definition.split('[FROM DOID]')[0] + '[FROM DOID]. ' + monDo_def

        old_subset = dict_old_mondo_to_info[monDo]['subset'] if 'subset' in dict_old_mondo_to_info[monDo] else []
        disease_new['subset'] = old_subset

    else:
        disease_new['http://www.geneontology.org/formats/oboInOwl#hasDbXref'] = other_xrefs_monDO
        disease_new['umls_cuis'] = umls_cuis_monDO
        disease_new['definition'] = monDo_def
        disease_new['synonym'] = monDO_synonyms

    query = ''' Match (n:Disease{identifier:"%s"}), (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})
    Create (n)-[:equal_to_monDO]->(a)
    Set '''
    return query

# set of all properties which start with http
set_http_properties=set([])

'''
integrate mondo into hetionet and change identifier
'''


def integrate_newer_version_mondo():
    counter_new_nodes = 0
    counter_switched_nodes = 0
    counter_merge_nodes = 0

    for monDo, disease_new in dict_monDO_info.items():
        if monDo=='MONDO:0002363':
            print('blub')

        # sort the xrefs in umls and other xrefs
        monDO_xref = disease_new[
            'http://www.geneontology.org/formats/oboInOwl#hasDbXref'] if 'http://www.geneontology.org/formats/oboInOwl#hasDbXref' in disease_new else []

        umls_cuis_monDO = []
        other_xrefs_monDO = []
        if type(monDO_xref) == list:
            for ref in monDO_xref:
                if ref[0:4] == 'UMLS':
                    umls_cuis_monDO.append(ref)
                else:
                    other_xrefs_monDO.append(ref)
        else:
            if monDO_xref[0:4] == 'UMLS':
                umls_cuis_monDO.append(monDO_xref)
            else:
                other_xrefs_monDO.append(monDO_xref)

        # one to one mapping of mondo and do or specific mapped one-to-one from me
        if monDo in dict_old_mondo_to_info:
            # print('one to one')
            counter_switched_nodes += 1

            query=prepare_values(monDo,disease_new, other_xrefs_monDO, umls_cuis_monDO)
            query = query % (monDo, monDo)

            for key, property in disease_new.items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#hasDbXref':
                        key = 'xrefs'
                    elif key == 'synonym':
                        key = 'synonyms'
                    elif key[0:5] == 'http:':
                        set_http_properties.add(key)
                        key = key.split('/')[-1].split('#')
                        if len(key)>1:
                            key=key[1]
                        else:
                            key=key[0]
                    if len(property) > 0 and type(property[0]) == int:
                        add_query = ''' n.%s=%s,''' % (key, property)
                    else:
                        property_string = '|'.join(property)
                        property = property_string.replace('"', "'")
                        add_query = ''' n.%s=["%s"],''' % (key, property.replace('|', '","'))
                    query = query + add_query
                else:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#id':
                        continue
                    elif key == 'label':
                        key = 'name'
                    elif key[0:5] == 'http:':
                        set_http_properties.add(key)
                        key = key.split('/')[-1].split('#')
                        if len(key)>1:
                            key=key[1]
                        else:
                            key=key[0]
                    if type(property) in [int, bool]:
                        add_query = ''' n.%s=%s,''' % (key, property)

                    else:
                        add_query = ''' n.%s="%s",''' % (key, property.replace('"', "'"))
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            string_resources = '","'.join(dict_old_mondo_to_info[monDo]['resource'])
            add_query = ''' n.url="%s" , n.resource=["%s"], n.mondo="yes"; \n ''' % (url, string_resources)
            query = query + add_query

        elif monDo in dict_new_mondo_to_old_mondos:
            # print('one to one')
            counter_switched_nodes += 1
            old_mondo=dict_new_mondo_to_old_mondos[monDo][0] if type(dict_new_mondo_to_old_mondos[monDo])==list else dict_new_mondo_to_old_mondos[monDo]

            query=prepare_values(old_mondo, disease_new, other_xrefs_monDO, umls_cuis_monDO)

            query = query % (old_mondo, monDo)

            for key, property in disease_new.items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#hasDbXref':
                        key = 'xrefs'
                    elif key == 'synonym':
                        key = 'synonyms'
                    elif key[0:5] == 'http:':
                        key = key.split('/')[-1].split('#')
                        if len(key) > 1:
                            key = key[1]
                        else:
                            key = key[0]
                    if len(property) > 0 and type(property[0]) == int:
                        add_query = ''' n.%s=%s,''' % (key, property)
                    else:
                        property_string = '|'.join(property)
                        property = property_string.replace('"', "'")
                        add_query = ''' n.%s=["%s"],''' % (key, property.replace('|', '","'))
                    query = query + add_query
                else:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#id':
                        key='identifier'
                    elif key == 'label':
                        key = 'name'
                    elif key[0:5] == 'http:':
                        set_http_properties.add(key)
                        key = key.split('/')[-1].split('#')
                        if len(key)>1:
                            key=key[1]
                        else:
                            key=key[0]
                    if type(property) in [int, bool]:
                        add_query = ''' n.%s=%s,''' % (key, property)

                    else:
                        add_query = ''' n.%s="%s",''' % (key, property.replace('"', "'"))
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            string_resources = '","'.join(dict_old_mondo_to_info[old_mondo]['resource'])
            add_query = ''' n.url="%s" , n.resource=["%s"], n.mondo="yes"; \n ''' % (url, string_resources)
            query = query + add_query

        # this is when a new node is generated
        else:
            # print('new')
            counter_new_nodes += 1

            disease_new['http://www.geneontology.org/formats/oboInOwl#hasDbXref'] = other_xrefs_monDO
            disease_new['umls_cuis'] = umls_cuis_monDO

            query = ''' Match  (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})
                        Create (n:Disease{identifier:"%s", '''
            query = query % (monDo, monDo)
            for key, property in disease_new.items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#hasDbXref':
                        key = 'xrefs'
                    elif key[0:5] == 'http:':
                        set_http_properties.add(key)
                        key = key.split('/')[-1].split('#')
                        if len(key) > 1:
                            key = key[1]
                        else:
                            key = key[0]
                    elif key == 'synonym':
                        key = 'synonyms'
                    if len(property) > 0 and type(property[0]) == int:
                        add_query = ''' %s:%s,''' % (key, property)
                    else:
                        property_string = '|'.join(property)
                        property_string = property_string.replace('"', "'")
                        add_query = ''' %s:["%s"],''' % (key, property_string.replace('|', '","'))
                    query = query + add_query
                else:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#id':
                        continue
                    elif key == 'synonym':
                        key = 'synonyms'
                    elif key == 'label':
                        key = 'name'
                    elif key[0:5] == 'http:':
                        set_http_properties.add(key)
                        key = key.split('/')[-1].split('#')
                        if len(key) > 1:
                            key = key[1]
                        else:
                            key = key[0]
                    if type(property) in [int, bool]:
                        add_query = ''' %s:%s,''' % (key, property)
                    else:
                        add_query = ''' %s:"%s",''' % (key, property.replace('"', "'"))
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            add_query = '''ctd:"no", ndf_rt:"no", resource:['MonDO'], diseaseOntology:"no", hetionet:"no", mondo:"yes", source:"Monarch Disease Ontology", url:"%s"})
                        Create (n)-[:equal_to_monDO]->(a); \n''' % (url)
            query = query + add_query

        # print(query)
        # sys.exit()
        g.run(query)


'''
delete all Disease nodes which has no relationship to a disease node
in this update the node MONDO:0006020 is merged with node MONDO:0019610, because it seems like 
also, the one that has an alternativ id from the old one are now merged into the new identifier
'''


def delete_not_existing_nodes_and_merge_nodes():
    # first merge if needed
    print('merge')
    print('##################################################################################################')
    if 'MONDO:0019610' not in dict_merge_alternative_ids:
        merge_information_from_one_node_to_another('MONDO:0006020', 'MONDO:0019610', 'Disease')
    else:
        print(merge_information_from_one_node_to_another['MONDO:0019610'])
    for new_id, old_id in dict_merge_alternative_ids.items():
        merge_information_from_one_node_to_another(old_id, new_id, 'Disease')
    print('merge end')

    # delete the http properties in Disease
    query='''Match (d:Disease) Remove '''
    for http_property in set_http_properties:
        query+='d.`'+http_property+'`, '
    query=query[:-2]
    print(query)
    g.run(query)

    print('##################################################################################################')

    # delete all nodes without relationship to mondo disease nodes
    query = '''Match (n:Disease) Where not (n)-[]-(:disease) Detach Delete n'''
    g.run(query)


'''
generate cypher file for subClassOf relationship
'''


def generate_cypher_file_for_relationship():
    # file counter
    file_counter = 1
    # maximal number of queries for a commit block
    constrain_number = 20000
    # maximal number of queries in a file
    creation_max_in_file = 1000000

    h = open('integrate_and_transformed_disease.cypher', 'w')
    h.write('begin \n')
    # count the number of queries
    counter_connection = 0

    query = ''' Match (a)-[r:subClassOf]->(b) Return a.`http://www.geneontology.org/formats/oboInOwl#id`, b.`http://www.geneontology.org/formats/oboInOwl#id`, r'''
    results = g.run(query)
    for child_id, parent_id, rela, in results:
        url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + child_id
        dict_rela = dict(rela)
        query = ''' Match (a:Disease{identifier:"%s"}), (b:Disease{identifier:"%s"})
        Create (a)-[:SUBCLASS_OF_DsoD{license:"CC BY 4.0",unbiased:false, source:"Monarch Disease Ontology", resource:['MonDO'] , mondo:'yes', mondo_source:"%s",'''
        query = query % (child_id, parent_id, url)
        for key, property in dict_rela.items():
            if key[0:4] == 'http':
                key = key.split('#')[1]
            if type(property) == list:
                property = '","'.join(property)
                add_query = '''%s:["%s"],''' % (key, property)
            else:
                add_query = '''%s:"%s",''' % (key, property)
            query += add_query

        query = query[0:-1] + ''' }]->(b);\n'''

        h.write(query)
        counter_connection += 1
        if counter_connection % constrain_number == 0:
            h.write('commit \n')
            if counter_connection % creation_max_in_file == 0:
                h.close()
                h = open('integrate_and_transformed_disease' + str(file_counter) + '.cypher', 'w')
                h.write('begin \n')
                file_counter += 1
            else:
                h.write('begin \n')

    h.write('commit \n')
    h.close()
    print('number of relationships:' + str(counter_connection))


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete all subclass relationships in Disease')

    delete_all_subclass_relationships()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in DO diseases ')

    load_in_all_DO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate the newer node version and add new nodes into Hetionet ')

    integrate_newer_version_mondo()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete not existing nodes and merge if another node with same name')

    delete_not_existing_nodes_and_merge_nodes()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate a cypher file to integrate the relationships ')

    generate_cypher_file_for_relationship()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
