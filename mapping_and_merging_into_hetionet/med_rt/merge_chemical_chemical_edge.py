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


# dictionary chemical tuple to resource
dict_chemical_tuple_to_resource = {}


def load_load_interaction_pairs():
    """
    Load all interaction tuple into a dictionary
    :return:
    """
    query = 'Match (n:Chemical)-[r:INTERACTS_CiC]->(m:Chemical) Return n.identifier, r.resource, m.identifier'
    results = g.run(query)
    for result in results:
        [chemical_id1, resource, chemical_id2] = result.values()
        dict_chemical_tuple_to_resource[(chemical_id1, chemical_id2)] = resource


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

    # file from relationship between gene and variant
    file_name = 'chemical_pharmacological/rela_' + rela_name + '_' + label + '.tsv'
    file_rela = open(file_name, 'w', encoding='utf-8')
    csv_rela = csv.writer(file_rela, delimiter='\t')
    header_rela = ['chemical_id1', 'chemical_id2', 'source', 'resource']
    csv_rela.writerow(header_rela)

    query = '''Match (c:Chemical{identifier:line.chemical_id1}), (p:Chemical{identifier:line.chemical_id2}) Merge (c)%s[r:%s]%s(p) On Create Set r.source=line.source, r.resource=['MED-RT'], r.url='http://purl.bioontology.org/ontology/NDFRT/'+line.pharmacological_class_id , r.license='UMLS license, available at https://uts.nlm.nih.gov/license.html', r.unbiased=false, r.med_rt='yes' On Match Set r.resource=split(line.resource,"|") , r.med_rt='yes' '''
    query = query % (direction_1, rela_name, direction_2)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ndf-rt/{file_name}',
                                              query)
    cypher_file.write(query)

    return csv_rela


# dictionary rela name in ndf-rt to information needed
dict_rela_name_to_other_information = {
    'CI': ['-', '->', 'INTERACTS_CiC'],
    'effect_may_be_inhibited_by': ['-', '->', 'INTERACTS_CiC'],
}

# set of not used pairs
set_of_not_used_pairs = set()


def load_connections(label):
    '''
    Load all connection betweenn chemical and pharmacological class from ndf-rt
    :return:
    '''

    query = f'Match (c:Chemical)--(:Chemical_Ingredient_MEDRT)-[t]->(n:{label})--(d:Chemical) Return c.identifier, type(t), t, d.identifier'
    results = g.run(query)

    # dictionary relationship to tsv
    dict_rela_to_tsv = {}

    # dictionary_mapping_pairs
    dict_mapping_pairs = {}

    for record in results:
        [chemical_id1, rela_type, rela, chemical_id2] = record.values()
        # ignore selfloops
        if chemical_id1 == chemical_id2:
            continue

        source = rela['qualifier'] if 'qualifier' in rela else ''
        # remove the different suffix
        if rela_type.count('_') == 1:
            rela_type = rela_type.split('_')[0]

        if rela_type in dict_rela_name_to_other_information:
            if rela_type not in dict_rela_to_tsv:
                rela_info = dict_rela_name_to_other_information[rela_type]
                csv_writer = write_files(label, rela_info[0], rela_info[1], rela_info[2])
                dict_rela_to_tsv[rela_type] = csv_writer
                dict_mapping_pairs[rela_type] = {}
        else:
            if (rela_type, label) not in set_of_not_used_pairs:
                print((rela_type, label))
                set_of_not_used_pairs.add((rela_type, label))
            continue

        if (chemical_id1, chemical_id2) not in dict_mapping_pairs[rela_type]:
            dict_mapping_pairs[rela_type][(chemical_id1, chemical_id2)] = set()

        dict_mapping_pairs[rela_type][(chemical_id1, chemical_id2)].add(source)

    for rela_type, dict_pairs in dict_mapping_pairs.items():
        rela_info = dict_rela_name_to_other_information[rela_type]
        if rela_info == 'INTERACTS_CiC':
            for (chemical_id1, chemical_id2), sources in dict_pairs.items():
                if (chemical_id1, chemical_id2) in dict_chemical_tuple_to_resource:
                    sources = ['MED-RT' if x == 'MED-RT:Authority:MEDRT' else x.split(':')[-1] + ' via MED-RT' for x in
                               sources]
                    dict_rela_to_tsv[rela_type].writerow(
                        [chemical_id1, chemical_id2, ' and '.join(sources), pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_tuple_to_resource[(chemical_id1, chemical_id2)], 'MED-RT')])
                elif (chemical_id2, chemical_id1) in dict_chemical_tuple_to_resource:
                    sources = ['MED-RT' if x == 'MED-RT:Authority:MEDRT' else x.split(':')[-1] + ' via MED-RT' for x in
                               sources]
                    dict_rela_to_tsv[rela_type].writerow(
                        [chemical_id1, chemical_id2, ' and '.join(sources), pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_tuple_to_resource[(chemical_id2, chemical_id1)], 'MED-RT')])
                else:
                    sources = ['MED-RT' if x == 'MED-RT:Authority:MEDRT' else x.split(':')[-1] + ' via MED-RT' for x in
                               sources]
                    dict_rela_to_tsv[rela_type].writerow(
                        [chemical_id1, chemical_id2, ' and '.join(sources)])


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
    print('load interaction pairs')

    load_load_interaction_pairs()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pairs and generate files')

    for label in ['other_MEDRT', 'Chemical_Ingredient_MEDRT']:
        load_connections(label)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
