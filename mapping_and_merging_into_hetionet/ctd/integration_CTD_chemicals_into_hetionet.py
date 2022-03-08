
import datetime
import sys, time, csv
import io
from collections import defaultdict
from typing import Any

sys.path.append("../..")
import create_connection_to_databases#


sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name




class DrugHetionet:
    """
    identifier:string (Drugbank ID)
    inchikey: string
    inchi: string
    name :string
    """

    def __init__(self, identifier, inchikey, inchi, name, cas_number, xrefs, resources,synonyms):
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name
        self.cas_number=cas_number
        self.xrefs=xrefs
        self.resources=resources
        self.synonyms=synonyms


class DrugCTD:
    """
    idType: string	(MESH)
    chemical_id: string
    synonyms: string list divided by |
    drugBankIDs:string list divided by |
    name:string
    how_mapped: string
    """

    def __init__(self, idType, chemical_id, synonyms,  name,  casRN):
        self.idType = idType
        self.chemical_id = chemical_id
        self.synonyms = synonyms
        self.name = name
        self.casRN=casRN

    def set_drugbankIDs(self, drugbank_ids):
        self.drugBankIDs= drugbank_ids

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped

#dictionary of mesh mapping to drugbank from umls
dict_mesh_to_drugbank_with_umls={}

#dictionary of mesh mapping to drugbank from rxnorm
dict_mesh_to_drugbank_with_rxnorm={}

'''
try to open file
'''
def try_to_open_file_and_read_information_into_dict(file, header, dictionary):
    try:
        cache_file=open(file,'r', encoding='utf-8')
        csv_reader=csv.DictReader(cache_file,delimiter='\t')
        for row in csv_reader:
            drugbank_ids=[]
            for drugbank_id in row['drugbank_ids'].split('|'):
                if drugbank_id in dict_drugs_hetionet:
                    drugbank_ids.append(drugbank_id)
            if len(drugbank_ids) >0:
                dictionary[row['mesh_id']]=list(set(row['drugbank_ids'].split('|')))
        cache_file.close()
        cache_file = open(file, 'a', encoding='utf-8')
        csv_writer = csv.writer(cache_file, delimiter='\t')
        return csv_writer

    except:
        cache_file=open(file,'w',encoding='utf-8')
        csv_writer=csv.writer(cache_file,delimiter='\t')
        csv_writer.writerow(header)
        return csv_writer

'''
Create mapping files or open and load mapping results
'''

def get_umls_mapping_result_or_generate_new_file():
    # header of cache file
    header=['mesh_id','drugbank_ids']

    # umls mapping
    global csv_writer_umls
    csv_writer_umls=try_to_open_file_and_read_information_into_dict('chemical/mapping_results_umls.tsv',header,dict_mesh_to_drugbank_with_umls)

    # rxnorm mapping
    global csv_writer_rxnorm
    csv_writer_rxnorm=try_to_open_file_and_read_information_into_dict('chemical/mapping_results_rxnorm.tsv',header,dict_mesh_to_drugbank_with_rxnorm)


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
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = create_connection_to_databases.database_connection_RxNorm()

# dictionary cas number to drugbank
dict_cas_to_drugbank={}

# list of removed multiple cas number
list_multi_cas=[]

#dictionary from drugbank synonym to drugbank id
dict_synonym_to_drugbank_id=defaultdict(set)

'''
remove all mapped mesh ids from not_mapped list
'''
def remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids):
    delete_mapped_mesh_ids = list(set(delete_mapped_mesh_ids))
    delete_mapped_mesh_ids.sort()
    delete_mapped_mesh_ids = list(reversed(delete_mapped_mesh_ids))
    for index in delete_mapped_mesh_ids:
        list_drug_CTD_without_drugbank_id.pop(index)

'''
remove all mapped mesh ids from not_mapped cuis list
'''
#
def remove_all_mapped_mesh_ids_from_not_mapped_cui_list(delete_cui):
    delete_cui = list(set(delete_cui))
    delete_cui.sort()
    delete_cui = list(reversed(delete_cui))
    for index in delete_cui:
        list_cuis_not_mapped_drugbank_id.pop(index)


