import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


class Drugpharmebinet:
    """
    license: string
    identifier: string (Drugbank ID)
    inchikey: string
    inchi: string
    name: string
    resource: list string
    xrefs: list string
    """

    def __init__(self, licenses, identifier, inchikey, inchi, name, resource, xrefs):
        self.license = licenses
        self.identifier = identifier
        self.inchikey = inchikey
        self.inchi = inchi
        self.name = name
        self.resource = resource
        self.xrefs = xrefs


class Drug_Aeolus:
    """
    vocabulary_id: string (defined the type of the concept_code which is rxnorm)
    name: string
    outcome_concept_id: string (OHDSI ID )
    concept_code: string (RxNorm ID [rxcui])
    drugbank_id: string
    how_mapped: string
    """

    def __init__(self, vocabulary_id, name, drug_concept_id, concept_code):
        self.vocabulary_id = vocabulary_id
        self.name = name
        self.drug_concept_id = drug_concept_id
        self.concept_code = concept_code

    def set_drugbank_id(self, drugbank_id):
        self.drugbank_id = drugbank_id

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all compounds with id (drugbank id) as key and class Drugpharmebinet as value
dict_all_drug = {}

# dictionary with all aeolus drugs with key drug_concept_id (OHDSI ID) and value is class Drug_Aeolus
dict_aeolus_drugs = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = create_connection_to_databases.database_connection_RxNorm()


# dictionary rxcui to drugbank ids
dict_rxcui_to_Drugbank_with_xref = {}

'''
load in all compounds from pharmebinet in dictionary
properties:
    license
    identifier
    inchikey
    inchi
    name
    source
    url
'''


def load_compounds_from_pharmebinet():
    query = 'MATCH (n:Chemical) RETURN n '
    results = g.run(query)

    for record in results:
        result= record.data()['n']
        licenses = result['license']
        identifier = result['identifier']
        inchikey = result['inchikey'] if 'inchikey' in result else ''
        inchi = result['inchi'] if 'inchi' in result else ''
        name = result['name']
        resource = result['resource'] if 'resource' in result else []
        xrefs = result['xrefs'] if 'xrefs' in result else []
        for xref in xrefs:
            if xref.startswith('RxNorm_CUI'):
                rxcui = xref.split(':')[1]
                if not rxcui in dict_rxcui_to_Drugbank_with_xref:
                    dict_rxcui_to_Drugbank_with_xref[rxcui] = set()
                dict_rxcui_to_Drugbank_with_xref[rxcui].add(identifier)

        drug = Drugpharmebinet(licenses, identifier, inchikey, inchi, name, resource, xrefs)

        dict_all_drug[identifier] = drug

    print('In pharmebinet:' + str(len(dict_all_drug)) + ' drugs')


# dictionary to translate rxnorm id to drug_concept_id
dict_rxnorm_to_drug_concept_id = {}

'''
load a part of aeolus drugs, which are not integrated, in a dictionary and set the property integrated='yes'
has properties:
    vocabulary_id: defined the type of the concept_code
    name
    drug_concept_id: OHDSI ID
    concept_code: RxNorm CUI
'''


def load_drug_aeolus_in_dictionary():
    query = '''MATCH (n:Aeolus_Drug)  RETURN n'''

    results = g.run(query)
    for record in results:
        result = record.data()['n']
        if result['vocabulary_id'] != 'RxNorm':
            print('ohje')
        rxcui = result['concept_code']
        drug_concept_id = result['drug_concept_id']
        drug = Drug_Aeolus(result['vocabulary_id'], result['name'], result['drug_concept_id'], result['concept_code'])
        dict_aeolus_drugs[drug_concept_id] = drug
        if not result['concept_code'] in dict_rxnorm_to_drug_concept_id:
            dict_rxnorm_to_drug_concept_id[result['concept_code']] = result['drug_concept_id']
        if rxcui in dict_rxcui_to_Drugbank_with_xref:
            dict_aeolus_drug_mapped_ids[drug_concept_id] = list(dict_rxcui_to_Drugbank_with_xref[rxcui])
            dict_aeolus_drugs[drug_concept_id].set_how_mapped('map rxcui with xref')
        else:
            list_aeolus_drugs_without_drugbank_id.append(rxcui)
    print('Size of Aoelus drug:' + str(len(dict_aeolus_drugs)))
    print('number of rxnorm ids in aeolus drug:' + str(len(dict_rxnorm_to_drug_concept_id)))
    print('number of not mapped:', len(list_aeolus_drugs_without_drugbank_id))


