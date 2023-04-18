import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary moa to rela type
dict_moa_to_rela_type = {}


def load_moa_to_edge_type():
    """
    Load manual defined relationship types
    :return:
    """
    with open('moa_to_rela_type.tsv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter='\t')
        for line in csv_reader:
            dict_moa_to_rela_type[line['Moa']] = line['edge_type']


# cypher file
cypher_file = open('output/cypher_edges.cypher', 'a', encoding='utf-8')


def prepare_query(rela_type, file_name):
    """
    Prepare the differene cypher queries for the different relationship types.
    :param rela_type: string
    :param file_name: string
    :return:
    """
    query = f'Match (m:Protein{{identifier:line.protein_id}}),(n:Chemical{{identifier:line.drug_id}}) Merge (m)<-[r:{rela_type}]-(n) On Create Set r.moas=split(line.moa,"|"), r.activities=split(line.activity,"|"), r.highest_clinical_status=split(line.highest_clinical_status,"|"), r.source="TTD", r.resource=["TTD"], r.url="ttd", r.license="No license", r.ttd="yes" On Match Set r.ttd="yes", r.resource=r.resource+"TTD"'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                              query)
    cypher_file.write(query)


# dictionary rela type to csv file
dict_rela_to_csv_file = {}


def get_right_csv_file(rela_type):
    """
    Prepare a new relationship tsv file and cypher querty if not existing
    :param rela_type: string
    :return:
    """
    rela_type = rela_type.upper() + '_CH' + ''.join([x[0].lower() for x in rela_type.split('_')]) + 'P'
    if rela_type not in dict_rela_to_csv_file:
        file_name = f'edges/{rela_type}.tsv'
        file = open(file_name, 'w', encoding='utf-8')
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(['protein_id', 'drug_id', 'moa', 'activity', 'highest_clinical_status'])
        prepare_query(rela_type, file_name)
        dict_rela_to_csv_file[rela_type] = csv_writer

    return dict_rela_to_csv_file[rela_type]


# dictionary rela to dictionary with tuple to list of properties moa, activity and highest_clinical_status
dict_rela_to_tuple_to_list_of_properties = {}


def prepare_dictionary(rela_type, protein_id, chemical_id, moa, activity, highest_clinical_status):
    """
    Prepare for each rela type an entry in the dictionary with value a dictionary with protein id and chemical id as key
     and value a list of list (moa, activity and highest_clinical_status)
    :param rela_type: string
    :param protein_id: string
    :param chemical_id: string
    :param moa: string
    :param activity: string
    :param highest_clinical_status: string
    :return:
    """
    if rela_type not in dict_rela_to_tuple_to_list_of_properties:
        dict_rela_to_tuple_to_list_of_properties[rela_type] = {}
    if (protein_id, chemical_id) not in dict_rela_to_tuple_to_list_of_properties[rela_type]:
        dict_rela_to_tuple_to_list_of_properties[rela_type][(protein_id, chemical_id)] = []
    dict_rela_to_tuple_to_list_of_properties[rela_type][(protein_id, chemical_id)].append(
        [moa, activity, highest_clinical_status])


def get_all_pairs_and_write_into_dictionary():
    query = 'Match (n:Protein)--(:TTD_Target)-[r]-(:TTD_Drug)--(m:Chemical) Return n.identifier, m.identifier, r.moa, r.activity, r.highest_clinical_status'
    results = g.run(query)
    for result in results:
        [protein_id, chemical_id, list_of_moas, activity, highest_clinical_status] = result.values()
        if list_of_moas is None:
            moa = ''
            rela_type = 'associates'
        else:
            if len(list_of_moas) > 1:
                for moa in list_of_moas:
                    moa = moa.lower()
                    # avoid problems because of tipo
                    if moa == 'agonis':
                        moa = 'agonist'
                    rela_type = dict_moa_to_rela_type[moa]
                    prepare_dictionary(rela_type, protein_id, chemical_id, moa, activity, highest_clinical_status)
                continue
            else:
                moa = list_of_moas[0]
                moa = moa.lower()
                if moa in ['immunomodulator (immunostimulant)', 'regulator (upregulator)']:
                    rela_type = 'upregulates'
                else:
                    moa = moa.split(' (')[0].split('(')[0]
                    rela_type = dict_moa_to_rela_type[moa]

        prepare_dictionary(rela_type, protein_id, chemical_id, moa, activity, highest_clinical_status)


def add_etries(set_infos, info):
    """
    add only not None information into the set
    :param set_infos: set
    :param info: string or None
    :return:
    """
    if info is not None:
        set_infos.add(info)


def prepare_tsv_and_queries():
    """
    Go through all rela types and generate tsv and cypher queries.
    Therefore, combine property information.
    :return:
    """
    for rela_type, dict_tuple_to_list_of_prop in dict_rela_to_tuple_to_list_of_properties.items():
        csv_writer = get_right_csv_file(rela_type)
        for (protein_id, chemical_id), list_of_prop in dict_tuple_to_list_of_prop.items():
            moas = set()
            activities = set()
            highest_clinical_statuses = set()
            for prop in list_of_prop:
                add_etries(moas, prop[0])
                add_etries(activities, prop[1])
                add_etries(highest_clinical_statuses, prop[2])
            csv_writer.writerow(
                [protein_id, chemical_id, '|'.join(moas), '|'.join(activities), '|'.join(highest_clinical_statuses)])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd ')

    print(datetime.datetime.now())
    print('create connection')
    create_connection_with_neo4j()

    print('#' * 50)
    print(datetime.datetime.now())
    print('load moa to edge type')
    load_moa_to_edge_type()

    print('#' * 50)
    print(datetime.datetime.now())
    print('get all pairs')
    get_all_pairs_and_write_into_dictionary()

    print('#' * 50)
    print(datetime.datetime.now())
    print('write all information into tsv and cypher query')

    prepare_tsv_and_queries()

    print('#' * 50)
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
