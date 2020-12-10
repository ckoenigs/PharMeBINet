import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def generate_file_and_cypher():
    """
    generate cypher file and csv file
    :return:
    """
    query = '''MATCH (:protein_IID)-[p:interacts]->(:protein_IID) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields; '''
    results = g.run(query)

    file_name = 'interaction/rela'

    cypher_file = open('interaction/cypher.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/iid/%s.tsv" As line FIELDTERMINATOR '\\t' 
            Match (p1:Protein{identifier:line.protein_id_1}), (p2:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PRiPR{ '''
    query = query % (path_of_directory, file_name)

    header = ['protein_id_1', 'protein_id_2']
    for head, in results:
        header.append(head)
        if head in ['targeting_drugs', 'evidence_type', 'dbs', 'methods', 'pmids']:
            query += head + ':split(line.' + head + ',"|"), '
        else:
            query += head + ':line.' + head + ', '

    query += ' license:"blub", iid:"yes", resource:["IID"], url:"blub"}]->(p2);\n'
    cypher_file.write(query)
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()
    return csv_writer


def prepare_dictionary(dictionary):
    """
    prepare the list values in dictionary to strings
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) == list:
            value = '|'.join(value)
        new_dict[key] = value
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}


def load_and_prepare_IID_human_data():
    """
    write only rela with exp into file
    """

    query = '''Match (p1:Protein)--(:protein_IID)-[r:interacts]->(:protein_IID)--(p2:Protein) Return p1.identifier, r, p2.identifier ; '''
    results = g.run(query)

    for p1_id, rela, p2_id, in results:
        evidence_types = rela['evidence_types'] if 'evidence_types' in rela else []
        if 'exp' in evidence_types:
            rela_info = dict(rela)
            rela_info['protein_id_1'] = p1_id
            rela_info['protein_id_2'] = p2_id
            if (p1_id, p2_id) not in dict_pair_to_infos:
                dict_pair_to_infos[(p1_id, p2_id)] = []
            dict_pair_to_infos[(p1_id, p2_id)].append(rela_info)


def wirte_info_into_files():
    csv_writer = generate_file_and_cypher()
    counter = 0
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        if len(list_of_dict) == 1:
            csv_writer.writerow(prepare_dictionary(list_of_dict[0]))
        else:
            print('multi')
            new_dict = {}
            for dictionary in list_of_dict:
                for key, value in dictionary.items():
                    if not key in new_dict:
                        new_dict[key] = value
                    elif new_dict[key] != value:
                        print(p1)
                        print(p2)
                        print(key)
                        print(value)
                        print(new_dict[key])
                        if type(value) == list:
                            set_value = set(value)
                            set_value = set_value.union(new_dict[key])
                            new_dict[key] = list(set_value)
                        else:
                            print('also different type problem')

            csv_writer.writerow(prepare_dictionary(new_dict))
        counter += 1
        if counter % 10000 == 0:
            print(counter)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('generate connection to neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('load IID human data')

    load_and_prepare_IID_human_data()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('prepare files')

    wirte_info_into_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
