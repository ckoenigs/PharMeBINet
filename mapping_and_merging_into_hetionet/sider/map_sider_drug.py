# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:16:45 2017

@author: Cassandra
"""
import datetime
import sys, csv
from collections import defaultdict
import gzip

sys.path.append("../..")
import create_connection_to_databases


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

# dictionary synonyms/name/brands chemical ids
dict_synonyms_to_chemicals_ids = {}

# dictionary_pubchem compound id to chemical id
dict_pubchem_to_chemical_ids = {}

'''
create connection to neo4j
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


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
    query = 'MATCH (n:Chemical) Where not n:Product RETURN n '
    results = g.run(query)

    for result, in results:
        identifier = result['identifier']
        inchikey = result['inchikey'] if 'inchikey' in result else ''
        if not inchikey in dict_inchikey_to_compound and inchikey != '':
            dict_inchikey_to_compound[inchikey] = [identifier]
        elif not inchikey == '':
            dict_inchikey_to_compound[inchikey].append(identifier)
        inchi = result['inchi']
        name = result['name'].lower() if 'name' in result else ''
        if not name in dict_name_to_chemical and name != '':
            dict_name_to_chemical[name] = set([identifier])
        elif name != '':
            dict_name_to_chemical[name].add(identifier)

        synonyms = result['synonyms']
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if not synonym in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[synonym] = set()
                dict_synonyms_to_chemicals_ids[synonym].add(identifier)
        brand_name_and_companys = result['international_brands_name_company']
        if brand_name_and_companys:
            for brand_name_and_company in brand_name_and_companys:
                brand_name = brand_name_and_company.split('::')[0]
                brand_name = brand_name.lower()
                if not brand_name in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[brand_name] = set()
                dict_synonyms_to_chemicals_ids[brand_name].add(identifier)
        resource = result['resource']
        # take mixtures name as synonym if it has only one ingredient and it is only the drug name!
        mixtures_name_ingredients = result['mixtures_name_ingredients'] if 'mixtures_name_ingredients' in result else []
        for mixture_name_ingredient in mixtures_name_ingredients:
            splitted = mixture_name_ingredient.split('::')
            mixture_name = splitted[0].lower()
            if not '+' in splitted[1]:
                solo_ingredient = splitted[1].lower()
                if name == solo_ingredient:
                    if not mixture_name in dict_synonyms_to_chemicals_ids:
                        dict_synonyms_to_chemicals_ids[mixture_name] = set()
                    dict_synonyms_to_chemicals_ids[mixture_name].add(identifier)

        xrefs = result['xrefs'] if 'xrefs' in result else []
        for xref in xrefs:
            if xref.startswith('PubChem Compound:'):
                id = int(xref.split(':')[1])
                if id not in dict_pubchem_to_chemical_ids:
                    dict_pubchem_to_chemical_ids[id] = set()
                dict_pubchem_to_chemical_ids[id].add(identifier)
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

        # https://www.biostars.org/p/155342/
        pubchem_flat = int(stitchIDflat[3:]) - 100000000
        pubchem_stereo = int(stitchIDstereo[3:])

        dict_sider_drug[pubchem_stereo] = drug
        # # check if some map already if not add to not mapped list
        # if pubchem_stereo in dict_pubchem_to_chemical_ids:
        #     dict_sider_drug[pubchem_stereo].set_how_mapped('drugbank to pubchem stereo')
        #     dict_sider_drug_with_chemical_ids[pubchem_stereo].extend(dict_pubchem_to_chemical_ids[pubchem_stereo])
        # elif pubchem_flat in dict_pubchem_to_chemical_ids:
        #     dict_sider_drug[pubchem_stereo].set_how_mapped('drugbank to pubchem flat')
        #     dict_sider_drug_with_chemical_ids[pubchem_stereo].extend(dict_pubchem_to_chemical_ids[pubchem_flat])
        # else:
        list_of_not_mapped_stitch_stereo.add(pubchem_stereo)

        if not pubchem_flat in dict_flat_to_stereo:
            dict_flat_to_stereo[pubchem_flat] = [pubchem_stereo]
        else:
            dict_flat_to_stereo[pubchem_flat].append(pubchem_stereo)

    print('number of drugs from sider:' + str(len(dict_sider_drug)))
    print('number of flat ids:' + str(len(dict_flat_to_stereo)))
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))


# dictionary with flat in pubchem form as key and a list of drugbank ids as values
dict_flat_to_drugbank = {}

# dictionary with flat in pubchem form as key and list of drugbank ids as value, but only the drugbank ids where stitch flat and stereo are the same
dict_flat_to_drugbank_same_stereo = defaultdict(list)

# dictionary with stereo id in pubchem form as key and drugbank ids as values
dict_sider_drug_with_chemical_ids = defaultdict(list)

'''
check for name mapping get the same results as the other method
'''


def check_with_name_mapping(pubchem_id, search_value, dict_key_name, dict_something_to_chemical_ids, is_element=False):
    name = dict_key_name[pubchem_id].lower() if pubchem_id in dict_key_name else ''
    splitted_name = name.rsplit('(', 1)[0]
    if len(splitted_name) > 0:
        name = splitted_name
    chemical_ids = dict_something_to_chemical_ids[search_value] if not is_element else set(
        dict_something_to_chemical_ids)

    # name and xref are the same identifier
    if name in dict_synonyms_to_chemicals_ids:
        chemical_ids_name = dict_synonyms_to_chemicals_ids[name]
        intersection = chemical_ids_name.intersection(chemical_ids)
        if intersection:
            chemical_ids = intersection
        else:
            return False, ''
    else:
        return False, ''
    return True, chemical_ids


'''
function to delete ids from list

'''


def delete_elements_from_list(delete_list):
    for entry in delete_list:
        if entry in list_of_not_mapped_stitch_stereo:
            list_of_not_mapped_stitch_stereo.remove(entry)


# list of all stitch stereo ids in pubchem form which are not mapped
list_of_not_mapped_stitch_stereo = set()

# list of all stitch flat ids in pubchem form which are not mapped
list_of_not_mapped_stitch_flat = []

'''
cHECK FOR THE PUBCHEM IDS IN THE DICTIONARY PUBCHEM TO chemical ids 
'''


def map_with_pubchem_id():
    # list of all index from in this step mapped stereo ids
    delete_list = set()
    for pubchem_id in list_of_not_mapped_stitch_stereo:
        stitch_flat = dict_sider_drug[pubchem_id].stitchIDflat
        pubchem_flat = int(stitch_flat[3:]) - 100000000

        if pubchem_id == 8982:
            print('huhu')

        # check if some map already if not add to not mapped list
        if pubchem_id in dict_pubchem_to_chemical_ids:
            # manual checked that methan do not map to activated charcoal (carbon)
            if pubchem_id == '297':
                continue
            # found, chemical_ids =check_with_name_mapping(pubchem_id,pubchem_id, dict_stereo_key_name, dict_pubchem_to_chemical_ids)
            # if not found:
            #     continue
            dict_sider_drug[pubchem_id].set_how_mapped('drugbank to pubchem stereo')
            dict_sider_drug_with_chemical_ids[pubchem_id].extend(dict_pubchem_to_chemical_ids[pubchem_id])
            delete_list.add(pubchem_id)
        elif pubchem_flat in dict_pubchem_to_chemical_ids:
            found, chemical_ids = check_with_name_mapping(pubchem_id, pubchem_flat, dict_stereo_key_name,
                                                          dict_pubchem_to_chemical_ids)
            if not found:
                continue

            dict_sider_drug[pubchem_id].set_how_mapped('drugbank to pubchem flat')
            dict_sider_drug_with_chemical_ids[pubchem_id].extend(chemical_ids)
            delete_list.add(pubchem_id)

    # removed all mapped stitch stereo ids from the not mapped list
    delete_elements_from_list(delete_list)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))


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
    part_exist = False
    f = None
    try:
        f = open('StitchData/chemical.sources.v5.0_part.tsv', 'r', encoding='utf-8')
        csv_reader = csv.reader(f, delimiter='\t')
        part_exist = True
    except OSError:
        f = gzip.open('StitchData/chemical.sources.v5.0.tsv.gz', 'rt')
        writer = open('StitchData/chemical.sources.v5.0_part.tsv', 'w', encoding='utf-8')
        csv_writer = csv.writer(writer, delimiter='\t')
        csv_reader = csv.reader(f, delimiter='\t')
    if not part_exist:
        csv_writer.writerow(next(csv_reader))
    else:
        next(csv_reader)
    list_of_sources = set()
    # list of all index from in this step mapped stereo ids
    delete_list = set()
    for line in csv_reader:
        if line[0].startswith('CIDm'):
            stitch_flat = int(line[0][4:])
            stitch_stereo = int(line[1][4:])
            xref_source = line[2]
            list_of_sources.add(xref_source)
            xref = line[3]
            if xref_source not in ['DrugBank', 'ChEMBL']:
                continue
            if not part_exist:
                csv_writer.writerow(line)
            # get durgbank id with stitch stereo id in pubchem form
            if xref_source == 'DrugBank':
                if stitch_stereo in list_of_not_mapped_stitch_stereo:
                    if xref in dict_all_drug:
                        found, chemical_ids = check_with_name_mapping(stitch_stereo, '', dict_stereo_key_name,
                                                                      xref, is_element=True)
                        if not found:
                            continue
                        delete_list.add(stitch_stereo)
                        dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id to drugbank ids')
                        dict_sider_drug_with_chemical_ids[stitch_stereo].append(xref)
                # get drugbank id with use of flat id in pubchem form
                if stitch_flat in dict_flat_to_stereo:
                    if xref in dict_all_drug:
                        stereos = dict_flat_to_stereo[stitch_flat]
                        if stitch_flat == stitch_stereo:
                            dict_flat_to_drugbank_same_stereo[stitch_flat].append(xref)

                        for stereo_id in stereos:
                            if not stereo_id in list_of_not_mapped_stitch_stereo:
                                continue

                            # todo check if this should be the flat once
                            found, chemical_ids = check_with_name_mapping(stitch_stereo, '', dict_stereo_key_name,
                                                                          xref, is_element=True)
                            if not found:
                                continue
                            delete_list.add(stereo_id)
                            dict_sider_drug[stereo_id].set_how_mapped('stitch flat id to drugbank ids')
                            dict_sider_drug_with_chemical_ids[stereo_id].append(xref)
            else:
                if stitch_stereo in list_of_not_mapped_stitch_stereo:
                    if xref in dict_chembl_to_drugbank_id:
                        found, chemical_ids = check_with_name_mapping(stitch_stereo, '', dict_stereo_key_name,
                                                                      xref, is_element=True)
                        if not found:
                            continue
                        delete_list.add(stitch_stereo)
                        dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id with chembl to drugbank ids')
                        dict_sider_drug_with_chemical_ids[stitch_stereo].extend(dict_chembl_to_drugbank_id[xref])
                # get drugbank id with use of flat id in pubchem form
                if stitch_flat in dict_flat_to_stereo:
                    if xref in dict_all_drug:
                        if stitch_flat == stitch_stereo:
                            dict_flat_to_drugbank_same_stereo[stitch_flat].append(dict_chembl_to_drugbank_id[xref])

                        for stereo_id in dict_flat_to_stereo[stitch_flat]:
                            if not stereo_id in list_of_not_mapped_stitch_stereo:
                                continue

                            found, chemical_ids = check_with_name_mapping(stitch_stereo, '', dict_stereo_key_name,
                                                                          xref, is_element=True)
                            if not found:
                                continue
                            delete_list.add(stereo_id)
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
    # removed all mapped stitch stereo ids from the not mapped list
    delete_elements_from_list(delete_list)

    for pubchem_stereo, drug in dict_sider_drug.items():
        if not pubchem_stereo in dict_sider_drug_with_chemical_ids:
            pubchem_flat = int(drug.stitchIDflat[3:]) - 100000000
            # if pubchem_flat in dict_flat_to_drugbank_same_stereo:
            #     i += 1
            #     dict_sider_drug_with_chemical_ids[pubchem_stereo] = dict_flat_to_drugbank_same_stereo[pubchem_flat]
            #     dict_sider_drug[pubchem_stereo].set_how_mapped(
            #         'stitch flat id (same as stereo is) to drugbank ids maybe with chembl')
            if pubchem_flat in dict_flat_to_drugbank:
                j += 1
                dict_sider_drug_with_chemical_ids[pubchem_stereo] = dict_flat_to_drugbank[pubchem_flat]
                dict_sider_drug[pubchem_stereo].set_how_mapped('stitch flat id to drugbank ids maybe with chembl')
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
    delete_list = set()
    for line in csv_reader:
        stitch_flat = int(line[0][4:])

        stitch_stereo = int(line[1][4:])
        if (stitch_stereo in dict_sider_drug or stitch_flat in dict_flat_to_stereo) and not part_exist:
            csv_writer.writerow(line)
        inchikey = line[3]
        if stitch_stereo in list_of_not_mapped_stitch_stereo:
            if inchikey in dict_inchikey_to_compound:
                found, chemical_ids = check_with_name_mapping(stitch_stereo, inchikey, dict_stereo_key_name,
                                                              dict_inchikey_to_compound)
                if not found:
                    continue
                delete_list.add(stitch_stereo)
                dict_sider_drug[stitch_stereo].set_how_mapped('stitch stereo id inchikey to drugbank ids')
                dict_sider_drug_with_chemical_ids[stitch_stereo] = chemical_ids

        # else:
        #     if stitch_flat in dict_flat_to_stereo:
        #         if inchikey in dict_inchikey_to_compound:
        #             stitch_stereos = dict_flat_to_stereo[stitch_flat]
        #             for stereo in stitch_stereos:
        #                 if stereo in list_of_not_mapped_stitch_stereo:
        #                     found, chemical_ids = check_with_name_mapping(stitch_stereo, inchikey, dict_stereo_key_name,
        #                                                                   dict_inchikey_to_compound)
        #                     if not found:
        #                         continue
        #                     delete_list.add(stereo)
        #                     dict_sider_drug[stereo].set_how_mapped('stitch flat id inchikey to drugbank ids')
        #                     dict_sider_drug_with_chemical_ids[stereo] = chemical_ids
    # removed all mapped stitch stereo ids from the not mapped list
    delete_elements_from_list(delete_list)
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
    for line in csv_reader:
        name = line[1].lower()

        if line[0][3:4] == 's':
            pubchemStereo_ID = int(line[0][4:])
            if pubchemStereo_ID == 16129672:
                print('huhu')
            if pubchemStereo_ID in dict_sider_drug and not part_exist:
                csv_writer.writerow(line)
            if pubchemStereo_ID in dict_sider_drug:
                dict_stereo_key_name[pubchemStereo_ID] = name


        else:
            pubchem_flat_ID = int(line[0][4:])
            if pubchem_flat_ID in dict_flat_to_stereo and not part_exist:
                csv_writer.writerow(line)
            dict_flat_key_name[pubchem_flat_ID] = name
            dict_name_to_flat_stereo_id[name.lower()] = [pubchem_flat_ID, '']

    print(len(dict_stereo_key_name))


'''
mapping with only name
'''


def map_with_names():
    # list of all index from in this step mapped stereo ids
    delete_list = set()
    for pubchemStereo_ID in list_of_not_mapped_stitch_stereo:
        if not pubchemStereo_ID in dict_stereo_key_name:
            continue
        name = dict_stereo_key_name[pubchemStereo_ID]
        if name in dict_name_to_chemical:
            delete_list.add(pubchemStereo_ID)
            dict_sider_drug[pubchemStereo_ID].set_how_mapped('stitch stereo id name to chemical ids name')
            dict_sider_drug_with_chemical_ids[pubchemStereo_ID] = list(dict_name_to_chemical[name])
        elif name in dict_synonyms_to_chemicals_ids:
            delete_list.add(pubchemStereo_ID)
            dict_sider_drug[pubchemStereo_ID].set_how_mapped('stitch stereo id name to chemical ids synonyms')
            dict_sider_drug_with_chemical_ids[pubchemStereo_ID] = list(dict_synonyms_to_chemicals_ids[name])

    # removed all mapped stitch stereo ids from the not mapped lis
    delete_elements_from_list(delete_list)
    print('number of mapped stitch stereo ids to drugbank:' + str(len(dict_sider_drug_with_chemical_ids)))
    print('number not mapped stitch stereo:' + str(len(list_of_not_mapped_stitch_stereo)))


'''
integrate sider drugs into hetionet directly. For the compound which are already in hetionet only some properties 
are add and a connection to the sider drug is generated. Further new compound for hetionet a gerneted which has also a
 connection to  the sider drug.  
'''


def integrate_sider_drugs_into_hetionet():
    # cypher file
    cypher_file = open('cypher_drug.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/sider/output/mapped_drug.tsv" As line Fieldterminator '\t' Match (c:Chemical{identifier:line.chemical_id}), (d:drugSider{stitchIDstereo:line.sider_id}) Set c.xrefs=split(line.xrefs,'|'), c.sider="yes", c.resource=split(line.resource,'|'), d.name=line.name, d.how_mapped=line.how_mapped
                    Create (c)-[:equal_to_drug_Sider]->(d);\n'''
    cypher_file.write(query)
    cypher_file.close()

    header = ['chemical_id', 'xrefs', 'resource', 'sider_id', 'name', 'how_mapped']
    file = open('output/mapped_drug.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
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
        # dict_how_mapped_to_file[how_mapped].writerow([dict_sider_drug[pubchem_stereo].stitchIDflat , dict_sider_drug[
        #     pubchem_stereo].stitchIDstereo , string_drugbank_ids ])

        for chemical_id in chemical_ids:
            resource = dict_all_drug[chemical_id].resource
            resource.append('SIDER')
            resource = list(set(resource))
            resource = '|'.join(resource)

            xrefs = dict_all_drug[chemical_id].xrefs
            xrefs.append('PubChem Compound:' + str(pubchem_stereo))
            xrefs = list(set(xrefs))
            xrefs = '|'.join(xrefs)
            csv_writer.writerow([chemical_id, xrefs, resource, stitch_stereo, name, how_mapped])

    file.close()

    # write all drugs from sider that did not mape in a csv file
    file = open('output/not_mapped_drugs.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['stereo', 'flat', 'name'])

    for pubchem_stereo in list_of_not_mapped_stitch_stereo:

        stitch_stereo = dict_sider_drug[pubchem_stereo].stitchIDstereo
        stitch_flat = dict_sider_drug[pubchem_stereo].stitchIDflat
        pubchem_flat = int(stitch_flat[3:]) - 100000000
        if pubchem_stereo in dict_stereo_key_name:
            name = dict_stereo_key_name[pubchem_stereo]
        elif pubchem_flat in dict_flat_key_name:
            name = dict_flat_key_name[pubchem_flat]
        else:
            name = ''
        csv_writer.writerow([stitch_stereo, stitch_flat, name])

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
    print('Load in stitch names')

    load_in_stitch_name()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Map with  drugbank pubchem xref')

    map_with_pubchem_id()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all for all stereo the inchikey and map to chemical ids')

    load_in_stitch_inchikeys()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print(
        'Load in all important information from the short from of chemical.source.v5.0.tsv and add them in dictionary')

    give_drugbank_ids_with_use_of_stitch_information()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in stitch name and map to chemical ids')

    map_with_names()

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
