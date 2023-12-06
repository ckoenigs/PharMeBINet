import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


def create_connection_with_neo4j_mysql():
    """
    create connection to neo4j and mysql
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = create_connection_to_databases.database_connection_RxNorm()


# dictionary rxcui to drugbank ids
dict_rxcui_to_Drugbank_with_xref = {}
# dictionary name/synonym to chemical ids
dict_name_to_chemical_ids = {}
# dictionary with all compounds with id as key and [resource, xrefs]
dict_chemical_id_to_resource_xrefs = {}


def load_compounds_from_pharmebinet():
    """
    load in all compounds from pharmebinet in dictionary
    properties:
        license
        identifier
        inchikey
        inchi
        name
        source
        url
    :return:
    """
    query = 'MATCH (n:Chemical) RETURN n.identifier, n.inchikey, n.inchi, n.name, n.resource, n.xrefs, n.synonyms '
    results = g.run(query)

    for record in results:
        [identifier, inchikey, inchi, name, resource, xrefs, synonyms] = record.values()
        inchikey = inchikey if inchikey else ''
        inchi = inchi if inchi else ''
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids, name.lower(), identifier)
        xrefs = xrefs if xrefs else []
        for xref in xrefs:
            if xref.startswith('RxNorm_CUI'):
                rxcui = xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_rxcui_to_Drugbank_with_xref, rxcui, identifier)
        dict_chemical_id_to_resource_xrefs[identifier] = [resource, set(xrefs)]

        if synonyms:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids, synonym.lower(), identifier)

    print('In pharmebinet:' + str(len(dict_chemical_id_to_resource_xrefs)) + ' drugs')


def search_for_mapping_in_rxnorm(sab, rxnorm_id, drug_concept_id, name, mapping_string):
    """
    Search in RxNorm for mapping
    :param sab:
    :param rxnorm_id:
    :param mapping_string
    :param drug_concept_id:
    :return:
    """
    cur = conRxNorm.cursor()
    query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = '%s' and RXCUI= '%s' ;")
    query = query % (sab, rxnorm_id)
    rows_counter = cur.execute(query)
    found_a_mapping = False
    if rows_counter > 0:
        # check if they are drugbank ids where the name is the same as in aeolus
        for (rxcui, lat, code, sab, label,) in cur:
            label = label.lower()
            if code in dict_chemical_id_to_resource_xrefs:
                xrefs = dict_chemical_id_to_resource_xrefs[code][1]
                xrefs.add('RxNorm_CUI:' + rxcui)
                found_a_mapping = True
                if label == name:
                    if not (drug_concept_id, code) in set_of_mapping_pairs:
                        set_of_mapping_pairs.add((drug_concept_id, code))
                        csv_writer.writerow([drug_concept_id, code, mapping_string + '_and_same_name',
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_chemical_id_to_resource_xrefs[code][0], "AEOLUS"),
                                             '|'.join(
                                                 go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical'))])
                else:
                    if not (drug_concept_id, code) in set_of_mapping_pairs:
                        set_of_mapping_pairs.add((drug_concept_id, code))
                        csv_writer.writerow([drug_concept_id, code, mapping_string,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_chemical_id_to_resource_xrefs[code][0], "AEOLUS"),
                                             '|'.join(
                                                 go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical'))])

    return found_a_mapping


# dictionaries for rxnorm and unii mapping preparation
dict_rxcuis_to_drugbank_id_generate_with_external_source = {}
dict_rxcuis_to_drugbank_id_generate_with_external_source_name = {}


def load_mapping_information_from_tsv_to_dictionary(file_name, dictionary):
    """
        load rxcui-drugbank id table from tsv file and prepare dictionary
        properties:
            0:rxcui
            1:drugbank ids separated with |
        :return:
        """
    f = open(file_name, 'r',
             encoding='utf-8')
    csv_reader = csv.reader(f, delimiter='\t')
    next(csv_reader)
    for line in csv_reader:
        rxnorm_id = line[0]
        drugbank_ids = line[1].split('|')
        if rxnorm_id not in dictionary:
            dictionary[rxnorm_id] = set(drugbank_ids)
        else:
            dictionary[rxnorm_id] = dictionary[rxnorm_id].union(drugbank_ids)
    f.close()


# tsv for mapped aeolus pairs
file = open('drug/mapped.tsv', 'w', encoding='utf-8')
csv_writer = csv.writer(file, delimiter='\t')
header = ['aeolus_id', 'chemical_id', 'how_mapped', 'resource', 'xrefs']
csv_writer.writerow(header)

# set of mapping pairs
set_of_mapping_pairs=set()

# dictionary manual mapped nodes
dict_manual_mapped_nodes={
    '19135934':'DBSALT002460',
    '19097468':'DBSALT002762'
}


def load_drug_aeolus_in_dictionary():
    """
    load a part of aeolus drugs, which are not integrated, in a dictionary and set the property integrated='yes'
