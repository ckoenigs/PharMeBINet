# -*- coding: utf-8 -*-
"""
Created on Thu May 18 09:18:08 2017

@author: Cassandra
"""
from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
import threading
import time

# encoding=utf8
reload(sys)
sys.setdefaultencoding('utf8')
'''
type name in mrconso
'''
dict_type_name_in_mrconso = {
    'SNOMEDCT_US_2016_03_01': ['SNOMEDCT_US', 'SNOMEDCT_VET'],
    "MESH": ["MSH"],
    "MEDRA": ["MDR"]
}


# class of thread
class synonymThread(threading.Thread):
    def __init__(self, threadID, name, key):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.key = key

    def run(self):
        #      print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock1.acquire()
        find_synonyms(self.key)
        #      print "Ending " + self.name
        #      print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock1.release()


# class of thread
class symptomFinderThread(threading.Thread):
    def __init__(self, threadID, name, key_cui, list_cui_with_synonyms):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.list_cui_with_synonyms = list_cui_with_synonyms
        self.key_cui = key_cui

    def run(self):
        # print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock2.acquire()
        find_symptoms(self.key_cui, self.list_cui_with_synonyms)
        #      print "Ending " + self.name
        #      print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock2.release()


# combine two list without duplication
def combin(a, b):
    combinList = a + [i for i in b if i not in a]
    # combinList= a + list(set(b)-set(a))
    return combinList


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary of all diseases in hetionet with cui as key and mondo as value
'''
cui1: mondo
'''
dict_of_all_diseases = {}

# list of all cuis of the diseases in hetionet
list_diseases_cuis = []
# list_diseases_cuis=['C0005396']


# dictionary with all mondos, which has no cuis, but xrefs
dict_mondo_to_xrefs = {}

# list of mondos which has no alternative identifier
list_mondo_without_refs = []

# dictionary with mondo as identifier and value is list of umls cuis
dict_mondo_to_umls_cuis = {}

# dictionary disease types with counter
dict_sty_counter = {}

# dictionary cui to sty
dict_cui_to_sty = {}

'''
load from hetionet all disease in and make a dictionary with the mondo and umls cui
use only the first cui, because the othere will befound with the search of the synonyms
Where n.identifier='DOID:6898' or n.identifier='DOID:0050879'
'''


