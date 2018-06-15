# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 11:55:50 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import sys, time, csv

sys.path.append('../aeolus/')
import get_drugbank_information


class DrugHetionet:
    """
    identifier:string (Drugbank ID)
    inchikey: string
    inchi: string
    name :string
    """

    def __init__(self, identifier, inchikey, inchi, name, cas_number):
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name
        self.cas_number=cas_number


class DrugCTD:
    """
    idType: string	(MESH)
    chemical_id: string
    synonyms: string list divided by |
    drugBankIDs:string list divided by |
    name:string
    how_mapped: string
    """

    def __init__(self, idType, chemical_id, synonyms, drugBankID, name, drugBankIDs,casRN):
        self.idType = idType
        self.chemical_id = chemical_id
        self.synonyms = synonyms
        if drugBankIDs == '':
            drugBankIDs = []
        self.drugBankIDs = drugBankIDs
        self.name = name
        drugBankIDs.append(drugBankID)
        self.drugBankIDs = list(set(drugBankIDs))
        self.casRN=casRN

    def set_drugbankIDs(self, drugbank_ids):
        self.drugBankIDs = list(set(drugbank_ids))

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all compounds from hetionet and  key is drugbank id and value is class DrugHetionet
dict_drugs_hetionet = {}

# dictionary with all alternative drugbank ids to original one
dict_alternative_to_drugbank_id={}

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

# dictionary cas number to durgbank
dict_cas_to_drugbank={}

# list of removed multiple cas number
list_multi_cas=[]


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
        cas_number= result['cas_number'] if 'cas_number' in result else ''
        alternative_ids=result['alternative_ids'] if 'alternative_ids' in result else ''
        #        resource=result['resource']

        drug = DrugHetionet(identifier, inchikey, inchi, name, cas_number)

        dict_drugs_hetionet[identifier] = drug
        for alt_drugbank_id in alternative_ids:
            # if alt_drugbank_id in dict_alternative_to_drugbank_id:
            #     print(alt_drugbank_id)
            #     sys.exit()
            dict_alternative_to_drugbank_id[alt_drugbank_id]=identifier

        if cas_number!='':
            if not cas_number in dict_cas_to_drugbank and not cas_number in list_multi_cas:
                dict_cas_to_drugbank[cas_number]=identifier
            else:
                if cas_number in list_multi_cas:
                    continue
                del dict_cas_to_drugbank[cas_number]
                list_multi_cas.append(cas_number)
                print('multi cas')

    print('In hetionet are:' + str(len(dict_drugs_hetionet)) + ' drugs')
    print(len(dict_cas_to_drugbank))


'''
add the new label chemical to compounds
'''
def add_new_label_to_compounds():
    query='''Match (n:Compound) Set n:Chemical RETURN n'''
    g.run(query)


# dictionary for all names to mesh
dict_name_synonym_to_mesh = {}

