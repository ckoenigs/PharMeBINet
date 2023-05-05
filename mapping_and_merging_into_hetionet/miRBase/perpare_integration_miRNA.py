import datetime
import csv
import sys
from collections import defaultdict

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
    g = driver.session()


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
        if property != id_property_name:
            list_of_properties.append(property + ':m.' + property)
        else:

            list_of_properties.append( 'identifier:m.'+property)

    query = f'Match (m:{label}{{id:line.id}}) Create (n:RNA :{additional_label} {{ {", ".join(list_of_properties)}, resource:["miRBase"], source:"miRBase", license:"CC0 with attribution", mirbase:"yes", url:"https://www.mirbase.org/cgi-bin/mirna_entry.pl?acc="+line.id}}) Create (n)-[:equals_rna_mirbase]->(m)'
    return query


# cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
cypher_file.write(pharmebinetutils.prepare_index_query('RNA', 'identifier', 'mirna'))


def generate_tsv_and_query(label, additional_label, id_property_name):
    """

    :param label:
    :param additional_label:
    :param id_property_name:
    :return:
    """
    file_name = f'output/{additional_label}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id'])
    query = get_node_properties_and_prepare_query(label, additional_label, id_property_name)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/miRBase/{file_name}',
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
    for record in results:
        identifier = record.data()['n.id']
        csv_writer.writerow([identifier])
        counter += 1
    file.close()

    print('number of ', additional_label, counter)


def prepare_different_nodes():
    """
    prepare the different queries and tsv files
    :return:
    """

    # pre-miRNA
    query = '''MATCH (n:miRBase_pre_miRNA) Where (n)--(:miRBase_Species{ncbi_taxid:9606}) RETURN  n.id '''
    load_in_all_pre_miRNA(query, 'miRBase_pre_miRNA', 'pre_miRNA', 'id')
    # miRNA
    query = '''MATCH (n:miRBase_miRNA) Where (n)--(:miRBase_pre_miRNA)--(:miRBase_Species{ncbi_taxid:9606}) RETURN  n.id '''
    load_in_all_pre_miRNA(query, 'miRBase_miRNA', 'miRNA', 'id')

    cypher_file.close()


def prepare_edge():
    """
    perpare rela tsv and cypher file and query
    :return:
    """
    file_name = 'output/edge_rna.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['pre_id', 'mirna_id', 'from', 'to'])
    query = '''MATCH (n:miRBase_miRNA)-[rela]-(m:miRBase_pre_miRNA) Where (m)--(:miRBase_Species{ncbi_taxid:9606}) RETURN  n.id, m.id,rela.from, rela.to  '''
    results = g.run(query)

    counter = 0
    for record in results:
        [mi_id,  pre_id, from_info, to_info] = record.values()
        csv_writer.writerow([pre_id, mi_id, from_info, to_info])
        counter += 1

    print('number of edges', counter)

    with open('output/cypher_edge.cypher', 'w', encoding='utf-8') as cypher_file_edge:
        query = 'MATCH (n:miRNA{identifier:line.mirna_id}),(m:pre_miRNA{identifier:line.pre_id}) Create (m)-[:CLEAVES_TO_RctR{from:line.from, to:line.to, source:"miRBase", resource:["miRBase"], license:"CC0 with attribution", url:"https://www.mirbase.org/cgi-bin/mirna_entry.pl?acc="+line.pre_id, mirbase:"yes"}]->(n)'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/miRBase/{file_name}',
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