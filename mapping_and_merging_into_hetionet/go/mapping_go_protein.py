from py2neo import Graph  # , authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# dictionary uniprot_id to resource
dict_uniprot_id_to_resource = {}

# dictionary alternative uniprot id to uniprot ids
dict_alternativ_uniprot_id_to_identifiers = {}


def add_entry_to_dictionary(dictionary, key, value):
    """
    prepare entry in dictionary if not exists. Then add new value.
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)

def generate_files(label, cypher_file):
    """
    generate cypher file and csv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'protein/go_protein_to_%s' % label
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['identifier', 'other_id', 'resource', 'mapped_with']
    csv_mapping.writerow(header)

    file_name_not = 'protein/not_go_protein_to_%s' % label
    file_not = open(file_name_not + '.tsv', 'w', encoding='utf-8')
    csv_not_mapping = csv.writer(file_not, delimiter='\t')
    header = ['identifier', 'name']
    csv_not_mapping.writerow(header)


    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/go/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:protein_go{identifier:line.identifier}), (v:%s{identifier:line.other_id}) Set v.go='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_go_%s{how_mapped:line.mapped_with}]->(n);\n'''
    query = query % (path_of_directory, file_name, label, label.lower())
    cypher_file.write(query)


    return csv_mapping, csv_not_mapping
'''
Load all Genes from my database  and add them into a dictionary
'''


def load_protein_and_add_to_dictionary():
    query = "MATCH (n:Protein) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']

        dict_uniprot_id_to_resource[identifier] = node['resource']
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for alternative_id in alternative_ids:
            add_entry_to_dictionary(dict_alternativ_uniprot_id_to_identifiers, alternative_id, identifier)
        gene_symbols = node['gene_name'] if 'gene_name' in node else []


    print('number of proteins:', len(dict_uniprot_id_to_resource))

# dictionary gene id to resource
dict_gene_id_to_resource={}

# dictionary gene symbol to gene ids
dict_symbol_to_gene_ids={}

# dictionary synonym to gene ids
dict_synonyms_to_gene_ids={}

def load_gene_and_add_to_dictionary():
    """
    Load gene symbol and source information into dictionaries
    :return:
    """
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']

        dict_gene_id_to_resource[identifier] = node['resource']
        gene_symbols = node['gene_symbols'] if 'gene_symbols' in node else []
        for gene_symbol in gene_symbols:
            add_entry_to_dictionary(dict_symbol_to_gene_ids, gene_symbol.lower(), identifier)

        synonyms=node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            add_entry_to_dictionary(dict_synonyms_to_gene_ids, synonym.lower(), identifier)

    print('number of gene:', len(dict_gene_id_to_resource))



def resource(resource):
    resource = set(resource)
    resource.add('GO')
    return '|'.join(resource)

'''
Load all pharmacologic class of drugbank and map to the pc from my database and write into file
'''


def load_all_protein_form_go_and_map_and_write_to_file():
    cypher_file = open('output/cypher_protein.cypher', 'w', encoding='utf-8')
    csv_writer, csv_not_mapped=generate_files('Protein', cypher_file)
    csv_writer_gene, csv_not_mapped_gene=generate_files('Gene', cypher_file)

    query = "MATCH (n:protein_go) RETURN n"
    results = g.run(query)
    counter = 0
    counter_not_mapped= 0
    count_mapped_symbol=0
    count_not_mapped_gene=0
    for node, in results:
        counter += 1
        identifier = node['identifier']
        if identifier in dict_uniprot_id_to_resource:
            csv_writer.writerow([identifier, identifier, resource(dict_uniprot_id_to_resource[identifier]),'id_mapped'])
        elif identifier in dict_alternativ_uniprot_id_to_identifiers:
            for real_id in dict_alternativ_uniprot_id_to_identifiers[identifier]:
                csv_writer.writerow([identifier, real_id, resource(dict_uniprot_id_to_resource[real_id]),'alt_id_mapped'])
        else:
            counter_not_mapped+=1
            csv_not_mapped.writerow([identifier, node['name']])

        symbol= node['symbol'].lower() if 'symbol' in node else None
        if not symbol:
            continue
        if symbol in dict_symbol_to_gene_ids:
            count_mapped_symbol+=1
            for gene_id in dict_symbol_to_gene_ids[symbol]:
                csv_writer_gene.writerow([identifier,gene_id,  resource(dict_gene_id_to_resource[gene_id]),'symbol'])
        elif symbol in dict_synonyms_to_gene_ids:
            count_mapped_symbol += 1
            for gene_id in dict_synonyms_to_gene_ids[symbol]:
                csv_writer_gene.writerow([identifier, gene_id, resource(dict_gene_id_to_resource[gene_id]), 'symbol_with_synonyms'])
        else:
            count_not_mapped_gene+=1
            csv_not_mapped_gene.writerow([identifier, symbol])

    print('all:',counter)
    print('not mapped:',counter_not_mapped)
    print('mapped gene symbol',count_mapped_symbol)
    print('not mapped gene symbol',count_not_mapped_gene)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path go protein')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all protein from database')

    load_protein_and_add_to_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all gene from database')

    load_gene_and_add_to_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all protein from go and map')

    load_all_protein_form_go_and_map_and_write_to_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
