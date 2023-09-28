import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def load_existing_pairs(label, rela_type, dictionary, direction_left=''):
    """
    Load all pairs of a specific RNA-labe-edge type into a dictionary
    :param label:
    :param rela_type:
    :param dictionary:
    :return:
    """
    query = f'Match (m:{label}){direction_left}-[r:{rela_type}]-(n:RNA) Return m.identifier, n.identifier, r.resource'
    results = g.run(query)
    for result in results:
        [node_id, rna_id, resource] = result.values()
        dictionary[(node_id, rna_id)] = resource


def prepare_edge(label, mirbase_label, dict_pair_to_resource):
    """
    perpare rela tsv and cypher file and query
    :return:
    """
    file_name = f'output/edge_rna_{label.lower()}.tsv'
    with open(file_name, 'w', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(['identifier', 'rna_id', 'resource', 'mirbase_id','from','to'])
        query = f'''MATCH (n:{label})--(:{mirbase_label})-[rela]-(h:miRBase_pre_miRNA)--(m:RNA) RETURN  n.identifier,  m.identifier, h.accession , rela '''
        print(query)
        results = g.run(query)

        counter = 0
        for record in results:
            [identifier, rna_id, pre_id, rela] = record.values()
            if (identifier, rna_id) in dict_pair_to_resource:
                csv_writer.writerow([identifier, rna_id, pharmebinetutils.resource_add_and_prepare(
                    dict_pair_to_resource[(identifier, rna_id)], 'miRBase'), pre_id, rela['from'], rela['to']])
            else:
                csv_writer.writerow([identifier, rna_id, '', pre_id, rela['from'], rela['to']])
            counter += 1

    print('number of edges', counter)
    return file_name


def prepare_mapping_and_file(label, rela_type, mirbase_label, direction_left=''):
    # dictionary pair to resource
    dict_pair_to_resource = {}
    print('#' * 20)
    print(datetime.datetime.now())
    print('load all pairs')

    load_existing_pairs(label, rela_type, dict_pair_to_resource, direction_left=direction_left)

    print('#' * 20)
    print(datetime.datetime.now())
    print('load all pairs of mirbase, map them and write into file')
    file_name = prepare_edge(label, mirbase_label, dict_pair_to_resource)

    return file_name


def prepare_cypher_file(gene_file, rna_file):
    """
    Prepare cypher file with gene-rna and rna-rna queries.
    :param gene_file:
    :param rna_file:
    :return:
    """
    with open('output/cypher_edge.cypher', 'w', encoding='utf-8') as cypher_file_edge:
        query = 'MATCH (n:Gene{identifier:line.identifier}),(m:RNA{identifier:line.rna_id}) Merge (n)-[l:TRANSCRIBES_TO_GttR]->(m) On Create Set l.from=line.from, l.to=line.to, l.source="miRBase", l.resource=["miRBase"], l.license="CC0 with attribution", l.url="https://www.mirbase.org/hairpin/"+line.mirbase_id, l.mirbase="yes" On Match Set l.resource=split(line.resource,"|"), l.mirbase="yes" '
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/miRBase/{gene_file}',
                                                  query)
        cypher_file_edge.write(query)

        query = 'MATCH (n:RNA{identifier:line.identifier}),(m:RNA{identifier:line.rna_id}) Merge (n)<-[l:CLEAVES_TO_RctR]-(m) On Create Set l.from=line.from, l.to=line.to, l.source="miRBase", l.resource=["miRBase"], l.license="CC0 with attribution", l.url="https://www.mirbase.org/hairpin/"+line.mirbase_id, l.mirbase="yes" On Match Set l.resource=split(line.resource,"|"), l.mirbase="yes" '
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/miRBase/{rna_file}',
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
    print('Load pairs, generate tsv file and map gene-rna ')

    file_name_gene = prepare_mapping_and_file('Gene', 'TRANSCRIBES_TO_GttR', 'miRBase_Gene')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load pairs, generate tsv file and map rna-rna ')

    file_name_RNA = prepare_mapping_and_file('RNA', 'CLEAVES_TO_RctR', 'miRBase_miRNA', direction_left='<')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Generate cypher file')

    prepare_cypher_file(file_name_gene, file_name_RNA)

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
