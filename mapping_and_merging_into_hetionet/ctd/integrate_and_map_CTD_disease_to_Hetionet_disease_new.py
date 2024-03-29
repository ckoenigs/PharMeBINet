import datetime
import sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


class Diseasepharmebinet:
    """
    identifier: string (mondo)
    umls_cuis: list
    xrefs: list (different other identifier like omim or mesh)
    synonyms: list (synonym names)
    resource: list (all different sources which include this disease)
    """

    def __init__(self, identifier, synonyms, umls_cuis, xrefs, resource):
        self.identifier = identifier
        self.umls_cuis = umls_cuis
        self.xrefs = xrefs
        self.synonyms = synonyms
        self.resource = resource


class DiseaseCTD:
    """
    idType: string (can be omim or mesh)
    name: string
    altDiseaseIDs: list (can be mesh, omim or do)
    doids: list with doids
    disease_id: sting (the mesh or omim ID)
    cuis: list (umls cuis of this disease)
    mondos:list (mapped mondos)
    how_mapped: string
    """

    def __init__(self, idType, name, altDiseaseIDs, disease_id, doids):
        self.idType = idType
        self.name = name
        self.altDiseaseIDs = altDiseaseIDs
        self.disease_id = disease_id
        self.doids = doids
        self.mondos = []
        self.cuis = []
        self.mapping = []

    def set_cuis(self, cuis):
        self.cuis = cuis

    def set_mondos(self, mondos):
        mondo_set = set(self.mondos)
        self.mondos = list(mondo_set.union(mondos))

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped

    def set_mapping_id(self, identifier):
        self.mapping.append(identifier)
        self.mapping = list(set(self.mapping))


# dictionary with all CTD diseases, which has a relationship  treats or induces with a drug
dict_CTD_disease = {}

# dictionary for pharmebinet diseases with mondo as key and value is class Diseasepharmebinet
dict_diseases_pharmebinet = {}

# dictionary mesh to mondos, information from Monarch Disease Ontology
dict_mesh_to_mondo = {}

# dictionary omim to mondos, information from Monarch Disease Ontology
dict_omim_to_mondo = {}

# dictionary umls cui to mondos, information from Monarch Disease Ontology
dict_umls_cui_to_mondo = {}

# dictionary DOID to mondos, information from Monarch Disease Ontology
dict_doid_to_mondo = {}

# dictionary with name/synonyms to mondo
dict_name_synonym_to_mondo_id = {}

# dictionary for pharmebinet identifier with name as value
dict_pharmebinet_id_to_name = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


'''
load in all diseases from pharmebinet in a dictionary
'''


