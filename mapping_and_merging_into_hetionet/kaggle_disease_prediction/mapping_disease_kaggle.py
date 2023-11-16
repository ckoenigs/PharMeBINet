import datetime
import sys, os
import csv

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


# dictionary disease id to resource
dict_disease_id_to_resource = {}

# dictionary synonym to disease
dict_synonym_to_ids = {}


# dictionary synonym to disease
dict_narrow_synonym_to_ids = {}


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
        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, name, identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, synonym, identifier)

        narrow_synonyms=node['narrow_synonyms'] if 'narrow_synonyms' in node else []
        for synonym in narrow_synonyms:
            synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_narrow_synonym_to_ids, synonym, identifier)

def generate_files(path_of_directory, file_name, source, label_kaggle, label_pharmebinet):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_path = os.path.join(path_of_directory, file_name)
    header = ['node_id', 'pharmebinet_node_id', 'how_mapped']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    query = f' Match (n:{label_kaggle}{{name:line.node_id}}), (v:{label_pharmebinet}{{identifier:line.pharmebinet_node_id}})  Create (v)-[:equal_to_kaggle_{label_pharmebinet.lower()}{{how_mapped:line.how_mapped}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    cypher_file.write(query)
    return csv_mapping

dict_manual_mapping={
    'Hypertension':'MONDO:0005044',
    'Cervical spondylosis':'MONDO:0008481',
    'Chronic cholestasis':'MONDO:0001751',
    'Osteoarthristis':'MONDO:0005178',
    'Hepatitis E':'MONDO:0005788',
    'Hepatitis D':'MONDO:0005789',
    'Hepatitis C':'MONDO:0005231',
    'Bronchial Asthma':'MONDO:0004979',
    'Fungal infection':'MONDO:0002041'
}

def load_all_kaggle_diseases_and_finish_the_files(csv_mapping):
    """
    Load all kaggle disease map to disease and write into file
    """

    query = "MATCH (n:kaggle_disease) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['name']
        name = node['name'].lower()

        if name in dict_synonym_to_ids:
            for node_id in dict_synonym_to_ids[name]:
                csv_mapping.writerow(
                    [identifier, node_id,'name'])
        elif identifier in dict_manual_mapping:
            csv_mapping.writerow(
                [identifier, dict_manual_mapping[identifier], 'manual'])
        elif name in dict_narrow_synonym_to_ids:
            for node_id in dict_narrow_synonym_to_ids[name]:
                csv_mapping.writerow(
                    [identifier, node_id,'narrow'])

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
        sys.exit('need a path kaggle disease')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/kaggle_disease_prediction')
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

    csv_mapping = generate_files(path_of_directory, 'mapping_disease.tsv', source,
                                                             'kaggle_disease', 'Disease')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all kaggle diseases from database')
    load_all_kaggle_diseases_and_finish_the_files(csv_mapping)
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
