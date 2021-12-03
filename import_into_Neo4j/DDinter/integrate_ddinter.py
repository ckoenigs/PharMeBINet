import sys, datetime, csv
from requests import get

dict_file_name_value = {
    'A': 'Interaction involving alimentary tract and metabolism drugs',
    'B': 'Interaction involving blood and blood forming organs drugs',
    'D': 'Interaction involving dermatologicals drugs',
    'H': 'Interaction involving systemic hormonal preparations, excluding sex hormones and insulins drugs',
    'L': 'Interaction involving antineoplastic and immunomodulating agents drugs',
    'P': 'Interaction involving antiparasitic products, insecticides and repellents drugs',
    'R': 'Interaction involving respiratory system drugs',
    'V': 'Interaction involving various drugs'

}

# query start
query_start = """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/import_into_Neo4j/DDinter/%s" As line FIELDTERMINATOR '\\t'"""
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

# dictionary drug id to name
dict_drug_id_to_name = {}


def add_node_to_dictionary(drug_id, name):
    if not drug_id in dict_drug_id_to_name:
        dict_drug_id_to_name[drug_id] = name
    else:
        if dict_drug_id_to_name[drug_id] != name:
            print('ohje')


def load_data(letter, csv_writer):
    """
    The files has the format:
    0: DDInterID_A
    1: Drug_A
    2: DDInterID_B
    3: Drug_B
    4: Level
    Extract information for nodes ad edges.
    :param letter: character
    :param csv_writer: csv writer
    """
    url = 'http://ddinter.scbdd.com/static/media/download/ddinter_downloads_code_%s.csv' % (letter)
    response = get(url)
    decode_response = response.content.decode('utf-8')
    csv_reader = csv.reader(decode_response.splitlines(), delimiter=',')

    # ignore header
    next(csv_reader)
    for row in csv_reader:
        drug_id_1 = row[0]
        add_node_to_dictionary(drug_id_1, row[1])
        drug_id_2 = row[2]
        add_node_to_dictionary(drug_id_2, row[3])
        csv_writer.writerow([drug_id_1, drug_id_2, row[4], dict_file_name_value[letter]])

    print('number of different drugs:', len(dict_drug_id_to_name))


def generate_drug_file(edge_file_name):
    """
    Write durg into csv file
    :edge_file_name: string
    :return:
    """

    file_name = 'output/node.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id', 'name'])

    query = query_start + ' Create (d:drug_ddinter{identifier:line.id, name:line.name});\n'
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)
    query = 'Create Constraint On (node:drug_ddinter) Assert node.identifier Is Unique;\n'
    cypher_file.write(query)
    query = query_start + ' Match (d1:drug_ddinter{identifier:line.id1}), (d2:drug_ddinter{identifier:line.id2}) Create (d1)-[:interacts{level:line.level,rela_info:line.rela_info}]->(d2);\n'
    query = query % (path_of_directory, edge_file_name)
    cypher_file.write(query)

    for id, name in dict_drug_id_to_name.items():
        csv_writer.writerow([id, name])


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path DDinter')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load DDinter data')


    file_name = 'output/edges.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id1', 'id2', 'level', 'rela_info'])


    for letter in dict_file_name_value:
        load_data(letter, csv_writer)
        # break

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('write drug file')

    generate_drug_file(file_name)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
