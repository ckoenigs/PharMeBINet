# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
import threading
import types


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary monarch DO to information: name
dict_monDO_info = {}

# dictionary external ids to monDO id
dict_external_ids_monDO = {}

# dict of xrefs from monDO which has multiple monDO IDs with counter
dict_source_mapped_to_multiple_monDOs = {}

'''
Load MonDO disease in dictionary
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:MonDOdisease) RETURN n '''
    results = g.run(query)
    for disease, in results:
        monDo_id = disease['id']
        dict_monDO_info[monDo_id] = [disease['name']]
        xrefs = disease['xref'] if 'xref' in disease else ''
        for external_id in xrefs.split('|'):
            external_id = external_id.split(' ')[0]
            if external_id == '':
                continue
            if external_id in dict_external_ids_monDO:
                if external_id.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                    dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] = 1
                else:
                    dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] += 1
                # print(external_id)
                dict_external_ids_monDO[external_id].append(monDo_id)
                # print(dict_external_ids_monDO[external_id])
            else:
                dict_external_ids_monDO[external_id] = [monDo_id]
    print(dict_source_mapped_to_multiple_monDOs)


# dictionary disease ontology to external ids
dict_DO_to_xref = {}

# dictionary do to indormation: name
dict_DO_to_info = {}

'''
Load in all disease ontology ids with external identifier and alternative id
'''


def load_in_all_DO_in_dictionary():
    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for disease, in results:
        Do_id = disease['identifier']
        dict_DO_to_info[Do_id] = [disease['name']]
        alternative_id = disease['alternateIds']
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        xrefs = xrefs[0].split(',')
        xrefs.extend(alternative_id)
        dict_DO_to_xref[Do_id] = xrefs

    print('Number of DOIDs:' + str(len(dict_DO_to_xref)))


# dictionary monDO to DOIDs
dict_monDo_to_DO = {}

# dictionary monDO to DOIDs with only doid mapping
dict_monDo_to_DO_only_doid = {}

# dictionary Do to monDos
dict_DO_to_monDOs = {}

# dictionary Do to monDos
dict_DO_to_monDOs_only_DO = {}

# list of not mapped doids
list_of_not_mapped_doids = []

'''
Go through all DOIDs and check if the DOID or the external IDs are in the xrefs-monDO dictionary and generate mapping
'''