def load_in_hetionet_disease_in_dictionary():
    query = '''MATCH (n:Disease)  RETURN n.identifier,n.umls_cuis , n.xrefs Limit 7000'''
    results = g.run(query)
    counter = 0
    count_cuis_double = 0
    file_types = open('cui_types_of_disease.txt', 'w')
    file_types.write('cui\tsty\n')
    for mondo, umls_cuis, xrefs, in results:
        #        print(mondo)
        #        print(umls_cuis)

        if len(umls_cuis) > 0 and not umls_cuis[0] == '':
            counter += 1

            list_umls_set_cuis = set([])
            for umls_cui in umls_cuis:
                if umls_cui == '':
                    continue
                cui = umls_cui.split(':')[1]
                list_umls_set_cuis.add(cui)

            dict_mondo_to_umls_cuis[mondo] = list(list_umls_set_cuis)
            cui = umls_cuis[0].split(':')[1]
            cur = con.cursor()
            query = ("SELECT sty FROM MRSTY WHERE cui='%s' ; ") % (cui)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for sty, in cur:
                    file_types.write(cui + '\t' + sty + '\n')
                    if sty in dict_sty_counter:
                        dict_sty_counter[sty] += 1
                    else:
                        dict_sty_counter[sty] = 1
                    if cui in dict_cui_to_sty:
                        dict_cui_to_sty[cui].add(sty)
                    else:
                        dict_cui_to_sty[cui] = set([sty])
            if not cui in dict_of_all_diseases:
                dict_of_all_diseases[cui] = [mondo]
            else:
                count_cuis_double += 1
                dict_of_all_diseases[cui].append(mondo)
        else:
            #            print('ne')
            #            print(mondo)
            #            print(xrefs)
            if xrefs[0] != '':
                dict_mondo_to_xrefs[mondo] = xrefs
            else:
                list_mondo_without_refs.append(mondo)

    print('how often a cuis is found:' + str(counter))
    print('how often a cui appears double:' + str(count_cuis_double))
    print('length of dict with cui and list of mondos:' + str(len(dict_of_all_diseases)))
    print('length of dict wit mondo and xref list:' + str(len(dict_mondo_to_xrefs)))
    print('length of disease ontology without a ref:' + str(len(list_mondo_without_refs)))

    # get umls cui with use of other external ids
    i = 0
    list_doi = dict_mondo_to_xrefs.keys()
    print(list_doi[0:5])
    j = 0
    for mondo, xrefs in dict_mondo_to_xrefs.items():
        has_found_a_cui = False
        for xref in xrefs:
            if has_found_a_cui:
                break
            splitted = xref.split(':')
            if len(splitted) == 2:
                sab = xref.split(':')[0]
                code = xref.split(':')[1]
                cur = con.cursor()
                if sab in dict_type_name_in_mrconso:

                    types = dict_type_name_in_mrconso[sab]
                    typstring = '","'.join(types)
                    query = ('Select CUI From MRCONSO Where SAB in ("%s") AND CODE= "%s" ')
                    query = query % (typstring, code)
                else:
                    if len(sab.split(',')) > 1:
                        sab = sab.split(',')[len(sab.split(',')) - 1].split("'")[1]
                    query = ('Select CUI From MRCONSO Where SAB= "%s" AND CODE= "%s" ')
                    query = query % (sab, code)
                #                    print(mondo)
                #                    print(code)
                #                    print(query)
                rows_counter = cur.execute(query)
                if rows_counter > 0:
                    for cui, in cur:
                        i += 1
                        dict_mondo_to_umls_cuis[mondo] = [cui]
                        cur = con.cursor()
                        query = ("SELECT sty FROM MRSTY WHERE cui='%s' ; ") % (cui)
                        rows_counter = cur.execute(query)
                        if rows_counter > 0:
                            for sty, in cur:
                                file_types.write(cui + '\t' + sty + '\n')
                                if sty in dict_sty_counter:
                                    dict_sty_counter[sty] += 1
                                else:
                                    dict_sty_counter[sty] = 1
                                if cui in dict_cui_to_sty:
                                    dict_cui_to_sty[cui].add(sty)
                                else:
                                    dict_cui_to_sty[cui] = set([sty])
                        if not cui is dict_of_all_diseases:
                            dict_of_all_diseases[cui] = [mondo]

                            has_found_a_cui = True
                            break
                        else:
                            dict_of_all_diseases[cui].append(mondo)
                            has_found_a_cui = True
                            break
            else:
                #                 print(xref)
                # some of the xref has a strange form and have to be changed
                xref = xref.replace("'", "")
                refs = xref.split(',')
                for ref in refs:
                    if has_found_a_cui:
                        break
                    #                    print(ref)
                    if len(ref.split(':')) == 2:
                        sab = ref.split(':')[0]
                        code = ref.split(':')[1]
                        cur = con.cursor()
                        if sab in dict_type_name_in_mrconso:

                            types = dict_type_name_in_mrconso[sab]
                            typstring = '","'.join(types)
                            query = ('Select CUI From MRCONSO Where SAB in ("%s") AND CODE= "%s" ')
                            query = query % (typstring, code)
                        else:
                            if len(sab.split(',')) > 1:
                                sab = sab.split(',')[len(sab.split(',')) - 1].split("'")[1]
                            query = ("Select CUI From MRCONSO Where SAB= '%s' AND CODE= '%s' ")
                            query = query % (sab, code)
                        #                            print(mondo)
                        #                            print(code)
                        #                            print(query)
                        #                            print('blub')
                        rows_counter = cur.execute(query)
                        if rows_counter > 0:
                            for cui, in cur:
                                i += 1
                                dict_mondo_to_umls_cuis[mondo] = [cui]
                                if not cui is dict_of_all_diseases:
                                    dict_of_all_diseases[cui] = [mondo]
                                    has_found_a_cui = True
                                    break
                                else:
                                    dict_of_all_diseases[cui].append(mondo)
                                    has_found_a_cui = True
                                    break
        j += 1
    global list_diseases_cuis
    list_diseases_cuis = dict_of_all_diseases.keys()

    print('how often a cuis is found:' + str(counter))
    print('how often a cui appears double:' + str(count_cuis_double))
    print('length of dict with cui and list of mondos:' + str(len(dict_of_all_diseases)))
    print('length of dict wit mondo and xref list:' + str(len(dict_mondo_to_xrefs)))
    print('length of disease ontology without a ref:' + str(len(list_mondo_without_refs)))
    print('length of dict with cui and list of mondos after use of xref:' + str(len(dict_of_all_diseases)))
    print(dict_sty_counter)


#    print(i)


# search for the name of a given cui in the dictionary of the MRCONSO. It take the
# prefer term if it has on else it take one possible name.
def get_name(cui):
    # list_of_names= dict_MRCONSO[cui]

    pn = False
    cur = con.cursor()
    # find the prefer term in english
    query = ("Select * From MRCONSO Where CUI = %s AND ts='P' AND stt='PF' AND ispref='Y' And LAT= 'ENG'")
    #    print(cui)
    #    query= query %(cui)
    rows_counter = cur.execute(query, (cui,))
    if rows_counter > 0:
        for name in cur:
            return name[14]
            pn = True
            break

    else:
        cur.close()
        cur = con.cursor()

        query = ("Select * From MRCONSO Where CUI = %s And LAT= 'ENG'")
        rows_counter = cur.execute(query, (cui,))
        print(cui)
        if rows_counter > 0:
            for name in cur:
                # position11 tty
                if name[12] == 'PN':
                    return name[14]
                    pn = True
                    break
            if not pn:
                for name in cur:
                    return name[14]
                    break
        else:
            cur.close()
            cur = con.cursor()
            # only names without an english name
            query = ("Select * From MRCONSO Where CUI = %s")
            rows_counter = cur.execute(query, (cui,))
            print('This %s has no english term' % (cui))
            for name in cur:
                # position11 tty
                if name[12] == 'PN':
                    return name[14]
                    pn = True
                    cur = con.cursor()
                    break
            if not pn:
                for name in cur:
                    return name[14]
                    cur = con.cursor()
    print('This %s is not in UMLS' % (cui))
    return 'is not in UMLS'


# dictionary with umls cui as key and all synonym cuis as value
dict_synonyms = {}
# list_synonyms=[['C0001973']]

# dictionary umls cui to name
dictionary_umls_cui_to_name = {}

# list of which REL we want to use to find the synonyms
list_rel = ['CHD', 'RB', 'RN', 'PAR', 'SY']

# list synonym cuis from xref
list_synonym_cuis_xref = []

# list synonym cuis from umls
list_synonym_cuis_umls = []

# dictionary of all cuis which replace the cuis which are not in UMLS
dict_cui_to_cui_not_in_umls = {}

