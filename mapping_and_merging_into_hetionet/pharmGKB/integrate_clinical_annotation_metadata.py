import datetime
import sys, csv
from collections import defaultdict

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
    dict_rela_partner_to_csv_file[rela] = csv_file

    query_rela = query_start + ' (b:ClinicalAnnotationMetadata{identifier:line.meta_id}), (c:%s{identifier:line.other_id}) Create (b)-[:%s]->(c);\n'
    rela_name = rela_name %('CAM')
    query_rela = query_rela % (file_name, rela, rela_name)
    cypher_file.write(query_rela)


# dictionary pGKB label to normal Label
dict_pGKB_label_to_label = {
    'PharmGKB_Gene': 'Gene',
    'PharmGKB_Variant': 'Variant',
    'PharmGKB_Chemical': 'Chemical',
    'PharmGKB_Phenotype': 'Phenotype',
    'PharmGKB_Haplotype': 'Variant'
}

# dictionary label to rela_name
dict_label_to_rela_name = {
    'Gene': 'ASSOCIATES_%saG',
    'Variant': 'ASSOCIATES_%saV',
    'Chemical': 'ASSOCIATES_%saC',
    'Phenotype': 'ASSOCIATES_%saPT'
    # 'Haplotype': 'ASSOCIATES_%saH'
}


def prepare_files(directory):
    """

    :return:
    """
    file_name = directory + '/meta_node.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['identifier', 'genotypes', 'clinical_phenotypes'])

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH '''

    query_meta_node = query_start + '(n:PharmGKB_ClinicalAnnotationMetadata{id:toInteger(line.identifier)}) Create (b:ClinicalAnnotationMetadata{'
    query = 'MATCH (p:PharmGKB_ClinicalAnnotationMetadata) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
    results = g.run(query)
    for property, in results:
        if property != 'id':
            query_meta_node += property + ':n.' + property + ', '
        else:
            query_meta_node += 'identifier:toString(n.' + property + '), '

    query_meta_node += ' genotypes:split(line.genotypes,"|"), clinical_phenotypes:split(line.clinical_phenotypes, "|")  , source:"PharmGKB", resource:["PharmGKB"], meta_edge:true, license:"%s"}) Create (n)<-[:equal_metadata]-(b);\n'
    query_meta_node = query_meta_node % (file_name, license)
    cypher_file.write(query_meta_node)
    cypher_file.write('Create Constraint On (node:ClinicalAnnotationMetadata) Assert node.identifier Is Unique;\n')

    for rela, rela_name in dict_label_to_rela_name.items():
        generate_rela_files(directory, rela, rela_name, query_start)

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


# dictionary meta edge id to clinical annotation infos
dict_meta_id_to_clinical_annotation_info = {}

def load_db_info_in():
    """
    First generate the files and the queries. Then prepare clinical annotation meta data. Therefor take only where the
    chemical and variants are mapped. Also fusion the clinical_annotation into the node and write the information in a
    csv file.
    :return:
    """
    csv_writer = prepare_files('metadata_edge')
    query = '''MATCH (d:PharmGKB_ClinicalAnnotationMetadata) 
    Match (d)--(:PharmGKB_Chemical)--(:Chemical) 
    Match (d)--(g)--(:Variant) Where  'PharmGKB_Variant' in labels(g) or "PharmGKB_Haplotype" in labels(g) 
    Optional Match (d)--(:PharmGKB_Gene)--(:Gene)
    Optional  Match (d)--(:PharmGKB_Phenotype)--(:Phenotype)   
    Match (d)--(e:PharmGKB_ClinicalAnnotation)
    Return Distinct d.id, e '''
    results = g.run(query)

    counter_meta_edges = 0
    for identifier, clinical_annotation, in results:
        counter_meta_edges += 1
        if identifier not in dict_meta_id_to_clinical_annotation_info:
            dict_meta_id_to_clinical_annotation_info[identifier] = {'genotype': set(), 'clinical_phenotype': set()}
        genotype = clinical_annotation['genotype']
        clinical_phenotype = clinical_annotation['clinical_phenotype']
        dict_meta_id_to_clinical_annotation_info[identifier]['genotype'].add(genotype)
        dict_meta_id_to_clinical_annotation_info[identifier]['clinical_phenotype'].add(clinical_phenotype)

    for identifier, dict_clinical_annotations in dict_meta_id_to_clinical_annotation_info.items():
        csv_writer.writerow([identifier, '|'.join(dict_clinical_annotations['genotype']),
                             '|'.join(dict_clinical_annotations['clinical_phenotype'])])

    print('length of chemical in db:' + str(counter_meta_edges))


def fill_the_rela_files():
    """
    
    :return: 
    """
    query_general='Match (n:PharmGKB_ClinicalAnnotationMetadata)--(:%s)--(m:%s) Return Distinct n.id, m.identifier'
    for pharmGKB_label, label in dict_pGKB_label_to_label.items():
        query= query_general % (pharmGKB_label, label)
        results=g.run(query)
        counter=0
        counter_specific=0
        for meta_id, other_id, in results:
            counter+=1
            if meta_id in dict_meta_id_to_clinical_annotation_info:
                counter_specific+=1
                dict_rela_partner_to_csv_file[label].writerow([meta_id,other_id])
        print('count rela with '+pharmGKB_label+':',counter)
        print('count rela with ' + pharmGKB_label + ' and other condition are working:', counter_specific)

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

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in variant from hetionet')

    load_db_info_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Fill rela files')

    fill_the_rela_files()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
