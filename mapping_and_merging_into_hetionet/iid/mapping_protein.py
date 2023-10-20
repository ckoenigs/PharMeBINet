import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
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
        gene_symbols = node['gene_name'] if 'gene_name' in node else []
        for gene_symbol in gene_symbols:
            if gene_symbol not in dict_gene_symbol_to_id:
                dict_gene_symbol_to_id[gene_symbol] = set()
            dict_gene_symbol_to_id[gene_symbol].add(identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv writer
    """
    # file from relationship between gene and variant
    file_name = 'protein/iid_protein_to_protein'
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['iid_uniprot_id', 'uniprot_id', 'resource', 'mapped_with']
    csv_mapping.writerow(header)
    cypher_file = open('protein/cypher.cypher', 'w', encoding='utf-8')

    query = ''' Match (n:protein_IID{identifier:line.iid_uniprot_id}), (v:Protein{identifier:line.uniprot_id}) Set v.iid='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_iid_protein{mapped_with:line.mapped_with}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/iid/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


'''
Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
'''


def load_all_iid_protein_and_finish_the_files(csv_mapping):
    query = "MATCH (n:protein_IID) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['identifier']

        if identifier in dict_protein_id_to_resource:
            csv_mapping.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_protein_id_to_resource[identifier], 'IID'), 'id'])
        elif identifier in dict_alt_id_to_id:
            for protein_id in dict_alt_id_to_id[identifier]:
                csv_mapping.writerow(
                    [identifier, protein_id,
                     pharmebinetutils.resource_add_and_prepare(dict_protein_id_to_resource[protein_id], 'IID'),
                     'alternative id'])
        else:
            # gene_symbols= node['symbols'] if 'symbols' in node else []
            # set_of_mapped_uniprot_ids=set()
            # found_a_map=False
            # for gene_symbol in gene_symbols:
            #     if gene_symbol in dict_gene_symbol_to_id:
            #         for protein_id in dict_gene_symbol_to_id[gene_symbol]:
            #             if protein_id not in set_of_mapped_uniprot_ids:
            #                 csv_mapping.writerow([identifier, protein_id, resource(protein_id),
            #                                       'gene symbol'])
            #                 set_of_mapped_uniprot_ids.add(protein_id)
            # #                 found_a_map=True
            # if not found_a_map:
            counter_not_mapped += 1
            print(identifier)
    print('number of not mapped proteins:', counter_not_mapped)
    print('number of all proteins:', counter_all)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path iid protein')

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

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all iid protein from database')

    load_all_iid_protein_and_finish_the_files(csv_mapping)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
