import datetime
import sys, csv
import urllib.request, urllib.error, urllib.parse
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

REST_URL = "http://data.bioontology.org"


# http://bioportal.bioontology.org/ontologies/MEDDRA?p=classes&conceptid=10059299


class SideEffect:
    """
    license: string
    identifier: string (umls cui)
    name: string
    source: string
    url: string
    meddraType: string
    synonyms: [string]
    umls_label: string
    resource: list of strings
    """

    def __init__(self, licenses, identifier, name, source, url, meddraType, synonyms, umls_label, resource):
        self.license = licenses
        self.identifier = identifier
        self.name = name
        self.source = source
        self.url = url
        self.meddraType = meddraType
        self.synonyms = synonyms
        self.umls_label = umls_label
        self.resource = resource if resource is not None else []


class SideEffect_Aeolus():
    """
    snomed_outcome_concept_id: string (snomed ct ID)
    vocabulary_id: string (defined the type of the concept_code wich is MedDRA)
    name: string
    outcome_concept_id: string (OHDSI ID)
    concept_code: string (MedDRA ID)
    cuis: string (umls cuis)
    """

    def __init__(self, snomed_outcome_concept_id, vocabulary_id, name, outcome_concept_id, concept_code):
        self.snomed_outcome_concept_id = snomed_outcome_concept_id
        self.vocabulary_id = vocabulary_id
        self.name = name
        self.outcome_concept_id = outcome_concept_id
        self.concept_code = concept_code
        self.cuis = None
        self.mapping = ''

    def set_mapping(self, mapping):
        self.mapping = mapping

    def set_cuis_id(self, cuis):
        self.cuis = cuis


# dictionary with all side effects from pharmebinet with umls cui as key and as value a class SideEffect
dict_all_side_effect = {}



def create_connection_with_neo4j():
    """
    create connection to neo4j and mysql
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def load_api_key():
    """
    Load api key for BioPortal
    :return:
    """
    global API_KEY
    file = open('api_key.txt', 'r', encoding='utf-8')
    API_KEY = next(file).strip(" \n")



def cache_api():
    """
    Create cache file or open and load mapping results
    :return:
    """
    # header of cache file
    header = ['meddra_id', 'umls_cuis']
    global csv_writer
    try:
        cache_file = open('cache_api_results.tsv', 'r', encoding='utf-8')
        csv_reader = csv.DictReader(cache_file, delimiter='\t')
        for row in csv_reader:
            dict_aeolus_SE_with_CUIs[row['meddra_id']] = list(set(row['umls_cuis'].split('|')))
        cache_file.close()
        cache_file = open('cache_api_results.tsv', 'a', encoding='utf-8')
        csv_writer = csv.writer(cache_file, delimiter='\t')

    except:
        cache_file = open('cache_api_results.tsv', 'w', encoding='utf-8')
        csv_writer = csv.writer(cache_file, delimiter='\t')
        csv_writer.writerow(header)



def get_json(url):
    """
    get from api results from url
    :param url:
    :return:
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())


# dictionary side effect name to se ids
dict_se_name_to_ids = {}


def add_entries_into_dict(key, value, dictionary):
    """
    add entry into dictionary
    :param key: string
    :param value: string
    :param dictionary: dictionary
    :return:
    """
    if not key in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def load_side_effects_from_pharmebinet_in_dict():
    """
    load in all side effects from pharmebinet into a dictionary
    has properties:
        license
        identifier
        name
        source
        url
        meddraType
        synonyms
        umls_label
        resource
    :return:
    """
    query = '''MATCH (n:SideEffect) RETURN n '''
    results = g.run(query)
    for record in results:
        result = record.data()['n']
        synonyms = result['synonyms'] if 'synonyms' in result else []
        umls_label = result['umls_label'] if 'umls_label' in result else ''
        meddraType = result['meddraType'] if 'meddraType' in result else ''
        license = result['license'] if 'license' in result else ''
        sideEffect = SideEffect(license, result['identifier'], result['name'], result['source'],
                                result['url'], meddraType, synonyms, umls_label,
                                result['resource'])
        dict_all_side_effect[result['identifier']] = sideEffect
        add_entries_into_dict(result['name'].lower(), result['identifier'], dict_se_name_to_ids)
        if 'synonyms' in result:
            for synonym in result['synonyms']:
                add_entries_into_dict(synonym.lower(), result['identifier'], dict_se_name_to_ids)

    print('size of side effects before the aeolus is add:' + str(len(dict_all_side_effect)))


