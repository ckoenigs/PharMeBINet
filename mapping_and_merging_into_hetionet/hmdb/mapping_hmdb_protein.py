import datetime
import sys, csv

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
    g = driver.session(database='graph')


# dictionary protein id to resource
dict_protein_id_to_resource = {}

# dictionary alternative protein id to ids
dict_alt_id_to_id = {}

# dictionary from gene symbol to protein id
dict_gene_symbol_to_id = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_protein_from_database_and_add_to_dict():
    query = "MATCH (n:Protein) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_protein_id_to_resource[identifier] = node['resource']
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for alternative_id in alternative_ids:
            if alternative_id not in dict_alt_id_to_id:
                dict_alt_id_to_id[alternative_id] = set()
            dict_alt_id_to_id[alternative_id].add(identifier)
    print('number of proteins:', len(dict_protein_id_to_resource))


def generate_files(path_of_directory, label):
    """
    generate cypher file and tsv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'protein/hmdb_protein_to_%s' % label
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['identifier', 'other_id', 'resource', 'mapped_with']
    csv_mapping.writerow(header)

    query = '''Match (n:Protein_HMDB{identifier:line.identifier}), (v:%s{identifier:line.other_id}) Set v.hmdb='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_hmdb_%s{how_mapped:line.mapped_with}]->(n)'''
    query = query % (label, label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hmdb/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


'''
Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
'''


def load_all_hmdb_protein_and_map(csv_mapping_protein):
    query = "MATCH (n:Protein_HMDB) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0

    file_not_mapped = open('protein/not_mapped.tsv', 'w', encoding='utf-8')
    csv_not_mapped = csv.writer(file_not_mapped, delimiter='\t')
    csv_not_mapped.writerow(['identifier', 'name', 'xrefs'])
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['identifier']
        xrefs = node['xrefs'] if 'xrefs' in node else []
        uniprot_name = node['uniprot_name'] if 'uniprot_name' in node else ''

        found_mapping = False
        for xref in xrefs:
            split_xref = xref.split(':')
            if split_xref[0] == 'uniprot_id':
                uniprot_id = split_xref[1]
                if uniprot_id in dict_protein_id_to_resource:
                    found_mapping = True
                    csv_mapping_protein.writerow(
                        [identifier, uniprot_id,
                         pharmebinetutils.resource_add_and_prepare(dict_protein_id_to_resource[uniprot_id], 'HMDB'),
                         'id'])
                # elif uniprot_id in dict_alt_id_to_id:
                #     found_mapping=True
                #     for protein_id in dict_alt_id_to_id[uniprot_id]:
                #         csv_mapping_protein.writerow(
                #             [identifier, protein_id, resource(dict_protein_id_to_resource[protein_id]), 'alternative id'])

        if not found_mapping:
            counter_not_mapped += 1
            csv_not_mapped.writerow([identifier, uniprot_name, '|'.join(xrefs)])
    print('number of not mapped proteins:', counter_not_mapped)
    print('number of all proteins:', counter_all)


def main():
    print(datetime.datetime.now())

    global path_of_directory, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hmdb protein')

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Protein from database')

    load_protein_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping_protein = generate_files(path_of_directory, 'Protein')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all hmdb protein from database')

    load_all_hmdb_protein_and_map(csv_mapping_protein)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
