import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def load_pharmgkb_in(label, directory):
    """
    generate mapping file and cypher file for a given label
    map nodes to chemical
    :param label: string
    :param directory: distionary
    :param mapped_label
    :return:
    """

    # csv_file
    file_name = directory + '/integrate_' + label.split('_')[1] + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['variant_id', 'gene_id'])

    generate_cypher_file(file_name)

    query = '''MATCH (a:Variant)--(:%s)-[:PharmGKB_HAS_VARIANT]-(:PharmGKB_Gene)--(b:Gene) RETURN a.identifier, b.identifier'''
    query = query % (label)
    results = g.run(query)

    # set of all tuples
    set_of_all_tuples = set()

    # set of variant gene pairs
    set_of_variant_gene_pair = set()

    for variant_id, gene_id, in results:
        if (variant_id,gene_id) in set_of_variant_gene_pair:
            continue
        set_of_variant_gene_pair.add((variant_id,gene_id))
        csv_writer.writerow([variant_id, gene_id])


# cypher file generation
cypher_file = open('output/cypher_edge.cypher', 'w')


def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:Variant{identifier:line.variant_id}), (c:Gene{identifier:line.gene_id}) Merge (c)-[r:HAS_GhV]->(n) On Create Set r.source="PharmGKB", r.resource=["PharmGKB"], r.pharmgkb
    ="yes" , r.license="%s" On Match Set r.resource=r.resource + "PharmGKB", r.pharmgkb="yes"; \n'''
    query = query % (file_name, license)
    cypher_file.write(query)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    for label in ['PharmGKB_Variant', 'PharmGKB_Haplotype']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Load in %s from pharmgb in' % (label))

        load_pharmgkb_in(label, 'variant_gene')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
