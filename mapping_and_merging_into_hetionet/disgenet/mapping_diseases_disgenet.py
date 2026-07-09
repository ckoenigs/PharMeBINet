import datetime
import os
import sys
import csv
import pandas as pd
from collections import defaultdict
import mapping_symptoms_disgenet

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


# dictionary disease id to Disease identifier
dict_umls_id_to_identifier = defaultdict(set)

# dictionary umls id to Disease identifier
dict_umls_id_from_umls_to_identifier = defaultdict(set)

# dictionary from disease id to resource
dict_disease_id_to_resource = defaultdict(set)

# dictionary from disease id to licenses
dict_disease_id_to_licenses = defaultdict(set)

# dict for alternative_ids
dict_xrefs_to_identifier = defaultdict(set)

# dict for name
dict_name_to_identifier = defaultdict(set)

license = pharmebinetutils.dict_source_to_license['disgenet']


def try_to_get_umls_ids_with_UMLS(name):
    """
    Try to get umls cuis be search with name in UMLS
    :param name:
    :return:
    """
    cur = con.cursor()
    query = ('Select Distinct CUI From MRCONSO Where STR = "%s";')
    query = query % (name)
    rows_counter = cur.execute(query)

    list_of_cuis = []

    if rows_counter > 0:
        # add found cuis
        for (cui,) in cur:
            list_of_cuis.append(cui)

    return list_of_cuis


