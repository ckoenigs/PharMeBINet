import sys, csv
import time
import datetime
import glob
import bz2
import urllib.request
import os.path
import ujson

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


request_headers = {

    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}


def download_file(url, file_name):
    """
    Download file
    :param url: string
    :param file_name: string
    :return:
    """
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open('./' + file_name, 'wb') as f:
        f.write(response.read())



def get_all_variants_with_rs(csv_writer):
    """
    Get all variant which has rs ids in xrefs and write them into the csv file if they are in the set
    :return:
    """
    query = 'Match (n:Variant) Where not n.identifier starts with "rs" and ANY ( x IN n.xrefs WHERE x contains "dbSNP" )   Return n.identifier, n.xrefs '
    results = g.run(query)
    for record in results:
        [clinvar_id, xrefs] = record.values()
        for xref in xrefs:
            if xref.startswith('dbSNP'):
                identifier = xref.split(':')[1].replace('rs', '')
                if identifier in set_of_rs_ids_in_pharmebinet:
                    csv_writer.writerow([identifier, clinvar_id, 'https://www.ncbi.nlm.nih.gov/home/about/policies/'])


# all nodes id to node infos
dict_nodes = {}

# set of all not existing dbSNP ids
set_not_existing_dbSNP_ids = set()

# set of dbSNP id in json
set_dbSNP_already_from_api = set()

# define key word for json id and the length
key_word_id = '"refsnp_id":"'
key_word_id_length = len(key_word_id)

def extract_id_from_json(line):
    """
    extract id from json with index
    :param line: string
    :return:
    """
    index_start_id = line.index(key_word_id) + key_word_id_length
    index_end_id = line.index('",')
    return line[index_start_id:index_end_id]


def load_already_extracted_infos_from_file(path_start):
    """
    To avoid to many questions to the api a file with the information is generated and if generated the data are
    add into a set, and the existing rs ids are writen into the tsv file. And remove all rs ids from the set of the pharmebinet
    :return:
    """
    global file_already_downloaded, csv_file_not_existing_ids, file_not_existing_ids
    file_name = path_start + 'dbSNP/api_infos.json'
    try:
        file_already_downloaded = open(file_name, 'r')
        counter_line = 0
        for line in file_already_downloaded:
            counter_line += 1
            node_id = extract_id_from_json(line)
            # print(node_id)

            if node_id in set_of_rs_ids_in_pharmebinet:
                node = ujson.loads(line)
                prepare_a_single_node.prepare_json_information_to_tsv(node)
                set_of_rs_ids_in_pharmebinet.remove(node_id)

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
            # set_not_existing_dbSNP_ids.add(line[0])
            if line[0] in set_of_rs_ids_in_pharmebinet:
                set_of_rs_ids_in_pharmebinet.remove(line[0])
        file_not_existing_ids.close()
        file_not_existing_ids = open(file_name_not_existing, 'a')
        csv_file_not_existing_ids = csv.writer(file_not_existing_ids)
    except:
        file_not_existing_ids = open(file_name_not_existing, 'w')
        csv_file_not_existing_ids = csv.writer(file_not_existing_ids)

    print('number after check already found nodes', len(set_of_rs_ids_in_pharmebinet))



# set of rs ids in pharmebinet
set_of_rs_ids_in_pharmebinet = set()

def load_dbSNP_data_for_nodes_with_dbSNP_in_db():
    """
    First, prepare TSV and cypher query. Next, generate TSV file for connection between nodes with rs id and dbSNP.
    Generate a further cypher file and add mapping cypher query. Next load all gene variant with rs identifier. Write
    mappings into TSV file. the rs ids are check if they are already in the api asked information or in the not existing
    file. Else it ask the api for information about rs ids of group size 10.
    :return:
    """
    global dict_rs_id_to_clinvar_ids
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
    counter_all = 0
    print('start rs', datetime.datetime.now())
    for rs_id, in results:
        counter_all += 1
        rs_id = rs_id.replace('rs', '')
        set_of_rs_ids_in_pharmebinet.add(rs_id)
    print('number of rs ids', len(set_of_rs_ids_in_pharmebinet))

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load variant which have a rs id as xref amd write clinvar dbSNP pair into tsv file')
    get_all_variants_with_rs(csv_writer)

    file.close()


def open_json_file_write_into_csv(path_to_data):
    """
    if dbSNP files are not download than download them.
    Next, load all dbSNP ids and check which where not found already.
    If some nodes where already checked before go through all files.
    """

    if not os.path.isfile(path_to_data + 'dbSNP/refsnp-chrY.json.bz2'):
        url = 'https://ftp.ncbi.nih.gov/snp/latest_release/JSON/refsnp-chr%s.json.bz2'
        list_chromosome = list(range(1, 23))
        list_chromosome.append('X')
        list_chromosome.append('Y')
        list_chromosome.append('MT')
        for chr in list_chromosome:
            url_file = url % (chr)
            print(url_file)
            pharmebinetutils.download_file(url_file, out=path_to_data + '/')
            time.sleep(30)

        # sys.exit('only download else it takes  too much time')

    print('number of rs ids which need to be checked:', len(set_of_rs_ids_in_pharmebinet))
    if len(set_of_rs_ids_in_pharmebinet) > 0:
        files = glob.glob(path_to_data + 'dbSNP/refsnp-chr*.json.bz2')
        # files = glob.glob(path_to_data + 'dbSNP/refsnp-chrY.json.bz2')
        for file in files:
            print(file)
            print(datetime.datetime.now())
            json_file = bz2.open(file, "rt")
            print(datetime.datetime.now())
            chr = file.split('refsnp-')[1].split('.json')[0]
            counter = 0
            for line in json_file:
                counter += 1
                index_start_id= line.index(key_word_id)+ key_word_id_length
                index_end_id= line.index('",')
                identifier = line[index_start_id:index_end_id]
                if identifier in set_of_rs_ids_in_pharmebinet:
                    data = ujson.loads(line)
                    file_already_downloaded.write(line)
                    prepare_a_single_node.prepare_json_information_to_tsv(data, chr)
                    set_of_rs_ids_in_pharmebinet.remove(identifier)
            print('end', datetime.datetime.now())

    file_already_downloaded.close()
    for not_matched_rs_id in set_of_rs_ids_in_pharmebinet:
        csv_file_not_existing_ids.writerow([not_matched_rs_id])
    file_not_existing_ids.close()


def main():
    global license, path_of_directory_dbSNP, path_to_data
    if len(sys.argv) > 3:
        path_of_directory = sys.argv[1]
        path_of_directory_dbSNP = path_of_directory + 'mapping_and_merging_into_hetionet/dbSNP/'
        license = sys.argv[2]
        path_to_data =sys.argv[3]
    else:
        sys.exit('need a path and license and path to data ')


    print(datetime.datetime.now())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()




    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load dbSNP node ids from pharmebinet')

    # prepare cypher query and csv file for snp
    prepare_a_single_node.path_to_data = path_of_directory_dbSNP
    prepare_a_single_node.prepare_snp_file()


    load_dbSNP_data_for_nodes_with_dbSNP_in_db()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load dbSNP node info from file if possible else generate a new file')


    load_already_extracted_infos_from_file(path_to_data)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    print('load json and prepare files')
    print(datetime.datetime.now())

    open_json_file_write_into_csv(path_to_data)

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
