import sys, csv
import datetime

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def database_connection():
    """
    Create connection to database
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def prepare_tsv_file():
    """
    Prepare mapping file as TSV file
    :return:
    """

    # generate tsv files
    global tsv_map_nodes

    # tsv with nodes which needs to be updated
    map_node_file = open('output/map_compounds.tsv', 'w', encoding='utf-8')
    tsv_map_nodes = csv.writer(map_node_file, delimiter='\t')
    tsv_map_nodes.writerow(['id', 'hetionet_id', 'how_mapped', 'resource'])


# dictionary mondo id to mondo name
dict_mondo_id_to_name = {}

'''
generate cypher queries to integrate and merge compound nodes
'''


def generate_cypher_queries():
    # cypher file to integrate mondo
    with open('output/cypher_drug.cypher', 'w', encoding='utf-8') as cypher_file:
        query = ''' Match (a:Compound_hetionet{identifier:line.hetionet_id}), (b:Compound{identifier:line.id})  Set b.hetionet="yes", b.resource=split(line.resource,"|") Create (b)-[:equal_to_hetionet_compound{how_mapped:line.how_mapped}]->(a) '''

        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  'mapping_and_merging_into_hetionet/hetionet/output/map_compounds.tsv',
                                                  query)
        cypher_file.write(query)


# dictionary mondo to resource
dict_compound_to_resource = {}

# dictionary alternative_ids to ids
dict_alternative_id_to_ids = {}

# dictionary name to mondo
dict_name_to_identifier = {}

# dictionary inchikey to mondo
dict_inchikey_to_identifier = {}


def load_in_all_compound_in_dictionary():
    """
    Load all Compounds from PharMeBINet in dictionaries
    :return:
    """
    query = ''' MATCH (n:Compound) RETURN n.identifier, n.resource, n.alternative_ids, n.inchikey, n.name'''
    results = g.run(query)
    for record in results:
        [identifier, resource, alternative_ids, inchikey, name] = record.values()
        dict_compound_to_resource[identifier] = set(resource)

        alternative_ids = alternative_ids if alternative_ids else []
        for alternative_id in alternative_ids:
            if alternative_id.startswith('DB'):
                pharmebinetutils.add_entry_to_dict_to_set(dict_alternative_id_to_ids, alternative_id, identifier)
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_identifier, name.lower(), identifier)
        pharmebinetutils.add_entry_to_dict_to_set(dict_inchikey_to_identifier, inchikey, identifier)


def mapping_hetionet_Compound():
    """
    Map hetionet compound to compounds
    :return:
    """
    query = 'MATCH (n:Compound_hetionet) RETURN n.identifier, n.name, n.inchikey'
    results = g.run(query)
    counter = 0
    counter_mapped = 0
    for record in results:
        counter += 1
        [identifier, name, inchikey] = record.values()

        is_mapped = False

        name = name.lower()
        inchikey = inchikey.split('=')[1]

        if identifier in dict_compound_to_resource:
            is_mapped = True
            tsv_map_nodes.writerow([identifier, identifier, 'id',
                                    pharmebinetutils.resource_add_and_prepare(dict_compound_to_resource[identifier],
                                                                              'Hetionet')])

        if is_mapped:
            counter_mapped += 1
            continue

        if inchikey in dict_inchikey_to_identifier:
            for db_id in dict_inchikey_to_identifier[inchikey]:
                is_mapped = True
                tsv_map_nodes.writerow([db_id, identifier, 'inchikey', pharmebinetutils.resource_add_and_prepare(
                    dict_compound_to_resource[db_id],
                    'Hetionet')])

        if is_mapped:
            counter_mapped += 1
            continue

        if identifier in dict_alternative_id_to_ids:
            for db_id in dict_alternative_id_to_ids[identifier]:
                is_mapped = True
                tsv_map_nodes.writerow([db_id, identifier, 'alternative_id', pharmebinetutils.resource_add_and_prepare(
                    dict_compound_to_resource[db_id],
                    'Hetionet')])

        if is_mapped:
            counter_mapped += 1
            continue

        if name in dict_name_to_identifier:
            for db_id in dict_name_to_identifier[name]:
                is_mapped = True
                tsv_map_nodes.writerow([db_id, identifier, 'name', pharmebinetutils.resource_add_and_prepare(
                    dict_compound_to_resource[db_id],
                    'Hetionet')])

        if is_mapped:
            counter_mapped += 1
            continue

    print('all hetionet compound:', counter)
    print('mapped:', counter_mapped)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all properties from mondo and put them as header into the tsv files ')

    prepare_tsv_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate cypher file')

    generate_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load compound')

    load_in_all_compound_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('map compound')

    mapping_hetionet_Compound()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
