# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 08:30:30 2017

@author: Cassandra
"""

import datetime, csv

# dictionary inchikey to rxnorm_ids
dict_inchikey_to_rxnorm_ids = {}

'''
go through all date in file UNIIs 28Apr2017 Records.txt and remember only the one with a rxcui
file has properties:
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


def load_all_inchikey_and_rxnorm_in_dict():
    f = open('unii/unii_data.txt', 'r')
    csv_reader=csv.DictReader(f,delimiter='\t',)
    g = open('results/UNIIs_with_RXCUI.tsv', 'w')
    csv_writer=csv.writer(g, delimiter='\t')
    csv_writer.writerow(['unii','rxcui'])

    print (datetime.datetime.utcnow())
    i = 0
    for line in csv_reader:
        unii=line['UNII']
        rxcui=line['RXCUI']
        csv_writer.writerow([unii,rxcui])


print (datetime.datetime.utcnow())


def main():
    print (datetime.datetime.utcnow())
    print('load all information over rxcui and inchikey in a dictionary and generate a file with unii and rxnorm')

    load_all_inchikey_and_rxnorm_in_dict()

    print(
    '###########################################################################################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