# dictionary wrong multiple mapped ctd
# manual checked
dict_wrong_multiple_mapped_ctd={
    'D006895':u'DB09111',
    'D012978':u'DB01440',
    'D006493':u'DB00407',
    'D000068759':u'DB01274',
    'D009173':u'DB00688',
    'C030290':u'DB02201',
    'C533860':u'DB05367',
    'D002955':u'DB03256',
    'C031545':u'DB05321',
    'D014191':u'DB02665',
    'D015283':u'DB01175'
}

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

    file_not_same_cas=open('chemical/not_same_cas.tsv','w')
    file_not_same_cas.write('mesh\tcas-mesh\tdurgbank\tcas-db\tmapping_with_cas\n')

    results = g.run(query)
    counter_drugbank=0

    for result, in results:
        idType = result['idType']
        chemical_id = result['chemical_id']
        synonyms = result['synonyms'] if 'synonyms' in result else []
        drugBankID = result['drugBankID'] if 'drugBankID' in result else ''
        drugBankIDs = result['drugBankIDs'] if 'drugBankIDs' in result else []
        casRN= result['casRN'] if 'casRN' in result else ''
        name = result['name'].lower()
        drug = DrugCTD(idType, chemical_id, synonyms, drugBankID, name, drugBankIDs,casRN)

        if chemical_id=='D004295':
            print('blub')

        # manual
        if chemical_id=='C007420'  or chemical_id=='D009002':
            dict_drugs_CTD_without_drugbankIDs[chemical_id] = drug
            list_drug_CTD_without_drugbank_id.append(chemical_id)
            dict_name_synonym_to_mesh[name] = chemical_id
            # if type(synonyms)!=list:
            #     synonyms = synonyms.split('|')
            for synonym in synonyms:
                dict_name_synonym_to_mesh[synonym.lower()] = chemical_id

            continue
        # elif chemical_id in dict_wrong_multiple_mapped_ctd:
        #     print(chemical_id)
        #     print(drugBankIDs)
        #     drugBankIDs.remove(dict_wrong_multiple_mapped_ctd[chemical_id])
        #     drug.set_drugbankIDs(drugBankIDs)




        # the nodes without a drugbank id are not mapped and for the one with DB ID the cas is checked
        # if it is not the same and another DB with this cas is there then replace the drugbank ids
        if drugBankID == '' and drugBankIDs=='':
            dict_drugs_CTD_without_drugbankIDs[chemical_id] = drug
            list_drug_CTD_without_drugbank_id.append(chemical_id)
            dict_name_synonym_to_mesh[name] = chemical_id
            # if type(synonyms)!=list:
            #     synonyms = synonyms.split('|')
            for synonym in synonyms:
                dict_name_synonym_to_mesh[synonym.lower()] = chemical_id
        else:
            counter_drugbank+=1
            if drugBankID in dict_drugs_hetionet:
                dict_drugs_CTD_with_drugbankIDs[chemical_id] = drug
                if dict_drugs_hetionet[drugBankID].cas_number!= casRN and casRN!='' and dict_drugs_hetionet[drugBankID].cas_number!='':
                    if casRN in dict_cas_to_drugbank:
                        file_not_same_cas.write(
                            chemical_id + '\t' + casRN + '\t' + drugBankID + '\t' + dict_drugs_hetionet[
                                drugBankID].cas_number + '\t' + dict_cas_to_drugbank[casRN] +  '\n')
                        # manual checked
                        if chemical_id == 'D017485' and drugbankId == 'DB03955':
                            dict_drugs_CTD_with_drugbankIDs[chemical_id].set_drugbankIDs(['DB03955'])
                            dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids from ctd')
                            continue
                        dict_drugs_CTD_with_drugbankIDs[chemical_id].set_drugbankIDs([dict_cas_to_drugbank[casRN]])
                    else:
                        file_not_same_cas.write(chemical_id+'\t'+casRN+'\t'+drugBankID+'\t'+dict_drugs_hetionet[drugBankID].cas_number+'\n')
                dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids from ctd')
            else:
                found_a_existing_db=False
                for drugbankId in drugBankIDs:
                    if drugbankId in  dict_drugs_hetionet:
                        found_a_existing_db=True
                        print('alternative mapped')
                        dict_drugs_CTD_with_drugbankIDs[chemical_id] = drug
                        if dict_drugs_hetionet[drugbankId].cas_number != casRN and casRN != '':
                            if casRN in dict_cas_to_drugbank:
                                file_not_same_cas.write(
                                    chemical_id + '\t' + casRN + '\t' + drugbankId + '\t' + dict_drugs_hetionet[
                                        drugbankId].cas_number + '\t' + dict_cas_to_drugbank[casRN] + '\n')

                                # manual checked
                                if chemical_id=='D017485' and drugbankId=='DB03955':
                                    dict_drugs_CTD_with_drugbankIDs[chemical_id].set_drugbankIDs(['DB03955'])
                                    dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids from ctd')
                                    continue
                                dict_drugs_CTD_with_drugbankIDs[chemical_id].set_drugbankIDs([dict_cas_to_drugbank[casRN]])
                            else:
                                file_not_same_cas.write(
                                    chemical_id + '\t' + casRN + '\t' + drugbankId + '\t' + dict_drugs_hetionet[
                                        drugbankId].cas_number + '\n')
                        dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids from ctd')

                if not found_a_existing_db:
                    dict_drugs_CTD_without_drugbankIDs[chemical_id] = drug
                    list_drug_CTD_without_drugbank_id.append(chemical_id)
                    dict_name_synonym_to_mesh[name] = chemical_id
                    # if type(synonyms)!=list:
                    #     synonyms = synonyms.split('|')
                    for synonym in synonyms:
                        dict_name_synonym_to_mesh[synonym.lower()] = chemical_id


    print(counter_drugbank)
    print('In ctd drugs without drugbank ids:' + str(len(dict_drugs_CTD_without_drugbankIDs)))
    print('In ctd drugs with drugbank ids:' + str(len(dict_drugs_CTD_with_drugbankIDs)))