# list of all rela of RN where key must be cui2
list_rela_rn_synonym = ['contains', 'has_precise_ingredient']

# list of all rela of RN where key must be cui2
list_rela_rb_synonym = ['contained_in', 'precise_ingredient_of']

''' 
search for all synonyms of all diseases of hetionet. 
it generate for every disease a csv file with all synonyms,with form cui1;name1;cui2;name2;rel;rela;mondo \n   
all so save the list of synonyms of a key in the list list_synonyms.
To get the information it search for every disease in mysql MRREL table for synonyms and take only
the relationships which has the right REL term. Also only by CHD the disease cui has to
be the first value and by PAR it has to be the second.  
'''


def find_synonyms(key):
    start = time.time()
    f = open('synonyms/synonyms' + key + '.csv', 'w')
    key_name = get_name(key)
    list_synonyms_cuis_from_mondo_do = set([])

    mondo_ids = dict_of_all_diseases[key]
    for mondo in mondo_ids:
        list_synonyms_cuis_from_mondo_do |= set(dict_mondo_to_umls_cuis[mondo])

    if key_name != 'is not in UMLS':
        dictionary_umls_cui_to_name[key] = key_name
        list_synonyms_cuis_from_mondo_do.add(key)
    elif len(list(list_synonyms_cuis_from_mondo_do)) > 0:
        for synonym_cui in list(list_synonyms_cuis_from_mondo_do):
            cui_name = get_name(synonym_cui)
            if cui_name != 'is not in UMLS':
                dict_cui_to_cui_not_in_umls[synonym_cui] = key
                key = synonym_cui
                dictionary_umls_cui_to_name[key] = cui_name
                break

    else:
        return

    if key in dict_cui_to_sty:
        stys = list(dict_cui_to_sty[key])
        stys = ';'.join(stys)
        f.write(stys + ';')
    f.write(key_name + '\n')
    f.write('cui1;name1;cui2;name2;rel;rela;mondo \n')
    # key='C0024117'
    # if key=='C0005396':
    #     print('blub')

    list_synonym_cuis_umls.append(key)
    synonym = set([])
    # synonym.add(key)
    cur = con.cursor()
    # print(key)
    query = ("SELECT cui1, rel, cui2,rela FROM MRREL WHERE (cui2 = %s OR cui1 = %s) AND rel in (%s) ; ")

    in_rel = ','.join(map(lambda x: '%s', list_rel))
    query = query % ('%s', '%s', in_rel)
    # print(query)
    allValues = [key, key]
    allValues.extend(list_rel)
    # print(allValues)
    # query=("SELECT cui1, rel, cui2,rela FROM MRREL WHERE cui2 = 'C1800706';")
    cur.execute(query, tuple(allValues))
    # cur.execute(query)
    # print('\t Query anfrage: %.4f seconds' % (time.time() - start))
    start = time.time()

    # go through all results and add them to the synonoyms if they fullfill the condition
    for (cui1, rel, cui2, rela) in cur:

        # find the name for cui1
        if cui1 in dictionary_umls_cui_to_name:
            name1 = dictionary_umls_cui_to_name[cui1]
        else:
            name1 = get_name(cui1)
            dictionary_umls_cui_to_name[cui1] = name1

        # find the name of the cui2
        if cui2 in dictionary_umls_cui_to_name:
            name2 = dictionary_umls_cui_to_name[cui2]
        else:
            name2 = get_name(cui2)
            dictionary_umls_cui_to_name[cui2] = name2

        # get the mondo of the disease
        # if cui1 in dict_of_all_diseases:
        #     mondo = dict_of_all_diseases[cui1]
        #
        # else:
        #     mondo = dict_of_all_diseases[cui2]
        mondo = '|'.join(mondo_ids)

        is_synonym = False

        if cui1 == key:
            synonym_cui = cui2
            if rel in ['SY', 'CHD'] or (
                    rel == 'RN' and not rela in list_rela_rn_synonym and not rela == 'has_alternative') or (
                    rel == 'RB' and rela in list_rela_rb_synonym) or (rel == 'RL' and rela == 'mapped_to'):
                # synonym.add(cui2)
                is_synonym = True
        else:
            synonym_cui = cui1

            if (rel == 'RB' and not rela in list_rela_rb_synonym and rela != 'alternative_of') or rel in ['PAR',
                                                                                                          'SY'] or (
                    rel == 'RN' and rela in list_rela_rn_synonym) or (rel == 'RL' and rela == 'mapped_from'):
                # synonym.add(cui1)
                is_synonym = True

        if is_synonym and synonym_cui not in synonym:
            synonym.add(synonym_cui)
            if rela is None:
                text = cui1 + ';' + name1 + ';' + cui2 + ';' + name2 + ';' + rel + ';;' + mondo + ' \n'
            else:
                text = cui1 + ';' + name1 + ';' + cui2 + ';' + name2 + ';' + rel + ';' + rela + ';' + mondo + ' \n'
            f.write(text)

    cur.close()

    # print('\tAuslesen aller rows im cursor: %.4f seconds' % (time.time() - start))
    list_synonym_cuis_xref.append(key)
    # only the new synonym cuis from xref
    list_synonyms_cuis_from_mondo_do.difference_update(synonym)
    if key in list_synonyms_cuis_from_mondo_do:
        list_synonyms_cuis_from_mondo_do.remove(key)
    # combine all cuis
    synonym = synonym | list_synonyms_cuis_from_mondo_do
    if key in dictionary_umls_cui_to_name:
        name_key = dictionary_umls_cui_to_name[key]
    else:
        name_key = get_name(key)
        dictionary_umls_cui_to_name[key] = name_key
    # add the xref cuis to the file
    for synonym_cui in list(list_synonyms_cuis_from_mondo_do):
        # find the name for cui1
        if synonym_cui in dictionary_umls_cui_to_name:
            name = dictionary_umls_cui_to_name[synonym_cui]
        else:
            name = get_name(synonym_cui)
            dictionary_umls_cui_to_name[synonym_cui] = name
        mondos = '|'.join(mondo_ids)
        text = synonym_cui + ';' + name + ';' + key + ';' + name_key + ';;;' + mondos + '\n'
        f.write(text)
    f.close()

    dict_synonyms[key] = synonym


