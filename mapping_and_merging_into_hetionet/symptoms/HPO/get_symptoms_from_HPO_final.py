# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:14:27 2017

@author: cassandra
"""

from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
from itertools import groupby

reload(sys)
# set default encoding on utf-8
sys.setdefaultencoding('utf-8')


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with the names as key and value is the doid
dict_name_to_doid = {}

# dictionary with umls cui as key and doid list as value
dict_umls_cui_to_doid = {}

# dictionary with omim id as key and doid list as value
dict_omim_to_doid = {}

'''
load all disease from hetionet and remember all name, synonym, umls cui and omim id
'''


def get_all_disease_information_from_hetionet():
    query = ''' Match (d:Disease) Return d.identifier, d.name, d.synonyms, d.xrefs, d.umls_cuis'''
    results = g.run(query)
    for doid, name, synonyms, xrefs, umls_cuis, in results:
        dict_name_to_doid[name.lower()] = doid
        #        synonyms=synonyms.split(',')
        for synonym in synonyms:
            synonym = synonym.split(' EXACT')[0].lower()
            synonym = synonym.split(' RELATED')[0].split(' NOS')[0]
            dict_name_to_doid[synonym] = doid
        for umls_cui in umls_cuis:
            #            print(umls_cui)
            if len(umls_cui) > 0:
                umls_cui = umls_cui.split(':')[1]
                if not umls_cui in dict_umls_cui_to_doid:
                    dict_umls_cui_to_doid[umls_cui] = [doid]
                else:
                    dict_umls_cui_to_doid[umls_cui].append(doid)
        for xref in xrefs:
            if xref[0:4] == 'OMIM':
                omim_id = xref.split(':')[1]
                if not omim_id in dict_omim_to_doid:
                    dict_omim_to_doid[omim_id] = [doid]
                else:
                    dict_omim_to_doid[omim_id].append(doid)

    print('number of name to doid:' + str(len(dict_name_to_doid)))
    print('number of different umls cuis:' + str(len(dict_umls_cui_to_doid)))
    print('number of different omims:' + str(len(dict_omim_to_doid)))


# dictionary with pair(doid, HPO id) and qualifier, db_reference, evidence code, frequency modifier
dict_disease_symptom_hpo_pair_to_information = {}

# dictionary with HPO id as key and value is [name, umls cui]
dict_hpo_ID_to_information = {}

# list of disease ids which are not mapped to doid
list_not_mapped_disease_ids_to_doid = []

# dictionary of already mapped disease to doids
dict_disease_id_to_doids = {}

# files for the different mapping steps of disease
file_decipher_name = open('mapping_files/disease/map_decipher_or_ORPHA_with_name.txt', 'w')
file_decipher_name.write('decipher id \t decipher name \t doid \t db_type \n')

file_decipher_name_umls = open('mapping_files/disease/map_decipher_or_ORPHA_with_name_umls_cui.txt', 'w')
file_decipher_name_umls.write('decipher id \t decipher name \t umls cuis \t doids \t db_type \n')

file_decipher_name_split = open('mapping_files/disease/map_decipher_or_ORPHA_with_name_split.txt', 'w')
file_decipher_name_split.write('decipher id \t decipher name \t doids \t db_type \n')

file_not_map_decipher = open('mapping_files/disease/not_map_decipher_or_ORPHA.txt', 'w')
file_not_map_decipher.write('decipher id \t decipher name \t db_type \n')

file_omim_omim = open('mapping_files/disease/map_omim_with_omim.txt', 'w')
file_omim_omim.write('omim id \t omim name \t doids \n')

file_omim_umls_cui = open('mapping_files/disease/map_omim_with_umls_cui.txt', 'w')
file_omim_umls_cui.write('omim id \t omim name \t umls cuis \t doids \n')

file_omim_name = open('mapping_files/disease/map_omim_with_name.txt', 'w')
file_omim_name.write('omim id \t omim name \t doids \n')

file_not_map_omim = open('mapping_files/disease/not_map_omim.txt', 'w')
file_not_map_omim.write('omim id \t omim name \t doids \n')

file_hpo_has_umls_cui = open('mapping_files/symptom/map_hpo_has_umls_cui.txt', 'w')
file_hpo_has_umls_cui.write('hpo id \t hpo name \t umls cui \n')

file_hpo_map_name_to_umls_cui = open('mapping_files/symptom/map_hpo_name_to_umls_cui.txt', 'w')
file_hpo_map_name_to_umls_cui.write('hpo id \t hpo name \t umls cui \n')

file_not_map_hpo = open('mapping_files/symptom/not_map_hpo.txt', 'w')
file_not_map_hpo.write('hpo id \t hpo name \n')

'''
load all disease-symptom information in and only remember the relationships where the disease 
can be mapped to DOID with use of UMLS and DO.
file:
    0 	DB 	
    1 	DB_Object_ID 	
    2 	DB_Name 	
    3 	Qualifier: can be NOT, Secondary, MILD, Moderate, Severe, can be multiple  
    4 	HPO ID 	
    5 	DB:Reference: source of the information	
    6 	Evidence code: 	how the information was gathered
    7 	Onset modifier: A term-id from the HPO-sub-ontology below the term “Age of onset” (HP:0003674). 	
    8 	Frequency modifier: A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279) 	
    9 	With: can have information  about characteristics 
    10 	Aspect: only with O (Phenotypic abnormality) 	
    11 	Synonym: can have synonyms for disease or disorder 	
    12 	Date 	
    13 	Assigned by 	
'''


def gather_all_disease_symptom_information_from_HPO():
    global doids
    # counter for decipher and orphanet diseases
    counter_decipher_orphanet = 0
    # counter for omim diseases
    counter_omim = 0
    # counter for not mapped decipher and orphanet diseases to doid
    counter_decipher_orphanet_not_mapped = 0
    # counter of mapped with name decipher and orphanet diseases
    counter_decipher_orphanet_map_with_name = 0
    # counter of mapped with splitted name decipher and orphanet diseases
    counter_decipher_orphanet_map_with_name_split = 0
    # counter of mapped with umls cui decipher and orphanet diseases
    counter_decipher_orphanet_map_with_mapped_umls_cui = 0
    # counter of not mapped omim disease
    counter_omim_not_mapped = 0
    # counter of mapped omim disease with omim
    counter_omim_map_with_omim = 0
    # counter of mapped omim diseases with umls cui
    counter_omim_map_with_umls_cui = 0
    # counter of mapped omim diseases with name
    counter_omim_with_name = 0

    i = 0

    f = open('phenotype_annotation.tab', 'r')
    for line in f:
        i += 1
        if i % 1000 == 0:
            print(datetime.datetime.utcnow())
            print(i)
            print('number of decipher:' + str(counter_decipher_orphanet))
            print('number of not mapped decipher:' + str(counter_decipher_orphanet_not_mapped))
            print('number of mapped decipher with name:' + str(counter_decipher_orphanet_map_with_name))
            print('number of decipher with mapped umls cui:' + str(counter_decipher_orphanet_map_with_mapped_umls_cui))
            print('number of mapped decipher with name splitted:' + str(counter_decipher_orphanet_map_with_name_split))
            print('number of omim:' + str(counter_omim))
            print('number of not mapped omim:' + str(counter_omim_not_mapped))
            print('number of direct map omim:' + str(counter_omim_map_with_omim))
            print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
            print('number of map omim with name:' + str(counter_omim_with_name))
        # if i == 100:
        #     break

        splitted = line.split('\t')
        db_disease = splitted[0]
        db_disease_id = splitted[1]
        db_disease_name = splitted[2].lower()
        qualifier = splitted[3]
        hpo_id = splitted[4]
        reference_id = splitted[5]
        evidence_code = splitted[6]
        frequency_modi = splitted[8]
        aspect = splitted[10]
        # O stands for phenotypic abnormality
        if aspect != 'O':
            continue
        # many diseases have more than one abnormal phenotype, so to make it faster search for every not mapped diseases 
        # only one time for the doid
        if db_disease_id in list_not_mapped_disease_ids_to_doid:
            continue

        # many diseases have more than one abnormal phenotype, so to make it faster search for every  diseases 
        # only one time for the doid
        if db_disease_id in dict_disease_id_to_doids:
            for doid in dict_disease_id_to_doids[db_disease_id]:
                dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier, reference_id, evidence_code,
                                                                                frequency_modi]
            if not hpo_id in dict_hpo_ID_to_information:
                dict_hpo_ID_to_information[hpo_id] = []
            continue

        # depending of the source of the diseases different mapping step's are used
        if db_disease != 'OMIM':
            counter_decipher_orphanet += 1
            #            print('decipher')
            #            print(counter_decipher_orphanet)
            # test if name is directly in dictionary
            if db_disease_name in dict_name_to_doid:
                doid = dict_name_to_doid[db_disease_name]
                #                print('decipher name')
                dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier, reference_id, evidence_code,
                                                                                frequency_modi]
                counter_decipher_orphanet_map_with_name += 1
                file_decipher_name.write(
                    db_disease_id + '\t' + db_disease_name + '\t' + doid + '\t' + db_disease + '\n')
                dict_disease_id_to_doids[db_disease_id] = [doid]
            else:
                # find doid with use of umls
                #                print('Decipher not mapped:'+db_disease_name)
                cur = con.cursor()
                #                print(db_disease_name)
                # this takes a lot of time
                query = ('Select CUI From MRCONSO Where lower(STR)="%s";')
                query = query % (db_disease_name)
                rows_counter = cur.execute(query)
                # rows_counter = 0
                found_a_map = False
                doids = []
                cuis = []

                if rows_counter > 0:
                    for (cui,) in cur:
                        if cui in dict_umls_cui_to_doid:
                            if not cui in cuis:
                                cuis.append(cui)
                                for doid in dict_umls_cui_to_doid[cui]:
                                    if not doid in doids:
                                        doids.append(doid)
                                        #                                print('decipher name umls cui')
                                        dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier,
                                                                                                        reference_id,
                                                                                                        evidence_code,
                                                                                                        frequency_modi]
                                        found_a_map = True
                if found_a_map:
                    counter_decipher_orphanet_map_with_mapped_umls_cui += 1
                    dict_disease_id_to_doids[db_disease_id] = doids
                    doids = '|'.join(doids)
                    cuis = '|'.join(cuis)
                    #                    print(db_disease_id)
                    #                    print(db_disease_name)
                    #                    print(cuis)
                    #                    print(doids)
                    file_decipher_name_umls.write(
                        db_disease_id + '\t' + db_disease_name + '\t' + cuis + '\t' + doids + '\t' + db_disease + '\n')
                else:
                    names = db_disease_name.split(' (')
                    has_found_one = False
                    doids = []
                    if len(names) > 1:
                        for name in names:
                            name = name.replace(')', '')
                            more_names = name.split(' / ')
                            for more_name in more_names:
                                if more_name in dict_name_to_doid:
                                    doid = dict_name_to_doid[more_name]
                                    #                print('decipher name')
                                    dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier,
                                                                                                    reference_id,
                                                                                                    evidence_code,
                                                                                                    frequency_modi]
                                    has_found_one = True

                    if has_found_one:
                        counter_decipher_orphanet_map_with_name_split += 1
                        dict_dict_disease_id_to_doids[db_disease_id] = doids
                        doids = '|'.join(doids)
                        file_decipher_name_split.write(
                            db_disease_id + '\t' + db_disease_name + '\t' + doids + '\t' + db_disease + '\n')
                    else:
                        counter_decipher_orphanet_not_mapped += 1
                        list_not_mapped_disease_ids_to_doid.append(db_disease_id)
                        file_not_map_decipher.write(db_disease_id + '\t' + db_disease_name + '\t' + db_disease + '\n')
                        continue
        else:
            counter_omim += 1
            #            print('omim')
            # test if omim id is direct in DO
            if db_disease_id in dict_omim_to_doid:
                counter_omim_map_with_omim += 1
                doids = []
                for doid in dict_omim_to_doid[db_disease_id]:
                    #                    print('omim')
                    dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier, reference_id,
                                                                                    evidence_code, frequency_modi]
                    doids.append(doid)
                dict_dict_disease_id_to_doids[db_disease_id] = doids
                doids = '|'.join(doids)
                file_omim_omim.write(db_disease_id + 'erweitern\t' + db_disease_name + '\t' + doids + '\n')

            else:
                # fined mapping with use of umls cuis
                cur = con.cursor()
                query = ('Select CUI From MRCONSO Where SAB="OMIM" and CODE= "%s" and lower(STR)="%s";')
                query = query % (db_disease_id, db_disease_name)
                rows_counter = cur.execute(query)
                found = False
                if rows_counter > 0:

                    doids = []
                    cuis = []
                    for (cui,) in cur:
                        #                        print(cui)
                        if cui in dict_umls_cui_to_doid:
                            if not cui in cuis:
                                cuis.append(cui)
                                for doid in dict_umls_cui_to_doid[cui]:
                                    if not doid in doids:
                                        #                                print('omim umls cui')
                                        dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier,
                                                                                                        reference_id,
                                                                                                        evidence_code,
                                                                                                        frequency_modi]
                                        found = True
                                        doids.append(doid)
                if found:
                    counter_omim_map_with_umls_cui += 1
                    dict_dict_disease_id_to_doids[db_disease_id] = doids
                    doids = '|'.join(doids)
                    cuis = '|'.join(cuis)
                    file_omim_umls_cui.write(db_disease_id + '\t' + db_disease_name + '\t' + cuis + '\t' + doids + '\n')

                else:
                    # last step is name mapping
                    if db_disease_name in dict_name_to_doid:
                        counter_omim_with_name += 1
                        doid = dict_name_to_doid[db_disease_name]
                        #                        print('omim name')
                        dict_disease_symptom_hpo_pair_to_information[(doid, hpo_id)] = [qualifier, reference_id,
                                                                                        evidence_code, frequency_modi]
                        file_omim_name.write(db_disease_id + '\t' + db_disease_name + '\t' + doid + '\n')
                        dict_disease_id_to_doids[db_disease_id] = [doid]

                    else:
                        #                        print('OMIM not mapped:'+db_disease_name)
                        counter_omim_not_mapped += 1
                        list_not_mapped_disease_ids_to_doid.append(db_disease_id)
                        file_not_map_omim.write(db_disease_id + '\t' + db_disease_name + '\n')
                        continue
        if not hpo_id in dict_hpo_ID_to_information:
            dict_hpo_ID_to_information[hpo_id] = []

    print('number of decipher:' + str(counter_decipher_orphanet))
    print('number of not mapped decipher:' + str(counter_decipher_orphanet_not_mapped))
    print('number of mapped decipher with name:' + str(counter_decipher_orphanet_map_with_name))
    print('number of decipher with mapped umls cui:' + str(counter_decipher_orphanet_map_with_mapped_umls_cui))
    print('number of mapped decipher with name splitted:' + str(counter_decipher_orphanet_map_with_name_split))
    print('number of omim:' + str(counter_omim))
    print('number of not mapped omim:' + str(counter_omim_not_mapped))
    print('number of direct map omim:' + str(counter_omim_map_with_omim))
    print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
    print('number of map omim with name:' + str(counter_omim_with_name))

    print('number of disease symptoms relationships:' + str(len(dict_disease_symptom_hpo_pair_to_information)))
    print('number of hpo:' + str(len(dict_hpo_ID_to_information)))


# use to delimet between the blocks
def is_data(line):
    return True if line.strip() else False


# file path to HPO data source
file_name = 'hpo.obo'

'''
function to find mesh id for a cui
'''


def cui_to_mesh(cui):
    cur = con.cursor()
    query = ("Select CODE From MRCONSO Where SAB= 'MSH' AND CUI= '%s'")
    query = query % (cui)
    rows_counter = cur.execute(query)
    if rows_counter > 0:
        codes = []
        for code, in cur:
            codes.append(code)

        codes = list(set(codes))
        return codes
    else:
        return []


'''
group the hpo terms together and get the information from the different terms
and integrate the symptoms with umls cui into Hetionet. But only the one are integrated which appears in the 
relationships between the disease and symptom 
'''


def get_hpo_information_and_map_to_umls():
    #    counter_has_no_xrefs=0
    #    counter_has_no_umls_cuis=0
    # the number of hpo symptoms which are in a relationship, but are not mapped to umls cui
    counter_no_umls_cui = 0
    # counter for the hpo symptoms which are not in hetionet
    counter_new_symptom_in_hetionet = 0
    #  counter for the symptoms which are already in Hetionet
    counter_symptom_from_hetionet = 0
    with open(file_name) as f:
        for (key, group) in groupby(f, is_data):
            #            print(key)
            if key:
                header = group.next().rstrip('\n')

                if header.find('[Term]') == -1:
                    continue

                use_full_hpo_id = True
                # dictionary for all values
                dict_all_info = {}
                # go throug all properties of the hpo id
                for info in group:
                    (key_term, value) = [element.strip() for element in info.split(":", 1)]
                    # check if the id is part of at least one relationship
                    if key_term == 'id':
                        if not value in dict_hpo_ID_to_information:
                            use_full_hpo_id = False
                            break
                    # for som propperties more than one value appears
                    if not key_term in dict_all_info:
                        dict_all_info[key_term] = [value]
                    else:
                        dict_all_info[key_term].append(value)
                #                    print(key_term)
                #                    print(value)

                # only for useful hpo ids
                if use_full_hpo_id:
                    #                    print(dict_all_info)
                    name = dict_all_info['name'][0].lower()
                    umls_cuis = []
                    has_at_least_one = False

                    umls_cui = ''

                    # try to find umls cui with external identifier from hpo
                    if 'xref' in dict_all_info:
                        for xref in dict_all_info['xref']:
                            if xref[0:4] == 'UMLS':
                                has_at_least_one = True
                                umls_cuis.append(xref.split(':')[1])
                        if has_at_least_one:
                            if len(umls_cuis) > 1:
                                cur = con.cursor()
                                query = ('Select CUI From MRCONSO Where  CUI in ("%s") And lower(STR)="%s" Limit 1;')
                                umls_cuis_string = '","'.join(umls_cuis)
                                query = query % (umls_cuis_string, name)
                                rows_counter = cur.execute(query)
                                if rows_counter > 0:
                                    for (cui,) in cur:
                                        umls_cuis = cui
                                else:
                                    umls_cuis = umls_cuis[0]
                            else:
                                umls_cuis = umls_cuis[0]

                            umls_cui = umls_cuis
                            dict_hpo_ID_to_information[dict_all_info['id'][0]].append(name)
                            dict_hpo_ID_to_information[dict_all_info['id'][0]].append(umls_cuis)
                            file_hpo_has_umls_cui.write(dict_all_info['id'][0] + '\t' + name + '\t' + umls_cui + '\n')
                        #                        else:
                    #                            print(dict_all_info['id'][0])
                    #                            print(';( ;( no umls cui')
                    #                            counter_has_no_umls_cuis+=1
                    #                    else:
                    #                        print(dict_all_info['id'][0])
                    #                        print(';( ;( has no xrefs')
                    #                        counter_has_no_xrefs+=1

                    # if no external identifier is a umls cui then search for the name in umls
                    if has_at_least_one == False:
                        cur = con.cursor()
                        query = ('Select CUI From MRCONSO Where  lower(STR)="%s" Limit 1;')
                        query = query % (name)
                        rows_counter = cur.execute(query)
                        if rows_counter > 0:
                            for (cui,) in cur:
                                umls_cui = cui
                            dict_hpo_ID_to_information[dict_all_info['id'][0]].append(name)
                            dict_hpo_ID_to_information[dict_all_info['id'][0]].append(umls_cui)
                            file_hpo_map_name_to_umls_cui.write(
                                dict_all_info['id'][0] + '\t' + name + '\t' + umls_cui + '\n')
                        else:

                            #                            print('Even know nothing is found ;(')
                            #                            print(dict_all_info['id'][0])
                            #                            print(name)
                            counter_no_umls_cui += 1
                            file_not_map_hpo.write(dict_all_info['id'][0] + '\t' + name + '\n')
                            continue
                    mesh_cui_ids = cui_to_mesh(umls_cui)
                    mesh_cui_ids.append(umls_cui)
                    # identifier can be umls cui or mesh id
                    query = '''MATCH (n:Symptom) Where n.identifier in ['%s'] RETURN n '''
                    #                    print(mesh_cui_ids)
                    mesh_cui_string = "','".join(mesh_cui_ids)
                    query = query % (mesh_cui_string)
                    is_their = g.run(query)
                    first_entry = is_their.evaluate()
                    name = name.replace('"', '')
                    url_hpo = 'http://compbio.charite.de/hpoweb/showterm?id=' + dict_all_info['id'][0]
                    if first_entry == None:
                        counter_new_symptom_in_hetionet += 1
                        url = 'http://identifiers.org/umls/' + umls_cui
                        query = '''
                        Create (s:Symptom{identifier:"%s",type:'cui',license:'UMLS licence', name:"%s", resource:['Human Phenotype Ontology'], source:'UMLS', url:"%s", hetionet:'no', do:'no', hpo:'yes', hpo_version:'1.2', hpo_release:'2017-10-05', url_HPO:"%s"});     '''
                        query = query % (umls_cui, name, url, url_hpo)
                    else:
                        resource = first_entry['resource'] if 'resource' in first_entry else []

                        resource.append("Human Phenotype Ontology")
                        resource = list(set(resource))
                        string_resource = '","'.join(resource)

                        counter_symptom_from_hetionet += 1
                        mesh_or_cui = first_entry['identifier']
                        query = '''MATCH (s:Symptom{identifier:"%s"}) 
                            Set   s.hpo='yes', s.cui="%s", s.hpo_version='1.2', s.hpo_release='2017-10-05', s.resource=["%s"] '''
                        query = query % (mesh_or_cui, umls_cui, string_resource)
                        # need to be reset because it mapped to a mesh or umls id
                        dict_hpo_ID_to_information[dict_all_info['id'][0]][1] = mesh_or_cui
                    g.run(query)

    # all symptoms which are not in hpo get the property hpo='no'
    query = '''MATCH (s:Symptom) Where not exists(s.hpo) Set s.hpo='no' '''
    g.run(query)
    #    print('number of hpo with no umle cui:'+str(counter_has_no_umls_cuis))
    #    print('number of hpo with no xrefs:'+str(counter_has_no_xrefs))
    print('number of hpos with no umls cui:' + str(counter_no_umls_cui))
    print('number of new symptoms:' + str(counter_new_symptom_in_hetionet))
    print('number of already existing symptoms:' + str(counter_symptom_from_hetionet))


'''
generate cypher file for the disease symptom connections, but only for the pairs where hpo
has a umls cui.
'''


def generate_cypher_file_for_connection():
    i = 1

    # cypher file with all cypher queries for the connection
    cypher_file = open('cypher/connection_symptoms_' + str(i) + '.cypher', 'w')
    cypher_file.write('begin \n')

    i += 1
    # count all cypher queries
    counter_connection = 0

    # number of queries in a commit block
    constrain_number = 20000

    # number of queries in a flie
    creation_max = 500000

    # counter new connection
    count_new_connection = 0

    # counter_update connection
    count_update_connection = 0

    for (doid, hpo_id), information in dict_disease_symptom_hpo_pair_to_information.items():
        try:
            file_d_s = open('disease-symptoms/disease_' + doid + '.txt', 'a')
        except:
            file_d_s = open('disease-symptoms/disease_' + doid + '.txt', 'w')
            query = ''' MATCH (n:Disease{identifier:"%s"}) Return n.name '''
            query = query % (doid)
            result = g.run(query)
            file_d_s.write(result.evaluate()[0] + '\n')
            file_d_s.write('\n symptomes: ID name hpo_id \n')

        #        print(dict_hpo_ID_to_information)
        #        print(hpo_id)
        #        print(dict_disease_symptom_hpo_pair_to_information.keys())
        if len(dict_hpo_ID_to_information[hpo_id]) == 0:
            continue
        # can be a umls cui or mesh id
        symptom_id = dict_hpo_ID_to_information[hpo_id][1]

        query = ''' MATCH (n:Symptom{identifier:"%s"}) Return n.name '''
        query = query % (symptom_id)
        result = g.run(query)
        file_d_s.write(symptom_id + ' ' + result.evaluate()[0] + ' ' + hpo_id + '\n')

        qualifier = information[0]
        reference_id = information[1]
        evidence_code = information[2]
        frequency_modi = information[3]

        query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"}) Set n.hpo='yes' Return l  '''
        query = query % (doid, symptom_id)
        result = g.run(query)
        first_entry = result.evaluate()
        url = 'http://compbio.charite.de/hpoweb/showterm?disease=' + reference_id
        if first_entry == None:
            query = '''MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"}) 
            Create (n)-[:PRESENTS_DpS{version:'phenotype_annotation.tab 2017-10-09 10:47',unbiased:'false',source:'%s',qualifier:'%s', efidence_code:'%s', frequency_modifier:'%s',  resource:['HPO'],hetionet:'no',do:'no', hpo:'yes', url:"%s"}]->(s); \n '''
            count_new_connection += 1
            query = query % (doid, symptom_id, reference_id, qualifier, evidence_code, frequency_modi, url)


        else:
            resource = first_entry['resource'] if 'resource' in first_entry else []
            resource.append("Human Phenotype Ontology")
            resource = list(set(resource))
            string_resource = '","'.join(resource)
            query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
            Set l.hpo='yes', l.version='phenotype_annotation.tab 2017-10-09 10:47', l.source='%s', l.qualifier='%s', l.efidence_code='%s', l.frequency_modifier='%s',l.resource=["%s"], l.url="%s"; \n'''
            count_update_connection += 1
            query = query % (
                doid, symptom_id, reference_id, qualifier, evidence_code, frequency_modi, string_resource, url)

        counter_connection += 1
        cypher_file.write(query)
        if counter_connection % constrain_number == 0:
            cypher_file.write('commit \n')
            if counter_connection % creation_max == 0:
                cypher_file.close()
                cypher_file = open('cypher/connection_symptoms_' + str(i) + '.cypher', 'w')
                cypher_file.write('begin \n')
                i += 1
            else:
                cypher_file.write('begin \n')

    cypher_file.write('commit \n begin \n')
    query = ''' MATCH ()-[l:PRESENTS_DpS]->(s:Symptom) Where not exists(l.hpo) Set l.hpo='no'; \n '''
    cypher_file.write(query)
    cypher_file.write('commit \n begin \n')
    cypher_file.write('Match (n:Disease) Where not exists(n.hpo) Set n.hpo="no"; \n')
    cypher_file.write('commit')

    print('number of new connection:' + str(count_new_connection))
    print('number of update connection:' + str(count_update_connection))
    print(counter_connection)


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in diseases information in dictionaries')

    get_all_disease_information_from_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather disease symptoms pairs with direct map of disease to DOID')
    gather_all_disease_symptom_information_from_HPO()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather symptoms information and map to umls cui if needed and integrated them into hetionet')

    get_hpo_information_and_map_to_umls()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship information into a cypher file')

    generate_cypher_file_for_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
