import datetime
import os
import sys
import csv
import pandas as pd
from collections import defaultdict
sys.path.append("../..")
import create_connection_to_databases


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary disease id to Disease identifier
dict_umls_id_to_identifier = defaultdict(set)

#dictionary from disease id to resource
dict_disease_id_to_resource = defaultdict(set)

#dict for alternative_ids
dict_xrefs_to_identifier = defaultdict(set)


def load_disease_from_database_and_add_to_dict():
    '''
    Load all Diseases from Graph-DB and add them into a dictionary
    '''
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)

    for node, in results:
        identifier = node['identifier']
        #for mapping with MONDO
        dict_disease_id_to_resource[identifier] = node['resource'] 


        if 'xrefs' in node:
            # find index of xrefs "UMLS" entry
            umls_id_idx = [i for i, item in enumerate(node['xrefs']) if item.startswith('UMLS')]
            # save all relevant xrefs (for alternative mapping)
            xrefs = [nr for nr in node['xrefs'] if nr.startswith(('NCIT', 'ICD', 'OMIM'))]
            for xref in xrefs:
                dict_xrefs_to_identifier[xref].add(identifier)
        else:
            umls_id_idx = []

        # for mapping with UMLS
        if umls_id_idx:
            _, umls_id = node['xrefs'][umls_id_idx[0]].split(':')
            # put umls_id as identifier if 'UMLS' exists in xrefs
            dict_umls_id_to_identifier[umls_id] = identifier



def generate_files(path_of_directory):
    """
    generate cypher file and csv file
    :return: csv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'DisGeNet_disease_to_disease'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['DisGeNet_diseaseId', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # master_database_change/mapping_and_merging_into_hetionet/DisGeNet/
    query = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}{file_name}.tsv" As line FIELDTERMINATOR "\\t" \
        Match (n:disease_DisGeNet{{diseaseId:line.DisGeNet_diseaseId}}), (v:Disease{{identifier:line.identifier}}) Set v.DisGeNet="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DisGeNet_disease{{mapped_with:line.mapping_method}}]->(n);\n'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    return csv_mapping


def resource(identifier):
    resource = set(dict_disease_id_to_resource[identifier])
    resource.add('DisGeNet')
    return '|'.join(resource)


def find_mondo(node):
    # find xrefs "MONDO" entry
    mondo_id_idx = [i for i, item in enumerate(node['code']) if item.startswith('MONDO:')]
    mondo_lst = [node['code'][idx] for idx in mondo_id_idx]
    return mondo_lst


def find_code(node):
    # return all relevant alternative-ids that are listed in disease_disGeNet under 'code'
    code_lst = [i for i in node['code'] if i.startswith(('NCI', 'ICD', 'OMIM'))]
    return code_lst

def load_all_DisGeNet_disease_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
    """

    query = "MATCH (n:disease_DisGeNet) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    equivalent_id_map = {"OMIM": "OMIM", "NCI": "NCIT", "ICD10CM": "ICD10", "ICD10": "ICD10", "ICD9CM": "ICD9", "ICD9":"ICD9"}

    not_mapped_path = os.path.join(path_of_directory, 'not_mapped.csv')
    header = ['DisGeNet_diseaseId', 'diseaseName', 'xrefs']
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow(header)

    for node, in results:
        counter_all += 1
        umls_id = node['diseaseId']
        if 'code' in node:
            mondo_ids = find_mondo(node)
            code_ids = find_code(node)
        else:
            mondo_ids = []
            code_ids = []
        # mapping via UMLS
        # print("umls " + umls_id)
        if umls_id in dict_umls_id_to_identifier:
            identifier = dict_umls_id_to_identifier[umls_id] #Disease Identifier
            csv_mapping.writerow([umls_id, identifier, resource(identifier), 'umls'])
        # mapping via MONDO
        elif mondo_ids:
            for mondo_id in mondo_ids:
                if mondo_id in dict_disease_id_to_resource:
                    csv_mapping.writerow([umls_id, mondo_id, resource(mondo_id), 'id'])
        # mapping via xrefs
        elif code_ids:
            for item in code_ids:
                name, id_num = item.split(':', 1)
                # generate equivalent ID (which might be a possible entry in Disease-dictionnary [dict_xrefs_to_id])
                equ_id = equivalent_id_map[name] + ":" + id_num # if name in equivalent_id_map.keys() else name
                if equ_id in dict_xrefs_to_identifier:
                    identifier = dict_xrefs_to_identifier[equ_id]
                    for ident in identifier: # in case of several values for one id
                        csv_mapping.writerow([umls_id, ident, resource(ident), equivalent_id_map[name].lower()])
        else:
            counter_not_mapped += 1
            codes = '|'.join(n for n in node['code']) if 'code' in node else None
            writer.writerow([umls_id, node['diseaseName'], codes])

    file.close()
    print('number of not-mapped disease_ids:', counter_not_mapped)
    print('number of all disease_ids:', counter_all)



######### MAIN #########
def main():
    print(datetime.datetime.utcnow())

    global home
    global path_of_directory
    global source


    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet disease')

    os.chdir(path_of_directory + 'master_database_change/mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'disease/')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all Diseases from database')
    load_disease_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher and csv file')
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all DisGeNet diseases from database')
    load_all_DisGeNet_disease_and_finish_the_files(csv_mapping)


if __name__ == "__main__":
    # execute only if run as a script
    main()
