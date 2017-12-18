# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 13:51:12 2017

@author: ckoenigs
"""

import datetime
import MySQLdb as mdb

# list of which REL we want to use to find the synonyms
list_rel = ['CHD', 'RB', 'RN', 'PAR', 'SY', 'RL']
# list of rela which are not aloud
list_rela = ['inverse_isa']
'''
create connection to mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')


# list of which REL we want to use to find the synonyms
list_rel = ['CHD', 'RB', 'RN', 'PAR', 'SY', 'RL']
# list of rela which are not aloud
list_rela = ['inverse_isa']

'''
function that search for a list of cuis synonym cuis 
'''


def search_for_synonyms_cuis(cuis):
    create_connection_with_neo4j_mysql()
    cur = con.cursor()
    #    print(cuis)
    # print(key)
    query = ("SELECT cui1, rel, cui2,rela FROM MRREL WHERE (cui2 In (%s) OR cui1 In (%s)) AND rel in (%s) ; ")
    in_cuis = ','.join(map(lambda x: '%s', cuis))
    in_rel = ','.join(map(lambda x: '%s', list_rel))
    query = query % (in_cuis, in_cuis, in_rel)

    allValues = []
    allValues.extend(cuis)
    allValues.extend(cuis)
    allValues.extend(list_rel)
    cur.execute(query, tuple(allValues))

    new_cuis_to_map = []
    for (cui1, rel, cui2, rela) in cur:
        if cui1 in cuis:
            if rel in ['RN', 'SY', 'RL']:
                new_cuis_to_map.append(cui2)
            elif rel == 'CHD' and rela != 'isa':
                new_cuis_to_map.append(cui2)
            elif rel == 'PAR' and rela == 'inverse_isa':
                new_cuis_to_map.append(cui2)
        else:
            if rel == 'RB' or (rel == 'PAR' and rela != 'inverse_isa') or (rel == 'CHD' and rela == 'isa'):
                new_cuis_to_map.append(cui1)

    new_cuis_to_map = list(set(new_cuis_to_map))
    return new_cuis_to_map
