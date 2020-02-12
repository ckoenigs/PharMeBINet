# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:16:45 2017

@author: Cassandra
"""
from py2neo import Graph
import datetime
import sys, csv
from collections import defaultdict
import gzip


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
        self.resource = resource
        self.xrefs = xrefs


# list all compound ids in hetionet
list_compound_in_hetionet = []

# dictionary with all compounds with drugbank id as key and class DrugHetionet as value
dict_all_drug = {}

# dictionary with all drugs from sider with the stereo id as key and class DrugSider as value
dict_sider_drug = {}

# dictionary inchikey to compound id
dict_inchikey_to_compound = {}

# dictioanry name to chemical
dict_name_to_chemical = {}

# dictionary chembl to drugbank id
dict_chembl_to_drugbank_id = {}

#dictionary synonyms chemical ids
dict_synonyms_to_chemicals_ids={}
'''
create connection to neo4j
'''


def create_connection_with_neo4j():
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


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
    query = 'MATCH (n:Chemical) RETURN n '
    results = g.run(query)

    for result, in results:
        identifier = result['identifier']
        inchikey = result['inchikey'] if 'inchikey' in result else ''
        if not inchikey in dict_inchikey_to_compound and inchikey != '':
            dict_inchikey_to_compound[inchikey] = [identifier]
        elif not inchikey == '':
            dict_inchikey_to_compound[inchikey].append(identifier)
        inchi = result['inchi']
        name = result['name'] if 'name' in result else ''
        if not name in dict_name_to_chemical and name != '':
            dict_name_to_chemical[name] = set([identifier])
        elif name != '':
            dict_name_to_chemical[name].add(identifier)

        synonyms=result['synonyms']
        if synonyms:
            for synonym in synonyms:
                if not synonym in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[synonym]=set()
                dict_synonyms_to_chemicals_ids[synonym].add(identifier)
        resource = result['resource']
        xrefs = result['xrefs'] if 'xrefs' in result else []
        for xref in xrefs:
            if xref.startswith('PubChem Compound:'):
                print('huhuh')
            elif xref.startswith('PubChem Substance:'):
                print('huhu')
        chembl_id = result['ChEMBL'] if 'ChEMBL' in result else ''
        if not chembl_id in dict_chembl_to_drugbank_id and chembl_id != '':
            dict_chembl_to_drugbank_id[chembl_id] = []
        if chembl_id != '':
            dict_chembl_to_drugbank_id[chembl_id].append(identifier)

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
dict_sider_drug_with_chemical_ids = defaultdict(list)

# files with all mapping for the different how_mapped mmethods
map_stereo_id_to_drugbank_id = open('drug/Sider_drug_map_stereo_id_to_drugbank.tsv', 'w', encoding='utf-8')
csv_map_stereo_id_to_drugbank_id = csv.writer(map_stereo_id_to_drugbank_id, delimiter='\t')
csv_map_stereo_id_to_drugbank_id.writerow(['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_flat_id_same_as_stereo_to_drugbank_id = open('drug/Sider_drug_map_flat_id_same_as_stereo_id_to_drugbank.tsv', 'w',
                                                 encoding='utf-8')
csv_map_flat_id_same_as_stereo_to_drugbank_id = csv.writer(map_flat_id_same_as_stereo_to_drugbank_id, delimiter='\t')
csv_map_flat_id_same_as_stereo_to_drugbank_id.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_flat_id_to_drugbank_id = open('drug/Sider_drug_map_flat_id_to_drugbank.tsv', 'w', encoding='utf-8')
csv_map_flat_id_to_drugbank_id = csv.writer(map_flat_id_to_drugbank_id, delimiter='\t')
csv_map_flat_id_to_drugbank_id.writerow(['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_to_inchikey_to_drugbank_id = open('drug/Sider_drug_map_stereo_to_inchikey_to_drugbank.tsv', 'w',
                                             encoding='utf-8')
csv_map_stereo_to_inchikey_to_drugbank_id = csv.writer(map_stereo_to_inchikey_to_drugbank_id, delimiter='\t')
csv_map_stereo_to_inchikey_to_drugbank_id.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative = open(
    'drug/Sider_drug_map_stereo_to_inchikey_to_drugbank_inchikeys_alternative.tsv', 'w', encoding='utf-8')
csv_map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative = csv.writer(
    map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative, delimiter='\t')
csv_map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_name_to_drugbank_id_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_name.tsv', 'w',
                                           encoding='utf-8')
csv_map_stereo_name_to_drugbank_id_name = csv.writer(map_stereo_name_to_drugbank_id_name, delimiter='\t')
csv_map_stereo_name_to_drugbank_id_name.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_name_to_drugbank_id_synonym_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_synonym_name.tsv', 'w',
                                                   encoding='utf-8')
csv_map_stereo_name_to_drugbank_id_synonym_name = csv.writer(map_stereo_name_to_drugbank_id_synonym_name,
                                                             delimiter='\t')
csv_map_stereo_name_to_drugbank_id_synonym_name.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_name_to_drugbank_id_brand_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_brand_name.tsv', 'w',
                                                 encoding='utf-8')
csv_map_stereo_name_to_drugbank_id_brand_name = csv.writer(map_stereo_name_to_drugbank_id_brand_name, delimiter='\t')
csv_map_stereo_name_to_drugbank_id_brand_name.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_name_to_drugbank_id_extra_name = open('drug/Sider_drug_map_stereo_name_to_drugbank_extra_name.tsv', 'w',
                                                 encoding='utf-8')
csv_stereo_name_to_drugbank_id_extra_name = csv.writer(map_stereo_name_to_drugbank_id_extra_name, delimiter='\t')
csv_stereo_name_to_drugbank_id_extra_name.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_stereo_chembl_to_drugbank_id = open('drug/Sider_drug_map_stereo_chembl_to_drugbank.tsv', 'w',
                                                 encoding='utf-8')
csv_map_stereo_chembl_to_drugbank_id = csv.writer(map_stereo_chembl_to_drugbank_id, delimiter='\t')
csv_map_stereo_chembl_to_drugbank_id.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

map_flat_inchikey_to_drugbank_id = open('drug/Sider_drug_map_stereo_flat_inchikey_to_drugbank.tsv', 'w',
                                                 encoding='utf-8')
csv_map_flat_inchikey_to_drugbank_id = csv.writer(map_flat_inchikey_to_drugbank_id, delimiter='\t')
csv_map_flat_inchikey_to_drugbank_id.writerow(
    ['stitch id flat', 'stitch id stereo', 'drugbank ids seperated with |'])

# dictionary with how_mapped as key and file as value
dict_how_mapped_to_file = {'stitch stereo id to drugbank ids': csv_map_stereo_id_to_drugbank_id,
                           'stitch flat id (same as stereo is) to drugbank ids': csv_map_flat_id_same_as_stereo_to_drugbank_id,
                           'stitch flat id to drugbank ids': csv_map_flat_id_to_drugbank_id,
                           'stitch stereo id inchikey to drugbank ids': csv_map_stereo_to_inchikey_to_drugbank_id,
                           'stitch stereo id alternativ inchikey to drugbank ids': csv_map_stereo_to_inchikey_to_drugbank_id_inchikey_alternative,
                           'stitch stereo id name to chemical ids name': csv_map_stereo_name_to_drugbank_id_name,
                           'stitch stereo id name to chemical ids synonyms': csv_map_stereo_name_to_drugbank_id_synonym_name,
                           'stitch stereo id name to drugbank ids brand names': csv_map_stereo_name_to_drugbank_id_brand_name,
                           'stitch stereo id name to drugbank ids extra_name names': csv_stereo_name_to_drugbank_id_extra_name,
                           'stitch stereo id with chembl to drugbank ids':csv_map_stereo_chembl_to_drugbank_id,
                           'stitch flat id inchikey to drugbank ids':csv_map_flat_inchikey_to_drugbank_id}

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
    part_exist=False
    f=None
    try:
        f=open('StitchData/chemical.sources.v5.0_part.tsv', 'r', encoding='utf-8')
        csv_reader = csv.reader(f, delimiter='\t')
        part_exist=True
    except OSError:
        f = gzip.open('StitchData/chemical.sources.v5.0.tsv.gz', 'rt')
        writer=open('StitchData/chemical.sources.v5.0_part.tsv', 'w', encoding='utf-8')
        csv_writer=csv.writer(writer,delimiter='\t')
        csv_reader = csv.reader(f, delimiter='\t')
    if not part_exist:
        csv_writer.writerow(next(csv_reader))
    else:
        next(csv_reader)
    list_of_sources = set()
    for line in csv_reader:
        if line[0].startswith('CIDm'):
            stitch_flat = int(line[0][4:])
            stitch_stereo = int(line[1][4:])
            if stitch_stereo==47725:
                print('lalala')
            xref_source = line[2]
            list_of_sources.add(xref_source)
            xref = line[3]
            if xref_source not in ['DrugBank', 'ChEMBL']:
                continue
            if not part_exist:
                csv_writer.writerow(line)
            # get durgbank id with stitch stereo id in pubchem form
            if xref_source == 'DrugBank':
                if stitch_stereo in dict_sider_drug:
                    if xref in dict_all_drug:
                        dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id to drugbank ids')
                        dict_sider_drug_with_chemical_ids[stitch_stereo].append(xref)
                # get drugbank id with use of flat id in pubchem form
                if stitch_flat in dict_flat_to_stereo:
                    if xref in dict_all_drug:
                        stereos = dict_flat_to_stereo[stitch_flat]
                        if stitch_flat == stitch_stereo:
                            dict_flat_to_drugbank_same_stereo[stitch_flat].append(xref)

                        for stereo_id in stereos:
                            dict_sider_drug[stereo_id].set_how_mapped('stitch flat id to drugbank ids')
                            dict_sider_drug_with_chemical_ids[stereo_id].append(xref)
            else:
                if stitch_stereo in dict_sider_drug:
                    if xref in dict_chembl_to_drugbank_id:
                        dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id with chembl to drugbank ids')
                        dict_sider_drug_with_chemical_ids[stitch_stereo].extend(dict_chembl_to_drugbank_id[xref])
                # get drugbank id with use of flat id in pubchem form
                if stitch_flat in dict_flat_to_stereo:
                    if xref in dict_all_drug:
                        if stitch_flat == stitch_stereo:
                            dict_flat_to_drugbank_same_stereo[stitch_flat].append(dict_chembl_to_drugbank_id[xref])

                        for stereo_id in dict_flat_to_stereo[stitch_flat]:
                            dict_sider_drug[stereo_id].set_how_mapped('stitch flat id with chembl to drugbank ids')
                            dict_sider_drug_with_chemical_ids[stereo_id].append(dict_chembl_to_drugbank_id[xref])

    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))
    print('number of mapped stitch flat ids to drugbank:' + str(len(dict_flat_to_drugbank)))
    print('number of mapped stitch flat ids to drugbank (same stereo):' + str(len(dict_flat_to_drugbank_same_stereo)))
    print(list_of_sources)

    # check if a sider drug which was not mapped with the stereo id has a mapped flat id
    g = open('not_mapped_pubchem_ids_from_stitch.txt', 'w', encoding='utf-8')
    # counter for mapped with flat id where flat and stereo are the same
    i = 0
    # counter for mapped with flat id where flat and stereo are not the same
    j = 0
    for pubchem_stereo, drug in dict_sider_drug.items():
        if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
            pubchem_flat = int(drug.stitchIDflat[3:]) - 100000000
            if pubchem_flat in dict_flat_to_drugbank_same_stereo:
                i += 1
                dict_sider_drug_with_chemical_ids[pubchem_stereo] = dict_flat_to_drugbank_same_stereo[pubchem_flat]
                dict_sider_drug[pubchem_stereo].set_how_mapped(
                    'stitch flat id (same as stereo is) to drugbank ids maybe with chembl')
            elif pubchem_flat in dict_flat_to_drugbank:
                j += 1
                dict_sider_drug_with_chemical_ids[pubchem_stereo] = dict_flat_to_drugbank[pubchem_flat]
                dict_sider_drug[pubchem_stereo].set_how_mapped('stitch flat id to drugbank ids maybe with chembl')
            else:
                list_of_not_mapped_stitch_stereo.append(pubchem_stereo)
                list_of_not_mapped_stitch_flat.append(pubchem_flat)
                g.write(str(pubchem_stereo) + ',')
    g.close()
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))


# dictionary with stitch stereo id in pubchem form as key and value is the name
dict_stereo_key_name = {}

# dictionary with flat in pubchem form as key and value is the name
dict_flat_key_name = {}

# dictionary with name as key and list with flat and stereo id
dict_name_to_flat_stereo_id = {}



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
    part_exist = False
    f = None
    try:
        f = open('StitchData/chemicals.inchikeys.v5.0_part.tsv', 'r', encoding='utf-8')
        part_exist = True
        csv_reader = csv.reader(f, delimiter='\t')
    except OSError:
        f = gzip.open('StitchData/chemicals.inchikeys.v5.0.tsv.gz', 'rt')
        writer = open('StitchData/chemicals.inchikeys.v5.0_part.tsv', 'w', encoding='utf-8')
        csv_writer = csv.writer(writer, delimiter='\t')
        csv_reader = csv.reader(f, delimiter='\t')
    if not part_exist:
        csv_writer.writerow(next(csv_reader))
    else:
        next(csv_reader)
    # list of all index from in this step mapped stereo ids
    delete_index = []
    for line in csv_reader:
        stitch_flat = int(line[0][4:])
        stitch_stereo = int(line[1][4:])
        if (stitch_stereo in dict_sider_drug or stitch_flat in dict_flat_to_stereo) and not part_exist:
            csv_writer.writerow(line)
        inchikey = line[3]
        if stitch_stereo in list_of_not_mapped_stitch_stereo:
            if inchikey in dict_inchikey_to_compound:
                delete_index.append(list_of_not_mapped_stitch_stereo.index(stitch_stereo))
                dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id inchikey to drugbank ids')
                dict_sider_drug_with_chemical_ids[stitch_stereo] = dict_inchikey_to_compound[inchikey]

        else:
            if stitch_flat in dict_flat_to_stereo:
                if inchikey in dict_inchikey_to_compound:
                    stitch_stereos = dict_flat_to_stereo[stitch_flat]
                    for stereo in stitch_stereos:
                        if stereo in list_of_not_mapped_stitch_stereo:
                            delete_index.append(list_of_not_mapped_stitch_stereo.index(stereo))
                            dict_sider_drug[stereo].set_how_mapped('stitch flat id inchikey to drugbank ids')
                            dict_sider_drug_with_chemical_ids[stereo] = dict_inchikey_to_compound[inchikey]
    # removed all mapped stitch stereo ids from the not mapped list
    delete_index = list(set(delete_index))
    delete_index.sort()
    delete_index = list(reversed(delete_index))
    for index in delete_index:
        list_of_not_mapped_stitch_stereo.pop(index)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))


'''
load in stitch name and save them in a dictionary
0:chemical
1:name    
2:molecular_weight        
3:SMILES_string

'''


def load_in_stitch_name():
    part_exist = False
    f = None
    try:
        f = open('StitchData/chemicals.v5.0_part.tsv', 'r', encoding='utf-8')
        part_exist = True
        csv_reader = csv.reader(f, delimiter='\t')
    except OSError:
        f = gzip.open('StitchData/chemicals.v5.0.tsv.gz', 'rt')
        writer = open('StitchData/chemicals.v5.0_part.tsv', 'w', encoding='utf-8')
        csv_writer = csv.writer(writer, delimiter='\t')
        csv_reader = csv.reader(f, delimiter='\t')
    if not part_exist:
        csv_writer.writerow(next(csv_reader))
    else:
        next(csv_reader)
    # list of all index from in this step mapped stereo ids
    delete_index = []
    for line in csv_reader:
        name = line[1].lower()
        if name=='goserelin':
            print('test')

        if line[0][3:4] == 's':
            pubchemStereo_ID = int(line[0][4:])
            if pubchemStereo_ID in dict_sider_drug  and not part_exist:
                csv_writer.writerow(line)
            if pubchemStereo_ID in dict_sider_drug:
                dict_stereo_key_name[pubchemStereo_ID] = name

            if pubchemStereo_ID  in list_of_not_mapped_stitch_stereo:
                if name in dict_name_to_chemical:
                    delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchemStereo_ID))
                    dict_sider_drug[pubchemStereo_ID].set_how_mapped('stitch stereo id name to chemical ids name')
                    dict_sider_drug_with_chemical_ids[pubchemStereo_ID] = list(dict_name_to_chemical[name])
                elif name in dict_synonyms_to_chemicals_ids:
                    delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchemStereo_ID))
                    dict_sider_drug[pubchemStereo_ID].set_how_mapped('stitch stereo id name to chemical ids synonyms')
                    dict_sider_drug_with_chemical_ids[pubchemStereo_ID] = list(dict_synonyms_to_chemicals_ids[name])

        else:
            pubchem_flat_ID = int(line[0][4:])
            if  pubchem_flat_ID in dict_flat_to_stereo and not part_exist:
                csv_writer.writerow(line)
            dict_flat_key_name[pubchem_flat_ID] = name
            dict_name_to_flat_stereo_id[name.lower()] = [pubchem_flat_ID, '']

    # removed all mapped stitch stereo ids from the not mapped lis
    delete_index = list(set(delete_index))
    delete_index.sort()
    delete_index = list(reversed(delete_index))
    for index in delete_index:
        list_of_not_mapped_stitch_stereo.pop(index)

    print(len(dict_stereo_key_name))
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))



'''
map stitch to drugbank with use of stitch name to drugbank name, synonyms ,Product Ingredients name and brands name
properties from durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv:

'''


def map_name_to_drugbank():
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
                    if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                        dict_sider_drug[pubchem_stereo].set_how_mapped('stitch stereo id name to drugbank ids name')
                        dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                    else:
                        dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)

                if pubchem_flat in dict_flat_to_stereo:
                    pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                    for pubchem_stereo in pubchem_stereos:
                        if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                            found_a_drugbank = True
                            delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                            if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                dict_sider_drug[pubchem_stereo].set_how_mapped(
                                    'stitch stereo id name to drugbank ids name')
                                dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                            else:
                                dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)

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
                                if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                    dict_sider_drug[pubchem_stereo].set_how_mapped(
                                        'stitch stereo id name to drugbank ids synonym names')
                                    dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                                else:
                                    dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)

                            if pubchem_flat in dict_flat_to_stereo:
                                pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                                for pubchem_stereo in pubchem_stereos:
                                    if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                        found_a_drugbank = True
                                        delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                        if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                            dict_sider_drug[pubchem_stereo].set_how_mapped(
                                                'stitch stereo id name to drugbank ids synonym names')
                                            dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                                        else:
                                            dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)
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
                                if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                    dict_sider_drug[pubchem_stereo].set_how_mapped(
                                        'stitch stereo id name to drugbank ids extra_name names')
                                    dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                                else:
                                    dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)

                            if pubchem_flat in dict_flat_to_stereo:
                                pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                                for pubchem_stereo in pubchem_stereos:
                                    if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                        found_a_drugbank = True
                                        delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                        if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                            dict_sider_drug[pubchem_stereo].set_how_mapped(
                                                'stitch stereo id name to drugbank ids extra_name names')
                                            dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                                        else:
                                            dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)
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
                                if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                    dict_sider_drug[pubchem_stereo].set_how_mapped(
                                        'stitch stereo id name to drugbank ids brand names')
                                    dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                                else:
                                    dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)

                            if pubchem_flat in dict_flat_to_stereo:
                                pubchem_stereos = dict_flat_to_stereo[pubchem_flat]
                                for pubchem_stereo in pubchem_stereos:
                                    if pubchem_stereo in list_of_not_mapped_stitch_stereo:
                                        delete_index.append(list_of_not_mapped_stitch_stereo.index(pubchem_stereo))
                                        if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
                                            dict_sider_drug[pubchem_stereo].set_how_mapped(
                                                'stitch stereo id name to drugbank ids brand names')
                                            dict_sider_drug_with_chemical_ids[pubchem_stereo] = [drugbank_id]

                                        else:
                                            dict_sider_drug_with_chemical_ids[pubchem_stereo].append(drugbank_id)

    # removed all mapped stitch stereo ids from the not mapped lis
    delete_index = list(set(delete_index))
    delete_index.sort()
    delete_index = list(reversed(delete_index))
    for index in delete_index:
        list_of_not_mapped_stitch_stereo.pop(index)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))


'''
integrate sider drugs into hetionet directly. For the compound which are already in hetionet only some properties 
are add and a connection to the sider drug is generated. Further new compound for hetionet a gerneted which has also a
 connection to  the sider drug.  
'''


def integrate_sider_drugs_into_hetionet():
    #cypher file
    cypher_file=open('cypher_drug.cypher','w',encoding='utf-8')
    
    query=query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/sider/output/mapped_drug.tsv" As line Fieldterminator '\t' Match (c:Chemical{identifier:line.chemical_id}), (d:drugSider{stitchIDstereo:line.sider_id}) Set c.xrefs=split(line.xrefs,'|'), c.sider="yes", c.resource=line.resource, d.name=line.name, d.how_mapped=line.how_mapped
                    Create (c)-[:equal_to_drug_Sider]->(d);\n'''
    cypher_file.write(query)
    cypher_file.close()

    header=['chemical_id','xrefs','resource','sider_id','name','how_mapped']
    file=open('output/mapped_drug.tsv','w',encoding='utf-8')
    csv_writer=csv.writer(file,delimiter='\t')
    csv_writer.writerow(header)

    # go through all mapped sider drugs and integrate them into hetionet
    for pubchem_stereo, chemical_ids in dict_sider_drug_with_chemical_ids.items():
        # if one of the drugbank ids are in hetionet
        # print(chemical_ids)
        # print(dict_sider_drug[pubchem_stereo].how_mapped)
        chemical_ids = list(set(chemical_ids))
        dict_sider_drug_with_chemical_ids[pubchem_stereo] = chemical_ids
        stitch_stereo = dict_sider_drug[pubchem_stereo].stitchIDstereo
        stitch_flat = dict_sider_drug[pubchem_stereo].stitchIDflat
        pubchem_flat = int(stitch_flat[4:])
        if pubchem_stereo in dict_stereo_key_name:
            name = dict_stereo_key_name[pubchem_stereo]
        elif pubchem_flat in dict_flat_key_name:
            name = dict_flat_key_name[pubchem_flat]
        else:
            name = ''
        #
        # print(pubchem_stereo)
        how_mapped = dict_sider_drug[pubchem_stereo].how_mapped

        # generate the mapping files for the different mapping steps
        string_drugbank_ids = "|".join(chemical_ids)
        dict_how_mapped_to_file[how_mapped].writerow([dict_sider_drug[pubchem_stereo].stitchIDflat , dict_sider_drug[
            pubchem_stereo].stitchIDstereo , string_drugbank_ids ])

        for chemical_id in chemical_ids:
            resource=dict_all_drug[chemical_id].resource
            resource.append('SIDER')
            resource=list(set(resource))
            resource='|'.join(resource)

            xrefs = dict_all_drug[chemical_id].xrefs
            xrefs.append('PubChem Compound:'+str(pubchem_stereo))
            xrefs = list(set(xrefs))
            xrefs = '|'.join(xrefs)
            csv_writer.writerow([chemical_id,xrefs,resource,stitch_stereo,name,how_mapped])

    file.close()

    # write all drugs from sider that did not mape in a csv file
    file=open('output/not_mapped_drugs.tsv','w',encoding='utf-8')
    csv_writer=csv.writer(file,delimiter='\t')
    csv_writer.writerow(['stereo','flat','name'])

    for pubchem_stereo in list_of_not_mapped_stitch_stereo:

        stitch_stereo = dict_sider_drug[pubchem_stereo].stitchIDstereo
        stitch_flat = dict_sider_drug[pubchem_stereo].stitchIDflat
        if pubchem_stereo in dict_stereo_key_name:
            name = dict_stereo_key_name[pubchem_stereo]
        elif pubchem_flat in dict_flat_key_name:
            name = dict_flat_key_name[pubchem_flat]
        else:
            name = ''
        csv_writer.writerow([stitch_stereo,stitch_flat,name])


    # all drugs which are not mapped with sider get the property sider:'no'

    # the general cypher file to update all chemicals and relationship which are not from aeolus
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = '''Match (c:Compound) Where not Exists(c.sider) 
    Set  c.sider='no';\n'''
    cypher_general.write(query)
    cypher_general.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path sider')
        
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Map drugs from sider to hetionet')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in all compounds from hetionet in dictionary')

    load_compounds_from_hetionet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in all drugs from sider in dictionary')

    load_sider_drug_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print(
        'Load in all important information from the short from of chemical.source.v5.0.tsv and add them in dictionary')

    give_drugbank_ids_with_use_of_stitch_information()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all for all stereo the inchikey and map to chemical ids')

    load_in_stitch_inchikeys()


    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in stitch name and map to chemical ids')

    load_in_stitch_name()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Integrate sider drugs into hetionet')

    integrate_sider_drugs_into_hetionet()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
