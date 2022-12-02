import datetime
import sys, csv
from collections import defaultdict
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


# dictionary rela partner to tsv file
dict_rela_partner_to_tsv_file = {}

# open rela cypher file
cypher_file = open('output/cypher_edge.cypher', 'a')


def generate_rela_files(directory, rela, rela_name, query_start):
    """
    Generate cyper query and file for rela
    :param directory: string
    :param rela: string
    :param rela_name: string
    :param query_start: string
    :return:
    """
    file_name = directory + '/rela_' + rela + '.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['meta_id', 'other_id'])
    dict_rela_partner_to_tsv_file[rela] = csv_file

    query_rela = query_start + ' (b:ClinicalAnnotation{identifier:line.meta_id}), (c:%s{identifier:line.other_id}) Create (b)-[:%s{ pharmgkb:"yes", source:"PharmGKB", url:"https://www.pharmgkb.org/clinicalAnnotation/"+line.meta_id, resource:["PharmGKB"], license:"%s"}]->(c);\n'
    rela_name = rela_name % ('CA')
    query_rela = query_rela % (file_name, rela, rela_name, license)
    cypher_file.write(query_rela)


# dictionary pGKB label to normal Label
dict_pGKB_label_to_label = {
    'PharmGKB_Gene': 'Gene',
    'PharmGKB_Variant': 'Variant',
    'PharmGKB_Chemical': ['Chemical', 'PharmacologicClass'],
    'PharmGKB_Phenotype': 'Phenotype',
    'PharmGKB_Haplotype': 'Variant'
}

# dictionary label to rela_name
dict_label_to_rela_name = {
    'Gene': 'ASSOCIATES_%saG',
    'Variant': 'ASSOCIATES_%saV',
    'Chemical': 'ASSOCIATES_%saCH',
    'Phenotype': 'ASSOCIATES_%saPT',
    'PharmacologicClass': 'ASSOCIATES_%saPC'
    # 'Haplotype': 'ASSOCIATES_%saH'
}


