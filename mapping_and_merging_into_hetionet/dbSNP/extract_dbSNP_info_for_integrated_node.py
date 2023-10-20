import datetime
import sys, csv
import requests
import ujson
import time

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("../../import_into_Neo4j/dbSNP")
import prepare_a_single_node


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def add_entry_to_dictionary(dictionary, key, value):
    """
    add entry  to dictionary
    :param dictionary:
    :param key:
    :param value:
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


# dictionary rs id to clinvar ids
dict_rs_id_to_clinvar_ids = {}


def get_all_variants_with_rs():
    """
    Get all variant which has rs ids in xrefs
    :return:
    """
    query = 'Match (n:Variant) Where not n.identifier starts with "rs" and ANY ( x IN n.xrefs WHERE x contains "dbSNP" )   Return n.identifier, n.xrefs '
    results = g.run(query)
    for record in results:
        [clinvar_id, xrefs] = record.values()
        for xref in xrefs:
            if xref.startswith('dbSNP'):
                add_entry_to_dictionary(dict_rs_id_to_clinvar_ids, xref.split(':')[1], clinvar_id)
    print('number of rs ids:', len(dict_rs_id_to_clinvar_ids))


# all nodes id to node infos
dict_nodes = {}

# set of all not existing dbSNP ids
set_not_existing_dbSNP_ids = set()

# set of dbSNP id in json
set_dbSNP_already_from_api = set()


def load_already_extracted_infos_from_file():
    """
    To avoid to many questions to the api a file with the information is generated and if generated the data are
    add into a dictionary
    :return:
    """
    global file_already_downloaded, csv_file_not_existing_ids
    file_name = '/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/dbSNP/api_infos.json'
    try:
        file_already_downloaded = open(file_name, 'r')
        counter_line = 0
        for line in file_already_downloaded.readlines():
            counter_line += 1
            node = ujson.loads(line)
            node_id = node['refsnp_id']
            # print(node_id)
            set_dbSNP_already_from_api.add(node_id)
            # dict_nodes[node_id] = node
        file_already_downloaded.close()
        file_already_downloaded = open(file_name, 'a')
    except:
        print('in new')
        file_already_downloaded = open(file_name, 'w')

    file_name_not_existing = 'data/not_existing_ids.tsv'
    try:
        file_not_existing_ids = open(file_name_not_existing, 'r')
        csv_reader = csv.reader(file_not_existing_ids)
        for line in csv_reader:
            set_not_existing_dbSNP_ids.add(line[0])
        file_not_existing_ids.close()
        file_not_existing_ids = open(file_name_not_existing, 'a')
        csv_file_not_existing_ids = csv.writer(file_not_existing_ids)
    except:
        file_not_existing_ids = open(file_name_not_existing, 'w')
        csv_file_not_existing_ids = csv.writer(file_not_existing_ids)


def prepare_string_to_right_json_string(res_string):
    """
    prepare dbSNP "json" to a real json string
    :param res_string: string
    :return: string
    """
    file_already_downloaded.write(res_string.replace('}{"refsnp_id"', '}\n{"refsnp_id"') + '\n')
    res_string = '{"nodes":[' + res_string + ']}'
    res_string = res_string.replace('}{"refsnp_id"', '},{"refsnp_id"')
    return res_string


print_a_real_error = False


def ask_api_and_prepare_return(ids):
    """
    Load dbSNP infos from API and preapare ad dictionary of nodes
    :param ids: string
    :return: dictionary {nodes:[node, node,...]}
    """
    global print_a_real_error
    dict_nodes_new = {}
    counter_not_found = 0
    if len(ids) > 0:
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=snp&id=%s&rettype=json&retmode=text'
        url = url % (ids)
        res = requests.get(url)
        res_json_string = res.text
        if res.status_code != 200 or '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">' in res_json_string:
            if not print_a_real_error:
                print(res_json_string, res.status_code)
                print_a_real_error = False
            time.sleep(10)
            res = requests.get(url)
            res_json_string = res.text
        #
        if res.status_code != 200 or '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">' in res_json_string:
            print('start error')
            print(res_json_string, res.status_code, url)
            sys.exit('second error')
        if res_json_string == '' and ',' not in ids:
            counter_not_found += 1
            csv_file_not_existing_ids.writerow([ids])
            print(ids)
            return dict_nodes_new, counter_not_found
        # check if nothing is found all ids single, because if one id is not existing in dbSNP anymore then nothing is
        # found. Therefore, check every id one by one.
        elif res_json_string == '':
            print('in loop')
            for single_id in ids.split(','):
                time.sleep(5)
                dict_node_new, count_not_found = ask_api_and_prepare_return(single_id)
                counter_not_found += count_not_found
                dict_nodes_new.update(dict_node_new)
            return dict_nodes_new, counter_not_found
        # print(ids, res_json_string)
        res_json_string = prepare_string_to_right_json_string(res_json_string)
        dict_nodes_new = ujson.loads(res_json_string)

    return dict_nodes_new, counter_not_found


def add_information_from_api_dictionary_to_files(dict_nodes_to_list):
    """
    Check if the api give some information and then parse every node information into files
    :param dict_nodes_to_list: dictionary
    :return:
    """
    if 'nodes' in dict_nodes_to_list:
        for node in dict_nodes_to_list['nodes']:
            prepare_a_single_node.prepare_json_information_to_tsv(node)


# set of dbSNP id which are in PharMeBiNet and already in json file
set_dbSnp_in_PharMeBiNEt_and_already_downloaded = set()


def load_dbSNP_data_for_nodes_with_dbSNP_in_db():
    """
    First, prepare TSV and cypher query. Next, generate TSV file for connection between nodes with rs id and dbSNP.
    Generate a further cypher file and add mapping cypher query. Next load all gene variant with rs identifier. Write
    mappings into TSV file. the rs ids are check if they are already in the api asked information or in the not existing
    file. Else it ask the api for information about rs ids of group size 10.
    :return:
    """
    # prepare cypher query and csv file for snp
    prepare_a_single_node.path_to_data = path_of_directory_dbSNP
    prepare_a_single_node.prepare_snp_file()

    file_name = 'output/rs_clinvar_rela.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['rs_id', 'clinvar_id', 'license'])

    cypher_file = open('output/cypher_dbSNP_clinVar.cypher', 'w', encoding='utf-8')
    query = ''' Match (n:Variant{identifier:line.rs_id}), (m:Variant{identifier:line.clinvar_id}) Create (m)-[:IS_ALLEL_OF_ViaoV{url:"https://www.ncbi.nlm.nih.gov/clinvar/variation/"+line.clinvar_id, license:"https://www.ncbi.nlm.nih.gov/home/about/policies/", source:"external identifier from ClinVar", resource:["ClinVar"], clinvar:"yes"}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory_dbSNP,
                                              file_name,
                                              query)
    cypher_file.write(query)

    # get nodes which should get dbSNP information
    query = 'Match (n:GeneVariant) Where n.identifier starts with "rs"  Return n.identifier '
    results = g.run(query)
    string_of_ids = ''
    counter_to_seek = 0
    counter_all = 0
    counter_not_existing = 0
    for record in results:
        [rs_id] = record.values()
        if rs_id in dict_rs_id_to_clinvar_ids:
            for clinvar_id in dict_rs_id_to_clinvar_ids[rs_id]:
                csv_writer.writerow([rs_id, clinvar_id, 'clinvar license'])
        # print(rs_id)
        counter_all += 1
        rs_id = rs_id.replace('rs', '')
        if rs_id not in set_dbSNP_already_from_api and not rs_id in set_not_existing_dbSNP_ids:
            # print('in api question')
            string_of_ids += rs_id + ','
            counter_to_seek += 1
            # 10 is ok but it seems like if on id is not a dbSNP id then they do not get any result of the query
            if counter_to_seek % 10 == 0:
                print('in api question')
                print(counter_to_seek)
                print(datetime.datetime.now())
                time.sleep(5)
                dict_nodes_to_list, counter_not_found = ask_api_and_prepare_return(string_of_ids[:-1])
                counter_not_existing += counter_not_found
                add_information_from_api_dictionary_to_files(dict_nodes_to_list)
                # print(dict_nodes_to_list)
                string_of_ids = ''
            if counter_to_seek % 5000 == 0:
                break

        elif not rs_id in set_not_existing_dbSNP_ids:
            set_dbSnp_in_PharMeBiNEt_and_already_downloaded.add(rs_id)
            # prepare_a_single_node.prepare_json_information_to_tsv(dict_nodes[rs_id])
        else:
            counter_not_existing += 1
        if counter_all % 500 == 0:
            print('500 through')

    print(string_of_ids)
    time.sleep(10)
    dict_nodes_to_list, counter_not_found = ask_api_and_prepare_return(string_of_ids)
    counter_not_existing += counter_not_found
    file_already_downloaded.close()
    add_information_from_api_dictionary_to_files(dict_nodes_to_list)
    # print(dict_nodes_to_list)

    print('all counted gene variant with rs:', counter_all)
    print('all not existing rs ids:', counter_not_existing)


def go_through_downloaded_json_and_add_them_to_tsv():
    """
    open file to  were already api information are loaded from dbSNP. Then prepare the json information and write into
    TSV file.
    :return:
    """
    file_name = '/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/dbSNP/api_infos.json'
    file_already_downloaded = open(file_name, 'r')
    counter_line = 0
    for line in file_already_downloaded.readlines():
        counter_line += 1
        node = ujson.loads(line)
        node_id = node['refsnp_id']
        if node_id in set_dbSnp_in_PharMeBiNEt_and_already_downloaded:
            prepare_a_single_node.prepare_json_information_to_tsv(node)
    file_already_downloaded.close()


def main():
    global license, path_of_directory_dbSNP
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        path_of_directory_dbSNP = path_of_directory + 'mapping_and_merging_into_hetionet/dbSNP/'
        license = sys.argv[2]
    else:
        sys.exit('need a path and license ')

    print(datetime.datetime.now())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load variant which have a rs id ')

    get_all_variants_with_rs()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load dbSNP node info from file if possible else generate a new file')

    load_already_extracted_infos_from_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load dbSNP node from db and get dbSNP infos')

    load_dbSNP_data_for_nodes_with_dbSNP_in_db()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Write already found data into tsv file')

    go_through_downloaded_json_and_add_them_to_tsv()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
