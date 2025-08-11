import csv
import sys
import datetime
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary name to ids
dict_name_to_id = defaultdict(set)

# dictionary synonyms to ids
dict_synonyms_to_id = defaultdict(set)

# dictionary chebi to ids
dict_chebi_to_id = defaultdict(set)

# dictionary inchikey to ids
dict_inchikey_to_id = defaultdict(set)

# dictionary_identifier_to_inchikey
dict_identifier_to_inchikey = {}

# dictionary chemical to salt information
dict_chemical_to_salts = {}

# dictionary chemical id to name
dict_chemical_id_to_name = {}


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.synonyms, n.resource, n.xrefs, n.inchikey, n.formula'''
    results = g.run(query)

    for identifier, name, synonyms, resource, xrefs, inchikey, formula, in results:
        xrefs = set(xrefs) if xrefs else set()
        dict_node_id_to_resource[identifier] = [resource, xrefs, formula]

        name = name.lower()
        dict_name_to_id[name].add(identifier)

        dict_chemical_id_to_name[identifier] = name

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_synonyms_to_id[synonym].add(identifier)

        if inchikey:
            dict_identifier_to_inchikey[identifier] = inchikey
            dict_inchikey_to_id[inchikey].add(identifier)

        for xref in xrefs:
            if xref.startswith('ChEBI'):
                dict_chebi_to_id[xref.split(':')[1]].add(identifier)

    query = '''Match (n:Chemical)-[:PART_OF_CpoSA]-(m:Salt) Return n.identifier, m.identifier'''
    for chemical_id, salt_id, in g.run(query):
        if not chemical_id in dict_chemical_to_salts:
            dict_chemical_to_salts[chemical_id] = set()
        dict_chemical_to_salts[chemical_id].add(salt_id)

    print('number of Chemical in database', len(dict_node_id_to_resource))


def prepare_query(file_name):
    """
    prepare query fro integration
    :param file_name:string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = '''MATCH (n:Chemical{identifier:line.db_id}), (g:Chemical_ChebiOntology{id:line.node_id}) Set n.resource=split(line.resource,"|"), n.xrefs=split(line.xrefs,"|"), n.chebi='yes', n.inchi = coalesce(n.inchi, line.inchi),  n.inchikey = coalesce(n.inchikey, line.inchikey),  n.smiles = coalesce(n.smiles, line.smiles) Create (n)-[:equal_chebi_chemical{how_mapped:line.how_mapped}]->(g)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/chebi/{file_name}',
                                              query)
    cypher_file.write(query)


def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id, csv_mapping, how_mapped, dict_property):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    dict_node_id_to_resource[identifier_db][1].add(identifier_act_id)
    xrefs = go_through_xrefs_and_change_if_needed_source_name(dict_node_id_to_resource[identifier_db][1], 'chemical')
    inchi = dict_property['inchi'] if 'inchi' in dict_property else ''
    inchikey = dict_property['inchikey'] if 'inchikey' in dict_property else ''
    smiles = dict_property['smiles'] if 'smiles' in dict_property else ''
    csv_mapping.writerow(
        [identifier_db, identifier_act_id,
         pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier_db][0], "ChEBI"),
         how_mapped, '|'.join(xrefs), inchi, inchikey, smiles])


# dictionary chebi to drugbank manual
dict_manual_mapping = {
    # "CHEBI:51025": "DBSALT000602",
    # "CHEBI:51161": "DBSALT000549",
    "CHEBI:9216": "DBSALT000380",
    "CHEBI:9702": "DBSALT002739",
    "CHEBI:108":"91572",
}


