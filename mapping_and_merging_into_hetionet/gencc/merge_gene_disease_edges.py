import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    # create connection with neo4j
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# ditionary gene-disease pair to rela information
dict_gene_disease_to_rela = {}


def load_existing_association_edges():
    """
    Load all gene disease pairs into a dictionary
    :return:
    """
    query = 'Match p=(n:Gene)-[r:ASSOCIATES_DaG]-(m:Disease) Return n.identifier, m.identifier, r'
    results = g.run(query)
    for result in results:
        [gene_id, disease_id, rela] = result.values()
        rela = dict(rela)
        dict_gene_disease_to_rela[(gene_id, disease_id)] = rela


def add_information_into_dictionary_and_merge(rela, dict_rela_to_info, gene_id, disease_id, hgnc_id, resource,
                                              pubMed_ids_merge=None, inheritances=None):
    """
    First get the different properties from the relationship. If the rela is not in the dicitionary generate an entry
    with ['classifications', 'inheritance', 'source','pubmed_ids', 'public_report_url', 'notes',
    'assertion_criterial_url', 'url']. If exists combine the classification ifnormation, moi title, submitter title and
    pubmed ids.
    :param rela:
    :param dict_rela_to_info:
    :param gene_id:
    :param disease_id:
    :param hgnc_id:
    :return:
    """
    public_report_url = rela['submitted_as_public_report_url'] if 'submitted_as_public_report_url' in rela else None
    notes = rela['submitted_as_notes'] if 'submitted_as_notes' in rela else None
    assertion_criterial_url = rela[
        'submitted_as_assertion_criteria_url'] if 'submitted_as_assertion_criteria_url' in rela else None
    pubmed_ids = set([str(x) for x in rela['submitted_as_pmids']]) if 'submitted_as_pmids' in rela else set()
    if (gene_id, disease_id) not in dict_rela_to_info:
        moi_titles = set([rela['moi_title']])
        if pubMed_ids_merge:
            pubmed_ids = pubmed_ids.union(pubMed_ids_merge)
        if inheritances:
            moi_titles = moi_titles.union(inheritances)
        dict_rela_to_info[(gene_id, disease_id)] = [set([rela['classification_title']]),
                                                    moi_titles, set([rela['submitter_title']]),
                                                    pubmed_ids, public_report_url, notes,
                                                    assertion_criterial_url, hgnc_id, resource]
    else:
        dict_rela_to_info[(gene_id, disease_id)][0].add(rela['classification_title'])
        dict_rela_to_info[(gene_id, disease_id)][1].add(rela['moi_title'])
        dict_rela_to_info[(gene_id, disease_id)][2].add(rela['submitter_title'])
        dict_rela_to_info[(gene_id, disease_id)][3] = dict_rela_to_info[(gene_id, disease_id)][3].union(
            pubmed_ids)


def generate_cypher_file_with_queries(properties, file_name, file_name_mapped):
    """
    Generate the fitting cypher file and add the mapping and new edge cypher queries.
    :param properties:
    :param file_name:
    :param file_name_mapped:
    :return:
    """
    with open('output/cypher_edge.cypher', 'w', encoding='utf-8') as cypher_file_edge:
        news = []
        mapped = []
        for prop in properties:
            if prop in ['public_report_url', 'notes', 'assertion_criterial_url']:
                news.append(prop + ':line.' + prop)
                mapped.append('r.' + prop + '=line.' + prop)
            elif prop == 'url':
                news.append(prop + ':"https://search.thegencc.org/genes/"+line.' + prop)
            elif prop == 'source':
                news.append(prop + ':line.' + prop + '+" via GenCC"')
            else:
                news.append(prop + ':split(line.' + prop + ',"|")')
                mapped.append('r.' + prop + '=split(line.' + prop + ',"|")')

        query_new = 'MATCH (n:Gene{identifier:line.gene_id}),(m:Disease{identifier:line.disease_id}) Create (m)-[:ASSOCIATES_DaG{'
        query_new += ', '.join(
            news) + ', license:"CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",  gencc:"yes" }]->(n)'
        query_new = pharmebinetutils.get_query_import(path_of_directory,
                                                      f'mapping_and_merging_into_hetionet/gencc/{file_name}',
                                                      query_new)
        cypher_file_edge.write(query_new)
        query_mapped = 'MATCH (n:Gene{identifier:line.gene_id})<-[r:ASSOCIATES_DaG]-(m:Disease{identifier:line.disease_id}) Set '
        query_mapped += ', '.join(mapped) + ', r.gencc="yes"'
        query_mapped = pharmebinetutils.get_query_import(path_of_directory,
                                                         f'mapping_and_merging_into_hetionet/gencc/{file_name_mapped}',
                                                         query_mapped)
        cypher_file_edge.write(query_mapped)


