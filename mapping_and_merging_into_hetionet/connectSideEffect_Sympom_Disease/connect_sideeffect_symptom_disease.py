import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases


class Symptom:
    """
    identifier:string (MESH id/ umls cui)
    name:string
    """

    def __init__(self, identifier, name, cuis):
        self.identifier = identifier
        self.name = name

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


class SideEffect:
    """
    identifier:string (umls cui)
    name:string
    how_mapped:string
    """

    def __init__(self, identifier, name):
        self.identifier = identifier
        self.name = name


'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g
    g = create_connection_to_databases.database_connection_neo4j()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

def correct_string_for_query(name):
    """
    Prepare string for mysql query
    :param name: string
    :return: string
    """
    return name.replace("'","\\'")


# dictionary of all symptoms from hetionet, with mesh_id/ umls cui as key and value is class Symptom
dict_symptoms = {}

# list with all mesh id which has no umls cui
list_mesh_without_cui = []

# dictionary with all side effects from hetionet with umls cui as key and class SideEffect as value
dict_side_effects = {}

# dictionary name/umls_id/meddra_id to set of sideeffects id
dict_name_ids_to_sideeffect_ids = {}

# set of pairs of symptom side effect
set_symptom_side_effect = set()

# set of pairs of disease side effect
set_disease_side_effect = set()

# set of pairs of disease symptom
set_disease_symptom = set()

# generate cypher file
cypher = open('output/cypher.cypher', 'w', encoding='utf-8')
query = 'Match (n:Disease) Set n:Phenotype;\n'
cypher.write(query)
query = 'Match (n:Symptom) Set n:Phenotype;\n'
cypher.write(query)
query = 'Match (n:SideEffect) Set n:Phenotype;\n'
cypher.write(query)


def add_element_to_dictionary(property, identifier, dictionary):
    """
    Add a key (property), value (identifier) to a dictionary
    :param property: string
    :param identifier:  string
    :param dictionary: dictionary
    :return: 
    """
    if not property in dictionary:
        dictionary[property] = set()
    dictionary[property].add(identifier)


def mapping(from_mapper, from_identifier, dictionary, map_file, how_mapped, set_of_pairs):
    """
    Map from one name/id of on label to the dictionary of the other label
    if mapped write into  the file the mapping pairs and how they mapped
    else return that it did not mapped
    :param from_mapper: string
    :param from_identifier: string
    :param dictionary: dictionary
    :param map_file: csv.writer
    :param how_mapped: string
    :param set_of_pairs: set of tuple pairs
    :return: if it mapped or not
    """
    if from_mapper in dictionary:
        for to_identifier in dictionary[from_mapper]:
            if not (from_identifier, to_identifier) in set_of_pairs:
                map_file.writerow([from_identifier, to_identifier, how_mapped])
                set_of_pairs.add((from_identifier, to_identifier))
        return True
    return False


