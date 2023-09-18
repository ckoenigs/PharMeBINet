import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j_and_mysql():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# open cypher file
cypher_file = open('relationships/cypher.cypher', 'a', encoding='utf-8')


def write_files(label, direction_1, direction_2, rela_name):
    '''
    generate tsv file and generate query for cypher file
    :param direction_1: string
    :param direction_2: string
    :param rela_name: string
    :return:  csv writer
    '''
    # give the rela the right abbreviation
    rela_name = rela_name % (pharmebinetutils.dictionary_label_to_abbreviation[label])

    # file from relationship between gene and variant
    file_name = 'chemical_pharmacological/rela_' + rela_name + '_' + label + '.tsv'
    file_rela = open(file_name, 'w', encoding='utf-8')
    csv_rela = csv.writer(file_rela, delimiter='\t')
    header_rela = ['chemical_id', 'pharmacological_class_id', 'source']
    csv_rela.writerow(header_rela)

    query = '''Match (c:%s{identifier:line.chemical_id}), (p:PharmacologicClass{identifier:line.pharmacological_class_id}) Merge (c)%s[r:%s]%s(p) On Create Set r.source=line.source, r.resource=['NDF-RT'], r.url='http://purl.bioontology.org/ontology/NDFRT/'+line.pharmacological_class_id , r.license='UMLS license, available at https://uts.nlm.nih.gov/license.html', r.unbiased=false, r.ndf_rt='yes' On Match Set r.resource=r.resource+'NDF-RT' , r.ndf_rt='yes' '''
    query = query % (label, direction_1, rela_name, direction_2)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ndf-rt/{file_name}',
                                              query)
    cypher_file.write(query)

    return csv_rela


# dictionary_mapping_pairs
dict_mapping_pairs = {}

# dictionary relationship to tsv
dict_rela_to_tsv = {}

# dictionary rela name in ndf-rt to information needed
# 'site_of_metabolism':['<-', '-', 'METABOLIZES_PCmC']
dict_rela_name_to_other_information = {
    # 'has': ['<-', '-', 'INCLUDES_PCi%s'],
    'has_SC': ['-', '->', 'HAS_STRUCTURAL_CLASSIFICATION_%shscPC'],
    'has_TC': ['-', '->', 'HAS_THERAPEUTIC_CATEGORY_%shtcPC'],
    'has_PK': ['-', '->', 'HAS_PHARMACOKINETIC_%shpPC'],
    'has_PE': ['-', '->', 'HAS_PHYSIOLOGIC_EFFECT_%shpePC'],
    'has_MoA': ['-', '->', 'HAS_MECHANISM_OF_ACTION_%shmoaPC'],
    'CI': ['-', '->', 'CONTRAINDICATES_%scPC'],
    'site_of_metabolism': ['<-', '-', 'METABOLIZES_PCm%s']
}


def load_connections(label):
    '''
    Load all connection betweenn chemical and pharmacological class from ndf-rt
    :return:
    '''
    query = "Match (c:%s)--(:NDFRT_DRUG_KIND)-[t]-(n)--(d:PharmacologicClass)  Where any(x in labels(n) where x in ['NDFRT_MECHANISM_OF_ACTION_KIND','NDFRT_PHARMACOKINETICS_KIND','NDFRT_PHYSIOLOGIC_EFFECT_KIND','NDFRT_THERAPEUTIC_CATEGORY_KIND']) Return c.identifier, type(t), t, d.identifier"
    query = query % (label)
    results = g.run(query)
    for record in results:
        [chemical_id, rela_type, rela, pharmacological_class_id] = record.values()
        # ignore selfloops
        if chemical_id == pharmacological_class_id:
            continue
        source = rela['source'] if 'source' in rela else ''
        # remove the different suffix
        if rela_type.count('_') == 1 and not rela_type.startswith('has_'):
            rela_type = rela_type.split('_')[0]

        if rela_type in dict_rela_name_to_other_information:
            if (rela_type, label) not in dict_rela_to_tsv:
                rela_info = dict_rela_name_to_other_information[rela_type]
                csv_writer = write_files(label, rela_info[0], rela_info[1], rela_info[2])
                dict_rela_to_tsv[(rela_type, label)] = csv_writer
                dict_mapping_pairs[(rela_type, label)] = {}
        else:
            print((rela_type, label))
            continue

        if (chemical_id, pharmacological_class_id) not in dict_mapping_pairs[(rela_type, label)]:
            dict_mapping_pairs[(rela_type, label)][(chemical_id, pharmacological_class_id)] = set()

        dict_mapping_pairs[(rela_type, label)][(chemical_id, pharmacological_class_id)].add(source)

    for (rela_type, label_loop), dict_pair_to_source in dict_mapping_pairs.items():
        if label != label_loop:
            continue
        for (chemical_id, pharmacological_class_id), sources in dict_pair_to_source.items():
            source = ' and '.join(
                ['NDF-RT' if rela_source == 'NDFRT' else rela_source + ' via NDF-RT' for rela_source in sources])
            dict_rela_to_tsv[(rela_type, label_loop)].writerow([chemical_id, pharmacological_class_id, source])


def main():
    print(datetime.datetime.now())
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path NDF-RT rela')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pairs and generate files')

    for label in ['Chemical', 'PharmacologicClass']:
        load_connections(label)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
