# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 08:30:30 2017

@author: Cassandra
"""

import datetime

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

    print (datetime.datetime.utcnow())
    i = 0
    for line in f:
        splitted = line.split('\t')

        rxcui = splitted[0]
        uniis = splitted[1]
        uniis = uniis.split('|')
        for unii in uniis:
            if not unii in dict_unii_to_rxcui:
                dict_unii_to_rxcui[unii] = [rxcui]
            else:
                dict_unii_to_rxcui[unii].append(rxcui)
        inchikeys = splitted[2].split('\n')[0].split('|')
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
    0:drugbank_id
    1:name	
    2:type	
    3:groups	
    4:atc_codes	
    5:categories	
    6:inchikey	
    7:inchi	
    8:inchikeys	
    9:synonyms	
    10:unii	
    11:uniis
    12:external_identifiers	
    13:extra_names
    14:brands
    15:molecular_forula	
    16:molecular_formular_experimental	
    17:gene_sequence	
    18:amino_acid_sequence	
    19:sequence
    20:description
'''


def map_with_inchikeys_to_drugbank():
    f = open('../drugbank/data/durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv', 'r')
    i = 0
    count_map_with_unii = 0
    count_map_with_inchikey = 0
    count_map_with_alt_inchikey = 0
    for drug in f:
        splitted = drug.split('\t')
        drugbank_id = splitted[0]
        # test if it is a drugbank entry
        if drugbank_id[0:2] == 'DB':

            i += 1
            inchikey = splitted[6]
            unii = splitted[10]
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

            uniis = splitted[11]
            if len(uniis) > 2:
                uniis = uniis.replace('[', '').replace(']', '')
                uniis = unii.replace("'", "")
                uniis = uniis.split('|')
                for unii in uniis:
                    if unii in dict_unii_to_rxcui:
                        #                        print('drinne')
                        count_map_with_unii += 1
                        rxcuis = dict_unii_to_rxcui[unii]
                        for rxcui in rxcuis:
                            if not rxcui in dict_rxnorm_to_drugbank_id:
                                dict_rxnorm_to_drugbank_id[rxcui] = [drugbank_id]
                            else:
                                dict_rxnorm_to_drugbank_id[rxcui].append(drugbank_id)

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


            alternative_inchikeys = splitted[8] if len(splitted[8]) > 6 else ' '
            if alternative_inchikeys[0] == '[':
                alternative_inchikeys = alternative_inchikeys.replace("'", "").replace('\n', '')
                alternative_inchikeys = [alternative_inchikeys.replace('[', '').replace(']', '')]
            else:
                alternative_inchikeys = alternative_inchikeys.replace('\n', '').split('|')
            for alternativ_inchikey in alternative_inchikeys:
                if alternativ_inchikey in dict_inchikey_to_rxnorm_ids:
                    count_map_with_alt_inchikey += 1
                    rxnorms = dict_inchikey_to_rxnorm_ids[alternativ_inchikey]
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
    f = open('results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey_4.tsv', 'w')
    f.write('rxcui \t drugbank ids with divided |\n')
    for rxcui, drugbank_ids in dict_rxnorm_to_drugbank_id.items():
        drugbank_ids = list(set(drugbank_ids))
        string_drugbank_ids = '|'.join(drugbank_ids)
        f.write(rxcui + '\t' + string_drugbank_ids + '\n')


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