# list of which RELA we want to use to find the symptomes
# list_rela=['associated_with','associated_disease','associated_finding_of', 'clinically_associated_with','diagnosed_by','diagnoses', 'diagnostic_criteria_of', 'has_sign_or_symptom', 'sign_or_symptom_of' ]

# dictionary with disease cui: [all relationship]
dict_possible_symptomes = {}

# dictionary with disease cui: [symptomes]
dict_disease_symptomes = {}

# dictionary with disease cui : dictionary symptome cui: rel, rela, sab
dict_all_info_rel = {}

# dictionary with all sympotms cuis and the in formation about them
dict_symptoms_cuis = {}

# list of all rel where a possible symptom appears
list_rel_of_possible_symptoms = set([])

# list of all rel where a possible symptom appears and values are cuis where they appeared
dict_rel_of_possible_symptoms_to_cuis = {}

# list of all rela where a possible symptom appears
list_rela_of_possible_symptoms = set([])

# list of all rela where a possible symptom appears and values are cuis where they appeared
dict_rela_of_possible_symptoms_to_cuis = {}

# dictionary for the files
# dict_files_with_path={}

# list OF REL NOT FOR SYMPTOMS
list_not_rel_symptoms = ['AQ', 'QB', 'SIB', 'SY']

# good rela from RQ where symptom can be cui 1 or 2
list_rela_rq_symptoms = [None, 'clinically_similar', 'inverse_isa', 'mapped_from', 'classified_as',
                         'primary_mapped_from', 'mapped_from', 'classifies', 'primary_mapped_to']

# all rela rq for symptoms where the symptom is cui1
list_rela_rq_symptoms_cui1 = ['inverse_isa', 'mapped_from', 'classified_as', 'primary_mapped_from']
# all rela rq for symptoms where the symptom is cui2
list_rela_rq_symptoms_cui2 = ['mapped_from', 'classifies', 'primary_mapped_to']

# list rela of RO for symptoms
list_rela_ro_symptoms = ['sign_or_symptom_of', 'may_be_finding_of_disease', 'mapped_from', 'mapped_to',
                         'is_associated_disease_of', 'has_sign_or_symptom', 'has_location', 'has_finding_site',
                         'has_associated_finding', 'disease_may_have_finding', 'disease_has_finding',
                         'characterized_by', 'characterizes', 'associated_with', 'associated_finding_of',
                         'associated_finding_of_excluded', ' associated_finding_of_possibly_included',
                         'associated_disease']
# list all rela of ro where cui 1 is symptom
list_rela_ro_symptoms_cui1=['mapped_from','is_associated_disease_of','has_sign_or_symptom','has_associated_finding','disease_may_have_finding','disease_has_finding','characterizes']

# list all rela of ro where cui 2 is symptom
list_rela_ro_symptoms_cui2=['sign_or_symptom_of','may_be_finding_of_disease','mapped_to','has_location' 'has_finding_site','characterized_by','associated_with','associated_finding_of','associated_finding_of_excluded', ' associated_finding_of_possibly_included']

'''
search for symptomes for every diseas.
For every diseas cui and all his synonyms it search in mysql MRREL for all 
relationships. It save for every disease all possible symptomes in one file and 
all fixed symptomes in another file. Also all possible symptome cuis will be in a 
list and at to the dictionary dict_possible_symptomes and all fixed symptomes will 
be in the dictionary dict_disease_symptomes.
'''


