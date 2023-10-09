import datetime
import sys, os

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
import general_function_bindingDB


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary chemical id to resource
dict_chemical_id_to_resource = {}

# dictionary inchikey to chemical ids
dict_chemical_inchikey_to_ids = {}

# dictionary synonym to chemical id
dict_chemical_synonym_to_chemical_ids = {}

dict_chemical_smiles = {}


def load_chemical_from_database_and_add_to_dict():
    """
    Load all Chemical from my database  and add them into a dictionary
    """
    query = "MATCH (n:Chemical) RETURN n"
    results = g.run(query)

    for record in results:
        node=record.data()['n']
        identifier = node['identifier']
        dict_chemical_id_to_resource[identifier] = node['resource']

        if 'inchikey' in node:
            inchikey = node['inchikey']
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_inchikey_to_ids, inchikey, identifier)

        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_synonym_to_chemical_ids, name, identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_synonym_to_chemical_ids, synonym.lower(),
                                                      identifier)
        if 'smiles' in node:
            smiles = node['smiles']
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_smiles, smiles, identifier)



def load_all_BioGrid_chemical_and_finish_the_files(csv_mapping):
    """
    Load all chamical and generate the queries, and add rela to the rela tsv
    Where (n)--(:bioGrid_interaction)
    """

    query = "MATCH (n:MONO_STRUCT_NAMES) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0

    for record in results:
        node = record.data()['n']
        counter_all += 1
        if 'monomerid' in node:
            identifier = node['monomerid']
            source = node['source'] if 'source' in node else ''
            source_id = node['source_id'] if 'source_id' in node else ''
        else:
            identifier = node['id']
            source = identifier.split(':')[0]
            source_id = identifier.split(':')[1]

        # mapping
        found_mapping = False



        if 'inchi_key' in node:
            inchikey = node['inchi_key']
            if inchikey in dict_chemical_inchikey_to_ids:
                found_mapping=True
                for chemical_id in dict_chemical_inchikey_to_ids[inchikey]:
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[chemical_id],
                                                                   "BindingDB"),
                         'inchikey'])

        if found_mapping:
            continue

        if source.lower() == 'drugbank':
            if source_id in dict_chemical_id_to_resource:
                found_mapping = True
                csv_mapping.writerow(
                    [identifier, source_id,
                     pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[source_id], "BindingDB"),
                     'drugbank_id'])
        if found_mapping:
            continue

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = synonym.lower()
            if synonym in dict_chemical_synonym_to_chemical_ids:
                found_mapping = True
                for chemical_id in dict_chemical_synonym_to_chemical_ids[synonym]:
                    csv_mapping.writerow(
                         [identifier, chemical_id,
                          pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[chemical_id],
                                                                    "BindingDB"),
                          'synonyms'])

        if found_mapping:
            continue
        if 'smiles_string' in node:
            smiles = node['smiles_string']
            if smiles in dict_chemical_smiles:
                found_mapping = True
                for chemical_id in dict_chemical_smiles[smiles]:
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[chemical_id],
                                                                   "BindingDB"),
                         'smiles'])
                print("found mapping, method: smiles")


        if not found_mapping:
            counter_not_mapped += 1
            #print('not mapped')
            #print(identifier)
            #print(name)
    print('number of not-mapped genes:', counter_not_mapped)
    print('number of all genes:', counter_all)



def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path bindingDB chemical')

    os.chdir(path_of_directory + "mapping_and_merging_into_hetionet\\bindingDB\\")
    home = os.getcwd()
    source = os.path.join(home, 'output\\')
    path_of_directory = os.path.join(home, 'chemical\\')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Chemical from database')
    load_chemical_from_database_and_add_to_dict()
    print("done")
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = general_function_bindingDB.generate_files(path_of_directory, 'mapped_chemical.tsv', source,
                                                          'MONO_STRUCT_NAMES', 'Chemical', ['monomerid', 'id'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all bindingDB monomer from database')
    load_all_BioGrid_chemical_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()