def prepare_and_write_information_into_tsv(dictionary_pair_to_infos, csv_writer):
    """
    go through dictionary and prepare for each entry the properties and write information into TSV file
    :param dictionary_pair_to_infos:
    :param csv_writer:
    :return:
    """
    for (gene_id, disease_id), list_of_prop in dictionary_pair_to_infos.items():
        new_prop_list = []
        counter = 0
        for prop in list_of_prop:
            if counter == 2:
                new_prop_list.append(','.join(prop))
            elif type(prop) != str and prop is not None:
                new_prop_list.append('|'.join(prop))
            else:
                new_prop_list.append(prop)
            counter += 1
        csv_writer.writerow([gene_id, disease_id] + new_prop_list)


def prepare_tsv_file_and_cypher_file(dict_mapping_pairs_infos, dict_new_pairs_infos):
    """
    Prepare the 2 tsv file for mapping and new edges and the fitting queries.
    :param dict_mapping_pairs_infos:
    :param dict_new_pairs_infos:
    :return:
    """
    file_name = 'output/edge_disease_gene_new.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    properties = ['classifications', 'inheritance', 'source', 'pubMed_ids', 'public_report_url', 'notes',
                  'assertion_criterial_url', 'url', 'resource']
    csv_writer.writerow(['gene_id', 'disease_id'] + properties)
    file_name_mapped = 'output/edge_disease_gene_mapped.tsv'
    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_writer_mapped = csv.writer(file_mapped, delimiter='\t')
    properties = ['classifications', 'inheritance', 'source', 'pubMed_ids', 'public_report_url', 'notes',
                  'assertion_criterial_url', 'url', 'resource']
    csv_writer_mapped.writerow(['gene_id', 'disease_id'] + properties)

    generate_cypher_file_with_queries(properties, file_name, file_name_mapped)

    prepare_and_write_information_into_tsv(dict_mapping_pairs_infos, csv_writer_mapped)
    prepare_and_write_information_into_tsv(dict_new_pairs_infos, csv_writer)


def prepare_edge():
    """
    perpare rela tsv and cypher file and query
    :return:
    """
    # take only edges with good evidences
    query = '''MATCH (n:Gene)--(l:GenCC_Gene)-[rela]-(:GenCC_Disease)--(m:Disease) Where rela.classification_title in ["Supportive","Strong","Definitive","Moderate"] and not rela.submitted_as_pmids is NULL RETURN  n.identifier,  m.identifier , rela, l.id '''
    results = g.run(query)

    dict_mapping_pairs_infos = {}
    dict_new_pairs_infos = {}

    counter = 0
    for record in results:
        [gene_id, disease_id, rela, hgnc_id] = record.values()
        rela = dict(rela)
        if (gene_id, disease_id) in dict_gene_disease_to_rela:
            rela_mapped = dict_gene_disease_to_rela[(gene_id, disease_id)]
            inheritances = set(rela_mapped['inheritance']) if 'inheritance' in rela_mapped else None
            pubMed_ids = set(rela_mapped['pubMed_ids']) if 'pubMed_ids' in rela_mapped else None
            resource = set(rela_mapped['resource'])
            resource.add('GenCC')
            add_information_into_dictionary_and_merge(rela, dict_mapping_pairs_infos, gene_id, disease_id, hgnc_id,
                                                      resource, pubMed_ids, inheritances)
        else:
            add_information_into_dictionary_and_merge(rela, dict_new_pairs_infos, gene_id, disease_id, hgnc_id,
                                                      set(['GenCC']))
        counter += 1

    prepare_tsv_file_and_cypher_file(dict_mapping_pairs_infos, dict_new_pairs_infos)

    print('number of edges', counter)


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

    print(datetime.datetime.now())
    print('Load existing gene-disease')

    load_existing_association_edges()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map generate tsv and cypher file ')

    prepare_edge()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
