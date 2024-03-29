import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


dict_existing_drug_interaction_to_resource = {}


def load_existing_drug_interaction():
    """
    Load all drug interaction from database
    :return:
    """
    query = '''MATCH (a:Chemical)-[s:INTERACTS_CHiCH]->(b:Chemical) RETURN a.identifier, b.identifier, s.resource'''
    results = g.run(query)
    for record in results:
        [chemical_1, chemical_2, resource] = record.values()
        dict_existing_drug_interaction_to_resource[(chemical_1, chemical_2)] = resource

    print('number of interaction in database already:', len(dict_existing_drug_interaction_to_resource))


def create_file_and_tsv_writer(file_name):
    """
    Generate file as tsv writer.
    :param file_name: string
    :return:
    """
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['chemical1', 'chemical2', 'level', 'rela_infos', 'resource'])
    return csv_writer


def load_ddinter_interaction(directory):
    """
    load all ddintere drug-drug interaction an map to existing or else create new edges.
    :param directory: directory
    :return:
    """

    # tsv_file
    file_name_mapped = directory + '/mapped_dd_inter.tsv'
    csv_writer_mapped = create_file_and_tsv_writer(file_name_mapped)

    file_name_new = directory + '/new_dd_inter.tsv'
    csv_writer_new = create_file_and_tsv_writer(file_name_new)

    # generate cypher files to integrate information
    generate_cypher_file(file_name_mapped, file_name_new)

    # get the ddinter edges
    query = '''MATCH (a:Chemical)--(:drug_ddinter)-[r:interacts]->(:drug_ddinter)--(b:Chemical) Where r.level<>'Unknown' RETURN a.identifier, b.identifier, collect(r.level), collect(r.rela_info) '''
    results = g.run(query)

    counter_all = 0
    counter_new = 0

    for record in results:
        [chemical_id1, chemical_id2, levels, rela_infos] = record.values()
        levels = set(levels)
        if len(levels) > 1:
            print(chemical_id1, chemical_id2, levels, rela_infos)
            sys.exit()
        counter_all += 1
        rela_infos = set(rela_infos)
        if (chemical_id1, chemical_id2) in dict_existing_drug_interaction_to_resource:
            print('chemical 1; chemical 2')
            csv_writer_mapped.writerow([chemical_id1, chemical_id2, levels.pop(), '|'.join(rela_infos),
                                        pharmebinetutils.resource_add_and_prepare(
                                            dict_existing_drug_interaction_to_resource[(chemical_id1, chemical_id2)],
                                            "DDinter")])
        elif (chemical_id2, chemical_id1) in dict_existing_drug_interaction_to_resource:
            print(';P')
            resource = set(dict_existing_drug_interaction_to_resource[(chemical_id2, chemical_id1)])
            resource.add('DDinter')
            csv_writer_mapped.writerow([chemical_id2, chemical_id1, levels.pop(), '|'.join(rela_infos),
                                        pharmebinetutils.resource_add_and_prepare(
                                            dict_existing_drug_interaction_to_resource[(chemical_id2, chemical_id1)],
                                            "DDinter")])
        else:
            counter_new += 1
            csv_writer_new.writerow(
                [chemical_id1, chemical_id2, levels.pop(), '|'.join(rela_infos)])

    print('count all edges:', counter_all)
    print('count new edges:', counter_new)


# cypher file generation
cypher_file = open('output/cypher_edge.cypher', 'w')


def generate_cypher_file(file_name, file_name_new):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param file_name_new: string
    :return:
    """
    query = ''' MATCH (n:Chemical{identifier:line.chemical1}), (c:Chemical{identifier:line.chemical2}) Match (n)-[r:INTERACTS_CHiCH]->(c)  Set r.resource=split(line.resource,"|"), r.ddinter="yes", r.level=line.level, r.rela_infos=split(line.rela_infos,"|")'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/DDinter/{file_name}', query)
    cypher_file.write(query)

    query = '''MATCH (n:Chemical{identifier:line.chemical1}), (c:Chemical{identifier:line.chemical2}) Create (n)-[r:INTERACTS_CHiCH{source:"DDinter", resource:["DDinter"], source:"DDinter", ddinter:"yes" , license:"%s", level:line.level, rela_infos:split(line.rela_infos,"|")}]->(c) '''
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/DDinter/{file_name_new}',
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory, license
    license = ''
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license ')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load existings drug-drug interactions')

    load_existing_drug_interaction()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in dd-interaction from ddinter in')

    load_ddinter_interaction('output')

    driver.close()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
