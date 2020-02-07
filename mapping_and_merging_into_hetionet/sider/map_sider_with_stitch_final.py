# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:16:45 2017

@author: Cassandra
"""
from py2neo import Graph
import datetime
import sys, csv
from collections import defaultdict






class DrugSider:
    """

    stitchIDflat: string
    stitchIDstereo: string
    PubChem_Coupound_ID: int
    inchi: string
    inchikey: string
    drugBank_id: string
    name: string
    how_mapped :string
    """

    def __init__(self, stitchIDflat, stitchIDstereo, PubChem_Coupound_ID):
        self.stitchIDflat = stitchIDflat
        self.PubChem_Coupound_ID = PubChem_Coupound_ID
        self.stitchIDstereo = stitchIDstereo

    def set_other_properties(self, inchi, inchikey):
        self.inchi = inchi
        self.inchikey = inchikey

    def set_drugBank_id(self, drugBank_id):
        self.drugBank_id = drugBank_id

    def set_name(self, name):
        self.name = name

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


class DrugHetionet:
    """
    license: string
    identifier: string (Drugbank Id)
    inchikey: string
    inchi: string
    name: string
    source: string
    url: string
    """

    def __init__(self, identifier, inchikey, inchi, name, resource, xrefs):
        #        self.license=licenses
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name
        self.resource=resource
        self.xrefs=xrefs



# list all compound ids in hetionet
list_compound_in_hetionet = []

# dictionary with all compounds with drugbank id as key and class DrugHetionet as value
dict_all_drug = {}

# dictionary with all drugs from sider with the stereo id as key and class DrugSider as value
dict_sider_drug = {}

'''
create connection to neo4j
'''


def create_connection_with_neo4j():
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))


'''
load in all compounds from hetionet in a dictionary
properties:
    license: string
    identifier: string (Drugbank ID)
    inchikey: string
    inchi: string
    name: string
    source: string
    url: url
'''


def load_compounds_from_hetionet():
    query = 'MATCH (n:Compound) RETURN n '
    results = g.run(query)

    for result, in results:
        identifier = result['identifier']
        inchikey = result['inchikey']
        inchi = result['inchi']
        name = result['name']
        resource=result['resource']
        xrefs = result['xrefs']

        drug = DrugHetionet(identifier, inchikey, inchi, name, resource, xrefs)
        dict_all_drug[identifier] = drug


# list of all stitch stereo id
list_stitchIDstereo = []

# dictionary with all flat ids in pubchem form as keys and a list of stereo ids in pubchem form as value
dict_flat_to_stereo = {}

'''
load all sider drugs in a dictionary, further generate the PubChem ID from Stitch stereo and flat

'''


def load_sider_drug_in_dict():
    query = 'MATCH (n:drugSider) RETURN n '
    results = g.run(query)

    for result, in results:

        stitchIDflat = result['stitchIDflat']
        stitchIDstereo = result['stitchIDstereo']
        PubChem_Coupound_ID = result['PubChem_Coupound_ID']
        list_stitchIDstereo.append(stitchIDstereo)

        drug = DrugSider(stitchIDflat, stitchIDstereo, PubChem_Coupound_ID)
        pubchem_flat = int(stitchIDflat[3:]) - 100000000
        pubchem_stereo = int(stitchIDstereo[3:])
        dict_sider_drug[pubchem_stereo] = drug
        if not pubchem_flat in dict_flat_to_stereo:
            dict_flat_to_stereo[pubchem_flat] = [pubchem_stereo]
        else:
            dict_flat_to_stereo[pubchem_flat].append(pubchem_stereo)

    print('number of drugs from sider:' + str(len(dict_sider_drug)))
    print('number of flat ids:' + str(len(dict_flat_to_stereo)))


# dictionary with flat in pubchem form as key and a list of drugbank ids as values
dict_flat_to_drugbank = {}

# dictionary with flat in pubchem form as key and list of drugbank ids as value, but only the drugbank ids where stitch flat and stereo are the same
dict_flat_to_drugbank_same_stereo = defaultdict(list)

# dictionary with stereo id in pubchem form as key and drugbank ids as values
dict_sider_drug_with_drugbank_ids = defaultdict(list)

# files with all mapping for the different how_mapped mmethods
map_stereo_id_to_drugbank_id = open('drug/Sider_drug_map_stereo_id_to_drugbank.tsv', 'w',encoding='utf-8')
map_stereo_id_to_drugbank_id.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_flat_id_same_as_stereo_to_drugbank_id = open('drug/Sider_drug_map_flat_id_same_as_stereo_id_to_drugbank.tsv', 'w',encoding='utf-8')
map_flat_id_same_as_stereo_to_drugbank_id.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_flat_id_to_drugbank_id = open('drug/Sider_drug_map_flat_id_to_drugbank.tsv', 'w',encoding='utf-8')
map_flat_id_to_drugbank_id.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_stereo_to_inchikey_to_drugbank_id = open('drug/Sider_drug_map_stereo_to_inchikey_to_drugbank.tsv', 'w',encoding='utf-8')
map_stereo_to_inchikey_to_drugbank_id.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative = open(
    'drug/Sider_drug_map_stereo_to_inchikey_to_drugbank_inchikeys_alternative.tsv', 'w',encoding='utf-8')
map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative.write(
    'stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_stereo_name_to_drugbank_id_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_name.tsv', 'w',encoding='utf-8')
map_stereo_name_to_drugbank_id_name.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_stereo_name_to_drugbank_id_synonym_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_synonym_name.tsv', 'w',encoding='utf-8')
map_stereo_name_to_drugbank_id_synonym_name.write(
    'stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_stereo_name_to_drugbank_id_brand_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_brand_name.tsv', 'w',encoding='utf-8')
map_stereo_name_to_drugbank_id_brand_name.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

map_stereo_name_to_drugbank_id_extra_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_extra_name.tsv', 'w',encoding='utf-8')
map_stereo_name_to_drugbank_id_extra_name.write('stitch id flat \t stitch id stereo \t drugbank ids seperated with |\n')

# dictionary with how_mapped as key and file as value
dict_how_mapped_to_file = {'stitch stereo id to drugbank ids': map_stereo_id_to_drugbank_id,
                           'stitch flat id (same as stereo is) to drugbank ids': map_flat_id_same_as_stereo_to_drugbank_id,
                           'stitch flat id to drugbank ids': map_flat_id_to_drugbank_id,
                           'stitch stereo id inchikey to drugbank ids': map_stereo_to_inchikey_to_drugbank_id,
                           'stitch stereo id alternativ inchikey to drugbank ids': map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative,
                           'stitch stereo id name to drugbank ids name': map_stereo_name_to_drugbank_id_name,
                           'stitch stereo id name to drugbank ids synonym names': map_stereo_name_to_drugbank_id_synonym_name,
                           'stitch stereo id name to drugbank ids brand names': map_stereo_name_to_drugbank_id_brand_name,
                           'stitch stereo id name to drugbank ids extra_name names': map_stereo_name_to_drugbank_id_extra_name}

# list of all stitch stereo ids in pubchem form which are not mapped
list_of_not_mapped_stitch_stereo = []

# list of all stitch flat ids in pubchem form which are not mapped
list_of_not_mapped_stitch_flat = []

'''
find for the different stitch stereo ids drugbank id with use of chemical.sources_DB.v5.0.tsv
properties:
    0:stitch flat id
    1:stitch stereo id
    2:source
    3:source id (Durgbank id)
    
if for the stereo id nothing is found uses the drugbank id which is found for the flat id. Prefer the flat ids where the 
steroe id is the same as the flat id. 
'''


def give_drugbank_ids_with_use_of_stitch_information():
    # find for the stereo id the drugbank ids and save for all flat ids in sider the drugbank ids
    f = open('StitchData/chemical.sources.v5.0.tsv', 'r',encoding='utf-8')
    csv_reader=csv.reader(f,delimiter='\t')
    next(csv_reader)
    for line in csv_reader:
        stitch_flat = int(line[0][4:])
        stitch_stereo = int(line[1][4:])
        xref_source=line[2]
        xref = line[3][0]
        # get durgbank id with stitch stereo id in pubchem form
        if stitch_stereo in dict_sider_drug:
            if xref_source=='DrugBank':
                if xref in dict_all_drug:
                    dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id to drugbank ids')
                    dict_sider_drug_with_drugbank_ids[stitch_stereo].append(xref)
        # get drugbank id with use of flat id in pubchem form
        if stitch_flat in dict_flat_to_stereo:
            if xref_source == 'DrugBank':
                if xref in dict_all_drug:
                    if stitch_flat == stitch_stereo:
                        dict_flat_to_drugbank_same_stereo[stitch_flat].append(xref)
                    dict_sider_drug_with_drugbank_ids[stitch_flat].append(xref)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_drugbank_ids)))
    print('number of mapped stitch flat ids to drugbank:' + str(len(dict_flat_to_drugbank)))
    print('number of mapped stitch flat ids to drugbank (same stereo):' + str(len(dict_flat_to_drugbank_same_stereo)))

    # check if a sider drug which was not mapped with the stereo id has a mapped flat id
    g = open('not_mapped_pubchem_ids_from_stitch.txt', 'w',encoding='utf-8')
    # counter for mapped with flat id where flat and stereo are the same
    i = 0
    # counter for mapped with flat id where flat and stereo are not the same
    j = 0
    for pubchem_stereo, drug in dict_sider_drug.items():
        if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
            pubchem_flat = int(drug.stitchIDflat[3:]) - 100000000
            if pubchem_flat in dict_flat_to_drugbank_same_stereo:
                i += 1
                dict_sider_drug_with_drugbank_ids[pubchem_stereo] = dict_flat_to_drugbank_same_stereo[pubchem_flat]
                dict_sider_drug[pubchem_stereo].set_how_mapped('stitch flat id (same as stereo is) to drugbank ids')
            elif pubchem_flat in dict_flat_to_drugbank:
                j += 1
                dict_sider_drug_with_drugbank_ids[pubchem_stereo] = dict_flat_to_drugbank[pubchem_flat]
                dict_sider_drug[pubchem_stereo].set_how_mapped('stitch flat id to drugbank ids')
            else:
                list_of_not_mapped_stitch_stereo.append(pubchem_stereo)
                list_of_not_mapped_stitch_flat.append(pubchem_flat)
                g.write(str(pubchem_stereo) + ',')
    g.close()
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_drugbank_ids)))


'''
make a smaller file of stitch inchikeys for the one stitch stereo which are not mapped to drugbank ids
properties:
    0:flat_chemical_id 	 
    1:stereo_chemical_id 	 
    3:source_cid	 	 
    4:inchikey 
    
make a smaller file of stitch chemicals for the stitch stereo and flat which are in sider
properties chemical.v5.0:
    0:chemical 	 
    1:name 	 
    2:molecular_weight 	 
    3:SMILES_string 
'''


def make_a_smaller_file_of_stitch_inchikey_and_chemical():
    g = open('StitchData/chemicals.inchikeys.v5.0.tsv', 'r',encoding='utf-8')
    h = open('StitchData/chemicals.inchikeys_part.v5.0.tsv', 'w',encoding='utf-8')
    i = 0
    for line in g:
        if i == 0:
            h.write(line)
            i += 1
            continue
        splitted = line.split('\t')
        stitch_flat = int(splitted[0][4:])
        stitch_stereo = int(splitted[1][4:])
        if stitch_stereo in list_of_not_mapped_stitch_stereo:
            h.write(line)
        elif stitch_flat in list_of_not_mapped_stitch_flat:
            h.write(line)
    g.close()
    h.close()

    g = open('StitchData/chemicals.v5.0.tsv', 'r',encoding='utf-8')
    h = open('StitchData/chemicals_part.v5.0.tsv', 'w',encoding='utf-8')
    i = 0
    for line in g:
        if i == 0:
            h.write(line)
            i += 1
            continue
        splitted = line.split('\t')

        if splitted[0][3:4] == 's':
            pubchemStereo_ID = int(splitted[0][4:])
            if pubchemStereo_ID in dict_sider_drug:
                h.write(line)
        else:
            pubchem_flat_ID = int(splitted[0][4:])
            if pubchem_flat_ID in dict_flat_to_stereo:
                h.write(line)


# dictionary with stitch stereo id in pubchem form as key and value is the name
dict_stereo_key_name = {}

# dictionary with flat in pubchem form as key and value is the name
dict_flat_key_name = {}

# dictionary with name as key and list with flat and stereo id
dict_name_to_flat_stereo_id = {}

'''
load in stitch name and save them in a dictionary
0:chemical
1:name    
2:molecular_weight        
3:SMILES_string

'''


def load_in_stitch_name():
    f = open('StitchData/chemicals_part.v5.0.tsv', 'r',encoding='utf-8')
    next(f)
    for line in f:
        splitted = line.split('\t')
        name = splitted[1]
        if splitted[0][3:4] == 's':
            pubchemStereo_ID = int(splitted[0][4:])
            dict_stereo_key_name[pubchemStereo_ID] = name
            dict_name_to_flat_stereo_id[name.lower()] = ['', pubchemStereo_ID]
        else:
            pubchem_flat_ID = int(splitted[0][4:])
            dict_flat_key_name[pubchem_flat_ID] = name
            dict_name_to_flat_stereo_id[name.lower()] = [pubchem_flat_ID, '']

    print(len(dict_stereo_key_name))


# dictionary with inchikey as key and value is stitch stereo in pubchem form
dict_inchikey_to_stitch_stereo = {}

'''
load from stitch the inchikey in a dictionary for all not mapped sider drugs
properties of chemicals.inchikeys_part.v5.0.tsv:
    0:flat_chemical_id 	 
    1:stereo_chemical_id 	 
    2:source_cid	 	 
    3:inchikey 
'''


def load_in_stitch_inchikeys():
    f = open('StitchData/chemicals.inchikeys_part.v5.0.tsv', 'r',encoding='utf-8')
    next(f)
    for line in f:
        splitted = line.split('\t')
        stitch_flat = int(splitted[0][4:])
        stitch_stereo = int(splitted[1][4:])
        inchikey = splitted[3].split('\n')[0]
        if stitch_stereo in list_of_not_mapped_stitch_stereo:
            if not inchikey in dict_inchikey_to_stitch_stereo:
                dict_inchikey_to_stitch_stereo[inchikey] = [stitch_stereo]
            else:
                dict_inchikey_to_stitch_stereo[inchikey].append(stitch_stereo)
        else:
            if stitch_flat in dict_flat_to_stereo:
                stitch_stereos = dict_flat_to_stereo[stitch_flat]
                for stereo in stitch_stereos:
                    if stitch_stereo in list_of_not_mapped_stitch_stereo:
                        if not inchikey in dict_inchikey_to_stitch_stereo:
                            dict_inchikey_to_stitch_stereo[inchikey] = [stitch_stereo]
                        else:
                            dict_inchikey_to_stitch_stereo[inchikey].append(stitch_stereo)


'''
map stitch to drugbank with use of inchikeys
properties from durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv:
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


def map_inchikeys_to_drugbank():
    f = open('../drugbank/data/durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv', 'r',encoding='utf-8')
    next(f)
    # list of all index from in this step mapped stereo ids
    delete_index = []
    for drug in f:
        splitted = drug.split('\t')
        drugbank_id = splitted[0]
        # test if it is a drugbank entry
        if drugbank_id[0:2] == 'DB':
            inchikey = splitted[6]
            found_a_drugbank = False

            if inchikey in dict_inchikey_to_stitch_stereo:
                stitch_stereos = dict_inchikey_to_stitch_stereo[inchikey]
                found_a_drugbank = True
                for stitch_stereo in stitch_stereos:
                    delete_index.append(list_of_not_mapped_stitch_stereo.index(stitch_stereo))
                    if not stitch_stereo in dict_sider_drug_with_drugbank_ids:
                        dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id inchikey to drugbank ids')
                        dict_sider_drug_with_drugbank_ids[stitch_stereo] = [drugbank_id]

                    else:
                        dict_sider_drug_with_drugbank_ids[stitch_stereo].append(drugbank_id)

            if len(splitted) > 9 and not found_a_drugbank:
                alternative_inchikeys = splitted[8] if len(splitted[8]) > 6 else ' '
                if alternative_inchikeys[0] == '[':
                    alternative_inchikeys = alternative_inchikeys.replace("'", "").replace('\n', '')
                    alternative_inchikeys = [alternative_inchikeys.replace('[', '').replace(']', '')]
                else:
                    alternative_inchikeys = alternative_inchikeys.replace('\n', '').split('|')
                for alternativ_inchikey in alternative_inchikeys:
                    if alternativ_inchikey in dict_inchikey_to_stitch_stereo:
                        stitch_stereos = dict_inchikey_to_stitch_stereo[alternativ_inchikey]
                        for stitch_stereo in stitch_stereos:
                            delete_index.append(list_of_not_mapped_stitch_stereo.index(stitch_stereo))
                            if not stitch_stereo in dict_sider_drug_with_drugbank_ids:
                                dict_sider_drug[stitch_stereo].set_how_mapped(
                                    'stitch stereo id alternativ inchikey to drugbank ids')
                                dict_sider_drug_with_drugbank_ids[stitch_stereo] = [drugbank_id]

                            else:
                                dict_sider_drug_with_drugbank_ids[stitch_stereo].append(drugbank_id)

    # removed all mapped stitch stereo ids from the not mapped list
    delete_index = list(set(delete_index))
    delete_index.sort()
    delete_index = list(reversed(delete_index))
    for index in delete_index:
        list_of_not_mapped_stitch_stereo.pop(index)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_drugbank_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))


'''
map stitch to drugbank with use of stitch name to drugbank name, synonyms ,Product Ingredients name and brands name
properties from durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv:
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


def map_name_to_drugbank():
    f = open('../drugbank/data/durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv', 'r',encoding='utf-8')
    next(f)
    # list of all index from in this step mapped stereo ids
    delete_index = []
    for drug in f:
        splitted = drug.split('\t')
        drugbank_id = splitted[0]
        # test if it is a drugbank entry
        if drugbank_id[0:2] == 'DB':
            name = splitted[1].lower()
            found_a_drugbank = False
            # search at drugbank name
            if name in dict_name_to_flat_stereo_id:
                pubchem_stereo = dict_name_to_flat_stereo_id[name][1]
                pubchem_flat = dict_name_to_flat_stereo_id[name][0]

                if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                    found_a_drugbank = True
                    delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                    if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                        dict_sider_drug[pubchem_stereo].set_how_mapped('stitch stereo id name to drugbank ids name')
                        dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                    else:
                        dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)

                if pubchem_flat in dict_flat_to_stereo:
                    pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                    for pubchem_stereo in pubchem_stereos:
                        if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                            found_a_drugbank = True
                            delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                            if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                dict_sider_drug[pubchem_stereo].set_how_mapped(
                                    'stitch stereo id name to drugbank ids name')
                                dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                            else:
                                dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)

            # search with drugbank synonyms
            if not found_a_drugbank:
                synonyms = splitted[9]
                if len(synonyms) > 0:
                    synonyms = synonyms.replace('[', '').replace(']', '').replace("'", "")
                    synonyms = synonyms.split('|')
                    for synonym in synonyms:
                        synonym = synonym.lower()
                        if synonym in dict_name_to_flat_stereo_id:
                            #                            print('here')
                            pubchem_stereo = dict_name_to_flat_stereo_id[synonym][1]
                            pubchem_flat = dict_name_to_flat_stereo_id[synonym][0]
                            if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                found_a_drugbank = True
                                delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                    dict_sider_drug[pubchem_stereo].set_how_mapped(
                                        'stitch stereo id name to drugbank ids synonym names')
                                    dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                                else:
                                    dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)

                            if pubchem_flat in dict_flat_to_stereo:
                                pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                                for pubchem_stereo in pubchem_stereos:
                                    if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                        found_a_drugbank = True
                                        delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                        if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                            dict_sider_drug[pubchem_stereo].set_how_mapped(
                                                'stitch stereo id name to drugbank ids synonym names')
                                            dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                                        else:
                                            dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)
            # search with drugbank Product Ingredients name
            if not found_a_drugbank:
                extra_names = splitted[13]
                if len(extra_names) > 0:
                    extra_names = extra_names.replace('[', '').replace(']', '').replace("'", "")
                    extra_names = extra_names.split('|')
                    #                    print('in here')
                    for extra_name in extra_names:
                        extra_name = extra_name.lower()
                        if extra_name in dict_name_to_flat_stereo_id:
                            #                            print('here')
                            pubchem_stereo = dict_name_to_flat_stereo_id[extra_name][1]
                            pubchem_flat = dict_name_to_flat_stereo_id[extra_name][0]
                            if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                #                                print('found')
                                #                                print(pubchem_stereo)
                                #                                print(extra_name)
                                found_a_drugbank = True
                                delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                    dict_sider_drug[pubchem_stereo].set_how_mapped(
                                        'stitch stereo id name to drugbank ids extra_name names')
                                    dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                                else:
                                    dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)

                            if pubchem_flat in dict_flat_to_stereo:
                                pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                                for pubchem_stereo in pubchem_stereos:
                                    if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                        found_a_drugbank = True
                                        delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                        if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                            dict_sider_drug[pubchem_stereo].set_how_mapped(
                                                'stitch stereo id name to drugbank ids extra_name names')
                                            dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                                        else:
                                            dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)
            # search with brand names of drugbank
            if not found_a_drugbank:
                brands = splitted[14]
                if len(brands) > 0:
                    brands = brands.replace('[', '').replace(']', '').replace("'", "")
                    brands = brands.split('|')
                    #                    print('in here')
                    for brand in brands:
                        brand = brand.lower()
                        if brand in dict_name_to_flat_stereo_id:
                            #                            print('here')
                            pubchem_stereo = dict_name_to_flat_stereo_id[brand][1]
                            pubchem_flat = dict_name_to_flat_stereo_id[brand][0]
                            if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                    dict_sider_drug[pubchem_stereo].set_how_mapped(
                                        'stitch stereo id name to drugbank ids brand names')
                                    dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                                else:
                                    dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)

                            if pubchem_flat in dict_flat_to_stereo:
                                pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                                for pubchem_stereo in pubchem_stereos:
                                    if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                        delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                        if not pubchem_stereo in dict_sider_drug_with_drugbank_ids:
                                            dict_sider_drug[pubchem_stereo].set_how_mapped(
                                                'stitch stereo id name to drugbank ids brand names')
                                            dict_sider_drug_with_drugbank_ids[pubchem_stereo] = [drugbank_id]

                                        else:
                                            dict_sider_drug_with_drugbank_ids[pubchem_stereo].append(drugbank_id)

    # removed all mapped stitch stereo ids from the not mapped lis
    delete_index = list(set(delete_index))
    delete_index.sort()
    delete_index = list(reversed(delete_index))
    for index in delete_index:
        list_of_not_mapped_stitch_stereo.pop(index)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_drugbank_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))


'''
integrate sider drugs into hetionet directly. For the compound which are already in hetionet only some properties 
are add and a connection to the sider drug is generated. Further new compound for hetionet a gerneted which has also a
 connection to  the sider drug.  
'''


def integrate_sider_drugs_into_hetionet():
    # a file with all sider drugs which has a drugbank id but this has no chemical information
    without_chemical = open('drug/durgbank_without_chemical_seq.tsv', 'w',encoding='utf-8')
    without_chemical.write('DB \t pubchem \n')

    get_drugbank_information.load_all_drugbank_ids_in_dictionary()
    # all possible mapped sider drug
    counter = 0
    # count all sider drug which are removed
    counter_with_one_which_is_removed = 0
    # count number of sider drugs which are mapped to hetionet
    counter_mapped_to_hetionet = 0
    # count all sider drugs which generate new hetionet compounds
    counter_new = 0

    # set hetionet compound that they are from hetionet
    query = '''MATCH  (c:Compound) Set c.hetionet="yes",  c.resource=["hetionet"] '''
    g.run(query)

    # go through all mapped sider drugs and integrate them into hetionet
    for pubchem_stereo, drugbank_ids in dict_sider_drug_with_drugbank_ids.items():
        counter += 1
        # if one of the drugbank ids are in hetionet
        mapped_to_hetionet = False
        drugbank_ids = list(set(drugbank_ids))
        dict_sider_drug_with_drugbank_ids[pubchem_stereo] = drugbank_ids
        stitch_stereo = dict_sider_drug[pubchem_stereo].stitchIDstereo
        stitch_flat = dict_sider_drug[pubchem_stereo].stitchIDflat
        pubchem_flat = int(stitch_flat[4:])
        if pubchem_stereo in dict_stereo_key_name:
            name = dict_stereo_key_name[pubchem_stereo]
        elif pubchem_flat in dict_flat_key_name:
            name = dict_flat_key_name[pubchem_flat]
        else:
            name = ''

        how_mapped = dict_sider_drug[pubchem_stereo].how_mapped

        # generate the mapping files for the different mapping steps
        string_drugbank_ids = "|".join(drugbank_ids)
        dict_how_mapped_to_file[how_mapped].write(dict_sider_drug[pubchem_stereo].stitchIDflat + '\t' + dict_sider_drug[
            pubchem_stereo].stitchIDstereo + '\t' + string_drugbank_ids + '\n')

        # set name and from which mapping step for the drug in sider
        query = '''MATCH (d:drugSider{stitchIDstereo:"%s"})
        Set d.name="%s", d.how_mapped="%s" '''
        query = query % (stitch_stereo, name, how_mapped)
        g.run(query)

        # create connection to mapped compound and create new compound if this is not existing

        # index of drugbank ids which has no chemical information
        delete_index = []
        # alternative drugbank if they have the same name as the drugbank id
        alternative_ids = []
        i = 0
        for drugbank_id in drugbank_ids:
            i += 1
            query = '''Match (c:Compound{identifier:"%s"}) Return c'''
            query = query % (drugbank_id)
            results = g.run(query)
            first_entry = results.evaluate()

            if first_entry == None:
                [name, inchi, inchikey] = get_drugbank_information.get_drugbank_inforamtion(drugbank_id)
                # if no information about this drugbank id exists then do not use this drugbank id
                if name == '':
                    delete_index.append(i - 1)
                    continue

                # to avoid alternative identifier
                query = '''Match (c:Compound) Where lower(c.name)='%s' Return c'''
                query = query % (name.lower())
                results = g.run(query)
                first_entry = results.evaluate()
                if first_entry != None:
                    delete_index.append(i - 1)
                    alternative_ids.append(first_entry['identifier'])
                    pubchem = str(pubchem_stereo) + ',' + first_entry[
                        'pubChem_id'] if 'pubChem_id' in first_entry else str(pubchem_stereo)
                    query = '''MATCH (d:drugSider{stitchIDstereo:"%s"}), (c:Compound{identifier:"%s"})
                    Set c.pubChem_id="%s", c.sider="yes", c.resource=["hetionet","SIDER"]
                    Create (c)-[:equal_to_drug_Sider]->(d) '''
                    query = query % (stitch_stereo, first_entry['identifier'], pubchem)
                    g.run(query)
                    mapped_to_hetionet = True
                    continue
                url = 'http://www.drugbank.ca/drugs/' + drugbank_id
                query = '''MATCH (d:drugSider{stitchIDstereo:"%s"})
                Create (c:Compound{identifier:"%s", pubChem_id:"%s", name:"%s",hetionet:"no", sider:"yes", resource:["SIDER"], inchi:"%s", inchikey:"%s", license:"CC0 1.0", source:"DrugBank via SIDER", url:"%s"})
                Create (c)-[:equal_to_drug_Sider]->(d) '''
                query = query % (stitch_stereo, drugbank_id, pubchem_stereo, name, inchi, inchikey, url)



            else:
                pubchem = str(pubchem_stereo) + ',' + first_entry['pubChem_id'] if 'pubChem_id' in first_entry else str(
                    pubchem_stereo)
                query = '''MATCH (d:drugSider{stitchIDstereo:"%s"}), (c:Compound{identifier:"%s"})
                Set c.pubChem_id="%s", c.hetionet="yes", c.sider="yes", c.resource=["hetionet","SIDER"]
                Create (c)-[:equal_to_drug_Sider]->(d) '''
                query = query % (stitch_stereo, drugbank_id, pubchem)

                mapped_to_hetionet = True
            g.run(query)

        # if all drugbank ids of do not appeare in the updated drugbank db then it is not mapped
        delete_index = list(reversed(delete_index))
        if len(delete_index) == len(drugbank_ids) and not len(alternative_ids) > 0:
            counter_with_one_which_is_removed += 1
            without_chemical.write(
                '|'.join(dict_sider_drug_with_drugbank_ids[pubchem_stereo]) + '\t' + str(pubchem_stereo) + '\n')

            query = '''MATCH (d:drugSider{stitchIDstereo:"%s"})
            Remove d.how_mapped '''
            query = query % (stitch_stereo)
            g.run(query)
            print(how_mapped)
        else:
            if mapped_to_hetionet:
                counter_mapped_to_hetionet += 1
            else:
                counter_new += 1
        # delete drugbank id without chemical information
        for index in delete_index:
            dict_sider_drug_with_drugbank_ids[pubchem_stereo].pop(index)

        dict_sider_drug_with_drugbank_ids[pubchem_stereo].extend(alternative_ids)

    print('number of mappe which has only an illegal drugbank id:' + str(counter_with_one_which_is_removed))
    print('number of stitch with theoretically a drugbank id:' + str(counter))
    print('mapped to hetionet:' + str(counter_mapped_to_hetionet))
    print('new compounds in hetionet:' + str(counter_new))
    # all drugs which are not mapped with sider get the property sider:'no'
    query = '''Match (c:Compound) Where not Exists(c.sider) 
    Set  c.sider='no', c.pubChem_id=""'''
    g.run(query)


'''
dictionary with compound-Se as key and value is a list of all different information
information :
    0:lowerFreq
    1:freq
    2:placebo
    3:upperfreq
    4:placebolowerfreq
    5:placebofreq
    6:placeboupperfreq
'''
dict_compound_SE_connection_informations = {}

'''
find all connection drug-se from sider for every compound-Se in hetionet and save all the information in a dictionary
'''


def find_all_compound_SE_pairs_of_sider():
    for stereo_pubchemID, drugbank_ids in dict_sider_drug_with_drugbank_ids.items():
        drugbank_ids = list(set(drugbank_ids))
        if len(drugbank_ids) > 0:

            stitch_stereo = dict_sider_drug[stereo_pubchemID].stitchIDstereo
            for drugbank_id in drugbank_ids:
                query = '''MATCH (n:drugSider{stitchIDstereo:"%s"})-[l:Causes]->(r) RETURN l,r.umlsIDmeddra '''
                query = query % (stitch_stereo)
                results = g.run(query)

                for connection, umlsId, in results:
                    lowerFreq = connection['lowerFreq'] if not connection['lowerFreq'] == None else ''
                    freq = connection['freq'] if not connection['freq'] == None else ''
                    placebo = connection['placebo'] if not connection['placebo'] == None else ''
                    upperFreq = connection['upperFreq'] if not connection['upperFreq'] == None else ''

                    placeboLowerFreq = connection['placeboLowerFreq'] if not connection[
                                                                                 'placeboLowerFreq'] == None else ''
                    placeboFreq = connection['placeboFreq'] if not connection['placeboFreq'] == None else ''
                    placeboUpperFreq = connection['placeboUpperFreq'] if not connection[
                                                                                 'placeboUpperFreq'] == None else ''

                    if not (drugbank_id, umlsId) in dict_compound_SE_connection_informations:
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)] = [[lowerFreq], [freq],
                                                                                           [placebo], [upperFreq],
                                                                                           [placeboLowerFreq],
                                                                                           [placeboFreq],
                                                                                           [placeboUpperFreq]]
                    else:
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][0].append(lowerFreq)
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][1].append(freq)
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][2].append(placebo)
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][3].append(upperFreq)
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][4].append(placeboLowerFreq)
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][5].append(placeboFreq)
                        dict_compound_SE_connection_informations[(drugbank_id, umlsId)][6].append(placeboUpperFreq)


# list of compound side effect tuple which create a new connection
list_tuple_compound_SE = []

'''
integration of relationship from sider into hetionet for the sider drugs which are mapped to drugbank id
'''


def integrate_relationship_from_sider_into_hetionet():
    # counter of the new compound-se connection
    number_of_new_connection = 0
    # counter of updated connection
    number_of_update_connection = 0
    # number of possible new connection
    number_of_in_new_connection = 0
    # file counter
    i = 1
    h = open('map_connection_of_sider_in_hetionet_' + str(i) + '.cypher', 'w',encoding='utf-8')
    h.write('begin \n')
    i += 1
    # counter of all queries
    counter_connection = 0

    # number of maximal queries per commit
    constrain_number = 20000
    # maximal number of queries in a cypher file
    creation_max = 1000000

    for (drugbank_id, umlsId), list_of_information in dict_compound_SE_connection_informations.items():
        # lowest frequency
        lowerFreq = str(min(list_of_information[0]))
        # all frequencies
        freqs = list_of_information[1]
        freqs_word = ''
        freqs_value = 0
        # count the number of frequencies with floats
        counter_values = 0
        for freq in freqs:
            # it is a word
            if '<' in freq:
                freqs_word = freq
            # is a float
            elif '%' in freq:
                counter_values += 1
                freq = freq.replace('%', '')
                # is a form .. to .. and take the average
                if '-' in freq:
                    freq = freq.split('-')
                    freq = (float(freq[0]) + float(freq[1])) / 2
                elif 'to' in freq:
                    freq = freq.split('to')
                    freq = (float(freq[0]) + float(freq[1])) / 2
                # only a number
                else:
                    freq = float(freq)
                freqs_value += freq
            else:
                freqs_word = freq
        # if at least on is a float take the average of all float frequencies
        if counter_values > 0:
            freq = str(freqs_value / counter_values) + '%'
        # take the word
        else:
            freq = freqs_word

        # maximal frequency
        upperFreq = str(max(list_of_information[3]))

        # placebo

        placebo = 'placebo' if 'placebo' in list_of_information[2] else ''

        # same as see above
        placeboFreqs = list_of_information[5]
        placeboFreqs_word = ''
        placeboFreqs_value = 0
        counter_values = 0
        for pfreq in placeboFreqs:
            if '<' in pfreq:
                placeboFreqs_word = pfreq
            elif '%' in pfreq:
                counter_values += 1
                pfreq = pfreq.replace('%', '')
                #                print(freq)
                if '-' in pfreq:
                    pfreq = pfreq.split('-')
                    pfreq = (float(pfreq[0]) + float(pfreq[1])) / 2
                elif 'to' in pfreq:
                    pfreq = pfreq.split('to')
                    pfreq = (float(pfreq[0]) + float(pfreq[1])) / 2
                else:
                    pfreq = float(pfreq)
                placeboFreqs_value += pfreq
            else:
                placeboFreqs_word = pfreq
        if counter_values > 0:
            placeboFreq = str(placeboFreqs_value / counter_values) + '%'
        else:
            placeboFreq = placeboFreqs_word

        placeboLowerFreq = str(min(list_of_information[4]))
        placeboUpperFreq = str(max(list_of_information[6]))

        licenses = 'CC BY-NC-SA 4.0'
        unbiased = 'false'
        source = 'SIDER 4.1'
        url = 'http://sideeffects.embl.de/se/' + umlsId

        query = '''Match (n:Compound{identifier:"%s"})-[l:CAUSES_CcSE]->(r:SideEffect{identifier:"%s"}) Return l'''
        query = query % (drugbank_id, umlsId)
        connection_their = g.run(query)
        first_entry = connection_their.evaluate()
        if first_entry == None:
            number_of_in_new_connection += 1
            if not (drugbank_id, umlsId) in list_tuple_compound_SE:
                query = '''Match (n:Compound{identifier:"%s"}),(r:SideEffect{identifier:"%s"}) 
                Create (n)-[:CAUSES_CcSE{url:"%s", source:"%s", unbiased:"%s", license:"%s", upperFrequency:"%s", resource:["SIDER"],  placebo:"%s", frequency:"%s", lowerFrequency:"%s",  placeboFrequency: "%s", placeboLowerFrequency: "%s", placeboUpperFrequency: "%s", hetionet:"no", sider:"yes", how_often_appears:"1"}]->(r);  \n'''
                query = query % (
                    drugbank_id, umlsId, url, source, unbiased, licenses, upperFreq, placebo, freq, lowerFreq,
                    placeboFreq,
                    placeboLowerFreq, placeboUpperFreq)
                number_of_new_connection += 1
                list_tuple_compound_SE.append((drugbank_id, umlsId))
            else:
                continue

        else:
            query = '''Match (n:Compound{identifier:"%s"})-[l:CAUSES_CcSE]->(r:SideEffect{identifier:"%s"}) 
            Set l.upperFrequency="%s", l.placebo="%s", l.frequency="%s", l.lowerFrequency="%s", l.placeboFrequency= "%s", l.resource:["SIDER","hetionet"], l.placeboLowerFrequency= "%s", l.placeboUpperFrequency= "%s", l.hetionet="yes", l.sider="yes", l.how_often_appears="1"; \n'''
            query = query % (
                drugbank_id, umlsId, upperFreq, placebo, freq, lowerFreq, placeboFreq, placeboLowerFreq,
                placeboUpperFreq)
            number_of_update_connection += 1

        h.write(query)

        # decide if a new commit block or file is generated
        counter_connection += 1
        if counter_connection % constrain_number == 0:
            h.write('commit \n')
            if counter_connection % creation_max == 0:
                h.close()
                h = open('map_connection_of_sider_in_hetionet_' + str(i) + '.cypher', 'w',encoding='utf-8')
                h.write('begin \n')
                i += 1
            h.write('begin \n')

    h.write('commit \n')
    h.write('begin \n')
    # all connection in hetionet which are not in sider get the properties none
    query = '''Match ()-[l:CAUSES_CcSE]-() Where not exists(l.frequency)
            Set l.upperFrequency="", l.placebo="", l.frequency="", l.lowerFrequency="", l.placeboFrequency= "", l.placeboLowerFrequency= "", l.placeboUpperFrequency= "", l.hetionet="yes", l.sider="no", l.how_often_appears="0", l.resource:["hetionet"]; \n'''
    h.write(query)
    h.write('commit ')

    print('Number of possible new connection:' + str(number_of_in_new_connection))
    print('Number of new connection:' + str(number_of_new_connection))
    print('Number of update connection:' + str(number_of_update_connection))
    print('all connection that will be integrated:' + str(counter_connection))
    print(i)


'''
a fuction for all function that are used for drug integration
'''


def integration_drug():
    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in all compounds from hetionet in dictionary')

    load_compounds_from_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in all drugs from sider in dictionary')

    load_sider_drug_in_dict()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print(
        'Load in all important information from the short from of chemical.source.v4.0.tsv and app them in dictionary')

    give_drugbank_ids_with_use_of_stitch_information()

    #    print('###########################################################################################################################')
    #    
    #    print (datetime.datetime.utcnow())
    #    print('Make a smaller file of stitch inchikeys for the stitch stereo (stitch flat) which did not get a drugbank id')
    #    
    #    make_a_smaller_file_of_stitch_inchikey_and_chemical()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in stitch name in a dictionary')

    load_in_stitch_name()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all for all stereo the inchikey in a dictionary')

    load_in_stitch_inchikeys()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map the stitch inchikeys to the inchikeys (alternative inchikeys) from drugbank')

    map_inchikeys_to_drugbank()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map the stitch name to the name, synonyms, product ingredients name and brand names from drugbank')

    map_name_to_drugbank()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate sider drugs into hetionet')

    integrate_sider_drugs_into_hetionet()


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map drugs from sider to hetionet')

    integration_drug()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Merge the edge information')

    find_all_compound_SE_pairs_of_sider()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate sider connection into hetionet')

    integrate_relationship_from_sider_into_hetionet()

    print(
        '###########################################################################################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