# list of all concept_id where no drugbank id is found, only save the rxnorm ids
list_aeolus_drugs_without_drugbank_id = []

# dictionary with key drug_concept_id and value is a list of drugbank ids
dict_aeolus_drug_mapped_ids = {}

'''
Search in RxNorm for mapping
'''


def search_for_mapping_in_rxnorm(sab, rxnorm_id, drug_concept_id, mapping_string):
    cur = conRxNorm.cursor()
    query = ("Select RXCUI,LAT,CODE,SAB,STR From RXNCONSO Where SAB = '%s' and RXCUI= '%s' ;")
    query = query % (sab, rxnorm_id)
    rows_counter = cur.execute(query)
    name = dict_aeolus_drugs[drug_concept_id].name.lower()
    found_a_mapping = False
    if rows_counter > 0:
        # list of all founded mapped identifier ids for the rxcui
        mapped_ids = []
        # list of all drugbank ids with the same name as in aeolus
        mapped_ids_same_name = []
        has_same_name = False
        # check if their are drugbank ids where the name is the same as in aeolus
        for (rxcui, lat, code, sab, label,) in cur:
            label = label.lower()
            if code in dict_all_drug:
                dict_all_drug[code].xrefs.append('RxNorm_CUI:' + rxcui)
                mapped_ids.append(code)
                found_a_mapping = True
                if label == name:
                    has_same_name = True
                    mapped_ids_same_name.append(code)

        if has_same_name:
            mapped_ids_same_name = list(set(mapped_ids_same_name))
            dict_aeolus_drug_mapped_ids[drug_concept_id] = mapped_ids_same_name
            dict_aeolus_drugs[drug_concept_id].set_how_mapped(mapping_string)
        elif found_a_mapping:
            mapped_ids = list(set(mapped_ids))
            dict_aeolus_drug_mapped_ids[drug_concept_id] = mapped_ids
            dict_aeolus_drugs[drug_concept_id].set_how_mapped(mapping_string)
    return found_a_mapping


'''
map rxnorm to drugbank with use of the RxNorm database
'''


def map_rxnorm_to_drugbank_use_rxnorm_database():
    # for rxnorm_id, drug_concept_id in dict_rxnorm_to_drug_concept_id.items():
    #     if not search_for_mapping_in_rxnorm('DRUGBANK', rxnorm_id, drug_concept_id, 'rxcui map to drugbank'):
    #         list_aeolus_drugs_without_drugbank_id.append(rxnorm_id)

    delete_list_without_DB = set()
    for rxnorm_id in list_aeolus_drugs_without_drugbank_id:
        drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]
        if search_for_mapping_in_rxnorm('DRUGBANK', rxnorm_id, drug_concept_id, 'rxcui map to drugbank'):
            delete_list_without_DB.add(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))

    # delete the new mapped rxnorm cuis from not map list
    delete_list_without_DB = list(delete_list_without_DB)
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))
    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('all that are map to drugbank id:' + str(len(dict_aeolus_drug_mapped_ids)))
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
map with use of map rxcui-drugbank id table with inchikeys and unii
idea form himmelstein
prioperties:
    0:rxcui
    1:drugbank ids separated with |
