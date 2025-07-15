import datetime
import sys, csv
import json

sys.path.append("../..")
import pharmebinetutils
import create_connection_to_databases


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary rela partner to tsv file
dict_rela_partner_to_tsv_file = {}

# directory of save the data
directory = 'annotation_variant_edge'

# open rela cypher file
cypher_file = open('output/cypher_edge.cypher', 'a')


def generate_rela_files(label, rela_name):
    """
    Generate cyper query and file for rela
    :param directory: string
    :param rela: string
    :param rela_name: string
    :return:
    """
    file_name = directory + '/rela_' + label + '.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['anno_id', 'other_id'])
    dict_rela_partner_to_tsv_file[label] = csv_file

    query_rela = 'Match (b:VariantAnnotation{identifier:line.anno_id}), (c:%s{identifier:line.other_id}) Create (b)-[:%s{pharmgkb:"yes", url:"https://www.pharmgkb.org/variantAnnotation/"+line.anno_id, source:"PharmGKB", resource:["PharmGKB"], license:"%s" }]->(c)'
    rela_name = rela_name % ('VA')
    query_rela = query_rela % (label, rela_name, license)

    query_rela = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                                   query_rela)
    cypher_file.write(query_rela)


# dictionary pGKB label to normal Label
dict_pGKB_label_to_label = {
    'PharmGKB_Gene': 'Gene',
    'PharmGKB_Variant': 'Variant',
    'PharmGKB_Chemical': ['Chemical', 'PharmacologicClass'],
    'PharmGKB_Haplotype': 'Variant'
}

# dictionary label to rela_name
dict_label_to_rela_name = {
    'Gene': 'ASSOCIATES_%saG',
    'Variant': 'ASSOCIATES_%saV',
    'Chemical': 'ASSOCIATES_%saCH',
    'Haplotype': 'ASSOCIATES_%saH',
    'PharmacologicClass': 'ASSOCIATES_%saPC'
}

# add constraint
add_constraint = False

# set of all VA ids where not all connections exists
set_of_all_VA_ids_without_all_connections = set()


def check_for_connection(label, label_to):
    """
    get all VA ids where a connection is not there
    :param label: string
    :param label_to: string
    :return:
    """
    query = '''Match (d:PharmGKB_VariantAnnotation)--(a:%s) Where not (a)--(:%s) Return d.id; '''
    query = query % (label, label_to)
    results = g.run(query)
    for record in results:
        [identifier] = record.values()
        set_of_all_VA_ids_without_all_connections.add(identifier)


def check_for_connection_chemical():
    """
    get all VA ids where a connection is not there to chemical or PC
    :return:
    """
    query = '''Match (d:PharmGKB_VariantAnnotation)--(a:PharmGKB_Chemical) Where not ((a)--(:Chemical) or (a)--(:PharmacologicClass)) Return d.id; '''
    results = g.run(query)
    for record in results:
        [identifier] = record.values()
        set_of_all_VA_ids_without_all_connections.add(identifier)


def prepare_files(label):
    """
    generate tsv file for nodes. Prepare cypher query and add to cypher file. Constraint is only one time added.
    :param label: string
    :return:
    """
    global add_constraint
    file_name = directory + '/' + label + '_node.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['identifier', 'study_parameters', 'guideline_urls', 'PubMed_ids', 'PubMed_Central_ids'])

    query_meta_node = 'Match (n:%s{id:toInteger(line.identifier)}) Create (b:VariantAnnotation :%s {'
    query = 'MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'
    query = query % (label)
    results = g.run(query)
    for property in results:
        property = property.data()['l']
        if property != 'id':
            query_meta_node += property + ':n.' + property + ', '
        else:
            query_meta_node += 'identifier:toString(n.' + property + '), '

    query_meta_node += ' study_parameters:split(line.study_parameters,"|"), guideline_urls:split(line.guideline_urls,"|"), pubMed_ids:split(line.PubMed_ids,"|"),pubMed_Central_ids:split(line.PubMed_Central_ids,"|") , source:"PharmGKB", resource:["PharmGKB"], node_edge:true, url:"https://www.pharmgkb.org/variantAnnotation/"+line.identifier, license:"%s", pharmgkb:"yes"}) Create (n)<-[:equal_metadata]-(b)'
    query_meta_node = query_meta_node % (label, label.split('_')[1], license)
    query_meta_node = pharmebinetutils.get_query_import(path_of_directory,
                                                        f'mapping_and_merging_into_hetionet/pharmGKB/{file_name}',
                                                        query_meta_node)
    if not add_constraint:
        cypher_file.write(pharmebinetutils.prepare_index_query('VariantAnnotation', 'identifier'))
        add_constraint = True
    cypher_file.write(query_meta_node)

    return csv_file


