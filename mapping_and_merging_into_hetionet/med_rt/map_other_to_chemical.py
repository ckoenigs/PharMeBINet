import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary with chemical id as key and the whole node as value
dict_chemical_pharmebinet_to_resource = {}

# dictionary synonyms/name/brands chemical ids
dict_synonyms_to_chemicals_ids = {}

# dictionary mesh id to chemicals ids
dict_mesh_id_to_chemicals_ids = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


'''
load in all compound from pharmebinet in a dictionary
'''


def load_pharmebinet_chemical_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier,n'''
    results = g.run(query)

    for record in results:
        [identifier, node] = record.values()
        dict_chemical_pharmebinet_to_resource[identifier] = dict(node)['resource']
        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_chemicals_ids, name, identifier)

        synonyms = node['synonyms']
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_chemicals_ids, synonym, identifier)
        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('MESH:'):
                xref = xref.split(':', 1)[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_mesh_id_to_chemicals_ids, xref, identifier)

    print('length of compound in pharmebinet:' + str(len(dict_chemical_pharmebinet_to_resource)))


def prepare_csv_file_and_cypher_file(label):
    """
    Prpare csv file and cypher query.
    :return:
    """
    file_name = f'chemical/map_{label}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['med_id', 'id', 'resource', 'how_mapped'])

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = f'Match (n:{label}{{id:line.med_id}}), (r:Chemical{{identifier:line.id}}) Set r.resource=split(line.resource,"|"), r.med_rt="yes" Create (r)-[:equal_chemical_med_rt{{how_mapped:line.how_mapped}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              'mapping_and_merging_into_hetionet/med_rt/' + file_name, query)
    cypher_file.write(query)

    return csv_writer


def load_med_rt_drug_in(label):
    query = f'''MATCH (n:{label}) RETURN n'''
    results = g.run(query)

    csv_writer = prepare_csv_file_and_cypher_file(label)
    count = 0
    counter_mapped = 0

    set_of_mapping_pairs = set()

    for record in results:
        result = record.data()['n']
        count += 1
        identifier = result['id']
        name = result['name'].lower()
        name = name.replace(' (product)', '').replace(' (substance)', '').replace(' (medicinal product)', '')
        namespace = result['namespace']
        mapped = False

        if name in dict_synonyms_to_chemicals_ids:
            mapped = True
            counter_mapped += 1
            for chemical_id in dict_synonyms_to_chemicals_ids[name]:
                if (identifier, chemical_id) in set_of_mapping_pairs:
                    continue
                set_of_mapping_pairs.add((identifier, chemical_id))
                csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                    dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'name'])

        if mapped:
            continue

        if namespace =='MeSH':
            if identifier in dict_chemical_pharmebinet_to_resource:
                mapped = True
                counter_mapped += 1
                if (identifier, identifier) in set_of_mapping_pairs:
                    continue
                set_of_mapping_pairs.add((identifier, identifier))
                csv_writer.writerow([identifier, identifier, pharmebinetutils.resource_add_and_prepare(
                    dict_chemical_pharmebinet_to_resource[identifier], 'MED-RT'), 'mesh'])

        if mapped:
            continue

        # many mappings are good but also a lot not so good because they are salts
        # if namespace=='MeSH':
        #     query = ('Select Distinct STR  From MRCONSO Where SCUI ="%s" ;')
        #     query = query % (identifier)
        #
        #     cur = con.cursor()
        #     rows_counter = cur.execute(query)
        #
        #     if rows_counter > 0:
        #         for (synonym,) in cur:
        #             if synonym in dict_synonyms_to_chemicals_ids:
        #                 mapped = True
        #                 for chemical_id in dict_synonyms_to_chemicals_ids[synonym]:
        #                     if (identifier, chemical_id) in set_of_mapping_pairs:
        #                         continue
        #                     set_of_mapping_pairs.add((identifier, chemical_id))
        #                     csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
        #                         dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'name_umls_mesh'])
        #
        # if mapped:
        #     counter_mapped += 1
        #     continue

    print('number of diseases in med-rt', label, count)
    print('number of mapped diseases in med-rt', label, counter_mapped)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in chemical from pharmebinet')

    load_pharmebinet_chemical_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in drug from med-rt')

    load_med_rt_drug_in('other_MEDRT')

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