def load_pharmebinet_diseases_in():
    query = '''MATCH (n:Disease) RETURN n.identifier,n.name, n.synonyms, n.xrefs, n.umls_cuis, n.resource, n.doids'''
    results = g.run(query)

    counter = 0
    for record in results:
        [identifier, name, synonyms, xrefs, umls_cuis, resource, doids] = record.values()
        counter += 1
        # if identifier=='MONDO:0002165':
        #     print('BLUB')
        # add name with mondo to dictionary
        name_formed = name.lower().split(' exact ')[0] if name else ''
        dict_pharmebinet_id_to_name[identifier] = name
        if name_formed not in dict_name_synonym_to_mondo_id:
            dict_name_synonym_to_mondo_id[name_formed] = set([identifier])
        else:
            dict_name_synonym_to_mondo_id[name_formed].add(identifier)

        # add the differnt synonyms with mondo to dictionary
        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()

                if synonym not in dict_name_synonym_to_mondo_id:
                    dict_name_synonym_to_mondo_id[synonym] = set([identifier])
                else:
                    dict_name_synonym_to_mondo_id[synonym].add(identifier)
        else:
            synonyms = []

        # list of the umls cuis without the label 'UMLS_CUI:'
        umls_cuis_without_label = []
        if umls_cuis:
            for umls_cui in umls_cuis:
                if len(umls_cui) > 0:
                    if len(umls_cui.split(':')) < 2:
                        print('ohje')
                    cui = umls_cui.split(':')[1]
                    umls_cuis_without_label.append(cui)
                    if cui in dict_umls_cui_to_mondo:
                        dict_umls_cui_to_mondo[cui].append(identifier)
                    else:
                        dict_umls_cui_to_mondo[cui] = [identifier]

        # generate dictionary with doid to mondo
        if doids:
            for doid in doids:
                if doid in dict_doid_to_mondo:
                    dict_doid_to_mondo[doid].append(identifier)
                else:
                    dict_doid_to_mondo[doid] = [identifier]

        # add all mondo  with mesh and omim in the dictionaries
        if xrefs:
            for xref in xrefs:
                if xref.split(':')[0] == 'MESH':
                    if not xref.split(':')[1] in dict_mesh_to_mondo:
                        dict_mesh_to_mondo[xref.split(':')[1]] = [identifier]
                    else:
                        dict_mesh_to_mondo[xref.split(':')[1]].append(identifier)
                        dict_mesh_to_mondo[xref.split(':')[1]] = list(set(dict_mesh_to_mondo[xref.split(':')[1]]))
                elif xref.split(':')[0] == 'OMIM':
                    if not xref.split(':')[1] in dict_omim_to_mondo:
                        dict_omim_to_mondo[xref.split(':')[1]] = [identifier]
                    else:
                        dict_omim_to_mondo[xref.split(':')[1]].append(identifier)
                        dict_omim_to_mondo[xref.split(':')[1]] = list(set(dict_omim_to_mondo[xref.split(':')[1]]))

        # generate class Diseasepharmebinet and add to dictionary
        disease = Diseasepharmebinet(identifier, synonyms, umls_cuis_without_label, xrefs, resource)
        dict_diseases_pharmebinet[identifier] = disease
    print('length of counter:', counter)
    print('length of disease in pharmebinet:' + str(len(dict_diseases_pharmebinet)))
    print('number of different MESH in mondo:' + str(len(dict_mesh_to_mondo)))
    print('number of different OMIM in mondo:' + str(len(dict_omim_to_mondo)))
    print('number of different UMLS CUI in mondo' + str(len(dict_umls_cui_to_mondo)))


# list of MESH/OMIM IDs which are not mapped to a mondo
list_not_mapped_to_mondo = []

# list of MESH/OMIM  IDs which are mapped
list_mapped_to_mondo = set([])

'''
load in all ctd disease from neo4j 
properties:
    idType
    altDiseaseIDs
    disease_id	
    synonyms
    parentIDs
    name
    parentTreeNumbers
    definition
    tree
    slimMappings
add all disease to a dictionary
then search if the disease has in CTD mondo as alternative ID 
'''


def load_disease_CTD():
    query = ''' MATCH (n:CTD_disease) RETURN n'''
    results = g.run(query)

    # go through all results from the query
    for record in results:
        result = record.data()['n']
        idType = result['idType']
        name = result['name'].lower()
        disease_id = result['disease_id']
        altDiseaseIDs = result['altDiseaseIDs'] if 'altDiseaseIDs' in result else []

        has_mondo = False
        list_dos = []
        for altDiseaseId in altDiseaseIDs:
            if altDiseaseId[0:2] == 'DO':
                list_dos.append(altDiseaseId[3:])

        disease = DiseaseCTD(idType, name, altDiseaseIDs, disease_id, list_dos)
        dict_CTD_disease[disease_id] = disease

    print('size of disease in neo4j:' + str(len(dict_CTD_disease)))
    # print('number of mapped ctd disease:' + str(len(list_mapped_to_mondo)))
    # print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
