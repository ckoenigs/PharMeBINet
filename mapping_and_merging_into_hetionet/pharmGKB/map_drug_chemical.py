import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


def create_connection_with_neo4j_and_mysql():
    """
    create connection to neo4j  and mysql
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


# dictionary of all chemical ids to resource
dict_chemical_to_resource = {}

# dictionary inchi to chemical id
dict_inchi_to_chemical_id = {}

# dictionary_pubchem_compound to chemical id
dict_pubchem_compound_to_chemical_id = {}

# dictionary rxnorm cui to chemical id
dict_rxcui_to_chemical_id = {}

# dictionary name to chemical id
dict_name_to_chemical_id = {}

# dictionary name to pharmacological class ids
dict_name_to_pharmacologic_class = {}

# dictionary identifier to pharmacological class ids
dict_identifier_to_pharmacologic_class = {}

# dictionary pharmacological class id to resource
dict_pc_to_resource = {}

# dict_atc_to_pc ids
dict_atc_to_pc = {}


def add_value_to_dictionary(dictionary, key, value):
    """
    add key to dictionary if not existing and add value to set
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def load_pharmacological_class():
    """
    load pharmacological information
    :return:
    """
    query = '''Match (n:PharmacologicClass) Return n.identifier, n.name, n.synonyms, n.resource, n.atc_codes '''

    for record in g.run(query):
        [identifier, name, synonyms, resource, atc_codes] = record.values()
        dict_pc_to_resource[identifier] = resource
        dict_identifier_to_pharmacologic_class[identifier] = identifier
        if atc_codes:
            for atc_code in atc_codes:
                add_value_to_dictionary(dict_atc_to_pc, atc_code, identifier)

        if name:
            name = name.lower()
            add_value_to_dictionary(dict_name_to_pharmacologic_class, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                add_value_to_dictionary(dict_name_to_pharmacologic_class, synonym, identifier)


# dictionary compound id to xrefs
dict_compound_id_to_xrefs = {}

# dictionary compound id to names
dict_compound_id_to_names = {}

# dictionary compound to salt ids
dict_compound_id_to_salts_id = {}

# dictionary mesh and drugbank id to chemical id
dict_mesh_db_id_to_chemical_id = {}

# dictionary from alternative drugbank id to identifier
dict_alter_id_to_id = {}

'''
load in all compound from pharmebinet in a dictionary
'''


def load_db_info_in():
    """
    Load chemical and write information into dictionaries
    :return:
    """
    query = '''MATCH (n:Chemical)  RETURN n.identifier,n.inchi, n.xrefs, n.resource, n.name, n.synonyms, n.alternative_ids'''
    results = g.run(query)

    for record in results:
        [identifier, inchi, xrefs, resource, name, synonyms, alternative_drug_ids] = record.values()
        dict_chemical_to_resource[identifier] = resource if resource else []
        dict_mesh_db_id_to_chemical_id[identifier] = set([identifier])
        if inchi:
            dict_inchi_to_chemical_id[inchi] = identifier
        xrefs = set(xrefs) if xrefs else set()
        dict_compound_id_to_xrefs[identifier] = xrefs
        if xrefs:
            for xref in xrefs:
                value = xref.split(':', 1)[1]
                if xref.startswith('PubChem Compound'):
                    add_value_to_dictionary(dict_pubchem_compound_to_chemical_id, value, identifier)
                elif xref.startswith('RxNorm_CUI'):
                    add_value_to_dictionary(dict_rxcui_to_chemical_id, value, identifier)
                elif xref.startswith('MESH'):
                    add_value_to_dictionary(dict_mesh_db_id_to_chemical_id, value, identifier)

        dict_compound_id_to_names[identifier] = set()
        if name:
            name = name.lower()
            dict_compound_id_to_names[identifier].add(name)
            add_value_to_dictionary(dict_name_to_chemical_id, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_compound_id_to_names[identifier].add(synonym)
                add_value_to_dictionary(dict_name_to_chemical_id, synonym, identifier)

        if alternative_drug_ids:
            for alt_db_id in alternative_drug_ids:
                add_value_to_dictionary(dict_alter_id_to_id, alt_db_id, identifier)

    query = '''MATCH (n:Chemical)--(m:Salt) RETURN n.identifier, m.identifier'''
    results = g.run(query)
    for record in results:
        [compound_id, salt_id] = record.values()
        if compound_id not in dict_compound_id_to_salts_id:
            dict_compound_id_to_salts_id[compound_id] = set()
        dict_compound_id_to_salts_id[compound_id].add(salt_id)

    print('length of chemical in db:' + str(len(dict_chemical_to_resource)))


def add_information_to_file(drugbank_id, identifier, csv_writer, how_mapped, tuple_set, dict_to_resource, xref=set()):
    """
    add mapper to file if not already is added!
    :param drugbank_id:
    :param identifier:
    :param csv_writer:
    :param how_mapped:
    :param tuple_set:
    :return:
    """
    if (drugbank_id, identifier) in tuple_set:
        return
    tuple_set.add((drugbank_id, identifier))
    xref.add('PharmGKB:' + identifier)
    xrefs = '|'.join(go_through_xrefs_and_change_if_needed_source_name(xref, 'chemical'))
    csv_writer.writerow(
        [drugbank_id, identifier, pharmebinetutils.resource_add_and_prepare(dict_to_resource[drugbank_id], 'PharmGKB'),
         how_mapped, xrefs])


def check_if_name_are_correct_or_with_salt(name, drugbank_id):
    """
    check if the name is fitting to drugbank id or to there salt if no mapping exists use the existing drugbank id 
    :param name: string
    :param drugbank_id: string 
    :return: set of drugbank ids
    """
    drugbank_ids = set([drugbank_id])
    if name in dict_name_to_chemical_id:
        chemical_ids = dict_name_to_chemical_id[name]
        if drugbank_id not in chemical_ids:
            if drugbank_id in dict_compound_id_to_salts_id:
                salts = dict_compound_id_to_salts_id[drugbank_id]
                if len(salts.intersection(chemical_ids)) > 0:
                    drugbank_ids = salts.intersection(chemical_ids)
    return drugbank_ids


def load_pharmgkb_in(label):
    """
    generate mapping file and cypher file for a given label
    map nodes to chemical
    :param label: string
    :return:
    """

    # tsv_file
    file_name = 'chemical/mapping_' + label.split('_')[1] + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier', 'pharmgkb_id', 'resource', 'how_mapped', 'xrefs'])
    generate_cypher_file(file_name, label, 'Chemical')

    # tsv file pharmacological file
    file_name_pc = 'chemical/mapping_pharmacological_class_' + label.split('_')[1] + '.tsv'
    file_pc = open(file_name_pc, 'w', encoding='utf-8')
    csv_writer_pc = csv.writer(file_pc, delimiter='\t')
    csv_writer_pc.writerow(['identifier', 'pharmgkb_id', 'resource', 'how_mapped'])
    generate_cypher_file(file_name_pc, label, 'PharmacologicClass')

    not_mapped_file = open('chemical/not_mapping_' + label.split('_')[1] + '.tsv', 'w', encoding='utf-8')
    csv_writer_not = csv.writer(not_mapped_file, delimiter='\t')
    csv_writer_not.writerow(['pharmgkb_id', 'namr'])
    # generate cypher file

    query = '''MATCH (n:%s) RETURN n'''
    query = query % (label)
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    # set of all tuples
    set_of_all_tuples = set()

    # set of all tuple to pc
    set_of_all_tuples_with_pc = set()

    for record in results:
        result = record.data()['n']
        identifier = result['id']

        mapped = False
        inchi = result['inchi'] if 'inchi' in result else ''
        name = result['name'].lower() if 'name' in result else ''
        types = result['types'] if 'types' in result else []

        if inchi in dict_inchi_to_chemical_id:
            mapped = True
            counter_map += 1
            add_information_to_file(dict_inchi_to_chemical_id[inchi], identifier, csv_writer, 'inchi',
                                    set_of_all_tuples, dict_chemical_to_resource,
                                    xref=dict_compound_id_to_xrefs[dict_inchi_to_chemical_id[inchi]])

        if mapped:
            continue

        cross_references = result['cross_references'] if 'cross_references' in result else []
        for cross_reference in cross_references:
            value = cross_reference.split(':', 1)[1]
            if cross_reference.startswith('DrugBank'):
                if value in dict_chemical_to_resource:
                    drugbank_ids = set([value])
                    if name != '':
                        drugbank_ids = check_if_name_are_correct_or_with_salt(name, value)
                    mapped = True
                    for drugbank_id in drugbank_ids:
                        add_information_to_file(drugbank_id, identifier, csv_writer, 'drugbank', set_of_all_tuples,
                                                dict_chemical_to_resource, xref=dict_compound_id_to_xrefs[drugbank_id])
                # elif value in dict_alter_id_to_id:
                #     drugbank_ids = dict_alter_id_to_id[value]
                #     mapped = True
                #     for drugbank_id in drugbank_ids:
                #         add_information_to_file(drugbank_id, identifier, csv_writer, 'drugbank_alternativ', set_of_all_tuples,
                #                                 dict_chemical_to_resource, xref=dict_compound_id_to_xrefs[drugbank_id])

        external_references = result['external_vocabulary'] if 'external_vocabulary' in result else []
        for xref in external_references:
            value = xref.split(':')[1].split('(')[0]
            if xref.startswith('NDFRT'):
                if value in dict_identifier_to_pharmacologic_class and 'Drug Class' in types:
                    mapped = True
                    add_information_to_file(value, identifier, csv_writer_pc, 'ndf-rt', set_of_all_tuples_with_pc,
                                            dict_pc_to_resource)

        if mapped:
            counter_map += 1
            continue

        pubchem_compound_identifiers = result[
            'pubchem_compound_identifiers'] if 'pubchem_compound_identifiers' in result else []
        for pubchem_compound_identifier in pubchem_compound_identifiers:
            if pubchem_compound_identifier in dict_pubchem_compound_to_chemical_id:
                mapped = True
                counter_map += 1
                for drugbank_id in dict_pubchem_compound_to_chemical_id[pubchem_compound_identifier]:
                    drugbank_ids = set([drugbank_id])
                    if name != '':
                        drugbank_ids = check_if_name_are_correct_or_with_salt(name, drugbank_id)
                    mapped = True
                    for db_id in drugbank_ids:
                        add_information_to_file(db_id, identifier, csv_writer, 'pubchem compound', set_of_all_tuples,
                                                dict_chemical_to_resource, xref=dict_compound_id_to_xrefs[db_id])
        # if mapped:
        #     continue
        #
        # rxnorm_identfiers = result[
        #     'rxnorm_identifiers'] if 'rxnorm_identifiers' in result else []
        # for rxnorm_identfier in rxnorm_identfiers:
        #     if rxnorm_identfier in dict_rxcui_to_chemical_id:
        #         mapped = True
        #         counter_map += 1
        #         for drugbank_id in dict_rxcui_to_chemical_id[rxnorm_identfier]:
        #             drugbank_ids = set([drugbank_id])
        #             if name != '':
        #                 drugbank_ids = check_if_name_are_correct_or_with_salt(name, drugbank_id)
        #             mapped = True
        #             for db_id in drugbank_ids:
        #                 add_information_to_file(db_id, identifier, csv_writer, 'rxcui',
        #                                         set_of_all_tuples,
        #                                         dict_chemical_to_resource, xref=dict_compound_id_to_xrefs[db_id])

        if mapped:
            continue

        if identifier in dict_chemical_to_resource:
            mapped = True
            add_information_to_file(identifier, identifier, csv_writer, 'mesh', set_of_all_tuples,
                                    dict_chemical_to_resource, xref=dict_compound_id_to_xrefs[identifier])

        if mapped:
            continue

        if len(name) > 0:
            if name in dict_name_to_chemical_id:
                mapped = True
                counter_map += 1
                for drugbank_id in dict_name_to_chemical_id[name]:
                    add_information_to_file(drugbank_id, identifier, csv_writer, 'name',
                                            set_of_all_tuples, dict_chemical_to_resource,
                                            xref=dict_compound_id_to_xrefs[drugbank_id])
        if mapped:
            continue

        # atc_codes = result[
        #     'atc_identifiers'] if 'atc_identifiers' in result else []
        # if 'Drug Class' in types:
        #     # only consider the one with only one atc code!
        #     if len(atc_codes)==1:
        #         for atc_code in atc_codes:
        #             if atc_code in dict_atc_to_pc:
        #                 mapped = True
        #                 counter_map += 1
        #                 for pharmacological_class_id in dict_atc_to_pc[atc_code]:
        #                     add_information_to_file(pharmacological_class_id, identifier, csv_writer_pc, 'atc',
        #                                             set_of_all_tuples_with_pc, dict_pc_to_resource)
        #
        # if mapped:
        #     continue

        if len(name) > 0 and types and 'Drug Class' in types:
            if name in dict_name_to_pharmacologic_class:
                mapped = True
                counter_map += 1
                for pharmacological_class_id in dict_name_to_pharmacologic_class[name]:
                    add_information_to_file(pharmacological_class_id, identifier, csv_writer_pc, 'name',
                                            set_of_all_tuples_with_pc, dict_pc_to_resource)

        if mapped:
            continue

        generic_names = result['generic_names'] if 'generic_names' in result else []
        if generic_names:
            for generic_name in generic_names:
                if generic_name in dict_name_to_chemical_id:
                    mapped = True
                    counter_map += 1
                    for drugbank_id in dict_name_to_chemical_id[generic_name]:
                        add_information_to_file(drugbank_id, identifier, csv_writer, 'generic_name',
                                                set_of_all_tuples, dict_chemical_to_resource,
                                                xref=dict_compound_id_to_xrefs[drugbank_id])
        if mapped:
            continue

        if len(name) > 0:
            name = name.lower()
            cur = con.cursor()
            # if not mapped map the name to umls cui
            query = ('Select Distinct CUI From MRCONSO Where STR= "%s";')
            query = query % (name.replace('"', '\''))
            # print(query)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                cuis = set()
                for (cui,) in cur:
                    cuis.add(cui)

                cur2 = con.cursor()
                # if not mapped map the name to umls cui
                query = (
                    'Select Distinct CODE, SAB From MRCONSO Where CUI in ("%s") and (SAB="MSH" or SAB="DRUGBANK");')
                query = query % ('","'.join(cuis))
                rows_counter = cur2.execute(query)
                if rows_counter > 0:
                    for (code, sab) in cur2:
                        if code in dict_mesh_db_id_to_chemical_id:
                            for chemical_id in dict_mesh_db_id_to_chemical_id[code]:
                                mapped = True
                                add_information_to_file(chemical_id, identifier, csv_writer,
                                                        'umls over mesh and drugbank', set_of_all_tuples,
                                                        dict_chemical_to_resource,
                                                        xref=dict_compound_id_to_xrefs[chemical_id])

        if not mapped:
            counter_not_mapped += 1
            csv_writer_not.writerow([identifier, result['name'], types])
        else:
            counter_map += 1

    print('number of chemical/drug which mapped:', counter_map)
    print('number of mapped:', len(set_of_all_tuples) + len(set_of_all_tuples_with_pc))
    print('mapped with pc:', len(set_of_all_tuples_with_pc))
    print('number of chemical/drug which not mapped:', counter_not_mapped)


def generate_cypher_file(file_name, label, to_label):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    if to_label == 'Chemical':
        extra_string = ', c.xrefs=split(line.xrefs,"|") '
    else:
        extra_string = ''
    cypher_file = open('output/cypher.cypher', 'a')
    query = '''  MATCH (n:%s{id:line.pharmgkb_id}), (c:%s{identifier:line.identifier})  Set c.pharmgkb='yes', c.resource=split(line.resource,'|') %s Create (c)-[:equal_to_%s_phamrgkb{how_mapped:line.how_mapped}]->(n)'''
    query = query % (label, to_label, extra_string, label.split('_')[1].lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j_and_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in chemical from pharmebinet')

    load_db_info_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in pharmacological class from pharmebinet')

    load_pharmacological_class()

    for label in ['PharmGKB_Chemical']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Load in %s from pharmgb in' % (label))

        load_pharmgkb_in(label)

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
