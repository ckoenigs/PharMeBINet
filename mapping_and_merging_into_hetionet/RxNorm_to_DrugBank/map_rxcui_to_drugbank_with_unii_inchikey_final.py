# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 08:30:30 2017

@author: Cassandra
"""

import datetime,csv

# dictionary inchikey to rxnorm_ids
dict_inchikey_to_rxnorm_ids = {}

# dictionary unii to rxcui
dict_unii_to_rxcui = {}

'''
go through the file new_rxcui_uniis_inchkeys.tsv and add the information to the different dictionaries
properties:
    0:rxcui
    1: uniis seperated with |
    2: inchikeys seperated with |
'''


def load_all_inchikey_and_rxnorm_in_dict():
    f = open('results/new_rxcui_uniis_inchkeys.tsv', 'r')
    csv_reader=csv.DictReader(f,delimiter='\t')

    print (datetime.datetime.utcnow())
    i = 0
    for line in csv_reader:
        rxcui = line['rxcui']
        uniis = line['uniis']
        uniis = uniis.split('|')
        for unii in uniis:
            if not unii in dict_unii_to_rxcui:
                dict_unii_to_rxcui[unii] = [rxcui]
            else:
                dict_unii_to_rxcui[unii].append(rxcui)
        inchikeys = line['inchikeys'].split('|') if line['inchikeys'] !='' else []
        for inchikey in inchikeys:
            if not inchikey in dict_inchikey_to_rxnorm_ids:
                dict_inchikey_to_rxnorm_ids[inchikey] = [rxcui]
            else:
                dict_inchikey_to_rxnorm_ids[inchikey].append(rxcui)

    print('number of inchikey:' + str(len(dict_inchikey_to_rxnorm_ids)))
    print('number of unii:' + str(len(dict_unii_to_rxcui)))


print (datetime.datetime.utcnow())

# dictionary rxnorm to drugbank id
dict_rxnorm_to_drugbank_id = {}

'''
go through all drugbank ids and compare the inchikeys with the inchikeys from rxcui, if they are the same then they are 
mapped. The same goes for the uniis.
properties:
    'unii','drugbank_id','inchikey'
'''


def map_with_inchikeys_to_drugbank():
    f = open('results/map_unii_to_drugbank_id_and_inchikey.tsv', 'r')
    csv_reader=csv.DictReader(f, delimiter='\t')
    i = 0
    count_map_with_unii = 0
    count_map_with_inchikey = 0
    count_map_with_alt_inchikey = 0
    for line in csv_reader:
        drugbank_id = line['drugbank_id']
        inchikey = line['inchikey']
        unii=line['unii']
        if not unii == '':
            if unii in dict_unii_to_rxcui:
                count_map_with_unii += 1
                rxcuis = dict_unii_to_rxcui[unii]
                for rxcui in rxcuis:
                    if not rxcui in dict_rxnorm_to_drugbank_id:
                        dict_rxnorm_to_drugbank_id[rxcui] = [drugbank_id]
                    else:
                        dict_rxnorm_to_drugbank_id[rxcui].append(drugbank_id)
            #                    continue

        if inchikey != '':
            if inchikey in dict_inchikey_to_rxnorm_ids:
                count_map_with_inchikey += 1
                #                    found_a_drugbank=True
                rxnorms = dict_inchikey_to_rxnorm_ids[inchikey]
                for rxcui in rxnorms:
                    if not rxcui in dict_rxnorm_to_drugbank_id:
                        dict_rxnorm_to_drugbank_id[rxcui] = [drugbank_id]
                    else:
                        dict_rxnorm_to_drugbank_id[rxcui].append(drugbank_id)

    print(i)
    print('number of mapped rxcuis:' + str(len(dict_rxnorm_to_drugbank_id)))
    print('number of map with unii:' + str(count_map_with_unii))
    print('number of map inchikey:' + str(count_map_with_inchikey))
    print('number of map alt inchikey:' + str(count_map_with_alt_inchikey))


'''
generate file rxnorm to drugbank 
'''


def generate_file_rxnorm_to_drugbank():
    f = open('results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv', 'w')
    csv_writer=csv.writer(f, delimiter='\t')
    csv_writer.writerow(['rxcui','drugbank_ids'])
    print(len(dict_rxnorm_to_drugbank_id))
    for rxcui, drugbank_ids in dict_rxnorm_to_drugbank_id.items():
        print(rxcui, drugbank_ids)
        drugbank_ids = list(set(drugbank_ids))
        string_drugbank_ids = '|'.join(drugbank_ids)
        csv_writer.writerow([rxcui , string_drugbank_ids ])


def main():
    print (datetime.datetime.utcnow())
    print('load all information over rxcui, unii and inchikey in a dictionary')

    load_all_inchikey_and_rxnorm_in_dict()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map with inchikey rxnorm to drugbank')

    map_with_inchikeys_to_drugbank()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('generate file map rxcui drugbank')

    generate_file_rxnorm_to_drugbank()

    print(
    '###########################################################################################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
