# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:14:27 2017

@author: cassandra
"""

import sys
import datetime
import threading, csv
from _collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases  # , authenticate


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


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary with the names as key and value is the mondo
dict_name_to_mondo = {}

# dictionary with umls cui as key and mondo list as value
dict_umls_cui_to_mondo = {}

# dictionary with omim id as key and mondo list as value
dict_omim_to_mondo = {}

# dictionary with Orphanet id as key and mondo list as value
dict_orphanet_to_mondo = {}

# dictionary mondo to node infos
dict_mondo_to_node = {}

'''
load all disease from hetionet and remember all name, synonym, umls cui and omim id
'''


def get_all_disease_information_from_hetionet():
    query = ''' Match (d:Disease) Return d.identifier, d.name, d.synonyms, d.xrefs, d.umls_cuis, d'''
    results = g.run(query)
    for mondo, name, synonyms, xrefs, umls_cuis, node, in results:
        dict_mondo_to_node[mondo] = dict(node)
        if name:
            dict_name_to_mondo[name.lower()] = mondo
        if mondo == 'MONDO:0007122':
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
                elif xref[0:9] == 'Orphanet:':
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
    print('number of different orphanets:' + str(len(dict_orphanet_to_mondo)))


# list of disease ids which are not mapped to mondo
list_not_mapped_disease_ids_to_mondo = []

# dictionary of already mapped disease to mondos
dict_disease_id_to_mondos = {}

# files for the different mapping steps of disease
file_decipher_name = open('mapping_files/disease/map_decipher_with_name.txt', 'w', encoding='utf-8')
csv_decipher_name = csv.writer(file_decipher_name, delimiter='\t')
csv_decipher_name.writerow(['decipher id', 'decipher name', 'mondo', 'db_type'])

file_decipher_name_umls = open('mapping_files/disease/map_decipher_with_name_umls_cui.txt', 'w', encoding='utf-8')
csv_decipher_name_umls = csv.writer(file_decipher_name_umls, delimiter='\t')
csv_decipher_name_umls.writerow(['decipher id', 'decipher name', 'umls cuis', 'mondo', 'db_type'])

file_decipher_name_split = open('mapping_files/disease/map_decipher_with_name_split.txt', 'w', encoding='utf-8')
csv_decipher_name_split = csv.writer(file_decipher_name_split, delimiter='\t')
csv_decipher_name_split.writerow(['decipher id', 'decipher name', 'mondo', 'db_type'])

file_not_map_decipher = open('mapping_files/disease/not_map_decipher.txt', 'w', encoding='utf-8')
csv_decipher_not_mapped = csv.writer(file_not_map_decipher, delimiter='\t')
csv_decipher_not_mapped.writerow(['decipher id', 'decipher name', 'db_type'])

file_omim_omim = open('mapping_files/disease/map_omim_with_omim.txt', 'w', encoding='utf-8')
csv_omim_omim = csv.writer(file_omim_omim, delimiter='\t')
csv_omim_omim.writerow(['omim id', 'omim name', 'mondos'])

file_omim_umls_cui = open('mapping_files/disease/map_omim_with_umls_cui.txt', 'w', encoding='utf-8')
csv_omim_cui = csv.writer(file_omim_umls_cui, delimiter='\t')
csv_omim_cui.writerow(['omim id', 'omim name', 'umls cuis', 'mondos'])

file_omim_name = open('mapping_files/disease/map_omim_with_name.txt', 'w', encoding='utf-8')
csv_omim_name = csv.writer(file_omim_name, delimiter='\t')
csv_omim_name.writerow(['omim id', 'omim name', 'mondos'])

file_not_map_orpha = open('mapping_files/disease/not_map_orpha.txt', 'w', encoding='utf-8')
csv_not_mapped_orpha = csv.writer(file_not_map_orpha, delimiter='\t')
csv_not_mapped_orpha.writerow(['orpha id', 'orpha name', 'mondos'])

file_orpha_orpha = open('mapping_files/disease/map_orpha_with_orpha.txt', 'w', encoding='utf-8')
csv_orpha_orpha = csv.writer(file_orpha_orpha, delimiter='\t')
csv_orpha_orpha.writerow(['orpha id', 'orpha name', 'mondos'])

file_orpha_name = open('mapping_files/disease/map_orpha_with_name.txt', 'w', encoding='utf-8')
csv_orpha_name = csv.writer(file_orpha_name, delimiter='\t')
csv_orpha_name.writerow(['orpha id', 'orpha name', 'mondos'])

file_not_map_omim = open('mapping_files/disease/not_map_omim.txt', 'w', encoding='utf-8')
csv_omim_not_mapped = csv.writer(file_not_map_omim, delimiter='\t')
csv_omim_not_mapped.writerow(['omim id', 'omim name'])

# counter for decipher and orphanet diseases
counter_decipher = 0
# counter for omim diseases
counter_omim = 0
## count for orphanet
counter_orpha = 0
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
    mondo = ''
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


def check_on_mapping_same_source(dictionary_of_source, counter_map_source_to_source, db_disease_names, db_disease_id,
                                 file_source_source):
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
            for db_disease_name in db_disease_names:
                mondo = mondo_with_name(db_disease_name)
                if mondo in mondos:
                    mondos = [mondo]
        dict_disease_id_to_mondos[db_disease_id] = mondos
        mondos = '|'.join(mondos)
        file_source_source.writerow([db_disease_id, db_disease_names, mondos])
        return True, counter_map_source_to_source
    else:
        return False, counter_map_source_to_source


'''
check for mapping with name
'''


def mapping_with_name(db_disease_names, db_disease_id, counter_source_with_name, file_source_name):
    # last step is name mapping
    for db_disease_name in db_disease_names:
        if db_disease_name in dict_name_to_mondo:
            counter_source_with_name += 1
            mondo = dict_name_to_mondo[db_disease_name]
            file_source_name.writerow([db_disease_id, db_disease_name, mondo])
            dict_disease_id_to_mondos[db_disease_id] = [mondo]
            return True, counter_source_with_name
    return False, counter_source_with_name


'''
not mapped disease
'''


def not_mapped_disease(counter_source_not_mapped, db_disease_id, db_disease_name, file_not_map_source):
    counter_source_not_mapped += 1
    list_not_mapped_disease_ids_to_mondo.append(db_disease_id)
    file_not_map_source.writerow([db_disease_id, db_disease_name])
    return counter_source_not_mapped


'''
check for an identifier
'''


def check_for_mapping_with_umls(db_disease_names, db_disease_id, name_in_umls, counter_source_map_with_umls_cui,
                                file_source_umls_cui):
    # get only the number
    id = db_disease_id.split(':')[1]

    # try to map with umls

    # fined mapping with use of umls cuis
    for db_disease_name in db_disease_names:
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
        file_source_umls_cui.writerow([db_disease_id, db_disease_name, cuis, mondos])
        return True, counter_source_map_with_umls_cui
    else:
        return False, counter_source_map_with_umls_cui


'''
load all disease information from neo4j in and only remember the relationships where the disease 
can be mapped to mondo with use of UMLS and DO.

'''


def map_hpo_disease_to_mondo(db_disease_id, db_disease_names, db_disease_source):
    global counter_decipher, counter_omim, counter_decipher_not_mapped
    global counter_decipher_map_with_name, counter_decipher_map_with_name_split
    global counter_decipher_map_with_mapped_umls_cui, counter_omim_not_mapped, counter_omim_map_with_omim
    global counter_omim_map_with_umls_cui, counter_omim_with_name, counter, counter_orpha, counter_orpha_with_name
    global counter_orpha_not_mapped, counter_orpha_map_with_orpha, counter_orpha_map_with_umls_cui

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
    db_disease_names = [x.lower() for x in db_disease_names]

    # depending of the source of the diseases different mapping step's are used
    if db_disease_source == 'DECIPHER':
        counter_decipher += 1
        #            print('decipher')
        #            print(counter_decipher)
        # test if name is directly in dictionary
        # else try to mapp the name but change the name so that no () appears and use the synonyms in the  name
        found_name_mapping, counter_decipher_map_with_name = mapping_with_name(db_disease_names, db_disease_id,
                                                                               counter_decipher_map_with_name,
                                                                               csv_decipher_name)
        if not found_name_mapping:
            for db_disease_name in db_disease_names:
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
                    db_disease_id, db_disease_names, mondos, db_disease_source])
            # try to map with find a umls cui for the name and mapp this id
            else:

                for db_disease_name in db_disease_names:
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
                        db_disease_id, db_disease_names, cuis, mondos, db_disease_source])
                else:
                    counter_decipher_not_mapped = not_mapped_disease(counter_decipher_not_mapped, db_disease_id,
                                                                     db_disease_names, csv_decipher_not_mapped)
                    return

    elif db_disease_source == 'OMIM':
        counter_omim += 1

        # get only the number
        id = db_disease_id.split(':')[1]

        #            print('omim')
        # test if omim id is direct in DO
        found_same_mapping, counter_omim_map_with_omim = check_on_mapping_same_source(dict_omim_to_mondo,
                                                                                      counter_omim_map_with_omim,
                                                                                      db_disease_names, db_disease_id,
                                                                                      csv_omim_omim)
        if not found_same_mapping:

            found_with_umls, counter_omim_map_with_umls_cui = check_for_mapping_with_umls(db_disease_names,
                                                                                          db_disease_id, "OMIM",
                                                                                          counter_omim_map_with_umls_cui,
                                                                                          csv_omim_cui)
            if not found_with_umls:
                mappped_with_name, counter_omim_with_name = mapping_with_name(db_disease_names, db_disease_id,
                                                                              counter_omim_with_name, csv_omim_name)
                if not mappped_with_name:
                    counter_omim_not_mapped = not_mapped_disease(counter_omim_not_mapped, db_disease_id,
                                                                 db_disease_names,
                                                                 csv_omim_not_mapped)
                    return

    elif db_disease_source == 'ORPHA':
        counter_orpha += 1
        #            print('omim')
        # test if ORPHA id is direct in Mondo
        found_same_mapping, counter_orpha_map_with_orpha = check_on_mapping_same_source(dict_orphanet_to_mondo,
                                                                                        counter_orpha_map_with_orpha,
                                                                                        db_disease_names,
                                                                                        db_disease_id, csv_orpha_orpha)
        if not found_same_mapping:
            # check if name mapps
            found_with_name, counter_orpha_with_name = mapping_with_name(db_disease_names, db_disease_id,
                                                                         counter_orpha_with_name, csv_orpha_name)
            if not found_with_name:
                # not mapped information are add to file
                counter_orpha_not_mapped = not_mapped_disease(counter_orpha_not_mapped, db_disease_id, db_disease_names,
                                                              csv_not_mapped_orpha)

    else:
        print('a different db disease source ' + db_disease_source)

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
file_disease = open('mapping_files/disease_mapped.tsv', 'w', encoding='utf-8')
csv_disease = csv.writer(file_disease, delimiter='\t')
csv_disease.writerow(['hpo_id', 'hetionet_id', 'resource'])

# cypher file for mapping and integration
cypher_file = open('cypher/cypher_disease.cypher', 'w')

# the general query start
query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/hpo/%s" As line FIELDTERMINATOR '\\t' 
    Match'''

'''
Integrate mapping connection between disease and HPOdisease and make a dictionary mondo to hpo id
'''


def integrate_mapping_of_disease_into_hetionet():
    # query for mapping disease and written into file
    query = query_start + ''' (n:HPOdisease{id: line.hpo_id}), (d:Disease{identifier:line.hetionet_id}) Set d.hpo="yes", d.resource=split(line.resource,"|") Create (d)-[:equal_to_hpo_disease]->(n);\n '''
    query = query % (path_of_directory, 'mapping_files/disease_mapped.tsv')
    cypher_file.write(query)
    # write mapping in csv file
    for hpo_id, mondos in dict_disease_id_to_mondos.items():
        for mondo in mondos:
            resources = set(dict_mondo_to_node[mondo]['resource'])
            resources.add('HPO')
            resources = sorted(resources)

            csv_disease.writerow([hpo_id, mondo, '|'.join(resources)])

            # fill mapped dictionary
            dict_mondo_to_hpo_ids[mondo].append(hpo_id)

    # query = '''Match (d:disease{identifier:"%s"}) Where exists(d.hpo) Set d.resource=d.resource+"HPO";\n '''
    # cypher_file.write(query)
    #
    # query = '''Match (d:disease{identifier:"%s"}) Where not exists(d.hpo) Set d.hpo="no";\n '''
    # cypher_file.write(query)


# dictionary of frequency of occurrence
dict_frequency = {}


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

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
