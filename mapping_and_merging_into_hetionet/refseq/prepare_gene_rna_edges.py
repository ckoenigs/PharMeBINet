import datetime
import csv, sys
import general_function_refseq

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create connection to neo4j and mysql
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def prepare_edge(tuple_label_and_refseq_label):
    """
    perpare rela tsv and cypher file and query
    :return:
    """
    file_name = f'output/edge_rna_{tuple_label_and_refseq_label[0]}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier', 'pre_id', 'start', 'end', 'strand', 'source', 'url'])
    #
    query = f'''MATCH (n:{tuple_label_and_refseq_label[0]})--(:{tuple_label_and_refseq_label[1]})-[rela]-(m:refSeq_RNA) RETURN  n.identifier,  m.id , rela '''
    print(query)
    results = g.run(query)

    counter = 0
    for record in results:
        [identifier, pre_id, rela] = record.values()
        rela = dict(rela)
        csv_writer.writerow([identifier, pre_id, rela['start'], rela['end'], rela['strand'], rela['source'],
                             general_function_refseq.prepare_url_id(pre_id)])
        counter += 1

    file.close()

    print('number of edges', counter)

    with open('output/cypher_edge.cypher', 'a', encoding='utf-8') as cypher_file_edge:
        query = f'MATCH (n:{tuple_label_and_refseq_label[0]}{{identifier:line.identifier}}),(m:RNA{{identifier:line.pre_id}}) Create (n)-[:{tuple_label_and_refseq_label[2]}{{start:line.start, end:line.end, source:"RefSeq from "+line.source, strand:line.strand, resource:["RefSeq"], license:"https://www.ncbi.nlm.nih.gov/home/about/policies/", url:"https://identifiers.org/refseq:"+line.url,  refseq:"yes"}}]->(m)'

        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/refseq/{file_name}',
                                                  query)
        cypher_file_edge.write(query)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map generate tsv and cypher file ')

    for tuple_label_and_refseq_label in [("Gene", "refSeq_Gene", "TRANSCRIBES_TO_GttR")]:
        prepare_edge(tuple_label_and_refseq_label)

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
