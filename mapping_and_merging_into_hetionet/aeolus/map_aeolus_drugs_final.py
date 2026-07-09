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

    # generate connection to mysql to RxNorm database
    global con_umls
    con_umls = create_connection_to_databases.database_connection_umls()


# dictionary rxcui to drugbank ids
dict_rxcui_to_Drugbank_with_xref = {}
# dictionary name/synonym to chemical ids
dict_name_to_chemical_ids = {}
# dictionary with all compounds with id as key and [resource, xrefs]
dict_chemical_id_to_resource_xrefs = {}

license = pharmebinetutils.dict_source_to_license['aeolus']


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
    query = 'MATCH (n:Chemical) RETURN n.identifier, n.inchikey, n.inchi, n.name, n.resource, n.xrefs, n.synonyms , n.licenses '
    results = g.run(query)

    for record in results:
        [identifier, inchikey, inchi, name, resource, xrefs, synonyms, licenses] = record.values()
        inchikey = inchikey if inchikey else ''
        inchi = inchi if inchi else ''
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids, name.lower(), identifier)
        xrefs = xrefs if xrefs else []
        for xref in xrefs:
            if xref.startswith('RxNorm_CUI'):
                rxcui = xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_rxcui_to_Drugbank_with_xref, rxcui, identifier)
        dict_chemical_id_to_resource_xrefs[identifier] = [resource, set(xrefs), set(licenses)]

        if synonyms:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids, synonym.lower(), identifier)

    print('In pharmebinet:' + str(len(dict_chemical_id_to_resource_xrefs)) + ' drugs')