def find_symptoms(key, synonym):
    synonym = list(synonym)
    #    print(synonym)
    synonym.append(key)

    # print(key)
    f = open('symptomes/all_relation_' + key + '.csv', 'w')
    name_key = dictionary_umls_cui_to_name[key]
    if key in dict_cui_to_cui_not_in_umls:
        mondos = dict_of_all_diseases[dict_cui_to_cui_not_in_umls[key]]
    else:
        mondos = dict_of_all_diseases[key]
    mondos_string = '|'.join(mondos)
    f.write(name_key + ';' + mondos_string + '\n')
    f.write('cui1;name1;cui2;name2;rel;rela \n')
    g = open('symptomes/ready/symptoms_' + key + '.csv', 'w')
    g.write(name_key + ';' + mondos_string + '\n')
    g.write('cui;name;rel;rela;sab; \n')

    symptomes = set()
    cur = con.cursor(mdb.cursors.SSCursor)
    # query = (
    #     "SELECT cui1, rel, cui2,rela, sab FROM MRREL WHERE (cui2 in (%s) OR cui1 in (%s)) and (rela<>'inverse_isa' or rela IS NULL); ")
    query = (
        "SELECT cui1, rel, cui2,rela, sab FROM MRREL WHERE (cui2 in (%s) XOR cui1 in (%s)) and rel not in (%s); ")
    in_cui = ','.join(map(lambda x: '%s', synonym))
    not_rel = ','.join(map(lambda x: '%s', list_not_rel_symptoms))
    # in_rel= ','.join(map(lambda x: '%s', list_rel ))
    # in_rela= ','.join(map(lambda x: '%s', list_rela ))
    query = query % (in_cui, in_cui, not_rel)
    # print(query)
    allValues = []
    allValues.extend(synonym)
    allValues.extend(synonym)
    allValues.extend(list_not_rel_symptoms)
    # allValues.extend(list_rel)
    # allValues.extend(list_rela)

    # print(len(list_all_possible_symtomes_from_filter))

    count_finding = 0
    count_symptom = 0

    rows_counter = cur.execute(query, tuple(allValues))
    start = time.time()

    for (cui1, rel, cui2, rela, sab,) in cur:
        #            print('huhu')

        if cui1 in dictionary_umls_cui_to_name:
            name1 = dictionary_umls_cui_to_name[cui1]
        else:
            #            name1=get_name(cui1)
            name1 = 'such selber'
        if cui2 in dictionary_umls_cui_to_name:
            name2 = dictionary_umls_cui_to_name[cui2]
        else:
            #            name2=get_name(cui2)
            name2 = 'such selber'
        # print('------------------------------------------------------------------------------------------')
        disease_cui1 = False
        if not cui1 in synonym:
            cui = cui1
            name = name1
            synonym_cui = cui2
        else:
            cui = cui2
            name = name2
            synonym_cui = cui1
            disease_cui1 = True

        if rela == None:
            text = cui1 + ';' + name1 + ';' + cui2 + ';' + name2 + ';' + rel + ';;' + sab + ' \n'
            information = [rel, '', sab]
            rela = ''
        #            if from type
        #                if dict_all_possible_symptoms_from_filter[cui[0]].find('Finding')!=-1:
        #                    if not rel in ['RQ','RO'] and not rela in ['inverse_isa','isa'] :
        #
        #                        if not key in dict_all_info_rel:dict_all_possible_symptoms_from_filter
        #                            dict_all_info_rel[key]={cui[0]: information}
        #                        elif not cui[0] in dict_all_info_rel[key]:
        #                            dict_all_info_rel[key][cui[0]]=information
        # print(cui)
        # print(rel)
        # print(rela)
        # print(dict_all_possible_symptoms_from_filter[cui[0]])
        # print(dict_all_info_rel[key][cui[0]])
        #                        symptomes=combin(symptomes,cui)
        #                        count_finding+=1
        #                        good=True
        #                else:
        # print(cui)
        else:
            text = cui1 + ';' + name1 + ';' + cui2 + ';' + name2 + ';' + rel + ';' + rela + ';' + sab + ' \n'
            information = [rel, rela, sab]

        #            if not key in dict_all_info_rel:
        #                dict_all_info_rel[key]={cui[0]: information}
        #            elif not cui[0] in dict_all_info_rel[key]:
        #                dict_all_info_rel[key][cui[0]]=information

        # print(information)

        #            print(text)
        f.write(text)
        good = False
        # print(rel, rela)
        if cui in list_all_possible_symtomes_from_filter:

            if rel == 'PAR' and disease_cui1:
                continue
            elif rel == 'CHD' and not disease_cui1:
                continue
            elif rel == 'RN' and rela in ['mapped_to', 'was_a', 'has_alternative']:
                continue
            elif rel == 'RB' and rela in ['mapped_from', 'inverse_was_a', 'alternative_of']:
                continue
            elif rel == 'RL' and dict_all_possible_symptoms_from_filter[cui] != 'Sign or Symptom':
                continue
            elif rel == 'RQ' and (
                    rela not in list_rela_rq_symptoms or (rela in list_rela_rq_symptoms_cui1 and disease_cui1) or (
                    rela in list_rela_rq_symptoms_cui2 and not disease_cui1)):
                continue
            elif rel == 'RO' and (
                    rela not in list_rela_ro_symptoms or (rela in list_rela_ro_symptoms_cui1 and disease_cui1) or (
                    rela in list_rela_ro_symptoms_cui2 and not disease_cui1)):
                continue

            if not key in dict_all_info_rel:
                dict_all_info_rel[key] = {cui: information}
            elif not cui in dict_all_info_rel[key]:
                dict_all_info_rel[key][cui] = information
                # print(rel)
                # print(rela)
                # print(dict_all_possible_symptoms_from_filter[cui[0]])

            #                symptomes.add(cui)
            #            symptomes=combin(symptomes,cui)
            count_symptom += 1

            if not cui in symptomes:
                list_rel_of_possible_symptoms.add(rel)
                if rel in dict_rel_of_possible_symptoms_to_cuis:
                    dict_rel_of_possible_symptoms_to_cuis[rel].add(key)
                else:
                    dict_rel_of_possible_symptoms_to_cuis[rel] = set([key])
                if rela in dict_rela_of_possible_symptoms_to_cuis:
                    dict_rela_of_possible_symptoms_to_cuis[rela].add(key)
                else:
                    dict_rela_of_possible_symptoms_to_cuis[rela] = set([key])
                list_rela_of_possible_symptoms.add(rela)
                text = cui + ';' + name + ';' + rel + ';' + rela + ';' + sab + ';' + \
                       dict_all_possible_symptoms_from_filter[cui] + ' \n'
                #                    print(text)
                g.write(text)
                symptomes.add(cui)

    print('\t Query anfrage: %.4f seconds' % (time.time() - start))
    dict_disease_symptomes[key] = list(symptomes)
    cur.close()
    f.close()


