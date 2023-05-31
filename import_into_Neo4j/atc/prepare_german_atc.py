import csv
import sys
import datetime
import pandas as pd

sys.path.append("../..")
import pharmebinetutils


def prepare_node_tsv_and_rela_tsv():
    file_name = 'output/node.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id', 'name'])

    file_name_edge = 'output/edge.tsv'
    file_edge = open(file_name_edge, 'w', encoding='utf-8')
    csv_writer_edge = csv.writer(file_edge, delimiter='\t')
    csv_writer_edge.writerow(['id1', 'id2'])

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = 'Create (n:atc_germany{identifier:line.id, name:line.name})'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/atc/{file_name}', query)
    cypher_file.write(query)
    cypher_file.write(pharmebinetutils.prepare_index_query('atc_germany', 'identifier'))

    query = 'Match (n:atc_germany{identifier:line.id1}),(m:atc_germany{identifier:line.id2}) Create (m)-[:belongs_to]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/atc/{file_name_edge}', query)
    cypher_file.write(query)

    return csv_writer, csv_writer_edge


def load_data_from_file(csv_node, csv_edge):
    atc_infos = pd.read_excel('data/ATC GKV-AI_2023.xlsm', index_col=None, sheet_name='WIdO-Index 2023 ATC-sortiert')
    header = list(atc_infos.columns)
    print(header)
    print(atc_infos.head())
    atc_infos = atc_infos.drop(['Unnamed: 1', 'Unnamed: 3', 'DDD-Info'], axis=1)
    print(atc_infos.head())
    atc_infos = atc_infos.dropna()
    dict_atc_tree = {}
    for index, row in atc_infos.iterrows():
        atc_code = row['ATC-Code'].rstrip()
        # print(atc_code)
        csv_node.writerow([atc_code, row['ATC-Bedeutung']])
        # level 1
        if len(atc_code) == 1:
            dict_atc_tree[atc_code] = {}
        # level 2
        elif len(atc_code) == 3:
            dict_atc_tree[atc_code[0]][atc_code] = {}
        # level 3
        elif len(atc_code) == 4:
            dict_atc_tree[atc_code[0]][atc_code[0:3]][atc_code] = {}
        # level 4
        elif len(atc_code) == 5:
            dict_atc_tree[atc_code[0]][atc_code[0:3]][atc_code[0:4]][atc_code] = set()
        # level 5
        else:
            dict_atc_tree[atc_code[0]][atc_code[0:3]][atc_code[0:4]][atc_code[0:5]].add(atc_code)

    for level1, dict_level2 in dict_atc_tree.items():
        for level2, dict_level3 in dict_level2.items():
            csv_edge.writerow([level1, level2])
            for level3, dict_level4 in dict_level3.items():
                csv_edge.writerow([level2, level3])
                for level4, set_level5 in dict_level4.items():
                    csv_edge.writerow([level3, level4])
                    for level5 in set_level5:
                        csv_edge.writerow([level4, level5])


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        print(path_of_directory)
    else:
        sys.exit('need a path atc')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare tsv and cypher queries')

    csv_node, csv_edge = prepare_node_tsv_and_rela_tsv()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('write tsv')

    load_data_from_file(csv_node, csv_edge)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
