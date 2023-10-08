import datetime
import os, sys
import csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary from gene symbol to protein id
dict_gene_symbol_to_id = {}
# dict for alternative_ids
dict_alternativeId_to_identifiers = defaultdict(set)


dict_name_to_id = {}
dict_identifier_to_resource = {}
dict_sequence_to_id = {}
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
            if gene_symbol not in dict_gene_symbol_to_id:
                dict_gene_symbol_to_id[gene_symbol] = set()
            dict_gene_symbol_to_id[gene_symbol].add(identifier)
        # create dict for alternative_ids
        for alternative_id in alternative_ids:
            # if alternative_id not in dict_alternativeId_to_identifiers:
            #     dict_alternativeId_to_identifiers[alternative_id] = set()
            dict_alternativeId_to_identifiers[alternative_id].add(identifier)

        if 'name' in node:
            name = node['name']
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_id, name, identifier)
        if 'as_sequences' in node:
            sequence = node['as_sequences'][0]
            pharmebinetutils.add_entry_to_dict_to_set(dict_sequence_to_id, sequence, identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_id, synonym.lower(),
                                                      identifier)




def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    file_name = 'BindingDB_polymer_to_protein'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['BindingDB_polymerid', 'identifier', 'resource', 'mapping_method']
    csv_mapping.writerow(header)
    cypher_file = open(os.path.join(source, 'cypher.cypher'), 'w', encoding='utf-8')

    # mapping_and_merging_into_hetionet/DisGeNet/
    query = f' Match (n:POLYMER_AND_NAMES{{polymerid:line.BindingDB_polymerid}}), (v:Protein{{identifier:line.identifier}}) Set v.bindingdb="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_BindingDB_polymer{{mapped_with:line.mapping_method}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name+'.tsv',
                                              query)
    query = query.replace("/", "")
    cypher_file.write(query)

    return csv_mapping


def load_all_bindingDB_polymer_and_finish_the_files(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """

    query = "MATCH (n:POLYMER_AND_NAMES) RETURN n"
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
        elif 'id' in node:
            identifier = node['id']
        # mapping
        found_mapping = False
        if identifier != "" and identifier in dict_identifier_to_resource:
            csv_mapping.writerow(
                [polymerid, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[identifier], "BindingDB"),
                 'id'])
            print("found id mapping")
            found_mapping = True
        if found_mapping:
            continue

        if identifier != "" and identifier in dict_alternativeId_to_identifiers:
            for uniprot_id in dict_alternativeId_to_identifiers[identifier]:
                csv_mapping.writerow([polymerid, uniprot_id,
                                      pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[uniprot_id],
                                                                                "BindingDB"),
                                      'alternative_id'])
            print("found alternative_id mapping")
            found_mapping = True
        if found_mapping:
            continue
        if 'display_name' in node:
            name = node['display_name']
            if 'source_organism' in node:
                nature = node['source_organism']
                if 'homo' in nature.lower() and name in dict_name_to_id:
                    found_mapping = True
                    for id in dict_name_to_id[name]:
                        csv_mapping.writerow(
                            [polymerid, id,
                            pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[id],
                                                                       "BindingDB"),
                            'name'])
                    print("found name mapping")
        if found_mapping:
            continue
        # if 'sequence' in node:
        #     sequence = node['sequence']
        #     sequence = sequence.replace("\n", "").replace(" ", "")
        #     if 'source_organism' in node:
        #         nature = node['source_organism']
        #         if 'homo' in nature.lower() and sequence in dict_sequence_to_id:
        #             found_mapping = True
        #             for id in dict_sequence_to_id[sequence]:
        #                 csv_mapping.writerow(
        #                     [polymerid, id,
        #                     pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[id],
        #                                                                "BindingDB"),
        #                     'sequence'])
        #             print("found sequence mapping")
        # if found_mapping:
        #     continue

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = synonym.lower()
            if 'source_organism' in node:
                nature = node['source_organism']
                if 'homo' in nature.lower() and synonym in dict_synonyms_to_id:
                    found_mapping = True
                    for id in dict_synonyms_to_id[synonym]:
                        csv_mapping.writerow(
                            [polymerid, id,
                            pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[id],
                                                                       "BindingDB"),
                            'synonyms'])
                    print("found synonym mapping")

        if not found_mapping:
            counter_not_mapped += 1
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

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet\\bindingDB\\')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'protein\\')

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
    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all DisGeNet proteins from database')
    load_all_bindingDB_polymer_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