#        print(len(symptomes))
#        print(len(dict_disease_symptomes))
#        print(count_finding)
#        print(count_symptom)


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

    #    else:
    #        cuis=search_for_synonyms_cuis(cui)
    #        cur = con.cursor()
    #        query=("Select CODE From MRCONSO Where SAB= 'MSH' AND CUI in ('%s')")
    #        cuis="','".join(cuis)
    #        query= query %(cuis)
    #        rows_counter=cur.execute(query)
    #        if rows_counter>0:
    #            codes=[]
    #            for code, in cur:
    #                codes.append(code)
    #
    #            codes=list(set(codes))
    #            return codes
    else:
        return []


#            sys.exit()

# dictionary symptom umls cui to mesh id or umls cui, if the mesh id or umls cui is already integrated into hetionet
dict_umls_cui_to_mesh_or_umls_cui = {}

'''
integrate the symptoms into Hetionet
'''


def integrate_symptoms_into_hetionet():
    counter_new_symptoms = 0
    counter_already_in_hetionet_symptoms = 0
    for symptom_cui, name in dict_symptoms_cuis.items():
        mesh_cui_ids = cui_to_mesh(symptom_cui)
        mesh_cui_ids.append(symptom_cui)
        query = '''MATCH (n:Symptom) Where n.identifier in ['%s'] RETURN n '''
        #                    print(mesh_cui_ids)
        mesh_cui_string = "','".join(mesh_cui_ids)
        query = query % (mesh_cui_string)
        is_their = g.run(query)
        first_entry = is_their.evaluate()
        name = name.replace('"', '')

        if first_entry == None:
            url = 'http://identifiers.org/umls/' + symptom_cui
            query = '''
            Create (s:Symptom{identifier:"%s",type:'cui',license:'UMLS licence', name:"%s", resource:['UMLS'], source:'UMLS', url:"%s", hetionet:'no', do:'no', hpo:'no', umls:'yes'});     '''
            query = query % (symptom_cui, name, url)
            counter_new_symptoms += 1
        else:
            mesh_or_cui = first_entry['identifier']
            resource = first_entry['resource'] if 'resource' in first_entry else []
            resource.append("UMLS")
            resource = list(set(resource))
            string_resource = '","'.join(resource)
            query = '''MATCH (s:Symptom{identifier:"%s"}) 
                Set   s.umls='yes', s.cui="%s", s.resource=["%s"] '''
            query = query % (mesh_or_cui, symptom_cui, string_resource)
            dict_umls_cui_to_mesh_or_umls_cui[symptom_cui] = mesh_or_cui
            counter_already_in_hetionet_symptoms += 1
        g.run(query)

    query = '''MATCH (s:Symptom) Where not exists(s.umls) Set s.umls='no' '''
    g.run(query)
    print('number of new symptoms:' + str(counter_new_symptoms))
    print('number of symptoms which are already in hetionet:' + str(counter_already_in_hetionet_symptoms))


'''
check if possible symptom cui_to_meshes are symptomes and append them to dict_disease_symptomes
'''