'''


def map_rxnorm_to_drugbank_with_use_inchikeys_and_unii():
    f = open('../RxNorm_to_DrugBank/results/map_rxnorm_to_drugbank_with_use_of_unii_and_inchikey.tsv', 'r')
    next(f)
    # list with all positions of the rxcuis which are  mapped in this step
    delete_list_without_DB = []
    for line in f:
        splitted = line.split('\t')
        rxnorm_id = splitted[0]
        drugbank_ids = splitted[1].split('\n')[0].split('\r')[0].split('|')
        if rxnorm_id in list_aeolus_drugs_without_drugbank_id:
            delete_list_without_DB.append(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))
            drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]

            dict_aeolus_drugs[drug_concept_id].set_how_mapped(
                'map rxnorm to drugbank with use of dhimmel inchikey and unii')

            dict_aeolus_drug_mapped_ids[drug_concept_id] = drugbank_ids
            # add to all mapped chemical the rxnorm cui as xref
            for drugbank_id in drugbank_ids:
                dict_all_drug[drugbank_id].xrefs.append('RxNorm_CUI:' + rxnorm_id)

    # delete the new mapped rxnorm cuis from not mapped list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))

    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('length of mapped OHDSI ID and rxnorm cui:' + str(len(dict_aeolus_drug_mapped_ids)))
    print('length of list with rxcui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
use file where rxnorm mapped to drugbank
used name mapping
'''


def map_name_rxnorm_to_drugbank():
    f = open('../RxNorm_to_DrugBank/results/name_map_drugbank_to_rxnorm.tsv', 'r')
    next(f)
    # list with all positions of the rxcuis which are  mapped in this step
    delete_list_without_DB = []
    for line in f:
        splitted = line.split('\t')
        drugbank_id = splitted[0]
        rxnorm_id = splitted[1].split('\n')[0]
        if rxnorm_id in list_aeolus_drugs_without_drugbank_id:
            delete_list_without_DB.append(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))
            drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]

            dict_aeolus_drugs[drug_concept_id].set_how_mapped('map rxnorm to drugbank with use of name mapping')
            dict_all_drug[drugbank_id].xrefs.append('RxNorm_CUI:' + rxnorm_id)

            if not drug_concept_id in dict_aeolus_drug_mapped_ids:
                dict_aeolus_drug_mapped_ids[drug_concept_id] = [drugbank_id]
            else:
                if not drugbank_id in dict_aeolus_drug_mapped_ids[drug_concept_id]:
                    dict_aeolus_drug_mapped_ids[drug_concept_id].append(drugbank_id)

    # delete the new mapped rxnorm cuis from not map list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))
    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)

    print('length of mapped rxnorm:' + str(len(dict_aeolus_drug_mapped_ids)))
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


'''
Map aeolus to chemicals with mesh id
'''


def map_to_mesh_chemical():
    # list with all positions of the rxcuis which are  mapped in this step
    delete_list_without_DB = []
    for rxnorm_id in list_aeolus_drugs_without_drugbank_id:
        drug_concept_id = dict_rxnorm_to_drug_concept_id[rxnorm_id]
        if search_for_mapping_in_rxnorm('MSH', rxnorm_id, drug_concept_id, 'rxcui map to MESH'):
            delete_list_without_DB.append(list_aeolus_drugs_without_drugbank_id.index(rxnorm_id))

    # delete the new mapped rxnorm cuis from not map list
    delete_list_without_DB = list(set(delete_list_without_DB))
    delete_list_without_DB.sort()
    delete_list_without_DB = list(reversed(delete_list_without_DB))
    for index in delete_list_without_DB:
        list_aeolus_drugs_without_drugbank_id.pop(index)
    print('length of list with cui but no drugbank:' + str(len(list_aeolus_drugs_without_drugbank_id)))


# list of drug_concept_ids which are map to pharmebinet
list_map_to_pharmebinet = []
# list of al drug_concept_ids that has a drugbank id but not mapped to pharmebinet
list_not_mapped = []

# genertate file for the different map methods
map_rxcui = open('drug/aeolus_map_with_use_of_rxcui.tsv', 'w')
csv_rxcui = csv.writer(map_rxcui, delimiter='\t')
csv_rxcui.writerow(['rxnorm_cui', 'drugbank_ids with | as seperator', 'name'])