get mondo ids and add them to the class 
'''


def mondo_to_class(disease_id, dict_mesh_or_omim_to_mondo, name_ctd):
    if disease_id in dict_mesh_or_omim_to_mondo:
        mondos_ids = dict_mesh_or_omim_to_mondo[disease_id]
        if len(mondos_ids) > 1:
            names_pharmebinet = {dict_pharmebinet_id_to_name[x]: x for x in mondos_ids}
            if name_ctd in names_pharmebinet:
                print('find only one string that fits and remove multiple mapping')
                mondos_ids = [names_pharmebinet[name_ctd]]

        dict_CTD_disease[disease_id].set_mondos(mondos_ids)
        dict_CTD_disease[disease_id].set_mapping_id(disease_id)
        dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id')
        list_mapped_to_mondo.add(disease_id)
    else:
        list_not_mapped_to_mondo.append(disease_id)


'''
map with use of mesh and omim ID to Monarch
'''


def map_disease_with_mesh_omim_to_monarch():
    counter = 0
    for disease_id, disease in dict_CTD_disease.items():
        if disease_id == 'D007007':
            print('blu')
        counter += 1
        # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
        if disease.idType == 'MESH':
            mondo_to_class(disease_id, dict_mesh_to_mondo, disease.name)
            continue

        elif disease.idType == 'OMIM':
            mondo_to_class(disease_id, dict_omim_to_mondo, disease.name)
            continue
        # else:
        #     print('geht es hier rein?')
        #     if disease_id in dict_omim_to_mondo:
        #         dict_CTD_disease[disease_id].set_mondos(dict_omim_to_mondo[disease_id])
        #         dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id')
        #         list_mapped_to_mondo.append(disease_id)
        #         continue
        #     elif disease_id in dict_mesh_to_mondo:
        #         dict_CTD_disease[disease_id].set_mondos(dict_mesh_to_mondo[disease_id])
        #         dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM tomondo id')
        #         list_mapped_to_mondo.append(disease_id)
        #         continue

        list_not_mapped_to_mondo.append(disease_id)

    print('number of mapped ctd disease after mesh/omim map:' + str(counter - len(list_not_mapped_to_mondo)))
    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
try to mapped the alternative mesh and omim ids
'''


def try_mapping_with_alternativ(altDiseaseID, disease_id, delete_map_mondo):
    mapped = False
    # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
    if altDiseaseID[0:4] == 'MESH':
        if altDiseaseID[5:] in dict_mesh_to_mondo:
            dict_CTD_disease[disease_id].set_mondos(dict_mesh_to_mondo[altDiseaseID[5:]])
            dict_CTD_disease[disease_id].set_mapping_id(altDiseaseID[5:])
            dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id with alternativ id')
            delete_map_mondo.add(list_not_mapped_to_mondo.index(disease_id))
            list_mapped_to_mondo.add(disease_id)
            mapped = True


    elif altDiseaseID[0:4] == 'OMIM':
        if altDiseaseID[5:] in dict_omim_to_mondo:
            omim_id = altDiseaseID[5:]
            mondos = dict_omim_to_mondo[altDiseaseID[5:]]
            dict_CTD_disease[disease_id].set_mondos(mondos)
            dict_CTD_disease[disease_id].set_mapping_id(altDiseaseID[5:])
            dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to mondo id with alternativ id')
            delete_map_mondo.add(list_not_mapped_to_mondo.index(disease_id))
            list_mapped_to_mondo.add(disease_id)
            mapped = True

    return delete_map_mondo, mapped


'''
map with us of mesh and omim of alternative ids to Monarch Disease Ontology
'''


def map_disease_with_mesh_omim_alternativ_ids_to_monarch_disease_ontology():
    counter = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = set([])
    for disease_id in list_not_mapped_to_mondo:
        if disease_id == 'D007239':
            print('blub')
        counter += 1
        altDiseaseIDs = dict_CTD_disease[disease_id].altDiseaseIDs
        mapped_something = False

        if type(altDiseaseIDs) == list:
            for altDiseaseID in altDiseaseIDs:
                delete_map_mondo, mapped = try_mapping_with_alternativ(altDiseaseID, disease_id, delete_map_mondo)
                if mapped:
                    mapped_something
        else:
            delete_map_mondo, mapped = try_mapping_with_alternativ(altDiseaseIDs, disease_id, delete_map_mondo)
            mapped_something = mapped

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo = list(delete_map_mondo)
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease after mesh/omim alternativ id map:' + str(
        counter - len(list_not_mapped_to_mondo)))
    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
