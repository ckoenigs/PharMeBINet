import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary of all pathway ids to resource
dict_pathway_to_resource = {}

# dictionary pathway symbol to pathway id
dict_pathway_name_to_pathway_id = {}


def add_entry_to_dictionary(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


'''
load in all compound from pharmebinet in a dictionary
'''


def load_db_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier, n.name ,n.synonyms, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, resource] = record.values()
        dict_pathway_to_resource[identifier] = set(resource) if resource else set()

        name = name.lower() if name is not None else ''
        add_entry_to_dictionary(dict_pathway_name_to_pathway_id, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                add_entry_to_dictionary(dict_pathway_name_to_pathway_id, synonym, identifier)

    print('length of pathway in db:' + str(len(dict_pathway_to_resource)))


def check_for_mapping(dict_source_to_ids, source, dict_source_to_pathway_ids, csv_writer, identifier):
    """
    go through all cui_ids of the different sources and check if the are in the dictionary to pathway id. If so add
    them into tsv file.
    :param dict_source_to_ids:
    :param source:
    :param dict_source_to_pathway_ids:
    :param csv_writer:
    :param identifier:
    :return:
    """
    found_mapping = False
    for cui in dict_source_to_ids[source]:
        if cui in dict_source_to_pathway_ids:
            found_mapping = True
            for pathway_id in dict_source_to_pathway_ids[cui]:
                resource = dict_pathway_to_resource[pathway_id]
                resource.add("PharmGKB")
                resource = "|".join(sorted(resource))
                csv_writer.writerow([pathway_id, identifier, resource, source.lower()])
    return found_mapping


def load_pharmgkb_phathways_in():
    """
    pathwayrate mapping file and cypher file
    mapp pathway pharmgkb to pathway
    :return:
    """
    # tsv_file
    file_name = 'pathway/mapping.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['pathway_id', 'pharmgkb_id', 'resource', 'how_mapped'])

    # pathwayrate cypher file
    pathwayrate_cypher_file(file_name)

    query = '''MATCH (n:PharmGKB_Pathway) RETURN n'''
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    for record in results:
        result = record.data()['n']
        identifier = result['id']
        dict_names = {}
        name = result['name'].lower() if 'name' in result else ''
        add_entry_to_dictionary(dict_names, 'name', name)

        found_a_mapping = False

        if 'name' in dict_names:
            found_a_mapping = check_for_mapping(dict_names, 'name', dict_pathway_name_to_pathway_id, csv_writer,
                                                identifier)

        if found_a_mapping:
            counter_map += 1
            continue

        counter_not_mapped += 1
    print('number of pathways which mapped:', counter_map)
    print('number of pathways which not mapped:', counter_not_mapped)


def pathwayrate_cypher_file(file_name):
    cypher_file = open('output/cypher.cypher', 'a')
    query = '''  MATCH (n:PharmGKB_pathway{id:line.pharmgkb_id}), (c:pathway{identifier:line.pathway_id})  Set c.pharmgkb='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_pathway_pharmgkb{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('pathwayrate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in pathway from pharmebinet')

    load_db_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in pathway from pharmgb in')

    load_pharmgkb_phathways_in()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
