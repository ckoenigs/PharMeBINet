import csv
import datetime
import wget
import gzip
import  sys

def prepare_header(header):
    return header.replace(' ','_').replace(',','').replace('\'','').replace('-','_')

def generate_node_and_rela_file_and_query(header_rela):
    """
    generate csv file for rela and node and also the cypher file with queries
    :param header_rela: list of strings
    :return:  csv writer for node and rela
    """
    node_file_name='output/node.tsv'
    node_file=open(node_file_name,'w',encoding='utf-8')
    csv_node= csv.writer(node_file,delimiter='\t')
    csv_node.writerow(['id', 'symbols'])

    cypher_file=open('output/cypher.cypher','w',encoding='utf-8')
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/import_into_Neo4j/IID/%s" As line fieldterminator '\\t' '''
    query= query_start+ 'Create (p:protein_IID{identifier:line.id, symbols:split(line.symbols,"|")});\n'
    query=query %(node_file_name)
    cypher_file.write(query)
    query='Create Constraint On (node:protein_IID) Assert node.identifier Is Unique; \n'
    cypher_file.write(query)

    # to avoid the problem with spaces
    header_rela= [prepare_header(x) for x in header_rela]

    rela_file_name='output/rela.tsv'
    rela_file=open(rela_file_name,'w',encoding='utf-8')
    csv_rela= csv.DictWriter(rela_file,delimiter='\t', fieldnames=header_rela)
    csv_rela.writeheader()


    query=query_start+ 'Match (p1:protein_IID{identifier:line.uniprot1}),(p2:protein_IID{identifier:line.uniprot2}) Create (p1)-[:interacts{'
    for header in header_rela:
        if header in []:
            continue
        elif header in []:
            query+= header+':split(line.'+header+',";"), '
        else:
            query += header + ':line.' + header + ', '
    query = query[:-2]+'}]->(p2);\n'
    query= query %(rela_file_name)
    cypher_file.write(query)

    return csv_node,csv_rela

# set protein ids
set_protein_ids=set()

def node_into_file(identifier, symbols, csv_file):
    """
    first check if node already in file or not and else add to file
    :param identifier: string
    :param symbols: string
    :param csv_file: csv writer
    """
    if identifier not in set_protein_ids:
        symbols=symbols.replace(';','|')
        if '-'==symbols:
            symbols==''
        csv_file.writerow([identifier, symbols])
        set_protein_ids.add(identifier)

def transform_empty_values_into_real_empty_values(dictionary):
    """
    remove the not known values int empty string because int the data the information are sigth with - or ?
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict={}
    for key, value in dictionary.items():
        if value in ['-','?','0']:
            value=''
        elif value=='1':
            value='true'
        key=prepare_header(key)
        new_dict[key]=value
    return new_dict


def load_and_prepare_IID_human_data():

    # download Pathway Commons v11
    url = 'http://iid.ophid.utoronto.ca/static/download/human_annotated_PPIs.txt.gz'
    filename = wget.download(url, out='data/')
    filename_without_gz =filename.rsplit('.',1)[0]
    # file=open(filename_without_gz,'wb')
    with gzip.open(filename,'rt') as f:
        csv_file=csv.DictReader(f, delimiter='\t')
        print(csv_file.fieldnames)
        csv_node, csv_rela=generate_node_and_rela_file_and_query(csv_file.fieldnames)
        for rela_info in csv_file:
            node_into_file(rela_info['uniprot1'],rela_info['symbol1'], csv_node)
            node_into_file(rela_info['uniprot2'], rela_info['symbol2'], csv_node)

            evidence_types=rela_info['evidence type'].split(';')
            if 'exp' in evidence_types:
                rela_info=dict(rela_info)
                rela_info=transform_empty_values_into_real_empty_values(rela_info)
                csv_rela.writerow(rela_info)



 # path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('load IID human data')


    load_and_prepare_IID_human_data()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load pathway commons information')

    # pathway_commons()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()