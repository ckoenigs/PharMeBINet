# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 13:25:13 2017

https://github.com/dhimmel/drugbank/blob/gh-pages/parse.ipynb
"""

import os
import csv
import gzip
import collections
import re
import io
import json
import xml.etree.ElementTree as ET
import datetime

import requests
import pandas

# open and parse xml drugbank file into a root tree
xml_file = os.path.join('drugbank_all_full_database.xml/full_database.xml')
print (datetime.datetime.utcnow())

tree = ET.parse(xml_file)
root = tree.getroot()

# fix root path
ns = '{http://www.drugbank.ca}'
inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"
molecular_formular_template="{ns}calculated-properties/{ns}property[{ns}kind='Molecular Formula']/{ns}value"
molecular_formular_experimental_template="{ns}experimental-properties/{ns}property[{ns}kind='Molecular Formula']/{ns}value"

                                          
counter=0
rows = list()
# go through all root entries and get the improtant information
for i, drug in enumerate(root):
    counter+=1
    row = collections.OrderedDict()
    assert drug.tag == ns + 'drug'
    row['type'] = drug.get('type')
    row['drugbank_id'] = drug.findtext(ns + "drugbank-id[@primary='true']")
    row['name'] = drug.findtext(ns + "name")
    row['description'] = drug.findtext(ns + "description").replace('\n','').replace('\r','')
    row['groups'] = [group.text for group in
        drug.findall("{ns}groups/{ns}group".format(ns = ns))]
    row['atc_codes'] = [code.get('code') for code in
        drug.findall("{ns}atc-codes/{ns}atc-code".format(ns = ns))]
    row['categories'] = [x.findtext(ns + 'category') for x in
        drug.findall("{ns}categories/{ns}category".format(ns = ns))]
    row['inchi'] = drug.findtext(inchi_template.format(ns = ns))
    row['inchikey'] = drug.findtext(inchikey_template.format(ns = ns))
    row['inchikeys']= [salt.text for salt in
        drug.findall("{ns}salts/{ns}salt/{ns}inchikey".format(ns = ns))]
    row['synonyms']= [salt.text for salt in
        drug.findall("{ns}synonyms/{ns}synonym".format(ns = ns))]
    row['unii']=drug.findtext(ns + "unii")
    extern_ids_source=[salt.text for salt in
        drug.findall("{ns}external-identifiers/{ns}external-identifier/{ns}resource".format(ns = ns))]
    extern_ids=[salt.text for salt in
        drug.findall("{ns}external-identifiers/{ns}external-identifier/{ns}identifier".format(ns = ns))]
    row['external_identifiers']=[i+':'+j for i,j in zip(extern_ids_source,extern_ids)]
    row['brands']=[salt.text for salt in
        drug.findall("{ns}international-brands/{ns}international-brand/{ns}name".format(ns = ns))]
    row['uniis']=[salt.text for salt in
        drug.findall("{ns}salts/{ns}salt/{ns}unii".format(ns = ns))]
    row['extra_names']=[salt.text for salt in
        drug.findall("{ns}salts/{ns}salt/{ns}name".format(ns = ns))]
    row['molecular_forula']=drug.findtext(molecular_formular_template.format(ns = ns))
    row['molecular_formular_experimental']=drug.findtext(molecular_formular_experimental_template.format(ns = ns))
    row['gene_sequence']= drug.findtext(ns + "gene-sequence").replace('\t','').replace('\n','').replace('\r','') if drug.findtext(ns + "gene-sequence")!=None else ''
    row['amino_acid_sequence']= drug.findtext(ns + "amino-acid-sequence").replace('\t','').replace('\n','').replace('\r','') if drug.findtext(ns + "amino-acid-sequence")!=None else ''
    row['sequence']= drug.findtext("{ns}sequences/{ns}sequence".format(ns = ns)).replace('\t','').replace('\n','').replace('\r','') if drug.findtext("{ns}sequences/{ns}sequence".format(ns = ns))!=None else ''
    
    # Add drug aliases
    aliases = {
        elem.text for elem in 
        drug.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
        drug.findall("{ns}synonyms/{ns}synonym[@language='English']".format(ns = ns)) +
        drug.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
        drug.findall("{ns}products/{ns}product/{ns}name".format(ns = ns))

    }
    aliases.add(row['name'])
    row['aliases'] = sorted(aliases)

    rows.append(row)
 
print('number of entries in drugbank:'+str(counter))
print (datetime.datetime.utcnow())
# write a json file with all alisa for every drugbank entry
alias_dict = {row['drugbank_id']: row['aliases'] for row in rows}
with open('./data/aliases.json', 'w') as fp:
    json.dump(alias_dict, fp, indent=2, sort_keys=True)

# change format from list to a string with separator | for every entry from a row
def collapse_list_values(row):
    for key, value in row.items():
        if isinstance(value, list):
            i=0
            # the list of inchikey, uniis or extra names has sometimes none as value and they have to be delete
            if key=='inchikeys'or key=='uniis' or key=='extra_names':
                list_delete = []
                for val in value:
                    if val == None:
                        list_delete.insert(0,i)
                    i += 1
                for j in list_delete:
                    del value[j]
                    
            if len(value)>1:
                string_value = '|'.join(value)
                row[key]=string_value.replace('\t','').replace('\n','').replace('\r','')
                
    return row

print (datetime.datetime.utcnow())
# combine all rows to a list and  every row contains only strings
rows = list(map(collapse_list_values, rows))

print (datetime.datetime.utcnow())
# the defined the header of the drugbank.tsv and put all information in this order
columns = ['drugbank_id', 'name', 'type', 'groups', 'atc_codes', 'categories', 'inchikey', 'inchi','inchikeys', 'synonyms', 'unii','uniis', 'external_identifiers','extra_names', 'brands', 'molecular_forula','molecular_formular_experimental','gene_sequence','amino_acid_sequence','sequence','description']
drugbank_df = pandas.DataFrame.from_dict(rows)[columns]
drugbank_df.head()

# definition of the slim version fo the file
drugbank_slim_df = drugbank_df[
    drugbank_df.groups.map(lambda x: 'approved' in x) &
    drugbank_df.inchi.map(lambda x: x is not None) &
    drugbank_df.type.map(lambda x: x == 'small molecule')
]
drugbank_slim_df.head()



# write drugbank tsv
path = os.path.join('data', 'drugbank_with_synonyms_uniis_extern_ids_molecular_seq_formular.tsv')
drugbank_df.to_csv(path, sep='\t', index=False)

# write slim drugbank tsv
path = os.path.join('data', 'drugbank-slim2_with_synonyms_uniis_extern_ids_molecular_formular.tsv')
drugbank_slim_df.to_csv(path, sep='\t', index=False)

