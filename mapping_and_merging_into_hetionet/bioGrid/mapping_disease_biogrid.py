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
    g = driver.session()


# dictionary disease id to resource
dict_disease_id_to_resource = {}

# dictionary doid to disease id
dict_doid_to_disease_ids = {}

# dictionary synonym to chemical id
dict_synonym_to_ids = {}


def load_diseases_from_database_and_add_to_dict():
    """
    Load all diseases from my database  and add them into a dictionary
    """
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_disease_id_to_resource[identifier] = node['resource']
        name = node['name']
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, name, identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, synonym, identifier)

        doids = node['alternative_ids'] if 'alternative_ids' in node else []
        for doid in doids:
            pharmebinetutils.add_entry_to_dict_to_set(dict_doid_to_disease_ids, doid, identifier)


def load_all_bioGrid_diseases_and_finish_the_files(csv_mapping):
    """
    Load all bioGrid disease map to disease and write into file
    """

    query = "MATCH (n:bioGrid_disease) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['id']
        name = node['name'].lower()

        # mapping
        if identifier in dict_doid_to_disease_ids:
            for node_id in dict_doid_to_disease_ids[identifier]:
                csv_mapping.writerow(
                    [identifier, node_id,
                     pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[node_id], "BioGrid"),
                     'doid'])
        elif name in dict_synonym_to_ids:
            for node_id in dict_synonym_to_ids[name]:
                csv_mapping.writerow(
                    [identifier, node_id,
                     pharmebinetutils.resource_add_and_prepare(dict_disease_id_to_resource[node_id], "BioGrid"),
                     'name'])


        else:
            counter_not_mapped += 1
            print('not mapped')
            print(identifier)
    print('number of not-mapped diseases:', counter_not_mapped)
    print('number of all diseases:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path biogrid disease')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bioGrid')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'disease/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all diseases from database')
    load_diseases_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('diseaserate cypher and tsv file')

    csv_mapping = general_function_bioGrid.generate_files(path_of_directory, 'mapping_disease.tsv', source,
                                                             'bioGrid_disease', 'Disease', ['id'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Disgenet diseases from database')
    load_all_bioGrid_diseases_and_finish_the_files(csv_mapping)
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