def generate_cypher_file_for_relationships():
    counter_new_connection = 0
    counter_connection_already_in_hetionet = 0
    i = 1
    h = open('intigrate_symptoms_and_relationships_' + str(i) + '.cypher', 'w')
    h.write('begin \n')
    i += 1
    # counter of connection queries
    counter_connection = 0
    # number of queries in on commit block
    constrain_number = 20000
    # number of quereies in on cypher file
    creation_max = 500000
    for cui, symptoms in dict_disease_symptomes.items():
        mondo_ids = dict_of_all_diseases[cui]
        for mondo in mondo_ids:
            for symptom in symptoms:

                if not symptom in dict_umls_cui_to_mesh_or_umls_cui:
                    query = '''MATCH (n:Disease{identifier:"%s"}), (s:Symptom{identifier:"%s"}) 
                    Set n.umls='yes'
                    Create (n)-[:PRESENTS_DpS{license:'UMLS ',unbiased:'false',source:'UMLS', resource:['UMLS'],hetionet:'no',do:'no', hpo:'no', umls:'yes'}]->(s); \n'''
                    query = query % (mondo, symptom)
                    counter_new_connection += 1
                else:
                    mesh_or_cui = dict_umls_cui_to_mesh_or_umls_cui[symptom]
                    query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"}) Return l  '''
                    query = query % (mondo, mesh_or_cui)
                    result = g.run(query)
                    first_entry = result.evaluate()
                    if first_entry == None:
                        query = '''MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"}) 
                        Set n.umls='yes', 
                        Create (n)-[:PRESENTS_DpS{license:'UMLS',unbiased:'false',source:'UMLS',resource:['UMLS'],hetionet:'no',do:'no', hpo:'no', umls:'yes'}]->(s); \n'''
                        query = query % (mondo, mesh_or_cui)
                        counter_new_connection += 1

                    else:
                        resource = first_entry['resource'] if 'resource' in first_entry else []
                        resource.append("UMLS")
                        resource = list(set(resource))
                        string_resource = '","'.join(resource)
                        query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
                        Set l.umls='yes', n.umls='yes', l.resource=["%s"] ; \n'''

                        query = query % (mondo, mesh_or_cui, string_resource)
                        counter_connection_already_in_hetionet += 1

                counter_connection += 1
                h.write(query)
                if counter_connection % constrain_number == 0:
                    h.write('commit \n')
                    if counter_connection % creation_max == 0:
                        h.close()
                        h = open('cypher/map_connection_of_ctd_in_hetionet_' + str(i) + '.cypher', 'w')
                        h.write('begin \n')
                        i += 1
                    else:
                        h.write('begin \n')
    h.write('commit \n begin \n')
    query = '''MATCH (n:Disease)-[l:PRESENTS_DpS]->(s:Symptom}) Where not exists(l.umls) Set l.umls='no'; \n  '''
    h.write(query)
    h.write('commit')

    print('number of new connection in Hetionet:' + str(counter_new_connection))
    print('number of already integrated connection in Hetionet:' + str(counter_connection_already_in_hetionet))
    print('all connection:' + str(counter_connection))


# all possible symptomes from the whole ulms database after the first filter
# cui: [name , semantic type]
dict_symptomes_filter_one = {}

# list of word that arent't use to be a symptome for the first filter
list_words_that_arenT_allowed = ['(disorder)', '(diagnosis)', 'history of', 'fh:', 'family history', 'signs of',
                                 'symptoms', 'history']

# boolean if it run through the function filter_one_find_symptomes()
run_first_filter = False

'''
The first filter to find symptoms in UMLS.
Search in mysql MRSTY for cui which has the semantic type 'Sign or Symptom',
'Mental or Behavioral Dysfunction', 'Finding', 'Mental Process', 'Social Behavior',
'Individual Behavior', 'Injury or Poisoning '.
All cuis will be save in the file all_possible_symptomes.txt. All result will be 
filter with the list list_words_that_arenT_allowed. All that pass this filter will 
be save in filter_possible_symptomes.txt.
'''


def filter_one_find_symptomes():
    cur = con.cursor()
    query = ("SELECT cui, sty FROM MRSTY WHERE sty in ('Sign or Symptom', 'Finding' ); ")
    # cur.execute("SELECT * FROM mrsty WHERE sty in ; ")
    # cur.execute(query, ("('Sign or Symptom','Mental or Behavioral Dysfunction', 'Finding', 'Mental Process', 'Social Behavior','Individual Behavior', 'Injury or Poisoning ' )"))
    cur.execute(query)
    # rows = cur.fetchall()
    f = open('all_possible_symptomes.txt', 'w')
    g = open('filter_possible_symptomes.txt', 'w')
    f.write('cui;name;sty \n')
    g.write('cui;name;sty \n')
    # for row in rows:
    for (cui, sty) in cur:
        # print(cui)
        if cui in dictionary_umls_cui_to_name:
            name = dictionary_umls_cui_to_name[cui]
        else:
            name = get_name(cui)
            dictionary_umls_cui_to_name[cui] = name
        # print(name)
        name = name.replace(';', ',')
        text = cui + ';' + name + ';' + sty + ' \n'
        f.write(text)
        bad_in = False
        for bad_word in list_words_that_arenT_allowed:
            lowerName = name.lower()
            if lowerName.find(bad_word) != -1:
                bad_in = True
                break
        if bad_in == False:
            dict_symptomes_filter_one[cui] = [name, sty]
            g.write(text)
    f.close()
    g.close()
    global run_first_filter
    run_first_filter = True


# list of word that arent't use to be a symptome for the second filter
list_words_that_arenT_allowed_second = ['dna', 'pap smear', 'pap-smear', 'biopsy', 'x-ray', 'mammogram',
                                        'echocardiography', 'echocardiogram', 'ekg', 'mri', 'electrocardiogram',
                                        'electroretinogram', 'electrodiathermy', 'electroretinographic',
                                        'electrocardiographic',
                                        'ultrasound', 'ecg', 'magnetic resonance', 'microscopy', 'orthopedic']

'''
It filter the result of the first filter with another list of words.
It go through all possible symptomes and look if it has a word from the list in it
if not it will be save in the file filter_2_possible_symptomes.txt.
'''


def filter_second_find_symptomes():
    g = open('filter_2_possible_symptomes.txt', 'w')
    g.write('cui;name;sty \n')
    if run_first_filter == True:
        for key, values in dict_symptomes_filter_one.items():
            name = values[0].lower()
            bad_in = False
            for bad_word in list_words_that_arenT_allowed_second:
                if name.find(bad_word) != -1:
                    bad_in = True
                    break
            if bad_in == False:
                text = key + ';' + name + ';' + values[1] + ' \n'
                g.write(text)
    else:
        f = open('filter_possible_symptomes.txt', 'r')
        for line in f:
            splitted = line.split(';')
            cui = splitted[0]
            # print(cui)
            bigName = splitted[1]
            sty = splitted[2]
            bad_in = False
            name = bigName.lower()
            for bad_word in list_words_that_arenT_allowed_second:
                if name.find(bad_word) != -1:
                    bad_in = True
                    break
            if bad_in == False:
                text = cui + ';' + name + ';' + sty
                g.write(text)
        f.close()
    g.close()


# list of word that arent't use to be a symptome for the second filter
# not seen and normal are new !!!!!!!!!!!!!
list_words_that_arenT_allowed_third = ['length', 'collision', 'born in', 'liveborn', 'year',
                                       'artificial skin', 'dental filling', 'barium enema',
                                       'military operations', 'hygiene', 'caused by', 'not seen']

'''
It filter the result of the first filter with another list of words.
It go through all possible symptomes and look if it has a word from the list in it
if not it will be save in the file filter_2_possible_symptomes.txt.
'''


def filter_third_find_symptomes():
    f = open('filter_2_possible_symptomes.txt', 'r')
    g = open('filter_3_possible_symptomes.txt', 'w')
    for line in f:
        splitted = line.split(';')
        cui = splitted[0];
        # print(cui)
        bigName = splitted[1]
        sty = splitted[2]
        bad_in = False
        name = bigName.lower()
        for bad_word in list_words_that_arenT_allowed_third:
            if name.find(bad_word) != -1:
                bad_in = True
                break
        if name.find('normal') != -1 and name.find('abnormal') == -1:
            bad_in = True
        if bad_in == False:
            text = cui + ';' + name + ';' + sty
            g.write(text)
    f.close()
    g.close()


# is all list with all symptomes after the filters
list_all_possible_symtomes_from_filter = set()

dict_all_possible_symptoms_from_filter = {}

'''
#go through the filtered file and save all cuis in the list 
#list_all_possible_symtomes_from_filter.
#file: 
    0:cui
    1:name
    2: semantic type (sty)