map_name = open('drug/aeolus_map_with_use_of_table_of_name_mapping.tsv', 'w')
csv_name = csv.writer(map_name, delimiter='\t')
csv_name.writerow(['rxnorm_cui', 'drugbank_ids with | as seperator', 'name'])

map_with_inchikey_unii = open('drug/aeolus_map_with_use_of_unii_and_inchikey.tsv', 'w')
csv__inchikey_unii = csv.writer(map_with_inchikey_unii, delimiter='\t')
csv__inchikey_unii.writerow(['rxnorm_cui', 'drugbank_ids with | as seperator', 'name'])

map_mesh = open('drug/aeolus_map_with_use_of_mesh.tsv', 'w')
csv_mesh = csv.writer(map_mesh, delimiter='\t')
csv_mesh.writerow(['rxnorm_cui', 'drugbank_ids with | as seperator', 'name'])

# generate file of not mapped aeolus drugs
not_mapped = open('drug/not_mapped_rxcuis.tsv', 'w')
not_mapped.write('drug_concept_id \t rxcui \t name \n')

# mapped with xref
map_xrefs = open('drug/aeolus_map_with_use_of_xrefs.tsv', 'w')
csv_xrefs = csv.writer(map_xrefs, delimiter='\t')
csv_xrefs.writerow(['rxnorm_cui', 'drugbank_ids with | as seperator', 'name'])

# dictionary with for every how_mapped has a different file
dict_how_mapped_files = {
    'map rxnorm to drugbank with use of name mapping': csv_name,
    'rxcui map to drugbank': csv_rxcui,
    'map rxnorm to drugbank with use of dhimmel inchikey and unii': csv__inchikey_unii,
    'rxcui map to MESH': csv_mesh,
    'map rxcui with xref': csv_xrefs}

# generate file with rxnom and a list of drugbank ids and wheere there are from
multiple_drugbankids = open('drug/aeolus_multiple_drugbank_ids.tsv', 'w')
multiple_drugbankids.write('rxnorm_cui \t drugbank_ids with | as seperator \t where are it from \n')

'''
map aeolus drug in pharmebinet compound
'''


def map_aeolus_drugs_to_pharmebinet():
    for drug_concept_id, mapped_ids in dict_aeolus_drug_mapped_ids.items():
        has_one = False
        has_two = False
        list_double_map_mapped_ids = []
        string_list_mapped_ids = "|".join(mapped_ids)
        rxnorm_cui = dict_aeolus_drugs[drug_concept_id].concept_code
        how_mapped = dict_aeolus_drugs[drug_concept_id].how_mapped
        dict_how_mapped_files[how_mapped].writerow(
            [rxnorm_cui, string_list_mapped_ids, dict_aeolus_drugs[drug_concept_id].name])
        if drug_concept_id == '42903441':
            print('blub')

        if len(mapped_ids) > 1:
            multiple_drugbankids.write(rxnorm_cui + '\t' + string_list_mapped_ids + '\t' + how_mapped + '\n')

        for drug_id in mapped_ids:
            if drug_id in dict_all_drug:
                list_double_map_mapped_ids.append(drug_id)

                if has_one:
                    has_two = True
                    dict_aeolus_drugs[drug_concept_id].drugbank_id.append(drug_id)
                else:
                    dict_aeolus_drugs[drug_concept_id].set_drugbank_id([drug_id])
                has_one = True
        if has_two:
            list_map_to_pharmebinet.append(drug_concept_id)
        elif has_one:
            list_map_to_pharmebinet.append(drug_concept_id)
        else:
            list_not_mapped.append(drug_concept_id)
    print('Mapped to pharmebinet:' + str(len(list_map_to_pharmebinet)))
    print('Will generate new nodes:' + str(len(list_not_mapped)))

    for drug_concept_id, drug in dict_aeolus_drugs.items():
        if not drug_concept_id in dict_aeolus_drug_mapped_ids:
            not_mapped.write(drug_concept_id + '\t' + drug.concept_code + '\t' + drug.name + '\n')