# dictionary with all aeolus side effects outcome_concept_id (OHDSI ID) as key and value is the class SideEffect_Aeolus
dict_side_effects_aeolus = {}

# list of list with all meddra cuis in groups of 100
list_of_list_of_meddra_ids = []

# number of group size
number_of_group_size = 200

# set of mapped meddra ids
set_concept_ids_mapped = set()


def load_side_effects_aeolus_in_dictionary():
    """
    load all aeolus side effects in a dictionary
    has properties:
        snomed_outcome_concept_id
        vocabulary_id: defined the type of the concept_code
        name
        outcome_concept_id: OHDSI ID
        concept_code: MedDRA ID
    :return:
    """
    # {concept_code:'10000031'}
    query = '''MATCH (n:Aeolus_Outcome) RETURN n'''
    results = g.run(query)
    # list of_meddra ids
    list_of_ids = []
    # counter
    counter = 0

    for record in results:
        result = record.data()['n']
        sideEffect = SideEffect_Aeolus(result['snomed_outcome_concept_id'], result['vocabulary_id'], result['name'],
                                       result['outcome_concept_id'], result['concept_code'])
        dict_side_effects_aeolus[result['concept_code']] = sideEffect
        # add all meddra ids where no cui is known in list of a given size
        # the list should be not to big because it will be asked with api
        if result['concept_code'] not in dict_aeolus_SE_with_CUIs:
            list_of_ids.append(result['concept_code'])
            counter += 1
            if counter % number_of_group_size == 0:
                list_of_list_of_meddra_ids.append(list_of_ids)
                list_of_ids = []

        if result['name'].lower() in dict_se_name_to_ids:
            list_map_to_pharmebinet.append(result['concept_code'])
            set_concept_ids_mapped.add(result['concept_code'])
            cuis = dict_se_name_to_ids[result['name'].lower()]
            for cui in cuis:
                # check if the mapping appears multiple time
                # also set the mapped cui into the class aeolus
                if cui not in dict_mapped_cuis_pharmebinet:
                    dict_mapped_cuis_pharmebinet[cui] = []
                dict_mapped_cuis_pharmebinet[cui].append(result['concept_code'])
                add_cui_information_to_class(result['concept_code'], cui, 'name_mapped')

    list_of_list_of_meddra_ids.append(list_of_ids)

    print('Size of Aoelus side effects:' + str(len(dict_side_effects_aeolus)))
    print('number of mapped:', len(dict_mapped_cuis_pharmebinet))


# dictionary disease name to identifier
dict_disease_name_to_id = {}

# dictionary disease umls cui to identifier
dict_disease_cui_to_id = {}

# dictionary meddra to mondo
dict_meddra_to_mondo = {}

# ditionary mondo to xrefs and resource
dict_mondo_to_xrefs_and_resource = {}


