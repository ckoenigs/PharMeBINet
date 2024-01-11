import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary with chemical id as key and resource
dict_chemical_pharmebinet_to_resource = {}

# dictionary with chemical id as key and name
dict_chemical_pharmebinet_to_name = {}

# dictionary with code as key and value is class DrugNDF_RT
dict_drug_NDF_RT = {}

# dictionary with rxcui as key and value is list of codes
dict_drug_NDF_RT_rxcui_to_code = {}

# dictionary with code as key and value is class DrugNDF_RT
dict_drug_NDF_RT_without_rxcui = {}

# dictionary unii to code because this is needed in a mapping step
dict_unii_to_code = defaultdict(list)

# dictionary synonyms/name/brands chemical ids
dict_synonyms_to_chemicals_ids = {}

# dictionary from rxcui to chemical ids
dict_rnxnorm_to_chemical_id = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

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


# dictionary from unii to chemical id
dict_unii_to_chemical_id = {}

# dictionary umls cui to chemical id
dict_umls_cui_to_chemical_id = {}


def check_for_rxcui(name, rxcui):
    """
    check if the rxcui ids are right
    :param name: string
    :param rxcui: string
    :return: list of strings
    """
    query = ('Select Distinct RXCUI  From RXNCONSO Where STR ="%s" ;')
    query = query % (name)
    # print(query)

    cur = conRxNorm.cursor()
    rows_counter = cur.execute(query)
    found_id = False
    if rows_counter > 0:
        other_id = []
        for rxnorm_cui in cur:
            if rxnorm_cui[0] == rxcui:
                found_id = True
            else:
                other_id.append(rxnorm_cui[0])
    else:
        # there is nothing that can found in rxnorm
        found_id = True
    if found_id:
        return [rxcui]
    else:
        return other_id


'''
load in all compound from pharmebinet in a dictionary
'''


