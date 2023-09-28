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
cypher_file = open('output/cypher_edge.cypher', 'a', encoding='utf-8')


def write_files(label, direction_1, direction_2, rela_name):
    '''
    generate tsv file and generate query for cypher file
    :param direction_1: string
    :param direction_2: string
    :param rela_name: string
    :return:  csv writer
    '''
    # give the rela the right abbreviation
    rela_name = rela_name % (pharmebinetutils.dictionary_label_to_abbreviation['Chemical'])

    # file from relationship between gene and variant
    file_name = 'chemical_pharmacological/rela_' + rela_name + '_' + label + '.tsv'
    file_rela = open(file_name, 'w', encoding='utf-8')
    csv_rela = csv.writer(file_rela, delimiter='\t')
    header_rela = ['chemical_id', 'pharmacological_class_id', 'source']
    csv_rela.writerow(header_rela)

    query = '''Match (c:Chemical{identifier:line.chemical_id}), (p:PharmacologicClass{identifier:line.pharmacological_class_id}) Merge (c)%s[r:%s]%s(p) On Create Set r.source=line.source, r.resource=['MED-RT'], r.url='http://purl.bioontology.org/ontology/NDFRT/'+line.pharmacological_class_id , r.license='UMLS license, available at https://uts.nlm.nih.gov/license.html', r.unbiased=false, r.med_rt='yes' '''
    query = query % ( direction_1, rela_name, direction_2)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/med_rt/{file_name}',
                                              query)
    cypher_file.write(query)

    return csv_rela


# dictionary_mapping_pairs
dict_mapping_pairs = {}

# dictionary relationship to tsv
dict_rela_to_tsv = {}

# dictionary rela name in med-rt to information needed
dict_rela_name_to_other_information = {
    ('has_SC', False): ['<-', '-', 'HAS_STRUCTURAL_CLASSIFICATION_PChsc%s'],
    ('has_SC', True): ['-', '->', 'HAS_STRUCTURAL_CLASSIFICATION_%shscPC'],
    ('has_TC', False): ['<-', '-', 'HAS_THERAPEUTIC_CATEGORY_PChtc%s'],
    ('has_TC', True): ['-', '->', 'HAS_THERAPEUTIC_CATEGORY_%shtcPC'],
    ('has_PK', False): ['<-', '-', 'HAS_PHARMACOKINETIC_PChp%s'],
    ('has_PK', True): ['-', '->', 'HAS_PHARMACOKINETIC_%shpPC'],
    ('has_PE', False): ['<-', '-', 'HAS_PHYSIOLOGIC_EFFECT_PChpe%s'],
    ('has_PE', True): ['-', '->', 'HAS_PHYSIOLOGIC_EFFECT_%shpePC'],
    ('has_MoA', False): ['<-', '-', 'HAS_MECHANISM_OF_ACTION_PChmoa%s'],
    ('has_MoA', True): ['-', '->', 'HAS_MECHANISM_OF_ACTION_%shmoaPC'],
    ('CI', True): ['-', '->', 'CONTRAINDICATES_%scPC'],
    ('CI', False): ['<-', '-', 'CONTRAINDICATES_PCc%s'],
    ('site_of_metabolism', True): ['<-', '-', 'METABOLIZES_PCm%s'],
    ('site_of_metabolism', False): ['-', '->', 'METABOLIZES_%smPC'],
    ('Parent', False): ['<-', '-', 'PARENT_OF_PCpo%s'],
    ('Parent', True): ['-', '->', 'PARENT_OF_%spoPC'],
}

# set of not used pairs
set_of_not_used_pairs = set()


def load_connections(label, directions):
    '''
    Load all connection between chemical and pharmacological class from med-rt
    :return:
    '''
    to_pc = True if directions[0] == '-' else False

    query = f'Match (c:Chemical)--(:{label}){directions[0]}[t]{directions[1]}(n)--(d:PharmacologicClass) Where not (n:Chemical)  Return c.identifier, type(t), t, n, d.identifier'
    results = g.run(query)

    for record in results:
        [chemical_id, rela_type, rela, pc_node, pharmacological_class_id] = record.values()
        # ignore selfloops
        if chemical_id == pharmacological_class_id:
            continue

        source = rela['qualifier'] if 'qualifier' in rela else ''
        # remove the different suffix
        if rela_type.count('_') == 1 and not rela_type.startswith('has'):
            rela_type = rela_type.split('_')[0]

        if (rela_type, to_pc) in dict_rela_name_to_other_information:
            if (rela_type, label, to_pc) not in dict_rela_to_tsv:
                rela_info = dict_rela_name_to_other_information[(rela_type, to_pc)]
                csv_writer = write_files(label, rela_info[0], rela_info[1], rela_info[2])
                dict_rela_to_tsv[(rela_type, label, to_pc)] = csv_writer
                dict_mapping_pairs[(rela_type, label, to_pc)] = {}
        else:
            if (rela_type, label, to_pc) not in set_of_not_used_pairs:
                print((rela_type, label, to_pc))
                set_of_not_used_pairs.add((rela_type, label, to_pc))
            continue

        if (chemical_id, pharmacological_class_id) not in dict_mapping_pairs[(rela_type, label, to_pc)]:
            dict_mapping_pairs[(rela_type, label, to_pc)][(chemical_id, pharmacological_class_id)] = set()

        dict_mapping_pairs[(rela_type, label, to_pc)][(chemical_id, pharmacological_class_id)].add(source)

    for (rela_type, label, to_pc), dict_pairs in dict_mapping_pairs.items():
        for (chemical_id, pharmacological_class_id), sources in dict_pairs.items():
            sources = ['MED-RT' if x == 'MED-RT:Authority:MEDRT' else x.split(':')[-1] + ' via MED-RT' for x in sources]
            dict_rela_to_tsv[(rela_type, label, to_pc)].writerow(
                [chemical_id, pharmacological_class_id, ' and '.join(sources)])


def main():
    print(datetime.datetime.now())
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path MED-RT-RT rela')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pairs and generate files')

    for label in ['other_MEDRT', 'Chemical_Ingredient_MEDRT']:
        for directions in [['-', '->'], ['<-', '-']]:
            load_connections(label, directions)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
