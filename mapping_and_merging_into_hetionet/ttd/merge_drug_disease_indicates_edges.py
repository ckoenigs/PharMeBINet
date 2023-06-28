import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary chemical-disease pair to resource
dict_chemical_disease_pair_to_resource = {}


def load_existing_pairs():
    """
    Load all existing pairs into a dictionary
    :return:
    """
    query = 'Match (n:Chemical)-[r:TREATS_CHtD]-(m:Disease) Return n.identifier, r.resource, m.identifier'
    for record in g.run(query):
        [chemical_id, resource, disease_id] = record.values()
        dict_chemical_disease_pair_to_resource[(chemical_id, disease_id)] = resource


def generate_csv_and_tsv(label):
    """
    Generate tsv file and add cypher query
    :return:
    """
    file_name = f'edges/drug_{label}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['chemical_id', 'disease_id', 'resource', 'ttd_id'])


    query = f' Match (c:Chemical{{identifier:line.chemical_id}}), (d:{label}{{identifier:line.disease_id}}) Merge (c)-[l:TREATS_CHt{label[0]}]->(d) On Create Set l.ttd="yes", l.resource=["TTD"], l.source="TTD", l.url="https://db.idrblab.net/ttd/data/drug/details/"+line.ttd_id, l.license="No license" On Match Set l.resource=split(line.resource,"|"), l.ttd="yes" '
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                              query)
    cypher_file.write(query)
    return csv_writer


def get_ttd_drug_disease_edge(label):
    """
    Load all pairs and write into tsv file
    :return:
    """
    csv_writer = generate_csv_and_tsv(label)

    set_of_pairs = set()

    query = f'Match p=(a:Chemical)--(b:TTD_Drug)-[r:TTD_INDICATES]-(:TTD_Disease)--(c:{label}) Return Distinct a.identifier, b.id, r.clinical_status, c.identifier'
    for record in g.run(query):
        [chemical_id, ttd_id, rela_clinical_status, disease_id] = record.values()
        if (chemical_id, disease_id) in set_of_pairs:
            print('double :O ', chemical_id, disease_id)
        set_of_pairs.add((chemical_id, disease_id))
        if (chemical_id, disease_id) in dict_chemical_disease_pair_to_resource:
            csv_writer.writerow([chemical_id, disease_id, pharmebinetutils.resource_add_and_prepare(
                dict_chemical_disease_pair_to_resource[(chemical_id, disease_id)], 'TTD'), ttd_id])
            continue
        csv_writer.writerow([chemical_id, disease_id, "TTD", ttd_id])


def main():
    global path_of_directory, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd ')

    cypher_file = open('output/cypher_edges.cypher', 'w', encoding='utf-8')

    print(datetime.datetime.now())
    print('create connection')
    create_connection_with_neo4j()

    print('#' * 50)
    print(datetime.datetime.now())
    print('load chemical-disease information')
    load_existing_pairs()

    print('#' * 50)
    print(datetime.datetime.now())
    print('map compound')
    for label in ['Disease','Symptom']:
        get_ttd_drug_disease_edge(label)

    cypher_file.close()

    print('#' * 50)
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