def load_pharmebinet_chemical_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier,n.unii, n.name, n.synonyms, n.international_brands_name_company, n.xrefs, n.resource '''
    results = g.run(query)

    for record in results:
        [identifier, unii, name, synonyms, brand_name_and_companys, xrefs, resource] = record.values()
        dict_chemical_pharmebinet_to_resource[identifier] = resource
        dict_chemical_pharmebinet_to_name[identifier] = name
        if unii is not None:
            if unii in dict_unii_to_chemical_id:
                sys.exit('ohje unii')
            dict_unii_to_chemical_id[unii] = [identifier]
        name = name.lower() if name is not None else ''
        if not name in dict_synonyms_to_chemicals_ids and name != '':
            dict_synonyms_to_chemicals_ids[name] = set()
        elif name != '':
            dict_synonyms_to_chemicals_ids[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if not synonym in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[synonym] = set()
                dict_synonyms_to_chemicals_ids[synonym].add(identifier)

        if brand_name_and_companys:
            for brand_name_and_company in brand_name_and_companys:
                brand_name = brand_name_and_company.split('::')[0]
                if not brand_name in dict_synonyms_to_chemicals_ids:
                    dict_synonyms_to_chemicals_ids[brand_name] = set()
                dict_synonyms_to_chemicals_ids[brand_name].add(identifier)

        if xrefs:
            for xref in xrefs:
                if xref.startswith('RxNorm_CUI:'):
                    xref = xref.split(':', 1)[1]
                    rxcuis = check_for_rxcui(name, xref)
                    for rxcui in rxcuis:
                        if rxcui not in dict_rnxnorm_to_chemical_id:
                            dict_rnxnorm_to_chemical_id[rxcui] = set()
                        dict_rnxnorm_to_chemical_id[rxcui].add(identifier)

        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where (SAB = 'DRUGBANK' or SAB='MSH') and CODE= %s ;")
        rows_counter = cur.execute(query, (identifier,))
        if rows_counter > 0:
            for (cui, lat, code, sab,) in cur:
                if cui not in dict_umls_cui_to_chemical_id:
                    dict_umls_cui_to_chemical_id[cui] = set()
                dict_umls_cui_to_chemical_id[cui].add(identifier)

    print('length of compound in pharmebinet:' + str(len(dict_chemical_pharmebinet_to_resource)))


'''
load in all compound from ndf-rt in a dictionary and get the  umls cui, rxcui
{code:'C21466'} 
'''


def load_ndf_rt_drug_in():
    #
    query = '''MATCH (n:NDFRT_DRUG_KIND) RETURN n'''
    results = g.run(query)
    count = 0
    i = 0
    count_name_map = 0

    for record in results:
        result = record.data()['n']
        count += 1
        code = result['code']
        properties = result['properties']
        name = result['name']
        properties = properties.split(',') if not type(properties) == list else properties
        association = result['association'] if 'association' in result else ''
        umls_cuis = set()
        rxnorm_cuis = []
        uniis = set()
        nui = ''
        node = dict(result)
        for prop in properties:
            if prop.startswith('UMLS_CUI'):
                cui = prop
                umls_cuis.add(cui.split(':')[1])
            elif prop.startswith('RxNorm_CUI'):
                cui = prop
                rxnorm_cuis.append(cui.split(':')[1])
            elif prop.startswith('NUI'):
                nui = prop.split(':')[1]
            elif prop.startswith('FDA_UNII'):
                unii = prop.split(':')[1]
                uniis.add(unii)
                dict_unii_to_code[unii].append(code)

        node['umls_cui'] = umls_cuis
        node['nui'] = nui
        node['unii'] = uniis
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
                rxnorm_cuis = list(set(rxnorm_cuis))

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
    print('number of mapped with unii:' + str(len(list_codes_with_drugbank_ids)))


# list of cuis which has no drugbank id
list_rxcuis_without_drugbank_ids = set()
# list_rxcuis_without_drugbank_ids=['1741407']


# list of code which are map to a drugbank id
list_codes_with_drugbank_ids = []

# dictionary from code to drugbank id
dict_mapped_code_to_db_id = {}

'''
check for name mapping get the same results as the other method
'''


def check_with_name_mapping(code, mapping_values):
    name = dict_drug_NDF_RT[code]['name'].lower() if 'name' in dict_drug_NDF_RT[code] else ''
    name = name.rsplit('[', 1)[0]

    # name and xref are the same identifier
    if name:
        if name in dict_synonyms_to_chemicals_ids:
            chemical_ids_name = dict_synonyms_to_chemicals_ids[name]
            intersection = chemical_ids_name.intersection(mapping_values)
            if intersection:
                chemical_ids = intersection
            else:
                if chemical_ids_name:
                    chemical_ids = chemical_ids_name
                else:
                    return False, ''
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
        if rxnorm_cui in dict_rnxnorm_to_chemical_id:
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            mapped_drugs = dict_rnxnorm_to_chemical_id[rxnorm_cui]
            for code in codes:
                dict_mapped_code_to_db_id[code] = list(mapped_drugs)
                dict_drug_NDF_RT[code]['mapped_ids'] = list(mapped_drugs)
                dict_drug_NDF_RT[code]['how_mapped'] = 'use rxcui to drugbank ids with xrefs'
                if not code in list_codes_with_drugbank_ids:
                    number_of_mapped += 1
                    list_codes_with_drugbank_ids.append(code)
            continue
        i += 1
        cur = conRxNorm.cursor()
        query = ("Select RXCUI,LAT,CODE,SAB From RXNCONSO Where (SAB = 'DRUGBANK' or SAB='MSH') and RXCUI= %s ;")
        rows_counter = cur.execute(query, (rxnorm_cui,))
        if rows_counter > 0:
            drugbank_ids = []
            mesh_ids = []
            for (rxcui, lat, code, sab,) in cur:
                if sab == 'DRUGBANK':
                    drugbank_ids.append(code)
                else:
                    mesh_ids.append(code)
            if rxcui == '35400':
                print('test')
            drugbank_ids = list(set(drugbank_ids))
            mesh_ids = list(set(mesh_ids))
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            in_drugbank = False
            in_chemical = False
            mapped_drugs = set()
            mapped_chemical = set()
            # check the mapped drugbank ids
            for drugbank in drugbank_ids:
                if drugbank in dict_chemical_pharmebinet_to_resource:
                    in_drugbank = True
                    mapped_drugs.add(drugbank)
            # check the mapped mesh ids
            for mesh in mesh_ids:
                if mesh in dict_chemical_pharmebinet_to_resource:
                    in_chemical = True
                    mapped_chemical.add(mesh)
            dict_code_to_mapped = {}
            if in_drugbank and in_chemical:
                print('mapped multiple')
                print(mesh_ids)
                dict_mesh_name_to_mesh_id = {}
                for mesh_id in mapped_chemical:
                    dict_mesh_name_to_mesh_id[dict_chemical_pharmebinet_to_name[mesh_id].lower()] = [mesh_id]
                print(drugbank_ids)
                dict_drug_name_to_db_id = {}
                for drugbank_id in mapped_drugs:
                    dict_drug_name_to_db_id[dict_chemical_pharmebinet_to_name[drugbank_id].lower()] = [drugbank_id]
                print(codes)
                find_a_mapping = False
                for code in codes:
                    name = dict_drug_NDF_RT[code]['name'].lower()
                    if name in dict_mesh_name_to_mesh_id:
                        dict_code_to_mapped[code] = dict_mesh_name_to_mesh_id[name]

                    if name in dict_drug_name_to_db_id:
                        if not code in dict_code_to_mapped:
                            dict_code_to_mapped[code] = dict_drug_name_to_db_id[name]
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

                    if len(mapped_drugs) > 0:
                        found, mapped_drugs = check_with_name_mapping(code, mapped_drugs)
                        if not found:
                            if not rxnorm_cui in list_rxcuis_without_drugbank_ids:
                                list_rxcuis_without_drugbank_ids.add(rxnorm_cui)
                            continue
                        dict_mapped_code_to_db_id[code] = list(mapped_drugs)
                        dict_drug_NDF_RT[code]['mapped_ids'] = list(mapped_drugs)
                    else:
                        found, mapped_chemical = check_with_name_mapping(code, mapped_chemical)
                        if not found:
                            if not rxnorm_cui in list_rxcuis_without_drugbank_ids:
                                list_rxcuis_without_drugbank_ids.add(rxnorm_cui)
                            continue
                        dict_mapped_code_to_db_id[code] = list(mapped_chemical)
                        dict_drug_NDF_RT[code]['mapped_ids'] = list(mapped_chemical)
                    dict_drug_NDF_RT[code]['how_mapped'] = 'use rxcui to drugbank ids or mesh with rxnorm'
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
            if code in dict_mapped_code_to_db_id:
                continue
            uniis = dict_drug_NDF_RT[code]['unii']
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

    # delete elements
    delete_elements_from_list(delete_mapped_codes)
    print('length of list of rxcuis with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))
    print('length of list of rxcuis without drugbank ids from rxnorm:' + str(len(list_rxcuis_without_drugbank_ids)))
    print('length of list of codes with all drugbank ids from rxnorm:' + str(len(dict_mapped_code_to_db_id)))


'''
load map rxnorm id to drugbank _id from dhimmel inchikey and use this to map the rest
properties:
    0:rxcui
    1:drugbank ids separated with |