'''
load in all compounds from hetionet in dictionary and generate a name/synonym dictionary to drugbank id
properties:
    license
    identifier
    inchikey
    inchi
    name
    source
    url
    synonyms
    Where n.identifier in ["DB00588","DB13867"]
'''


def load_compounds_from_hetionet():
    query = 'MATCH (n:Compound) Where not n:Product RETURN n '
    results = g.run(query)
    i = 0

    for result, in results:
        i += 1
        identifier = result['identifier']
        inchikey = result['inchikey']
        inchi = result['inchi']
        name = result['name'].lower()
        cas_number= result['cas_number'] if 'cas_number' in result else ''
        alternative_ids=result['alternative_ids'] if 'alternative_ids' in result else []
        alternative_ids=list(filter(bool,alternative_ids))
        synonyms=[x.lower() for x in result['synonyms']] if 'synonyms' in result else []
        xrefs= result['xrefs'] if 'xrefs' in result else []
        resource = result['resource'] if 'resource' in result else []

        #generate name/synonym dictionary to drugbank identifier
        dict_synonym_to_drugbank_id[name].add(identifier) if  name is not None else print('no name')

        for synonym in synonyms:
            dict_synonym_to_drugbank_id[synonym].add(identifier)
        #        resource=result['resource']

        drug = DrugHetionet(identifier, inchikey, inchi, name, cas_number, xrefs, resource,synonyms)

        dict_drugs_hetionet[identifier] = drug
        for alt_drugbank_id in alternative_ids:
            # if alt_drugbank_id in dict_alternative_to_drugbank_id:
            #     print(alt_drugbank_id)
            #     sys.exit()
            dict_alternative_to_drugbank_id[alt_drugbank_id]=identifier

        if cas_number!='':
            if not cas_number in dict_cas_to_drugbank :
                dict_cas_to_drugbank[cas_number]=[identifier]
            else:
                dict_cas_to_drugbank[cas_number].append(identifier)
                print('multi cas')

    print('In hetionet are:' + str(len(dict_drugs_hetionet)) + ' drugs')
    print(len(dict_cas_to_drugbank))


# dictionary wrong multiple mapped ctd
# manual checked
dict_wrong_multiple_mapped_ctd={
    'D012978':u'DB01440',
    'D006493':u'DB00407',
    'C030290':u'DB02201',
    'D002955':u'DB03256',
    'D014191':u'DB02665'
}

file_not_same_cas = open('chemical/not_same_cas.tsv', 'w')
csv_not_the_same_cas = csv.writer(file_not_same_cas, delimiter='\t')
csv_not_the_same_cas.writerow(['mesh', 'cas-mesh', 'drugbank', 'cas-db', 'mapping_with_cas'])

