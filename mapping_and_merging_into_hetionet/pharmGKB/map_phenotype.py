import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of all disease ids to resource
dict_disease_to_resource = {}

# dictionary of all disease ids to xrefs
dict_disease_to_xrefs = {}

# dictionary disease name to disease id
dict_disease_name_to_disease_id = {}

# dictionary of all symptom ids to resource
dict_symptom_to_resource = {}

# dictionary of all symptom ids to xrefs
dict_symptom_to_xrefs = {}

# dictionary symptom name to symptom id
dict_symptom_name_to_symptom_id = {}

# dictionary of all se ids to resource
dict_se_to_resource = {}

# dictionary of all se ids to xrefs
dict_se_to_xrefs = {}

# dictionary se name to se id
dict_se_name_to_se_id = {}

# dictionary xrefs to dictionary for xref id to disease id
dict_xrefs_to_dict_xref_to_disease = {}

# dictionary xrefs to dictionary for xref id to symptom id
dict_xrefs_to_dict_xref_to_symptom = {}

# dictionary xrefs to dictionary for xref id to se id
dict_xrefs_to_dict_xref_to_se = {}


def add_entry_to_dictionary(dictionary, key, value):
    """
    Integrate a key -value to set in to a dictionary. if kex not existing key is add to dictionary with a set.
    :param dictionary:
    :param key:
    :param value:
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def prepare_and_integrate_information_into_dictionary(xref, dict_xrefs_to_dict_xref_id_to_identifier, identifier,
                                                      source):
    """
    gete only the id from the xref
    add source to dictionary if not existing and then add xref-identifier pair into dictionary
    :param xref: string
    :param dict_xrefs_to_dict_xref_id_to_identifier:dictionary
    :param identifier: string
    :param source: string
    :return:
    """
    xref = xref.split(':', 1)[1]
    if source not in dict_xrefs_to_dict_xref_id_to_identifier:
        dict_xrefs_to_dict_xref_id_to_identifier[source] = {}
    add_entry_to_dictionary(dict_xrefs_to_dict_xref_id_to_identifier[source], xref, identifier)


'''
load in all compound from hetionet in a dictionary
'''


def load_db_nodes_in(label, dict_node_to_resource, dict_node_name_to_node_id, dict_xrefs_to_dict_xref_id_to_identifier,
                     dict_node_to_xrefs, identifier_umls=False):
    query = '''MATCH (n:%s) RETURN n.identifier, n.name ,n.synonyms, n.resource, n.xrefs'''
    query = query % (label)
    results = g.run(query)

    for identifier, name, synonyms, resource, xrefs, in results:
        dict_node_to_resource[identifier] = set(resource) if resource else set()
        dict_node_to_xrefs[identifier] = set(xrefs) if xrefs else set()

        name = name.lower()
        add_entry_to_dictionary(dict_node_name_to_node_id, name, identifier)

        if identifier_umls:
            if 'umls' not in dict_xrefs_to_dict_xref_id_to_identifier:
                dict_xrefs_to_dict_xref_id_to_identifier['umls'] = {}
            add_entry_to_dictionary(dict_xrefs_to_dict_xref_id_to_identifier['umls'], identifier, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                add_entry_to_dictionary(dict_node_name_to_node_id, synonym, identifier)

        if xrefs:
            for xref in xrefs:
                if xref.startswith('UMLS'):
                    prepare_and_integrate_information_into_dictionary(xref, dict_xrefs_to_dict_xref_id_to_identifier,
                                                                      identifier, 'umls')

                elif xref.startswith('MESH'):
                    prepare_and_integrate_information_into_dictionary(xref, dict_xrefs_to_dict_xref_id_to_identifier,
                                                                      identifier, 'mesh')
                elif xref.startswith('MedDRA'):
                    prepare_and_integrate_information_into_dictionary(xref, dict_xrefs_to_dict_xref_id_to_identifier,
                                                                      identifier, 'meddra')
                elif xref.startswith('SCTID'):
                    prepare_and_integrate_information_into_dictionary(xref, dict_xrefs_to_dict_xref_id_to_identifier,
                                                                      identifier, 'snomed')
                elif xref.startswith('SNOMEDCT_US'):
                    prepare_and_integrate_information_into_dictionary(xref, dict_xrefs_to_dict_xref_id_to_identifier,
                                                                      identifier, 'snomed')

    print('length of disease in db:' + str(len(dict_disease_to_resource)))


# dict_source_to_pair
dict_source_to_pair = {}


def check_for_mapping(dict_source_to_ids, source, source_extra, dict_source_to_disease_ids, csv_writer, identifier,
                      dictionary_node_to_resource, dict_node_to_xrefs, label):
    """
    go through all cui_ids of the different sources and check if the are in the dictionary to disease id. If so add
    them into tsv file.
    :param dict_source_to_ids:
    :param source:
    :param dict_source_to_disease_ids:
    :param csv_writer:
    :param identifier:
    :return:
    """
    if not source_extra in dict_source_to_pair:
        dict_source_to_pair[source_extra] = set()

    found_mapping = False
    for cui in dict_source_to_ids[source]:
        if cui in dict_source_to_disease_ids:
            found_mapping = True
            for disease_id in dict_source_to_disease_ids[cui]:
                if (disease_id, identifier) in dict_source_to_pair[source_extra]:
                    continue
                print(disease_id)
                resource = dictionary_node_to_resource[disease_id]
                print(resource)
                resource.add("PharmGKB")
                resource = "|".join(sorted(resource))
                xrefs = dict_node_to_xrefs[disease_id]
                xrefs.add('PharmGKB:' + identifier)
                xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, label)
                csv_writer.writerow([disease_id, identifier, resource, source_extra.lower(), '|'.join(xrefs)])
                dict_source_to_pair[source_extra].add((disease_id, identifier))
    return found_mapping


def load_pharmgkb_phenotypes_in():
    """
    diseaserate mapping file and cypher file
    mapp disease pharmgkb to disease
    :return:
    """

    # generate cypher file
    dict_csv_map, csv_new = generate_cypher_file()

    query = '''MATCH (n:PharmGKB_Phenotype)--() RETURN Distinct n'''
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    for result, in results:
        identifier = result['id']
        dict_names = {}
        name = result['name'].lower() if 'name' in result else ''
        add_entry_to_dictionary(dict_names, 'name', name)

        external_identifiers = result['external_vocabulary'] if 'external_vocabulary' in result else []
        dict_source_to_ids = {}
        for external_identifier in external_identifiers:
            source_info = external_identifier.split(':', 1)
            add_entry_to_dictionary(dict_source_to_ids, source_info[0], source_info[1].split('(')[0])

        found_a_mapping = False

        if 'name' in dict_names:
            found_a_mapping = check_for_mapping(dict_names, 'name', 'name_disease', dict_disease_name_to_disease_id,
                                                dict_csv_map['Disease'],
                                                identifier, dict_disease_to_resource, dict_disease_to_xrefs, 'Disease')

        if found_a_mapping:
            counter_map += 1
            continue

        if 'SnoMedCT' in dict_source_to_ids:
            found_a_mapping = check_for_mapping(dict_source_to_ids, 'SnoMedCT', 'SnoMedCT_disease',
                                                dict_xrefs_to_dict_xref_to_disease['snomed'],
                                                dict_csv_map['Disease'], identifier, dict_disease_to_resource,
                                                dict_disease_to_xrefs, 'Disease')

        if found_a_mapping:
            counter_map += 1
            continue

        if 'UMLS' in dict_source_to_ids:
            found_a_mapping = check_for_mapping(dict_source_to_ids, 'UMLS', 'UMLS_disease',
                                                dict_xrefs_to_dict_xref_to_disease['umls'],
                                                dict_csv_map['Disease'], identifier, dict_disease_to_resource,
                                                dict_disease_to_xrefs, 'Disease')

        if found_a_mapping:
            counter_map += 1
            continue

        if 'name' in dict_names:
            found_a_mapping = check_for_mapping(dict_names, 'name', 'name_symptom', dict_symptom_name_to_symptom_id,
                                                dict_csv_map['Symptom'],
                                                identifier, dict_symptom_to_resource, dict_symptom_to_xrefs, 'Symptom')

        if found_a_mapping:
            counter_map += 1
            continue

        # if 'SnoMedCT' in dict_source_to_ids:
        #     found_a_mapping = check_for_mapping(dict_source_to_ids, 'SnoMedCT', 'Snomed_symptom',
        #                                         dict_xrefs_to_dict_xref_to_symptom['snomed'],
        #                                         dict_csv_map['Symptom'], identifier, dict_symptom_to_resource,dict_symptom_to_xrefs )
        #
        # if found_a_mapping:
        #     counter_map += 1
        #     continue

        if 'UMLS' in dict_source_to_ids:
            found_a_mapping = check_for_mapping(dict_source_to_ids, 'UMLS', 'UMLS_symptom',
                                                dict_xrefs_to_dict_xref_to_symptom['umls'],
                                                dict_csv_map['Symptom'], identifier, dict_symptom_to_resource,
                                                dict_symptom_to_xrefs, 'Symptom')

        if found_a_mapping:
            counter_map += 1
            continue

        if 'name' in dict_names:
            found_a_mapping = check_for_mapping(dict_names, 'name', 'name_se',
                                                dict_se_name_to_se_id, dict_csv_map['SideEffect'],
                                                identifier,
                                                dict_se_to_resource, dict_se_to_xrefs, 'SideEffect')

        if found_a_mapping:
            counter_map += 1
            continue

        if 'UMLS' in dict_source_to_ids:
            found_a_mapping = check_for_mapping(dict_source_to_ids, 'UMLS', 'UMLS_se',
                                                dict_xrefs_to_dict_xref_to_se['umls'],
                                                dict_csv_map['SideEffect'], identifier, dict_se_to_resource,
                                                dict_se_to_xrefs, 'SideEffect')

        if found_a_mapping:
            counter_map += 1
            continue

        # if 'alternate_names' in result:
        #     for alternate_name in result['alternate_names']:
        #         alternate_name = alternate_name.lower()
        #         add_entry_to_dictionary(dict_names, 'name', alternate_name)
        #     found_a_mapping = check_for_mapping(dict_names, 'name', 'alternate_names_and_name_se',
        #                                        dict_se_name_to_se_id, dict_csv_map['SideEffect'],
        #                                        identifier,
        #                                        dict_se_to_resource, dict_se_to_xrefs)

        if found_a_mapping:
            counter_map += 1
            continue
        # if 'MeSH' in dict_source_to_ids:
        #     found_a_mapping=check_for_mapping(dict_source_to_ids, 'MeSH', dict_mesh_to_disease, csv_writer,identifier)
        #
        # if found_a_mapping:
        #     counter_map+=1
        #     continue
        #
        # if 'MedDRA' in dict_source_to_ids:
        #     found_a_mapping=check_for_mapping(dict_source_to_ids, 'MedDRA', dict_meddra_to_disease, csv_writer,identifier)
        #
        # if found_a_mapping:
        #     counter_map+=1
        #     continue

        # alternate_names would be another possibility

        # I do not want to add a node which is named adverse events!
        if identifier != 'PA166151827':
            external_identifiers.append('pharmGKB:' + identifier)
            xrefs = '|'.join(
                go_through_xrefs_and_change_if_needed_source_name([x.rsplit('(', 1)[0] for x in external_identifiers],
                                                                  'Phenotype'))
            csv_new.writerow([identifier, xrefs])

        print(name)
        print(result)
        counter_not_mapped += 1
    print('number of diseases which mapped:', counter_map)
    print('number of diseases which not mapped:', counter_not_mapped)


def generate_cypher_file():
    dict_label_to_tsv_mapping = {}
    # new file
    file_name_new = 'disease/new.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_writer_new = csv.writer(file_new, delimiter='\t')
    csv_writer_new.writerow(['pharmgkb_id', 'xrefs'])
    cypher_file = open('output/cypher.cypher', 'a')

    for label in ["Disease", "Symptom", "SideEffect"]:
        # tsv_file
        file_name = 'disease/mapping_' + label + '.tsv'
        file = open(file_name, 'w', encoding='utf-8')
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(['disease_id', 'pharmgkb_id', 'resource', 'how_mapped', 'xrefs'])
        dict_label_to_tsv_mapping[label] = csv_writer
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:PharmGKB_Phenotype{id:line.pharmgkb_id}), (c:%s{identifier:line.disease_id})   Set c.pharmgkb='yes', c.xrefs=split(line.xrefs,"|"),  c.resource=split(line.resource,'|') Create (c)-[:equal_to_disease_pharmgkb{how_mapped:line.how_mapped}]->(n); \n'''

        query = query % (file_name, label)
        cypher_file.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:PharmGKB_Phenotype{id:line.pharmgkb_id}) Create (c:Phenotype{identifier:line.pharmgkb_id, name:n.name, synonyms:n.alternate_names ,xrefs:split(line.xrefs,'|'), source:"PharmGKB", url:'https://www.pharmgkb.org/disease/'+line.pharmgkb_id , license:"%s", pharmgkb:'yes', resource:['PharmGKB']})  Create (c)-[:equal_to_disease_pharmgkb{how_mapped:'new'}]->(n); \n'''

    query = query % (file_name_new, license)
    cypher_file.write(query)
    cypher_file.close()
    return dict_label_to_tsv_mapping, csv_writer_new


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license')

    print(datetime.datetime.now())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in disease and symptom from hetionet')

    load_db_nodes_in('Disease', dict_disease_to_resource, dict_disease_name_to_disease_id,
                     dict_xrefs_to_dict_xref_to_disease, dict_disease_to_xrefs)

    load_db_nodes_in('Symptom', dict_symptom_to_resource, dict_symptom_name_to_symptom_id,
                     dict_xrefs_to_dict_xref_to_symptom, dict_symptom_to_xrefs)

    load_db_nodes_in('SideEffect', dict_se_to_resource, dict_se_name_to_se_id,
                     dict_xrefs_to_dict_xref_to_se, dict_se_to_xrefs, identifier_umls=True)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in disease from pharmgb in')

    load_pharmgkb_phenotypes_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