def search_for_mapping_to_drugbank_in_rxnorm( rxnorm_id, drug_concept_id, name):
    """
    Search in RxNorm for mapping to drugbank
    :param rxnorm_id:
    :param drug_concept_id:
    :param name:
    :return:
    """
    cur = conRxNorm.cursor()
    query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = 'DRUGBANK' and RXCUI= '%s' ;")
    query = query % ( rxnorm_id)
    rows_counter = cur.execute(query)
    found_a_mapping = False
    if rows_counter > 0:
        # check if they are drugbank ids where the name is the same as in aeolus
        for (rxcui, lat, code, sab, label,) in cur:
            label = label.lower()
            if code in dict_chemical_id_to_resource_xrefs:
                xrefs = dict_chemical_id_to_resource_xrefs[code][1]
                xrefs.add('RxNorm_CUI:' + rxcui)
                dict_chemical_id_to_resource_xrefs[code][2].add(license)
                found_a_mapping = True
                if label == name:
                    if not (drug_concept_id, code) in set_of_mapping_pairs:
                        set_of_mapping_pairs.add((drug_concept_id, code))
                        csv_writer.writerow([drug_concept_id, code, 'rxcui_map_to_drugbank_and_same_name',
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_chemical_id_to_resource_xrefs[code][0], "AEOLUS"),
                                             '|'.join(
                                                 go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical')), '|'.join(dict_chemical_id_to_resource_xrefs[code][2])])
                else:
                    if not (drug_concept_id, code) in set_of_mapping_pairs:
                        set_of_mapping_pairs.add((drug_concept_id, code))
                        csv_writer.writerow([drug_concept_id, code, 'rxcui_map_to_drugbank',
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_chemical_id_to_resource_xrefs[code][0], "AEOLUS"),
                                             '|'.join(
                                                 go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical')), '|'.join(dict_chemical_id_to_resource_xrefs[code][2])])

    return found_a_mapping


def search_for_mapping_in_umls( rxnorm_id, drug_concept_id):
    """
    Search in UMLS mapping from rxcui to mesh ids over umls cui.
    :param rxnorm_id:
    :param drug_concept_id:
    :return:
    """
    dict_rxcui_to_mesh_ids = pharmebinetutils.getMeshFromUMLSWithRxCUI(con_umls, {rxnorm_id})
    found_a_mapping = False
    if len(dict_rxcui_to_mesh_ids) > 0:
        # check if they are drugbank ids where the name is the same as in aeolus
        for mesh_id in dict_rxcui_to_mesh_ids[rxnorm_id]:
            if mesh_id in dict_chemical_id_to_resource_xrefs:
                xrefs = dict_chemical_id_to_resource_xrefs[mesh_id][1]
                xrefs.add('RxNorm_CUI:' + rxnorm_id)
                found_a_mapping = True
                dict_chemical_id_to_resource_xrefs[mesh_id][2].add(license)
                if not (drug_concept_id, mesh_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id, mesh_id))
                    csv_writer.writerow([drug_concept_id, mesh_id, "rxcui_map_to_MESH_over_umls",
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_chemical_id_to_resource_xrefs[mesh_id][0], "AEOLUS"),
                                         '|'.join(
                                             go_through_xrefs_and_change_if_needed_source_name(xrefs, 'chemical')), '|'.join(dict_chemical_id_to_resource_xrefs[mesh_id][2])])

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
header = ['aeolus_id', 'chemical_id', 'how_mapped', 'resource', 'xrefs', 'licenses']
csv_writer.writerow(header)

# set of mapping pairs
set_of_mapping_pairs=set()

# dictionary manual mapped nodes
dict_manual_mapped_nodes={
    '19135934':'DBSALT002460',
    '19097468':'DBSALT002762'
}

def write_to_tsv_file(drug_concept_id, chemical_id, xrefs, mapping_method):
    dict_chemical_id_to_resource_xrefs[chemical_id][2].add(license)
    csv_writer.writerow([drug_concept_id, chemical_id, mapping_method,
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_xrefs[chemical_id][0], "AEOLUS"),
                         '|'.join(xrefs), '|'.join(dict_chemical_id_to_resource_xrefs[chemical_id][2])])

def load_drug_aeolus_in_dictionary():
    """
    load a part of aeolus drugs, which are not integrated, in a dictionary and set the property integrated=true
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
                    write_to_tsv_file(drug_concept_id, chemical_id, go_through_xrefs_and_change_if_needed_source_name(
                                             dict_chemical_id_to_resource_xrefs[chemical_id][1], 'chemical'), 'map_rxcui_with_xref')

        if found_mapping:
            continue

        if drug_concept_id in dict_manual_mapped_nodes:
            found_mapping = True
            chemical_id=dict_manual_mapped_nodes[drug_concept_id]
            if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                write_to_tsv_file(drug_concept_id, chemical_id, go_through_xrefs_and_change_if_needed_source_name(
                    dict_chemical_id_to_resource_xrefs[chemical_id][1], 'chemical'), 'manual_mapped')

        if found_mapping:
            continue

        found_mapping = search_for_mapping_to_drugbank_in_rxnorm( rxcui, drug_concept_id, name)

        if found_mapping:
            continue

        if rxcui in dict_rxcuis_to_drugbank_id_generate_with_external_source:
            for chemical_id in dict_rxcuis_to_drugbank_id_generate_with_external_source[rxcui]:
                if chemical_id=='DB16550' and rxcui=='6204':
                    continue
                found_mapping = True
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    xrefs = dict_chemical_id_to_resource_xrefs[chemical_id][1]
                    xrefs.add('RxNorm_CUI:' + rxcui)
                    write_to_tsv_file(drug_concept_id, chemical_id, go_through_xrefs_and_change_if_needed_source_name(
                        xrefs, 'chemical'), 'map_rxnorm_to_drugbank_with_use_of_dhimmel_inchikey_and_unii')

        if found_mapping:
            continue

        if rxcui in dict_rxcuis_to_drugbank_id_generate_with_external_source_name:
            found_mapping = True
            for chemical_id in dict_rxcuis_to_drugbank_id_generate_with_external_source_name[rxcui]:
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    xrefs = dict_chemical_id_to_resource_xrefs[chemical_id][1]
                    xrefs.add('RxNorm_CUI:' + rxcui)
                    write_to_tsv_file(drug_concept_id, chemical_id, go_through_xrefs_and_change_if_needed_source_name(
                        xrefs, 'chemical'), 'map_rxnorm_to_drugbank_with_use_of_name_mapping')

        if found_mapping:
            continue

        found_mapping = search_for_mapping_in_umls( rxcui, drug_concept_id)

        if found_mapping:
            continue

        if name in dict_name_to_chemical_ids:
            found_mapping = True
            for chemical_id in dict_name_to_chemical_ids[name]:
                if not (drug_concept_id,chemical_id) in set_of_mapping_pairs:
                    set_of_mapping_pairs.add((drug_concept_id,chemical_id))
                    xrefs = dict_chemical_id_to_resource_xrefs[chemical_id][1]
                    xrefs.add('RxNorm_CUI:' + rxcui)
                    write_to_tsv_file(drug_concept_id, chemical_id, go_through_xrefs_and_change_if_needed_source_name(
                        xrefs, 'chemical'), 'name_mapping')

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

    query = ''' Match (a:Aeolus_Drug{drug_concept_id:line.aeolus_id}),(n:Chemical{identifier:line.chemical_id}) Set   n.aeolus=True,n.resource= split(line.resource,'|') ,n.licenses= split(line.licenses,'|') , n.xrefs=split(line.xrefs,'|') Create (n)-[:equal_to_Aeolus_drug{how_mapped:line.how_mapped}]->(a)'''
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
    print('Load in all drugs from pharmebinet in a dictionary')

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