def map_DO_to_monDO_with_DO_and_xrefs():
    not_direct_name_matching_file = open('not_direct_name_matching_file.tsv','w')
    not_direct_name_matching_file.write('monDO \t DOID \t name monDO \t name DOID \n')
    counter_name_not_matching = 0
    for doid, xrefs in dict_DO_to_xref.items():
        if doid in dict_external_ids_monDO:

            for monDO in dict_external_ids_monDO[doid]:
                monDOname = dict_monDO_info[monDO][0].lower().split(' (')[0]
                do_name= dict_DO_to_info[doid][0].lower().replace("'",'')
                if monDOname != do_name :
                    counter_name_not_matching += 1
                    not_direct_name_matching_file.write(
                        monDO + '\t' + doid + '\t' + dict_monDO_info[monDO][0] + '\t' + dict_DO_to_info[doid][0] + '\n')
                    # print(monDO)
                    # print(doid)
                    # print(dict_monDO_info[monDO][0])
                    # print(dict_DO_to_info[doid][0])
                if monDO in dict_monDo_to_DO:
                    dict_monDo_to_DO[monDO].add(doid)
                    if monDO in dict_monDo_to_DO_only_doid:
                        dict_monDo_to_DO_only_doid[monDO].add(doid)
                    else:
                        dict_monDo_to_DO_only_doid[monDO] = set([doid])
                else:
                    dict_monDo_to_DO[monDO] = set([doid])
                    dict_monDo_to_DO_only_doid[monDO] = set([doid])

                if doid in dict_DO_to_monDOs:
                    dict_DO_to_monDOs[doid].add(monDO)
                    dict_DO_to_monDOs_only_DO[doid].add(monDO)
                else:
                    dict_DO_to_monDOs[doid] = set([monDO])
                    dict_DO_to_monDOs_only_DO[doid] = set([monDO])
        else:
            list_of_not_mapped_doids.append(doid)
        for xref in xrefs:
            xref = xref.replace("'", "")
            if xref in dict_external_ids_monDO:
                for monDO in dict_external_ids_monDO[xref]:
                    if monDO in dict_monDo_to_DO:
                        dict_monDo_to_DO[monDO].add(doid)
                    else:
                        dict_monDo_to_DO[monDO] = set([doid])
                    if doid in dict_DO_to_monDOs:
                        # if monDO not in dict_DO_to_monDOs[doid]:
                        # print(xref)
                        dict_DO_to_monDOs[doid].add(monDO)
                    else:
                        dict_DO_to_monDOs[doid] = set([monDO])

    print('number of not name matching mappes:' + str(counter_name_not_matching))
    print('number of mapped doids with only doids:' + str(len(dict_DO_to_monDOs_only_DO)))
    print('number of mapped doids:' + str(len(dict_DO_to_monDOs_only_DO)))

    print('number of mapped monDO with only doids:' + str(len(dict_monDo_to_DO_only_doid)))
    print('number of mapped monDO:' + str(len(dict_monDo_to_DO)))

    counter_more_than_one_monDO_ID = 0

    for doid, mondos in dict_DO_to_monDOs.items():
        if len(mondos) > 1:
            counter_more_than_one_monDO_ID += 1

    print('number of multiple monDO IDs:' + str(counter_more_than_one_monDO_ID))

    print(list_of_not_mapped_doids)

    #file for multiple mapped monDO IDs
    file_mondo_to_multiple_doids = open('multiple_doids_for_monDO.tsv','w')
    file_mondo_to_multiple_doids.write('monDO\t monDO name\t doids \t doid names\n')
    for monDO, doids in dict_monDo_to_DO_only_doid.items():
        if len(doids) > 1:
            text= monDO+'\t'+dict_monDO_info[monDO][0]+'\t'+ '|'.join(doids)+'\t'
            for doid in doids:
                text= text +dict_DO_to_info[doid][0]+'|'
            file_mondo_to_multiple_doids.write(text[0:-1]+'\n')
            # print(monDO)
            # print(doids)

    # print(dict_DO_to_monDOs)
    print('###################################################################################')
    # print(dict_DO_to_monDOs_only_DO)

    print('###################################################################################')
    # print(dict_monDo_to_DO)


'''
Generate mapping files
'''


def mapping_files():
    for doid, mondos in dict_DO_to_monDOs_only_DO.items():
        f = open('mapping/Do_to_monDO/' + doid + '.txt', 'w')
        f.write(doid + '\t' + dict_DO_to_info[doid][0] + '\n')
        f.write('monDO ID \t name \n')
        for mondo in mondos:
            f.write(mondo + '\t' + dict_monDO_info[mondo][0] + '\n')
        f.close()

    for monDo, doids in dict_monDo_to_DO.items():
        g = open('mapping/monDO_to_DO/with_xref/' + monDo + '.txt', 'w')
        g.write(mondo + '\t' + dict_monDO_info[monDo][0] + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + dict_DO_to_info[doid][0] + '\n')
        g.close()

    for monDo, doids in dict_monDo_to_DO_only_doid.items():
        g = open('mapping/monDO_to_DO/without_xref/' + monDo + '.txt', 'w')
        g.write(mondo + '\t' + dict_monDO_info[monDo][0] + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + dict_DO_to_info[doid][0] + '\n')
        g.close()

'''

'''


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in DO diseases ')

    load_in_all_DO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Map DO to monDO ')

    map_DO_to_monDO_with_DO_and_xrefs()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate the mapping files ')

    mapping_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
