import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary with disease id as key and the whole node as value
dict_disease_pharmebinet_to_resource = {}

# dictionary synonyms/name disease ids
dict_synonyms_to_diseases_ids = {}
# dictionary synonyms/name symptom ids
dict_synonyms_to_symptom_ids = {}

# dictionary umls to disease ids
dict_umls_to_diseases_ids = {}
# dictionary umls to symptom ids
dict_umls_to_symptom_ids = {}

# dictionary mesh to disease ids
dict_mesh_to_diseases_ids = {}
# dictionary mesh to symptom ids
dict_mesh_to_symptom_ids = {}

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


def load_pharmebinet_disease_in(label, dict_synonyms_to_node_ids, dict_umls_to_node_ids, dict_mesh_to_node_ids):
    query = f'''MATCH (n:{label}) RETURN n.identifier,n'''
    results = g.run(query)

    for record in results:
        [identifier, node] = record.values()
        dict_disease_pharmebinet_to_resource[identifier] = dict(node)['resource']
        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_node_ids, name, identifier)

        synonyms = node['synonyms']
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym)
                pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_node_ids, synonym, identifier)
        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('UMLS:'):
                xref = xref.split(':', 1)[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_umls_to_node_ids, xref, identifier)
            if xref.startswith('MESH:'):
                xref = xref.split(':', 1)[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_mesh_to_node_ids, xref, identifier)

    print('length of compound in pharmebinet:' + str(len(dict_disease_pharmebinet_to_resource)))


def prepare_csv_file_and_cypher_file(label, label_2):
    """
    Prpare csv file and cypher query.
    :return:
    """
    file_name = f'disease/map_{label}_{label_2}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['med_id', 'id', 'resource', 'how_mapped'])

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = f'Match (n:{label}{{id:line.med_id}}), (r:{label_2}{{identifier:line.id}}) Set r.resource=split(line.resource,"|"), r.med_rt="yes" Create (r)-[:equal_disease_med_rt{{how_mapped:line.how_mapped}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              'mapping_and_merging_into_hetionet/med_rt/' + file_name, query)
    cypher_file.write(query)

    return csv_writer


def load_med_rt_drug_in(label):
    query = f'''MATCH (n:{label}) RETURN n'''
    results = g.run(query)

    csv_writer_disease = prepare_csv_file_and_cypher_file(label, 'Disease')
    csv_writer_symptom = prepare_csv_file_and_cypher_file(label, 'Symptom')
    count = 0
    counter_mapped = 0

    set_of_mapping_pairs = set()

    for record in results:
        result = record.data()['n']
        count += 1
        identifier = result['id']
        xref = result['xref'] if 'xref' in result else ''
        name = result['name'].lower()
        name = name.replace(' (product)', '').replace(' (substance)', '').replace(' (medicinal product)', '')

        mapped = False

        if name in dict_synonyms_to_diseases_ids:
            mapped = True
            counter_mapped += 1
            for disease_id in dict_synonyms_to_diseases_ids[name]:
                if (identifier, disease_id) in set_of_mapping_pairs:
                    continue
                set_of_mapping_pairs.add((identifier, disease_id))
                csv_writer_disease.writerow([identifier, disease_id, pharmebinetutils.resource_add_and_prepare(
                    dict_disease_pharmebinet_to_resource[disease_id], 'MED-RT'), 'name'])

        if mapped:
            continue



        query = ('Select Distinct CUI  From MRCONSO Where STR ="%s" ;')
        query = query % (name)

        cur = con.cursor()
        rows_counter = cur.execute(query)

        set_cuis = set()

        if rows_counter > 0:
            for (cui,) in cur:
                set_cuis.add(cui)
                if cui in dict_umls_to_diseases_ids:
                    mapped = True
                    for disease_id in dict_umls_to_diseases_ids[cui]:
                        if (identifier, disease_id) in set_of_mapping_pairs:
                            continue
                        set_of_mapping_pairs.add((identifier, disease_id))
                        csv_writer_disease.writerow([identifier, disease_id, pharmebinetutils.resource_add_and_prepare(
                            dict_disease_pharmebinet_to_resource[disease_id], 'MED-RT'), 'umls'])

        if mapped:
            counter_mapped += 1
            continue

        if name in dict_synonyms_to_symptom_ids:
            mapped = True
            counter_mapped += 1
            for symptom_id in dict_synonyms_to_symptom_ids[name]:
                if (identifier, symptom_id) in set_of_mapping_pairs:
                    continue
                set_of_mapping_pairs.add((identifier, symptom_id))
                csv_writer_symptom.writerow([identifier, symptom_id, pharmebinetutils.resource_add_and_prepare(
                    dict_disease_pharmebinet_to_resource[symptom_id], 'MED-RT'), 'name'])

        if mapped:
            continue

        if xref.startswith('MeSH'):
            mesh_id = xref.split(':')[1]
            if mesh_id in dict_mesh_to_symptom_ids:
                mapped = True
                counter_mapped += 1
                for symptom_id in dict_mesh_to_symptom_ids[mesh_id]:
                    if (identifier, symptom_id) in set_of_mapping_pairs:
                        continue
                    set_of_mapping_pairs.add((identifier, symptom_id))
                    csv_writer_symptom.writerow([identifier, symptom_id, pharmebinetutils.resource_add_and_prepare(
                        dict_disease_pharmebinet_to_resource[symptom_id], 'MED-RT'), 'mesh'])

        if mapped:
            continue

        if len(set_cuis) > 0:
            for cui in set_cuis:
                if cui in dict_umls_to_symptom_ids:
                    mapped = True
                    for symptom_id in dict_umls_to_symptom_ids[cui]:
                        if (identifier, symptom_id) in set_of_mapping_pairs:
                            continue
                        set_of_mapping_pairs.add((identifier, symptom_id))
                        csv_writer_symptom.writerow([identifier, symptom_id, pharmebinetutils.resource_add_and_prepare(
                            dict_disease_pharmebinet_to_resource[symptom_id], 'MED-RT'), 'umls'])

        if mapped:
            counter_mapped += 1
            continue

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
    print('Load in disease from pharmebinet')

    load_pharmebinet_disease_in('Disease', dict_synonyms_to_diseases_ids, dict_umls_to_diseases_ids,
                                dict_mesh_to_diseases_ids)

    load_pharmebinet_disease_in('Symptom', dict_synonyms_to_symptom_ids, dict_umls_to_symptom_ids,
                                dict_mesh_to_symptom_ids)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in drug from med-rt')

    for label in ['other_MEDRT', 'Disease_Finding_MEDRT']:
        load_med_rt_drug_in(label)

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
