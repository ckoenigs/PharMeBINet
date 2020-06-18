# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 11:55:50 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys

sys.path.append('../aeolus/')
import get_drugbank_information


class DrugHetionet:
    """
    identifier:string (Drugbank ID)
    inchikey: string
    inchi: string
    name :string
    """

    def __init__(self, identifier, inchikey, inchi, name):
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name


class DrugCTD:
    """
    idType: string	(MESH)
    chemical_id: string	
    synonyms: string list divided by |	
    drugBankIDs:string list divided by |
    name:string
    how_mapped: string
    """

    def __init__(self, idType, chemical_id, synonyms, drugBankID, name, drugBankIDs):
        self.idType = idType
        self.chemical_id = chemical_id
        self.synonyms = synonyms
        if drugBankIDs != '':
            drugBankIDs = drugBankIDs.split('|')
        else:
            drugBankIDs = []
        self.drugBankIDs = drugBankIDs
        self.name = name
        drugBankIDs.append(drugBankID)
        self.drugBankIDs = drugBankIDs

    def set_drugbankIDs(self, drugbank_ids):
        self.drugBankIDs = drugbank_ids

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all compounds from hetionet and  key is drugbank id and value is class DrugHetionet
dict_drugs_hetinet = {}

# dictionary from ctd with all drugs that has a drugbank id, key is chemical id and value is class DrugCTD
dict_drugs_CTD_with_drugbankIDs = {}

# dictionary with all drugs without a drugbank from ctd, key is chemical id and value is class DrugCTD
dict_drugs_CTD_without_drugbankIDs = {}

# list of mesh id from ctd which are not mapped
list_drug_CTD_without_drugbank_id = []

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = mdb.connect('localhost', 'root', 'Za8p7Tf', 'RxNorm')


'''
load in all compounds from hetionet in dictionary and add to dictionary
properties:
    license
    identifier
    inchikey
    inchi
    name
    source
    url
'''


def load_compounds_from_hetionet():
    query = 'MATCH (n:Compound) RETURN n '
    results = g.run(query)
    i = 0

    for result, in results:
        i += 1
        identifier = result['identifier']
        inchikey = result['inchikey']
        inchi = result['inchi']
        name = result['name']
        #        resource=result['resource']

        drug = DrugHetionet(identifier, inchikey, inchi, name)

        dict_drugs_hetinet[identifier] = drug

    print('In hetionet are:' + str(len(dict_drugs_hetinet)) + ' drugs')


# dictionary for all names to mesh
dict_name_synonym_to_mesh = {}

'''
load in all drugs from CTD from neo4j and divide the into the dictionary with drugbank ids and without
properties:
    casRN	
    idType	
    chemical_id	
    synonyms	
    drugBankIDs	
    parentIDs	
    drugBankID
    name
    definition	
    parentTreeNumbers
    treeNumbers
'''


def load_drugs_from_CTD():
    query = 'MATCH (n:CTDchemical) RETURN n'

    results = g.run(query)

    for result, in results:
        idType = result['idType']
        chemical_id = result['chemical_id']
        synonyms = result['synonyms']
        drugBankID = result['drugBankID']
        drugBankIDs = result['drugBankIDs']
        name = result['name'].lower()
        drug = DrugCTD(idType, chemical_id, synonyms, drugBankID, name, drugBankIDs)
        if drugBankID == '':
            dict_drugs_CTD_without_drugbankIDs[chemical_id] = drug
            list_drug_CTD_without_drugbank_id.append(chemical_id)
            dict_name_synonym_to_mesh[name] = chemical_id
            synonyms = synonyms.split('|')
            for synonym in synonyms:
                dict_name_synonym_to_mesh[synonym.lower()] = chemical_id
        else:
            dict_drugs_CTD_with_drugbankIDs[chemical_id] = drug
            dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids from ctd')

    print('In ctd drugs without drugbank ids:' + str(len(dict_drugs_CTD_without_drugbankIDs)))
    print('In ctd drugs with drugbank ids:' + str(len(dict_drugs_CTD_with_drugbankIDs)))


# dictionary with all mesh id, which have not a drugbank id, and value are the umls cuis
dict_mesh_to_cuis = {}

# list of mesh ids that have no cui
list_mesh_without_cui = []

'''
Find for all drugs from CTD without a drugbank id umls cuis with use of umls
Id type of drug are MESH
'''


