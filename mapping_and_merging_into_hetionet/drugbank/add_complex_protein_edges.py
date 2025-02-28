import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases  # , authenticate
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def create_cypher_and_tsv_files():
    """
    Create cypher and tsv files for nodes and relationships
    :return:
    """
    file_name='rela_protein/complex_protein.tsv'
    rela_file = open(file_name, 'w')
    global  csv_rela
    rela_header = ['complex_id', 'protein_id']

    cypher_rela = open('rela_protein/cypher.cypher', 'a', encoding='utf-8')
    query_rela = 'Match (b:MolecularComplex{identifier:line.complex_id}), (a:Protein {identifier:line.protein_id}) Create (b)-[r:HAS_COMPONENT_MChcP{license:"%s", url:"https://go.drugbank.com/bio_entities/"+line.complex_id, source:"DrugBank", resource:["DrugBank"], drugbank:"yes" }]->(a)'
    query_rela = query_rela % (license)
    query_rela = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/drugbank/{file_name}',
                                                   query_rela)
    cypher_rela.write(query_rela)
    cypher_rela.close()
    csv_rela = csv.writer(rela_file, delimiter='\t')
    csv_rela.writerow(rela_header)



def fill_rela_tsv():
    """
    Fill the rela tsv file
    :return:
    """
    query = '''MATCH (n:Protein_DrugBank)-[:has_component_POhcPO]->(:Protein_DrugBank)--(b:Protein) RETURN n.identifier, b.identifier'''
    result = g.run(query)
    for record in result:
        [complex_id, protein_id] = record.values()
        csv_rela.writerow([complex_id, protein_id])


def main():
    # path to directory of project
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need a license')
    global license
    license = sys.argv[2]
    path_of_directory = sys.argv[1]
    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('open and create cypher and tsv files')

    create_cypher_and_tsv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('create rela')

    fill_rela_tsv()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
