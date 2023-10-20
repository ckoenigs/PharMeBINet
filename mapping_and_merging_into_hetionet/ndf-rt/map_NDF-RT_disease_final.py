import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


class Diseasepharmebinet:
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


# dictionary with DO_id as key and class Diseasepharmebinet as value
dict_diseases_pharmebinet = {}

# dictionary with code as key and value is class DiseaseNDF_RT
dict_diseases_NDF_RT = {}

# dictionary with name/synonyms to doid
dict_name_synonym_to_mondo_id = {}

# dictionary umls cui to mondo
dict_umls_to_mondo = {}

# dictionary mesh cui to mondo
dict_mesh_to_mondo = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


'''
prepare the different xrefs dictionaries
'''


def prepare_dictionary_xrefs_to_mondo(xref_cui, identifier, dictionary_xref):
    cui = xref_cui.split(':')[1] if len(xref_cui.split(':')) > 1 else xref_cui
    pharmebinetutils.add_entry_to_dict_to_set(dictionary_xref, cui, identifier)
    return cui


'''
load in all diseases from pharmebinet in a dictionary in a dictionary and  generate dictionary and list with all names and synonyms
'''


def load_pharmebinet_diseases_in():
    query = '''MATCH (n:Disease) RETURN n.identifier,n.name, n.synonyms, n.xrefs, n.umls_cuis, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, xrefs, umls_cuis, resource] = record.values()
        umls_cuis_without_label = []
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_synonym_to_mondo_id, name.lower(), identifier)
        if umls_cuis:
            for umls_cui in umls_cuis:
                if len(umls_cui) > 0:
                    cui = prepare_dictionary_xrefs_to_mondo(umls_cui, identifier, dict_umls_to_mondo)
                    umls_cuis_without_label.append(cui)
        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_synonym_to_mondo_id, synonym, identifier)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('MESH:'):
                    prepare_dictionary_xrefs_to_mondo(xref, identifier, dict_mesh_to_mondo)
        resource = resource if resource is not None else []
        disease = Diseasepharmebinet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_diseases_pharmebinet[identifier] = disease
    print('length of disease in pharmebinet:' + str(len(dict_diseases_pharmebinet)))


# dictionary name/synonym to symptom ids
dict_name_synonym_to_symptom_ids = {}

# dictionary mesh to symptoms
dict_mesh_to_symptom_ids = {}

# dictionary umls to symptoms ids
dict_umls_to_symptom_ids = {}

# dictionary symptom id to symptom infos
dict_symptom_infos = {}

'''
load in all diseases from pharmebinet in a dictionary in a dictionary and  generate dictionary and list with all names and synonyms
'''


def load_pharmebinet_symptom_in():
    query = '''MATCH (n:Symptom) RETURN n.identifier,n.name, n.synonyms, n.xrefs,  n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, xrefs, resource] = record.values()
        umls_cuis_without_label = []
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_synonym_to_symptom_ids, name.lower(), identifier)
        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_synonym_to_symptom_ids, synonym, identifier)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('MESH:'):
                    prepare_dictionary_xrefs_to_mondo(xref, identifier, dict_mesh_to_symptom_ids)
                elif xref.startswith('UMLS:'):
                    cui = prepare_dictionary_xrefs_to_mondo(xref, identifier, dict_umls_to_symptom_ids)
                    umls_cuis_without_label.append(cui)
        resource = resource if resource is not None else []
        disease = Diseasepharmebinet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_symptom_infos[identifier] = disease
    print('length of symptom in pharmebinet:' + str(len(dict_symptom_infos)))


'''
load in all diseases from ndf-rt in a dictionary and get all umls cuis
'''


def load_ndf_rt_diseases_in():
    query = '''MATCH (n:NDFRT_DISEASE_KIND) RETURN n'''
    results = g.run(query)
    i = 0
    for record in results:
        result = record.data()['n']
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


