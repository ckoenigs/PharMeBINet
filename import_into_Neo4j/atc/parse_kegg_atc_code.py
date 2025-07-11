# https://www.genome.jp/kegg-bin/get_htext?br08303.keg
# https://www.genome.jp/kegg-bin/download_htext?htext=br08303.keg&format=json&filedir=
import csv, os
import ujson, sys
import datetime
import urllib.request

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

sys.path.append("../..")
import pharmebinetutils


def prepare_node_tsv_and_rela_tsv():
    """
    Prepare different TSV files and generate cypher file and the fitting cypher queries.
    :return:
    """
    file_name = 'output/node.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id', 'name'])

    file_name_edge = 'output/edge.tsv'
    file_edge = open(file_name_edge, 'w', encoding='utf-8')
    csv_writer_edge = csv.writer(file_edge, delimiter='\t')
    csv_writer_edge.writerow(['id1', 'id2'])

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = 'Create (n:atc_kegg{identifier:line.id, name:line.name})'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/atc/{file_name}', query)
    cypher_file.write(query)
    cypher_file.write(pharmebinetutils.prepare_index_query('atc_kegg', 'identifier'))

    query = 'Match (n:atc_kegg{identifier:line.id1}),(m:atc_kegg{identifier:line.id2}) Create (m)-[:belongs_to]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/atc/{file_name_edge}', query)
    cypher_file.write(query)

    return csv_writer, csv_writer_edge


def parse_name_to_id_and_name(string_name, csv_node):
    level_node = string_name.split(' ', 1)
    level_id = level_node[0]
    level_name = level_node[1].split(' [DG')[0]
    csv_node.writerow([level_id, level_name])
    return level_id


def load_information_form_json(csv_node, csv_edge):
    """
    Open ATC json and extract atc nodes and structures.
    :param csv_node:
    :param csv_edge:
    :return:
    """
    file = open('data/atc_kegg.json', 'r', encoding='utf-8')
    data = ujson.load(file)

    # level 1 children
    for child in data['children']:
        level1_id = parse_name_to_id_and_name(child['name'], csv_node)
        # level 2 children
        for level2_child in child['children']:
            level2_id = parse_name_to_id_and_name(level2_child['name'], csv_node)
            csv_edge.writerow([level1_id, level2_id])

            if 'children' in level2_child:
                # level 3 children
                for level3_child in level2_child['children']:
                    level3_id = parse_name_to_id_and_name(level3_child['name'], csv_node)
                    csv_edge.writerow([level2_id, level3_id])

                    if 'children' in level3_child:
                        # level 4 children
                        for level4_child in level3_child['children']:
                            level4_id = parse_name_to_id_and_name(level4_child['name'], csv_node)
                            csv_edge.writerow([level3_id, level4_id])
                            if 'children' in level4_child:
                                # level 5 children
                                for level5_child in level4_child['children']:
                                    level5_id = parse_name_to_id_and_name(level5_child['name'], csv_node)
                                    csv_edge.writerow([level4_id, level5_id])



def get_website_source(url: str) -> str:
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/35.0.1916.47 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response:
        print(response.headers)
        print(response.headers.get_content_charset())
        return response.read().decode('utf-8')

def check_for_new_version():
    try:
        source=get_website_source('https://www.genome.jp/kegg-bin/get_htext?br08303.keg')
        # parsed_html = BeautifulSoup(source, "lxml")
        if '<br>Last updated: ' in source:
            last_updated=source.split('<br>Last updated: ')[1].split('<br>')[0]
            print(last_updated)
            last_update_date=datetime.datetime.strptime(last_updated, '%B %d, %Y')
            print(last_update_date)
        download=False
        if os.path.isfile('update.txt'):
            with open('update.txt', 'r', encoding='utf-8') as f:
                other_data=next(f)
                print(other_data)
                other_data_update=datetime.datetime.strptime(other_data, '%Y-%m-%d')
                if other_data_update < last_update_date:
                    download=True
                # f.write(last_update_date.strftime('%Y-%m-%d'))
        else:
            download=True
    except:
        print('error')
        download=True

    if download:
        print('download')
        pharmebinetutils.download_file('https://www.genome.jp/kegg-bin/download_htext?htext=br08303.keg&format=json&filedir=',out='data/', file_name='atc_kegg.json')
        with open('update.txt', 'w', encoding='utf-8') as f:
            f.write(last_update_date.strftime('%Y-%m-%d'))


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        print(path_of_directory)
    else:
        sys.exit('need a path atc')

    check_for_new_version()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare tsv and cypher queries')

    csv_node, csv_edge = prepare_node_tsv_and_rela_tsv()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('write tsv')

    load_information_form_json(csv_node, csv_edge)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
