import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary with name pharmebinet as key and uniprotID as value
dict_uniprot_id_to_name = {}

# dictionary with name pharmebinet as key and alternative ids as value
dict_name_alt_ids_pharmebinet = {}

# dictionary with name reactome as key and uniprotID as value
dict_name_uniprot_reactome = {}

# dictionary with uniprotID as key and resource as value
dict_uniprot_to_resource = {}

dict_alternative_id_to_protein_id = {}

'''
load in all uniprotIDs of Protein from pharmebinet in a dictionary
'''


def load_pharmebinet_uniprotIDs_in():
    query = '''MATCH (n:Protein) RETURN n.identifier, n.name, n.alternative_ids, n.resource'''
    results = graph_database.run(query)

    for record in results:
        [identifier, name, alternative_ids, resource] = record.values()
        dict_uniprot_id_to_name[identifier] = name.lower()
        dict_uniprot_to_resource[identifier] = resource if resource else []
        if alternative_ids:
            for alt_id in alternative_ids:
                # print(alt_id)
                dict_alternative_id_to_protein_id[alt_id] = identifier

    print('number of uniprotIDs in pharmebinet Protein:' + str(len(dict_uniprot_id_to_name)))


file_not_mapped_uniprotIDs = open('uniprotIDs/not_mapped_uniprotIDs.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_uniprotIDs, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])

file_mapped_uniprotIDs = open('uniprotIDs/mapped_uniprotIDs.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_uniprotIDs, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_pharmebinet', 'resource'])

'''
load all reactome uniprotIDs ReferenceEntity and check if they are in pharmebinet or not
'''


def load_reactome_referenceEntity_in():
    global highest_identifier
    query = '''MATCH (n:PhysicalEntity_reactome)-[r:referenceEntity]-(a:ReferenceEntity_reactome) WHERE a.databaseName = 'UniProt' RETURN a.identifier, a.name, n.name'''
    # p = (n:PhysicalEntity) - [r:referenceEntity]-(a:ReferenceEntity) Where a.databaseName = 'UniProt' RETURN n, r, a Limit 25
    results = graph_database.run(query)
    set_pairs = set()
    counter_map_with_id = 0
    for record in results:
        [identifier, names, physicalEntityNames] = record.values()
        name = names[0].lower() if names else physicalEntityNames[0].lower()
        if identifier in dict_uniprot_id_to_name:
            if not (identifier, identifier) in set_pairs:
                counter_map_with_id += 1
                # print(identifier)
                csv_mapped.writerow([identifier, identifier,
                                     pharmebinetutils.resource_add_and_prepare(dict_uniprot_to_resource[identifier],
                                                                               'Reactome')])
                set_pairs.add((identifier, identifier))
        elif identifier in dict_alternative_id_to_protein_id:
            pharmebinet_uniprotID = dict_alternative_id_to_protein_id[identifier]
            if not (identifier, pharmebinet_uniprotID) in set_pairs:
                csv_mapped.writerow([identifier, pharmebinet_uniprotID,
                                     pharmebinetutils.resource_add_and_prepare(
                                         dict_uniprot_to_resource[pharmebinet_uniprotID],
                                         'Reactome')])
                set_pairs.add((identifier, pharmebinet_uniprotID))
        else:
            csv_not_mapped.writerow([identifier, name])

    print('number of mapping with id:' + str(counter_map_with_id))


'''
generate connection between mapping ReferenceEntity of reactome and Protein pharmebinet and generate new edges
'''


def create_cypher_file():
    cypher_file = open('output/cypher_mapping2.cypher', 'a', encoding="utf-8")
    query = ''' MATCH (d:Protein{identifier:line.id_pharmebinet}),(c:ReferenceEntity_reactome{identifier:line.id}) CREATE (d)-[: equal_to_reactome_uniprot]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/uniprotIDs/mapped_uniprotIDs.tsv',
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())
    print('Load all uniprotIDs from pharmebinet Protein into a dictionary')

    load_pharmebinet_uniprotIDs_in()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())
    print('Load all reactome uniprotIDs from ReferenceEntity from neo4j into a dictionary')

    load_reactome_referenceEntity_in()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())
    print('Integrate new edges to reactome ')

    create_cypher_file()

    driver.close()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