def find_cui_for_ctd_drugs():
    # count the number of mesh ids which could be only mapped to umls cui with use of the name
    count_map_with_name = 0
    for mesh_id, drug in dict_drugs_CTD_without_drugbankIDs.items():
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB, STR From MRCONSO Where SAB='MSH' and CODE= '%s';")
        query = query % (mesh_id)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            list_cuis = []
            for (cui, lat, code, sab, label) in cur:
                list_cuis.append(cui)
            list_cuis = list(set(list_cuis))
            dict_mesh_to_cuis[mesh_id] = list_cuis
        else:

            cur = con.cursor()
            # if not mapped map the name to umls cui
            query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where lower(STR)= %s And SAB='MSH' ;")
            rows_counter = cur.execute(query, dict_drugs_CTD_without_drugbankIDs[mesh_id].name.lower())
            if rows_counter > 0:
                print(mesh_id)
                count_map_with_name += 1
                list_cuis = []
                for (cui, lat, code, sab) in cur:
                    list_cuis.append(cui)
                print(list(set(list_cuis)))
                dict_mesh_to_cuis[mesh_id] = list_cuis
            else:
                list_mesh_without_cui.append(mesh_id)

    print('number of name mapped:' + str(count_map_with_name))
    print('number of mesh with cuis:' + str(len(dict_mesh_to_cuis)))
    print('number of mesh without cuis:' + str(len(list_mesh_without_cui)))


# list of mesh id which are not mapped to drugbank with umls cuis mapped ctd
list_cuis_not_mapped_drugbank_id = []

'''
map umls cui to drugbank id with use of umls
'''


def map_cui_to_drugbank_with_umls():
    # mesh ids which are mapped to drugbank in this step
    delete_mapped_mesh = []
    for mesh_id, cuis in dict_mesh_to_cuis.items():
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where SAB = 'DRUGBANK' AND CUI in ('%s') ;")
        cuis = "','".join(cuis)
        query = query % (cuis)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            drugbank_ids = []
            for (cui, lat, code, sab) in cur:
                drugbank_ids.append(code)
            drugbank_ids = list(set(drugbank_ids))
            dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
            delete_mapped_mesh.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(drugbank_ids)
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use umls cui to map to drugbank ids')
        else:
            list_cuis_not_mapped_drugbank_id.append(mesh_id)

    # remove all mapped mesh ids from not_mapped list
    delete_mapped_mesh = list(set(delete_mapped_mesh))
    delete_mapped_mesh.sort()
    delete_mapped_mesh = list(reversed(delete_mapped_mesh))
    for index in delete_mapped_mesh:
        list_drug_CTD_without_drugbank_id.pop(index)

    print('length of list of mesh ids with all drugbank ids from umls:' + str(len(dict_drugs_CTD_with_drugbankIDs)))
    print('length of list of cuis without drugbank ids from umls:' + str(len(list_cuis_not_mapped_drugbank_id)))
    print('number of mesh ids which are not mapped:' + str(len(list_drug_CTD_without_drugbank_id)))


# dictionary with all mesh id, which have not a drugbank id, and value are the rxcuis
dict_mesh_to_rxcuis = {}

# list of mesh ids that have no rxcui
list_mesh_without_rxcui = []

# dictionary of rxcui to mesh ids
dict_rxcui_to_mesh = {}
'''
map mesh to rxcui
'''


def find_rxcui_for_ctd_drugs():
    # counter of mapped mesh ids with name to rxcui
    counter_map_to_rxcui_with_name = 0
    # number of not mapped mesh ids
    count_not_mapped = 0
    for mesh_id in list_drug_CTD_without_drugbank_id:
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = 'MSH' and CODE='%s' ;")
        query = query % (mesh_id)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            list_rxcuis = []
            for (rxcui, lat, code, sab, label) in cur:
                list_rxcuis.append(rxcui)
                if not rxcui in dict_rxcui_to_mesh:
                    dict_mesh_to_rxcuis[rxcui] = [mesh_id]
                else:
                    dict_mesh_to_rxcuis[rxcui].append(mesh_id)
            list_rxcuis = list(set(list_rxcuis))
            dict_mesh_to_rxcuis[mesh_id] = list_rxcuis
        else:
            count_not_mapped += 1
            list_mesh_without_cui.append(mesh_id)

    print('number of mesh with rxcuis:' + str(len(dict_mesh_to_cuis)))
    print('number of mesh without rxcuis:' + str(len(list_mesh_without_cui)))
    print('number of mapped with name:' + str(counter_map_to_rxcui_with_name))
    print('number of not mapped mesh:' + str(count_not_mapped))


# list of mesh id which are not mapped to drugbank with umlshe mapped ctd
list_rxcuis_not_mapped_drugbank_id = []

'''
map cui to drugbank id with use of rxnorm
'''


