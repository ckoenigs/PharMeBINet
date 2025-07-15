import datetime
import csv
import sys
import general_function_refseq

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def get_node_properties_and_prepare_query(label, additional_label, id_property_name):
    """
    Prapare query for node with an additonal label.
    :param label: string
    :param additional_label: string additional label in RNA
    :param id_property_name: string
    :return:
    """
    query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    query = query % (label)
    result = g.run(query)

    list_of_properties = []
    for property in result:
        property = property.data()['l']
        if property not in [id_property_name, 'description']:
            list_of_properties.append(property + ':m.' + property)
        else:
            if property == id_property_name:
                list_of_properties.append('identifier:m.' + property)
            else:
                list_of_properties.append('name:m.' + property)

    query = f'Match (m:{label}{{id:line.id}}) Create (n:RNA :{additional_label} {{ {", ".join(list_of_properties)}, resource:["RefSeq"], source:"RefSeq", license:"CC0 with attribution", refseq:"yes", url:"https://identifiers.org/refseq:"+line.url}}) Create (n)-[:equals_rna_refseq]->(m)'
    return query


# cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
cypher_file.write(pharmebinetutils.prepare_index_query('RNA', 'identifier', 'mirna'))
cypher_file.write(pharmebinetutils.prepare_index_query_text('RNA', 'name','mirna'))


def generate_tsv_and_query(label, additional_label, id_property_name):
    """

    :param label:
    :param additional_label:
    :param id_property_name:
    :return:
    """
    file_name = f'rna/{additional_label}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id', 'url'])
    query = get_node_properties_and_prepare_query(label, additional_label, id_property_name)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/refseq/{file_name}',
                                              query)
    cypher_file.write(query)
    return csv_writer, file


def load_in_all_pre_miRNA(query, label, additional_label, property_name):
    """
    Prepare first the TSV file and the cypher query. The fill the tsv file.
    :param query:
    :param label:
    :param additional_label:
    :param property_name:
    :return:
    """
    csv_writer, file = generate_tsv_and_query(label, additional_label, property_name)

    results = g.run(query)

    counter = 0
    for identifier, in results:

        csv_writer.writerow([identifier, general_function_refseq.prepare_url_id(identifier)])
        counter += 1
    file.close()

    print('number of ', additional_label, counter)


def prepare_different_nodes():
    """
    prepare the different queries and tsv files
    :return:
    """
    list_of_labels = ["refSeq_PrimaryTranscript", "refSeq_lncRNA", "refSeq_mRNA", "refSeq_miRNA",
                      # "refSeq_Exon", it is not only RNA but also a lot of different types
                      "refSeq_Transcript", "refSeq_snoRNA", "refSeq_rRNA", "refSeq_RNasePRNA", "refSeq_RNaseMRPRNA",
                      "refSeq_scRNA", "refSeq_snRNA", "refSeq_YRNA", "refSeq_antisenseRNA", "refSeq_tRNA",
                      "refSeq_vaultRNA", "refSeq_telomeraseRNA", "refSeq_ncRNA"
                      ]
    for label in list_of_labels:
        query = f'MATCH (n:{label})  RETURN  n.id'

        load_in_all_pre_miRNA(query, label, label.split('_')[1], 'id')
    cypher_file.close()


def prepare_edge():
    """
    perpare rela tsv and cypher file and query
    :return:
    """
    file_name = 'rna/edge_rna.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['pre_id', 'mirna_id', 'start', 'end','strand', 'source' ,'url'])
    query = '''MATCH p=(n:refSeq_RNA)-[r]->(m:refSeq_RNA) RETURN  n.id, m.id,r.start, r.end, r.strand, r.source  '''
    results = g.run(query)

    counter = 0
    for record in results:
        [pre_id, mi_id, start, end, strand, source] = record.values()
        csv_writer.writerow([pre_id, mi_id, start, end, strand, source, general_function_refseq.prepare_url_id(pre_id)])
        counter += 1

    print('number of edges', counter)

    with open('output/cypher_edge.cypher', 'w', encoding='utf-8') as cypher_file_edge:
        query = 'MATCH (n:RNA{identifier:line.mirna_id}),(m:RNA{identifier:line.pre_id}) Set n.url="https://identifiers.org/refseq:"+line.url Create (m)-[:CLEAVES_TO_RctR{start:line.start, end:line.end, strand:line.strand, source:"RefSeq via "+line.source, resource:["RefSeq"], license:"https://www.ncbi.nlm.nih.gov/home/about/policies/", url:"https://identifiers.org/refseq:"+line.url, refseq:"yes"}]->(n)'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/refseq/{file_name}',
                                                  query)
        cypher_file_edge.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Prepare the different ')

    prepare_different_nodes()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('prepare edge information')

    prepare_edge()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
