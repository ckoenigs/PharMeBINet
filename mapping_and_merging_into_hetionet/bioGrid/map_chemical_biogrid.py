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
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


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
    query = "MATCH (n:Chemical) RETURN n.identifier, n.resource, n.inchikey, n.name, n.synonyms, n.licenses "
    results = g.run(query)

    for record in results:
        [identifier, resource, inchikey, name, synonyms, licenses] = record.values()
        dict_chemical_id_to_resource[identifier] = [resource, set(licenses)]

        if inchikey:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_inchikey_to_ids, inchikey, identifier)

        name = name.lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_synonym_to_chemical_ids, name, identifier)
        synonyms = synonyms if synonyms else []


def load_all_BioGrid_chemical_and_finish_the_files(csv_mapping):
    """
    Load all chamical and generate the queries, and add rela to the rela tsv
    Where (n)--(:bioGrid_interaction)
    """

    query = "MATCH (n:bioGrid_chemical) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
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
                found_mapping = True
                for chemical_id in dict_chemical_inchikey_to_ids[inchikey]:
                    general_function_bioGrid.write_to_tsv_file(dict_chemical_id_to_resource,csv_mapping, identifier, chemical_id,'inchikey')
        if found_mapping:
            continue

        if source.lower() == 'drugbank':
            if source_id in dict_chemical_id_to_resource:
                found_mapping = True
                general_function_bioGrid.write_to_tsv_file(dict_chemical_id_to_resource,csv_mapping, identifier, source_id, 'drugbank_id')
        if found_mapping:
            continue

        if name in dict_chemical_synonym_to_chemical_ids:
            found_mapping = True
            for chemical_id in dict_chemical_synonym_to_chemical_ids[name]:
                general_function_bioGrid.write_to_tsv_file(dict_chemical_id_to_resource,csv_mapping, identifier, chemical_id, 'name')
        # if found_mapping:
        #     continue
        #
        # synonyms = node['synonyms'] if 'synonyms' in node else []
        # for synonym in synonyms:
        #     synonym=synonym.lower()
        #     if synonym in dict_chemical_synonym_to_chemical_ids:
        #         found_mapping=True
        #         for chemical_id in dict_chemical_synonym_to_chemical_ids[synonym]:
        #             general_function_bioGrid.write_to_tsv_file(dict_chemical_id_to_resource,csv_mapping, identifier, chemical_id, 'synonyms')

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
                                                          'bioGrid_chemical', 'Chemical', ['chemical_id', 'id'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all bioGrid chemicals from database')
    load_all_BioGrid_chemical_and_finish_the_files(csv_mapping)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