# dictionary with code as key and value is a list of disease ids
dict_mapped = {}
# dictionary with code as key and value is a list of symptom ids
dict_mapped_symptom = {}
# list of codes which are not mapped to disease or symptom
list_code_not_mapped = []

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
mapping of ndf-rt disease to disease and symptom
first mapping is using mesh and umls to map to disease
next the the mesh and umls are mapped to symptoms.
Then the name is mapped to name/synonym of disease.
The last try mapped name to name/synonym of symptoms.
'''


def map_ndf_rt_disease_to_disease_and_symptom():
    for code, diseaseNdfRT in dict_diseases_NDF_RT.items():
        if code == 'C5722':
            print('ok')
        cuis_pharmebinet = diseaseNdfRT.umls_cuis
        mesh_cuis = diseaseNdfRT.mesh_cuis
        umls_mapping = prepare_mapping_list(cuis_pharmebinet, dict_umls_to_mondo)

        name = dict_diseases_NDF_RT[code].name.split(' [')[0]
        label = name.lower()
        label_split = label.split(' exact')[0]

        mesh_mapping = prepare_mapping_list(mesh_cuis, dict_mesh_to_mondo)

        intersection = umls_mapping.intersection(mesh_mapping)

        found_mapping = False

        if len(intersection) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis umls and mesh from ndf-rt and pharmebinet')
            dict_mapped[code] = list(intersection)
            found_mapping = True

        elif len(mesh_mapping) > 0 and len(umls_mapping) > 0:
            if name in dict_name_synonym_to_mondo_id:
                disease_ids = dict_name_synonym_to_mondo_id[name]
                mesh_umls_mappings = umls_mapping.union(mesh_mapping)
                intersection = mesh_umls_mappings.intersection(disease_ids)
                if len(intersection) > 0:
                    dict_diseases_NDF_RT[code].set_how_mapped(
                        'mesh_or_umls_with_name_mapping')
                    dict_mapped[code] = list(intersection)
                    found_mapping = True
                else:
                    print(code)
                    print(mesh_mapping)
                    print(umls_mapping)
                    sys.exit('both map but not to the same')
        elif len(umls_mapping) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis umls from ndf-rt and pharmebinet')
            dict_mapped[code] = list(umls_mapping)
            found_mapping = True
        elif len(mesh_mapping) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map of cuis mesh from ndf-rt and pharmebinet')
            dict_mapped[code] = list(mesh_mapping)
            found_mapping = True

        if found_mapping:
            continue

        if label_split in dict_name_synonym_to_mondo_id:
            dict_diseases_NDF_RT[code].set_how_mapped('direct map with name')
            found_mapping = True
            if not code in dict_mapped:
                dict_mapped[code] = dict_name_synonym_to_mondo_id[label_split]
            else:
                dict_mapped[code].union(dict_name_synonym_to_mondo_id[label_split])
        elif label_split in dict_name_synonym_to_symptom_ids:
            dict_diseases_NDF_RT[code].set_how_mapped('name')
            found_mapping = True
            if not code in dict_mapped_symptom:
                dict_mapped_symptom[code] = dict_name_synonym_to_symptom_ids[label_split]
            else:
                dict_mapped_symptom[code].union(dict_name_synonym_to_symptom_ids[label_split])

        if found_mapping:
            continue

        umls_mapping = prepare_mapping_list(cuis_pharmebinet, dict_umls_to_symptom_ids)

        mesh_mapping = prepare_mapping_list(mesh_cuis, dict_mesh_to_symptom_ids)

        intersection = umls_mapping.intersection(mesh_mapping)
        if len(intersection) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('umls_mesh_to_symptom')
            dict_mapped_symptom[code] = list(intersection)
            found_mapping = True

        elif len(mesh_mapping) > 0 and len(umls_mapping) > 0:
            print(code)
            print(mesh_mapping)
            print(umls_mapping)
            sys.exit('both map but not to the same')
        elif len(umls_mapping) > 0:
            dict_diseases_NDF_RT[code].set_how_mapped('umls_to_symptom')
            dict_mapped_symptom[code] = list(umls_mapping)
            found_mapping = True
        # this mapping is not good!
        # elif len(mesh_mapping) > 0:
        #     dict_diseases_NDF_RT[code].set_how_mapped('mesh_to_symptom')
        #     dict_mapped_symptom[code] = list(mesh_mapping)
        #     found_mapping = True

        if found_mapping:
            continue


        else:
            list_code_not_mapped.append(code)

    print('number of mapped:', len(dict_mapped) + len(dict_mapped_symptom))
    print('number of not mapped:' + str(len(list_code_not_mapped)))


list_of_codes_which_cuis_are_not_disease_or_se = ['C31768', 'C31772', 'C31784']

# dictionary with code as key and synonym cuis as value
dict_code_synonym_cuis = {}

# generate file with code and a list of DO ids and where there are from
multiple_DO_ids = open('ndf_rt_multiple_DO_ids.tsv', 'w')
multiple_DO_ids.write('ndf-rt code \t DO_ids with | as seperator \t where are it from  \t name\n')

'''
this integrate only properties into pharmebinet for the one that are mapped,
because all data from disease ontology are integrated
all Disease which are not mapped with a ndf-rt disease get the propertie no
'''


def integrate_ndf_rt_disease_into_pharmebinet():
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = ''' MATCH (n:NDFRT_DISEASE_KIND{code:line.code}), (d:Disease{identifier:line.disease_id}) Set n.MONDO_IDs=split(line.mondo_ids,'|'), d.resource=split(line.resource,'|'), d.ndf_rt='yes'  Create (d)-[:equal_to_Disease_NDF_RT{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ndf-rt/disease/mapped.tsv',
                                              query)
    cypher_file.write(query)
    query = ''' MATCH (n:NDFRT_DISEASE_KIND{code:line.code}), (d:Symptom{identifier:line.symptom_id}) Set n.Symptom_ids=split(line.mondo_ids,'|'), d.resource=split(line.resource,'|'), d.ndf_rt='yes'  Create (d)-[:equal_to_Symptom_NDF_RT{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ndf-rt/disease/mapped_symptom.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.close()
    file = open('disease/mapped.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    header = ['code', 'disease_id', 'mondo_ids', 'how_mapped', 'resource']
    csv_writer.writerow(header)
    for code, mondo_ids in dict_mapped.items():
        mondo_strings = "|".join(mondo_ids)
        how_mapped = dict_diseases_NDF_RT[code].how_mapped
        for mondo_id in mondo_ids:
            csv_writer.writerow([code, mondo_id, mondo_strings, how_mapped,
                                 pharmebinetutils.resource_add_and_prepare(dict_diseases_pharmebinet[mondo_id].resource,
                                                                           'NDF-RT')])
    file.close()

    file_symptom = open('disease/mapped_symptom.tsv', 'w', encoding='utf-8')
    csv_writer_symptom = csv.writer(file_symptom, delimiter='\t')
    header = ['code', 'symptom_id', 'symptom_ids', 'how_mapped', 'resource']
    csv_writer_symptom.writerow(header)

    for code, symptom_ids in dict_mapped_symptom.items():
        symptom_strings = "|".join(symptom_ids)
        how_mapped = dict_diseases_NDF_RT[code].how_mapped
        for symptom_id in symptom_ids:
            csv_writer_symptom.writerow([code, symptom_id, symptom_strings, how_mapped,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_symptom_infos[symptom_id].resource,
                                             'NDF-RT')])
    file_symptom.close()

    # write file with all not mapped disease
    file_not_mapped = open('disease/not_mapped.tsv', 'w', encoding='utf-8')
    csv_writer_not_mapped = csv.writer(file_not_mapped, delimiter='\t')
    csv_writer_not_mapped.writerow(['code', 'name', 'properties'])
    for code in list_code_not_mapped:
        csv_writer_not_mapped.writerow([code, dict_diseases_NDF_RT[code].name, dict_diseases_NDF_RT[code].umls_cuis,
                                        dict_diseases_NDF_RT[code].properties])
    file_not_mapped.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in diseases from pharmebinet')

    load_pharmebinet_diseases_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in symptom from pharmebinet')

    load_pharmebinet_symptom_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in diseases from ndf-rt')

    load_ndf_rt_diseases_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map round one, check the cuis from disease ontology to cuis in ndf-rt')

    map_ndf_rt_disease_to_disease_and_symptom()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('integrate ndf-rt into pharmebinet')

    integrate_ndf_rt_disease_into_pharmebinet()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
