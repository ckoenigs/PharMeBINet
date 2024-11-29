import sys, datetime, csv
from requests import get

sys.path.append("../..")
import pharmebinetutils

def load_data():
    """
    The file has the format:
    0: gene identifier
    1: gene name
    2: disease identifier
    3: disease name
    4: source database
    5: source score
    6: confidence score
    Extract information for nodes ad edges.
    :param letter: character
    :param csv_writer: csv writer
    """
    url = 'https://download.jensenlab.org/human_disease_experiments_full.tsv'
    response = get(url)
    decode_response = response.content.decode('utf-8')
    csv_reader = csv.reader(decode_response.splitlines(), delimiter='\t')

    csv_disease, csv_gene, csv_writer = generate_files()

    set_gene_id=set()
    set_disease_id=set()

    # ignore header
    next(csv_reader)
    for row in csv_reader:
        gene_id = row[0]
        if not gene_id in set_gene_id:
            csv_gene.writerow([gene_id,row[1]])
            set_gene_id.add(gene_id)
        disease_id = row[2]
        if not disease_id in set_disease_id:
            csv_disease.writerow([disease_id,row[3]])
            set_disease_id.add(disease_id)
        csv_writer.writerow([gene_id, disease_id, row[4], row[5],row[6]])

    print('number of different genes:', len(set_gene_id))
    print('number of different disease:', len(set_disease_id))


def generate_node_file(label, cypher_file):
    """
    Prepare csv file for node with a given label and add cypher query
    :param label:
    :return:
    """

    file_name = f'output/node_{label}.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id', 'name'])

    query = f' Create (d:DISEASES_{label}{{identifier:line.id, name:line.name}})'
    query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/disease/' + file_name, query)
    cypher_file.write(query)
    cypher_file.write(pharmebinetutils.prepare_index_query(f'DISEASES_{label}', 'identifier'))
    return csv_writer

def generate_files():
    """
    Genearte gene, disease and edge tsv files
    :return:
    """

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

    csv_disease=generate_node_file('Disease', cypher_file)
    csv_gene=generate_node_file('Gene', cypher_file)

    file_name = f'output/edge.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['gene_id', 'disease_id','source','sourceScore','confidenceScore'])

    cypher_file.close()
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding='utf-8')

    query = f' Match (a:DISEASES_Gene{{identifier:line.gene_id}}), (d:DISEASES_Disease{{identifier:line.disease_id}}) Create (a)-[:association{{source:line.source,sourceScore:line.sourceScore,confidenceScore:line.confidenceScore}}]->(d)'
    query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/disease/' + file_name, query)
    cypher_file.write(query)
    cypher_file.close()

    return csv_disease, csv_gene, csv_writer


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path DISEASE')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load DISEASE data')


    load_data()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