# list with all mesh that did not mapp with cas
list_not_mapped_with_cas=[]

'''
mapping with cas number
'''
def map_with_cas_number_to_drugbank():
    delete_mapped_mesh_ids=[]
    counter_map_with_cas=0
    for mesh_id, information in dict_drugs_CTD_without_drugbankIDs.items():
        casRN= information.casRN

        if casRN in dict_cas_to_drugbank:
            counter_map_with_cas+=1
            dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs([dict_cas_to_drugbank[casRN]])
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use cas number to map to drugbank ids')
            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
        else:
            list_not_mapped_with_cas.append(mesh_id)

    # remove all mapped mesh ids from not_mapped list
    delete_mapped_mesh_ids = list(set(delete_mapped_mesh_ids))
    delete_mapped_mesh_ids.sort()
    delete_mapped_mesh_ids = list(reversed(delete_mapped_mesh_ids))
    for index in delete_mapped_mesh_ids:
        list_drug_CTD_without_drugbank_id.pop(index)

    print('number of mappings with cas:'+str(counter_map_with_cas))
    print(len(list_drug_CTD_without_drugbank_id))
    print(len(list_not_mapped_with_cas))
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
    for mesh_id in list_not_mapped_with_cas:

        # start = time.time()
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB, STR From MRCONSO Where SAB='MSH' and CODE= '%s';")
        query = query % (mesh_id)

        rows_counter = cur.execute(query)
        # time_measurement = time.time() - start
        # print('\t Search for cui in mysql: %.4f seconds' % (time_measurement))
        if rows_counter > 0:
            list_cuis = []
            for (cui, lat, code, sab, label) in cur:
                list_cuis.append(cui)
            list_cuis = list(set(list_cuis))
            dict_mesh_to_cuis[mesh_id] = list_cuis
        else:

            cur = con.cursor()
            # if not mapped map the name to umls cui
            query = ('Select CUI,LAT,CODE,SAB From MRCONSO Where lower(STR)= "%s" And SAB="MSH" ;')
            query= query % (dict_drugs_CTD_without_drugbankIDs[mesh_id].name.lower())
            rows_counter = cur.execute(query )
            if rows_counter > 0:
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
        #manula not mapped
        if mesh_id in ['C006012']:
            list_cuis_not_mapped_drugbank_id.append(mesh_id)
            continue

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
        # print(mesh_id)
        # start = time.time()
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = 'MSH' and CODE='%s' ;")
        query = query % (mesh_id)
        rows_counter = cur.execute(query)
        # time_measurement = time.time() - start
        # print('\t Search for rxcui in mysql: %.4f seconds' % (time_measurement))
        # start = time.time()
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
            # time_measurement = time.time() - start
            # print('\t Go through all rxnorm results and add to dictionary: %.4f seconds' % (time_measurement))
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

        # manual map not well
        if mesh_id in ['C018375','C006012']:
            list_rxcuis_not_mapped_drugbank_id.append(mesh_id)
            continue

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
    print('number of mesh ids which are not mapped:' + str(len(list_drug_CTD_without_drugbank_id)))


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

map_with_cas = open('chemical/ctd_chemical_to_compound_map_use_cas.tsv', 'w')
map_with_cas.write('MESH \t drugbank_ids with | as seperator  \n')