# dictionary count deleted drugbank ids fro the different mapping methods
dict_how_mapped_delete_counter = {}

'''
Generate cypher file to update or create the relationships in pharmebinet
'''


def generate_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = ''' Match (a:Aeolus_Drug{drug_concept_id:line.aeolus_id}),(n:Chemical{identifier:line.chemical_id}) Set a.mapped_id=split(line.mapped_ids,'|'), a.how_mapped=line.how_mapped ,  n.aeolus="yes",n.resource= split(line.resource,'|') , n.xrefs=split(line.xrefs,'|') Create (n)-[:equal_to_Aeolus_drug]->(a)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/aeolus/drug/mapped.tsv', query)
    cypher_file.write(query)

    cypher_file.close()


# tsv for mapped aeolus pairs
file = open('drug/mapped.tsv', 'w', encoding='utf-8')
csv_writer = csv.writer(file, delimiter='\t')
header = ['aeolus_id', 'chemical_id', 'mapped_ids', 'how_mapped', 'resource', 'xrefs']
csv_writer.writerow(header)

'''
integrate aeolus drugs in hetiont, by map generate a edge from pharmebinet to the mapped aeolus node
if no pharmebinet node is found, then generate a new node for compound
'''


def integrate_aeolus_drugs_into_pharmebinet():
    # count all possible mapped aeolus drug
    counter = 0
    # count all aeolus which are only mapped to illegal drugbank ids
    counter_with_one_which_is_removed = 0

    for drug_concept_id, mapped_ids in dict_aeolus_drug_mapped_ids.items():
        counter += 1
        index = 0
        how_mapped = dict_aeolus_drugs[drug_concept_id].how_mapped
        delete_index = []
        alternative_ids = []
        mapped_ids_string = '|'.join(mapped_ids)
        for mapped_id in mapped_ids:
            index += 1
            xrefs = go_through_xrefs_and_change_if_needed_source_name(dict_all_drug[mapped_id].xrefs, 'chemical')
            xrefs_string = '|'.join(xrefs)
            csv_writer.writerow([drug_concept_id, mapped_id, mapped_ids_string, how_mapped,
                                 pharmebinetutils.resource_add_and_prepare(dict_all_drug[mapped_id].resource, "AEOLUS"), xrefs_string])

    print('all aeolus drug which are map to drugbank, where some drugbank id are not existing:' + str(counter))
    print(dict_how_mapped_delete_counter)


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

    # dictionary with all aeolus drugs with key drug_concept_id and value is class Drug_Aeolus
    global dict_aeolus_drugs
    dict_aeolus_drugs = {}

    # dictionary to translate rxnorm id to drug_concept_id
    global dict_rxnorm_to_drug_concept_id
    dict_rxnorm_to_drug_concept_id = {}

    # list with rxnorm ids which are not mapped to drugbank ID
    global list_aeolus_drugs_without_mapped_id
    list_aeolus_drugs_without_mapped_id = []

    # dictionary with key drug_concept_id and value is a list of drugbank ids
    global dict_aeolus_drug_mapped_ids
    dict_aeolus_drug_mapped_ids = {}

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all drugs from aeolus in a dictionary')

    load_drug_aeolus_in_dictionary()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Find drugbank ids with use of the rxcuis and save them in a dictionary')

    map_rxnorm_to_drugbank_use_rxnorm_database()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map with use of rxnorm_to drugbank with mapping using unii and inchikey')

    map_rxnorm_to_drugbank_with_use_inchikeys_and_unii()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map with rxnorm to drugbank with use of mapping file with name')

    map_name_rxnorm_to_drugbank()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map with mesh to chemical')

    map_to_mesh_chemical()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map the drugbank id from the aeolus drug to the chemicals in pharmebinet')

    map_aeolus_drugs_to_pharmebinet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Generate tsv of mapped drugs')

    integrate_aeolus_drugs_into_pharmebinet()

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
