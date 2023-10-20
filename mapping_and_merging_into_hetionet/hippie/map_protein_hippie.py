import datetime
import csv
import sys

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


def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w')

    query = "MATCH (n:Protein_Hippie{identifier:line.id1}), (c:Protein{identifier:line.id2})  Set c.hippie='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_protein_hippie{how_mapped:line.how_mapped}]->(n)"

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hippie/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def generate_files():
    """
    Generate tsv file and cypher file with query
    :return:
    """
    global csv_writer, file
    file_name = 'output/mapped_proteins.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id1', 'id2', 'resource', 'how_mapped'])

    generate_cypher_file(file_name)


# dictionary protein entry to protein id
dict_protein_entry_to_protein_ids = {}
# protein id to resource
dict_protein_id_to_resource = {}
# dictionary gene id to protein id
dict_gene_id_to_protein_id = {}


def load_protein_in():
    '''
    Load Protein information and write into the different dictionaries
    :return:
    '''
    query = '''MATCH (n:Protein) RETURN n.identifier, n.resource, n.entry_name'''
    results = g.run(query)

    for record in results:
        [identifier, resource, entry_name] = record.values()
        dict_protein_id_to_resource[identifier] = set(resource)
        if entry_name in dict_protein_entry_to_protein_ids:
            print('ohje double entry')
        dict_protein_entry_to_protein_ids[entry_name] = identifier

    query = '''MATCH (g:Gene)--(n:Protein) RETURN n.identifier, g.identifier'''
    results = g.run(query)

    for record in results:
        [protein_id, gene_id] = record.values()
        if gene_id not in dict_gene_id_to_protein_id:
            dict_gene_id_to_protein_id[gene_id] = set()
        dict_gene_id_to_protein_id[gene_id].add(protein_id)


def load_and_map_hippie_protein():
    '''

    :return:
    '''
    query = '''MATCH (n:Protein_Hippie) RETURN n'''
    results = g.run(query)
    counter = 0
    counter_mapped = 0
    for record in results:
        node = record.data()['n']
        counter += 1
        identifier = node['identifier']
        found_mapping = False

        if identifier.startswith('entrez gene:'):
            entrez_id = identifier.split(':')[1]
            if entrez_id in dict_gene_id_to_protein_id:
                found_mapping = True
                for protein_id in dict_gene_id_to_protein_id[entrez_id]:
                    csv_writer.writerow([identifier, protein_id,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_protein_id_to_resource[protein_id], 'HIPPIE'),
                                         'gene_to_protein'])

        if found_mapping:
            continue

        if 'alternative_id' in node:
            alternative_ids = node['alternative_id']
            if alternative_ids.startswith('uniprotkb:'):

                uniprot_entry = alternative_ids.split(':')[1]
                if uniprot_entry in dict_protein_entry_to_protein_ids:
                    protein_id = dict_protein_entry_to_protein_ids[uniprot_entry]
                    csv_writer.writerow([identifier, protein_id, pharmebinetutils.resource_add_and_prepare(
                        dict_protein_id_to_resource[protein_id], 'HIPPIE'), 'uniprot_entry'])
                    counter_mapped += 1
                    found_mapping = True

        if found_mapping:
            continue
        # else:
        #     print('no alternative ids')
        #     print(node)
    print('counter:', counter)
    print('counter for mapping:', counter_mapped)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hippie protein')

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')
    print("generate files")
    print(datetime.datetime.utcnow())

    generate_files()

    print(
        '###########################################################################################################################')
    print("load protein in")
    print(datetime.datetime.utcnow())

    load_protein_in()

    driver.close()

    print(
        '###########################################################################################################################')
    print("load and mapp hippie protein ")
    print(datetime.datetime.utcnow())

    load_and_map_hippie_protein()

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
