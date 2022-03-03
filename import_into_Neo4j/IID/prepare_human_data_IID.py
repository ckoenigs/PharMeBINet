import csv
import datetime
import wget
import gzip
import sys


def prepare_header(header):
    return header.replace(' ', '_').replace(',', '').replace('\'', '').replace('-', '_')


dict_number_to_number = {
    '1': 'one',
    '2': 'two',
    '4': 'four',
    '8': 'eight',
}


def generate_node_and_rela_file_and_query(header_rela):
    """
    generate tsv file for rela and node and also the cypher file with queries
    :param header_rela: list of strings
    :return:  csv writer for node and rela
    """
    node_file_name = 'output/node.tsv'
    node_file = open(node_file_name, 'w', encoding='utf-8')
    csv_node = csv.writer(node_file, delimiter='\t')
    csv_node.writerow(['id', 'symbols'])

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/IID/%s" As line fieldterminator '\\t' '''
    query = query_start + 'Create (p:protein_IID{identifier:line.id, symbols:split(line.symbols,"|")});\n'
    query = query % (node_file_name)
    cypher_file.write(query)
    query = 'Create Constraint On (node:protein_IID) Assert node.identifier Is Unique; \n'
    cypher_file.write(query)

    # to avoid the problem with spaces
    header_rela = [prepare_header(x) for x in header_rela]

    rela_file_name = 'output/rela.tsv'
    rela_file = open(rela_file_name, 'w', encoding='utf-8')
    csv_rela = csv.DictWriter(rela_file, delimiter='\t', fieldnames=header_rela)
    csv_rela.writeheader()

    query = query_start + 'Match (p1:protein_IID{identifier:line.uniprot1}),(p2:protein_IID{identifier:line.uniprot2}) Create (p1)-[:interacts{'
    for header in header_rela:
        if header in ['uniprot1', 'uniprot2', 'symbol1', 'symbol2']:
            continue
        elif header in ['targeting_drugs', 'evidence_type', 'db_with_ppi', 'methods', 'pmids',
                        'drugs_targeting_both_proteins', 'drugs_targeting_one_or_both_proteins',
                        'complexes_with_both_proteins', 'complexes_with_one_or_both_proteins', 'direction_information',
                        'causing_mutations', 'decreasing_mutations', 'decreasing_rate_mutations',
                        'decreasing_strength_mutations', "disrupting_mutations", "disrupting_rate_mutations",
                        "disrupting_strength_mutations", "increasing_mutations", "increasing_rate_mutations",
                        "increasing_strength_mutations", "no_effect_mutations", "unknown_effect_mutations"]:
            if header in ['evidence_type', 'db_with_ppi','experiments']:
                query += header + 's:split(line.`' + header + '`,"|"), '
            else:
                query += header + ':split(line.`' + header + '`,"|"), '
        else:
            if header.startswith('#'):
                query += header.replace('#', 'number') + ':line.`' + header + '`, '
            elif header[0] in ['1', '2', '4', '8']:
                first_letter = header[0]
                query += header.replace(first_letter, dict_number_to_number[first_letter]) + ':line.`' + header + '`, '
            else:
                query += prepare_header(header) + ':line.`' + header + '`, '
    query = query[:-2] + '}]->(p2);\n'
    query = query % (rela_file_name)
    cypher_file.write(query)

    return csv_node, csv_rela


# set protein ids
set_protein_ids = set()


def node_into_file(identifier, symbols, csv_file):
    """
    first check if node already in file or not and else add to file
    :param identifier: string
    :param symbols: string
    :param csv_file: csv writer
    """
    if identifier not in set_protein_ids:
        symbols = symbols.replace(';', '|')
        if '-' == symbols:
            symbols == ''
        csv_file.writerow([identifier, symbols])
        set_protein_ids.add(identifier)


def transform_empty_values_into_real_empty_values(dictionary):
    """
    remove the not known values int empty string because int the data the information are sigth with - or ?
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if value in ['-', '?', '0']:
            value = ''
        elif value == '1' and key in ['stable', 'transient', 'directed', 'bidirected', 'alpaca', 'cat', 'chicken',
                                      'cow', 'dog', 'duck', 'fly', 'guinea_pig', 'horse', 'mouse', 'pig', 'rabbit',
                                      'rat', 'sheep', 'turkey', 'worm', 'yeast']:
            # todo direction
            value = 'true'
        key = prepare_header(key)
        new_dict[key] = value
    if 'directions' in dictionary and dictionary['directions']=='<':
        # print(dictionary['directions'])
        uniprot1=dictionary['uniprot1']
        new_dict['uniprot1']=dictionary['uniprot2']
        new_dict['uniprot2']= uniprot1
        del new_dict['directions']
    elif 'directions' in dictionary and dictionary['directions']=='>':
        del new_dict['directions']
    return new_dict


def load_and_prepare_IID_human_data(evidence_type_filter):
    # download IID PP interaction
    url = 'http://iid.ophid.utoronto.ca/static/download/human_annotated_PPIs.txt.gz'
    filename = wget.download(url, out='data/')
    filename_without_gz = filename.rsplit('.', 1)[0]
    # file=open(filename_without_gz,'wb')
    counter_edges=0

    counter_other_type=0
    with gzip.open(filename, 'rt') as f:
        csv_file = csv.DictReader(f, delimiter='\t')
        print(csv_file.fieldnames)
        csv_node, csv_rela = generate_node_and_rela_file_and_query(csv_file.fieldnames)
        for rela_info in csv_file:
            node_into_file(rela_info['uniprot1'], rela_info['symbol1'], csv_node)
            node_into_file(rela_info['uniprot2'], rela_info['symbol2'], csv_node)

            evidence_types=rela_info['evidence_type'].split('|') # 'evidence_type'
            rela_info = transform_empty_values_into_real_empty_values(rela_info)
            if evidence_type_filter=='':
                csv_rela.writerow(rela_info)
            elif evidence_type_filter in evidence_types:
                csv_rela.writerow(rela_info)
            else:
                counter_other_type+=1
                # print('evidence types',evidence_types)
            counter_edges+=1
    print('it has a total number of edges:',counter_edges)
    print('number of edges with other evidence types:',counter_other_type)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    #evidence type filter
    evidence_type_filter=''
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        if len(sys.argv)==3:
            evidence_type_filter=sys.argv[2]
    else:
        sys.exit('need a path and a optional filter like exp, pred, ortho')

    print(datetime.datetime.utcnow())
    print('load IID human data')

    load_and_prepare_IID_human_data(evidence_type_filter)

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