Map with use of doids
'''


def map_disease_with_doids_to_monarch_disease_ontology():
    counter = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    for disease_id in list_not_mapped_to_mondo:
        if disease_id == 'D007239':
            print('blub')
        counter += 1
        doids = dict_CTD_disease[disease_id].doids
        if type(doids) == list:
            for doid in doids:
                if doid in dict_doid_to_mondo:
                    dict_CTD_disease[disease_id].set_mondos(dict_doid_to_mondo[doid])
                    dict_CTD_disease[disease_id].set_mapping_id(doid)
                    dict_CTD_disease[disease_id].set_how_mapped('map with DOID to mondo id')
                    delete_map_mondo.append(list_not_mapped_to_mondo.index(disease_id))
                    list_mapped_to_mondo.add(disease_id)
        else:
            if doids in dict_doid_to_mondo:
                dict_CTD_disease[disease_id].set_mondos(dict_doid_to_mondo[doids])
                dict_CTD_disease[disease_id].set_mapping_id(doids)
                dict_CTD_disease[disease_id].set_how_mapped('map with DOID to mondo id')
                delete_map_mondo.append(list_not_mapped_to_mondo.index(disease_id))
                list_mapped_to_mondo.add(disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease after doid map:' + str(
        counter - len(list_not_mapped_to_mondo)))
    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
mapping with cui?
'''


def map_to_cui_and_try_to_map_to_pharmebinet():
    counter_map = 0
    counter_map_but_not = 0
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    # number of not mapped mesh ids
    count_not_mapped = 0
    for identifier in list_not_mapped_to_mondo:
        idType = dict_CTD_disease[identifier].idType
        # this map to MONDO:0013267 but this is wrong
        if identifier == '607447':
            continue
        # this map to MONDO:0007803
        elif identifier == 'D007024':
            dict_CTD_disease[identifier].set_mondos(['MONDO:0005469'])
            dict_CTD_disease[identifier].set_mapping_id('self mapped')
            delete_map_mondo.append(list_not_mapped_to_mondo.index(identifier))
            dict_CTD_disease[identifier].set_how_mapped('cui match')
            list_mapped_to_mondo.add(identifier)
            counter_map += 1
            continue

        sab = ''
        # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
        if idType == 'MESH':
            sab = 'MSH'
        elif idType == 'OMIM':
            sab = 'OMIM'
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB, STR From MRCONSO Where SAB in ('%s') and CODE= '%s';")
        query = query % (sab, identifier)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            found_some = False
            for (cui, lat, code, sab, label) in cur:
                if cui in dict_umls_cui_to_mondo:
                    found_some = True
                    dict_CTD_disease[identifier].set_mondos(dict_umls_cui_to_mondo[cui])
                    dict_CTD_disease[identifier].set_mapping_id(cui)
                    delete_map_mondo.append(list_not_mapped_to_mondo.index(identifier))
                    dict_CTD_disease[identifier].set_how_mapped('cui match')
                    list_mapped_to_mondo.add(identifier)
            if not found_some:
                counter_map_but_not += 1
            else:

                counter_map += 1
        else:
            count_not_mapped

    print('number of mapped:' + str(counter_map))
    print('number of mapped but not:' + str(counter_map_but_not))
    print('number of not mapped:' + str(count_not_mapped))

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo = list(set(delete_map_mondo))
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


'''
map the name of ctd disease name to name or synonym of Monarch Disease Ontology
'''


def map_with_name():
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    for ctd_disease_id in list_not_mapped_to_mondo:
        name = dict_CTD_disease[ctd_disease_id].name.lower()

        if name.lower() in dict_name_synonym_to_mondo_id:
            dict_CTD_disease[ctd_disease_id].set_mondos(dict_name_synonym_to_mondo_id[name.lower()])
            dict_CTD_disease[ctd_disease_id].set_mapping_id('')
            delete_map_mondo.append(list_not_mapped_to_mondo.index(ctd_disease_id))
            dict_CTD_disease[ctd_disease_id].set_how_mapped('string_match')
            list_mapped_to_mondo.add(ctd_disease_id)

    # delete mapped ctd IDs from list with not mapped CTD identifiers
    delete_map_mondo.sort()
    delete_map_mondo = list(reversed(delete_map_mondo))
    for index in delete_map_mondo:
        list_not_mapped_to_mondo.pop(index)

    print('number of mapped ctd disease:' + str(len(list(list_mapped_to_mondo))))
    print('number of not mapped ctd disease:' + str(len(list_not_mapped_to_mondo)))


# dictionary symptom id to resource
dict_symptom_id_to_resource = {}

# dictionary symptom id to resource
dict_symptom_name_to_ids = {}

