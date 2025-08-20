import datetime
import sys, csv
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# disease ontology license
license = 'CC BY 4.0'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# cypher file
cypher_file = open('output/cypher_edge.cypher', 'w', encoding='utf-8')
# dictionary study id to pubmed id
dict_study_id_to_pmid = {}


def load_all_studies_with_pubmed_ids():
    """
    Load all studies and the additional publication infos
    :return:
    """
    query = 'Match (n:GWASCatalog_Study)--(a:GWASCatalog_Publication) Return n.id, a.pmid'
    for study_id, pmid, in g.run(query):
        dict_study_id_to_pmid[study_id] = str(pmid)


# dictionary existing disease-variant pairs with their information
dict_pair_to_resource_and_pmids = {}


def load_existing_pairs():
    """
    Load all pairs of a ND WRITE RESOURCE AND PUBMED INFORMATION INTO dictionary
    :return:
    """
    query = f'Match (m:Phenotype)-[r]-(n:Variant) Where type(r) starts with "ASSOCIATES_" Return m.identifier, n.identifier, r.resource, r.pubMed_ids'
    results = g.run(query)
    for node_id, node_id_2, resource, pubmed_ids, in results:
        dict_pair_to_resource_and_pmids[(node_id, node_id_2)] = [resource, set(pubmed_ids) if pubmed_ids else set()]


def create_file_with_header(other_label, header, addition):
    """
    prepare a tsv file with a given header
    :param other_label: string
    :param header: list of string
    :param addition: string
    :return:
    """
    file_name = 'edge/edge_to_%s_%s.tsv' % (other_label, addition)
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(header)
    return file_name, csv_writer


def create_tsv_file(other_label):
    """
    Generate tsv files for given labels. Also, the cypher query is prepared and add to the cypher file.
    :param other_label: string
    :return:
    """
    file_name, csv_writer_new = create_file_with_header(other_label,
                                                        ['variant_id', 'phenotype_id', 'pubmed_ids', 'additional_info',
                                                         'study_id'], 'new')
    file_name_merge, csv_writer_merge = create_file_with_header(other_label,
                                                                ['variant_id', 'phenotype_id', 'resource', 'pubmed_ids',
                                                                 'additional_info'], 'merge')

    query = f'Match (n:Variant{{identifier:line.variant_id}})-[r:ASSOCIATES_Va{pharmebinetutils.dictionary_label_to_abbreviation[other_label]}]->(m:{other_label} {{identifier:line.phenotype_id}}) Set r.resource=split(line.resource,"|"), r.gwas="yes", r.pubMed_ids=split(line.pubmed_ids,"|"), r.gwas_information=split(line.additional_info,"|") '
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/gwas/{file_name_merge}',
                                              query)
    cypher_file.write(query)

    query = f'Match (n:Variant{{identifier:line.variant_id}}), (m:{other_label} {{identifier:line.phenotype_id}}) Create (m)<-[:ASSOCIATES_Va{pharmebinetutils.dictionary_label_to_abbreviation[other_label]} {{source:"GWAS", resource:["GWAS"], gwas:"yes", pubMed_ids:split(line.pubmed_ids,"|"), gwas_information:split(line.additional_info,"|"), url:"https://www.ebi.ac.uk/gwas/studies/"+line.study_id, license:"https://www.ebi.ac.uk/about/terms-of-use/"}}]-(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/gwas/{file_name}',
                                              query)
    cypher_file.write(query)

    return [csv_writer_new, csv_writer_merge]


def go_through_all_gwas_pairs(label_pharmebinet):
    # dictionary pair to gwas information
    dict_pair_to_gwas_edge_information = {}

    # dictionary_label_to_tsv_files first new second merge
    dict_label_to_tsv_files = {}

    # dictionary id to label
    dict_id_to_label = {}
    query = f'Match (n:Variant)--(a:GWASCatalog_Association)--(b:GWASCatalog_Study)--(:GWASCatalog_Trait)--(m:{label_pharmebinet}) Return n.identifier, m.identifier, a.strongest_snp_risk_allele, a.p_value, a.risk_allele_frequency, b, labels(m) '
    for variant_id, phenotype_id, strongest_snp_risk_allele, p_value, risk_allele_frequency, edge_info, labels_phenotype, in g.run(
            query):
        edge_info = dict(edge_info)
        edge_info['risk_allel_info'] = [{'strongest_snp_risk_allele': strongest_snp_risk_allele, 'p-value': p_value,
                                         'risk_allele_frequency': risk_allele_frequency}]
        if label_pharmebinet=='Phenotype' and  phenotype_id not in dict_id_to_label:
            dict_id_to_label[
                phenotype_id] = 'Disease' if 'Disease' in labels_phenotype else 'Symptom' if 'Symptom' in labels_phenotype else 'SideEffect' if 'SideEffect' in labels_phenotype else 'Phenotype'
        if not (phenotype_id, variant_id) in dict_pair_to_gwas_edge_information:
            dict_pair_to_gwas_edge_information[( phenotype_id, variant_id)] = []
        dict_pair_to_gwas_edge_information[( phenotype_id,variant_id)].append(edge_info)

    for pair, list_of_edge_information in dict_pair_to_gwas_edge_information.items():
        # set of pubmed_ids
        set_pubmed_ids = set()
        # dictionary study id to study information
        dict_study_id_to_study_info = {}

        for edge_info in list_of_edge_information:
            study_id = edge_info['id']
            edge_info['pubmed_ids'] = dict_study_id_to_pmid[study_id]
            set_pubmed_ids.add(dict_study_id_to_pmid[study_id])
            if study_id not in dict_study_id_to_study_info:
                dict_study_id_to_study_info[study_id] = edge_info
            else:
                dict_study_id_to_study_info[study_id]['risk_allel_info'].append(edge_info['risk_allel_info'][0])

        label = dict_id_to_label[pair[0]] if label_pharmebinet == "Phenotype"  else label_pharmebinet
        if label not in dict_label_to_tsv_files:
            dict_label_to_tsv_files[label] = create_tsv_file(label)
        if pair in dict_pair_to_resource_and_pmids:
            dict_label_to_tsv_files[label][1].writerow(
                [pair[1], pair[0], pharmebinetutils.resource_add_and_prepare(dict_pair_to_resource_and_pmids[pair][0],'GWAS'), '|'.join(dict_pair_to_resource_and_pmids[pair][1].union(set_pubmed_ids)), '|'.join([json.dumps(x) for x in dict_study_id_to_study_info.values()]) ])
        else:
            dict_label_to_tsv_files[label][0].writerow(
                [pair[1], pair[0],
                 '|'.join(set_pubmed_ids), '|'.join([json.dumps(x) for x in dict_study_id_to_study_info.values()]), list(dict_study_id_to_study_info.keys())[0]])


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('fill dictionary study to pubmed ids')

    load_all_studies_with_pubmed_ids()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('load existing phenotype-variant edges')

    load_existing_pairs()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('go through all gwas pairs and write information into tsv files')


    go_through_all_gwas_pairs("Phenotype")
    go_through_all_gwas_pairs("BiologicalProcess")

    cypher_file.close()
    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