def prepare_files(directory):
    """

    :return:
    """
    file_name = directory + '/meta_node.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['identifier', 'allele_infos'])

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH '''

    query_meta_node = query_start + '(n:PharmGKB_ClinicalAnnotation{id:toInteger(line.identifier)}) Create (b:ClinicalAnnotation{'
    query = 'MATCH (p:PharmGKB_ClinicalAnnotation) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
    results = g.run(query)
    for property, in results:
        if property != 'id':
            query_meta_node += property + ':n.' + property + ', '
        else:
            query_meta_node += 'identifier:toString(n.' + property + '), '

    query_meta_node += ' allele_infos:split(line.allele_infos,"|")  , pharmgkb:"yes", source:"PharmGKB", resource:["PharmGKB"], node_edge:true, license:"%s"}) Create (n)<-[:equal_metadata]-(b);\n'
    query_meta_node = query_meta_node % (file_name, license)
    cypher_file.write(query_meta_node)
    cypher_file.write('Create Constraint On (node:ClinicalAnnotation) Assert node.identifier Is Unique;\n')

    for rela, rela_name in dict_label_to_rela_name.items():
        generate_rela_files(directory, rela, rela_name, query_start)

    return csv_file


# set of allCA ids where not all connections exists
set_of_all_CA_ids_without_all_connections = set()


def check_for_connection(label, label_to):
    """
    get all CA ids where a connection is not there
    :param label: string
    :param label_to: string
    :return:
    """
    query = '''Match (d:PharmGKB_ClinicalAnnotation)--(a:%s) Where not (a)--(:%s) Return d.id; '''
    query = query % (label, label_to)
    results = g.run(query)
    for identifier, in results:
        set_of_all_CA_ids_without_all_connections.add(identifier)


def check_for_connection_chemical():
    """
    get all CA ids where a connection is not there
    :return:
    """
    query = '''Match (d:PharmGKB_ClinicalAnnotation)--(a:PharmGKB_Chemical) Where not ((a)--(:Chemical) or (a)--(:PharmacologicClass)) Return d.id; '''
    results = g.run(query)
    for identifier, in results:
        set_of_all_CA_ids_without_all_connections.add(identifier)


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


# dictionary meta edge id to clinical annotation infos
dict_meta_id_to_clinical_annotation_info = {}


def load_db_info_in():
    """
    First generate the files and the queries. Then prepare clinical annotation meta data. Therefor take only where the
    chemical and variants are mapped. Also fusion the clinical_annotation into the node and write the information in a
    tsv file.
    :return:
    """
    #{id:1444667346}
    query = '''Match (d:PharmGKB_ClinicalAnnotation)--(e:PharmGKB_ClinicalAnnotationAllele) Return Distinct d.id, e'''
    results = g.run(query)
    for identifier, clinical_annotation, in results:
        if identifier not in dict_meta_id_to_clinical_annotation_info:
            dict_meta_id_to_clinical_annotation_info[identifier] = []
        # blub=json.dumps(dict(clinical_annotation))
        clinical_annotation['text']=clinical_annotation['text'].replace('"','\'')
        clinical_annotation_allele_json = json.dumps(dict(clinical_annotation)).replace('\\"', '"')
        dict_meta_id_to_clinical_annotation_info[identifier].append(clinical_annotation_allele_json)

    csv_writer = prepare_files('metadata_edge')
    query = '''MATCH (d:PharmGKB_ClinicalAnnotation) Where d.level_of_evidence<>'4' Return d.id'''
    results = g.run(query)

    counter_meta_edges = 0
    counter_integrated = 0
    for identifier, in results:
        counter_meta_edges += 1
        if identifier not in set_of_all_CA_ids_without_all_connections:
            counter_integrated += 1
            if identifier in dict_meta_id_to_clinical_annotation_info:
                allels = '|'.join(dict_meta_id_to_clinical_annotation_info[identifier])
            else:
                allels = ''
            csv_writer.writerow([identifier, allels])

    print('length of CA in db:' + str(counter_meta_edges))
    print('length of CA in with all connections:', counter_integrated)


def get_rela_and_add_to_tsv_file(query_general, pharmGKB_label, label):
    """
    ssearch for all relationship pairs of a given pGKB label and db label and write into a tsv file.
    :param query_general: string
    :param pharmGKB_label: string
    :param label: string
    :return:
    """
    query = query_general % (pharmGKB_label, label)
    results = g.run(query)
    counter = 0
    counter_specific = 0
    for meta_id, other_id, in results:
        counter += 1
        if meta_id in dict_meta_id_to_clinical_annotation_info:
            counter_specific += 1
            dict_rela_partner_to_tsv_file[label].writerow([meta_id, other_id])

    return counter, counter_specific


def fill_the_rela_files():
    """
    
    :return: 
    """
    query_general = 'Match (n:PharmGKB_ClinicalAnnotation)--(:%s)--(m:%s) Return Distinct n.id, m.identifier'
    for pharmGKB_label, label in dict_pGKB_label_to_label.items():
        counter = 0
        counter_specific = 0
        if type(label) == str:
            counter, counter_specific = get_rela_and_add_to_tsv_file(query_general, pharmGKB_label, label)
        else:
            for db_label in label:
                counter_part, counter_specific_part = get_rela_and_add_to_tsv_file(query_general, pharmGKB_label,
                                                                                   db_label)
                counter += counter_part
                counter_specific += counter_specific_part
        print('count rela with ' + pharmGKB_label + ':', counter)
        print('count rela with ' + pharmGKB_label + ' and other condition are working:', counter_specific)


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
    print('get all CA ids wher not all connections exists')

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
    print('Load in metadata from pharmebinet')

    load_db_info_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Fill rela files')

    fill_the_rela_files()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
