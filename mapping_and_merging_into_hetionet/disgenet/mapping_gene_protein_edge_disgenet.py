import datetime
import os
import sys
import csv

sys.path.append("../..")
import create_connection_to_databases


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def open_file(file_path):
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode)
    return file


def get_pairs_information():
    '''
    Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'gene_to_protein.tsv'
    file_path = os.path.join(path_of_directory, file_name)
    cypher_name = 'cypher_edge.cypher'
    cypher_edge = open_file(os.path.join(source, cypher_name))
    gene_to_protein = open_file(os.path.join(path_of_directory, file_name))
    gene_to_protein_writer = csv.writer(gene_to_protein, delimiter='\t')
    gene_to_protein_writer.writerow(['gene_id', 'protein_id'])

    # I check manually on the new edges between gene and protein and most are not accurate, so only the existing are
    # updated
    # query = '''Match (n:Gene)--(:gene_DisGeNet)-[k]-(:protein_DisGeNet)--(p:Protein) Merge (n)-[r:PRODUCES_GpP]->(p) On Create Set r.source="DisGeNet", r.resource=["DisGeNet"], r.disgenet="yes", r.license="CC BY 4.0" On Match Set r.resource=r.resource+"DisGeNet" r.disgenet="yes";'''
    query = f'''USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:{file_path}" AS line FIELDTERMINATOR "\\t"   Match (n:Protein{{identifier:line.protein_id}})-[r:PRODUCES_GpP]-(v:Gene{{identifier:line.gene_id}})  Set r.resource=r.resource+"DisGeNet", r.disgenet="yes";\n'''
    cypher_edge.write(query)
    cypher_edge.close()

    query = """Match (n:Gene)--(:gene_DisGeNet)-[k]-(:protein_DisGeNet)--(p:Protein) Return Distinct n.identifier,  p.identifier; """
    results = g.run(query)
    # dictionary pairs to info
    set_pairs = set()

    for gene_id, protein_id, in results:
        if (gene_id, protein_id) in set_pairs:
            continue
        gene_to_protein_writer.writerow([gene_id, protein_id])
        set_pairs.add((gene_id, protein_id))

    gene_to_protein.close()


######### MAIN #########
def main():
    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet protein')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene_protein_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all information of the genes/proteins')

    get_pairs_information()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
