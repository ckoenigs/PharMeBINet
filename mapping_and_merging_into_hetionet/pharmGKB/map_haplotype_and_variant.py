import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of all node ids to resource
dict_node_to_resource = {}

# dictionary ndbSnp id to node id
dict_dbSNP_to_id={}

# dictionary  name to node id
dict_name_to_node_id={}


def add_value_to_dictionary(dictionary, key, value):
    """
    add key to dictionary if not existing and add value to set
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)



'''
load in all compound from hetionet in a dictionary
'''


def load_db_info_in():
    query = '''MATCH (n:Variant) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms'''
    results = g.run(query)

    for identifier,  xrefs, resource, name, synonyms, in results:
        dict_node_to_resource[identifier] = resource if resource else []

        if xrefs:
            for xref in xrefs:
                if xref.startswith('dbSNP'):
                    add_value_to_dictionary(dict_dbSNP_to_id, xref.split(':')[1], identifier)
        if name:
            name = name.lower()
            add_value_to_dictionary(dict_name_to_node_id, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                add_value_to_dictionary(dict_name_to_node_id, synonym, identifier)

    print('length of chemical in db:' + str(len(dict_node_to_resource)))


def add_information_to_file(drugbank_id, identifier, csv_writer, how_mapped, tuple_set, dict_to_resource):
    """
    add mapper to file if not already is added!
    :param drugbank_id:
    :param identifier:
    :param csv_writer:
    :param how_mapped:
    :param tuple_set:
    :return:
    """
    if (drugbank_id, identifier) in tuple_set:
        return
    tuple_set.add((drugbank_id, identifier))
    resource = dict_to_resource[drugbank_id]
    resource.append('PharmGKB')
    resource = "|".join(sorted(set(resource)))
    csv_writer.writerow([drugbank_id, identifier, resource, how_mapped])


def load_pharmgkb_in(label, directory, mapped_label):
    """
    generate mapping file and cypher file for a given label
    map nodes to chemical
    :param label: string
    :param directory: distionary
    :param mapped_label
    :return:
    """

    # csv_file
    file_name = directory+'/mapping_' + label.split('_')[1] + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier', 'pharmgkb_id', 'resource', 'how_mapped'])

    # csv_file for new
    file_name_new = directory + '/new_' + label.split('_')[1] + '.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_writer_new = csv.writer(file_new, delimiter='\t')
    csv_writer_new.writerow(['identifier', 'dbid', 'how_mapped'])

    # csv file for not mapping
    not_mapped_file = open(directory+'/not_mapping_' + label.split('_')[1] + '.tsv', 'w', encoding='utf-8')
    csv_writer_not = csv.writer(not_mapped_file, delimiter='\t')
    csv_writer_not.writerow(['pharmgkb_id', 'name'])
    # generate cypher file
    generate_cypher_file(file_name, label, mapped_label)
    generate_cypher_file(file_name_new, label, mapped_label, False)

    query = '''MATCH (n:%s) RETURN n'''
    query = query % (label)
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    # set of all tuples
    set_of_all_tuples = set()


    for result, in results:
        name= result['name']
        identifier = result['id'] if 'id' in result else name


        mapped = False

        if len(name) > 0:
            name = name.lower()
            if name in dict_dbSNP_to_id:
                mapped = True
                counter_map += 1
                for identifier_variant in dict_dbSNP_to_id[name]:
                    add_information_to_file(identifier_variant, identifier, csv_writer, 'dbSNP',
                                            set_of_all_tuples, dict_node_to_resource)
            if mapped:
                continue

            if name in dict_name_to_node_id:
                mapped = True
                counter_map += 1
                for identifier_variant in dict_name_to_node_id[name]:
                    add_information_to_file(identifier_variant, identifier, csv_writer, 'name',
                                            set_of_all_tuples, dict_node_to_resource)
            if mapped:
                continue


        if not mapped:
            counter_not_mapped += 1
            csv_writer_not.writerow([identifier, result['name'], result['types']])
            if name.startswith('rs') and name[2].isdigit():
                csv_writer_new.writerow([identifier,name,  'new'])

    print('number of variant which mapped:', counter_map)
    print('number of mapped:', len(set_of_all_tuples) )
    print('number of variant which not mapped:', counter_not_mapped)


def generate_cypher_file(file_name, label, mapped_label, mapped=True):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')
    if mapped:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:%s), (c:%s{identifier:line.identifier}) Where n.id=line.pharmgkb_id or n.name=line.pharmgkb_id  Set c.pharmgkb='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_%s_phamrgkb{how_mapped:line.how_mapped}]->(n); \n'''
        query = query % (file_name, label,  mapped_label, label.split('_')[1].lower())
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:%s) Where n.id=line.identifier or n.name=line.identifier   Create (c:%s :GeneVariant{identifier:line.dbid, name:n.name, synonyms:n.synonyms, location:n.location, pharmgkb:'yes', resource:["PharmGBK"], xrefs:["dbSNP:"+line.dbid] ,license:"CC BY-SA 4.0" , source:"dbSNP from PharmGKB"})-[:equal_to_%s_phamrgkb{how_mapped:line.how_mapped}]->(n);\n '''
        query = query % (file_name, label, mapped_label, label.split('_')[1].lower())
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in variant from hetionet')

    load_db_info_in()

    for label in ['PharmGKB_Variant', 'PharmGKB_Haplotype']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Load in %s from pharmgb in' % (label))

        load_pharmgkb_in(label, 'variant','Variant')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