def load_disease_infos():
    """
    Load all disease with umls, identifier and name (,synonyms?)
    :return:
    """
    query = '''Match (n:Disease) Return n.identifier, n.name, n.umls_cuis, n.xrefs, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, umls_cuis, xrefs, resource] = record.values()
        dict_mondo_to_xrefs_and_resource[identifier] = [xrefs, resource]
        if name:
            name = name.lower()
            if name in dict_disease_name_to_id:
                print('name is double')
                dict_disease_name_to_id[name].append(identifier)
                print(dict_disease_name_to_id[name])

            else:
                dict_disease_name_to_id[name] = [identifier]
        if umls_cuis:
            for umls_cui in umls_cuis:
                cui = umls_cui.split(':')[1]
                if cui in dict_disease_cui_to_id:
                    dict_disease_cui_to_id[cui].append(identifier)
                else:
                    dict_disease_cui_to_id[cui] = [identifier]
        if xrefs:
            for xref in xrefs:
                if xref.startswith('MedDRA'):
                    meddra_id = xref.split(':')[1]
                    if meddra_id in dict_meddra_to_mondo:
                        dict_meddra_to_mondo[meddra_id].add(identifier)
                    else:
                        dict_meddra_to_mondo[meddra_id] = set([identifier])


# dictionary with for every key outcome_concept a list of umls cuis as value
dict_aeolus_SE_with_CUIs = {}

# generate file with meddra and a list of umls cuis and where there are from
multiple_cuis = open('output/aeolus_multiple_cuis.tsv', 'w')
csv_multiple_cuis = csv.writer(multiple_cuis, delimiter='\t')
csv_multiple_cuis.writerow(['MedDRA id', 'cuis with | as seperator ', 'where are it from'])

# list of concept codes which do not have a cui
list_aeolus_outcome_without_cui = []


def search_with_api_bioportal():
    """
    search for cui with api from bioportal
    :return:
    """
    global csv_writer
    # counter for not equal names
    counter_for_not_equal_names = 0

    # counter for meddra ids which has no cui
    counter_meddra_id_without_cui = 0

    # search for cui id in bioportal
    for list_ids in list_of_list_of_meddra_ids:
        if len(list_ids) == 0:
            continue
        string_ids = ' '.join(list_ids)
        part = "/search?q=" + urllib.parse.quote(string_ids) + "&include=cui,prefLabel&pagesize=250&ontology=MEDDRA"
        url = REST_URL + part
        results_all = get_json(url)
        if results_all['totalCount'] > 250:
            sys.exit('more results thant it can show')
        results = results_all['collection']

        dict_all_inside = {}
        # check if this api got an result
        if results:
            for result in results:
                # print(results)
                all_infos = result['@id'].split('/')
                meddra_id = all_infos[-1]
                if meddra_id == '10052551':
                    print('test')
                # filter out all results which are not from meddra
                if all_infos[-2] != 'MEDDRA':
                    continue

                # check if the result has a cui
                if 'cui' in result:
                    cuis = result['cui']
                else:
                    print('no cui')
                    print(meddra_id)
                    continue
                pref_name = result['prefLabel']

                # check if the id is really in this list
                if not meddra_id in list_ids:
                    print('ohje')
                    print(meddra_id)
                    print(url)
                    print(list_ids)
                    print(result)
                    print('What did happend')
                    continue

                # if it contains more than one cui write it into an extra file
                if len(list(set(cuis))) > 1:
                    cuis_string = "|".join(list(set(cuis)))
                    csv_multiple_cuis.writerow([meddra_id, cuis_string, 'from bioportal'])
                dict_all_inside[meddra_id] = cuis
                sideEffect_name = dict_side_effects_aeolus[meddra_id].name
                dict_aeolus_SE_with_CUIs[meddra_id] = list(set(cuis))
                csv_writer.writerow([meddra_id, '|'.join(cuis)])
                # check if names are equal
                if pref_name != sideEffect_name:
                    counter_for_not_equal_names += 1

            # check if some do not have a cui and if so add the to the list without cui
            if len(list_ids) != len(dict_all_inside):
                set_list = set(list_ids)
                set_keys = set(dict_all_inside.keys())
                not_mapped_list = list(set_list.difference(set_keys))
                counter_meddra_id_without_cui += len(not_mapped_list)
                list_aeolus_outcome_without_cui.extend(not_mapped_list)
        else:
            print('not in bioportal')
            print(list_ids)
            list_aeolus_outcome_without_cui.extend(list_ids)

    print('Size of Aoelus side effects:' + str(len(dict_side_effects_aeolus)))
    print('number of not equal names:' + str(counter_for_not_equal_names))
    print('number of not mapped meddra ids:' + str(counter_meddra_id_without_cui))


# list with all outcome_concept from aeolus that did not map direkt
list_not_mapped_to_pharmebinet = []

# list with all mapped outcome_concept
list_map_to_pharmebinet = []

# list with all mapped cuis:
dict_mapped_cuis_pharmebinet = {}


def add_cui_information_to_class(key, cui, mapped):
    """
    add cui information into aeolus se class
    :param key:
    :param cui:
    :param mapped:
    :return:
    """
    if key not in dict_side_effects_aeolus:
        return
    if dict_side_effects_aeolus[key].cuis is None:
        dict_side_effects_aeolus[key].set_cuis_id([cui])
        dict_side_effects_aeolus[key].set_mapping(mapped)
    else:
        dict_side_effects_aeolus[key].cuis.append(cui)



def map_first_round():
    """
    map direct to pharmebinet and remember which did not map in list
    :return:
    """
    for key, cuis in dict_aeolus_SE_with_CUIs.items():
        has_one = False
        if key in set_concept_ids_mapped:
            continue
        for cui in cuis:
            if cui in dict_all_side_effect:

                list_map_to_pharmebinet.append(key)

                # check if the mapping appears multiple time
                # also set the mapped cui into the class aeolus
                if cui in dict_mapped_cuis_pharmebinet:

                    dict_mapped_cuis_pharmebinet[cui].append(key)
                    add_cui_information_to_class(key, cui, 'api_umls_cui')
                else:
                    dict_mapped_cuis_pharmebinet[cui] = [key]

                    add_cui_information_to_class(key, cui, 'api_umls_cui')

                has_one = True
        # remember not mapped aeolus se
        if has_one == False:
            list_not_mapped_to_pharmebinet.append(key)

    print('length of list which are mapped to pharmebinet:' + str(len(list_map_to_pharmebinet)))
    print('lenth of list which has a cui but are not mapped to pharmebinet:' + str(len(list_not_mapped_to_pharmebinet)))
    print('the number of nodes to which they are mapped:' + str(len(dict_mapped_cuis_pharmebinet)))


# dictionary mapped aeolus outcomet to disease ids
dict_outcome_to_disease = {}

# new nodes  dictionary from umls cui to aeolus outcome
dict_new_node_cui_to_concept = {}


def generate_tsv_file(list_of_delet_index, list_not_mapped, concept_code, diseases, mapping_method, csv_writer):
    """
    get the mapped thins and add them to the dictionary and also write all mappings into the tsv file
    :param list_of_delet_index:
    :param list_not_mapped:
    :param concept_code:
    :param diseases:
    :param mapping_method:
    :param csv_writer:
    :return:
    """
    list_of_delet_index.append(list_not_mapped.index(concept_code))
    dict_outcome_to_disease[concept_code] = list(diseases)
    for disease_id in diseases:
        resource_disease = dict_mondo_to_xrefs_and_resource[disease_id][1] if \
            dict_mondo_to_xrefs_and_resource[disease_id][1] is not None else []

        xref_disease = dict_mondo_to_xrefs_and_resource[disease_id][0] if \
            dict_mondo_to_xrefs_and_resource[disease_id][0] is not None else []
        xref_disease.append("MedDRA:" + concept_code)
        xref_disease = go_through_xrefs_and_change_if_needed_source_name(xref_disease, 'disease')
        xref_string = '|'.join(xref_disease)

        csv_writer.writerow(
            [concept_code, disease_id, mapping_method,
             pharmebinetutils.resource_add_and_prepare(resource_disease, "AEOLUS"), xref_string])


def mapping_to_disease():
    """
    Try to map the not mapped to disease
    :return:
    """
    # open file for mapping with disease
    file = open('output/se_disease_mapping.tsv', 'w')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['aSE', 'disease_id', 'mapping_method', 'resource', 'xrefs'])

    # open file for not mapping with anything
    file_not_mapped = open('output/se_not_mapping.tsv', 'w')
    csv_writer_not_mapped = csv.writer(file_not_mapped, delimiter='\t')
    csv_writer_not_mapped.writerow(['aSE', 'name'])

    # list of delete indeces
    list_of_delete_index_with_cui = []
    list_of_delete_index_without_cui = []

    counter_of_mapping_tries = 0
    counter_of_not_mapped = 0
    # fist outcome with cui but did not mapped
    for concept_code in list_not_mapped_to_pharmebinet:
        counter_of_mapping_tries += 1
        if concept_code in dict_meddra_to_mondo:
            generate_tsv_file(list_of_delete_index_with_cui, list_not_mapped_to_pharmebinet, concept_code,
                              dict_meddra_to_mondo[concept_code], 'meddra mapping',
                              csv_writer)

        else:
            if concept_code == '10062075':
                print('test')
            cuis = dict_aeolus_SE_with_CUIs[concept_code]
            if concept_code not in dict_side_effects_aeolus:
                continue
            name = dict_side_effects_aeolus[concept_code].name.lower()
            mapped_cuis_disease = set()
            for cui in cuis:
                if cui in dict_disease_cui_to_id:
                    mapped_cuis_disease = mapped_cuis_disease.union(dict_disease_cui_to_id[cui])

            mapped_name_disease = set()
            if name in dict_disease_name_to_id:
                mapped_name_disease = set(dict_disease_name_to_id[name])

            find_intersection = mapped_name_disease.intersection(mapped_cuis_disease)
            if len(find_intersection) > 0:
                generate_tsv_file(list_of_delete_index_with_cui, list_not_mapped_to_pharmebinet, concept_code,
                                  find_intersection, 'intersection name and cui mapping',
                                  csv_writer)
                if len(find_intersection) > 1:
                    print('intersection is greater than one')
            elif len(mapped_cuis_disease) > 0 and len(mapped_name_disease) == 0:
                generate_tsv_file(list_of_delete_index_with_cui, list_not_mapped_to_pharmebinet, concept_code,
                                  mapped_cuis_disease, 'cui mapping',
                                  csv_writer)
            elif len(mapped_cuis_disease) == 0 and len(mapped_name_disease) > 0:
                generate_tsv_file(list_of_delete_index_with_cui, list_not_mapped_to_pharmebinet, concept_code,
                                  mapped_name_disease, 'name mapping',
                                  csv_writer)

            elif len(mapped_cuis_disease) > 0 and len(mapped_name_disease) > 0:
                # take the name mapping because this is better
                generate_tsv_file(list_of_delete_index_with_cui, list_not_mapped_to_pharmebinet, concept_code,
                                  mapped_name_disease, 'name mapping, but both did mapped',
                                  csv_writer)
                print(concept_code)
                print(mapped_cuis_disease)
                print(mapped_name_disease)
                print('mapped with name and cui but no intersection')
            else:
                # print('no mapping to disease possible')
                counter_of_not_mapped += 1
                for cui in cuis:
                    if cui in dict_new_node_cui_to_concept:
                        dict_new_node_cui_to_concept[cui].append(concept_code)
                    else:
                        dict_new_node_cui_to_concept[cui] = [concept_code]

    list_of_delete_index_with_cui = sorted(list_of_delete_index_with_cui, reverse=True)
    for index in list_of_delete_index_with_cui:
        list_not_mapped_to_pharmebinet.pop(index)

    print('number of mapping tries:' + str(counter_of_mapping_tries))
    print('number of not mapped:' + str(counter_of_not_mapped))

    # try mapping of the outcomes without umls cui with name mapping
    for concept_code in list_aeolus_outcome_without_cui:
        counter_of_mapping_tries += 1
        name = dict_side_effects_aeolus[concept_code].name.lower()
        if concept_code in dict_meddra_to_mondo:
            generate_tsv_file(list_of_delete_index_without_cui, list_aeolus_outcome_without_cui, concept_code,
                              dict_meddra_to_mondo[concept_code], 'meddra mapping',
                              csv_writer)

        if name in dict_disease_name_to_id:
            mapped_name_disease = dict_disease_name_to_id[name]
            generate_tsv_file(list_of_delete_index_without_cui, list_aeolus_outcome_without_cui, concept_code,
                              mapped_name_disease, 'meddra_mapping_name',
                              csv_writer)

            if len(mapped_name_disease) > 1:
                print('multiple mapping with name')
                print(concept_code)
                print(name)
                print(mapped_name_disease)
        else:
            # print('no mapping is possible')
            counter_of_not_mapped += 1
            csv_writer_not_mapped.writerow([concept_code, dict_side_effects_aeolus[concept_code].name])

    print('number of mapping tries:' + str(counter_of_mapping_tries))
    print('number of not mapped:' + str(counter_of_not_mapped))



def integrate_aeolus_into_pharmebinet():
    """
    integrate aeolus in hetiont, by map generate a edge from pharmebinet to the mapped aeolus node
    if no pharmebinet node is found, then generate a new node for side effects
    :return:
    """
    # file for already existing se
    file_existing = open('output/se_existing.tsv', 'w', encoding='utf-8')
    csv_existing = csv.writer(file_existing, delimiter='\t')
    csv_existing.writerow(['aSE', 'SE', 'cuis', 'resources', 'mapping_method'])

    # query for mapping
    query_start = ''' Match (a:Aeolus_Outcome{concept_code:line.aSE})'''

    cypher_file = open('output/cypher.cypher', 'w')

    # query for the update nodes and relationship
    query='Match (n:SideEffect{identifier:line.SE}) Where n.xrefs is NULL Set n.xrefs=[]'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/aeolus/output/se_existing.tsv',
                                                     query)
    cypher_file.write(query)
    query_update = query_start + ' , (n:SideEffect{identifier:line.SE}) Set a.cuis=split(line.cuis,"|"), n.resource=split(line.resources,"|") , n.aeolus="yes", n.xrefs=n.xrefs+("MedDRA:"+line.aSE) Create (n)-[:equal_to_Aeolus_SE{mapping_method:line.mapping_method}]->(a)'
    query_update = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/aeolus/output/se_existing.tsv',
                                                     query_update)
    cypher_file.write(query_update)

    # query for mapping disease
    query_update = query_start + ''' , (n:Disease{identifier:line.disease_id}) Set  n.resource=split(line.resource,"|") , n.aeolus="yes", n.xrefs=split(line.xrefs,"|") Create (n)-[:equal_to_Aeolus_SE{mapping_method:line.mapping_method}]->(a)'''
    query_update = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/aeolus/output/se_disease_mapping.tsv',
                                                     query_update)
    cypher_file.write(query_update)

    # update and generate connection between mapped aeolus outcome and pharmebinet side effect
    counter_mapped = 0
    for outcome_concept in list_map_to_pharmebinet:
        if outcome_concept not in dict_side_effects_aeolus:
            continue
        cuis = dict_side_effects_aeolus[outcome_concept].cuis
        cuis_string = '|'.join(cuis)
        counter_mapped += 1
        for cui in cuis:
            resource = dict_all_side_effect[cui].resource
            resource.append("AEOLUS")
            resource = list(set(resource))
            resources = '|'.join(resource)

            csv_existing.writerow([outcome_concept, cui, cuis_string, resources, dict_side_effects_aeolus[outcome_concept].mapping])
    print('number of mapped:', counter_mapped)

    # close file
    file_existing.close()

    # open new file for new se
    file_new = open('output/se_new.tsv', 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    csv_new.writerow(['aSE', 'SE', 'cuis', 'meddras'])

    # query for the update nodes and relationship
    query_new = query_start + ' Set a.cuis=split(line.cuis,"|") Merge (n:SideEffect{identifier:line.SE}) On Create Set  n.license="CC0 1.0", n.name=a.name , n.source="UMLS via AEOLUS", n.url="http://identifiers.org/umls/"+line.SE , n.resource=["AEOLUS"],  n.aeolus="yes", n.xrefs=split(line.meddras,"|")  Create (n)-[:equal_to_Aeolus_SE]->(a)'
    query_new = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/aeolus/output/se_new.tsv',
                                                  query_new)
    cypher_file.write(query_new)

    # generate new pharmebinet side effects and connect the with the aeolus outcome
    for cui, outcome_concepts in dict_new_node_cui_to_concept.items():
        if len(outcome_concepts) == 1:
            csv_new.writerow([outcome_concepts[0], cui, '|'.join(dict_aeolus_SE_with_CUIs[outcome_concepts[0]]),
                              'MedDRA:' + '|MedDRA:'.join(outcome_concepts)])
        else:
            print(cui)
            print(outcome_concepts)
            print('multi concept for one cui')
            for outcome_concept in outcome_concepts:
                csv_new.writerow([outcome_concept, cui, '|'.join(dict_aeolus_SE_with_CUIs[outcome_concepts[0]]),
                                  'MedDRA:' + '|MedDRA:'.join(outcome_concepts)])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path aeolus se')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load api key')

    load_api_key()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load already mapped from api cache')

    cache_api()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all Side effects from pharmebinet in a dictionary')

    load_side_effects_from_pharmebinet_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all Side effects from AEOLUS in a dictionary')

    load_side_effects_aeolus_in_dictionary()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all disease from pharmebinet in a dictionary')

    load_disease_infos()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Find cuis for aeolus side effects')

    search_with_api_bioportal()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map round one')

    map_first_round()
    # search_with_api_bioportal()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map round two to disease')

    mapping_to_disease()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('intergarte aeolus outcome to pharmebinet(+Sider)')

    integrate_aeolus_into_pharmebinet()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
