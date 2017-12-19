# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 08:35:25 2017

@author: Cassandra
"""
# dictionary with key rxnorm cui and value unii list
dict_rxcui_to_unii = {}
# dictionary with key unii and value rxnorm cui list
dict_unii_to_rxcui = {}

'''
load all rxnorm cui and unii from fda-srs in dictionaries
0:UNII	
1:PT	
2:RN	
3:EC	
4:NCIT	
5:RXCUI	
6:ITIS	
7:NCBI	
8:PLANTS	
9:GRIN	
10:MPNS	
11:INN_ID	
12:MF	
13:INCHIKEY	
14:SMILES	
15:UNII_TYPE
'''

g = open('Unii/UNIIs_with_RXCUI.tsv', 'r')
next(g)
for line in g:
    splitted = line.split('\t')
    unii = splitted[0]
    rxcui = splitted[5]
    if not rxcui in dict_rxcui_to_unii:
        dict_rxcui_to_unii[rxcui] = [unii]
    else:
        dict_rxcui_to_unii[rxcui].append(unii)
    if not unii in dict_unii_to_rxcui:
        dict_unii_to_rxcui[unii] = [rxcui]
    else:
        dict_unii_to_rxcui[unii].append(rxcui)

print('number of rxcui:' + str(len(dict_rxcui_to_unii)))
print('number of unii:' + str(len(dict_unii_to_rxcui)))
g.close()

'''
load all rxnorm cui and unii from rxnorm in dictionaries
0:rxcui
1:unii
'''
counter_rxcui = 0
counter_unii = 0
count_different_unii = 0
f = open('data/map_rxnorm_to_UNII.tsv', 'r')
next(f)
for line in f:
    splitted = line.split('\t')
    rxcui = splitted[0]
    unii = splitted[1].split('\n')[0]
    if not rxcui in dict_rxcui_to_unii:
        counter_rxcui += 1
        dict_rxcui_to_unii[rxcui] = [unii]
    else:
        if not unii in dict_rxcui_to_unii[rxcui]:
            count_different_unii += 1
            dict_rxcui_to_unii[rxcui].append(unii)

    if not unii in dict_unii_to_rxcui:
        dict_unii_to_rxcui[unii] = [rxcui]
        counter_unii += 1
    else:
        dict_unii_to_rxcui[unii].append(rxcui)

f.close()
print(counter_rxcui)
print(count_different_unii)
print(counter_unii)
print('number of rxcui:' + str(len(dict_rxcui_to_unii)))
print('number of unii:' + str(len(dict_unii_to_rxcui)))

dict_unii_to_inchi_key = {}

'''
find for all unii a inchikey in fda-srs
0:UNII	
1:PT	
2:RN	
3:EC	
4:NCIT	
5:RXCUI	
6:ITIS	
7:NCBI	
8:PLANTS	
9:GRIN	
10:MPNS	
11:INN_ID	
12:MF	
13:INCHIKEY	
14:SMILES	
15:UNII_TYPE

'''
h = open('Unii/UNIIs 28Apr2017 Records.txt', 'r')
next(h)
for line in h:
    splitted = line.split('\t')
    unii = splitted[0]
    inchikey = splitted[13]
    if inchikey != '':
        if unii in dict_unii_to_rxcui:
            if not unii in dict_unii_to_inchi_key:
                dict_unii_to_inchi_key[unii] = inchikey

h.close()
print(len(dict_unii_to_inchi_key))

'''
generate new file with rxcui, uniis, inchikeys
'''
g = open('Unii/new_rxcui_uniis_inchkeys.tsv', 'w')
g.write('rxcui \t uniis \t inchikeys \n')
for rxcui, uniis in dict_rxcui_to_unii.items():
    uniis = list(set(uniis))
    inchikeys_list = []
    for unii in uniis:
        if unii in dict_unii_to_inchi_key:
            inchikeys_list.append(dict_unii_to_inchi_key[unii])
    inchikeys_list = list(set(inchikeys_list))
    string_uniis = '|'.join(uniis)
    string_inchikeys = '|'.join(inchikeys_list)
    g.write(rxcui + '\t' + string_uniis + '\t' + string_inchikeys + '\n')

g.close()
