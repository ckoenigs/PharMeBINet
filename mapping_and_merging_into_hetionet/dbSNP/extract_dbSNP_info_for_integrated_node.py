import datetime
import sys, csv
import requests
import ujson
import time

sys.path.append("../..")
import create_connection_to_databases
sys.path.append("../../import_into_Neo4j/dbSNP")
import prepare_a_single_node


'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def add_entry_to_dictionary(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


# all nodes id to node infos
dict_nodes = {}

# set of all not existing dbSNP ids
set_not_existing_dbSNP_ids=set()


def load_already_extracted_infos_from_file():
    """
    To avoid to many questions to the api a file with the information is generated and if generated the data are
    add into a dictionary
    :return:
    """
    global file , csv_file_not_existing_ids
    file_name = 'data/api_infos.json'
    try:
        file = open(file_name, 'r')
        for line in file.readlines():
            node = ujson.loads(line)
            node_id = node['refsnp_id']
            dict_nodes[node_id] = node
        file.close()
        file=open(file_name, 'a')
    except:
        file = open(file_name, 'w')
        
    file_name_not_existing='data/not_existing_ids.tsv'
    try:
        file_not_existing_ids = open(file_name_not_existing, 'r')
        csv_reader=csv.reader(file_not_existing_ids)
        for line in csv_reader:
            set_not_existing_dbSNP_ids.add(line[0])
        file_not_existing_ids.close()
        file_not_existing_ids=open(file_name_not_existing, 'a')
        csv_file_not_existing_ids=csv.writer(file_not_existing_ids)
    except:
        file_not_existing_ids = open(file_name_not_existing, 'w')
        csv_file_not_existing_ids=csv.writer(file_not_existing_ids)
    



def prepare_string_to_right_json_string(res_string):
    """
    prepare dbSNP "json" to a real json string
    :param res_string: string
    :return: string
    """
    file.write(res_string.replace('}{"refsnp_id"', '}\n{"refsnp_id"')+'\n')
    res_string = '{"nodes":[' + res_string + ']}'
    res_string = res_string.replace('}{"refsnp_id"', '},{"refsnp_id"')
    return res_string


def ask_api_and_prepare_return(ids):
    """
    Load dbSNP infos from API and preapare ad dictionary of nodes
    :param ids: string
    :return: dictionary {nodes:[node, node,...]}
    """
    dict_nodes_new={}
    if len(ids)>0:
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=snp&id=%s&rettype=json&retmode=text'
        url = url % (ids)
        res = requests.get(url)
        res_json_string = res.text
        if res_json_string=='' and not ',' in ids:
            csv_file_not_existing_ids.writerow([ids])
            print(ids)
            return dict_nodes_new
        # check if nothing is found all ids single, because if one id is not existing in dbSNP anymore then nothing is 
        # found. Therefore, check every id one by one. 
        elif res_json_string=='':
            for single_id in ids.split(','):
                time.sleep(5)
                dict_node_new= ask_api_and_prepare_return(single_id)
                dict_nodes_new.update(dict_node_new)
            return dict_nodes_new

        res_json_string = prepare_string_to_right_json_string(res_json_string)
        dict_nodes_new=ujson.loads(res_json_string)
    return dict_nodes_new

def add_information_from_api_dictionary_to_files(dict_nodes_to_list):
    """
    Check if the api give some information and then pasre every node information into files
    :param dict_nodes_to_list: dictionary
    :return:
    """
    if 'nodes' in dict_nodes_to_list:
        for node in dict_nodes_to_list['nodes']:
            prepare_a_single_node.prepare_json_information_to_tsv(node)


def load_dbSNP_data_for_nodes_with_dbSNP_in_db():
    # prepare cypher query and csv file for snp
    prepare_a_single_node.path_to_data =path_of_directory
    prepare_a_single_node.prepare_snp_file()

    # get nodes which should get dbSNP information
    query = 'Match (n:GeneVariant) Where n.identifier starts with "rs"  Return n.identifier '
    results = g.run(query)
    string_of_ids = ''
    counter_to_seek=0
    counter_all=0
    for rs_id, in results:
        # print(rs_id)
        counter_all+=1
        rs_id= rs_id.replace('rs', '')
        if rs_id not in dict_nodes and not rs_id in set_not_existing_dbSNP_ids:
            # print('in api question')
            string_of_ids += rs_id + ','
            counter_to_seek+=1
            # 10 is ok but it seems like if on id is not a dbSNP id then they do not get any result of the query
            if counter_to_seek % 10==0:
                print(counter_to_seek)
                print(datetime.datetime.utcnow())
                time.sleep(5)
                dict_nodes_to_list = ask_api_and_prepare_return(string_of_ids[:-1])
                add_information_from_api_dictionary_to_files(dict_nodes_to_list)
                # print(dict_nodes_to_list)
                string_of_ids=''
        elif not rs_id in set_not_existing_dbSNP_ids :
            prepare_a_single_node.prepare_json_information_to_tsv(dict_nodes[rs_id])
        if counter_all % 500==0:
            print('100 through')


    print(string_of_ids)
    time.sleep(10)
    dict_nodes_to_list=ask_api_and_prepare_return(string_of_ids)
    add_information_from_api_dictionary_to_files(dict_nodes_to_list)
    # print(dict_nodes_to_list)



def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1] +'master_database_change/mapping_and_merging_into_hetionet/dbSNP/'
        license = sys.argv[2]
    else:
        sys.exit('need a path and license')

    print(datetime.datetime.utcnow())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load dbSNP node info from file if possible else generate a new file')

    load_already_extracted_infos_from_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load dbSNP node from db and get dbSNP infos')

    load_dbSNP_data_for_nodes_with_dbSNP_in_db()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