def load_disease_from_database_and_add_to_dict():
    '''
    Load all Diseases from Graph-DB and add them into a dictionary
    '''
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        # for mapping with MONDO
        dict_disease_id_to_resource[identifier] = node['resource']
        dict_disease_id_to_licenses[identifier] = set(node['licenses'])

        name = node['name'].lower()
        dict_name_to_identifier[name].add(identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
            dict_name_to_identifier[synonym].add(identifier)

        if 'xrefs' in node:
            # find index of xrefs "UMLS" entry
            umls_id_idx = [item for item in node['xrefs'] if item.startswith('UMLS')]
            # save all relevant xrefs (for alternative mapping)
            xrefs = [nr for nr in node['xrefs'] if nr.startswith(('NCIT'))]  # 'ICD', , 'DOID',  'OMIM'
            for xref in xrefs:
                dict_xrefs_to_identifier[xref].add(identifier)
        else:
            umls_id_idx = []

        # add alternative DOIDs to previous xref-dict if exist
        if 'doids' in node:
            for do_id in node['doids']:
                dict_xrefs_to_identifier[do_id].add(identifier)

        # for mapping with UMLS
        if umls_id_idx:
            # _, umls_id = node['xrefs'][umls_id_idx[0]].split(':')
            for umls_id in umls_id_idx:
                umls_id = umls_id.split(':')[1]
                # put umls_id as identifier if 'UMLS' exists in xrefs
                dict_umls_id_to_identifier[umls_id].add(identifier)
        else:
            umls_cuis = try_to_get_umls_ids_with_UMLS(name)
            for umls_id in umls_cuis:
                dict_umls_id_from_umls_to_identifier[umls_id].add(identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'DisGeNet_disease_to_disease'

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    query = f' Match (n:disease_DisGeNet{{diseaseId:line.DisGeNet_diseaseId}}), (v:Disease{{identifier:line.identifier}}) Set v.disgenet=true, v.resource=split(line.resource,"|"),  v.licenses=split(line.licenses,"|") Create (v)-[:equal_to_DisGeNet_disease{{mapped_with:split(line.mapping_method, "|")}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name + '.tsv',
                                              query)
    cypher_file.write(query)

    query = mapping_symptoms_disgenet.generate_files(path_of_directory)

    cypher_file.write(query)
    cypher_file.close()


def check_for_multiple_mapping_and_try_to_reduce_multiple_mapping(name, mapping_ids):
    """
    Try to reduce multiple mapping be also consider name mapping ids intersection
    :param name: string
    :param mapping_ids: set of mapped ids
    :return: set of ids
    """
    if len(mapping_ids) > 1 and name in dict_name_to_identifier:
        name_mapped_ids = dict_name_to_identifier[name]
        intersection = name_mapped_ids.intersection(mapping_ids)
        if len(intersection) > 0:
            return intersection

    return mapping_ids


def find_mondo(node):
    # find xrefs "MONDO" entry
    mondo_id_idx = [i for i, item in enumerate(node['code']) if item.startswith('MONDO:')]
    mondo_lst = [node['code'][idx] for idx in mondo_id_idx]
    return mondo_lst


def find_code(node):
    # return all relevant alternative-ids that are listed in disease_disGeNet under 'code'
    code_lst = [i for i in node['code'] if i.startswith(('NCI'))]  # 'ICD', , 'DO',  'OMIM'
    return code_lst


def write_to_tsv_file(disgenet_id, pharmebinet_id, list_of_entries, mapping_method):
    dict_disease_id_to_licenses[pharmebinet_id].add(license)
    list_of_entries.append([disgenet_id, pharmebinet_id,
                             pharmebinetutils.resource_add_and_prepare(
                                 dict_disease_id_to_resource[pharmebinet_id], 'DisGeNet'),
                             mapping_method, '|'.join(dict_disease_id_to_licenses[pharmebinet_id])])


def load_all_DisGeNet_disease_and_finish_the_files():
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:disease_DisGeNet) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    equivalent_id_map = {"OMIM": "OMIM", "NCI": "NCIT", "ICD10CM": "ICD10", "ICD10": "ICD10", "ICD9CM": "ICD9",
                         "ICD9": "ICD9", "DO": "DOID"}

    not_mapped_path = os.path.join(path_of_directory, 'not_mapped.tsv')
    header = ['DisGeNet_diseaseId', 'diseaseName', 'xrefs']
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(header)

    list_of_entries = []

    for record in results:
        node = record.data()['n']
        counter_all += 1
        umls_id = node['diseaseId']
        if 'code' in node:
            mondo_ids = find_mondo(node)
            code_ids = find_code(node)
        else:
            mondo_ids = []
            code_ids = []

        name = node['diseaseName'].lower()

        found_mappping = False
        # mapping via UMLS
        # print("umls " + umls_id)
        if umls_id in dict_umls_id_to_identifier:
            ids_with_umls = dict_umls_id_to_identifier[umls_id]
            maybe_reduced_ids = check_for_multiple_mapping_and_try_to_reduce_multiple_mapping(name, ids_with_umls)
            for mondo_id in maybe_reduced_ids:
                found_mappping = True
                write_to_tsv_file(umls_id, mondo_id, list_of_entries, 'umls')

        if found_mappping:
            continue
        # mapping via name
        elif name:
            if name in dict_name_to_identifier:
                for mondo_id in dict_name_to_identifier[name]:
                    found_mappping = True
                    write_to_tsv_file(umls_id, mondo_id, list_of_entries, 'name')

        if found_mappping:
            continue

        refs = node['code'] if 'code' in node else []
        # mapping symptoms
        found_mappping = mapping_symptoms_disgenet.load_all_unmapped_DisGeNet_disease_and_finish_the_files(name,
                                                                                                           umls_id,
                                                                                                           refs)

        if found_mappping:
            continue
        # mapping via umls
        elif umls_id in dict_umls_id_from_umls_to_identifier:
            for mondo_id in dict_umls_id_from_umls_to_identifier[umls_id]:
                found_mappping = True
                write_to_tsv_file(umls_id, mondo_id, list_of_entries, 'umls_umls')

        # if found_mappping:
        #     continue
        # # mapping via MONDO
        # elif mondo_ids:
        #     for mondo_id in mondo_ids:
        #         if mondo_id in dict_disease_id_to_resource:
        #             found_mappping=True
        #             write_to_tsv_file(umls_id, mondo_id, list_of_entries, 'id')

        if found_mappping:
            continue
        # mapping via xrefs
        elif code_ids:
            for item in code_ids:
                name, id_num = item.split(':', 1)
                # generate equivalent ID (which might be a possible entry in Disease-dictionnary [dict_xrefs_to_id])
                equ_id = equivalent_id_map[name] + ":" + id_num  # if name in equivalent_id_map.keys() else name
                if equ_id in dict_xrefs_to_identifier:
                    found_mappping = True
                    mondo_ids = dict_xrefs_to_identifier[equ_id]
                    for mondo_id in mondo_ids:  # in case of several values for one id
                        write_to_tsv_file(umls_id, mondo_id, list_of_entries, equivalent_id_map[name].lower())

        if found_mappping:
            continue
        else:
            counter_not_mapped += 1
            # codes = '|'.join(n for n in node['code']) if 'code' in node else None
            writer.writerow([umls_id, node['diseaseName'], refs])

    mapping_df = pd.DataFrame(list_of_entries,columns=['DisGeNet_diseaseId', 'identifier', 'resource', 'mapping_method', 'licenses'])
    file.close()
    # aggregate the entries that were mapped several times
    df_grouped = mapping_df.groupby(['DisGeNet_diseaseId', 'identifier', 'resource', 'licenses'], as_index=False).agg(
        {'mapping_method': set})
    df_grouped['mapping_method'] = df_grouped['mapping_method'].apply(lambda x: '|'.join(list(x)))

    file_name = 'DisGeNet_disease_to_disease'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    df_grouped.to_csv(file_path, sep='\t', index=False, na_rep='')

    print('number of not-mapped disease_ids:', counter_not_mapped)
    print('number of all disease_ids:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet disease')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'disease/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Diseases from database')
    load_disease_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Symptoms from database')
    mapping_symptoms_disgenet.load_symptoms_from_database_and_add_to_dict(g)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    generate_files(path_of_directory)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all DisGeNet diseases from database')
    load_all_DisGeNet_disease_and_finish_the_files()


if __name__ == "__main__":
    # execute only if run as a script
    main()