has properties:
    vocabulary_id: defined the type of the concept_code
    name
    drug_concept_id: OHDSI ID
    concept_code: RxNorm CUI
    :return:
    """
    query = '''MATCH (n:Aeolus_Drug)  RETURN n'''
    counter = 0
    counter_not_mapped = 0

    results = g.run(query)
    for record in results:
        counter += 1
        result = record.data()['n']
        if result['vocabulary_id'] != 'RxNorm':
            print('ohje')
        rxcui = result['concept_code']
        drug_concept_id = result['drug_concept_id']
        name = result['name'].lower()

        found_mapping = False
        if rxcui in dict_rxcui_to_Drugbank_with_xref:
            found_mapping = True
            for chemical_id in dict_rxcui_to_Drugbank_with_xref[rxcui]:
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    csv_writer.writerow([drug_concept_id, chemical_id, 'map_rxcui_with_xref',
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_chemical_id_to_resource_xrefs[chemical_id][0], "AEOLUS"),
                                         '|'.join(go_through_xrefs_and_change_if_needed_source_name(
                                             dict_chemical_id_to_resource_xrefs[chemical_id][1], 'chemical'))])

        if found_mapping:
            continue

        if drug_concept_id in dict_manual_mapped_nodes:
            found_mapping = True
            chemical_id=dict_manual_mapped_nodes[drug_concept_id]
            if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                csv_writer.writerow([drug_concept_id, chemical_id, 'manual_mapped',
                                     pharmebinetutils.resource_add_and_prepare(
                                         dict_chemical_id_to_resource_xrefs[chemical_id][0], "AEOLUS"),
                                     '|'.join(go_through_xrefs_and_change_if_needed_source_name(
                                         dict_chemical_id_to_resource_xrefs[chemical_id][1], 'chemical'))])

        if found_mapping:
            continue

        found_mapping = search_for_mapping_in_rxnorm('DRUGBANK', rxcui, drug_concept_id, name, 'rxcui_map_to_drugbank')

        if found_mapping:
            continue

        if rxcui in dict_rxcuis_to_drugbank_id_generate_with_external_source:
            found_mapping = True
            for chemical_id in dict_rxcuis_to_drugbank_id_generate_with_external_source[rxcui]:
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    xrefs = dict_chemical_id_to_resource_xrefs[chemical_id][1]
                    xrefs.add('RxNorm_CUI:' + rxcui)
                    csv_writer.writerow(
                        [drug_concept_id, chemical_id, 'map_rxnorm_to_drugbank_with_use_of_dhimmel_inchikey_and_unii',
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_xrefs[chemical_id][0], "AEOLUS"),
                         '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical'))])

        if found_mapping:
            continue

        if rxcui in dict_rxcuis_to_drugbank_id_generate_with_external_source_name:
            found_mapping = True
            for chemical_id in dict_rxcuis_to_drugbank_id_generate_with_external_source_name[rxcui]:
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    xrefs = dict_chemical_id_to_resource_xrefs[chemical_id][1]
                    xrefs.add('RxNorm_CUI:' + rxcui)
                    csv_writer.writerow(
                        [drug_concept_id, chemical_id, 'map_rxnorm_to_drugbank_with_use_of_name_mapping',
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_xrefs[chemical_id][0], "AEOLUS"),
                         '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical'))])

        if found_mapping:
            continue

        found_mapping = search_for_mapping_in_rxnorm('MSH', rxcui, drug_concept_id, name, 'rxcui_map_to_MESH')

        if found_mapping:
            continue

        if name in dict_name_to_chemical_ids:
            found_mapping = True
            for chemical_id in dict_name_to_chemical_ids[name]:
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    xrefs = dict_chemical_id_to_resource_xrefs[chemical_id][1]
                    xrefs.add('RxNorm_CUI:' + rxcui)
                    csv_writer.writerow(
                        [drug_concept_id, chemical_id, 'name_mapping',
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_xrefs[chemical_id][0], "AEOLUS"),
                         '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical'))])

        if found_mapping:
            continue

        counter_not_mapped += 1

    print('number of nodes in aeolus', counter)
    print('number of not mapped nodes in aeolus', counter_not_mapped)


def generate_cypher_file():
    """
    Generate cypher file to update or create the relationships in pharmebinet
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = ''' Match (a:Aeolus_Drug{drug_concept_id:line.aeolus_id}),(n:Chemical{identifier:line.chemical_id}) Set   n.aeolus="yes",n.resource= split(line.resource,'|') , n.xrefs=split(line.xrefs,'|') Create (n)-[:equal_to_Aeolus_drug{how_mapped:line.how_mapped}]->(a)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/aeolus/drug/mapped.tsv', query)
    cypher_file.write(query)

    cypher_file.close()


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
    print('Load in all drugs from pharmebinet (+Sider) in a dictionary')

    load_compounds_from_pharmebinet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('prepare mapping table')

    # load rxcui-drugbank id table with inchikeys and unii idea form himmelstein
    load_mapping_information_from_tsv_to_dictionary(
        '../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv',
        dict_rxcuis_to_drugbank_id_generate_with_external_source)

    load_mapping_information_from_tsv_to_dictionary(
        '../RxNorm_to_DrugBank/results/name_map_drugbank_to_rxnorm.tsv',
        dict_rxcuis_to_drugbank_id_generate_with_external_source_name)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all drugs from aeolus map them to chemical')

    load_drug_aeolus_in_dictionary()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Generate cypher')

    generate_cypher_file()

    driver.close()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