def add_value_to_dictionary(dictionary, key, value):
    """
    add key to dictionary if not existing and add value to set
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if value not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def add_check_and_add_info(property_in_pGKB, literature, property_name, dictionary):
    """
    First, check if the property id in the node. The get the value of this property. If the new_property name is not in
    the dictionary generate a set. Add the value to the dictionary.
    :param property_in_pGKB: string
    :param literature: node
    :param property_name: string
    :param dictionary: dictionary
    :return:
    """
    if property_in_pGKB in literature:
        value = str(literature[property_in_pGKB])
        if property_name not in dictionary:
            dictionary[property_name] = set()
        if property_name == 'guideline_urls':
            value = 'https://www.pharmgkb.org/literature/' + value
        dictionary[property_name].add(value)


# dictionary annotation id id to list of studies parameter
dict_annotation_to_study_parameters = {}

# dictionary annotation id id to list of pubmed ids
dict_annotation_to_literatur = {}


def load_additional_information_into_dictionary():
    """
    Prepare the StudyParameters and Literatures information.
    :return:
    """
    query = '''Match (d:PharmGKB_VariantAnnotation)--(e:PharmGKB_StudyParameters) Return d.id, e'''
    results = g.run(query)
    for record in results:
        [identifier, study_parameter] = record.values()
        if identifier not in dict_annotation_to_study_parameters:
            dict_annotation_to_study_parameters[identifier] = []
        dict_annotation_to_study_parameters[identifier].append(dict(study_parameter))

    query = '''Match (d:PharmGKB_VariantAnnotation)--(e:PharmGKB_Literature) Return d.id, e'''
    results = g.run(query)
    for record in results:
        [identifier, literatur] = record.values()
        if identifier not in dict_annotation_to_literatur:
            dict_annotation_to_literatur[identifier] = {}

        add_check_and_add_info('id', literatur, 'guideline_urls', dict_annotation_to_literatur[identifier])
        add_check_and_add_info('pmid', literatur, 'PubMed_ids', dict_annotation_to_literatur[identifier])
        add_check_and_add_info('pmcid', literatur, 'PubMed_Central_ids', dict_annotation_to_literatur[identifier])


def add_infos_into_list(identifier, property_name, infos):
    """
    Depending of information exists they are add to the list or an empty value.
    :param identifier: string
    :param property_name: string
    :param infos: list
    :return:
    """
    if property_name in dict_annotation_to_literatur[identifier]:
        infos.append('|'.join(dict_annotation_to_literatur[identifier][property_name]))
    else:
        infos.append('')


def load_db_info_in(label, csv_writer):
    """
    First generate the files and the queries. Then prepare clinical annotation meta data. Therefor take only where the
    chemical and variants are mapped. Also fusion the clinical_annotation into the node and write the information in a
    tsv file.
    :param label: string
    :param csv_writer: csv writer
    :return:
    """

    query = '''MATCH (d:%s) Where d.significance='yes'  Return Distinct d.id '''
    query = query % (label)
    results = g.run(query)

    counter_meta_edges = 0
    counter_of_integrated_edges = 0
    for record in results:
        [identifier] = record.values()
        counter_meta_edges += 1
        if identifier not in set_of_all_VA_ids_without_all_connections:
            counter_of_integrated_edges += 1
            if identifier in dict_annotation_to_study_parameters:
                list_of_study_parameters_as_json = [json.dumps(x).replace('"', '\'') for x in
                                                    dict_annotation_to_study_parameters[identifier]]
            else:
                list_of_study_parameters_as_json = []
            infos = [identifier, '|'.join(list_of_study_parameters_as_json)]
            if identifier in dict_annotation_to_literatur:
                add_infos_into_list(identifier, 'guideline_urls', infos)
                add_infos_into_list(identifier, 'PubMed_ids', infos)
                add_infos_into_list(identifier, 'PubMed_Central_ids', infos)

            csv_writer.writerow(infos)

    print('length of ' + label + ' in db:' + str(counter_meta_edges))
    print('length of ' + label + ' in db with all connections:' + str(counter_of_integrated_edges))


def fill_the_rela_files(label_node):
    """
    check for relationship form the new nodes to chemical, variant and gene. Add cypher query to metaData annotation.
    :param label_node: string
    :return:
    """
    query = 'Match (n:VariantAnnotation)--(:%s)-[r]-(:PharmGKB_ClinicalAnnotation)--(b:ClinicalAnnotation) Create (n)<-[h:HAS_EVIDENCE_CAheVA]-(b) Set h=r, h.pubMed_ids=[r.pmid],  h.pharmgkb="yes", h.source="PharmGKB", h.resource=["PharmGKB"], h.license="%s", h.url="https://www.pharmgkb.org/variantAnnotation/"+n.identifier Remove h.pmid;\n'
    query = query % (label_node, license)
    cypher_file.write(query)
    query_general = 'Match (n:%s)--(:%s)--(m:%s) Return Distinct n.id, m.identifier'
    for pharmGKB_label, label in dict_pGKB_label_to_label.items():
        if type(label) == str:
            query = query_general % (label_node, pharmGKB_label, label)
            results = g.run(query)
            counter = 0
            # counter_specific = 0
            for record in results:
                [meta_id, other_id] = record.values()
                counter += 1
                dict_rela_partner_to_tsv_file[label].writerow([meta_id, other_id])
                # if meta_id in dict_annotation_to_study_parameters:
                #     counter_specific += 1
        else:
            for single_label in label:
                query = query_general % (label_node, pharmGKB_label, single_label)
                results = g.run(query)
                counter = 0
                counter_specific = 0
                for record in results:
                    [meta_id, other_id] = record.values()
                    counter += 1
                    dict_rela_partner_to_tsv_file[single_label].writerow([meta_id, other_id])
                    # if meta_id in dict_annotation_to_study_parameters:
                    #     counter_specific += 1
        print('count rela with ' + pharmGKB_label + ':', counter)
        # print('count rela with ' + pharmGKB_label + ' and other condition are working:', counter_specific)


def prepare_delete_variant_annotation():
    """
    All variant annotation are delete where the pGKB chemical/gene/ClinivalAnnotation are not mapped to my
    database. So add the query to check and delete to cypher file.
    :return:
    """
    # list_of_delete_label_if_not_mapped = ['ClinicalAnnotationMetadata', 'Gene']
    # query = 'MATCH p=(a:VariantAnnotation)--(n:PharmGKB_VariantAnnotation)--(b:PharmGKB_%s) Where not (b)--(:%s) Detach Delete a;\n'
    # for label in list_of_delete_label_if_not_mapped:
    #     new_query = query % (label, label)
    #     cypher_file.write(new_query)
    query = 'MATCH p=(a:VariantAnnotation)--(n:PharmGKB_VariantAnnotation)--(b:PharmGKB_Chemical) Where not( (b)--(:Chemical) or (b)--(:PharmacologicClass)) Detach Delete a;\n'
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

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('get all VA ids wher not all connections exists')

    list_of_labels = [
        ['PharmGKB_Variant', 'Variant'],
        ['PharmGKB_Haplotype', 'Variant'],
        ['PharmGKB_Gene', 'Gene'],
        ['PharmGKB_Phenotype', 'Phenotype'],
    ]

    for pair in list_of_labels:
        check_for_connection(pair[0], pair[1])
    check_for_connection_chemical()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load additional information of literature and study parameters into dictionaries')

    load_additional_information_into_dictionary()
    # prepare the meta_nodes
    for label in ['PharmGKB_VariantDrugAnnotation', 'PharmGKB_VariantFunctionalAnalysisAnnotation',
                  'PharmGKB_VariantPhenotypeAnnotation']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Generate genration file for node')

        csv_writer = prepare_files(label)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Load in ' + label + ' from neo4j')

        load_db_info_in(label, csv_writer)

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print('Prepare relationship files')

    for label, rela_name in dict_label_to_rela_name.items():
        generate_rela_files(label, rela_name)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Fill rela files')

    fill_the_rela_files('PharmGKB_VariantAnnotation')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('prepare delete queries')

    prepare_delete_variant_annotation()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