'''


def map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv', 'r')
    csv_reader = csv.reader(f, delimiter='\t')
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

                if code in dict_mapped_code_to_db_id:
                    continue
                dict_drug_NDF_RT[code]['mapped_ids'] = drugbank_ids
                dict_drug_NDF_RT[code]['how_mapped'] = 'use rxcui to drugbank ids with unii and inchikey to drugbank'
                dict_mapped_code_to_db_id[code] = drugbank_ids
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
    csv_reader = csv.reader(f, delimiter='\t')
    next(csv_reader)
    # list of all rxcuis which are mapped to drugbank id in this step
    delete_list = set()
    number_of_mapped = 0
    for line in csv_reader:
        rxnorm_cui = line[0]
        drugbank_id = line[1]
        if rxnorm_cui in list_rxcuis_without_drugbank_ids:
            codes = dict_drug_NDF_RT_rxcui_to_code[rxnorm_cui]
            for code in codes:

                if code in dict_mapped_code_to_db_id:
                    continue
                if not code in dict_mapped_code_to_db_id:
                    dict_drug_NDF_RT[code]['mapped_ids'] = [drugbank_id]
                    dict_drug_NDF_RT[code]['how_mapped'] = 'use rxcui to drugbank ids with name mapping'
                    delete_list.add(rxnorm_cui)
                    dict_mapped_code_to_db_id[code] = [drugbank_id]
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
                name = name.rsplit('[', 1)[0] if not name.startswith('[') else name.rsplit('] ', 1)[1]
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

                umls_cuis = dict_drug_NDF_RT[code]['umls_cui'] if 'umls_cui' in dict_drug_NDF_RT[code] else ''
                for umls_cui in umls_cuis:
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


# dictionary with all cuis that are not mapped
dict_cui_to_codes = {}

# list of rxnorms without a cui
list_rxnorm_without_cui = []

# dictionary umls cuis that are mapped to pharmebinet, as key umls cui and value is a list of drugbank ids
dict_map_cui_to_pharmebinet_drugbank_ids = {}

# list of cuis that are not mapped
list_not_map_to_pharmebinet_with_drugbank_ids = []

# dictionary of how_mapped with file as value
dict_how_mapped_file = {}

# generate file with rxnom and a list of drugbank ids and where there are from
multiple_drugbankids = open('ndf_rt_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('ndf-rt code \t drugbank_ids with | as seperator \t where are it from  \t name\n')

'''
write a file with all ndf-rt drugs mapped to drugbank and a file with all not mapped
'''


def generate_tsv_for_mapped_and_not_mapped_ndf_rts():
    for code in list_codes_with_drugbank_ids:
        drugbank_ids = dict_drug_NDF_RT[code]['mapped_ids']
        mapped_drugbanks = []
        name = dict_drug_NDF_RT[code]['name']
        string_drugbank_ids = "|".join(drugbank_ids)
        how_mapped = dict_drug_NDF_RT[code]['how_mapped']

        if not how_mapped in dict_how_mapped_file:
            how_mapped_string = how_mapped.replace(' ', '_')
            map = open('drug/' + how_mapped_string + '.tsv', 'w', encoding='utf-8')
            csv_writer = csv.writer(map, delimiter='\t')
            csv_writer.writerow(['ndf-rt code', 'drugbank_ids with | as seperator', 'name'])
            dict_how_mapped_file[how_mapped] = csv_writer
        dict_how_mapped_file[how_mapped].writerow([code, string_drugbank_ids, name])

        if len(drugbank_ids) > 1:
            multiple_drugbankids.write(code + '\t' + string_drugbank_ids + '\t' + how_mapped + '\t' + name + '\n')

        if len(drugbank_ids) >= 1:
            dict_map_cui_to_pharmebinet_drugbank_ids[code] = mapped_drugbanks
        else:
            list_not_map_to_pharmebinet_with_drugbank_ids.append(code)

    print('number of map to pharmebinet:' + str(len(dict_map_cui_to_pharmebinet_drugbank_ids)))
    print(
        'number with drugbank but not mapped to pharmebinet:' + str(len(list_not_map_to_pharmebinet_with_drugbank_ids)))

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
integrate the ndf-rt drugs into pharmebinet for the drugs which are map to drugbank and generate a cypher file 
a connection between compounds in pharmebinet and ndf-rt drug.
'''


