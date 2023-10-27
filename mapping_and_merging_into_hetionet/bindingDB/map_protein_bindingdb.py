import datetime
import os, sys
import csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
import general_function_bindingDB


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary from gene symbol to protein id
dict_gene_symbol_to_id = {}
# dict for alternative_ids to identifier
dict_alternativeId_to_identifiers = defaultdict(set)

# dictionary name to identifier
dict_name_to_id = {}
# dictionary identifier to resource
dict_identifier_to_resource = {}
# dictionary sequence to identifier
dict_sequence_to_id = {}
# dictionary synonyms to identifier
dict_synonyms_to_id = {}


def load_protein_from_database_and_add_to_dict():
    '''
    Load all Proteins from Graph-DB and add them into a dictionary
    '''
    query = "MATCH (n:Protein) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_identifier_to_resource[identifier] = node['resource']
        gene_symbols = node['gene_name'] if 'gene_name' in node else []
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for gene_symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_id, gene_symbol, identifier)
        # create dict for alternative_ids
        for alternative_id in alternative_ids:
            pharmebinetutils.add_entry_to_dict_to_set(dict_alternativeId_to_identifiers, alternative_id, identifier)

        if 'name' in node:
            name = node['name'].lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_id, name, identifier)
        if 'as_sequences' in node:
            sequence = node['as_sequences'][0]
            pharmebinetutils.add_entry_to_dict_to_set(dict_sequence_to_id, sequence, identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_id, synonym.lower(),
                                                      identifier)


def load_all_bindingDB_polymer_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    # query = "MATCH (n:bindingDB_POLYMER_AND_NAMES) WHERE n.scientific_name ='Homo sapiens' or (n.scientific_name is null and tolower(n.source_organism) in ['human', 'human sapiens (human)', 'homo sapiens', 'homo sapiens (human)']) RETURN n"
    query = "MATCH (n:bindingDB_POLYMER_AND_NAMES) WHERE n.taxid ='9606'  RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        polymerid = node['polymerid']
        identifier = ""
        if 'unpid1' in node:
            identifier = node['unpid1']
            if "[" in identifier:
                pos = identifier.find("[")
                identifier = identifier[0:pos]

        if 'unpid1' in node and ',' in node['unpid1']:
            counter_not_mapped += 1
            continue

        # mapping
        found_mapping = False
        if identifier != "" and identifier in dict_identifier_to_resource:
            csv_mapping.writerow(
                [polymerid, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier], "BindingDB"),
                 'id'])
            found_mapping = True
        if found_mapping:
            continue

        if identifier != "" and identifier in dict_alternativeId_to_identifiers:
            for uniprot_id in dict_alternativeId_to_identifiers[identifier]:
                csv_mapping.writerow([polymerid, uniprot_id,
                                      pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[uniprot_id],
                                                                                "BindingDB"),
                                      'alternative_id'])
            found_mapping = True
        if found_mapping:
            continue

        if '-' in identifier:
            identifier = identifier.split('-')[0]
            if identifier in dict_identifier_to_resource:
                csv_mapping.writerow(
                    [polymerid, identifier,
                     pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier], "BindingDB"),
                     'id-iso'])
                found_mapping = True
        if found_mapping:
            continue

        if 'display_name' in node:
            name = node['display_name'].lower()

            if name in dict_name_to_id:
                found_mapping = True
                for id in dict_name_to_id[name]:
                    csv_mapping.writerow(
                        [polymerid, id,
                         pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[id],
                                                                   "BindingDB"),
                         'name'])
        if found_mapping:
            continue
        # if 'sequence' in node:
        #     sequence = node['sequence']
        #     sequence = sequence.replace("\n", "").replace(" ", "")
        #     if sequence in dict_sequence_to_id:
        #         found_mapping = True
        #         for id in dict_sequence_to_id[sequence]:
        #             csv_mapping.writerow(
        #                 [polymerid, id,
        #                 pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[id],
        #                                                            "BindingDB"),
        #                 'sequence'])
        #         print("found sequence mapping")
        # if found_mapping:
        #     continue

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = synonym.lower()
            if synonym in dict_synonyms_to_id:
                found_mapping = True
                for id in dict_synonyms_to_id[synonym]:
                    csv_mapping.writerow(
                        [polymerid, id,
                         pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[id],
                                                                   "BindingDB"),
                         'synonyms'])

        if not found_mapping:
            counter_not_mapped += 1
            print(polymerid)
            print(identifier)

    print('number of not-mapped proteins:', counter_not_mapped)
    print('number of all proteins:', counter_all)


def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path bindingdb polymer')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bindingDB/')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    cypher = open('output/cypher.cypher', 'w', encoding='utf-8')
    cypher.close()
    path_of_directory = os.path.join(home, 'protein/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Proteins from database')
    load_protein_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = general_function_bindingDB.generate_files(path_of_directory, 'BindingDB_polymer_to_protein.tsv',
                                                            source,
                                                            'bindingDB_POLYMER_AND_NAMES', 'Protein', ['polymerid'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Binding proteins from database')
    load_all_bindingDB_polymer_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
