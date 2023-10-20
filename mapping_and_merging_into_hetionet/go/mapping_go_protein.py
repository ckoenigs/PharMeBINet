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


# dictionary uniprot_id to resource
dict_uniprot_id_to_resource = {}

# dictionary alternative uniprot id to uniprot ids
dict_alternative_uniprot_id_to_identifiers = {}


def generate_files(label, cypher_file):
    """
    generate cypher file and tsv file
    :return: csv writer
    """
    # file from relationship between gene and variant
    file_name = 'protein/go_protein_to_%s' % label
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    tsv_mapping = csv.writer(file, delimiter='\t')
    header = ['identifier', 'other_id', 'resource', 'mapped_with']
    tsv_mapping.writerow(header)

    file_name_not = 'protein/not_go_protein_to_%s' % label
    file_not = open(file_name_not + '.tsv', 'w', encoding='utf-8')
    tsv_not_mapping = csv.writer(file_not, delimiter='\t')
    header = ['identifier', 'name']
    tsv_not_mapping.writerow(header)

    query = '''Match (n:protein_go{identifier:line.identifier}), (v:%s{identifier:line.other_id}) Set v.go='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_go_%s{how_mapped:line.mapped_with}]->(n)'''
    query = query % (label, label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/go/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return tsv_mapping, tsv_not_mapping


'''
Load all Genes from my database  and add them into a dictionary
'''


def load_protein_and_add_to_dictionary():
    query = "MATCH (n:Protein) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']

        dict_uniprot_id_to_resource[identifier] = node['resource']
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for alternative_id in alternative_ids:
            pharmebinetutils.add_entry_to_dict_to_set(dict_alternative_uniprot_id_to_identifiers, alternative_id,
                                                      identifier)
        gene_symbols = node['gene_name'] if 'gene_name' in node else []

    print('number of proteins:', len(dict_uniprot_id_to_resource))


# dictionary gene id to resource
dict_gene_id_to_resource = {}

# dictionary gene symbol to gene ids
dict_symbol_to_gene_ids = {}

# dictionary offical gene symbol to gene ids
dict_unique_gene_symbol_to_gene_ids = {}

# dictionary synonym to gene ids
dict_synonyms_to_gene_ids = {}


def load_gene_and_add_to_dictionary():
    """
    Load gene symbol and source information into dictionaries
    :return:
    """
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']

        dict_gene_id_to_resource[identifier] = node['resource']
        gene_symbol = node['gene_symbol']
        pharmebinetutils.add_entry_to_dict_to_set(dict_unique_gene_symbol_to_gene_ids, gene_symbol.lower(), identifier)
        gene_symbols = node['gene_symbols'] if 'gene_symbols' in node else []
        for gene_symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_symbol_to_gene_ids, gene_symbol.lower(), identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_gene_ids, synonym.lower(), identifier)

    print('number of gene:', len(dict_gene_id_to_resource))


'''
Load all pharmacologic class of drugbank and map to the pc from my database and write into file
'''


def load_all_protein_form_go_and_map_and_write_to_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    tsv_writer, tsv_not_mapped = generate_files('Protein', cypher_file)
    tsv_writer_gene, tsv_not_mapped_gene = generate_files('Gene', cypher_file)

    query = "MATCH (n:protein_go) RETURN n"
    results = g.run(query)
    counter = 0
    counter_not_mapped = 0
    count_mapped_symbol = 0
    count_not_mapped_gene = 0
    for record in results:
        node = record.data()['n']
        counter += 1
        identifier = node['identifier']
        if identifier in dict_uniprot_id_to_resource:
            tsv_writer.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_uniprot_id_to_resource[identifier], 'GO'), 'id_mapped'])
        elif identifier in dict_alternative_uniprot_id_to_identifiers:
            for real_id in dict_alternative_uniprot_id_to_identifiers[identifier]:
                tsv_writer.writerow(
                    [identifier, real_id,
                     pharmebinetutils.resource_add_and_prepare(dict_uniprot_id_to_resource[real_id], 'GO'),
                     'alt_id_mapped'])
        else:
            counter_not_mapped += 1
            tsv_not_mapped.writerow([identifier, node['name']])

        symbol = node['symbol'].lower() if 'symbol' in node else None
        if not symbol:
            continue
        if symbol in dict_unique_gene_symbol_to_gene_ids:
            count_mapped_symbol += 1
            for gene_id in dict_unique_gene_symbol_to_gene_ids[symbol]:
                tsv_writer_gene.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], 'GO'),
                     'unique_symbol'])
        elif symbol in dict_symbol_to_gene_ids:
            count_mapped_symbol += 1
            for gene_id in dict_symbol_to_gene_ids[symbol]:
                tsv_writer_gene.writerow([identifier, gene_id,
                                          pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id],
                                                                                    'GO'), 'symbol'])
        elif symbol in dict_synonyms_to_gene_ids:
            count_mapped_symbol += 1
            for gene_id in dict_synonyms_to_gene_ids[symbol]:
                tsv_writer_gene.writerow(
                    [identifier, gene_id,
                     pharmebinetutils.resource_add_and_prepare(dict_gene_id_to_resource[gene_id], 'GO'),
                     'symbol_with_synonyms'])
        else:
            count_not_mapped_gene += 1
            tsv_not_mapped_gene.writerow([identifier, symbol])

    print('all:', counter)
    print('not mapped:', counter_not_mapped)
    print('mapped gene symbol', count_mapped_symbol)
    print('not mapped gene symbol', count_not_mapped_gene)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path go protein')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all protein from database')

    load_protein_and_add_to_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all gene from database')

    load_gene_and_add_to_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all protein from go and map')

    load_all_protein_form_go_and_map_and_write_to_file()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
