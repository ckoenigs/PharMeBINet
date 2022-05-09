# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:52:43 2017

@author: ckoenig
"""

'''integrate the other diseases and relationships from disease ontology in pharmebinet'''
import datetime
import sys, csv

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases

# file to put all information in it
output = open('output_fusion.txt', 'w', encoding='utf-8')

# disease ontology license
license = 'CC0 1.0 Universal'

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of all diseases in pharmebinet with key the disease ontology and value class Disease
dict_diseases_in_pharmebinet = {}

# list doids of all disease in pharmebinet
list_diseases_in_pharmebinet = []

# dict_doid_to_mondo_ids
dict_doid_to_mondo_ids = {}

# dict_omim_to_mondo_ids
dict_omim_to_mondo_ids = {}


# dict_name_to_mondo_ids
dict_name_to_mondo_ids = {}

def add_entry_to_dictionary(key, value, dictionary):
    """
    Add information into dictionary with ste as values
    :param key: string
    :param value: string
    :param dictionary: dictionary
    :return:
    """
    if key not in dictionary:
        dictionary[key]=set()
    dictionary[key].add(value)

'''
load all disease in the dictionary
has properties:
name 
identifier
source
license
url
'''


def load_all_disease_in_dictionary():
    query = '''Match (n:Disease) RETURN n '''
    results = g.run(query)
    for disease, in results:
        identifier = disease['identifier']
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        for xref in xrefs:
            if xref.startswith('DOID:'):
                add_entry_to_dictionary(xref,identifier, dict_doid_to_mondo_ids)
        name= disease['name'].lower()
        add_entry_to_dictionary(name, identifier, dict_name_to_mondo_ids)

        synonyms= disease['synonyms'] if 'synonyms' in disease else []
        for synonym in synonyms:
            if synonym[-1]==']':
                synonym=synonym.rsplit('[',1)[0]
            synonym=synonym.lower()
            add_entry_to_dictionary(synonym, identifier, dict_name_to_mondo_ids)

        list_diseases_in_pharmebinet.append(identifier)
        disease = dict(disease)
        # dict_diseases_in_pharmebinet['huh']=disease
        dict_diseases_in_pharmebinet[identifier] = disease
    print('size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_pharmebinet)))
    output.write(
        'size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_pharmebinet)) + '\n')

    # try consider only the lowest level omim so it should not have a with to general omim mapping od do
    query = '''Match (n:Disease) Where not ()-[:IS_A_DiaD]->(n) Return n'''
    results = g.run(query)
    for disease, in results:
        identifier = disease['identifier']
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        for xref in xrefs:
            if xref.startswith('OMIM:'):
                add_entry_to_dictionary(xref, identifier, dict_omim_to_mondo_ids)


# in pharmebinet is a alternative doid used: dictionary with alternative id as key and original id in disease ontology
#   as value
dict_alternative_id = {}

# dictionary from disease ontology properties name to pharmebinet properties names
dict_DO_prop_to_pharmebinet_prop = {'id': 'identifier',
                                 "synonym": "synonyms",
                                 "def": "definition",
                                 "alt_id": "alternative_ids",
                                 }

dict_pharmebinet_prop_to_DO_prop = {y: x for x, y in dict_DO_prop_to_pharmebinet_prop.items()}

# diesease ontology_name_resource
do_name = "Disease Ontology"

# disease ontology label
do_label = 'diseaseontology'

# generate tsv files for integration
header_nodes = ['identifier', 'mondo_id', 'definition', "synonyms", "umls_cuis",  "alternative_ids", 'resource', 'how_mapped']
# tsv file for DOID which are already in pharmebinet
file_included = open('output/mapped.tsv', 'w', encoding='utf-8')
csv_writer_included = csv.DictWriter(file_included, delimiter='\t', fieldnames=header_nodes)
csv_writer_included.writeheader()


# tsv for relationship
# header of rela
header_rela = ['child', 'parent','doid']
file_rela = open('output/new_rela.tsv', 'w', encoding='utf-8')
csv_writer_rela = csv.DictWriter(file_rela, delimiter='\t', fieldnames=header_rela)
csv_writer_rela.writeheader()

'''
Create cypher file to update and create new Disease nodes from tsv.
Also create cypher query for generate is a relationships between Diseases
'''


def generate_cypher_file():
    cypher_file = open('cypher.cypher', 'w', encoding='utf-8')
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/do/output/%s.tsv" As line FIELDTERMINATOR '\\t' '''

    query_middel_set = ''
    query_middel_set_alt = ''
    for header in header_nodes:
        if header in ['how_mapped','mondo_id', 'identifier']:
            continue
        if header in ['synonyms', 'alternative_ids', 'umls_cuis', 'resource']:
            query_middel_set += 'n.' + header + '=split(line.' + header + ',"|"), '
            continue
        query_middel_set += 'n.' + header + '=line.' + header + ', '

    query_set = query_start + ' Match (n:Disease{identifier:line.mondo_id}), (b:%s{id:line.identifier}) Set ' + query_middel_set + ' n.diseaseOntology="yes" Create (n)-[:equal_to {how_mapped:line.how_mapped}]->(b);\n'
    print(query_set)
    query_set = query_set % ("mapped", do_label)
    cypher_file.write(query_set)

    query_rela = query_start + '''Match (d:Disease {identifier:line.child}), (d2:Disease {identifier:line.parent}) Merge (d)-[r:IS_A_DiaD]->(d2) On Create Set r.license="%s", r.source="%s", r.unbiased=false, r.resource=["Disease Ontology"] ,r.diseaseOntology='yes', r.url="http://purl.obolibrary.org/obo/DOID_"+line.doid  On Match Set r.resource="Disease Ontology"+ r.resource ,r.diseaseOntology='yes' ;\n '''
    query_rela = query_rela % ("new_rela", license, do_name)
    cypher_file.write(query_rela)
    cypher_file.close()


# dictionary from disease ontology node id to mondos set
dict_mapping_do_to_mondo={}

# dictionary mondo id to update information
dict_mondo_id_update_info={}

def gather_mappings(mondo, dict_info):
    """
    Gather all mapped doid
    :param mondo: string
    :param dict_info: dictionary
    :return:
    """
    if not mondo in dict_mondo_id_update_info:
        dict_mondo_id_update_info[mondo]=[]
    dict_mondo_id_update_info[mondo].append(dict_info)
    


def prepare_mapped_data(disease, identifier, alternative_ids, how_mapped, overlap, dict_some_identifier_to_mondo_ids):
    """
    prepare do information for mapped part and the combine information with mondo disease.
    :param disease: dict
    :param identifier: string
    :param alternative_ids: list
    :param how_mapped: string
    :param overlap: set
    :param dict_some_identifier_to_mondo_ids: dictionary
    :return:
    """
    # add the other information to the disease
    xrefs = disease['xrefs'] if disease['xrefs'] != None else ''
    xref_umls_cuis = []
    xref_other = []
    omim_ids = set()
    for xref in xrefs:
        if xref.split(':')[0] == 'UMLS_CUI':
            xref_umls_cuis.append(xref)
        elif xref.startswith('OMIM:'):
            omim_ids.add(xref)
        xref_other.append(xref)

    disease = dict(disease)

    # dictionary of integrated
    dict_of_information = {'umls_cuis': xref_umls_cuis, 'identifier': identifier, 'how_mapped': how_mapped}

    for property in header_nodes:
        if property in dict_pharmebinet_prop_to_DO_prop:
            key = dict_pharmebinet_prop_to_DO_prop[property]
        else:
            key = property
        if key in disease:
            dict_of_information[property] = disease[key]
    dict_of_information['alternative_ids'] = alternative_ids

    dict_mapping_do_to_mondo[identifier] = set()
    for other_identifier in overlap:
        dict_mapping_do_to_mondo[identifier].union(dict_some_identifier_to_mondo_ids[other_identifier])
        for mondo in dict_some_identifier_to_mondo_ids[other_identifier]:
            gather_mappings(mondo, dict_of_information)

# dictionary manual mapping from DOID to OMIM
dict_doid_to_omim_id={'DOID:0080869':'OMIM:616947',
                      'DOID:0080735':'OMIM:614557'}

'''
load the do information in the dictionary
test if not the alternativ doid is used in mondo , but do not use the old entries (is_obsolete=true)
properties:
    definition
    synonyms
    xrefs: external identifier
    umls_cuis
    alt_id
    subset
    id
    name
DOID:9917 war nur als alternative id da
'''


def load_disease_ontologie_in_pharmebinet():
    query = '''Match (n:%s) Where not exists(n.is_obsolete) and not ()-[:is_a]->(n) RETURN n.id''' % (do_label)
    results = g.run(query)
    set_doid_which_are_leaves=set()
    for identifier, in results:
        set_doid_which_are_leaves.add(identifier)

    query = '''Match (n:%s) Where not exists(n.is_obsolete) RETURN n''' % (do_label)
    results = g.run(query)
    set_of_all_doids = set(dict_doid_to_mondo_ids.keys())

    counter_mapped = 0
    counter_all = 0
    for disease, in results:
        identifier=disease['id']
        counter_all += 1
        if disease['id'] == 'DOID:10210':
            print('blub')
        alternative_ids = disease['alt_ids'] if 'alt_ids' in disease else []
        alternative_ids.append(identifier)
        overlap = list(set(alternative_ids).intersection( set_of_all_doids))
        has_overlap_between_do_and_mondo = True if len(overlap) > 0 else False

        mapped_already=False

        if  has_overlap_between_do_and_mondo:

            prepare_mapped_data(disease, identifier, alternative_ids,'doid',overlap,dict_doid_to_mondo_ids)
            mapped_already=True

        if mapped_already:
            counter_mapped+=1
            continue

        name= disease['name'].lower()

        if name in dict_name_to_mondo_ids:
            prepare_mapped_data(disease, identifier, alternative_ids, 'name', [name], dict_name_to_mondo_ids)
            mapped_already = True

        if mapped_already:
            counter_mapped+=1
            continue

        synonyms= disease['synonyms'] if 'synonyms' in disease else []

        mapped_synonyms=set()
        for synonym in synonyms:
            synonym=synonym.lower()
            if synonym in dict_name_to_mondo_ids:
                mapped_synonyms.add(synonym)
                mapped_already = True

        if mapped_already:
            counter_mapped+=1
            prepare_mapped_data(disease, identifier, alternative_ids, 'synonyms', mapped_synonyms, dict_name_to_mondo_ids)
            continue

        xrefs= disease['xrefs'] if 'xrefs' in disease else []
        omim_set=set()
        for xref in xrefs:
            if xref.startswith('OMIM:'):
                omim_set.add(xref)
        if len(omim_set)==1 and identifier in set_doid_which_are_leaves:
            # manual mapped doid to mondo
            if identifier in dict_doid_to_omim_id:
                omim_set=set([dict_doid_to_omim_id[identifier]])
            overlap= omim_set.intersection(dict_omim_to_mondo_ids.keys())
            if len(overlap)>0:
                prepare_mapped_data(disease, identifier, alternative_ids,'omim',overlap,dict_omim_to_mondo_ids)

    print('Number of mapped DO: ' + str(counter_mapped))
    output.write(
        'Number of mapped DO: ' + str(counter_mapped) + '\n')

    print('Number of all DO: ' + str(counter_all))
    output.write(
        'Number of all DO: ' + str(counter_all) + '\n')


def combine_information(list_of_info_dict, mondo):
    """
    combine the mapping information
    :param list_of_info_dict: list of dictionaries
    :param mondo: string
    :return: dict_of_information
    """
    dict_of_information={}
    mondo_disease = dict_diseases_in_pharmebinet[mondo]
    counter=0
    for dict_info in list_of_info_dict:
        for key, value in dict_info.items():
            if counter==0:
                if key == 'identifier':
                    dict_of_information[key] = set([value])
                    continue
                if key in mondo_disease :
                    if type(value) == str:
                        if key == 'definition':
                            # print(value, mondo_disease[key])
                            if value != mondo_disease[key]:
                                dict_of_information[key] = mondo_disease[key] + ' [MONDO] ' + value + ' [DO]'
                        else:
                            print(key, 'string', mondo)
                    else:
                        info_mondo = set(mondo_disease[key])
                        info_mondo = info_mondo.union(value)
                        dict_of_information[key] = info_mondo
                else:

                    # print(value, mondo_disease.keys())
                    # print(key, 'prop not in mondo')
                    if type(value) == str:
                        dict_of_information[key] = value
                    else:
                        dict_of_information[key] = set(value)
            else:
                if key == 'identifier':
                    dict_of_information[key].add(value)
                    continue
                if key in dict_of_information:
                    if type(value) == str:
                        if value != dict_of_information[key] and not value in dict_of_information[key]:
                            dict_of_information[key] = dict_of_information[key] + ' ' + value + ' [DO]'
                    else:
                        dict_of_information[key] = dict_of_information[key].union(value)
                else:
                    if key in mondo_disease :
                        if type(value) == str:
                            if key == 'definition':
                                # print(value, mondo_disease[key])
                                if value != mondo_disease[key] and not value in mondo_disease[key]:
                                    dict_of_information[key] = mondo_disease[key] + ' [MONDO] ' + value + ' [DO]'
                        else:
                            info_mondo = set(mondo_disease[key])
                            info_mondo = info_mondo.union(value)
                            dict_of_information[key] = info_mondo
                    else:
                        print(value, mondo_disease)
                        print(key, 'prop not in mondo multy comination')
                        if type(value) == str:
                            if value == 'definition':
                                dict_of_information[key] = value + ' [DO]'
                            else:
                                dict_of_information[key] = value
                        else:
                            dict_of_information[key] = set(value)
        counter+=1
    return dict_of_information


def prepare_data_for_tsv():
    counter_multiple_edges=0
    # prepare the information which are written into tsv file
    for mondo_id, list_of_dict_of_information in dict_mondo_id_update_info.items():

        disease_mondo = dict_diseases_in_pharmebinet[mondo_id]

        if len(list_of_dict_of_information)==1:
            dict_of_information= combine_information(list_of_dict_of_information, mondo_id)

        else:
            filter_list_of_dict_info=[]
            counter_multiple_edges+=1
            how_mapped_set=set()
            for dict_info in list_of_dict_of_information:
                how_mapped_set.add(dict_info['how_mapped'])
                if dict_info['how_mapped']=='doid':
                    filter_list_of_dict_info.append(dict_info)
            if len(filter_list_of_dict_info)==len(list_of_dict_of_information):
                print('same number')
            if len(filter_list_of_dict_info) ==0:
                print('all mappings removed')
                print(list_of_dict_of_information)
                filter_list_of_dict_info=list_of_dict_of_information
                if list_of_dict_of_information[0]['how_mapped']=='omim' and len(how_mapped_set)==1:
                    print(mondo_id)
                    print([x['identifier'] for x in filter_list_of_dict_info])
                    sys.exit('multiple mapping only omim was a problem so far')
            dict_of_information= combine_information(filter_list_of_dict_info, mondo_id)

        dict_of_information['mondo_id'] = mondo_id

        resource = set(disease_mondo['resource'])
        resource.add(do_name)
        resource = list(resource)
        resource.sort()
        dict_of_information['resource'] = resource

        for key in header_nodes:
            # need in case in DO are no information the mondo information else this information will be empty
            if key not in dict_of_information and key in disease_mondo:
                dict_of_information[key]=disease_mondo[key]

            # prepare list/set information
            if key in dict_of_information and type(dict_of_information[key])!=str and key!='identifier':
                # print(dict_of_information[key], key)
                dict_of_information[key]='|'.join(dict_of_information[key])
        for doid in dict_of_information['identifier']:
            copy_dict=dict_of_information.copy()
            copy_dict['identifier']=doid
            csv_writer_included.writerow(copy_dict)

    print('number of multiple mappings:',counter_multiple_edges)



'''
load connection from Disease ontolegy in dictionary and check if the alternative is used in pharmebinet
'''


def load_in_all_connection_from_disease_ontology():
    counter = 0

    set_of_child_parent_pairs=set()

    query = ''' Match (n:%s)-[r:is_a]->(p:%s) Return n.id,p.id ''' % (do_label, do_label)
    results = g.run(query)
    for child_id, parent_id, in results:
        if child_id in dict_doid_to_mondo_ids and parent_id in dict_doid_to_mondo_ids:
            for mondo_child in dict_doid_to_mondo_ids[child_id]:
                for mondo_parent in dict_doid_to_mondo_ids[parent_id]:
                    if (mondo_child,mondo_parent) in set_of_child_parent_pairs:
                        continue
                    # dictionary with relationship infos
                    dict_rela_info = {'child': mondo_child, 'parent': mondo_parent, 'doid':child_id}
                    csv_writer_rela.writerow(dict_rela_info)
                    counter += 1
                    set_of_child_parent_pairs.add((mondo_child,mondo_parent))

    print('number of relationships:' + str(counter))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))
    print('create connection with neo4j')
    output.write('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))
    print('generate cypher file')
    output.write('generate cypher file')

    generate_cypher_file()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))
    print('load all pharmebinet diseases in dictionary')
    output.write('load all pharmebinet diseases in dictionary')

    load_all_disease_in_dictionary()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))

    print('load all disease ontology diseases in dictionary')
    output.write('load all disease ontology diseases in dictionary')

    load_disease_ontologie_in_pharmebinet()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))

    print('prepare data for tsv file')
    output.write('prepare data for tsv file')

    prepare_data_for_tsv()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))

    print('load all connection in dictionary')
    output.write('load all connection in dictionary')

    load_in_all_connection_from_disease_ontology()

    print(
        '#################################################################################################################################################################')
    output.write(
        '#################################################################################################################################################################')
    print(len(dict_diseases_in_pharmebinet))

    print(datetime.datetime.now())
    output.write(str(datetime.datetime.now()))
    output.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