'''


def all_possible_symptomes_from_filter(filter_file):
    f = open(filter_file)
    for line in f:
        splitted = line.split(';')
        cui = splitted[0]
        name = splitted[1]
        sty = splitted[2]
        if not cui in dictionary_umls_cui_to_name:
            dictionary_umls_cui_to_name[cui] = name
        list_all_possible_symtomes_from_filter.add(cui)
        dict_all_possible_symptoms_from_filter[cui] = sty.split('\n')[0]


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print(get_name('C0005396'))

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in cui diseases')

    load_in_hetionet_disease_in_dictionary()

    # sys.exit()

    print('##########################################################################')
    #
    #    print(datetime.datetime.utcnow())
    #    print('load all information of from conso')
    #    #get_names()
    #    load_in_MRCONSO()
    # print(list_conso_name)
    # print(dict_MRCONSO)
    i = 0
    #    for key,value in dict_MRCONSO.items():
    #        print(key,value)
    #        i+=1
    #        if i>10:
    #            break
    #    print('##########################################################################')
    #
    #    print(datetime.datetime.utcnow())
    #    print('generate contraindication file')
    #    find_contraindication()#
    #
    #    print('##########################################################################')
    #
    #    print(datetime.datetime.utcnow())
    #    print('generate induces file')
    #    find_induces()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('find synonyms for the diseases')

    # create a lock, is used to synchronized threads
    global threadLock1
    threadLock1 = threading.Lock()

    # all threads
    threads_synonyms = []

    thread_id = 1

    for key in list_diseases_cuis:
        # create thread
        thread = synonymThread(thread_id, 'thread_' + str(thread_id), key)
        # start thread
        thread.start()
        # add to list
        threads_synonyms.append(thread)
        # increase thread id
        thread_id += 1

    # wait for all threads
    for t in threads_synonyms:
        t.join()

    # sys.exit()
    # print(list_diseases_cuis)
    # print(list_synonyms)
    print('Number of synonym cuis with umls:' + str(len(list_synonym_cuis_umls)))

    print('Number of synonym cuis with xref:' + str(len(list_synonym_cuis_xref)))

    # print(dict_possible_symptomes)
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('first filter of a list of all possible symptoms')
    filter_one_find_symptomes()
    # i = 0

    #    for key,value in dict_symptomes_filter_one.items():
    #        print(key,value)
    #        i+=1
    #        if i>10:
    #            break
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('second filter of a list of all possible symptoms')
    filter_second_find_symptomes()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('third filter of a list of all possible symptoms')
    filter_third_find_symptomes()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in filter file to get cui from possible symptomes')
    all_possible_symptomes_from_filter('filter_3_possible_symptomes.txt')

    print('##########################################################################')

    # sys.exit()

    print(datetime.datetime.utcnow())
    print('find symptoms for every diseases')

    # create a lock, is used to synchronized threads
    global threadLock2
    threadLock2 = threading.Lock()

    # all threads
    threads = []

    thread_id = 1

    print('how many diseases with synonyms:' + str(len(dict_synonyms)))

    for key, synonyms in dict_synonyms.items():
        # create thread
        thread = symptomFinderThread(thread_id, 'thread_' + str(thread_id), key, synonyms)
        # start thread
        thread.start()
        # add to list
        threads.append(thread)
        # increase thread id
        thread_id += 1

    # wait for all threads
    for t in threads:
        t.join()

    print(list(list_rel_of_possible_symptoms))
    print('###########################################################################################')

    for rel, list_set_cuis in dict_rel_of_possible_symptoms_to_cuis.items():
        file_rel = open('rel/' + rel + '.txt', 'w')
        file_rel.write('\n'.join(list(list_set_cuis)) + '\n')

    print('rela')

    print(list(list_rela_of_possible_symptoms))
    print('###########################################################################################')

    for rela, list_set_cuis in dict_rela_of_possible_symptoms_to_cuis.items():
        file_rela = open('rel/rela/' + rela + '.txt', 'w')
        file_rela.write('\n'.join(list(list_set_cuis)) + '\n')

    #    find_symptoms()

    #    print('##########################################################################')
    #
    #    print(datetime.datetime.utcnow())
    #    print('get all symptoms for every diseases')
    #    generate_file_for_symptoms()

    #    print('##########################################################################')
    #
    #    print('get all rel')
    #    print(datetime.datetime.utcnow())
    # all_rel_in_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate into symptoms into hetionet')

    #    integrate_symptoms_into_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('create cypher file for connections')

    #    generate_cypher_file_for_relationships()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()

# d=[[1,2],[2,3]]
# c=list(map(lambda x: x[0]+4,d))
# c=list(map(lambda x: x[0]+4 if x[1]=='3' else None,d))
