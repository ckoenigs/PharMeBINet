import datetime
import sys, csv
import json

'''
for the clinical annotation levels of evidence https://www.pharmgkb.org/page/clinAnnLevels

'''

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary rela partner to csv file
dict_rela_partner_to_csv_file = {}

# directory of save the data
directory = 'annotation_variant_edge'

# open rela cypher file
cypher_file = open('output/cypher_edge.cypher', 'a')


def generate_rela_files(label, rela_name, query_start):
    """
    Generate cyper query and file for rela
    :param directory: string
    :param rela: string
    :param rela_name: string
    :param query_start: string
    :return:
    """
    file_name = directory + '/rela_' + label + '.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['anno_id', 'other_id'])
    dict_rela_partner_to_csv_file[label] = csv_file

    query_rela = query_start + ' (b:VariantAnnotation{identifier:line.anno_id}), (c:%s{identifier:line.other_id}) Create (b)-[:%s]->(c);\n'
    rela_name = rela_name % ('VA')
    query_rela = query_rela % (file_name, label, rela_name)
    cypher_file.write(query_rela)


# dictionary pGKB label to normal Label
dict_pGKB_label_to_label = {
    'PharmGKB_Gene': 'Gene',
    'PharmGKB_Variant': 'Variant',
    'PharmGKB_Chemical': 'Chemical',
    'PharmGKB_Haplotype': 'Variant'
}

# dictionary label to rela_name
dict_label_to_rela_name = {
    'Gene': 'ASSOCIATES_%saG',
    'Variant': 'ASSOCIATES_%saV',
    'Chemical': 'ASSOCIATES_%saC',
    'Haplotype': 'ASSOCIATES_%saH'
}

# add constraint
add_constraint = False


def prepare_files(label, query_start):
    """
    generate tsv file for nodes. Prepare cypher query and add to cypher file. Constraint is only one time added.
    :param label: string
    :param query_start: string
    :return:
    """
    global add_constraint
    file_name = directory + '/' + label + '_node.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['identifier', 'study_parameters'])

    query_meta_node = query_start + '(n:%s{id:toInteger(line.identifier)}) Create (b:VariantAnnotation :%s {'
    query = 'MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
    query = query % (label)
    results = g.run(query)
    for property, in results:
        if property != 'id':
            query_meta_node += property + ':n.' + property + ', '
        else:
            query_meta_node += 'identifier:toString(n.' + property + '), '

    query_meta_node += ' study_parameters:split(line.study_parameters,"|") , source:"PharmGKB", resource:["PharmGKB"], meta_edge:true, license:"%s"}) Create (n)<-[:equal_metadata]-(b);\n'
    query_meta_node = query_meta_node % (file_name, label, label.split('_')[1], license)
    cypher_file.write(query_meta_node)
    if not add_constraint:
        cypher_file.write('Create Constraint On (node:VariantAnnotation) Assert node.identifier Is Unique;\n')
        add_constraint = True

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


# dictionary annotation id id to list of studies parameter
dict_annotation_to_study_parameters = {}


def load_db_info_in(label, csv_writer):
    """
    First generate the files and the queries. Then prepare clinical annotation meta data. Therefor take only where the
    chemical and variants are mapped. Also fusion the clinical_annotation into the node and write the information in a
    csv file.
    :param label: string
    :param csv_writer: csv writer
    :return:
    """
    dict_va_id_to_study_parametwers = {}
    query = '''Match (d)--(e:PharmGKB_StudyParameters) Return d.id, e'''
    results = g.run(query)
    for identifier, study_parameter, in results:
        if identifier not in dict_annotation_to_study_parameters:
            dict_annotation_to_study_parameters[identifier] = []
        dict_annotation_to_study_parameters[identifier].append(dict(study_parameter))

    query = '''MATCH (d:%s) 
    Match (d)--(g)--(:Variant) Where  'PharmGKB_Variant' in labels(g) or "PharmGKB_Haplotype" in labels(g) 
    Return Distinct d.id '''
    query = query % (label)
    results = g.run(query)

    counter_meta_edges = 0
    for identifier, in results:
        counter_meta_edges += 1
        if identifier in dict_annotation_to_study_parameters:
            list_of_study_parameters_as_json = [json.dumps(x).replace('"', '\'') for x in
                                                dict_annotation_to_study_parameters[identifier]]
        else:
            list_of_study_parameters_as_json = []
        csv_writer.writerow([identifier, '|'.join(list_of_study_parameters_as_json)])

    print('length of ' + label + ' in db:' + str(counter_meta_edges))


def fill_the_rela_files(label_node):
    """
    check for relationship form the new nodes to chemical, variant and gene. Add cypher query to metaData annotation.
    :param label_node: string
    :return:
    """
    query = 'Match (n:VariantAnnotation)--(:%s)--(:PharmGKB_ClinicalAnnotationMetadata)--(b:ClinicalAnnotationMetadata) Create (n)<-[:ASSOICATES_CAMaVA]-(b);\n'
    query = query % (label_node)
    cypher_file.write(query)
    query_general = 'Match (n:%s)--(:%s)--(m:%s) Return Distinct n.id, m.identifier'
    for pharmGKB_label, label in dict_pGKB_label_to_label.items():
        query = query_general % (label_node, pharmGKB_label, label)
        results = g.run(query)
        counter = 0
        counter_specific = 0
        for meta_id, other_id, in results:
            counter += 1
            if meta_id in dict_annotation_to_study_parameters:
                counter_specific += 1
                dict_rela_partner_to_csv_file[label].writerow([meta_id, other_id])
        print('count rela with ' + pharmGKB_label + ':', counter)
        print('count rela with ' + pharmGKB_label + ' and other condition are working:', counter_specific)

def prepare_delete_variant_annotation():
    """
    All variant annotation are delete where the pGKB chemical/gene/ClinivalAnnotationMetadata are not mapped to my
    database. So add the query to check and delete to cypher file.
    :return:
    """
    list_of_delete_label_if_not_mapped=['ClinicalAnnotationMetadata','Gene','Chemical']
    query='MATCH p=(a:VariantAnnotation)--(n:PharmGKB_VariantAnnotation)--(b:PharmGKB_%s) Where not (b)--(:%s) Detach Delete a;\n'
    for label in list_of_delete_label_if_not_mapped:
        new_query=query %(label,label)
        cypher_file.write(new_query)


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

    # query start
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH '''

    # prepare the meta_nodes
    for label in ['PharmGKB_VariantDrugAnnotation', 'PharmGKB_VariantFunctionalAnalysisAnnotation',
                  'PharmGKB_VariantPhenotypeAnnotation']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Generate genration file for node')

        csv_writer = prepare_files(label, query_start)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Load in ' + label + ' from hetionet')

        load_db_info_in(label, csv_writer)

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())
    print('Prepare relationship files')

    for label, rela_name in dict_label_to_rela_name.items():
        generate_rela_files(label, rela_name, query_start)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Fill rela files')

    fill_the_rela_files('PharmGKB_VariantAnnotation')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('prepare delete queries')

    prepare_delete_variant_annotation()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