# dictionary symptom id to resource
dict_symptom_mesh_to_ids = {}


def load_symptoms_information():
    query = "Match (n:Symptom) Return n.identifier, n.name, n.synonyms, n.xrefs, n.resource"
    results = g.run(query)
    for record in results:
        [identifier, name, synonyms, xrefs, resource] = record.values()
        dict_symptom_id_to_resource[identifier] = resource
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_synonym_to_mondo_id, name.lower(), identifier)
        if synonyms:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_synonym_to_mondo_id, synonym.lower(), identifier)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('MESH'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_symptom_mesh_to_ids, xref.split(':')[1], identifier)


def map_to_symptoms():
    # all mesh and omim identifier which are mapped in this function
    delete_map_mondo = []
    file = open("disease_Disease/mapped_to_symptoms.tsv", 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    header = ['ctd_id', 'node_id', 'mondos', 'resource', 'how_mapped']
    csv_writer.writerow(header)
    counter_mapped = 0
    for ctd_disease_id in list_not_mapped_to_mondo:
        name = dict_CTD_disease[ctd_disease_id].name.lower()

        found_mapping = False

        if name in dict_name_synonym_to_mondo_id:
            found_mapping = True
            mapped_ids = dict_name_synonym_to_mondo_id[name]
            mapping_ids_string = '|'.join(mapped_ids)
            for mapped_id in mapped_ids:
                csv_writer.writerow(
                    [ctd_disease_id, mapped_id, mapping_ids_string,
                     pharmebinetutils.resource_add_and_prepare(dict_symptom_id_to_resource[mapped_id], 'CTD'),
                     'name'])

        if found_mapping:
            counter_mapped += 1
            continue

        # mapping from Melanosis [D008548] to Freckling is wrong
        # the same goes for:
        # "Choristoma"	"D002828" to	"Gray matter heterotopia"
        # "Dermatitis, Perioral"	"D019557" to	"Chapped lip"
        if ctd_disease_id in ["D008548", "D002828", "D019557"]:
            continue

        if ctd_disease_id in dict_symptom_mesh_to_ids:
            found_mapping = True
            mapped_ids = dict_symptom_mesh_to_ids[ctd_disease_id]
            mapping_ids_string = '|'.join(mapped_ids)
            for mapped_id in mapped_ids:
                csv_writer.writerow(
                    [ctd_disease_id, mapped_id, mapping_ids_string,
                     pharmebinetutils.resource_add_and_prepare(dict_symptom_id_to_resource[mapped_id], 'CTD'),
                     'mesh'])

        if found_mapping:
            counter_mapped += 1

    print('From the number of not mapped:', len(list_not_mapped_to_mondo), " are now so many mapped:", counter_mapped)


# files for the different map strategies
map_mesh_omim_to_mondo_file = open('disease_Disease/map_CTD_disease_mesh_omim_to_mondo.tsv', 'w', encoding='utf-8')
header = ['CTD MESH/OMIM', 'type', 'name', 'Monarch Disease Ontology divided by |', 'mondo names', 'map_id']
map_mesh_omim_to_mondo = csv.writer(map_mesh_omim_to_mondo_file, delimiter='\t')
map_mesh_omim_to_mondo.writerow(header)

map_mesh_omim_to_mondo_with_alt_file = open('disease_Disease/map_CTD_disease_alternativ_mesh_omim_to_mondo.tsv', 'w',
                                            encoding='utf-8')
map_mesh_omim_to_mondo_with_alt = csv.writer(map_mesh_omim_to_mondo_with_alt_file, delimiter='\t')
map_mesh_omim_to_mondo_with_alt.writerow(header)

map_mesh_omim_to_mondo_with_name_file = open('disease_Disease/map_CTD_disease_name_to_mondo_name_synonyms.tsv', 'w',
                                             encoding='utf-8')
map_mesh_omim_to_mondo_with_name = csv.writer(map_mesh_omim_to_mondo_with_name_file, delimiter='\t')
map_mesh_omim_to_mondo_with_name.writerow(header)

map_doid_to_mondo_file = open('disease_Disease/map_CTD_disease_doid_to_mondo.tsv', 'w', encoding='utf-8')
map_doid_to_mondo = csv.writer(map_doid_to_mondo_file, delimiter='\t')
map_doid_to_mondo.writerow(header)

map_cui_to_mondo_file = open('disease_Disease/map_CTD_disease_map_to_cui_to_mondo.tsv', 'w', encoding='utf-8')
map_cui_to_mondo = csv.writer(map_cui_to_mondo_file, delimiter='\t')
map_cui_to_mondo.writerow(header)

# multiple mapped ctd disease
multiple_mapped_ctd_disease_file = open('disease_Disease/multiple_mapped_ctd_disease.tsv', 'w', encoding='utf-8')
otherheader = header[:-1]
otherheader.append('mapping_strategy')
multiple_mapped_ctd_disease = csv.writer(multiple_mapped_ctd_disease_file, delimiter='\t')
multiple_mapped_ctd_disease.writerow(otherheader)
# multiple_mapped_ctd_disease.write(
#     'CTD MESH/OMIM','type\tname','Monarch Disease Ontology divided by |','mondo names\t mapping_strategy \n')

# dictionary map how_mapped to a file
dict_how_mapped_to_file = {
    'map with Mesh or OMIM to mondo id': map_mesh_omim_to_mondo,
    'map with Mesh or OMIM to mondo id with alternativ id': map_mesh_omim_to_mondo_with_alt,
    'string_match': map_mesh_omim_to_mondo_with_name,
    'map with DOID to mondo id': map_doid_to_mondo,
    'cui match': map_cui_to_mondo
}

# dictionary multiple mapping ctd which mapping source
dict_how_mapped_to_multiple_mapping = {
    'map with Mesh or OMIM to mondo id': 0,
    'map with Mesh or OMIM to mondo id with alternativ id': 0,
    'string_match': 0,
    'map with DOID to mondo id': 0,
    'cui match': 0
}

'''
integrate disease into pharmebinet:
The ctd disease in neo4j gett a connection to the pharmebinet disease.
Further they get the list of mondos as properties.
The mapped pharmebinet disease  will get additional properties.
'''


def integrate_disease_into_pharmebinet():
    counter_all = 0
    counter_not_mapped = 0

    counter_intersection = 0
    # count the number of mapped ctd disease
    counter_with_mondos = 0
    csvfile_ctd_pharmebinet_disease = open('disease_Disease/ctd_pharmebinet.tsv', 'w', encoding='utf-8')
    writer = csv.writer(csvfile_ctd_pharmebinet_disease, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['CTD_diseaseID', 'pharmebinetDiseaseId', 'mondos', 'resource', 'how_mapped'])

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = '''Match (d)-[r:equal_to_D_Disease_CTD]->(n) Delete r;\n '''
    cypher_file.write(query)
    # go through all ctd disease
    for ctd_disease_id, ctd_disease in dict_CTD_disease.items():
        counter_all += 1
        name = ctd_disease.name.lower()
        if ctd_disease_id == 'D004806':
            print('blub')
        mondos = ctd_disease.mondos
        if len(mondos) > 1 and type(mondos) == list:
            if name.lower() in dict_name_synonym_to_mondo_id:
                mondos_name = dict_name_synonym_to_mondo_id[name.lower()]
                mondos_intersection = list(set(mondos).intersection(mondos_name))
                if len(mondos_intersection) > 0:
                    counter_intersection += 1
                    mondos = mondos_intersection
                    # print(ctd_disease_id)
        if len(mondos) > 0:
            counter_with_mondos += 1
            how_mapped = ctd_disease.how_mapped
            string_mondos = "|".join(mondos)
            names = ''

            mapping_ids = ctd_disease.mapping
            mapping_ids_string = '|'.join(mapping_ids)

            names = '|'.join([dict_pharmebinet_id_to_name[mondo] for mondo in mondos])

            idType = ctd_disease.idType

            if len(mondos) > 1:
                dict_how_mapped_to_multiple_mapping[how_mapped] += 1
                multiple_mapped_ctd_disease.writerow([ctd_disease_id, idType, name, string_mondos, names
                                                         , how_mapped])
            # print([ctd_disease_id ,idType , name , string_mondos , names[:-1] ,
            #                                            mapping_ids_string ])

            dict_how_mapped_to_file[how_mapped].writerow([ctd_disease_id, idType, name, string_mondos, names,
                                                          mapping_ids_string])
            string_mondos = "|".join(mondos)
            # set in neo4j the mondos for the ctd disease
            # query = '''MATCH (n:CTD_disease{disease_id:'%s'}) SET n.mondos=['%s'] '''
            # query = query % (ctd_disease_id, string_mondos)
            # g.run(query)

            # generate for all mapped mondos a connection and add new properties to pharmebinet disease
            for mondo in mondos:
                disease_class = dict_diseases_pharmebinet[mondo]
                resource = set(disease_class.resource)
                writer.writerow(
                    [ctd_disease_id, mondo, string_mondos, pharmebinetutils.resource_add_and_prepare(resource, 'CTD'),
                     how_mapped])
        else:
            counter_not_mapped += 1
            if ctd_disease_id not in list_not_mapped_to_mondo:
                print(ctd_disease_id)
            #     print(ctd_disease.how_mapped)

    print('all steps:' + str(counter_all))
    print('not mapped:' + str(counter_not_mapped))
    print('number of mapped ctd disease:' + str(counter_with_mondos))
    print('counter intersection mondos:' + str(counter_intersection))
    print(dict_how_mapped_to_multiple_mapping)
    query = '''MATCH (n:CTD_disease{disease_id:line.CTD_diseaseID}), (d:Disease{identifier:line.pharmebinetDiseaseId}) Merge (d)-[:equal_CTD_disease{how_mapped:line.how_mapped}]->(n) Set  n.mondos=split(line.mondos, '|') With line, d, n Where d.ctd is NULL Set d.resource=split(line.resource,"|") , d.ctd='yes', d.ctd_url='http://ctdbase.org/detail.go?type=disease&acc='+line.CTD_diseaseID '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/disease_Disease/ctd_pharmebinet.tsv',
                                              query)
    cypher_file.write(query)
    query = ''' MATCH (n:CTD_disease{disease_id:line.ctd_id}), (d:Symptom{identifier:line.node_id}) Merge (d)-[:equal_CTD_disease{how_mapped:line.how_mapped}]->(n) Set  n.mondos=split(line.mondos, '|') With line, d, n Where d.ctd is NULL Set d.resource=split(line.resource,"|") , d.ctd='yes', d.ctd_url='http://ctdbase.org/detail.go?type=disease&acc='+line.CTD_diseaseID '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/disease_Disease/mapped_to_symptoms.tsv',
                                              query)
    cypher_file.write(query)

    # generate a file with all not mapped diseases from ctd
    file_not_map = open('disease_Disease/not_map_CTD_disease.tsv', 'w', encoding='utf-8')
    csv_not_mapped = csv.writer(file_not_map, delimiter='\t')

    csv_not_mapped.writerow(['CTD MESH/OMIM', 'type ', 'CTD names'])
    for identifier_ctd in list_not_mapped_to_mondo:
        ctd_disease = dict_CTD_disease[identifier_ctd]
        idType = ctd_disease.idType
        name = ctd_disease.name
        csv_not_mapped.writerow([identifier_ctd, idType, name])


# path to directory
path_of_directory = ''


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
    print('Load all disease from pharmebinet into a dictionary')

    load_pharmebinet_diseases_in()

    # print(dict_name_synonym_to_mondo_id['Combined Oxidative Phosphorylation Deficiency type 5'.lower()])

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all ctd diseases from neo4j into a dictionary')

    load_disease_CTD()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map ctd disease mesh or Omim to Disease ')

    map_disease_with_mesh_omim_to_monarch()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map ctd disease alternative mesh or Omim to Disease ')

    map_disease_with_mesh_omim_alternativ_ids_to_monarch_disease_ontology()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map ctd disease doid to Disease ')

    map_disease_with_doids_to_monarch_disease_ontology()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map ctd disease cui to Disease ')

    map_to_cui_and_try_to_map_to_pharmebinet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map ctd disease name to mondo name and synonyms')

    map_with_name()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load symptoms information into dictionary')

    load_symptoms_information()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map the not mapped to symptoms')

    map_to_symptoms()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('integrate disease into pharmebinet')

    integrate_disease_into_pharmebinet()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
