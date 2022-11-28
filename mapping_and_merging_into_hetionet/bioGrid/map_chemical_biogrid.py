import datetime
import sys, os
import general_function_bioGrid

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary chemical id to resource
dict_chemical_id_to_resource = {}

# dictionary inchikey to chemical ids
dict_chemical_inchikey_to_ids = {}

# dictionary synonym to chemical id
dict_chemical_synonym_to_chemical_ids = {}


def load_chemical_from_database_and_add_to_dict():
    """
    Load all Chemical from my database  and add them into a dictionary
    """
    query = "MATCH (n:Chemical) RETURN n"
    results = g.run(query)

    for node, in results:
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


def load_all_BioGrid_chemical_and_finish_the_files(csv_mapping):
    """
    Load all chamical and generate the queries, and add rela to the rela tsv
    Where (n)--(:bioGrid_interaction)
    """

    query = "MATCH (n:bioGrid_chemical) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for node, in results:
        counter_all += 1
        if 'chemical_id' in node:
            identifier = node['chemical_id']
            source = node['source'] if 'source' in node else ''
            source_id = node['source_id'] if 'source_id' in node else ''
        else:
            identifier = node['id']
            source = identifier.split(':')[0]
            source_id = identifier.split(':')[1]
        name = node['name'].lower()

        # mapping
        found_mapping = False



        if 'inchikey' in node:
            inchikey = node['inchikey']
            if inchikey in dict_chemical_inchikey_to_ids:
                found_mapping=True
                for chemical_id in dict_chemical_inchikey_to_ids[inchikey]:
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[chemical_id],
                                                                   "bioGrid"),
                         'inchikey'])
        if found_mapping:
            continue

        if source.lower() == 'drugbank':
            if source_id in dict_chemical_id_to_resource:
                found_mapping = True
                csv_mapping.writerow(
                    [identifier, source_id,
                     pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[source_id], "bioGrid"),
                     'drugbank_id'])
        if found_mapping:
            continue

        if name in dict_chemical_synonym_to_chemical_ids:
            found_mapping = True
            for chemical_id in dict_chemical_synonym_to_chemical_ids[name]:
                csv_mapping.writerow(
                    [identifier, chemical_id,
                     pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[chemical_id], "bioGrid"),
                     'name'])
        # if found_mapping:
        #     continue
        #
        # synonyms = node['synonyms'] if 'synonyms' in node else []
        # for synonym in synonyms:
        #     synonym=synonym.lower()
        #     if synonym in dict_chemical_synonym_to_chemical_ids:
        #         found_mapping=True
        #         for chemical_id in dict_chemical_synonym_to_chemical_ids[synonym]:
        #             csv_mapping.writerow(
        #                 [identifier, chemical_id,
        #                  pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[chemical_id],
        #                                                            "bioGrid"),
        #                  'synonyms'])

        if not found_mapping:
            counter_not_mapped += 1
            print('not mapped')
            print(identifier)
            print(name)
    print('number of not-mapped genes:', counter_not_mapped)
    print('number of all genes:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path biogrid chemical')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bioGrid')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'chemical/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Chemical from database')
    load_chemical_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = general_function_bioGrid.generate_files(path_of_directory, 'mapped_chemical.tsv', source,
                                                          'bioGrid_chemical', 'Chemical', ['chemical_id','id'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all bioGrid chemicals from database')
    load_all_BioGrid_chemical_and_finish_the_files(csv_mapping)


if __name__ == "__main__":
    # execute only if run as a script
    main()