# dictionary with how_mapped as key and file as value
dict_how_mapped_file = {
    'drugbank ids from ctd': map_ctd,
    'use umls cui to map to drugbank ids': map_with_cui,
    'use map table rxcui to map to drugbank ids': map_with_rxcui_table,
    'use rxnorm rxcui to map to drugbank ids': map_with_rxcui,
    'use  name to map to drugbank ids': map_with_name,
    'use cas number to map to drugbank ids':map_with_cas}

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
        # manual mapped
        if mesh=='C025314':
            drugbank_ids.append('DB13949')
        elif mesh in dict_wrong_multiple_mapped_ctd:
            drugbank_ids.remove(dict_wrong_multiple_mapped_ctd[mesh])
            drug.set_drugbankIDs(drugbank_ids)

        string_drugbank_ids = "|".join(drugbank_ids)
        how_mapped = drug.how_mapped

        dict_how_mapped_file[how_mapped].write(mesh + '\t' + string_drugbank_ids + '\n')

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(mesh + '\t' + string_drugbank_ids + '\t' + how_mapped + '\n')

        delete_drugbank_id_and_add_element={}
        delete_not_existing_ids=[]

        for drugbank_id in drugbank_ids:
            if drugbank_id in dict_drugs_hetionet:
                mapped.append(drugbank_id)
            elif drugbank_id in dict_alternative_to_drugbank_id:
                delete_drugbank_id_and_add_element[drugbank_id]=dict_alternative_to_drugbank_id[drugbank_id]
                mapped.append(dict_alternative_to_drugbank_id[drugbank_id])
            else:
                print(mesh)
                delete_not_existing_ids.append(drugbank_id)
                print(drugbank_id)
                print(drugbank_ids)

        if len(delete_drugbank_id_and_add_element)>0:
            for delete_id, add_id in delete_drugbank_id_and_add_element.items():
                drugbank_ids.remove(delete_id)
                drugbank_ids.append(add_id)
            drug.set_drugbankIDs(drugbank_ids)

        if len(delete_not_existing_ids)>0:
            for delete_id in delete_not_existing_ids:
                drugbank_ids.remove(delete_id)
            drug.set_drugbankIDs(drugbank_ids)


        if len(mapped) > 0:
            dict_ctd_to_compound[mesh] = mapped
        else:
            list_new_compounds.append((mesh,drugbank_ids))
            drugbank_ids=[]
            drug.set_drugbankIDs(drugbank_ids)

    print('mapped to hetionet compound:' + str(len(dict_ctd_to_compound)))
    print('will be new generated:' + str(len(list_new_compounds)))
    print(list_new_compounds)

    # all not mapped ctd chemicals
    g = open('chemical/not_mapped_drugs.tsv', 'w')
    g.write('mesh id \t name \t synonyms\n')

    for chemical_id, drug in dict_drugs_CTD_without_drugbankIDs.items():
        if not chemical_id in dict_drugs_CTD_with_drugbankIDs:
            #            print(chemical_id)
            #            print(drug.name)
            #            print(drug.synonyms.encode('utf-8'))
            synonyms=','.join(drug.synonyms)
            synonym = synonyms.encode('utf-8')
            #            print(synonym+'\n'+drug.name.encode('utf-8'))
            g.write(chemical_id.encode('utf-8') + '\t' + drug.name.encode('utf-8') + '\t' + synonym + '\n')
    g.close()
    # sys.exit()


# dictionary how_mapped mit delete number
dict_how_mapped_delete_counter = {}

# add the chemicals which are not in compounds in a csv file
csvfile = open('chemical/chemicals.csv', 'wb')
writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(
    ['ChemicalID', 'parentIDs', 'parentTreeNumbers', 'treeNumbers', 'definition', 'synonyms', 'name', 'casRN'])

'''
integration of ctd chemicals in hetionet
'''


