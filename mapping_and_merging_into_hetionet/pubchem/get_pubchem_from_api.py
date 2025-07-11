import datetime
import sys, csv
import requests
import time

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# all nodes id to node infos
dict_nodes = {}


def prepare_dictionary(dictionary_node):
    """
    Prepare the dictionary such that lists are strings
    :param dictionary_node:
    :return:
    """
    new_dict = {}
    for key, value in dictionary_node.items():
        if type(value) == list:
            new_dict[key] = ','.join(value)
        else:
            new_dict[key] = value
    return new_dict


def parse_sdf(sdf_string, ids, counter_not_found):
    """
    parse the sdf string to nodes  and write them to tsv files
    :param sdf_string:
    :param ids:
    :return:
    """
    dict_one_node_information = {}
    key = ''
    counter_entries = 0
    set_properties_sdf = set()
    ids_in_sdf = set()
    for line in sdf_string.split('\n'):
        if len(line.strip()) != 0:
            if line.startswith("> "):
                key = line.split('<')[1].split('>')[0]
                set_properties_sdf.add(key)
            elif line.strip() == "$$$$":
                counter_entries += 1
                ids_in_sdf.add(dict_one_node_information['PUBCHEM_COMPOUND_CID'])
                dict_one_node_information = prepare_dictionary(dict_one_node_information)
                csv_writer_api.writerow(dict_one_node_information)
                csv_writer.writerow(dict_one_node_information)
                dict_one_node_information = {}
                key = ''
            elif key != '':
                if key in dict_one_node_information and not type(dict_one_node_information[key]) == list:
                    dict_one_node_information[key] = [dict_one_node_information[key], line.strip()]
                elif key in dict_one_node_information:
                    dict_one_node_information[key].append(line.strip())
                else:
                    dict_one_node_information[key] = line.strip()

    # write all not found nodes in the not found tsv file
    difference = set(ids).difference(ids_in_sdf)
    for diff in difference:
        csv_file_not_existing_ids.writerow([diff])
        counter_not_found += 1
    # print('keys', set_properties_sdf)
    return counter_not_found


# header for the tsv files
header = ['PUBCHEM_ATOM_UDEF_STEREO_COUNT', 'PUBCHEM_COMPONENT_COUNT', 'PUBCHEM_CONNECTIVITY_SMILES',
          'PUBCHEM_SMILES', 'PUBCHEM_XLOGP3_AA', 'PUBCHEM_IUPAC_INCHIKEY', 'PUBCHEM_ATOM_DEF_STEREO_COUNT',
          'PUBCHEM_CACTVS_TAUTO_COUNT', 'PUBCHEM_CACTVS_HBOND_DONOR', 'PUBCHEM_COORDINATE_TYPE',
          'PUBCHEM_BOND_UDEF_STEREO_COUNT', 'PUBCHEM_MOLECULAR_FORMULA', 'PUBCHEM_TOTAL_CHARGE',
          'PUBCHEM_CACTVS_SUBSKEYS', 'PUBCHEM_CACTVS_COMPLEXITY', 'PUBCHEM_HEAVY_ATOM_COUNT',
          'PUBCHEM_BONDANNOTATIONS', 'PUBCHEM_IUPAC_NAME_MARKUP', 'PUBCHEM_COMPOUND_CANONICALIZED',
          'PUBCHEM_CACTVS_HBOND_ACCEPTOR', 'PUBCHEM_IUPAC_CAS_NAME', 'PUBCHEM_IUPAC_NAME',
          'PUBCHEM_IUPAC_TRADITIONAL_NAME', 'PUBCHEM_MONOISOTOPIC_WEIGHT', 'PUBCHEM_COMPOUND_CID',
          'PUBCHEM_IUPAC_INCHI', 'PUBCHEM_CACTVS_ROTATABLE_BOND', 'PUBCHEM_EXACT_MASS',
          'PUBCHEM_BOND_DEF_STEREO_COUNT', 'PUBCHEM_IUPAC_OPENEYE_NAME', 'PUBCHEM_ISOTOPIC_ATOM_COUNT',
          'PUBCHEM_MOLECULAR_WEIGHT', 'PUBCHEM_CACTVS_TPSA', 'PUBCHEM_IUPAC_SYSTEMATIC_NAME', 'PUBCHEM_XLOGP3',
          'PUBCHEM_NONSTANDARDBOND']


def generate_node_tsv_and_query():
    """
    Generate node tsv file and cypher query
    :return:
    """
    global csv_writer
    file_name = 'output/node.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, delimiter='\t', fieldnames=header)
    csv_writer.writeheader()

    with open('output/cypher.cypher', 'w', encoding='utf-8') as f:
        f.write(pharmebinetutils.prepare_index_query('PubChem_compounds', 'identifier'))
        query = 'Create (n:PubChem_compounds{identifier:line.PUBCHEM_COMPOUND_CID, %s})'
        query_prop = []
        for head in header:
            if not head in ['PUBCHEM_COMPOUND_CID', 'PUBCHEM_COORDINATE_TYPE', 'PUBCHEM_BONDANNOTATIONS']:
                query_prop.append(head + ':line.' + head)
            elif head in ['PUBCHEM_COORDINATE_TYPE', 'PUBCHEM_BONDANNOTATIONS']:
                query_prop.append(head + f':split(line.{head},"|")')
        query = query % ','.join(query_prop)
        query = pharmebinetutils.get_query_import(path_of_directory_pubchem, f'{file_name}', query)
        f.write(query)


