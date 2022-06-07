import datetime
import os
import sys
import csv
from collections import defaultdict
sys.path.append("../..")
from pharmebinetutils import *



# dictionary disease id to Disease identifier
dict_umls_id_to_identifier = defaultdict(set)

#dictionary from symptom id to resource
dict_symptom_id_to_resource = defaultdict(set)

#dict for alternative_ids
dict_xrefs_to_identifier = defaultdict(set)

# dictionary name to set of ids
dict_name_to_identifier= defaultdict(set)

def check_for_multiple_mapping_and_try_to_reduce_multiple_mapping(name, mapping_ids):
    """
    Try to reduce multiple mapping be also consider name mapping ids intersection
    :param name: string
    :param mapping_ids: set of mapped ids
    :return: set of ids
    """
    if len(mapping_ids)>1 and name in dict_name_to_identifier:
        name_mapped_ids=dict_name_to_identifier[name]
        intersection= name_mapped_ids.intersection(mapping_ids)
        if len(intersection)>0:
            return intersection

    return mapping_ids

def load_symptoms_from_database_and_add_to_dict(g):
    '''
    Load all Symptoms from Graph-DB and add them into a dictionary
    '''
    query = "MATCH (n:Symptom) RETURN n"
    results = g.run(query)

    for node, in results:
        identifier = node['identifier'] #Mesh identifier
        #for mapping with MESH
        dict_symptom_id_to_resource[identifier] = node['resource']

        name= node['name'].lower()
        dict_name_to_identifier[name].add(identifier)

        if 'synonyms' in node:
            for synonym in node['synonyms']:
                dict_name_to_identifier[synonym.lower()].add(identifier)

        if 'xrefs' in node:
            # find index of xrefs "UMLS" entry
            umls_id_idx = [i for i, item in enumerate(node['xrefs']) if item.startswith('UMLS')]
            # save all relevant xrefs (for alternative mapping)
            xrefs = [nr for nr in node['xrefs'] if nr.startswith(('HPO'))] # 'MESH',
            for xref in xrefs:
                dict_xrefs_to_identifier[xref].add(identifier)
        else:
            umls_id_idx = []

        # add alternative HPO-IDs to previous xref-dict if exist
        if 'alternative_ids' in node:
            for hp_id in node['alternative_ids']:
                if hp_id.startswith('HP'):
                    name = "HPO:"+hp_id
                    dict_xrefs_to_identifier[name].add(identifier)

        # for mapping with UMLS
        if umls_id_idx:
            for i in umls_id_idx:
                _, umls_id = node['xrefs'][i].split(':')
                # put umls_id as identifier if 'UMLS' exists in xrefs
                dict_umls_id_to_identifier[umls_id].add(identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    global csv_mapping
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'DisGeNet_disease_to_symptom'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['DisGeNet_diseaseId', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}{file_name}.tsv" As line FIELDTERMINATOR "\\t" \
        Match (n:disease_DisGeNet{{diseaseId:line.DisGeNet_diseaseId}}), (v:Symptom{{identifier:line.identifier}}) Set v.disgenet="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_DisGeNet_disease{{mapped_with:line.mapping_method}}]->(n);\n'

    return  query



def load_all_unmapped_DisGeNet_disease_and_finish_the_files(name,umls_id,xrefs):
    """
    Load all unmapped DisGeNet_diseases sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """
    equivalent_id_map = {"MSH": "MESH", "HPO":"HPO"}

    alternative_ids = [x for x in xrefs if x.startswith(( 'HPO'))] if not xrefs is None else [] # 'MSH',

    # mapping via UMLS
    if umls_id in dict_umls_id_to_identifier:
        # Mesh Identifier from Symptom
        identifiers = dict_umls_id_to_identifier[umls_id]
        reduced_identifier= check_for_multiple_mapping_and_try_to_reduce_multiple_mapping(name,identifiers)
        for identifier in reduced_identifier:
            csv_mapping.writerow([umls_id, identifier, resource_add_and_prepare(dict_symptom_id_to_resource[identifier],"DisGeNet"), 'umls'])
        return  True

    # name mapping
    if name:
        if name in dict_name_to_identifier:
            for identifier in dict_name_to_identifier[name]:
                csv_mapping.writerow([umls_id, identifier, resource_add_and_prepare(dict_symptom_id_to_resource[identifier],"DisGeNet"), 'name'])
            return True

    # mapping via xrefs
    if alternative_ids:
        found_mapping=False
        # mapping via xrefs
        for item in alternative_ids:
            name, id_num = item.split(':', 1)
            # generate equivalent ID (which might be a possible entry in Symptom-dictionnary [dict_xrefs_to_id])
            # if name in equivalent_id_map.keys() else name
            equ_id = equivalent_id_map[name] + ":" + id_num
            if equ_id in dict_xrefs_to_identifier:
                found_mapping=True
                identifiers = dict_xrefs_to_identifier[equ_id]
                reduced_identifier = check_for_multiple_mapping_and_try_to_reduce_multiple_mapping(name, identifiers)
                for ident in reduced_identifier:  # in case of several values for one id
                    csv_mapping.writerow([umls_id, ident, resource_add_and_prepare(dict_symptom_id_to_resource[ident],"DisGeNet"), equivalent_id_map[name].lower()])
        return found_mapping

    else:
        return False