def create_cypher_query(header, from_label, to_label, file_name):
    if to_label == 'SideEffect':
        short_second = 'SE'
    else:
        short_second = to_label[0]
    if from_label =='Phenotype':
        short_first ='PT'
    else:
        short_first=from_label[0]
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/connectSideEffect_Sympom_Disease/%s" As line FIELDTERMINATOR '\\t' 
                Match (first:%s {identifier:line.%s}), (second:%s {identifier:line.%s})  Create (first)-[:EQUAL_%se%s{how_mapped:line.%s, pharmebinet:'yes'}]->(second);\n'''
    query = query % (file_name, from_label, header[0], to_label, header[1], short_first, short_second, header[2])
    cypher.write(query)


def create_mapping_file(directory, file_name, header, from_label, to_label):
    """
    generate the tsv writer for the mapping file and additionaly also the
    :param directory:
    :param file_name:
    :param header:
    :param from_label:
    :param to_label:
    :return:
    """
    path = directory + '/' + file_name
    map_file = open(path, 'w', encoding='utf-8')
    csv_writer = csv.writer(map_file, delimiter='\t')
    csv_writer.writerow(header)

    create_cypher_query(header, from_label, to_label, path)
    return csv_writer


'''
function that load all side effects in a dictionary 
'''


def load_all_sideEffects_in_a_dict():
    query = '''MATCH (n:SideEffect) RETURN n.name, n.identifier, n.xrefs '''
    results = g.run(query)
    for name, cui, xrefs, in results:
        name = name.lower()
        side_effect = SideEffect(cui, name)
        dict_side_effects[cui] = side_effect

        add_element_to_dictionary(name, cui, dict_name_ids_to_sideeffect_ids)
        add_element_to_dictionary(cui, cui, dict_name_ids_to_sideeffect_ids)

        if xrefs:
            for xref in xrefs:
                add_element_to_dictionary(xref, cui, dict_name_ids_to_sideeffect_ids)

    print('size of side effects in hetionet:' + str(len(dict_side_effects)))


# dictionary name/mesh to set of symptom ids
dict_name_and_mesh_ids_to_symptom_ids = {}

# dictionary hpo id to set of symptom ids
dict_hpo_ids_to_symptom_ids = {}

# dictionary umls id to set of symptom ids
dict_umls_id_to_symptom_ids = {}

'''
function that load all symptoms in a dictionary and check if it has a umls cui or not
if not find a cui with us of umls via mysql. Take preferred the umls cui wwhere the name is the same.
'''


def load_all_symptoms_in_a_dict():
    query = "MATCH (n:Symptom) RETURN n"
    results = g.run(query)
    counter_with_name = 0
    counter_without_name = 0

    # create mapping file to side effect and cypher query
    csv_mapping_s_to_se = create_mapping_file('mapping_symptom_sideeffect', 'map_s_to_se.tsv',
                                              ['symptom_id', 'side_effect_id', 'how_mapped'], 'Symptom', 'SideEffect')
    for result, in results:
        name = result['name'].lower()
        identifier = result['identifier']
        xrefs= result['xrefs'] if 'xrefs' in result else []

        symptom = Symptom(identifier, name, [])
        add_element_to_dictionary(name, identifier, dict_name_and_mesh_ids_to_symptom_ids)


        mapped_with_name = mapping(name, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_s_to_se,
                                   'mapped with name', set_symptom_side_effect)
        if mapped_with_name:
            counter_with_name += 1

        set_mesh = set()
        cuis=set()
        for xref in xrefs:
            if xref.startswith('MESH'):
                mesh_id=xref.split(':')[1]
                set_mesh.add(mesh_id)
                add_element_to_dictionary(mesh_id, identifier, dict_name_and_mesh_ids_to_symptom_ids)
            elif xref.startswith('UMLS'):
                umls_cui=xref.split(':')[1]
                cuis.add(umls_cui)
                # add_element_to_dictionary(umls_cui, identifier, dict_umls_id_to_symptom_ids)
            elif xref.startswith('HPO'):
                hpo_id=xref.split(':',1)[1]
                add_element_to_dictionary(hpo_id, identifier, dict_hpo_ids_to_symptom_ids)


        # manual checked with wrong mapping with umls
        if identifier in ['D004881']:
            list_mesh_without_cui.append(identifier)
            print(identifier)
            continue

        found_with_umls=False
        cuis_from_umls=set()

        # get first hte umls with the same name
        cur = con.cursor()
        query = ("Select CUI From MRCONSO Where STR='%s';")
        query = query % (correct_string_for_query(name))
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            found_with_umls = True
            # list of all umls cuis which has the mesh id
            list_cuis = []
            same_name = False
            # list of all umls cuis with the same name
            list_cuis_with_same_name = set()
            for (cui,) in cur:
                cuis_from_umls.add(cui)
        # because sometimes when I checked the umls cuis of HPO they were not so good. So, they are validated with umls
        # information.
        if len(set_mesh)>0 and len(cuis_from_umls)==0:
            for mesh_id in set_mesh:
                cur = con.cursor()
                query = ("Select CUI,LAT,STR From MRCONSO Where SAB='MSH' and CODE= '%s';")
                query = query % (mesh_id)
                rows_counter = cur.execute(query)
                if rows_counter > 0:
                    found_with_umls=True
                    # list of all umls cuis which has the mesh id
                    list_cuis = []
                    same_name = False
                    # list of all umls cuis with the same name
                    list_cuis_with_same_name = set()
                    for (cui, lat, label,) in cur:
                        label = label.lower()
                        list_cuis.append(cui)
                        if label == name:
                            same_name = True
                            list_cuis_with_same_name.add(cui)
                    if same_name:
                        cuis_from_umls = cuis_from_umls.union(list_cuis_with_same_name)
                        counter_with_name += 1
                    else:
                        cuis_from_umls = cuis_from_umls.union(list_cuis)
                        counter_without_name += 1

        # check compare hpo umls cui and umls cui from umls with mesh and/or name
        # if overlap exists this is used else the one from umls nad only noting else exists the umls cuis from HPO
        intersection= cuis.intersection(cuis_from_umls)
        found_intersection=False
        if len(intersection)>0:
            cuis=intersection
        else:
            cuis=cuis_from_umls if len(cuis_from_umls)>0 else cuis

        for cui in cuis:
            add_element_to_dictionary(cui, identifier, dict_umls_id_to_symptom_ids)
            list_cuis_mapped = set()
            mapped_with='xrefs umls cui' if not found_with_umls else 'mapped with umls cui with umls and/or xref'
            if not mapped_with_name:
                mapping(cui, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_s_to_se,
                        mapped_with, set_symptom_side_effect)
                if cui in dict_side_effects:
                    list_cuis_mapped.add(cui)
                if len(list_cuis_mapped) > 0:
                    # dict_mesh_map_to_cui[identifier] = list_cuis_mapped
                    symptom.set_how_mapped('map with all cuis of mesh id')
        if len(cuis)==0:
            list_mesh_without_cui.append(identifier)

            # print(identifier)

        dict_symptoms[identifier] = symptom

    print('Number of Symptoms without a umls cui and now from umls',len(list_mesh_without_cui))
    print('Number of symptoms in hetionet:' + str(len(dict_symptoms)))
    print('mapped with mesh and name:' + str(counter_with_name))
    print('mapped only with mesh:' + str(counter_without_name))


def load_and_map_disease():
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)

    # create mapping file to side effect and cypher query
    csv_mapping_d_to_se = create_mapping_file('mapping_disease_mapping', 'map_d_to_se.tsv',
                                              ['disease_id', 'side_effect_id', 'how_mapped'], 'Disease', 'SideEffect')

    csv_mapping_d_to_s = create_mapping_file('mapping_disease_mapping', 'map_d_to_s.tsv',
                                             ['disease_id', 'symptom_id', 'how_mapped'], 'Disease', 'Symptom')

    counter_mapped_se = 0
    counter_mapped_symp = 0

    for disease, in results:
        name = disease['name'].lower() if 'name' in disease else ''
        identifier = disease['identifier']

        mapped_to_sideeffect = False
        mapped_to_symptom = False
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        umls_cuis=[]
        mesh_ids=[]
        for xref in xrefs:
            if xref.lower().startswith('umls'):
                umls = xref.split(':')[1]
                umls_cuis.append(umls)
                mapped = mapping(umls, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se,
                                 'mapped with UMLS ID', set_disease_side_effect)
                if mapped:
                    mapped_to_sideeffect = True
                    counter_mapped_se += 1
                # mapped = mapping(umls, identifier, dict_umls_id_to_symptom_ids, csv_mapping_d_to_s,
                #                  'mapped with UMLS ID from xref', set_disease_symptom)
                # if mapped:
                #     mapped_to_symptom = True
                #     counter_mapped_symp += 1
            elif xref.lower().startswith('meddra'):
                mapped = mapping(xref, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se,
                                 'mapped with MedDRA ID', set_disease_side_effect)
                if mapped:
                    mapped_to_sideeffect = True
                    counter_mapped_se += 1
            elif xref.lower().startswith('mesh'):
                mesh = xref.split(':')[1]
                mesh_ids.append(mesh)
                # mapped = mapping(mesh, identifier, dict_name_and_mesh_ids_to_symptom_ids, csv_mapping_d_to_s,
                #                  'mapped with MESH ID', set_disease_symptom)
                # if mapped:
                #     mapped_to_symptom = True
                #     counter_mapped_symp += 1
            elif xref.lower().startswith('hp'):
                mapped = mapping(xref, identifier, dict_hpo_ids_to_symptom_ids, csv_mapping_d_to_s,
                                 'mapped with HPO ID', set_disease_symptom)
                if mapped:
                    mapped_to_symptom = True
                    counter_mapped_symp += 1

        if not mapped_to_sideeffect:
            mapped = mapping(name, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se, 'mapped with name',
                             set_disease_side_effect)

            # if not map try with disease synonyms
            if not mapped:
                synonyms = disease['synonyms'] if 'synonyms' in disease else []
                for synonym in synonyms:
                    if '[' in synonym:
                        synonym = synonym.rsplit(' [', 1)[0]
                    synonym = synonym.lower()
                    mapped_syn = mapping(synonym, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_d_to_se,
                                         'mapped with synonyms', set_disease_side_effect)
                    if mapped_syn:
                        mapped = True

            if not mapped:
                cur = con.cursor()
                query = ('Select CUI,LAT,STR From MRCONSO Where  STR= "%s";')
                query = query % (correct_string_for_query(name))
                rows_counter = cur.execute(query)
                mapped_with_umls = False
                if rows_counter > 0:
                    for (cui, lat, label,) in cur:
                        mapped_with_umls = mapping(cui, identifier, dict_name_ids_to_sideeffect_ids,
                                                   csv_mapping_d_to_se,
                                                   'mapped with cui from umls', set_disease_side_effect)
                        if mapped_with_umls:
                            mapped = True
            if mapped:
                counter_mapped_se += 1
        if not mapped_to_symptom:
            for umls in umls_cuis:
                mapped = mapping(umls, identifier, dict_umls_id_to_symptom_ids, csv_mapping_d_to_s,
                                 'mapped with UMLS ID from xref', set_disease_symptom)
                if mapped:
                    mapped_to_symptom = True
                    counter_mapped_symp += 1
                    # break

        # if not mapped_to_symptom:
        #     for mesh in mesh_ids:
        #         mapped = mapping(mesh, identifier, dict_name_and_mesh_ids_to_symptom_ids, csv_mapping_d_to_s,
        #                          'mapped with MESH ID', set_disease_symptom)
        #         if mapped:
        #             mapped_to_symptom = True
        #             counter_mapped_symp += 1
                # break

        if not mapped_to_symptom:
            mapped = mapping(name, identifier, dict_name_and_mesh_ids_to_symptom_ids, csv_mapping_d_to_s, 'mapped with name',
                             set_disease_symptom)
            if mapped:
                counter_mapped_symp += 1

    print('number of mapped disease to se:', counter_mapped_se)
    print('number of mapped disease to symptom:', counter_mapped_symp)

def load_and_map_phenotype():
    query = "MATCH (n:Phenotype) Where size(labels(n))=1 RETURN n"
    results = g.run(query)

    # create mapping file to side effect and cypher query
    csv_mapping_p_to_se = create_mapping_file('mapping_phenotype_mapping', 'map_p_to_se.tsv',
                                              ['phenotype_id', 'side_effect_id', 'how_mapped'], 'Phenotype', 'SideEffect')

    set_phenotype_se=set()

    counter_mapped_se = 0

    for phenotype, in results:
        name = phenotype['name'].lower() if 'name' in phenotype else ''
        identifier = phenotype['identifier']

        mapped_to_sideeffect = False
        xrefs = phenotype['xrefs'] if 'xrefs' in phenotype else []
        for xref in xrefs:
            if xref.lower().startswith('umls'):
                umls = xref.split(':')[1]
                mapped = mapping(umls, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_p_to_se,
                                 'mapped with UMLS ID', set_phenotype_se)
                if mapped:
                    mapped_to_sideeffect = True
                    counter_mapped_se += 1
            elif xref.lower().startswith('meddra'):
                mapped = mapping(xref, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_p_to_se,
                                 'mapped with MedDRA ID', set_phenotype_se)
                if mapped:
                    mapped_to_sideeffect = True
                    counter_mapped_se += 1

        if not mapped_to_sideeffect:
            mapped = mapping(name, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_p_to_se, 'mapped with name',
                             set_phenotype_se)

            # if not map try with phenotype synonyms
            if not mapped:
                synonyms = phenotype['synonyms'] if 'synonyms' in phenotype else []
                for synonym in synonyms:
                    if '[' in synonym:
                        synonym = synonym.rsplit(' [', 1)[0]
                    synonym = synonym.lower()
                    mapped_syn = mapping(synonym, identifier, dict_name_ids_to_sideeffect_ids, csv_mapping_p_to_se,
                                         'mapped with synonyms', set_phenotype_se)
                    if mapped_syn:
                        mapped = True

            if not mapped:
                cur = con.cursor()
                query = ('Select CUI,LAT,STR From MRCONSO Where  STR= "%s";')
                query = query % (correct_string_for_query(name))
                rows_counter = cur.execute(query)
                mapped_with_umls = False
                if rows_counter > 0:
                    for (cui, lat, label,) in cur:
                        mapped_with_umls = mapping(cui, identifier, dict_name_ids_to_sideeffect_ids,
                                                   csv_mapping_p_to_se,
                                                   'mapped with cui from umls', set_phenotype_se)
                        if mapped_with_umls:
                            mapped = True
            if mapped:
                counter_mapped_se += 1


    print('number of mapped phenotype to se:', counter_mapped_se)

def main():
    global path_of_directory

    # path to to project
    if len(sys.argv) == 2:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path for connection of se,s,d')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in side effects from hetionet')

    load_all_sideEffects_in_a_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in symptoms from hetionet and map to se')

    load_all_symptoms_in_a_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load disease an map to se and symptom')

    load_and_map_disease()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load phenotype an map to se and symptom')

    load_and_map_phenotype()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
