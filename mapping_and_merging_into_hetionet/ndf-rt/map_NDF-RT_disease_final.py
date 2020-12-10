# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:15:37 2017

@author: ckoenigs
"""

import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases


class DiseaseHetionet:
    """
    identifier: string (doid)
    umls_cuis: list
    xrefs: list (external identifier like mesh or omim)
    synonyms: list (synonym names) 
    resource: list
    """

    def __init__(self, identifier, synonyms, umls_cuis, xrefs, resource):
        self.identifier = identifier
        self.umls_cuis = umls_cuis
        self.xrefs = xrefs
        self.synonyms = synonyms
        self.resource = resource


class DiseaseNDF_RT:
    """
    code: string 
    name: string
    properties: list (like identifier or synonyms
    umls_cuis: list
    diseaseOntology_id: strin
    """

    def __init__(self, code, name, properties, umls_cuis, mesh_cuis, rxnorm_cuis):
        self.code = code
        self.name = name
        self.properties = properties
        self.umls_cuis = umls_cuis
        self.mesh_cuis = mesh_cuis
        self.rxnorm_cuis = rxnorm_cuis

    def set_diseaseOntology_id(self, diseaseOntology_id):
        self.diseaseOntology_id = diseaseOntology_id

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with DO_id as key and class DiseaseHetionet as value
dict_diseases_hetionet = {}

# dictionary with code as key and value is class DiseaseNDF_RT
dict_diseases_NDF_RT = {}

# dictionary with name/synonyms to doid
dict_name_synonym_to_mondo_id = {}

# list with all names and synonyms of disease ontology
list_name_synonyms = []

# dictionary umls cui to mondo
dict_umls_to_mondo = {}

# dictionary mesh cui to mondo
dict_mesh_to_mondo = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


'''
prepare the different xrefs dictionaries
'''


def prepare_dictionary_xrefs_to_mondo(xref_cui, identifier, dictionary_xref):
    cui = xref_cui.split(':')[1] if len(xref_cui.split(':')) > 1 else xref_cui
    if cui in dictionary_xref:
        dictionary_xref[cui].add(identifier)
    else:
        dictionary_xref[cui] = {identifier}
    return cui


'''
load in all diseases from hetionet in a dictionary in a dictionary and  generate dictionary and list with all names and synonyms
'''


def load_hetionet_diseases_in():
    query = '''MATCH (n:Disease) RETURN n.identifier,n.name, n.synonyms, n.xrefs, n.umls_cuis, n.resource'''
    results = g.run(query)

    for identifier, name, synonyms, xrefs, umls_cuis, resource, in results:
        umls_cuis_without_label = []
        dict_name_synonym_to_mondo_id[name.lower()] = identifier
        list_name_synonyms.append(name)
        if umls_cuis:
            for umls_cui in umls_cuis:
                if len(umls_cui) > 0:
                    cui = prepare_dictionary_xrefs_to_mondo(umls_cui, identifier, dict_umls_to_mondo)
                    umls_cuis_without_label.append(cui)
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.split(':')[0].lower()
                dict_name_synonym_to_mondo_id[synonym] = identifier
                list_name_synonyms.append(synonym)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('MESH:'):
                    prepare_dictionary_xrefs_to_mondo(xref, identifier, dict_mesh_to_mondo)
        resource = resource if resource is not None else []
        disease = DiseaseHetionet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_diseases_hetionet[identifier] = disease
    print('length of disease in hetionet:' + str(len(dict_diseases_hetionet)))


'''
load in all diseases from ndf-rt in a dictionary and get all umls cuis
'''


def load_ndf_rt_diseases_in():
    query = '''MATCH (n:NDF_RT_DISEASE_KIND) RETURN n'''
    results = g.run(query)
    i = 0
    for result, in results:
        code = result['code']
        properties = result['properties']
        name = result['name'].lower()
        umls_cuis = []
        mesh_cuis = []
        rxnorm_cuis = []
        for prop in properties:
            if prop[0:8] == 'UMLS_CUI':
                cui = prop
                umls_cuis.append(cui.split(':')[1])
            elif prop.startswith('MeSH_DUI:'):
                mesh_cuis.append(prop.split(':')[1])
            elif prop.startswith('RxNorm_CUI'):
                rxnorm_cuis.append(prop.split(':')[1])

        disease = DiseaseNDF_RT(code, name, properties, umls_cuis, mesh_cuis, rxnorm_cuis)
        dict_diseases_NDF_RT[code] = disease
        i += 1
    print('length of disease in ndf-rt:' + str(len(dict_diseases_NDF_RT)))


# dictionary with code as key and value is a list of disease ontology ids
dict_mapped = {}
# list of codes which are not mapped to disease ontology ids
list_code_not_mapped = []

# files for the how_mapped
map_direct_cui_cui = open('disease/ndf_rt_disease_cui_cui_map.tsv', 'w')
csv_direct_cui = csv.writer(map_direct_cui_cui, delimiter='\t')
csv_direct_cui.writerow(['code in NDF-RT', 'name in NDF-RT', 'MONDO ids with | as seperator'])

map_direct_name = open('disease/ndf_rt_disease_name_name_synonym_map.tsv', 'w')
csv_direct_name_synonyms = csv.writer(map_direct_name, delimiter='\t')
csv_direct_name_synonyms.writerow(['code in NDF-RT', 'name in NDF-RT', 'MONDO ids with | as seperator'])

map_synonym_cuis = open('disease/ndf_rt_disease_synonyms_map.tsv', 'w')
csv_direct_synonyms = csv.writer(map_synonym_cuis, delimiter='\t')
csv_direct_synonyms.writerow(['code in NDF-RT', 'name in NDF-RT', 'MONDO ids with | as seperator'])

'''
prepare mapping list
'''


def prepare_mapping_list(cuis, dictionary):
    mapping = set()
    for cui in cuis:
        if cui in dictionary:
            mapping = mapping.union(dictionary[cui])
    return mapping


'''
first round of map:
go through all diseases from hetionet and check if the umls cuis  are the same to the 
ndf-rt diseases
'''


def map_with_cuis_go_through_all():
    for code, diseaseNdfRT in dict_diseases_NDF_RT.items():
        if code == 'C5722':
            print('ok')
        cuis_hetionet = diseaseNdfRT.umls_cuis
        mesh_cuis = diseaseNdfRT.mesh_cuis
        umls_mapping = prepare_mapping_list(cuis_hetionet, dict_umls_to_mondo)

        mesh_mapping = prepare_mapping_list(mesh_cuis, dict_mesh_to_mondo)

        intersection = umls_mapping.intersection(mesh_mapping)

        if len(intersection) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis umls and mesh from ndf-rt and hetionet')
            dict_mapped[code] = list(intersection)

        elif len(mesh_mapping) > 0 and len(umls_mapping) > 0:
            print(code)
            print(mesh_mapping)
            print(umls_mapping)
        elif len(umls_mapping) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis umls from ndf-rt and hetionet')
            dict_mapped[code] = list(umls_mapping)
        elif len(mesh_mapping) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis mesh from ndf-rt and hetionet')
            dict_mapped[code] = list(mesh_mapping)
        else:
            list_code_not_mapped.append(code)

    print('number of mapped:' + str(len(dict_mapped)))
    for code in dict_diseases_NDF_RT.keys():
        if code in dict_mapped:
            string_do_ids = '|'.join(dict_mapped[code])
            csv_direct_cui.writerow([code, dict_diseases_NDF_RT[code].name, string_do_ids])
    print('number of not mapped:' + str(len(list_code_not_mapped)))


list_of_codes_which_cuis_are_not_disease_or_se = ['C31768', 'C31772', 'C31784']
'''
map the name of ndf-rt disease to name or synonym of disease ontology
'''


def map_with_name():
    delete_map_code = []
    for code in list_code_not_mapped:
        name = dict_diseases_NDF_RT[code].name.split(' [')[0]
        label = name.lower()
        label_split = label.split(' exact')[0]
        if label_split in dict_name_synonym_to_mondo_id:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map with name')
            delete_map_code.append(list_code_not_mapped.index(code))
            if not code in dict_mapped:
                dict_mapped[code] = set([dict_name_synonym_to_mondo_id[label_split]])
            else:
                dict_mapped[code].union(dict_name_synonym_to_mondo_id[label_split])

    delete_map_code = list(set(delete_map_code))
    delete_map_code.sort()
    delete_map_code = list(reversed(delete_map_code))
    for index in delete_map_code:
        code = list_code_not_mapped.pop(index)
        string_do_ids = '|'.join(dict_mapped[code])
        csv_direct_name_synonyms.writerow([code, dict_diseases_NDF_RT[code].name, string_do_ids])

    print('number of mapped:' + str(len(dict_mapped)))
    print('number of not mapped:' + str(len(list_code_not_mapped)))


# dictionary with code as key and synonym cuis as value
dict_code_synonym_cuis = {}

# generate file with code and a list of DO ids and where there are from
multiple_DO_ids = open('ndf_rt_multiple_DO_ids.tsv', 'w')
multiple_DO_ids.write('ndf-rt code \t DO_ids with | as seperator \t where are it from  \t name\n')

'''
this integrate only properties into hetionet for the one that are mapped,
because all data from disease ontology are integrated
all Disease which are not mapped with a ndf-rt disease get the propertie no
'''


def integrate_ndf_rt_disease_into_hetionet():
    cypher_file = open('disease/cypher.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ndf-rt/disease/mapped.csv" As line MATCH (n:NDF_RT_DISEASE_KIND{code:line.code}), (d:Disease{identifier:line.disease_id}) Set n.MONDO_IDs=split(line.mondo_ids,'|'), n.how_mapped=line.how_mapped, d.resource=split(line.resource,'|'), d.ndf_rt='yes'  Create (d)-[:equal_to_Disease_NDF_RT]->(n);\n'''
    cypher_file.write(query)
    cypher_file.close()
    file = open('disease/mapped.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file)
    header = ['code', 'disease_id', 'mondo_ids', 'how_mapped', 'resource']
    csv_writer.writerow(header)
    for code, mondo_ids in dict_mapped.items():
        mondo_strings = "|".join(mondo_ids)
        how_mapped = dict_diseases_NDF_RT[code].how_mapped
        if len(mondo_ids) > 1:
            string_mondo_ids = "|".join(mondo_ids)
            # multiple_mondo_ids.write(
            #     code + '\t' + string_mondo_ids + '\t' + how_mapped + '\t' + dict_diseases_NDF_RT[code].name + '\n')
        for mondo_id in mondo_ids:
            resource = dict_diseases_hetionet[mondo_id].resource
            resource.append('NDF-RT')
            resource = list(set(resource))
            resource = "|".join(resource)
            csv_writer.writerow([code, mondo_id, mondo_strings, how_mapped, resource])

    # write file with all not mapped disease
    file_not_mapped = open('disease/not_mapped.csv', 'w', encoding='utf-8')
    csv_writer_not_mapped = csv.writer(file_not_mapped)
    csv_writer_not_mapped.writerow(['code', 'name', 'properties'])
    for code in list_code_not_mapped:
        csv_writer_not_mapped.writerow([code, dict_diseases_NDF_RT[code].name, dict_diseases_NDF_RT[code].umls_cuis,
                                        dict_diseases_NDF_RT[code].properties])

    # add query to update disease nodes with do='no'
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = ''':begin\n MATCH (n:Disease) Where Not Exists(n.ndf_rt) Set n.ndf_rt="no";\n :commit\n '''
    cypher_general.write(query)
    cypher_general.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in diseases from hetionet')

    load_hetionet_diseases_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in diseases from ndf-rt')

    load_ndf_rt_diseases_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('map round one, check the cuis from disease ontology to cuis in ndf-rt')

    map_with_cuis_go_through_all()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('map with name ndf-rt to name or synonym od DO')

    map_with_name()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('integrate ndf-rt into hetionet')

    integrate_ndf_rt_disease_into_hetionet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
