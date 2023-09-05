import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def load_pharmgkb_in(label, directory):
    """
    generate mapping file and cypher file for a given label
    map nodes to chemical
    :param label: string
    :param directory: distionary
    :param mapped_label
    :return:
    """

    # tsv_file
    file_name = directory + '/integrate_' + label.split('_')[1] + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['variant_id', 'gene_id', 'pGKB_id'])

    generate_cypher_file(file_name)

    query = '''MATCH (a:Variant)--(z:%s)-[:PharmGKB_HAS_VARIANT]-(:PharmGKB_Gene)--(b:Gene) RETURN a.identifier, z.id,  b.identifier'''
    query = query % (label)
    results = g.run(query)

    # set of all tuples
    set_of_all_tuples = set()

    # set of variant gene pairs
    set_of_variant_gene_pair = set()

    for record in results:
        [variant_id, pGKB_id, gene_id] = record.values()
        if (variant_id, gene_id) in set_of_variant_gene_pair:
            continue
        set_of_variant_gene_pair.add((variant_id, gene_id))
        csv_writer.writerow([variant_id, gene_id, pGKB_id])


# cypher file generation
cypher_file = open('output/cypher_edge.cypher', 'w')


def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    query = '''  MATCH (n:Variant{identifier:line.variant_id}), (c:Gene{identifier:line.gene_id}) Merge (c)-[r:HAS_GhGV]->(n) On Create Set r.source="PharmGKB", r.resource=["PharmGKB"], r.pharmgkb="yes" , r.license="%s", r.url="https://www.pharmgkb.org/variant/"+line.pGKB_id On Match Set r.resource=r.resource + "PharmGKB", r.pharmgkb="yes"'''
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    for label in ['PharmGKB_Variant', 'PharmGKB_Haplotype']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Load in %s from pharmgb in' % (label))

        load_pharmgkb_in(label, 'variant_gene')

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