def map_rxcui_to_drugbank_with_rxnorm():
    delete_cui = []
    delete_mapped_mesh_ids = []
    for mesh_id, rxcuis in dict_mesh_to_rxcuis.items():
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB From RXNCONSO Where SAB = 'DRUGBANK' AND RXCUI in ('%s') ;")
        rxcuis = "','".join(rxcuis)
        query = query % (rxcuis)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            drugbank_ids = []
            for (rxcui, lat, code, sab) in cur:
                drugbank_ids.append(code)
            drugbank_ids = list(set(drugbank_ids))
            dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(drugbank_ids)
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use rxnorm rxcui to map to drugbank ids')
            if mesh_id in list_cuis_not_mapped_drugbank_id:
                delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))
        else:
            list_rxcuis_not_mapped_drugbank_id.append(mesh_id)

    # remove all mapped mesh ids from not_mapped umls cui list
    delete_cui = list(set(delete_cui))
    delete_cui.sort()
    delete_cui = list(reversed(delete_cui))
    for index in delete_cui:
        list_cuis_not_mapped_drugbank_id.pop(index)

    # remove all mapped mesh ids from not_mapped list
    delete_mapped_mesh_ids = list(set(delete_mapped_mesh_ids))
    delete_mapped_mesh_ids.sort()
    delete_mapped_mesh_ids = list(reversed(delete_mapped_mesh_ids))
    for index in delete_mapped_mesh_ids:
        list_drug_CTD_without_drugbank_id.pop(index)

    print('length of list of mesh id with all drugbank ids from rxnorm:' + str(len(dict_drugs_CTD_with_drugbankIDs)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_not_mapped_drugbank_id)))
    print('length of list of cuis without drugbank ids from umls:' + str(len(list_cuis_not_mapped_drugbank_id)))
    print('number of mesh ids which are not mapped:' + str(len(list_drug_CTD_without_drugbank_id)))


'''
load map rxnorm id to drugbank _id from dhimmel inchikey and use this to map the rest
properties:
    0:rxcui
    1:drugbank ids seperated with |
'''


def map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey_4.tsv', 'r')
    next(f)
    delete_rxcui = []
    delete_cui = []
    delete_mapped_mesh_ids = []
    for line in f:
        splitted = line.split('\t')
        rxnorm_cui = splitted[0]
        drugbank_ids = splitted[1].split('\n')[0].split('|')
        if rxnorm_cui in dict_rxcui_to_mesh:
            mesh_ids = dict_rxcui_to_mesh[rxnorm_cui]
            for mesh_id in mesh_ids:
                if mesh_id in list_rxcuis_not_mapped_drugbank_id:
                    drugbank_ids = list(set(drugbank_ids))
                    dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                    delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                    dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(drugbank_ids)
                    dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped(
                        'use map table rxcui to map to drugbank ids')
                    if mesh_id in list_cuis_not_mapped_drugbank_id:
                        delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))
                    delete_rxcui.append(list_rxcuis_not_mapped_drugbank_id.index(mesh_id))

    # remove all mapped mesh ids from not_mapped rxnorm list
    delete_rxcui = list(set(delete_rxcui))
    delete_rxcui.sort()
    delete_rxcui = list(reversed(delete_rxcui))
    for index in delete_rxcui:
        list_rxcuis_not_mapped_drugbank_id.pop(index)

    # remove all mapped mesh ids from not_mapped umls cui list
    delete_cui = list(set(delete_cui))
    delete_cui.sort()
    delete_cui = list(reversed(delete_cui))
    for index in delete_cui:
        list_cuis_not_mapped_drugbank_id.pop(index)

    # remove all mapped mesh ids from not_mapped list
    delete_mapped_mesh_ids = list(set(delete_mapped_mesh_ids))
    delete_mapped_mesh_ids.sort()
    delete_mapped_mesh_ids = list(reversed(delete_mapped_mesh_ids))
    for index in delete_mapped_mesh_ids:
        list_drug_CTD_without_drugbank_id.pop(index)

    print('length of list of mesh id with all drugbank ids from rxnorm:' + str(len(dict_drugs_CTD_with_drugbankIDs)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_not_mapped_drugbank_id)))
    print('length of list of cuis without drugbank ids from umls:' + str(len(list_cuis_not_mapped_drugbank_id)))
    print('number of mesh ids which are not mapped:' + str(len(list_drug_CTD_without_drugbank_id)))