'''
check if the external reference of ctd drugbank id has the same cas number
add the mapped ctd in dictionary
'''
def check_and_add_the_mapping(chemical_id, drug, drugBankID,casRN,name,synonyms):
    dict_drugs_CTD_with_drugbankIDs[chemical_id] = drug
    drugbank_ids=set()
    drugbank_ids_name=[]
    if name in dict_synonym_to_drugbank_id:
        drugbank_ids_name=list(dict_synonym_to_drugbank_id[name])
    if dict_drugs_hetionet[drugBankID].cas_number != casRN and casRN != '' and dict_drugs_hetionet[
        drugBankID].cas_number != '':
        if casRN in dict_cas_to_drugbank:
            drug_string='|'.join(dict_cas_to_drugbank[casRN])
            csv_not_the_same_cas.writerow([
                chemical_id, casRN, drugBankID, dict_drugs_hetionet[
                    drugBankID].cas_number, drug_string])
            # manual checked
            # if chemical_id == 'D017485' and drugBankID == 'DB03955':
            #     dict_drugs_CTD_with_drugbankIDs[chemical_id].set_drugbankIDs(['DB03955'])
            #     dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids from ctd')
            #     return False, [drugBankID]

            ctd_names=set([name])
            ctd_names=ctd_names.union(synonyms)
            fitting_drugbank_ids=set()
            for drugbank_id in set(dict_cas_to_drugbank[casRN]):
                drugbank_id_names=set([dict_drugs_hetionet[drugbank_id].name])
                drugbank_id_names=drugbank_id_names.union(dict_drugs_hetionet[drugbank_id].synonyms)
                if len(ctd_names.intersection(drugbank_id_names))>0:
                    fitting_drugbank_ids.add(drugbank_id)

            drugbank_ids =fitting_drugbank_ids
            dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('cas-id from ctd')
        else:
            csv_not_the_same_cas.writerow([chemical_id, casRN, drugBankID, dict_drugs_hetionet[drugBankID].cas_number])
    if len(drugbank_ids)==0:
        drugbank_ids.add(drugBankID)
        drugbank_ids.union(drugbank_ids_name)
        dict_drugs_CTD_with_drugbankIDs[chemical_id].set_how_mapped('drugbank ids and name from ctd')
    return True, list(drugbank_ids)


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
    
