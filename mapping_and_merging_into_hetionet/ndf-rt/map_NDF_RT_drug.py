# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:15:37 2017

@author: ckoenigs
"""

import datetime
import sys, csv
from collections import defaultdict


sys.path.append("../..")
import create_connection_to_databases


# dictionary with chemical id as key and the whole node as value
dict_chemical_hetionet={}

# dictionary with code as key and value is class DrugNDF_RT
dict_drug_NDF_RT = {}

# dictionary with rxcui as key and value is list of codes
dict_drug_NDF_RT_rxcui_to_code = {}

# dictionary with code as key and value is class DrugNDF_RT
dict_drug_NDF_RT_without_rxcui = {}

# dictionary unii to code because this is needed in a mapping step
dict_unii_to_code=defaultdict(list)


#dictionary synonyms/name/brands chemical ids
dict_synonyms_to_chemicals_ids={}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g
    g = create_connection_to_databases.database_connection_neo4j()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = create_connection_to_databases.database_connection_RxNorm()


'''
function to delete ids from list

'''
def delete_elements_from_list(delete_list):
    for entry in delete_list:
        if entry in list_rxcuis_without_drugbank_ids:
            list_rxcuis_without_drugbank_ids.remove(entry)

#dictionary from unii to chemical id
dict_unii_to_chemical_id={}

# dictionary umls cui to chemical id
dict_umls_cui_to_chemical_id={}

'''
load in all compound from hetionet in a dictionary
'''


def load_hetionet_chemical_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier,n'''
    results = g.run(query)

    for identifier, node, in results:
        dict_chemical_hetionet[identifier] = dict(node)
        if 'unii' in node:
            if node['unii'] in dict_unii_to_chemical_id:
                sys.exit('ohje unii')
            dict_unii_to_chemical_id[node['unii']]=[identifier]
        name = node['name'].lower() if 'name' in node else ''
        if not name in dict_synonyms_to_chemicals_ids:
            dict_synonyms_to_chemicals_ids[name] = set()
        dict_synonyms_to_chemicals_ids[name].add(identifier)

        synonyms = node['synonyms']
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if not synonym in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[synonym] = set()
                dict_synonyms_to_chemicals_ids[synonym].add(identifier)
        brand_name_and_companys = node['international_brands_name_company']
        if brand_name_and_companys:
            for brand_name_and_company in brand_name_and_companys:
                brand_name = brand_name_and_company.split('::')[0]
                if not brand_name in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[brand_name] = set()
                dict_synonyms_to_chemicals_ids[brand_name].add(identifier)

        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where (SAB = 'DRUGBANK' or SAB='MSH') and CODE= %s ;")
        rows_counter = cur.execute(query, (identifier,))
        if rows_counter > 0:
            for (cui, lat, code, sab,) in cur:
                if cui not in dict_umls_cui_to_chemical_id:
                    dict_umls_cui_to_chemical_id[cui]=set()
                dict_umls_cui_to_chemical_id[cui].add(identifier)


    print('length of compound in hetionet:' + str(len(dict_chemical_hetionet)))



'''
load in all compound from ndf-rt in a dictionary and get the  umls cui, rxcui
{code:'C21466'} 
'''


def load_ndf_rt_drug_in():
    query = '''MATCH (n:NDF_RT_DRUG_KIND) RETURN n'''
    results = g.run(query)
    count = 0
    i = 0
    count_name_map = 0

    for result, in results:
        count += 1
        code = result['code']
        properties = result['properties']
        name = result['name']
        properties = properties.split(',') if not type(properties)==list else properties
        association = result['association'] if result['association'] != '' else ''
        umls_cuis = set()
        rxnorm_cuis = []
        uniis=set()
        nui = ''
        node=dict(result)
        for prop in properties:
            if prop[0:8] == 'UMLS_CUI':
                cui = prop
                umls_cuis.add(cui.split(':')[1])
            elif prop[0:10] == 'RxNorm_CUI':
                cui = prop
                rxnorm_cuis.append(cui.split(':')[1])
            elif prop[0:4] == 'NUI':
                nui = prop.split(':')[1]
            elif prop[0:8]=='FDA_UNII':
                unii=prop.split(':')[1]
                uniis.add(unii)
                dict_unii_to_code[unii].append(code)


        node['umls_cui']=umls_cuis
        node['nui']=nui
        node['unii']=uniis
        # generate dictionary with rxnorm cui as key and value list of codes
        if len(rxnorm_cuis) == 1:
            if not rxnorm_cuis[0] in dict_drug_NDF_RT_rxcui_to_code:
                dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]] = [code]
            else:
                dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]].append(code)
            i += 1

            node['rxnorm_cui'] = rxnorm_cuis
        elif len(rxnorm_cuis) == 0:
            cur = conRxNorm.cursor()
            # search for rxcui with name
            query = ("Select Distinct RXCUI From RXNCONSO Where STR = '%s' ;")
            query = query % (name.lower())
            #        print(query)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                count_name_map += 1
                rxnorm_cuis = []
                for cui, in cur:
                    rxnorm_cuis.append(cui)
                rxnorm_cuis=list(set(rxnorm_cuis))

                node['rxnorm_cui'] = rxnorm_cuis
                if len(rxnorm_cuis) == 1:
                    if not rxnorm_cuis[0] in dict_drug_NDF_RT_rxcui_to_code:
                        dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]] = [code]
                    else:
                        dict_drug_NDF_RT_rxcui_to_code[rxnorm_cuis[0]].append(code)
                elif len(rxnorm_cuis) == 0:
                    dict_drug_NDF_RT_without_rxcui[code] = node
                else:
                    print('multiple rxnomrs')
            else:
                dict_drug_NDF_RT_without_rxcui[code] = node

        dict_drug_NDF_RT[code] = node


    print('number of all drugs from ndf-rt:' + str(count))
    print('length of compound in ndf-rt with rxcui:' + str(len(dict_drug_NDF_RT_rxcui_to_code)))
    a = True if count != len(dict_drug_NDF_RT_rxcui_to_code) else False
    print('is multiple mapping:' + str(a))
    print('length of compound in ndf-rt without rxcui:' + str(len(dict_drug_NDF_RT_without_rxcui)))
    print('number of name mapped rxcuis:' + str(count_name_map))


    print('number of unii:' + str(len(dict_unii_to_code)))
    print('number of mapped with unii:'+str(len(list_codes_with_drugbank_ids)))



# list of cuis which has no drugbank id
list_rxcuis_without_drugbank_ids = set()
# list_rxcuis_without_drugbank_ids=['1741407']


# list of code which are map to a drugbank id
list_codes_with_drugbank_ids = []

# dictionary from code to drugbank id
dict_mapped_code_to_db_id={}

'''
check for name mapping get the same results as the other method
'''
def check_with_name_mapping(code,mapping_values):
    name = dict_drug_NDF_RT[code]['name'].lower() if 'name' in dict_drug_NDF_RT[code] else ''
    name = name.rsplit('[', 1)[0]

    # name and xref are the same identifier
    if name in dict_synonyms_to_chemicals_ids:
        chemical_ids_name = dict_synonyms_to_chemicals_ids[name]
        intersection = chemical_ids_name.intersection(mapping_values)
        if intersection:
            chemical_ids = intersection
        else:
            return False, ''
    else:
        return False, ''
    return True, chemical_ids


'''
map rxnorm to drugbank with use of the RxNorm database and to mesh
'''


def map_rxnorm_to_drugbank_use_rxnorm_database():
    i = 0
    number_of_mapped = 0
    for rxnorm_cui in dict_drug_NDF_RT_rxcui_to_code.keys():
        i += 1
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB From RXNCONSO Where (SAB = 'DRUGBANK' or SAB='MSH') and RXCUI= %s ;")
        rows_counter = cur.execute(query, (rxnorm_cui,))
        if rows_counter > 0:
            drugbank_ids = []
            mesh_ids=[]
            for (rxcui, lat, code, sab,) in cur:
                if sab=='DRUGBANK':
                    drugbank_ids.append(code)
                else:
                    mesh_ids.append(code)
            if rxcui=='35400':
                print('test')
            drugbank_ids = list(set(drugbank_ids))
            mesh_ids = list(set(mesh_ids))
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            in_drugbank=False
            in_chemical=False
            mapped_drugs=set()
            mapped_chemical=set()
            #check the mapped drugbank ids
            for drugbank in drugbank_ids:
                if drugbank in dict_chemical_hetionet:
                    in_drugbank=True
                    mapped_drugs.add(drugbank)
            #check the mapped mesh ids
            for mesh in mesh_ids:
                if mesh in dict_chemical_hetionet:
                    in_chemical=True
                    mapped_chemical.add(mesh)
            dict_code_to_mapped={}
            if in_drugbank and in_chemical:
                print('mapped multiple')
                print(mesh_ids)
                dict_mesh_name_to_mesh_id={}
                for mesh_id in mapped_chemical:
                    dict_mesh_name_to_mesh_id[dict_chemical_hetionet[mesh_id]['name'].lower()]=[mesh_id]
                print(drugbank_ids)
                dict_drug_name_to_db_id={}
                for drugbank_id in mapped_drugs:
                    dict_drug_name_to_db_id[dict_chemical_hetionet[drugbank_id]['name'].lower()]=[drugbank_id]
                print(codes)
                find_a_mapping=False
                for code in codes:
                    name = dict_drug_NDF_RT[code]['name'].lower()
                    if name in dict_mesh_name_to_mesh_id:
                        dict_code_to_mapped[code]=dict_mesh_name_to_mesh_id[name]

                    if name in dict_drug_name_to_db_id:
                        if not code in dict_code_to_mapped:
                            dict_code_to_mapped[code]=dict_drug_name_to_db_id[name]
                        else:
                            print('error')
                            print(name)
                            print(code)
                            print(dict_drug_name_to_db_id[name])
                            print(dict_code_to_mapped[code])
                            sys.exit('mapped to both and both have the same name ;(')

                    if not code in dict_code_to_mapped:
                        print('error')
                        print(code)
                        print(name)
                        print(mesh_ids)
                        print(drugbank_ids)
                        sys.exit('no mapping with both and name')

                if not find_a_mapping:
                    print('error')
                    print(code)
                    print(name)
                    print('mapped to mesh and drugbank :(')

            if in_chemical or in_drugbank:
                for code in codes:

                    if len(mapped_drugs)>0:
                        found,mapped_drugs=check_with_name_mapping(code, mapped_drugs)
                        if not found:
                            continue
                        dict_mapped_code_to_db_id[code]=list(mapped_drugs)
                        dict_drug_NDF_RT[code]['mapped_ids'] = list(mapped_drugs)
                    else:
                        found, mapped_chemical = check_with_name_mapping(code, mapped_chemical)
                        if not found:
                            continue
                        dict_mapped_code_to_db_id[code]=list(mapped_chemical)
                        dict_drug_NDF_RT[code]['mapped_ids'] = list(mapped_chemical)
                    dict_drug_NDF_RT[code]['how_mapped']='use rxcui to drugbank ids or mesh with rxnorm'
                    if not code in list_codes_with_drugbank_ids:
                        number_of_mapped += 1
                        list_codes_with_drugbank_ids.append(code)
            else:
                if not rxnorm_cui in list_rxcuis_without_drugbank_ids:
                    list_rxcuis_without_drugbank_ids.add(rxnorm_cui)
        else:
            if not rxnorm_cui in list_rxcuis_without_drugbank_ids:
                list_rxcuis_without_drugbank_ids.add(rxnorm_cui)

    print('new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))

'''
mapp with unii to chemical
'''
def map_with_unii_to_chemical():
    # list of all codes which are mapped to drugbank id in this step
    delete_mapped_codes = set()
    for rxcui in list_rxcuis_without_drugbank_ids:
        codes = dict_drug_NDF_RT_rxcui_to_code[rxcui]
        for code in codes:
            uniis=dict_drug_NDF_RT[code]['unii']
            for unii in uniis:
                if unii in dict_unii_to_chemical_id:
                    mapped_to = dict_unii_to_chemical_id[unii]
                    found, mapped_to = check_with_name_mapping(code, mapped_to)
                    if not found:
                        continue
                    mapping_with_unii = True
                    delete_mapped_codes.add(rxcui)
                    dict_mapped_code_to_db_id[code] = mapped_to
                    dict_drug_NDF_RT[code]['mapped_ids'] = mapped_to
                    dict_drug_NDF_RT[code]['how_mapped'] = 'use unii to drugbank ids or mesh'
                    list_codes_with_drugbank_ids.append(code)

    #delete elements
    delete_elements_from_list(delete_mapped_codes)
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))

'''
load map rxnorm id to drugbank _id from dhimmel inchikey and use this to map the rest
properties:
    0:rxcui
    1:drugbank ids seperated with |
'''


def map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv', 'r')
    csv_reader=csv.reader(f,delimiter='\t')
    next(csv_reader)
    number_of_mapped = 0
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = set()
    for line in csv_reader:
        rxnorm_cui = line[0]
        drugbank_ids = line[1].split('|')
        if rxnorm_cui in list_rxcuis_without_drugbank_ids:
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            for code in codes:
                dict_drug_NDF_RT[code]['mapped_ids']=drugbank_ids
                dict_drug_NDF_RT[code]['how_mapped']='use rxcui to drugbank ids with unii and inchikey to drugbank'
                dict_mapped_code_to_db_id[code]=drugbank_ids
                delete_list.add(rxnorm_cui)
                if not code in list_codes_with_drugbank_ids:
                    number_of_mapped += 1
                    list_codes_with_drugbank_ids.append(code)

    # remove all new mapped rxcuis from not mapped list
    delete_elements_from_list(delete_list)

    print('new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))



'''
load map rxnorm id to drugbank _id from drugbank name mapped to rxnorm 
properties:
    0:drugbank_id
    1:rxcui
'''


def map_use_name_mapped_rxnorm_drugbank():
    f = open('../RxNorm_to_DrugBank/results/name_map_drugbank_to_rxnorm.tsv', 'r')
    csv_reader=csv.reader(f, delimiter='\t')
    next(csv_reader)
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = set()
    number_of_mapped = 0
    for line in csv_reader:
        rxnorm_cui = line[1]
        drugbank_id = line[0]
        if rxnorm_cui in list_rxcuis_without_drugbank_ids:
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            for code in codes:

                if not code in dict_mapped_code_to_db_id :
                    dict_drug_NDF_RT[code]['mapped_ids']=[drugbank_id]
                    dict_drug_NDF_RT[code]['how_mapped']='use rxcui to drugbank ids with name mapping'
                    delete_list.add(rxnorm_cui)
                    dict_mapped_code_to_db_id[code]=[drugbank_id]
                    if not code in list_codes_with_drugbank_ids:
                        number_of_mapped += 1
                        list_codes_with_drugbank_ids.append(code)

    # remove all new mapped rxcuis from not mapped list
    delete_elements_from_list(delete_list)

    print('number of new mapped:' + str(number_of_mapped))
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))




'''
mAPPING WITH NAME TO NAME, SYNONYM and brands name
'''
def name_mapping():
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = set()
    for rxcui in list_rxcuis_without_drugbank_ids:
        codes = dict_drug_NDF_RT_rxcui_to_code[rxcui]
        for code in codes:
            if not code in dict_mapped_code_to_db_id:

                name = dict_drug_NDF_RT[code]['name'].lower() if 'name' in dict_drug_NDF_RT[code] else ''
                name=name.rsplit('[',1)[0]
                if name in dict_synonyms_to_chemicals_ids:
                    dict_drug_NDF_RT[code]['mapped_ids'] = list(dict_synonyms_to_chemicals_ids[name])
                    dict_drug_NDF_RT[code]['how_mapped'] = 'use name mapping with synonyms and brands'
                    delete_list.add(rxcui)
                    dict_mapped_code_to_db_id[code] = list(dict_synonyms_to_chemicals_ids[name])
                    if not code in list_codes_with_drugbank_ids:
                        list_codes_with_drugbank_ids.append(code)

    # remove all new mapped rxcuis from not mapped list
    delete_elements_from_list(delete_list)

    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))


'''
mAPPING WITH umsl cui
'''


def umls_cui_mapping():
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = set()
    for rxcui in list_rxcuis_without_drugbank_ids:
        codes = dict_drug_NDF_RT_rxcui_to_code[rxcui]
        for code in codes:
            if not code in dict_mapped_code_to_db_id:

                umls_cui = dict_drug_NDF_RT[code]['umls_cui'] if 'umls_cui' in dict_drug_NDF_RT[code] else ''
                if umls_cui in dict_umls_cui_to_chemical_id:
                    dict_drug_NDF_RT[code]['mapped_ids'] = list(dict_umls_cui_to_chemical_id[umls_cui])
                    dict_drug_NDF_RT[code]['how_mapped'] = 'use name mapping with umls'
                    delete_list.add(rxcui)
                    dict_mapped_code_to_db_id[code] = list(dict_umls_cui_to_chemical_id[umls_cui])
                    if not code in list_codes_with_drugbank_ids:
                        list_codes_with_drugbank_ids.append(code)

    # remove all new mapped rxcuis from not mapped list
    delete_elements_from_list(delete_list)

    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))



# '''
# find drugbank id by using the ingredient from of drug_kind
# this is define in the association with name:Product_Component
# This can be used because drugbank is not so specific with the drugs.
# '''
#
#
# def map_to_drugbank_id_with_ingredient_from():
#     # write all drugs which are mapped with this technical in a file
#     g = open('ingredients_with_no_drugbank_id_or_not_in_hetionet.tsv', 'w')
#     csv_writer=csv.writer(g, delimiter='\t')
#     csv_writer.writerow(['code','name','associated code','name of associated code','why'])
#     number_of_mapped = 0
#     # list of all codes which are mapped to drugbank id in this step
#     delete_mapped_codes = set()
#     for rxcui in list_rxcuis_without_drugbank_ids:
#         codes = dict_drug_NDF_RT_rxcui_to_code[rxcui]
#         index = 0
#         for code in codes:
#             index += 1
#             if 'association' in dict_drug_NDF_RT[code]:
#                 associations = dict_drug_NDF_RT[code]['association']
#                 for association in associations:
#                     if association[0:17] == 'Product_Component':
#                         associatied_code = association.split(':')[1]
#                         if associatied_code in dict_drug_NDF_RT:
#                             if 'mapped_ids' in dict_drug_NDF_RT[associatied_code]:
#                                 drugbank_ids = dict_drug_NDF_RT[associatied_code]['mapped_ids']
#                                 dict_drug_NDF_RT[code]['mapped_ids']=drugbank_ids
#                                 dict_drug_NDF_RT[code]['how_mapped']='use association to the ingredient from'
#                                 if not code in list_codes_with_drugbank_ids:
#                                     number_of_mapped += 1
#                                     list_codes_with_drugbank_ids.append(code)
#                                 delete_mapped_codes.add(rxcui)
#                             else:
#                                 csv_writer.writerow([code , dict_drug_NDF_RT[code]['name'] , associatied_code ,
#                                         dict_drug_NDF_RT[
#                                             associatied_code]['name'] + 'ingredient also not mapped to drugbank id'])
#                         else:
#                             csv_writer.writerow([code , dict_drug_NDF_RT[
#                             code]['name'] , associatied_code , '' ,'ingredient not in hetionet'])
#             else:
#                 csv_writer.writerow([code, dict_drug_NDF_RT[
#                             code]['name'],'','',  ' no association in hetionet'])
#     # remove all codes from the not mapped list of the rxcui
#     delete_elements_from_list(delete_mapped_codes)
#
#     print('number of new mapped:' + str(number_of_mapped))
#
#     print('length of list of codes with all drugbank ids from rxnorm:' + str(len(list_codes_with_drugbank_ids)))


# dictionary with all cuis that are not mapped
dict_cui_to_codes = {}

# list of rxnorms without a cui
list_rxnorm_without_cui = []


# dictionary umls cuis that are mapped to hetionet, as key umls cui and value is a list of drugbank ids
dict_map_cui_to_hetionet_drugbank_ids = {}

# list of cuis that are not mapped
list_not_map_to_hetionet_with_drugbank_ids = []



# dictionary of how_mapped with file as value
dict_how_mapped_file = {}

# generate file with rxnom and a list of drugbank ids and where there are from
multiple_drugbankids = open('ndf_rt_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('ndf-rt code \t drugbank_ids with | as seperator \t where are it from  \t name\n')

'''
write a file with all ndf-rt drugs mapped to drugbank and a file with all not mapped
'''


def generate_csv_for_mapped_and_not_mapped_ndf_rts():
    for code in list_codes_with_drugbank_ids:
        drugbank_ids = dict_drug_NDF_RT[code]['mapped_ids']
        mapped_drugbanks = []
        name = dict_drug_NDF_RT[code]['name']
        string_drugbank_ids = "|".join(drugbank_ids)
        how_mapped = dict_drug_NDF_RT[code]['how_mapped']

        if not how_mapped in dict_how_mapped_file:
            how_mapped_string=how_mapped.replace(' ','_')
            map = open('drug/'+how_mapped_string+'.tsv', 'w',encoding='utf-8')
            csv_writer=csv.writer(map,delimiter='\t')
            csv_writer.writerow(['ndf-rt code','drugbank_ids with | as seperator','name'])
            dict_how_mapped_file[how_mapped]=csv_writer
        dict_how_mapped_file[how_mapped].writerow([code , string_drugbank_ids , name ])

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(code + '\t' + string_drugbank_ids + '\t' + how_mapped + '\t' + name + '\n')

        if len(drugbank_ids) >= 1:
            dict_map_cui_to_hetionet_drugbank_ids[code] = mapped_drugbanks
        else:
            list_not_map_to_hetionet_with_drugbank_ids.append(code)

    print('number of map to hetionet:' + str(len(dict_map_cui_to_hetionet_drugbank_ids)))
    print('number with drugbank but not mapped to hetionet:' + str(len(list_not_map_to_hetionet_with_drugbank_ids)))

    # generate a file with all not mapped ndf-rt drugs
    g = open('drug/drugs_that_did_not_get_a_drugbank_id.tsv', 'w')
    g.write('ndf-rt code \t rxcuis \t uniis \t name\n')
    for code, drug in dict_drug_NDF_RT.items():
        if not code in list_codes_with_drugbank_ids:
            rxcuis = list(dict_drug_NDF_RT[code]['rxnorm_cuis']) if 'rxnorm_cuis' in dict_drug_NDF_RT[code] else []
            string_rxcui = '|'.join(rxcuis)
            uniis = list(dict_drug_NDF_RT[code]['uniis']) if 'uniis' in dict_drug_NDF_RT[code] else []
            string_uniis = '|'.join(uniis)
            g.write(code + '\t' + string_rxcui + '\t' + string_uniis + '\t' + drug['name'] + '\n')
    g.close()


# dictionary count of delete of drugbank id from different mapping methods
dict_how_mapped_delete_counter = {}

'''
integrate the ndf-rt drugs into hetionet for the drugs which are map to drugbank and generate a cypher file 
a connection between compounds in hetionet and ndf-rt drug.
'''


def integration_of_ndf_rt_drugs_into_hetionet():
    # count all possible mapped ndf-rt codes
    counter = 0
    # count all ndf-rt codes which has illegal drugbank ids
    counter_illegal_drugbank = 0
    # number of all connection
    counter_drugbank_connection = 0
    # list wiwth all codes which are mapped to only illegal drugbank ids
    delete_code = []

    cypher_file=open('drug/cypher.cypher','w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ndf-rt/drug/mapping_drug.csv" As line  FIELDTERMINATOR '\\t'  MATCH (n:NDF_RT_DRUG_KIND{code:line.code}), (c:Chemical{identifier:line.Chemical_id})  Set n.mapped_ids=split(line.mapped_ids,'|'), n.how_mapped=line.how_mapped, c.ndf_rt='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_drug_ndf_rt]->(n); \n'''
    cypher_file.write(query)
    cypher_file.close()
    writer=open('drug/mapping_drug.csv','w')
    csv_writer=csv.writer(writer,delimiter='\t')
    header=['code','mapped_ids','how_mapped','Chemical_id','resource']
    csv_writer.writerow(header)
    for code in list_codes_with_drugbank_ids:
        if code=='C11442':
            print('huhu')
        counter += 1
        drugbank_ids = dict_drug_NDF_RT[code]['mapped_ids']
        string_drugbank_ids = "|".join(drugbank_ids)
        how_mapped = dict_drug_NDF_RT[code]['how_mapped']


        for drugbank_id in drugbank_ids:
            resources=set(dict_chemical_hetionet[drugbank_id]['resource'])
            resources.add('NDF-RT')
            string_resource='|'.join(list(resources))
            list_of_values=[code,string_drugbank_ids,how_mapped,drugbank_id,string_resource]
            csv_writer.writerow(list_of_values)


    # the general cypher file to update all chemicals and relationship which are not from ndfrt
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    # all not mapped compound get as property ndf-rt='no'
    query = ''':begin \n Match (c:Chemical) Where not exists(c.ndf_rt) 
            Set c.ndf_rt="no"; \n :commit '''
    cypher_general.write(query)
    cypher_general.close()


def main():

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in chemical from hetionet')

    load_hetionet_chemical_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in drug from ndf-rt')

    load_ndf_rt_drug_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map rxcui to drugbank ids with use of rxnorm')

    map_rxnorm_to_drugbank_use_rxnorm_database()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map unii to drugbank ids')

    map_with_unii_to_chemical()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map rxcui to drugbank ids with use of rxnorm-drugbank table with unii and inchikey from dhimmel')

    map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map rxcui to drugbank ids with use of rxnorm-drugbank table with name mapping')

    map_use_name_mapped_rxnorm_drugbank()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('name mapping')

    name_mapping()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('umls mapping')

    umls_cui_mapping()

    # print(
    #     '###########################################################################################################################')
    #
    # print (datetime.datetime.utcnow())
    # print('map with use of the ingredient')
    #
    # map_to_drugbank_id_with_ingredient_from()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('create csv files for mapped and not mapped ndf-rt drugs')

    generate_csv_for_mapped_and_not_mapped_ndf_rts()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('integrate ndf-rt drugs into hetionet')

    integration_of_ndf_rt_drugs_into_hetionet()
    #
    # print(
    #     '###########################################################################################################################')
    #
    # print (datetime.datetime.utcnow())
    # print('integrate ndf-rt connection into hetionet')
    #
    # integrate_connection_into_hetionet()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()