def integration_of_ctd_chemicals_into_hetionet_compound():
    get_drugbank_information.load_all_drugbank_ids_in_dictionary()
    # count all mesh ids which are mapped to a drugbank id
    counter = 0
    # count mapped to drugbank id, but the drugbank id is old or has no chemical information
    counter_illegal_drugbank_ids = 0

    #delete all equal_chemical_CTD relationships
    query='''Match ()-[r:equal_chemical_CTD]->() Delete r'''
    g.run(query)


    for mesh_id, drug in dict_drugs_CTD_with_drugbankIDs.items():
        counter += 1
        delete_index = []
        # manual check that this mapped wrong
        if mesh_id in ['C018375', 'D007483']:
            query = '''Match (c:CTDchemical{chemical_id:'%s'}) Return c'''
            query = query % (mesh_id)
            result = g.run(query)
            first = result.evaluate()
            parentIDs = '|'.join(first['parentIDs']) if 'parentIDs' in first else ''
            parentTreeNumbers = '|'.join(first['parentTreeNumbers']) if 'parentTreeNumbers' in first else ''
            treeNumbers = '|'.join(first['treeNumbers']) if 'treeNumbers' in first else ''
            definition = first['definition'] if 'definition' in first else ''
            synonyms = '|'.join(first['synonyms']) if 'synonyms' in first else ''
            name = first['name'] if 'name' in first else ''
            casRN = first['casRN'] if 'casRN' in first else ''

            writer.writerow(
                [mesh_id, parentIDs, parentTreeNumbers, treeNumbers, definition, synonyms,
                 name, casRN])
            continue
        if mesh_id=='D004295':
            print('blub')
        index = 0
        how_mapped = drug.how_mapped
        drugbank_ids = drug.drugBankIDs

        for drugbank_id in drugbank_ids:

            index += 1
            query = '''Match (c:Compound{identifier:"%s"}) Return c '''
            query = query % (drugbank_id)
            results = g.run(query)
            first_entry = results.evaluate()
            #
            # if first_entry == None:
            #
            #     [name, inchi, inchikey] = get_drugbank_information.get_drugbank_information(drugbank_id)
            #     if name == '':
            #         delete_index.append(index - 1)
            #         continue
            #     url = 'http://www.drugbank.ca/drugs/' + drugbank_id
            #     url_ctd = 'http://ctdbase.org/detail.go?type=chem&acc=' + mesh_id
            #     query = ''' MATCH (n:CTDchemical{chemical_id:"%s"})
            #         Set n.mapped_drugbank_ids=["%s"], n.how_mapped="%s"
            #         Create (c:Compound{identifier:"%s",inchikey:"%s", inchi:"%s", url:"%s",resource:["CTD"],ndf_rt:"no", sider:"no", hetionet:"no", aeolus:"no", ctd_url:"%s", name:"%s",source:"Drugbank via CTD"  , ctd:"yes", pubChem:"", license:" Copyright 2002-2012 MDI Biological Laboratory. All rights reserved. Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved."})
            #         Create (c)-[:equal_chemical_CTD]->(n)
            #         '''
            #     query = query % (
            #         mesh_id, drugbank_id, dict_drugs_CTD_with_drugbankIDs[mesh_id].how_mapped, drugbank_id, inchikey,
            #         inchi, url,
            #         url_ctd, name)
            # else:
            if not drugbank_id in dict_drugs_hetionet:
                print(mesh_id)
                print(drugbank_id)
                delete_index.append(index - 1)
                continue
            resource = first_entry['resource'] if 'resource' in first_entry else []
            resource.append("CTD")
            resource = list(set(resource))
            string_resource = '","'.join(resource)
            url = 'http://ctdbase.org/detail.go?type=chem&acc=' + mesh_id
            query = ''' MATCH (n:CTDchemical{chemical_id:"%s"}), (c:Compound{identifier:"%s"})
            Set c.ctd="yes", c.ctd_url="%s", c.resource=["%s"]
            Create (c)-[:equal_chemical_CTD]->(n)
            '''
            query = query % (mesh_id, drugbank_id, url, string_resource)

            g.run(query)

        # add the mapping typ which mapped to a not usable durgbank id
        delete_index = list(set(delete_index))
        delete_index.sort()
        delete_index = list(reversed(delete_index))
        if len(delete_index) == len(drugbank_ids):
            counter_illegal_drugbank_ids += 1
            print(mesh_id)
            if how_mapped in dict_how_mapped_delete_counter:
                dict_how_mapped_delete_counter[how_mapped] += 1
            else:
                dict_how_mapped_delete_counter[how_mapped] = 1
            query='''Match (c:CTDchemical{chemical_id:'%s'}) Return c'''
            query=query %(mesh_id)
            result=g.run(query)
            first=result.evaluate()
            parentIDs='|'.join(first['parentIDs']) if 'parentIDs' in first else ''
            parentTreeNumbers = '|'.join(first['parentTreeNumbers']) if 'parentTreeNumbers' in first else ''
            treeNumbers = '|'.join(first['treeNumbers']) if 'treeNumbers' in first else ''
            definition = first['definition'] if 'definition' in first else ''
            synonyms = '|'.join(first['synonyms']) if 'synonyms' in first else ''
            name = first['name'] if 'name' in first else ''
            casRN = first['casRN'] if 'casRN' in first else ''


            writer.writerow(
                [mesh_id, parentIDs, parentTreeNumbers, treeNumbers, definition,  synonyms,
                 name, casRN])
        for index in delete_index:
            drug.drugBankIDs.pop(index)

    # all compounds which are not mapped with ctd drug get as property ctd='no'
    query = ''' MATCH  (c:Compound) Where not exists(c.ctd)
            Set c.ctd="no", c.ctd_url="" '''
    g.run(query)

    print('number of ctd drug which has no legal drugbank id:' + str(counter_illegal_drugbank_ids))
    print('number of all ctd which are mapped include the one with illegal drugbank ids:' + str(counter))
    print(dict_how_mapped_delete_counter)