{chemical_id:"D012978"}
'''


def load_drugs_from_CTD():
    query = 'MATCH (n:CTD_chemical) RETURN n'
    results = g.run(query)
    counter_drugbank=0

    for result, in results:
        idType = result['idType']
        chemical_id = result['chemical_id']
        if chemical_id=='D012978':
            print('huhu')
        synonyms = [x.lower() for x in result['synonyms']] if 'synonyms' in result else []

        casRN= result['casRN'] if 'casRN' in result else ''
        name = result['name'].lower()
        drug = DrugCTD(idType, chemical_id, synonyms,  name,casRN)


        # manual
        if chemical_id=='C007420':
            dict_drugs_CTD_without_drugbankIDs[chemical_id] = drug
            list_drug_CTD_without_drugbank_id.append(chemical_id)

            continue
        dict_drugs_CTD_without_drugbankIDs[chemical_id] = drug
        list_drug_CTD_without_drugbank_id.append(chemical_id)


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
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(dict_cas_to_drugbank[casRN])
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use cas number to map to drugbank ids')
            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
        else:
            list_not_mapped_with_cas.append(mesh_id)

    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids)

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
    delete_mapped_mesh_ids = []
    # count the number of mesh ids which could be only mapped to umls cui with use of the name
    count_map_with_name = 0
    for mesh_id in list_not_mapped_with_cas:

        found_mapping=False
        if mesh_id in dict_mesh_to_drugbank_with_umls:
            mesh_name=dict_drugs_CTD_without_drugbankIDs[mesh_id].name.lower()
            drugbank_ids=set()
            if mesh_name in dict_synonym_to_drugbank_id:
                drugbank_ids=drugbank_ids.union(dict_synonym_to_drugbank_id[mesh_name])
            mesh_synonyms=dict_drugs_CTD_without_drugbankIDs[mesh_id].synonyms
            for synonym in mesh_synonyms:
                synonym=synonym.lower()
                if synonym in dict_synonym_to_drugbank_id:
                    drugbank_ids = drugbank_ids.union(dict_synonym_to_drugbank_id[synonym])

            if len(drugbank_ids.intersection(dict_mesh_to_drugbank_with_umls[mesh_id]))>0:

                dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(dict_mesh_to_drugbank_with_umls[mesh_id])
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use umls cui to map to drugbank ids')
                delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                found_mapping=True

        if not found_mapping:

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
                query = ('Select CUI,LAT,CODE,SAB From MRCONSO Where STR= "%s" And SAB="MSH" ;')
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


    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids)


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
                if code in dict_drugs_hetionet:
                    drugbank_ids.append(code)
            drugbank_ids = list(set(drugbank_ids))
            if len(drugbank_ids)>0:
                drugbank_ids_name=[]
                if dict_drugs_CTD_without_drugbankIDs[mesh_id].name in dict_synonym_to_drugbank_id:
                    drugbank_ids_name = dict_synonym_to_drugbank_id[dict_drugs_CTD_without_drugbankIDs[mesh_id].name]
                drugbank_ids=list(set(drugbank_ids).union(drugbank_ids_name))
                drugbank_string='|'.join(drugbank_ids)
                csv_writer_umls.writerow([mesh_id,drugbank_string])
                dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                delete_mapped_mesh.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(drugbank_ids)
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use umls cui to map to drugbank ids')
            else:
                list_cuis_not_mapped_drugbank_id.append(mesh_id)
        else:
            list_cuis_not_mapped_drugbank_id.append(mesh_id)

    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh)

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
    # remember the index of the mapped mesh ids int the different not mapped lists
    delete_cui = []
    delete_mapped_mesh_ids = []
    for mesh_id in list_drug_CTD_without_drugbank_id:
        if mesh_id in dict_mesh_to_drugbank_with_rxnorm:
            dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(dict_mesh_to_drugbank_with_rxnorm[mesh_id])
            dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use rxnorm rxcui to map to drugbank ids')
            if mesh_id in list_cuis_not_mapped_drugbank_id:
                delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))
        else:
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

    # remove all mapped mesh ids from not_mapped umls cui list
    remove_all_mapped_mesh_ids_from_not_mapped_cui_list(delete_cui)

    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids)

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
                if code in dict_drugs_hetionet:
                    drugbank_ids.append(code)
            drugbank_ids = list(set(drugbank_ids))
            if len(drugbank_ids)>0:
                drugbank_ids_name=[]
                if dict_drugs_CTD_without_drugbankIDs[mesh_id].name in dict_synonym_to_drugbank_id:
                    drugbank_ids_name = dict_synonym_to_drugbank_id[dict_drugs_CTD_without_drugbankIDs[mesh_id].name]
                drugbank_ids=list(set(drugbank_ids).union(drugbank_ids_name))
                drugbank_string='|'.join(drugbank_ids)
                csv_writer_rxnorm.writerow([mesh_id,drugbank_string])
                dict_drugs_CTD_with_drugbankIDs[mesh_id] = dict_drugs_CTD_without_drugbankIDs[mesh_id]
                delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(mesh_id))
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_drugbankIDs(drugbank_ids)
                dict_drugs_CTD_with_drugbankIDs[mesh_id].set_how_mapped('use rxnorm rxcui to map to drugbank ids')
                if mesh_id in list_cuis_not_mapped_drugbank_id:
                    delete_cui.append(list_cuis_not_mapped_drugbank_id.index(mesh_id))
            else:
                list_rxcuis_not_mapped_drugbank_id.append(mesh_id)

        else:
            list_rxcuis_not_mapped_drugbank_id.append(mesh_id)

    # remove all mapped mesh ids from not_mapped umls cui list
    remove_all_mapped_mesh_ids_from_not_mapped_cui_list(delete_cui)

    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids)

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
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv', 'r')
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
    remove_all_mapped_mesh_ids_from_not_mapped_cui_list(delete_cui)

    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids)

    print('length of list of mesh id with all drugbank ids from rxnorm:' + str(len(dict_drugs_CTD_with_drugbankIDs)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_not_mapped_drugbank_id)))
    print('length of list of cuis without drugbank ids from umls:' + str(len(list_cuis_not_mapped_drugbank_id)))
    print('number of mesh ids which are not mapped:' + str(len(list_drug_CTD_without_drugbank_id)))

'''
map with name or synonyms to drugbank but with the value in Hetionet (Drugbank drugs are all integrated into Hetionet)
'''
def map_with_name_to_drugbank():
    delete_cui = []
    delete_mapped_mesh_ids = []
    for ctd_id in list_drug_CTD_without_drugbank_id:
        name=dict_drugs_CTD_without_drugbankIDs[ctd_id].name
        synonyms=dict_drugs_CTD_without_drugbankIDs[ctd_id].synonyms

        if name in dict_synonym_to_drugbank_id:
            dict_drugs_CTD_with_drugbankIDs[ctd_id] = dict_drugs_CTD_without_drugbankIDs[ctd_id]
            delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(ctd_id))
            dict_drugs_CTD_with_drugbankIDs[ctd_id].set_drugbankIDs(list(dict_synonym_to_drugbank_id[name]))
            dict_drugs_CTD_with_drugbankIDs[ctd_id].set_how_mapped('use  name to map to drugbank ids')
            if ctd_id in list_cuis_not_mapped_drugbank_id:
                delete_cui.append(list_cuis_not_mapped_drugbank_id.index(ctd_id))
        for synonym in synonyms:
            if synonym in dict_synonym_to_drugbank_id:
                dict_drugs_CTD_with_drugbankIDs[ctd_id] = dict_drugs_CTD_without_drugbankIDs[ctd_id]
                delete_mapped_mesh_ids.append(list_drug_CTD_without_drugbank_id.index(ctd_id))
                dict_drugs_CTD_with_drugbankIDs[ctd_id].set_drugbankIDs(list(dict_synonym_to_drugbank_id[synonym]))
                dict_drugs_CTD_with_drugbankIDs[ctd_id].set_how_mapped('use  name to map to drugbank ids synonyms')
                if ctd_id in list_cuis_not_mapped_drugbank_id:
                    delete_cui.append(list_cuis_not_mapped_drugbank_id.index(ctd_id))

    # remove all mapped mesh ids from not_mapped cuis list
    remove_all_mapped_mesh_ids_from_not_mapped_cui_list(delete_cui)

    # remove all mapped mesh ids from not_mapped list
    remove_mesh_ids_from_not_mapped_list(delete_mapped_mesh_ids)
    print('number of mesh ids which are not mapped:' + str(len(list_drug_CTD_without_drugbank_id)))



# dictionary for all ctd mesh ids which are mapped to hetionet with mesh as key and value are drugbank ids
dict_ctd_to_compound = {}

# list of new generated compound with mesh ids
list_new_compounds = []

# dictionary with how_mapped as key and file as value
dict_how_mapped_file = {}

# generate file with mesh id and a list of drugbank ids and where they are from
multiple_drugbankids = open('ctd_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('MESH id \t drugbank_ids with | as seperator \t where are it from \n')

'''
map drugbank id from ctd to compound in hetionet
'''


def map_ctd_to_hetionet_compound():

    # all not mapped ctd chemicals
    not_mapped_file = open('chemical/not_mapped_drugs.tsv', 'w', encoding='utf-8')
    not_mapped_csv=csv.writer(not_mapped_file,delimiter='\t')
    not_mapped_csv.writerow(['mesh id','name', 'synonyms'])

    for mesh, drug in dict_drugs_CTD_with_drugbankIDs.items():
        drugbank_ids = set(drug.drugBankIDs)

        mapped = []
        if mesh=='D000068759':
            print('ohje ')
        # manual mapped
        if mesh=='C025314':
            drugbank_ids.add('DB13949')
        # check if the mesh id is mapped to the wrond drugbank id
        elif mesh in dict_wrong_multiple_mapped_ctd:
            if dict_wrong_multiple_mapped_ctd[mesh] in drugbank_ids:
                drugbank_ids.remove(dict_wrong_multiple_mapped_ctd[mesh])

        string_drugbank_ids = "|".join(list(drugbank_ids))
        how_mapped = drug.how_mapped

        if how_mapped not in dict_how_mapped_file:
            map_with = open('chemical/ctd_chemical_to_compound_map_use_'+how_mapped.replace(' ','_')+'.tsv', 'w')
            csv_mapped = csv.writer(map_with, delimiter='\t')
            csv_mapped.writerow(['MESH', 'drugbank_ids with | as seperator'])
            dict_how_mapped_file[how_mapped]=csv_mapped
        dict_how_mapped_file[how_mapped].writerow([mesh , string_drugbank_ids] )

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(mesh + '\t' + string_drugbank_ids + '\t' + how_mapped + '\n')

        delete_drugbank_id_and_add_element={}

        # check out which which are alternative ids
        for drugbank_id in drugbank_ids:
            if drugbank_id in dict_alternative_to_drugbank_id:
                delete_drugbank_id_and_add_element[drugbank_id]=dict_alternative_to_drugbank_id[drugbank_id]
                mapped.append(dict_alternative_to_drugbank_id[drugbank_id])
            else:
                mapped.append(drugbank_id)

        # make the list so that only the first drugbank ids are in the list and not the alternative ids
        if len(delete_drugbank_id_and_add_element)>0:
            for delete_id, add_id in delete_drugbank_id_and_add_element.items():
                drugbank_ids.remove(delete_id)
                drugbank_ids.add(add_id)


        # check out if they have at least one drugbank id and will merge with a compound or will be a chemical
        if len(mapped) > 0:
            dict_ctd_to_compound[mesh] = mapped
        # if no drugbank is in the real set then the ctd term should be moved to the unmapped list
        else:
            list_drug_CTD_without_drugbank_id.append(mesh)
            # list_new_compounds.append((mesh,drugbank_ids))
            drugbank_ids=set()
            writer.writerow([mesh])

        # check if ctd map to multiple nodes and if then find intersection with name mapping
        if len(drugbank_ids)>1:
            name=drug.name
            name_drugbank_ids=set()
            synonyms=drug.synonyms
            if name in dict_synonym_to_drugbank_id:
                name_drugbank_ids.update(list(dict_synonym_to_drugbank_id[name]))
            for synonym in synonyms:
                synonym=synonym.lower()
                if synonym in dict_synonym_to_drugbank_id:
                    name_drugbank_ids.update(list(dict_synonym_to_drugbank_id[synonym]))

            if len(name_drugbank_ids)>0:
                intersection_drugbank_ids=name_drugbank_ids.intersection(drugbank_ids)
                if len(intersection_drugbank_ids)>0:
                    drugbank_ids=intersection_drugbank_ids
                    print('intersection worked')
                    print(mesh)
                    if len(drugbank_ids)>1:
                        print(name_drugbank_ids)
                        print(drugbank_ids)
                        print(how_mapped)
                else:
                    print('no intersection')
                    print(drugbank_ids)
                    print(name_drugbank_ids)
                    print(drugbank_ids)
                    print(mesh)
            else:
                print('intersection not possible')
                print(mesh)

        drug.set_drugbankIDs(list(drugbank_ids))
        dict_drugs_CTD_with_drugbankIDs[mesh]=drug

    print('mapped to hetionet compound:' + str(len(dict_ctd_to_compound)))


    for chemical_id, drug in dict_drugs_CTD_without_drugbankIDs.items():
        if not chemical_id in dict_drugs_CTD_with_drugbankIDs:
            writer.writerow([chemical_id])
            #            print(chemical_id)
            #            print(drug.name)
            #            print(drug.synonyms.encode('utf-8'))
            synonyms=','.join(drug.synonyms)
            synonym = synonyms
            #            print(synonym+'\n'+drug.name.encode('utf-8'))
            not_mapped_csv.writerow([chemical_id , drug.name, synonym ])
    not_mapped_file.close()
    # sys.exit()


# dictionary how_mapped mit delete number
dict_how_mapped_delete_counter = {}

# add the chemicals which are not in compounds in a tsv file
csvfile = io.open('chemical/chemicals.tsv', 'w', encoding='utf-8', newline='')
writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['ChemicalID'])

'''
integration of ctd chemicals in hetionet
'''


def integration_of_ctd_chemicals_into_hetionet_compound():
    # count all mesh ids which are mapped to a drugbank id
    counter = 0
    # count mapped to drugbank id, but the drugbank id is old or has no chemical information
    counter_illegal_drugbank_ids = 0

    # file with all chemical_mapped to compound and used to integrated them into Hetionet
    csvfile_db = io.open('chemical/chemicals_drugbank.tsv', 'w', encoding='utf-8', newline='')
    writer_compound = csv.writer(csvfile_db, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer_compound.writerow(
        ['ChemicalID', 'Drugbank_id', 'url', 'string_resource', 'string_drugbank_ids', 'string_xml','how_mapped'])



    for mesh_id, drug in dict_drugs_CTD_with_drugbankIDs.items():
        counter += 1
        index = 0
        how_mapped = drug.how_mapped
        drugbank_ids = drug.drugBankIDs
        for drugbank_id in drugbank_ids:


            index += 1
            resource = set(dict_drugs_hetionet[drugbank_id].resources)
            resource.add("CTD")
            string_resource = '|'.join(resource)
            string_dbs='|'.join(drugbank_ids)

            xrefs = dict_drugs_hetionet[drugbank_id].xrefs
            xrefs.append("MESH:"+mesh_id)
            xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical')
            string_xrefs = '|'.join(xrefs)

            url = 'http://ctdbase.org/detail.go?type=chem&acc=' + mesh_id
            writer_compound.writerow([mesh_id, drugbank_id, url, string_resource,string_dbs, string_xrefs,how_mapped])


    print('number of ctd drug which has no legal drugbank id:' + str(counter_illegal_drugbank_ids))
    print('number of all ctd which are mapped include the one with illegal drugbank ids:' + str(counter))



'''
add all not mapped ctd chemicals to tsv and then integrate into neo4j as chemicals
'''
def generate_cypher_file():

    cypher_file= open('output/cypher.cypher','a',encoding='utf-8')
    cypher_file.write(''':begin\nMatch (n:Compound) Set n:Chemical;\n:Commit\n''')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ctd/chemical/chemicals_drugbank.tsv" As line   FIELDTERMINATOR '\\t' MATCH (n:CTD_chemical{chemical_id:line.ChemicalID}), (c:Compound{identifier:line.Drugbank_id}) Set c.ctd="yes", c.ctd_url=line.url, c.resource=split(line.string_resource,'|'), c.xrefs=split(line.string_xml,'|'), n.drugBankIDs=split(line.string_drugbank_ids,'|')  Create (c)-[:equal_chemical_CTD{how_mapped:line.how_mapped}]->(n);\n'''
    cypher_file.write(query)
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ctd/chemical/chemicals.tsv" As line  FIELDTERMINATOR '\\t' MATCH (n:CTD_chemical{chemical_id:line.ChemicalID}) Create (d:Chemical{identifier:line.ChemicalID, parentIDs:n.parentIDs, parentTreeNumbers:n.parentTreeNumbers, treeNumbers:n.treeNumbers, definition:n.definition, synonyms:n.synonyms, name:n.name, cas_number:n.casRN, resource:['CTD'], ctd:'yes', ctd_url:'http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, url:"https://meshb.nlm.nih.gov/record/ui?ui="+line.ChemicalID,  license:"Copyright 2002-2012 MDI Biological Laboratory. All rights reserved. Copyright 2012-2021 NC State University. All rights reserved.", source:"MeSH via CTD" }) With d, n Create (d)-[:equal_to_CTD_chemical]->(n);\n '''
    cypher_file.write(query)
    cypher_file.write(':begin\n Create Constraint On (node:Chemical) Assert node.identifier Is Unique;\n :commit\n')
    cypher_file.close()

    # add query to update disease nodes with do='no'
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = ''':begin\n MATCH (n:Chemical) Where not exists(n.ctd) Set n.ctd="no";\n :commit\n '''
    cypher_general.write(query)
    cypher_general.close()

# says if chemicals exists or not so need to create chemicals or merge
exists_chemicals=False


def main():
    # path to directory
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    global exists_chemicals
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
    print('Load all mesh drugbank ids from file in dictionary and prepare file')


    get_umls_mapping_result_or_generate_new_file()

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

    map_with_name_to_drugbank()

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
    print('generate cypher file for integration of chemical')

    generate_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