def get_all_chebi_and_map(dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = 'output/mapping_chemical.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8', newline='')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    # ['monoisotopicmass',  'charge',  'mass', 'smiles', 'formula']
    csv_mapping.writerow(['db_id', 'node_id', 'resource', 'how_mapped', 'xrefs', 'inchi', 'inchikey', 'smiles'])

    prepare_query(file_name)

    # get data
    query = '''MATCH (n:Chemical_ChebiOntology)   RETURN n.id, n.name, n.synonyms, n.property_values, n.xrefs'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    set_of_all_possible_properties = set()
    for identifier, name, synonyms, property_values, xrefs, in results:
        only_number_id = identifier.split(':')[1]

        name = name.lower()

        is_mapped = False

        dict_property_to_value = {}
        bool_formular_and_inchi_formular_equal = True
        if property_values:
            for value in property_values:
                value = value.replace('" xsd:string', '')
                key_value_pair = value.split(' "')
                dict_property_to_value[key_value_pair[0].replace('http://purl.obolibrary.org/obo/chebi/', '')] = \
                    key_value_pair[1]
            set_of_all_possible_properties = set_of_all_possible_properties.union(dict_property_to_value.keys())

            if 'inchi' in dict_property_to_value and 'formula' in dict_property_to_value:
                inchi = dict_property_to_value['inchi']
                if inchi.split('/')[1] != dict_property_to_value['formula']:
                    # print('different')
                    bool_formular_and_inchi_formular_equal = False
            # elif 'inchi' in dict_property_to_value:
            #     print('only one')
            # elif 'formula' in dict_property_to_value:
            #     print('only one')

            if 'inchikey' in dict_property_to_value:
                if dict_property_to_value['inchikey'] in dict_inchikey_to_id:
                    is_mapped = True
                    counter_mapping += 1
                    for chemical_id in dict_inchikey_to_id[dict_property_to_value['inchikey']]:
                        add_to_file(dict_node_id_to_resource, chemical_id, identifier, csv_mapping, 'inchikey',
                                    dict_property_to_value)

        if is_mapped:
            continue

        if name in dict_name_to_id:
            is_mapped = True
            counter_mapping += 1
            for drugbank_id in dict_name_to_id[name]:
                if 'inchikey' in dict_property_to_value and drugbank_id in dict_identifier_to_inchikey:
                    start_chebi_inchikey = dict_property_to_value['inchikey'].split('-')[0]
                    start_pharmebinet_inchikey = dict_identifier_to_inchikey[drugbank_id].split('-')[0]
                    if start_pharmebinet_inchikey == start_chebi_inchikey:
                        add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping,
                                    'name_and_part_inchikey_mapping', dict_property_to_value)
                        continue
                    else:
                        print(identifier, drugbank_id)
                        print('different inchikeys', start_pharmebinet_inchikey, start_chebi_inchikey)
                        continue
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'name_mapping',
                            dict_property_to_value)

        if is_mapped:
            continue

        if name in dict_synonyms_to_id:
            found_real_mapping = False
            for drugbank_id in dict_synonyms_to_id[name]:
                if 'inchikey' in dict_property_to_value and drugbank_id in dict_identifier_to_inchikey and bool_formular_and_inchi_formular_equal:
                    start_chebi_inchikey = dict_property_to_value['inchikey'].split('-')[0]
                    start_pharmebinet_inchikey = dict_identifier_to_inchikey[drugbank_id].split('-')[0]
                    if start_pharmebinet_inchikey == start_chebi_inchikey:
                        formula_pmbin = dict_node_id_to_resource[drugbank_id][2]
                        if 'formula' in dict_property_to_value:
                            if dict_property_to_value['formula'] != formula_pmbin:
                                print('different', formula_pmbin, dict_property_to_value['formula'])
                                continue
                        found_real_mapping = True
                        add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping,
                                    'synonym_and_part_inchikey_mapping', dict_property_to_value)
                        continue
                    else:
                        print(identifier, drugbank_id)
                        print('different inchikeys', start_pharmebinet_inchikey, start_chebi_inchikey)
                        continue
                # CHEBI:15693 is a general name for suger molecules and this happened to be in some synonyms
                if drugbank_id.startswith('DB') or (
                not (drugbank_id.startswith('D') or drugbank_id.startswith('C'))) and identifier not in ['CHEBI:15693']:
                    found_real_mapping = True
                    add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'synonyms_mapping',
                                dict_property_to_value)
            if found_real_mapping:
                is_mapped = True
                counter_mapping += 1

        if is_mapped:
            continue

        if identifier in dict_manual_mapping:
            counter_mapping += 1
            drugbank_id = dict_manual_mapping[identifier]
            is_mapped = True
            add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'manual mapping',
                        dict_property_to_value)

        if is_mapped:
            continue

        # CHEBI:87818 map but is a salt form
        # CHEBI:57398 maps completely wrong
        # CHEBI:15851 wrong position of N
        # CHEBI:3079 maps completely wrong
        # CHEBI:25979 maps completely wrong
        # "CHEBI:28272" a bit different
        # CHEBI:53786 not the right salt
        # "CHEBI:9704" not the right salt
        # "CHEBI:51030" "
        # "CHEBI:64194" "
        # "CHEBI:50240" "
        # "CHEBI:31332" "
        # "CHEBI:50894" "
        set_wrong_ids_with_xrefs = {'CHEBI:87818', 'CHEBI:57398', 'CHEBI:15851', 'CHEBI:3079', 'CHEBI:25979',
                                    "CHEBI:28272", "CHEBI:53786", "CHEBI:9704", "CHEBI:51030", "CHEBI:64194",
                                    "CHEBI:50240", "CHEBI:31332", "CHEBI:50894"}
        if xrefs and not identifier in set_wrong_ids_with_xrefs:
            for xref in xrefs:
                if xref.startswith('DrugBank:'):
                    db_id = xref.split(':')[1]
                    if db_id in dict_node_id_to_resource:
                        split_name = name.split(' ')
                        chemical_name_split = dict_chemical_id_to_name[db_id].split(' ')
                        if len(split_name) == 1 or len(split_name) == len(chemical_name_split):
                            is_mapped = True
                            counter_mapping += 1
                            add_to_file(dict_node_id_to_resource, db_id, identifier, csv_mapping, 'drugbank_xref',
                                        dict_property_to_value)
                        else:
                            if db_id in dict_chemical_to_salts:
                                for salt_id in dict_chemical_to_salts[db_id]:
                                    salt_name = dict_chemical_id_to_name[salt_id].split(' ')
                                    found_equal = False
                                    for split in split_name:
                                        if split in salt_name:
                                            found_equal = True
                                    if found_equal and len(split_name) == len(salt_name):
                                        is_mapped = True
                                        counter_mapping += 1
                                        add_to_file(dict_node_id_to_resource, salt_id, identifier, csv_mapping,
                                                    'drugbank_xref_salt',
                                                    dict_property_to_value)
                        if not is_mapped:
                            print('xref drugbank id did not mapped', xref)

        if is_mapped:
            continue

        if only_number_id in dict_chebi_to_id:
            is_mapped = True
            counter_mapping += 1
            for chemical_id in dict_chebi_to_id[only_number_id]:
                add_to_file(dict_node_id_to_resource, chemical_id, identifier, csv_mapping, 'chebi',
                            dict_property_to_value)

        if not is_mapped:
            counter_not_mapped += 1
            # print(' not in database :O')
            # print(identifier, name)
    print(set_of_all_possible_properties)
    print('mapped:', counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path chebi')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')

    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all drugs from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_chebi_and_map(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
