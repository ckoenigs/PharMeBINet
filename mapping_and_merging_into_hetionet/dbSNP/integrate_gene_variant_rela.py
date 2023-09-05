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
    g = driver.session()


# set of rela pairs
set_of_rela_pairs = set()


def load_rela_from_database_and_add_to_dict(csv_writter):
    """
    Get all gene-varinat pairs and write into file
    :param csv_writter:
    :return:
    """
    query = "MATCH (n:Gene)--(:gene_dbSNP)--(:snp_dbSNP)--(b:Variant) RETURN n.identifier, b.identifier"
    results = g.run(query)
    for record in results:
        [identifier, variant_id] = record.values()
        if not (identifier, variant_id) in set_of_rela_pairs:
            csv_writter.writerow([identifier, variant_id])
            set_of_rela_pairs.add((identifier, variant_id))


# cypher file
cypher_file = open('output_mapping/cypher_edge.cypher', 'w', encoding='utf-8')


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # file from relationship between gene and variant
    file_name = 'output_mapping/gene_variant'
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['gene_id', 'variant_id']
    csv_mapping.writerow(header)

    query = '''Match (n:Gene{identifier:line.gene_id}), (v:Variant{identifier:line.variant_id}) Merge (n)-[r:HAS_GhGV]->(v)  On Match Set  r.dbsnp="yes", r.resource=r.resource+"dbSNP"  On Create Set r.dbsnp="yes", r.resource=["dbSNP"], r.url="https://www.ncbi.nlm.nih.gov/snp/"+line.variant_id , r.source="dbSNP", r.license="https://www.ncbi.nlm.nih.gov/home/about/policies/"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/dbSNP/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


def main():
    print(datetime.datetime.now())
    global path_of_directory, license
    if len(sys.argv) < 2:
        sys.exit('need  path to directory gene variant and license')
    path_of_directory = sys.argv[1]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Gene-variant pairs into a tsv file from database')

    load_rela_from_database_and_add_to_dict(csv_mapping)

    driver.close()
    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