def load_already_extracted_infos_from_file(path_start):
    """
    To avoid to many questions to the api a file with the information is generated and if generated the data are
    add into a set, and the existing pubchem are writen into the tsv file.
    :return:
    """
    global file_already_downloaded, csv_writer_api, csv_file_not_existing_ids
    file_name = path_start + 'api_infos.tsv'
    try:
        file_already_downloaded = open(file_name, 'r', encoding='utf-8')
        csv_reader = csv.DictReader(file_already_downloaded, delimiter='\t')
        counter_line = 0
        for line in csv_reader:
            counter_line += 1
            node_id = line['PUBCHEM_COMPOUND_CID']

            ############################################
            if node_id in set_of_pubchem_ids_in_pharmebinet:
                csv_writer.writerow(line)
                set_of_pubchem_ids_in_pharmebinet.remove(node_id)
        file_already_downloaded.close()
        file_already_downloaded = open(file_name, 'a')
        csv_writer_api = csv.DictWriter(file_already_downloaded, delimiter='\t', fieldnames=header)
    except:
        print('in new')
        file_already_downloaded = open(file_name, 'w')
        csv_writer_api = csv.DictWriter(file_already_downloaded, delimiter='\t', fieldnames=header)
        csv_writer_api.writeheader()

    file_name_not_existing = 'data/not_existing_ids.tsv'
    try:
        file_not_existing_ids = open(file_name_not_existing, 'r')
        csv_reader = csv.reader(file_not_existing_ids)
        for line in csv_reader:

            if line[0] in set_of_pubchem_ids_in_pharmebinet:
                set_of_pubchem_ids_in_pharmebinet.remove(line[0])
        file_not_existing_ids.close()
        file_not_existing_ids = open(file_name_not_existing, 'a')
        csv_file_not_existing_ids = csv.writer(file_not_existing_ids)
    except:
        file_not_existing_ids = open(file_name_not_existing, 'w')
        csv_file_not_existing_ids = csv.writer(file_not_existing_ids)

def ask_api_and_prepare_return(ids):
    """
    Load pubchem infos from API and prepare and add dictionary of nodes
    :param ids: string
    :return: dictionary {nodes:[node, node,...]}
    """
    counter_not_found = 0
    ids_string = ','.join(ids)
    if len(ids) > 0:
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/%s/SDF'
        url = url % (ids_string)
        res = requests.get(url)
        res_json_string = res.text
        if res.status_code != 200 or '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">' in res_json_string:
            print(res_json_string, res.status_code)
            time.sleep(10)
            res = requests.get(url)
            res_json_string = res.text
        #
        if res.status_code != 200 or '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">' in res_json_string:
            print('start error')
            print(res_json_string, res.status_code, url)
            sys.exit('second error')
        if res_json_string == '':
            for identifier in ids:
                counter_not_found += 1
                csv_file_not_existing_ids.writerow([identifier])
            print(ids)
            return counter_not_found

        else:
            counter_not_found = parse_sdf(res_json_string, ids, counter_not_found)

    return counter_not_found


# set of allpubchem chemicals in pharmebinet
set_of_pubchem_ids_in_pharmebinet = set()


def load_pubchem_ids_from_pharmebinet():
    """
    :return:
    """
    # get nodes which should get pubchem information
    query = 'Match (n:Chemical) Where n.source starts with "PubChem" Return n.identifier'
    results = g.run(query)

    for pubchem_id, in results:
        set_of_pubchem_ids_in_pharmebinet.add(pubchem_id)

    print('number of chemical in pharMeBiNet:', len(set_of_pubchem_ids_in_pharmebinet))


def get_information_from_api():
    print('number to check for api:', len(set_of_pubchem_ids_in_pharmebinet))
    api_id_list = []
    counter_to_seek = 0
    counter_not_existing = 0
    for pubchem_id in set_of_pubchem_ids_in_pharmebinet:
        api_id_list.append(pubchem_id)
        counter_to_seek += 1
        if counter_to_seek % 40 == 0:
            # print('in api question')
            # print(counter_to_seek)
            # print(datetime.datetime.now())
            time.sleep(5)
            counter_not_found = ask_api_and_prepare_return(api_id_list)
            counter_not_existing += counter_not_found
            # print(dict_nodes_to_list)
            api_id_list = []
        # if counter_to_seek % 50000 == 0:
        #     break

        if counter_to_seek % 500 == 0:
            print(datetime.datetime.now())
            print('500 through', counter_to_seek)

    time.sleep(10)
    counter_not_found = ask_api_and_prepare_return(api_id_list)
    counter_not_existing += counter_not_found
    file_already_downloaded.close()

    print('all counted gene variant with rs:', counter_to_seek)
    print('all not existing rs ids:', counter_not_existing)


def main():
    global license, path_of_directory_pubchem, path_to_data
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        path_of_directory_pubchem = path_of_directory + 'mapping_and_merging_into_hetionet/pubchem/'
        # license = sys.argv[2]
        path_to_data = 'data/'
    else:
        sys.exit('need a path and license and path to data ')

    print(datetime.datetime.now())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('prepare query and tsv file')

    generate_node_tsv_and_query()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('load pubchem ids from pharmebinet')

    load_pubchem_ids_from_pharmebinet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load pubchem node info from file if possible else generate a new file')

    load_already_extracted_infos_from_file(path_to_data)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load pubchem node from db and get pubchem infos')

    get_information_from_api()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
