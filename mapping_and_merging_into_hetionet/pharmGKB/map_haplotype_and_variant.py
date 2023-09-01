import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary of all node ids to resource
dict_node_to_resource = {}

# dictionary of all node ids to xrefs
dict_node_to_xrefs = {}

# dictionary ndbSnp id to node id
dict_dbSNP_to_id = {}

# dictionary  name to node id
dict_name_to_node_id = {}


def load_db_info_in():
    """
    load in all variants from pharmebinet in a dictionary
    :return:
    """
    query = '''MATCH (n:Variant) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms'''
    results = g.run(query)

    for record in results:
        [identifier, xrefs, resource, name, synonyms] = record.values()
        dict_node_to_resource[identifier] = resource if resource else []
        dict_node_to_xrefs[identifier] = xrefs if xrefs else []
        if identifier.startswith('rs'):
            pharmebinetutils.add_entry_to_dict_to_set(dict_dbSNP_to_id, identifier, identifier)
        # if xrefs:
        #     for xref in xrefs:
        #         if xref.startswith('dbSNP'):
        # pharmebinetutils.add_entry_to_dict_to_set(dict_dbSNP_to_id, xref.split(':')[1], identifier)
        if name:
            name = name.lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_node_id, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_node_id, synonym, identifier)

    print('length of chemical in db:' + str(len(dict_node_to_resource)))


def add_information_to_file(variant_id, identifier, csv_writer, how_mapped, tuple_set, dict_to_resource):
    """
    add mapper to file if not already is added!
    :param variant_id:
    :param identifier:
    :param csv_writer:
    :param how_mapped:
    :param tuple_set:
    :return:
    """
    if (variant_id, identifier) in tuple_set:
        return
    tuple_set.add((variant_id, identifier))
    xrefs = dict_node_to_xrefs[variant_id]
    if identifier.startswith('PA'):
        xrefs.append('PharmGKB:' + identifier)
    xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, 'Variant')
    csv_writer.writerow(
        [variant_id, identifier, pharmebinetutils.resource_add_and_prepare(dict_to_resource[variant_id], 'PharmGKB'),
         how_mapped, '|'.join(xrefs)])


def load_pharmgkb_in(label, directory, mapped_label):
    """
    generate mapping file and cypher file for a given label
    map nodes to chemical
    :param label: string
    :param directory: distionary
    :param mapped_label
    :return:
    """

    # tsv_file
    file_name = directory + '/mapping_' + label.split('_')[1] + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier', 'pharmgkb_id', 'resource', 'how_mapped', 'xrefs'])

    # tsv_file for new
    file_name_new = directory + '/new_' + label.split('_')[1] + '.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_writer_new = csv.writer(file_new, delimiter='\t')
    csv_writer_new.writerow(['identifier', 'dbid', 'how_mapped', 'xrefs'])

    # tsv file for not mapping
    not_mapped_file = open(directory + '/not_mapping_' + label.split('_')[1] + '.tsv', 'w', encoding='utf-8')
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

    for record in results:
        result = record.data()['n']
        name = result['name']
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
            csv_writer_not.writerow([identifier, result['name']])
            if name.startswith('rs') and name[2].isdigit():
                xrefs = ['dbSNP:' + name]
                if identifier:
                    xrefs.append('PharmGKB:' + identifier)
                csv_writer_new.writerow([identifier, name, 'new', '|'.join(xrefs)])

    print('number of variant which mapped:', counter_map)
    print('number of mapped:', len(set_of_all_tuples))
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
        query = '''  MATCH (n:%s), (c:%s{identifier:line.identifier}) Where n.id=line.pharmgkb_id or n.name=line.pharmgkb_id  Set c.pharmgkb='yes', c.resource=split(line.resource,'|'), c.xrefs=split(line.xrefs,'|') Create (c)-[:equal_to_%s_phamrgkb{how_mapped:line.how_mapped}]->(n)'''
        query = query % (label, mapped_label, label.split('_')[1].lower())
    else:
        query = '''  MATCH (n:%s) Where n.id=line.identifier or n.name=line.identifier   Create (c:%s :GeneVariant{identifier:line.dbid, name:n.name, synonyms:n.synonyms, location:n.location, pharmgkb:'yes', resource:["PharmGKB"], xrefs:split(line.xrefs,"|") ,license:"%s" , source:"dbSNP from PharmGKB"})-[:equal_to_%s_phamrgkb{how_mapped:line.how_mapped}]->(n) '''
        query = query % (label, mapped_label, license, label.split('_')[1].lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in variant from pharmebinet')

    load_db_info_in()

    for label in ['PharmGKB_Variant', 'PharmGKB_Haplotype']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Load in %s from pharmgb in' % (label))

        load_pharmgkb_in(label, 'variant', 'Variant')

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