'''
add all not mapped ctd chemicals to csv and then integrate into neo4j as chemicals
'''
def add_chemicals_to_csv():
    # delete all equal_chemical_CTD relationships
    query = '''Match ()-[r:equal_to_CTD_chemical]->() Delete r'''
    g.run(query)

    for mesh_id in list_drug_CTD_without_drugbank_id:
        query = '''Match (c:CTDchemical{chemical_id:'%s'}) Return c'''
        query = query % (mesh_id)
        result = g.run(query)
        first = result.evaluate()
        parentIDs = '|'.join(first['parentIDs']).encode('utf8') if 'parentIDs' in first else ''
        parentTreeNumbers = '|'.join(first['parentTreeNumbers']).encode('utf8') if 'parentTreeNumbers' in first else ''
        treeNumbers = '|'.join(first['treeNumbers']).encode('utf8') if 'treeNumbers' in first else ''
        definition = first['definition'].encode('utf8') if 'definition' in first else ''
        synonyms = '|'.join(first['synonyms']).encode('utf8') if 'synonyms' in first else ''
        name = first['name'].encode('utf8') if 'name' in first else ''
        casRN = first['casRN'].encode('utf8') if 'casRN' in first else ''
        writer.writerow(
            [mesh_id, parentIDs, parentTreeNumbers, treeNumbers, definition, synonyms,
             name, casRN])

    cypher_file= open('chemical/cypher.cypher','w')
    if exists_chemicals:
        query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical/chemicals.csv" As line MATCH (n:CTDchemical{chemical_id:line.ChemicalID}) Merge (d:Chemical{identifier:line.ChemicalID}) On Create Set d.parentIDs=split(line.parentIDs,'|'), d.parentTreeNumbers=split(line.parentTreeNumbers,'|'), d.treeNumbers=split(line.treeNumbers,'|'), d.definition=line.definition, d.synonyms=split(line.synonyms,'|'), d.name=line.name, d.cas_number=line.casRN, d.resource=['CTD'], d.ctd='yes', d.ctd_url='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, d.url="https://meshb.nlm.nih.gov/record/ui?ui="+line.ChemicalID,  d.license="U.S. National Library of Medicine ", d.source="MeSH via CTD" On Match Set d.parentIDs=split(line.parentIDs,'|'), d.parentTreeNumbers=split(line.parentTreeNumbers,'|'), d.treeNumbers=split(line.treeNumbers,'|'), d.definition=line.definition, d.synonyms=split(line.synonyms,'|'), d.name=line.name, d.cas_number=line.casRN With d, n Create (d)-[:equal_to_CTD_chemical]->(n)  ;\n '''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical/chemicals.csv" As line MATCH (n:CTDchemical{chemical_id:line.ChemicalID}) Create (d:Chemical{identifier:line.ChemicalID, parentIDs:split(line.parentIDs,'|'), parentTreeNumbers:split(line.parentTreeNumbers,'|'), treeNumbers:split(line.treeNumbers,'|'), definition:line.definition, synonyms:split(line.synonyms,'|'), name:line.name, cas_number:line.casRN, resource:['CTD'], ctd:'yes', ctd_url:'http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, url:"https://meshb.nlm.nih.gov/record/ui?ui="+line.ChemicalID,  license:"U.S. National Library of Medicine ", source:"MeSH via CTD" }) With d, n Create (d)-[:equal_to_CTD_chemical]->(n);\n '''
    cypher_file.write(query)

# says if chemicals exists or not so need to create chemicals or merge
exists_chemicals=False


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
    print('add new label if needed')

    query='''Match (n:Chemical) Return n '''
    result=g.run(query)
    first= result.evaluate()

    if first is None:
        add_new_label_to_compounds()
        exists_chemicals=True

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all drugs from ctd into dictionaries depending on the drugbank id exist or not ')

    load_drugs_from_CTD()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map with use of cas')

    map_with_cas_number_to_drugbank()

    print (datetime.datetime.utcnow())

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
    print('Integrate CTD chemicals to chemicals into hetionet')

    add_chemicals_to_csv()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