'''
map mesh to drugbank by mapping the name or synonym of ctd to name, brands, extra names or synonym of drugbank
properties Drugbank:
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


def map_ctd_chemical_to_drugbank_with_lable_map():
    f = open('../drugbank/data/durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv', 'r')
    next(f)
    delete_cui = []
    delete_mapped_mesh_ids = []
    for line in f:
        splitted = line.split('\t')
        drugbank_id = splitted[0]
        name = splitted[1].lower()
        synonyms = splitted[9].replace('[', '').replace(']', '').replace("'", "").lower()
        synonyms = synonyms.split('|')
        extra_names = splitted[13].replace('[', '').replace(']', '').replace("'", "").lower()
        extra_names = extra_names.split('|')
        brands = splitted[14].replace('[', '').replace(']', '').replace("'", "").lower()
        brands = brands.split('|')
        if name in dict_name_synonym_to_mesh:
            mesh_id = dict_name_synonym_to_mesh[name]
            if mesh_id in list_drug_CTD_without_drugbank_id:
                dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs([drugbank_id])
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use  name to map to drugbank ids')
                if mesh_id in list_cuis_not_mapped_drugbank_id:
                    delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))
        else:
            found_a_drugbank_id = False
            for synonym in synonyms:
                if synonym in dict_name_synonym_to_mesh:
                    found_a_drugbank_id = True
                    mesh_id = dict_name_synonym_to_mesh[synonym]
                    if mesh_id in list_drug_CTD_without_drugbank_id:
                        dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                        delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                        dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs([drugbank_id])
                        dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use  name to map to drugbank ids')
                        if mesh_id in list_cuis_not_mapped_drugbank_id:
                            delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))

            if not found_a_drugbank_id:
                for extra_name in extra_names:
                    if extra_name in dict_name_synonym_to_mesh:
                        found_a_drugbank_id = True
                        mesh_id = dict_name_synonym_to_mesh[extra_name]
                        #                        print(mesh_id)
                        #                        print(dict_drugs_CTD_without_drugbankIDs[mesh_id].name)
                        if mesh_id in list_drug_CTD_without_drugbank_id:
                            dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs([drugbank_id])
                            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use  name to map to drugbank ids')
                            if mesh_id in list_cuis_not_mapped_drugbank_id:
                                delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))

            if not found_a_drugbank_id:
                for brand in brands:
                    if brand in dict_name_synonym_to_mesh:
                        found_a_drugbank_id = True
                        mesh_id = dict_name_synonym_to_mesh[brand]
                        if mesh_id in list_drug_CTD_without_drugbank_id:
                            dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs([drugbank_id])
                            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use  name to map to drugbank ids')
                            if mesh_id in list_cuis_not_mapped_drugbank_id:
                                delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))

    # remove all mapped mesh ids from not_mapped cuis list
    delete_cui = list(set(delete_cui))
    delete_cui.sort()
    delete_cui = list(reversed(delete_cui))
    for index in delete_cui:
        list_cuis_not_mapped_drugbank_id.pop(index)

    # remove all mapped mesh ids from not_mapped list
    delete_mapped_mesh_ids = list(set(delete_mapped_mesh_ids))
    delete_mapped_mesh_ids.sort()
    delete_mapped_mesh_ids = list(reversed(delete_mapped_mesh_ids))
    for index in delete_mapped_mesh_ids:
        list_drug_CTD_without_drugbank_id.pop(index)


# dictionary for all ctd mesh ids which are mapped to hetionet with mesh as key and value are drugbank ids
dict_ctd_to_compound = {}

# list of new generated compound with mesh ids
list_new_compounds = []

# all how_mapped files with mappings
map_ctd = open('chemical/ctd_chemical_to_compound_map_from_ctd.tsv', 'w')
map_ctd.write('MESH \t drugbank_ids with | as seperator  \n')

map_with_cui = open('chemical/ctd_chemical_to_compound_map_use_UMLS_cui.tsv', 'w')
map_with_cui.write('MESH \t drugbank_ids with | as seperator  \n')

map_with_rxcui = open('chemical/ctd_chemical_to_compound_map_use_rxnorm_rxcui.tsv', 'w')
map_with_rxcui.write('MESH \t drugbank_ids with | as seperator  \n')

map_with_rxcui_table = open('chemical/ctd_chemical_to_compound_map_use_rxcui_map_table.tsv', 'w')
map_with_rxcui_table.write('MESH \t drugbank_ids with | as seperator  \n')

map_with_name = open('chemical/ctd_chemical_to_compound_map_use_names.tsv', 'w')
map_with_name.write('MESH \t drugbank_ids with | as seperator  \n')

# dictionary with how_mapped as key and file as value
dict_how_mapped_file = {
    'drugbank ids from ctd': map_ctd,
    'use umls cui to map to drugbank ids': map_with_cui,
    'use map table rxcui to map to drugbank ids': map_with_rxcui_table,
    'use rxnorm rxcui to map to drugbank ids': map_with_rxcui,
    'use  name to map to drugbank ids': map_with_name}

# generate file with mesh id and a list of drugbank ids and where they are from
multiple_drugbankids = open('ctd_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('MESH id \t drugbank_ids with | as seperator \t where are it from \n')

'''
map drugbank id from ctd to compound in hetionet
'''


def map_ctd_to_hetionet_compound():
    for mesh, drug in dict_drugs_CTD_with_drugbankIDs.items():
        drugbank_ids = drug.drugBankIDs
        mapped = []
        string_drugbank_ids = "|".join(drugbank_ids)
        how_mapped = drug.how_mapped

        dict_how_mapped_file[how_mapped].write(mesh + '\t' + string_drugbank_ids + '\n')

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(mesh + '\t' + string_drugbank_ids + '\t' + how_mapped + '\n')

        for drugbank_id in drugbank_ids:
            if drugbank_id in dict_drugs_hetinet:
                mapped.append(drugbank_id)
        if len(mapped) > 0:
            dict_ctd_to_compound[mesh] = mapped
        else:
            list_new_compounds.append(mesh)

    print('mapped to hetionet compound:' + str(len(dict_ctd_to_compound)))
    print('will be new generated:' + str(len(list_new_compounds)))

    # all not mapped ctd chemicals
    g = open('chemical/not_mapped_drugs.tsv', 'w')
    g.write('mesh id \t name \t synonyms\n')

    for chemical_id, drug in dict_drugs_CTD_without_drugbankIDs.items():
        if not chemical_id in dict_drugs_CTD_with_drugbankIDs:
            #            print(chemical_id)
            #            print(drug.name)
            #            print(drug.synonyms.encode('utf-8'))
            synonym = drug.synonyms.encode('utf-8')
            #            print(synonym+'\n'+drug.name.encode('utf-8'))
            g.write(chemical_id.encode('utf-8') + '\t' + drug.name.encode('utf-8') + '\t' + synonym + '\n')
    g.close()


# dictionary how_mapped mit delete number
dict_how_mapped_delete_counter = {}

'''
integration of ctd chemicals in hetionet
'''


def integration_of_ctd_chemicals_into_hetionet_compound():
    get_drugbank_information.load_all_drugbank_ids_in_dictionary()
    # count all mesh ids which are mapped to a drugbank id
    counter = 0
    # count mapped to drugbank id, but the drugbank id is old or has no chemical information
    counter_illegal_drugbank_ids = 0
    for mesh_id, drug in dict_drugs_CTD_with_drugbankIDs.items():
        counter += 1
        delete_index = []
        # manual check that this mapped wrong
        if mesh_id in ['C018375', 'D007483']:
            continue
        index = 0
        how_mapped = drug.how_mapped
        drugbank_ids = drug.drugBankIDs
        for drugbank_id in drugbank_ids:

            index += 1
            query = '''Match (c:Compound{identifier:"%s"}) Return c '''
            query = query % (drugbank_id)
            results = g.run(query)
            first_entry = results.evaluate()

            if first_entry == None:

                [name, inchi, inchikey] = get_drugbank_information.get_drugbank_information(drugbank_id)
                if name == '':
                    delete_index.append(index - 1)
                    continue
                url = 'http://www.drugbank.ca/drugs/' + drugbank_id
                url_ctd = 'http://ctdbase.org/detail.go?type=chem&acc=' + mesh_id
                query = ''' MATCH (n:CTDchemical{chemical_id:"%s"})
                    Set n.mapped_drugbank_ids=["%s"], n.how_mapped="%s" 
                    Create (c:Compound{identifier:"%s",inchikey:"%s", inchi:"%s", url:"%s",resource:["CTD"],ndf_rt:"no", sider:"no", hetionet:"no", aeolus:"no", ctd_url:"%s", name:"%s",source:"Drugbank via CTD"  , ctd:"yes", pubChem:"", license:" Copyright 2002-2012 MDI Biological Laboratory. All rights reserved. Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved."})    
                    Create (c)-[:equal_chemichal_CTD]->(n)
                    '''
                query = query % (
                    mesh_id, drugbank_id, dict_drugs_CTD_with_drugbankIDs[mesh_id].how_mapped, drugbank_id, inchikey,
                    inchi, url,
                    url_ctd, name)
            else:
                resource = first_entry['resource'] if 'resource' in first_entry else []
                resource.append("CTD")
                resource = list(set(resource))
                string_resource = '","'.join(resource)
                url = 'http://ctdbase.org/detail.go?type=chem&acc=' + mesh_id
                query = ''' MATCH (n:CTDchemical{chemical_id:"%s"}), (c:Compound{identifier:"%s"})
                Set c.ctd="yes", c.ctd_url="%s", c.resource=["%s"]
                Create (c)-[:equal_chemichal_CTD]->(n)
                '''
                query = query % (mesh_id, drugbank_id, url, string_resource)

            g.run(query)

        # add the mapping typ which mapped to a not usable durgbank id
        delete_index = list(set(delete_index))
        delete_index.sort()
        delete_index = list(reversed(delete_index))
        if len(delete_index) == len(drugbank_ids):
            counter_illegal_drugbank_ids += 1
            if how_mapped in dict_how_mapped_delete_counter:
                dict_how_mapped_delete_counter[how_mapped] += 1
            else:
                dict_how_mapped_delete_counter[how_mapped] = 1
        for index in delete_index:
            drug.drugBankIDs.pop(index)

    # all compounds which are not mapped with ctd drug get as property ctd='no'
    query = ''' MATCH  (c:Compound) Where not exists(c.ctd)
            Set c.ctd="no", c.ctd_url="" '''
    g.run(query)

    print('number of ctd drug which has no legal drugbank id:' + str(counter_illegal_drugbank_ids))
    print('number of all ctd which are mapped include the one with illegal drugbank ids:' + str(counter))
    print(dict_how_mapped_delete_counter)


# list causes new pairs
list_causes_new_pairs = []

# dictionary induces new pair 
list_inducese_new_pairs = []

# dictionary treates new pair
list_treats_new_pairs = []

'''
create cypher file to integrate ctd connection into hetionet
'''


def intigrate_connection_from_ctd_to_hetionet():
    #count how many new treats association are generated
    number_of_new_connection_association = 0
    # count how many  treats association are already included
    number_of_update_connection_association = 0
    # count how many new causes association are generated
    number_of_new_connection_causes = 0
    # count how many causes association are already included
    number_of_update_connection_causes = 0
    # count how many new induces association are generated
    number_of_new_connection_induce = 0
    # count how many induces association are already included
    number_of_update_connection_induce = 0

    i = 1
    h = open('map_connection_of_cdt_in_hetionet_' + str(i) + '.cypher', 'w')
    h.write('begin \n')
    i += 1

    counter_connection = 0

    constrain_number = 20000
    creation_max = 1000000

    for mesh_id, drug in dict_drugs_CTD_with_drugbankIDs.items():
        url_ctd = 'http://ctdbase.org/detail.go?type=chem&acc=' + mesh_id
        # it is for phenotye and disease as side effects
        drugbank_ids = drug.drugBankIDs
        for drugbank_id in drugbank_ids:

            # all chemical outcome connection
            query = '''Match (n:CTDchemical{chemical_id:"%s"})-[l:Causes]-(r) Return l,r.cui '''
            query = query % (mesh_id)
            results = g.run(query)

            if results:
                for (relationship, cui) in results:
                    phenotypeActionDegreeType = relationship['phenotypeActionDegreeType'] if relationship['phenotypeActionDegreeType'] != None else ''
                    query = '''Match (c:Compound{identifier:"%s"})-[r:CAUSES_CcSE]->(s:SideEffect{identifier:"%s"}) Return r '''
                    query = query % (drugbank_id, cui)
                    connection_exist = g.run(query)
                    first_entry = connection_exist.evaluate()
                    if first_entry == None:
                        if not (drugbank_id, cui) in list_causes_new_pairs:
                            number_of_new_connection_causes += 1
                            query = '''Match (c:Compound{identifier:"%s"}), (s:SideEffect{identifier:"%s"}) 
                            Create(c)-[r:CAUSES_CcSE{how_often_appears:"1", phenotype_action_degree_type:"%s", url_ctd:"%s" ,url:"%s",unbiased:false, resource:['CTD'],license:" Copyright 2002-2012 MDI Biological Laboratory. All rights reserved. Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved.", ctd:"yes", sider:"no", hetionet:"no",upperFrequency:"", placebo:"", frequency:"", lowerFrequency:"",  placeboFrequency: "", placeboLowerFrequency: "", placeboUpperFrequency: ""}]->(s);\n '''
                            query = query % (drugbank_id, cui, phenotypeActionDegreeType, url_ctd, url_ctd)
                            list_causes_new_pairs.append((drugbank_id, cui))
                        else:
                            continue
                    else:
                        number_of_update_connection_causes += 1
                        resource = first_entry['resource'] if first_entry['resource'] != None else []
                        resource.append('CTD')
                        resource = '","'.join(resource)
                        how_often = str(int(first_entry['how_often_appears']) + 1) if first_entry['how_often_appears'] != None else '1'
                        query = '''Match (c:Compound{identifier:"%s"})-[l:CAUSES_CcSE]-(r:SideEffect{identifier:"%s"})
                        Set  l.how_often_appears="%s", l.resource=["%s"], l.ctd="yes", l.phenotype_action_degree_type="%s", l.url_ctd="%s";\n'''
                        query = query % (drugbank_id, cui, how_often, resource, phenotypeActionDegreeType, url_ctd)
                    #                g.run(query)
                    counter_connection += 1
                    h.write(query)
                    if counter_connection % constrain_number == 0:
                        h.write('commit \n')
                        if counter_connection % creation_max == 0:
                            h.close()
                            h = open('cypher/map_connection_of_ctd_in_hetionet_' + str(i) + '.cypher', 'w')
                            h.write('begin \n')
                            i += 1

                        else:
                            h.write('begin \n')

            # all induce connection from association table
            query = '''Match (n:CTDchemical{chemical_id:"%s"})-[l:Association{directEvidence:'marker/mechanism'}]-(r) Return l,r.doids '''
            query = query % (mesh_id)
            results = g.run(query)
            if results:
                for (rela, doids) in results:
                    inferenceScore = rela['inferenceScore'] if rela['inferenceScore'] != None else ''
                    pubMedIDs = rela['pubMedIDs'] if rela['pubMedIDs'] != None else ''
                    inferenceGeneSymbol = rela['inferenceGeneSymbol'] if rela['inferenceGeneSymbol'] != None else ''
                    directEvidence = rela['directEvidence'] if rela['directEvidence'] != None else ''
                    if len(doids) > 0:
                        for doid in doids:
                            query = '''Match (c:Compound{identifier:"%s"})-[r:INDUCES_CiD]->(s:Disease{identifier:"%s"}) Return r '''
                            query = query % (drugbank_id, doid)
                            connection_exist = g.run(query)
                            first_entry = connection_exist.evaluate()
                            if first_entry == None:
                                if not (drugbank_id, doid) in list_inducese_new_pairs:
                                    query = '''Match (c:Compound{identifier:"%s"}), (s:Disease{identifier:"%s"}) 
                                    Create(c)-[r:INDUCES_CiD{how_often_appears:"1",inferenceScore:"%s", pubMedIDs:"%s",inferenceGeneSymbol:"%s",directEvidence:"%s", url_ctd:"%s"  ,unbiased:false, resource:['CTD'], ctd:"yes",ndf_rt:"no", license:"Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved."}]->(s);\n '''
                                    query = query % (
                                        drugbank_id, doid, inferenceScore, pubMedIDs, inferenceGeneSymbol,
                                        directEvidence,
                                        url_ctd)
                                    number_of_new_connection_induce += 1
                                    list_inducese_new_pairs.append((drugbank_id, doid))
                                else:
                                    continue

                            else:
                                number_of_update_connection_induce += 1
                                resource = first_entry['resource'] if first_entry['resource'] != None else []
                                resource.append('CTD')
                                resource = '","'.join(resource)
                                how_often = str(int(first_entry['how_often_appears']) + 1) if first_entry[
                                                                                                  'how_often_appears'] != None else '1'
                                query = '''Match (c:Compound{identifier:"%s"})-[l:INDUCES_CiD]-(r:Disease{identifier:"%s"})
                                Set  l.how_often_appears="%s", l.resource=["%s"], l.ctd="yes", l.inferenceScore="%s", l.pubMedIDs="%s", l.inferenceGeneSymbol="%s", l.directEvidence="%s", l.url_ctd="%s";\n '''
                                query = query % (
                                    drugbank_id, doid, how_often, resource, inferenceScore, pubMedIDs,
                                    inferenceGeneSymbol,
                                    directEvidence, url_ctd)
                            #                g.run(query)
                            counter_connection += 1
                            h.write(query)
                            if counter_connection % constrain_number == 0:
                                h.write('commit \n')
                                if counter_connection % creation_max == 0:
                                    h.close()
                                    h = open('cypher/map_connection_of_ctd_in_hetionet_' + str(i) + '.cypher', 'w')
                                    h.write('begin \n')
                                    i += 1
                                else:
                                    h.write('begin \n')

            # all relationships where a drug treats a disease
            query = '''Match (n:CTDchemical{chemical_id:"%s"})-[l:Association{directEvidence:'therapeutic'}]-(r) Return l,r.doids '''
            query = query % (mesh_id)
            results = g.run(query)
            if results:
                for (rela, doids) in results:
                    inferenceScore = rela['inferenceScore'] if rela['inferenceScore'] != None else ''
                    pubMedIDs = rela['pubMedIDs'] if rela['pubMedIDs'] != None else ''
                    inferenceGeneSymbol = rela['inferenceGeneSymbol'] if rela['inferenceGeneSymbol'] != None else ''
                    directEvidence = rela['directEvidence'] if rela['directEvidence'] != None else ''
                    if len(doids) > 0:
                        for doid in doids:
                            query = '''Match (c:Compound{identifier:"%s"})-[r:TREATS_CtD]->(s:Disease{identifier:"%s"}) Return r '''
                            query = query % (drugbank_id, doid)
                            connection_exist = g.run(query)
                            first_entry = connection_exist.evaluate()
                            if first_entry == None:
                                if not (drugbank_id, doid) in list_treats_new_pairs:
                                    number_of_new_connection_association += 1
                                    query = '''Match (c:Compound{identifier:"%s"}), (s:Disease{identifier:"%s"}) 
                                    Create(c)-[r:TREATS_CtD{how_often_appears:"1",inferenceScore:"%s", pubMedIDs:"%s",inferenceGeneSymbol:"%s",directEvidence:"%s", url_ctd:"%s"  ,unbiased:false, resource:['CTD'], ctd:"yes", hetionet:"no", license:" Copyright 2002-2012 MDI Biological Laboratory. All rights reserved. Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved."}]->(s);\n '''
                                    query = query % (
                                        drugbank_id, doid, inferenceScore, pubMedIDs, inferenceGeneSymbol,
                                        directEvidence,
                                        url_ctd)
                                    list_treats_new_pairs.append((drugbank_id, doid))
                                else:
                                    continue

                            else:
                                number_of_update_connection_association += 1
                                resource = first_entry['resource'] if first_entry['resource'] != None else []
                                resource.append('CTD')
                                resource.append('Hetionet')
                                resource = '","'.join(resource)
                                how_often = str(int(first_entry['how_often_appears']) + 1) if first_entry['how_often_appears'] != None else '1'
                                query = '''Match (c:Compound{identifier:"%s"})-[l:TREATS_CtD]-(r:Disease{identifier:"%s"})
                                Set  l.how_often_appears="%s", l.resource=["%s"], l.ctd="yes", l.hetionet="yes", l.inferenceScore="%s", l.pubMedIDs="%s", l.inferenceGeneSymbol="%s", l.directEvidence="%s", l.url_ctd="%s";\n '''
                                query = query % (
                                    drugbank_id, doid, how_often, resource, inferenceScore, pubMedIDs,
                                    inferenceGeneSymbol,
                                    directEvidence, url_ctd)

                            counter_connection += 1
                            h.write(query)
                            if counter_connection % constrain_number == 0:
                                h.write('commit \n')
                                if counter_connection % creation_max == 0:
                                    h.close()
                                    h = open('cypher/map_connection_of_ctd_in_hetionet_' + str(i) + '.cypher', 'w')
                                    h.write('begin \n')
                                    i += 1
                                else:
                                    h.write('begin \n')

    # all treat connection which are not in ctd get as property ctd='no'
    h.write('commit \n begin \n')
    query = ''' Match ()-[r:TREATS_CtD]-() Where not exists(r.ctd)
                Set r.ctd="no", r.hetionet="yes", r.resource=['Hetionet']; \n '''
    h.write(query)
    h.write('commit \n begin \n')
    # all induces connection which are not in ctd get as property ctd='no'
    query = ''' Match ()-[r:INDUCES_CiD]-() Where not exists(r.ctd)
            Set r.ctd="no"; \n '''
    h.write(query)
    h.write('commit \n begin \n')
    # all causes connection which are not in ctd get as property ctd='no'
    query = ''' Match ()-[r:CAUSES_CcSE]-() Where not exists(r.ctd)
            Set r.ctd="no"; \n '''
    h.write(query)
    h.write('commit')

    print('number of new connection causes:' + str(number_of_new_connection_causes))
    print('number of updated connection causes:' + str(number_of_update_connection_causes))
    print('number of new connection induce:' + str(number_of_new_connection_induce))
    print('number of updated connection induce:' + str(number_of_update_connection_induce))
    print('number of new connection of treats:' + str(number_of_new_connection_association))
    print('number of update connection of treats:' + str(number_of_update_connection_association))


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all compounds from hetionet into a dictionary')

    load_compounds_from_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all drugs from ctd into dictionaries depending on the drugbank id exist or not ')

    load_drugs_from_CTD()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find cuis for the ctd mesh terms ')

    find_cui_for_ctd_drugs()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find drugbank ids with use of the cuis in umls ')

    map_cui_to_drugbank_with_umls()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find rxcuis for the ctd mesh terms  ')

    find_rxcui_for_ctd_drugs()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find drugbank ids with use of the rxcuis in rxnorm ')

    map_rxcui_to_drugbank_with_rxnorm()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find drugbank ids with use of the rxnorm drugbank table which is generated with unii and inchikeys ')

    map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Find drugbank ids with use of the name mapping')

    map_ctd_chemical_to_drugbank_with_lable_map()

    #    print('###########################################################################################################################')
    #    
    #    print (datetime.datetime.utcnow())
    #    print('Find drugbank ids with use of the synonym cuis in umls ')
    #    
    #    search_for_synonyms_and_map_to_drugbank_ids()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map ctd chemical to hetionet compound ')

    map_ctd_to_hetionet_compound()

    #    
    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate CTD chemicals into hetionet')

    integration_of_ctd_chemicals_into_hetionet_compound()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate CTD connection into hetionet')

    intigrate_connection_from_ctd_to_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