def integration_of_ndf_rt_drugs_into_pharmebinet():
    # count all possible mapped ndf-rt codes
    counter = 0
    # count all ndf-rt codes which has illegal drugbank ids
    counter_illegal_drugbank = 0
    # number of all connection
    counter_drugbank_connection = 0
    # list with all codes which are mapped to only illegal drugbank ids
    delete_code = []

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = '''  MATCH (n:NDFRT_DRUG_KIND{code:line.code}), (c:Chemical{identifier:line.Chemical_id})  Set   c.ndf_rt='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_drug_ndf_rt{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ndf-rt/drug/mapping_drug.tsv',
                                              query)
    cypher_file.write(query)
    query = '''Match (b:Chemical)--(:NDFRT_DRUG_KIND)-[:effect_may_be_inhibited_by]->(:NDFRT_DRUG_KIND)--(c:Chemical) Merge (b)<-[r:INTERACTS_CHiCH]-(c)  On Match Set r.resource=r.resource+'NDF-RT', r.ndf_rt='yes' On Create set r.resource=['NDF-RT'], r.source='NDF-RT', r.ndf_rt='yes', r.license='UMLS license, available at https://uts.nlm.nih.gov/license.html';\n '''
    cypher_file.write(query)
    cypher_file.close()
    writer = open('drug/mapping_drug.tsv', 'w')
    csv_writer = csv.writer(writer, delimiter='\t')
    header = ['code', 'how_mapped', 'Chemical_id', 'resource']
    csv_writer.writerow(header)
    for code in list_codes_with_drugbank_ids:
        if code == 'C11442':
            print('huhu')
        counter += 1
        drugbank_ids = dict_drug_NDF_RT[code]['mapped_ids']
        if len(drugbank_ids) > 1:
            print('multiple maPPING NODES', code, '|'.join(drugbank_ids))
        how_mapped = dict_drug_NDF_RT[code]['how_mapped']

        for drugbank_id in drugbank_ids:
            resources = set(dict_chemical_pharmebinet_to_resource[drugbank_id])
            resources.add('NDF-RT')
            string_resource = '|'.join(list(resources))
            list_of_values = [code, how_mapped, drugbank_id, string_resource]
            csv_writer.writerow(list_of_values)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in chemical from pharmebinet')

    load_pharmebinet_chemical_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in drug from ndf-rt')

    load_ndf_rt_drug_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map rxcui to drugbank ids with use of rxnorm')

    map_rxnorm_to_drugbank_use_rxnorm_database()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map unii to drugbank ids')

    map_with_unii_to_chemical()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map rxcui to drugbank ids with use of rxnorm-drugbank table with unii and inchikey from dhimmel')

    map_use_dhimmel_rxnorm_drugbank_map_unii_inchikey()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map rxcui to drugbank ids with use of rxnorm-drugbank table with name mapping')

    # map_use_name_mapped_rxnorm_drugbank()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('name mapping')

    name_mapping()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('umls mapping')

    umls_cui_mapping()

    # print(
    #     '###########################################################################################################################')
    #
    # print (datetime.datetime.now())
    # print('map with use of the ingredient')
    #
    # map_to_drugbank_id_with_ingredient_from()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('create tsv files for mapped and not mapped ndf-rt drugs')

    generate_tsv_for_mapped_and_not_mapped_ndf_rts()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('integrate ndf-rt drugs into pharmebinet')

    integration_of_ndf_rt_drugs_into_pharmebinet()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
