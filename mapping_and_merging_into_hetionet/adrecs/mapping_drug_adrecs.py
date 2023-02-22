import csv
import sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary name to ids
dict_name_to_id = {}

# dictionary source to source id to chemical ids
dict_source_to_source_id_to_chemical_ids = {}


def fill_dict_source_with_information(source, source_id, identifier):
    """
    fill the dictionary source to source ids to chemical ids
    :param source: string
    :param source_id: string
    :param identifier: string
    :return:
    """
    if source not in dict_source_to_source_id_to_chemical_ids:
        dict_source_to_source_id_to_chemical_ids[source] = {}
    pharmebinetutils.add_entry_to_dict_to_set(dict_source_to_source_id_to_chemical_ids[source], source_id, identifier)


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.synonyms, n.resource, n.xrefs'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, resource, xrefs] = record.values()
        dict_node_id_to_resource[identifier] = resource

        name = name.lower()
        if name not in dict_name_to_id:
            dict_name_to_id[name] = set()
        dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if synonym not in dict_name_to_id:
                    dict_name_to_id[synonym] = set()
                dict_name_to_id[synonym].add(identifier)
        if xrefs:
            for xref in xrefs:
                [source, xref] = xref.split(':', 1)
                if source == 'KEGG Compound' or source == 'KEGG Drug':
                    fill_dict_source_with_information('kegg', xref, identifier)
                elif source == 'MESH':
                    fill_dict_source_with_information('mesh', xref, identifier)
                elif source == 'PubChem Compound':
                    fill_dict_source_with_information('pubchem', xref, identifier)
                elif source == 'Therapeutic Targets Database':
                    fill_dict_source_with_information('ttd', xref, identifier)

    print('number of Chemical in database', len(dict_node_id_to_resource))


def prepare_query(file_name, db_label, adrecs_label, db_id, adrecs_id_internal, adrecs_id):
    """
    prepare query for integration
    :param file_name:string
    :param db_label: string
    :param adrecs_label: string
    :param db_id: string
    :param adrecs_id_internal:string
    :param adrecs_id: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = ''' MATCH (n:%s{identifier:line.%s}), (g:%s{%s:line.%s}) Set n.resource=split(line.resource,"|"), n.adrecs_target='yes' Create (n)-[:equal_adrecs_target_%s{how_mapped:line.how_mapped}]->(g)'''
    query = query % (db_label, db_id, adrecs_label, adrecs_id_internal, adrecs_id, db_label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/{director}/{file_name}', query)
    cypher_file.write(query)


def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id, csv_mapping, how_mapped):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    csv_mapping.writerow([identifier_db, identifier_act_id,
                          pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier_db], 'ADReCs'),
                          how_mapped])


def check_for_mapping_in_source_dictionary(source, source_id, dict_node_id_to_resource, identifier, csv_mapping,
                                           counter_mapping):
    found_mapping = False
    if source_id in dict_source_to_source_id_to_chemical_ids[source]:
        counter_mapping += 1
        found_mapping = True
        for chemical_id in dict_source_to_source_id_to_chemical_ids[source][source_id]:
            add_to_file(dict_node_id_to_resource, chemical_id, identifier, csv_mapping, source)
    return found_mapping, counter_mapping


def get_all_adrecs_target_and_map(db_label, dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'act_id', 'resource', 'how_mapped'])

    prepare_query(file_name, db_label, 'ADReCS_Drug', 'db_id', 'id', 'act_id')

    # get data
    query = '''MATCH (n:ADReCS_Drug) RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    for record in results:
        node = record.data()['n']
        # rs or a name
        identifier = node['id']
        name = node['name'].lower()
        drugbank_id = node['drugbank_id'] if 'drugbank_id' in node else ''
        mesh_id = node['mesh_id'] if 'mesh_id' in node else ''
        kegg_id = node['kegg_id'] if 'kegg_id' in node else ''
        pubchem_id = node['pubchem_id'] if 'pubchem_id' in node else ''
        ttd_id = node['ttd_id'] if 'ttd_id' in node else ''
        found_mapping = False
        if drugbank_id != '':
            if drugbank_id in dict_node_id_to_resource:
                counter_mapping += 1
                found_mapping = True
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'drugbank')

        if found_mapping:
            continue

        if name in dict_name_to_id:
            counter_mapping += 1
            found_mapping = True
            for drugbank_id in dict_name_to_id[name]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'name')

        if found_mapping:
            continue

        if pubchem_id != '':
            found_mapping, counter_mapping = check_for_mapping_in_source_dictionary('pubchem', pubchem_id,
                                                                                    dict_node_id_to_resource,
                                                                                    identifier, csv_mapping,
                                                                                    counter_mapping)

        if found_mapping:
            continue

        if kegg_id != '':
            found_mapping, counter_mapping = check_for_mapping_in_source_dictionary('kegg', kegg_id,
                                                                                    dict_node_id_to_resource,
                                                                                    identifier, csv_mapping,
                                                                                    counter_mapping)

        if found_mapping:
            continue

        if ttd_id != '':
            found_mapping, counter_mapping = check_for_mapping_in_source_dictionary('ttd', ttd_id,
                                                                                    dict_node_id_to_resource,
                                                                                    identifier, csv_mapping,
                                                                                    counter_mapping)

        if found_mapping:
            continue

        if mesh_id != '':
            if mesh_id in dict_node_id_to_resource:
                counter_mapping += 1
                found_mapping = True
                add_to_file(dict_node_id_to_resource, mesh_id, identifier, csv_mapping, 'mesh')

        if found_mapping:
            continue

        counter_not_mapped += 1
        print(' not in database :O')
        print(identifier)
    print('mapped:', counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        director = sys.argv[2]
    else:
        sys.exit('need a path adrecs-target and directory')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')

    # dict node id to resource
    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all drugs from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_adrecs_target_and_map('Chemical', dict_node_id_to_resource)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
