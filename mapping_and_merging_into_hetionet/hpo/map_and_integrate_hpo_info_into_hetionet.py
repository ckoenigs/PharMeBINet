# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:14:27 2017

@author: cassandra
"""

from py2neo import Graph#, authenticate
import MySQLdb as mdb
import sys
import datetime, time
import threading, csv
from _collections import defaultdict


# class of thread
class diseaseMapThread(threading.Thread):
    def __init__(self, threadID, name, db_disease_id, db_disease_name, db_disease_source):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.db_disease_id = db_disease_id
        self.db_disease_name = db_disease_name
        self.db_disease_source = db_disease_source

    def run(self):
        # print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock.acquire()
        map_hpo_disease_to_mondo(self.db_disease_id, self.db_disease_name, self.db_disease_source)
        #      print "Ending " + self.name
        #      print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()

# class of thread
class SymptomMapThread(threading.Thread):
    def __init__(self, threadID, name, symptom_name, symptom_xrefs, symptom_hpo_id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.symptom_name = symptom_name
        self.symptom_xrefs = symptom_xrefs
        self.symptom_hpo_id = symptom_hpo_id

    def run(self):
        # print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock.acquire()
        symptoms_mapping(self.symptom_name, self.symptom_xrefs,self.symptom_hpo_id)
        #      print "Ending " + self.name
        #      print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'umls')


    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# dictionary with the names as key and value is the mondo
dict_name_to_mondo = {}

# dictionary with umls cui as key and mondo list as value
dict_umls_cui_to_mondo = {}

# dictionary with omim id as key and mondo list as value
dict_omim_to_mondo = {}

# dictionary with Orphanet id as key and mondo list as value
dict_orphanet_to_mondo={}

'''
load all disease from hetionet and remember all name, synonym, umls cui and omim id
'''


def get_all_disease_information_from_hetionet():
    query = ''' Match (d:Disease) Return d.identifier, d.name, d.synonyms, d.xrefs, d.umls_cuis'''
    results = g.run(query)
    for mondo, name, synonyms, xrefs, umls_cuis, in results:
        if name:
            dict_name_to_mondo[name.lower()] = mondo
        if mondo =='MONDO:0007122':
            print('blub')
        #        synonyms=synonyms.split(',')
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_name_to_mondo[synonym] = mondo
        if umls_cuis:
            for umls_cui in umls_cuis:
                #            print(umls_cui)
                if len(umls_cui) > 0:
                    umls_cui = umls_cui.split(':')[1]
                    if not umls_cui in dict_umls_cui_to_mondo:
                        dict_umls_cui_to_mondo[umls_cui] = set([mondo])
                    else:
                        dict_umls_cui_to_mondo[umls_cui].add(mondo)
        if xrefs:
            for xref in xrefs:
                if xref[0:5] == 'OMIM:':
                    omim_id = xref.split(':')[1]
                    if not omim_id in dict_omim_to_mondo:
                        dict_omim_to_mondo[omim_id] = set([mondo])
                    else:
                        dict_omim_to_mondo[omim_id].add(mondo)
                elif xref[0:9]=='Orphanet:':
                    # print(mondo)
                    # print(xref)
                    orphanet_id = xref.split(':')[1]
                    if not orphanet_id in dict_orphanet_to_mondo:
                        dict_orphanet_to_mondo[orphanet_id] = set([mondo])
                    else:
                        dict_orphanet_to_mondo[orphanet_id].add(mondo)
                elif xref[0:5] == 'UMLS:':
                    umls_cui = xref.split(':')[1]
                    if not umls_cui in dict_umls_cui_to_mondo:
                        dict_umls_cui_to_mondo[umls_cui] = set[mondo]
                    else:
                        dict_umls_cui_to_mondo[umls_cui].add(mondo)

    print('number of name to mondo:' + str(len(dict_name_to_mondo)))
    print('number of different umls cuis:' + str(len(dict_umls_cui_to_mondo)))
    print('number of different omims:' + str(len(dict_omim_to_mondo)))
    print('number of different orphanets:'+str(len(dict_orphanet_to_mondo)))


# list of disease ids which are not mapped to mondo
list_not_mapped_disease_ids_to_mondo = []

# dictionary of already mapped disease to mondos
dict_disease_id_to_mondos = {}

# files for the different mapping steps of disease
file_decipher_name = open('mapping_files/disease/map_decipher_with_name.txt', 'w', encoding='utf-8')
csv_decipher_name=csv.writer(file_decipher_name,delimiter='\t')
csv_decipher_name.writerow(['decipher id','decipher name','mondo','db_type'])

file_decipher_name_umls = open('mapping_files/disease/map_decipher_with_name_umls_cui.txt', 'w', encoding='utf-8')
csv_decipher_name_umls=csv.writer(file_decipher_name_umls,delimiter='\t')
csv_decipher_name_umls.writerow(['decipher id','decipher name','umls cuis','mondo','db_type'])

file_decipher_name_split = open('mapping_files/disease/map_decipher_with_name_split.txt', 'w', encoding='utf-8')
csv_decipher_name_split=csv.writer(file_decipher_name_split,delimiter='\t')
csv_decipher_name_split.writerow(['decipher id','decipher name','mondo','db_type'])

file_not_map_decipher = open('mapping_files/disease/not_map_decipher.txt', 'w', encoding='utf-8')
csv_decipher_not_mapped=csv.writer(file_not_map_decipher,delimiter='\t')
csv_decipher_not_mapped.writerow(['decipher id','decipher name','db_type'])

file_omim_omim = open('mapping_files/disease/map_omim_with_omim.txt', 'w', encoding='utf-8')
csv_omim_omim=csv.writer(file_omim_omim,delimiter='\t')
csv_omim_omim.writerow(['omim id','omim name','mondos'])

file_omim_umls_cui = open('mapping_files/disease/map_omim_with_umls_cui.txt', 'w', encoding='utf-8')
csv_omim_cui=csv.writer(file_omim_umls_cui,delimiter='\t')
csv_omim_cui.writerow(['omim id','omim name','umls cuis','mondos'])

file_omim_name = open('mapping_files/disease/map_omim_with_name.txt', 'w', encoding='utf-8')
csv_omim_name=csv.writer(file_omim_name,delimiter='\t')
csv_omim_name.writerow(['omim id','omim name','mondos'])

file_not_map_orpha = open('mapping_files/disease/not_map_orpha.txt', 'w', encoding='utf-8')
csv_not_mapped_orpha=csv.writer(file_not_map_orpha,delimiter='\t')
csv_not_mapped_orpha.writerow(['orpha id','orpha name','mondos'])

file_orpha_orpha = open('mapping_files/disease/map_orpha_with_orpha.txt', 'w', encoding='utf-8')
csv_orpha_orpha=csv.writer(file_orpha_orpha,delimiter='\t')
csv_orpha_orpha.writerow(['orpha id','orpha name','mondos'])

file_orpha_name = open('mapping_files/disease/map_orpha_with_name.txt', 'w', encoding='utf-8')
csv_orpha_name=csv.writer(file_orpha_name,delimiter='\t')
csv_orpha_name.writerow(['orpha id','orpha name','mondos'])

file_not_map_omim = open('mapping_files/disease/not_map_omim.txt', 'w', encoding='utf-8')
csv_omim_not_mapped=csv.writer(file_not_map_omim,delimiter='\t')
csv_omim_not_mapped.writerow(['omim id','omim name'])

file_hpo_has_umls_cui = open('mapping_files/symptom/map_hpo_has_umls_cui.txt', 'w', encoding='utf-8')
csv_symptoms=csv.writer(file_hpo_has_umls_cui,delimiter='\t')
csv_symptoms.writerow(['hpo id','hpo name','umls cui'])

file_hpo_map_name_to_umls_cui = open('mapping_files/symptom/map_hpo_name_to_umls_cui.txt', 'w', encoding='utf-8')
csv_symptoms_name=csv.writer(file_hpo_map_name_to_umls_cui,delimiter='\t')
csv_symptoms_name.writerow(['hpo id','hpo name','umls cui'])

file_not_map_hpo = open('mapping_files/symptom/not_map_hpo.txt', 'w', encoding='utf-8')
csv_symptoms_not_mapped=csv.writer(file_not_map_hpo,delimiter='\t')
csv_symptoms_not_mapped.writerow(['hpo id','hpo name'])

# counter for decipher and orphanet diseases
counter_decipher = 0
# counter for omim diseases
counter_omim = 0
## count for orphanet
counter_orpha =0
# counter for not mapped decipher and orphanet diseases to mondo
counter_decipher_not_mapped = 0
# counter of mapped with name decipher and orphanet diseases
counter_decipher_map_with_name = 0
# counter of mapped with splitted name decipher and orphanet diseases
counter_decipher_map_with_name_split = 0
# counter of mapped with umls cui decipher and orphanet diseases
counter_decipher_map_with_mapped_umls_cui = 0
# counter of not mapped omim disease
counter_omim_not_mapped = 0
# counter of mapped omim disease with omim
counter_omim_map_with_omim = 0
# counter of mapped omim diseases with umls cui
counter_omim_map_with_umls_cui = 0
# counter of mapped omim diseases with name
counter_omim_with_name = 0
# counter of mapped orphanet diseases with name
counter_orpha_with_name = 0
# counter of not mapped orphanet disease
counter_orpha_not_mapped = 0
# counter of mapped orphanet disease with orphanet
counter_orpha_map_with_orpha = 0
# counter of mapped orphanet diseases with umls cui
counter_orpha_map_with_umls_cui = 0


# counter
counter = 0


'''
function that search for mondo with name, but also with splitted version of the name
'''
def mondo_with_name(db_disease_name):
    mondo=''
    if db_disease_name in dict_name_to_mondo:
        mondo = dict_name_to_mondo[db_disease_name]

    else:
        for name in db_disease_name.split(';'):
            if name in dict_name_to_mondo:
                mondo = dict_name_to_mondo[name]

    return mondo

'''
check on mapping same source
'''
def check_on_mapping_same_source(dictionary_of_source, counter_map_source_to_source,db_disease_name, db_disease_id,file_source_source):
    # get only the number
    id = db_disease_id.split(':')[1]
    if id in dictionary_of_source:
        counter_map_source_to_source += 1
        mondos = []
        for mondo in dictionary_of_source[id]:
            mondos.append(mondo)

        # most one of the multiple mapping is not the best that's why also use the name to get the
        # better mapping result
        if len(mondos) > 1:
            mondo = mondo_with_name(db_disease_name)
            if mondo in mondos:
                mondos = [mondo]
        dict_disease_id_to_mondos[db_disease_id] = mondos
        mondos = '|'.join(mondos)
        file_source_source.writerow([db_disease_id,db_disease_name, mondos ])
        return True, counter_map_source_to_source
    else:
        return False, counter_map_source_to_source

'''
check for mapping with name
'''
def mapping_with_name(db_disease_name, db_disease_id,counter_source_with_name,file_source_name):
    # last step is name mapping
    if db_disease_name in dict_name_to_mondo:
        counter_source_with_name += 1
        mondo = dict_name_to_mondo[db_disease_name]
        file_source_name.writerow([db_disease_id , db_disease_name , mondo ])
        dict_disease_id_to_mondos[db_disease_id] = [mondo]
        return True, counter_source_with_name
    else:
        return False, counter_source_with_name

'''
not mapped disease
'''
def not_mapped_disease(counter_source_not_mapped,db_disease_id,db_disease_name,file_not_map_source):
    counter_source_not_mapped += 1
    list_not_mapped_disease_ids_to_mondo.append(db_disease_id)
    file_not_map_source.writerow([db_disease_id , db_disease_name ])
    return counter_source_not_mapped

'''
check for an identifier
'''
def check_for_mapping_with_umls(db_disease_name, db_disease_id,name_in_umls, counter_source_map_with_umls_cui, file_source_umls_cui):
    # get only the number
    id=db_disease_id.split(':')[1]

    # try to map with umls

    # fined mapping with use of umls cuis
    cur = con.cursor()
    query = ('Select CUI From MRCONSO Where SAB="%s" and CODE= "%s" and STR="%s";')
    query = query % (name_in_umls, id, db_disease_name)
    rows_counter = cur.execute(query)
    found = False
    if rows_counter > 0:

        mondos = []
        cuis = []
        for (cui,) in cur:
            #                        print(cui)
            if cui in dict_umls_cui_to_mondo:
                if not cui in cuis:
                    cuis.append(cui)
                    for mondo in dict_umls_cui_to_mondo[cui]:
                        if not mondo in mondos:
                            found = True
                            mondos.append(mondo)
    if found:
        counter_source_map_with_umls_cui += 1
        # most one of the multiple mapping is not the best that's why also use the name to get the
        # better mapping result
        if len(mondos) > 1:
            mondo = mondo_with_name(db_disease_name)
            if mondo in mondos:
                mondos = [mondo]
        dict_disease_id_to_mondos[db_disease_id] = mondos
        mondos = '|'.join(mondos)
        cuis = '|'.join(cuis)
        file_source_umls_cui.writerow([db_disease_id , db_disease_name , cuis , mondos ])
        return True, counter_source_map_with_umls_cui
    else:
        return False, counter_source_map_with_umls_cui






'''
load all disease information from neo4j in and only remember the relationships where the disease 
can be mapped to mondo with use of UMLS and DO.

'''


def map_hpo_disease_to_mondo(db_disease_id, db_disease_name, db_disease_source):
    global counter_decipher, counter_omim, counter_decipher_not_mapped
    global counter_decipher_map_with_name, counter_decipher_map_with_name_split
    global counter_decipher_map_with_mapped_umls_cui, counter_omim_not_mapped, counter_omim_map_with_omim
    global counter_omim_map_with_umls_cui, counter_omim_with_name, counter, counter_orpha, counter_orpha_with_name
    global counter_orpha_not_mapped, counter_orpha_map_with_orpha,  counter_orpha_map_with_umls_cui

    counter += 1
    if counter % 5000 == 0:
        print(datetime.datetime.utcnow())
        print(counter)
        print('number of decipher:' + str(counter_decipher))
        print('number of not mapped decipher:' + str(counter_decipher_not_mapped))
        print('number of mapped decipher with name:' + str(counter_decipher_map_with_name))
        print('number of decipher with mapped umls cui:' + str(counter_decipher_map_with_mapped_umls_cui))
        print('number of mapped decipher with name splitted:' + str(counter_decipher_map_with_name_split))
        print('number of omim:' + str(counter_omim))
        print('number of not mapped omim:' + str(counter_omim_not_mapped))
        print('number of direct map omim:' + str(counter_omim_map_with_omim))
        print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
        print('number of map omim with name:' + str(counter_omim_with_name))
        print('number of orpha:' + str(counter_orpha))
        print('number of not mapped orpha:' + str(counter_orpha_not_mapped))
        print('number of direct map orpha:' + str(counter_orpha_map_with_orpha))
        print('number of map orpha with umls cui:' + str(counter_orpha_map_with_umls_cui))
        print('number of map orpha with name:' + str(counter_orpha_with_name))
          # if i == 100:
    #     break
    db_disease_name = db_disease_name.lower()

    # depending of the source of the diseases different mapping step's are used
    if db_disease_source == 'DECIPHER':
        counter_decipher += 1
        #            print('decipher')
        #            print(counter_decipher)
        # test if name is directly in dictionary
        # else try to mapp the name but change the name so that no () appears and use the synonyms in the  name
        found_name_mapping,counter_decipher_map_with_name =mapping_with_name(db_disease_name,db_disease_id,counter_decipher_map_with_name,csv_decipher_name)
        if not found_name_mapping:
            names = db_disease_name.split(' (')
            has_found_one = False
            mondos = set([])
            if len(names) > 1:
                for name in names:
                    name = name.replace(')', '')
                    more_names = name.split(' / ')
                    for more_name in more_names:
                        if more_name in dict_name_to_mondo:
                            mondo = dict_name_to_mondo[more_name]
                            mondos.add(mondo)
                            has_found_one = True

            if has_found_one:
                counter_decipher_map_with_name_split += 1
                dict_disease_id_to_mondos[db_disease_id] = list(mondos)
                mondos = '|'.join(list(mondos))
                csv_decipher_name_split.writerow([
                    db_disease_id , db_disease_name , mondos , db_disease_source])
            # try to map with find a umls cui for the name and mapp this id
            else:
                cur = con.cursor()
                # this takes a lot of time
                query = ('Select CUI From MRCONSO Where STR="%s";')
                query = query % (db_disease_name)
                rows_counter = cur.execute(query)
                # rows_counter = 0
                found_a_map = False
                mondos = []
                cuis = []

                if rows_counter > 0:
                    for (cui,) in cur:
                        if cui in dict_umls_cui_to_mondo:
                            if not cui in cuis:
                                cuis.append(cui)
                                for mondo in dict_umls_cui_to_mondo[cui]:
                                    if not mondo in mondos:
                                        mondos.append(mondo)
                                        found_a_map = True
                if found_a_map:
                    counter_decipher_map_with_mapped_umls_cui += 1
                    dict_disease_id_to_mondos[db_disease_id] = mondos
                    mondos = '|'.join(mondos)
                    cuis = '|'.join(cuis)
                    csv_decipher_name_umls.writerow([
                        db_disease_id , db_disease_name , cuis , mondos , db_disease_source ])
                else:
                    counter_decipher_not_mapped= not_mapped_disease(counter_decipher_not_mapped,db_disease_id,db_disease_name,csv_decipher_not_mapped)
                    return

    elif db_disease_source == 'OMIM':
        counter_omim += 1

        # get only the number
        id = db_disease_id.split(':')[1]

        #            print('omim')
        # test if omim id is direct in DO
        found_same_mapping, counter_omim_map_with_omim=check_on_mapping_same_source(dict_omim_to_mondo,counter_omim_map_with_omim,db_disease_name,db_disease_id,csv_omim_omim)
        if not found_same_mapping:

            found_with_umls, counter_omim_map_with_umls_cui = check_for_mapping_with_umls(db_disease_name,db_disease_id,"OMIM",counter_omim_map_with_umls_cui,csv_omim_cui)
            if not found_with_umls:
                mappped_with_name, counter_omim_with_name=mapping_with_name(db_disease_name,db_disease_id,counter_omim_with_name,csv_omim_name)
                if not mappped_with_name:
                    counter_omim_not_mapped=not_mapped_disease(counter_omim_not_mapped, db_disease_id, db_disease_name,
                                       csv_omim_not_mapped)
                    return

    elif db_disease_source == 'ORPHA':
        counter_orpha += 1
        #            print('omim')
        # test if ORPHA id is direct in Mondo
        found_same_mapping, counter_orpha_map_with_orpha=check_on_mapping_same_source(dict_orphanet_to_mondo, counter_orpha_map_with_orpha, db_disease_name,
                                            db_disease_id, csv_orpha_orpha)
        if not found_same_mapping:
            #check if name mapps
            found_with_name, counter_orpha_with_name=mapping_with_name(db_disease_name,db_disease_id,counter_orpha_with_name,csv_orpha_name)
            if not found_with_name:
                #not mapped information are add to file
                counter_orpha_not_mapped=not_mapped_disease(counter_orpha_not_mapped,db_disease_id,db_disease_name,csv_not_mapped_orpha)

    else:
        print('a different db disease source '+ db_disease_source)

    # print('number of decipher:' + str(counter_decipher))
    # print('number of not mapped decipher:' + str(counter_decipher_not_mapped))
    # print('number of mapped decipher with name:' + str(counter_decipher_map_with_name))
    # print('number of decipher with mapped umls cui:' + str(counter_decipher_map_with_mapped_umls_cui))
    # print('number of mapped decipher with name splitted:' + str(counter_decipher_map_with_name_split))
    # print('number of omim:' + str(counter_omim))
    # print('number of not mapped omim:' + str(counter_omim_not_mapped))
    # print('number of direct map omim:' + str(counter_omim_map_with_omim))
    # print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
    # print('number of map omim with name:' + str(counter_omim_with_name))


# dictionary with mondo as key and hpo ids as value
dict_mondo_to_hpo_ids = defaultdict(list)

# csv file for mapping disease
file_disease=open('mapping_files/disease_mapped.tsv','w', encoding='utf-8')
csv_disease= csv.writer(file_disease,delimiter='\t')
csv_disease.writerow(['hpo_id','hetionet_id'])


# csv file for mapping disease
file_symptom_mapped=open('mapping_files/symptom_mapped.tsv','w', encoding='utf-8')
csv_symptom_mapped= csv.writer(file_symptom_mapped,delimiter='\t')
csv_symptom_mapped.writerow(['hpo_id','hetionet_id', 'umls_cuis','mesh_ids'])

# cypher file for mapping and integration
cypher_file=open('cypher.cypher','w')


# csv file for mapping disease
file_symptom_new=open('mapping_files/symptom_new.tsv','w', encoding='utf-8')
csv_symptom_new= csv.writer(file_symptom_new,delimiter='\t')
csv_symptom_new.writerow(['hpo_id','hetionet_id', 'umls_cuis','mesh_ids'])


# the general query start
query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/hpo/%s" As line FIELDTERMINATOR '\\t' 
    Match'''


'''
Integrate mapping connection between disease and HPOdisease and make a dictionary mondo to hpo id
'''


def integrate_mapping_of_disease_into_hetionet():
    #query for mapping disease and written into file
    query= query_start+ ''' (n:HPOdisease{id: line.hpo_id}), (d:Disease{identifier:line.hetionet_id}) Set d.hpo="yes" Create (d)-[:equal_to_hpo_disease]->(n);\n '''
    query =query %(path_of_directory,'disease_mapped.tsv')
    cypher_file.write(query)
    # write mapping in csv file
    for hpo_id, mondos in dict_disease_id_to_mondos.items():
        for mondo in mondos:
            csv_disease.writerow([hpo_id, mondo])

            # fill mapped dictionary
            dict_mondo_to_hpo_ids[mondo].append(hpo_id)

    query = '''Match (d:disease{identifier:"%s"}) Where exists(d.hpo) Set d.resource=d.resource+"HPO";\n '''
    cypher_file.write(query)

    query = '''Match (d:disease{identifier:"%s"}) Where not exists(d.hpo) Set d.hpo="no";\n '''
    cypher_file.write(query)


'''
function to find mesh id for a cui
'''


def cui_to_mesh(cui):
    cur = con.cursor()
    query = ("Select Distinct CODE From MRCONSO Where SAB= 'MSH' AND CUI In ('%s')")
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

## dictionary of symptoms
dict_of_hetionet_symptoms={}


'''
Get al symptoms from hetionet and put this information into a dictionary
'''
def get_all_symptoms_and_add_to_dict():
    query = '''MATCH (n:Symptom) RETURN n  '''
    results=g.run(query)

    #add all symptoms to dictioanry
    for result, in results:
        identifier=result['identifier']
        dict_of_hetionet_symptoms[identifier]=dict(result)


# dictionary from hpo symptom to hetionet symptom
dict_hpo_to_hetionet_symptoms=defaultdict(set)

#dictionary with the new mesh ids
dict_new_mesh_ids={}

'''
first search for umls cuis if not in hpo existing check in umls
then map with umls to mesh
check if mesh are in hetionet esle generate new nodes
'''
def symptoms_mapping(name, xrefs, hpo_id):
    global counter_no_umls_cui, counter_symptoms
    global counter_new_symptom_in_hetionet, counter_symptom_from_hetionet
    #                    print(dict_all_info)
    name = name.lower()
    umls_cuis = []
    has_at_least_one = False

    if hpo_id=='HP:0002027':
        print('oj')

    # start = time.time()
    # try to find umls cui with external identifier from hpo
    if xrefs is not None:
        for xref in xrefs:
            if xref[0:4] == 'UMLS':
                has_at_least_one = True
                umls_cuis.append(xref.split(':')[1])
            else:
                print('other xref then umls :O')
                print(xref)
        if has_at_least_one:
            csv_symptoms.writerow([hpo_id, name, '|'.join(umls_cuis)])
    # print('\t xrefs : %.4f seconds' % (time.time() - start))
    # start = time.time()

    # if no external identifier is a umls cui then search for the name in umls
    if not has_at_least_one:
        cur = con.cursor()
        query = 'SELECT DISTINCT CUI FROM MRCONSO WHERE STR = "%s";' % name
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            for (cui,) in cur:
                umls_cuis.append(cui)
            csv_symptoms_name.writerow([
                hpo_id, name, '|'.join(umls_cuis)])
        else:
            counter_no_umls_cui += 1
            csv_symptoms_not_mapped.writerow([hpo_id, name])
            return
    # print('\t umls : %.4f seconds' % (time.time() - start))
    # start = time.time()

    #
    no_cui_in_hetinet_symptomes = False
    all_mapped_cuis_mesh_ids = []
    # string form of umls cuis
    umls_string = '|'.join(umls_cuis)

    name = name.replace('"', '')
    umls_cuis_string_for_mysql = "','".join(umls_cuis)
    mesh_cui_ids = cui_to_mesh(umls_cuis_string_for_mysql)
    # found one
    found_one = False
    # string form of mesh cuis
    mesh_cuis_string = '|'.join(mesh_cui_ids)

    #check if mesh ids from hpo map to hetionet mesh
    for mesh_id in mesh_cui_ids:

        if mesh_id in dict_of_hetionet_symptoms:
            found_one = True

            csv_symptom_mapped.writerow([hpo_id, mesh_id, umls_string, mesh_cuis_string])
            dict_hpo_to_hetionet_symptoms[hpo_id].add(mesh_id)

            all_mapped_cuis_mesh_ids.append(mesh_id)
    # print('\t preparation and write into files : %.4f seconds' % (time.time() - start))
    # start = time.time()

    if not found_one:
        name = name.replace('"', '')
        counter_new_symptom_in_hetionet+=1
        dict_hpo_to_mesh_ids[hpo_id]=mesh_cui_ids
        for mesh_id in mesh_cui_ids:
            if mesh_id in dict_new_mesh_ids:
                print('oh no double mesh, this can cause problems')
                print(mesh_id)
                print(hpo_id)
                print(dict_new_mesh_ids[mesh_id])
                print(name)
                dict_new_mesh_ids[mesh_id].append(hpo_id)
            else:
                dict_new_mesh_ids[mesh_id]=[hpo_id]
            csv_symptom_new.writerow([hpo_id, mesh_id, umls_string, mesh_cuis_string])
            dict_hpo_to_hetionet_symptoms[hpo_id].add(mesh_id)
    else:
        dict_hpo_to_mesh_ids[hpo_id]=all_mapped_cuis_mesh_ids
        counter_symptom_from_hetionet+=1

        # print('\t not mapped write into file : %.4f seconds' % (time.time() - start))

    if counter_symptoms % 200 == 0:
        print(counter_symptoms)
        print(datetime.datetime.utcnow())

# aspect dictionary
dict_aspect={
    'P': 'Phenotypic abnormality',
    'I': 'inheritance',
    'C': 'onset and clinical course'
}

# dictionary of hpo symptoms
dict_hpo_symptoms={}

#dictionary mapping hpo to mesh
dict_hpo_to_mesh_ids={}


'''
Map hpo symptomes to umls cui or mesh and generate connection between symptoms and hpo symptoms. Further the 
hpo symptoms get the mapped umls_cui or mesh as property.
'''


def map_hpo_symptoms_and_integrate_into_hetionet():
    global counter_symptoms, counter_no_umls_cui
    # '','hetionet_id', 'umls_cuis'
    query =query_start+ '''MATCH (s:Symptom{identifier:line.hetionet_id }) , (n:HPOsymptom{id:line.hpo_id}) Set s.hpo='yes', s.umls_cuis=split(line.umls_cuis,"|") s.xrefs=n.xrefs , s.hpo_version='1.2', s.hpo_release='2019-11-08', s.definition=n.def, s.synonyms=n.synonyms, s.url_HPO="http://compbio.charite.de/hpoweb/showterm?id="+line.hpo_id, n.mesh_ids=split(line.mesh_ids,'|') Create (s)-[:equal_to_hpo_symptoms]->(n);\n'''
    query = query %(path_of_directory,'symptom_mapped.tsv')
    cypher_file.write(query)
    # all symptoms which are in hetionet set the resource hpo
    query = '''MATCH (s:Symptom) Where exists(s.hpo) Set s.resource=s.resource+"HPO";\n '''
    cypher_file.write(query)

    query=query_start+''' Match (n:HPOsymptom{id:line.hpo_id}) Set n.mesh_ids=split(line.mesh_ids,'|') Create (s:Symptom{identifier:line.hetionet_id, umls_cuis:split(line.umls_cuis,"|") ,source:'MESH',license:'UMLS licence', name:n.name, resource:['HPO'], source:'MESH', url:"http://identifiers.org/mesh/"+line.hetionet_id , xrefs:n.xrefs, hpo:'yes', hpo_version:'1.2', hpo_release:'2019-11-08', definition:n.def, url_HPO:"http://compbio.charite.de/hpoweb/showterm?id="+line.hpo_id})  Create (s)-[:equal_to_hpo_symptoms]->(n);\n '''
    query=query %(path_of_directory,'symptom_new.tsv')
    cypher_file.write(query)
    #    counter_has_no_xrefs=0
    #    counter_has_no_umls_cuis=0
    global counter_no_umls_cui, counter_new_symptom_in_hetionet, counter_symptom_from_hetionet
    # the number of hpo symptoms which are in a relationship, but are not mapped to umls cui
    counter_no_umls_cui = 0
    # counter for the hpo symptoms which are not in hetionet
    counter_new_symptom_in_hetionet = 0
    #  counter for the symptoms which are already in Hetionet
    counter_symptom_from_hetionet = 0

    # create a lock, is used to synchronized threads
    global threadLock
    threadLock = threading.Lock()

    # all threads
    threads_symptoms = []

    thread_id = 1


    query = '''MATCH (n:HPOsymptom) Where not exists(n.replaced_by)  RETURN n, n.id, n.name, n.xref '''
    results = g.run(query)
    counter_symptoms=0

    for node, hpo_id, name, xrefs, in results:
        counter_symptoms+=1
        dict_hpo_symptoms[hpo_id]=node

        # create thread
        thread = SymptomMapThread(thread_id, 'thread_' + str(thread_id), name,xrefs,hpo_id)
        # start thread
        thread.start()
        # add to list
        threads_symptoms.append(thread)
        # increase thread id
        thread_id += 1
        if thread_id % 200 == 0:
            # wait for all threads
            for t in threads_symptoms:
                t.join()

        # wait for all threads
    for t in threads_symptoms:
        t.join()


    # all symptoms which are not in hpo get the property hpo='no'
    query = '''MATCH (s:Symptom) Where not exists(s.hpo) Set s.hpo='no';\n '''
    cypher_file.write(query)

    #    print('number of hpo with no umle cui:'+str(counter_has_no_umls_cuis))
    #    print('number of hpo with no xrefs:'+str(counter_has_no_xrefs))
    print('number of hpos with no umls cui:' + str(counter_no_umls_cui))
    print('number of new symptoms:' + str(counter_new_symptom_in_hetionet))
    print('number of already existing symptoms:' + str(counter_symptom_from_hetionet))


# list of all new disease-symptom pairs
list_new_disease_symptom_pairs = []

# dictionary of frequency of occurrence
dict_frequency={}


'''
generate cypher file for the disease symptom connections, but only for the pairs where hpo
has a umls cui.
'''


def generate_cypher_file_for_connection(cypher_file):
    #definition of counter
    count_new_connection=0
    count_update_connection=0
    counter_connection=0

    # csv file for relationship symptom- disease
    file_rela_new = open('mapping_files/rela_new.tsv', 'w', encoding='utf-8')
    csv_rela_new = csv.writer(file_rela_new, delimiter='\t')

    file_rela_update = open('mapping_files/rela_update.tsv', 'w', encoding='utf-8')
    csv_rela_update = csv.writer(file_rela_update, delimiter='\t')

    properties=['disease_id', 'symptom']

    # get all properties
    query='MATCH (n:HPOdisease)-[p:present]-(:HPOsymptom) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
    results=g.run(query)
    query_exist=''' (n:Disease{identifier: line.disease_id})-[r:PRESENTS_DpS]-(s:Symptom{identifier:line.symptom}) Set '''
    query_new=''' (n:Disease{identifier: line.disease_id}), (s:Symptom{identifier:line.symptom}) Create (n)-[r:PRESENTS_DpS{'''
    for result, in results:
        if result!='frequency_modifier':

            properties.append(result)
            query_exist+= 'r.'+result+'=split(line.'+result+',"|"), '
            query_new +=  result + ':split(line.' + result + ',"|"), '
        else:
            for x in ['frequence_name', 'frequence_def']:
                properties.append(x)
                query_exist += 'r.' + x + '=split(line.' + x + ',"|"), '
                query_new += x + ':split(line.' + x + ',"|"), '

    csv_rela_new.writerow(properties)
    csv_rela_update.writerow(properties)
    query_exists=query_start+query_exist[:-2]+"r.hpo='yes', r.version='phenotype_annotation.tab 2019-11-08', r.resource=r.resource+'HPO', r.url='http://compbio.charite.de/hpoweb/showterm?disease='+line.source; \n"
    query_exists=query_exists %(path_of_directory,"rela_update.tsv")
    cypher_file.write(query_exists)
    query='''Match (n:Disease})-[r:PRESENTS_DpS]-(s:Symptom) Where r.hpo='yes SET r.resource=r.resource+'HPO';\n '''
    cypher_file.write(query)

    query_new=query_start+query_new[:-2]+'''version:'phenotype_annotation.tab 2019-11-08',unbiased:'false',source:'Human Phenontype Ontology', resource:['HPO'], hpo:'yes', url:'http://compbio.charite.de/hpoweb/showterm?disease='+line.source}]->(s);\n'''
    query_new = query_new % (path_of_directory, "rela_new.tsv")
    cypher_file.write(query_new)

    # fill the files
    for mondo, hpo_disease_ids in dict_mondo_to_hpo_ids.items():

        for hpo_disease_id in hpo_disease_ids:
            query = '''MATCH p=(:HPOdisease{id:"%s"})-[r:present]->(b) RETURN r, b.id '''
            query = query % (hpo_disease_id)
            results = g.run(query)

            for connection, hpo_id, in results:
                # some hpo did not map to mesh
                if hpo_id in dict_hpo_to_mesh_ids:
                    mesh_ids= dict_hpo_to_mesh_ids[hpo_id]
                    if len(mesh_ids) > 0:
                        rela_properties=[]
                        for property in properties:
                            if property not in ['frequency_modifier', 'aspect']:
                                rela_properties.append(connection[property])
                            elif property =='aspect':
                                if 'aspect' in connection:
                                    if len(connection['aspect'])>1:
                                        sys.exit('HPO mapping has multiple aspects')
                                    for aspect in connection['aspect']:
                                        if aspect in dict_aspect:
                                            rela_properties.append(dict_aspect[aspect])
                                        else:
                                            rela_properties.append(aspect)
                                else:
                                    rela_properties.append('')
                            else:
                                node = dict_hpo_symptoms[connection[property]]
                                rela_properties.append(node['name'])
                                rela_properties.append(node['def'])

                        for mesh_id in mesh_ids:

                            all_properties = [mondo, mesh_id]
                            all_properties.extend(rela_properties)

                            if (mondo, mesh_id) in list_new_disease_symptom_pairs:
                                continue
                            elif mesh_id in dict_new_mesh_ids:
                                counter_connection += 1
                                count_new_connection+=1
                                csv_rela_new.writerow(all_properties)
                                list_new_disease_symptom_pairs.append((mondo,mesh_id))
                            else:
                                counter_connection+=1
                                query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"}) 
                                Set n.hpo='yes' Return l '''
                                query = query % (mondo, mesh_id)
                                result = g.run(query)
                                first_entry = result.evaluate()
                                #create new relationship
                                if first_entry == None:
                                    csv_rela_new.writerow(all_properties)
                                    # query = '''MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"})
                                    # Create (n)-[:PRESENTS_DpS{version:'phenotype_annotation.tab 2019-11-08',unbiased:'false',source:'%s',qualifier:'%s', efidence_code:'%s', frequency_modifier:'%s',  resource:['HPO'],hetionet:'no',do:'no', hpo:'yes', url:"%s"}]->(s); \n '''
                                    count_new_connection += 1
                                    list_new_disease_symptom_pairs.append((mondo,mesh_id))

                                else:
                                    # query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
                                    # Set l.hpo='yes', l.version='phenotype_annotation.tab 2017-10-09 10:47', l.source='%s', l.qualifier='%s', l.efidence_code='%s', l.frequency_modifier='%s',l.resource=["%s"], l.url="%s"; \n'''
                                    count_update_connection += 1
                                    csv_rela_update.writerow(all_properties)

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

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

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
    print('map hpo disease to mondo')

    # create a lock, is used to synchronized threads
    global threadLock
    threadLock = threading.Lock()

    # all threads
    threads_disease = []

    thread_id = 1

    # search for hpo disease, but exclude old entries
    query = ''' Match (d:HPOdisease) Where not exists(d.is_obsolete)  Return d.id, d.name, d.source'''
    results = g.run(query)
    for db_disease_id, db_disease_name, db_disease_source, in results:
        # create thread
        thread = diseaseMapThread(thread_id, 'thread_' + str(thread_id), db_disease_id, db_disease_name,
                                  db_disease_source)
        # start thread
        thread.start()
        # add to list
        threads_disease.append(thread)
        # increase thread id
        thread_id += 1
        if thread_id % 200 == 0:
            # wait for all threads
            for t in threads_disease:
                t.join()

    # wait for all threads
    for t in threads_disease:
        t.join()
    #     map_hpo_disease_to_mondo(db_disease_id, db_disease_name, db_disease_source)

    print('finished mapping disease')
    print('number of decipher:' + str(counter_decipher))
    print('number of not mapped decipher:' + str(counter_decipher_not_mapped))
    print('number of mapped decipher with name:' + str(counter_decipher_map_with_name))
    print('number of decipher with mapped umls cui:' + str(counter_decipher_map_with_mapped_umls_cui))
    print('number of mapped decipher with name splitted:' + str(counter_decipher_map_with_name_split))
    print('number of omim:' + str(counter_omim))
    print('number of not mapped omim:' + str(counter_omim_not_mapped))
    print('number of direct map omim:' + str(counter_omim_map_with_omim))
    print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
    print('number of map omim with name:' + str(counter_omim_with_name))
    print('number of orpha:' + str(counter_orpha))
    print('number of not mapped orpha:' + str(counter_orpha_not_mapped))
    print('number of direct map orpha:' + str(counter_orpha_map_with_orpha))
    print('number of map orpha with umls cui:' + str(counter_orpha_map_with_umls_cui))
    print('number of map orpha with name:' + str(counter_orpha_with_name))

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate mapping into hetionet for disease')

    integrate_mapping_of_disease_into_hetionet()
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate dictionary from symptoms of hetionet')


    get_all_symptoms_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('map hpo symptoms to mesh or umls cui and integrated them into hetionet')

    map_hpo_symptoms_and_integrate_into_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship information into a cypher file')

    generate_cypher_file_for_connection(cypher_file)

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
