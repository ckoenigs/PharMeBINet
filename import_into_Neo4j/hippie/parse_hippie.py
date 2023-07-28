import csv, datetime, sys
import os.path

sys.path.append("../..")
import pharmebinetutils


def download_and_open_file():
    global csv_reader
    print('download file if not exist', datetime.datetime.now())
    if not os.path.exists('HIPPIE-current.mitab.txt'):
        url = 'http://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/HIPPIE-current.mitab.txt'
        pharmebinetutils.download_file(url,out='data/')

    file = open('data/HIPPIE-current.mitab.txt', 'r', encoding='utf-8')
    csv_reader = csv.DictReader(file, delimiter='\t')


def create_tsv_files():
    global node_file_name, header_node, csv_node
    print('start generate tsv', datetime.datetime.now())
    node_file_name = 'output/node.tsv'
    node_file = open(node_file_name, 'w', encoding='utf-8')
    csv_node = csv.writer(node_file, delimiter='\t')
    header_node = ['identifier', 'alternative_id', 'aliases', 'taxid', 'gene_name']
    csv_node.writerow(header_node)

    global edge_file_name, header_edge, csv_edge
    edge_file_name = 'output/edge.tsv'
    edge_file = open(edge_file_name, 'w', encoding='utf-8')
    csv_edge = csv.writer(edge_file, delimiter='\t')
    header_edge = ['id1', 'id2', 'detection_methods', 'publication_author', 'publication_id', 'interaction_types',
                   'source_dbs', 'interaction_ids', 'confidence_value', 'presence_in_other_species']
    csv_edge.writerow(header_edge)


def create_cypher_queries():
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

    query_node = ' Create (n:Protein_Hippie{ '
    for property in header_node:
        query_node += property + ': line.' + property + ', '
    query_node = query_node[:-2] + '})'
    query_node = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/hippie/{node_file_name}',
                                                   query_node)
    cypher_file.write(query_node)

    cypher_file.write(pharmebinetutils.prepare_index_query('Protein_Hippie', 'identifier'))
    cypher_file.close()
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding='utf-8')

    query_edge = ' Match (n:Protein_Hippie{identifier:line.id1}),(m:Protein_Hippie{identifier:line.id2}) Create (n)-[:INTERACTS{ '
    for property in header_edge[2:]:
        if property not in ['confidence_value']:
            query_edge += property + ': split(line.' + property + ', "|"), '
        else:
            query_edge += property + ': line.' + property + ', '

    query_edge = query_edge[:-2] + '}]->(m)'
    query_edge = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/hippie/{edge_file_name}',
                                                   query_edge)

    cypher_file.write(query_edge)
    cypher_file.close()


set_ids = set()


def add_check_if_entry_is_empty(value):
    return value if value != '-' else ''


"""
0:'ID Interactor A': node 1
1:'ID Interactor B': node 2
2:'Alt IDs Interactor A': node 1
3:'Alt IDs Interactor B': node 2
4:'Aliases Interactor A': node 1
5:'Aliases Interactor B': node 2
6:'Interaction Detection Methods': edge
7:'Publication 1st Author': edge
8:'Publication Identifiers': edge
9:'Taxid Interactor A': node 1
10:'Taxid Interactor B': node 2
11:'Interaction Types': edge
12:'Source Databases': edge
13:'Interaction Identifiers': edge
14:'Confidence Value': edge
15:'Presence In Other Species': edge
16:'Gene Name Interactor A': node 1
17:'Gene Name Interactor B': node 2

"""


def extract_info_from_mitab_file():
    for line in csv_reader:
        id1 = line['ID Interactor A']
        if id1 == '-':
            if line['Alt IDs Interactor A'] != '-':
                id1 = line['Alt IDs Interactor A']
            else:
                print('A', line)
        id2 = line['ID Interactor B']
        if id2 == '-':
            if line['Alt IDs Interactor B'] != '-':
                id2 = line['Alt IDs Interactor B']
            else:
                print('B', line)
        if id1 not in set_ids:
            csv_node.writerow([id1, add_check_if_entry_is_empty(line['Alt IDs Interactor A']),
                               add_check_if_entry_is_empty(line['Aliases Interactor A']),
                               add_check_if_entry_is_empty(line['Taxid Interactor A']),
                               add_check_if_entry_is_empty(line['Gene Name Interactor A'])])
            set_ids.add(id1)
        if id2 not in set_ids:
            csv_node.writerow([id2, add_check_if_entry_is_empty(line['Alt IDs Interactor B']),
                               add_check_if_entry_is_empty(line['Aliases Interactor B']),
                               add_check_if_entry_is_empty(line['Taxid Interactor B']),
                               add_check_if_entry_is_empty(line['Gene Name Interactor B'])])
            set_ids.add(id2)
        csv_edge.writerow([id1, id2, add_check_if_entry_is_empty(line['Interaction Detection Methods']),
                           add_check_if_entry_is_empty(line['Publication 1st Author']),
                           add_check_if_entry_is_empty(line['Publication Identifiers']),
                           add_check_if_entry_is_empty(line['Interaction Types']),
                           add_check_if_entry_is_empty(line['Source Databases']),
                           add_check_if_entry_is_empty(line['Interaction Identifiers']),
                           add_check_if_entry_is_empty(line['Confidence Value']),
                           add_check_if_entry_is_empty(line['Presence In Other Species'])])
        # print(dict(line))
        # print(dict(line).keys())
        # break


print(datetime.datetime.now())


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path Hippie')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('download and open data file')

    download_and_open_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create tsv files')

    create_tsv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare cypher queries')
    create_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('extract info form mitab file into different tsv files')
    extract_info_from_mitab_file()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
