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


def generate_cypher_file():
    dict_label_to_csv_mapping = {}
    # new file
    file_name_new = 'disease/new.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_writer_new = csv.writer(file_new, delimiter='\t')
    csv_writer_new.writerow(['pharmgkb_id', 'xrefs'])
    cypher_file = open('output/cypher.cypher', 'a')

    for label in ["Disease", "Symptom", "SideEffect"]:
        # csv_file
        file_name = 'disease/mapping_' + label + '.tsv'
        file = open(file_name, 'w', encoding='utf-8')
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(['disease_id', 'pharmgkb_id', 'resource', 'how_mapped'])
        dict_label_to_csv_mapping[label] = csv_writer
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:PharmGKB_Phenotype{id:line.pharmgkb_id}), (c:%s{identifier:line.disease_id})   Set c.pharmgkb='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_disease_pharmgkb{how_mapped:line.how_mapped}]->(n); \n'''

        query = query % (file_name, label)
        cypher_file.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:PharmGKB_Phenotype{id:line.pharmgkb_id}) Create (c:Phenotype{identifier:line.pharmgkb_id, name:n.name, synonyms:n.alternate_names ,xrefs:split(line.xrefs,'|'), source:"PharmGKB", url:'https://www.pharmgkb.org/disease/'+line.pharmgkb_id , license:"%s", pharmgkb:'yes', resource:['PharmGKB']})  Create (c)-[:equal_to_disease_pharmgkb{how_mapped:'new'}]->(n); \n'''

    query = query % (file_name_new, license)
    cypher_file.write(query)
    cypher_file.close()
    return dict_label_to_csv_mapping, csv_writer_new


# all nodes id to node infos
dict_nodes = {}


def load_already_extracted_infos_from_file():
    global file
    file_name = 'data/api_infos.json'
    try:
        file = open(file_name, 'r')
        for line in file.readlines():
            node = ujson.loads(line)
            node_id = node['refsnp_id']
            dict_nodes[node_id] = node_id
        file.close()
        file=open(file_name, 'a')
    except:
        file = open(file_name, 'w')



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
    dict_nodes_new={}
    if len(ids)>0:
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=snp&id=%s&rettype=json&retmode=text'
        url = url % (ids[:-1])
        res = requests.get(url)
        res_json_string = res.text
        res_json_string = prepare_string_to_right_json_string(res_json_string)
        dict_nodes_new=ujson.loads(res_json_string)
    return dict_nodes_new


def load_dbSNP_data_for_nodes_with_dbSNP_in_db():
    query = 'Match (n:Variant) Where size(labels(n))=1  Return n.identifier Limit 100'
    results = g.run(query)
    string_of_ids = ''
    counter_to_seek=0
    for rs_id, in results:
        rs_id= rs_id.replace('rs', '')
        if rs_id not in dict_nodes:
            string_of_ids += rs_id + ','
            counter_to_seek+=1
            if counter_to_seek % 10==0:
                print(10)
                time.sleep(5)
                dict_nodes_to_list = ask_api_and_prepare_return(string_of_ids)
                # print(dict_nodes_to_list)
                string_of_ids=''

    print(string_of_ids)
    time.sleep(5)
    dict_nodes_to_list=ask_api_and_prepare_return(string_of_ids)
    print(dict_nodes_to_list)



def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
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
