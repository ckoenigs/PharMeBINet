import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv writer
    """
    # file from relationship between compound and pc
    file_name = 'compound_to_pc'
    file = open('compound_pc/' + file_name + '.tsv', 'w', encoding='utf-8')
    header = ['pc_id', 'compound_id']
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file = open('rela_protein/cypher.cypher', 'a', encoding='utf-8')

    query = ''' Match (n:Compound{identifier:line.compound_id}), (v:PharmacologicClass{identifier:line.pc_id}) MERGE (v)-[r:INCLUDES_PCiCH]->(n) On Create set  r.license="%s",  r.source="DrugBank", r.drugbank="yes", r.resource=["DrugBank"], r.url="https://go.drugbank.com/drugs/"+line.compound_id On Match Set r.drugbank="yes", r.resource=["DrugBank"]+r.resource '''
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/compound_pc/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping



def load_all_pair_and_prepare_for_dictionary(csv_mapping):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    :param csv_mapping:
    :return:
    """
    query = "MATCH (v:PharmacologicClass)--(n:PharmacologicClass_DrugBank)-[r]-(:Compound_DrugBank)--(c:Compound) RETURN v.identifier,  c.identifier"
    results = g.run(query)

    set_drug_pc_pair = set()
    for record in results:
        [pc_id, drug_id] = record.values()
        if not (pc_id, drug_id) in set_drug_pc_pair:
            csv_mapping.writerow([pc_id, drug_id])
            set_drug_pc_pair.add((pc_id, drug_id))


def main():
    print(datetime.datetime.now())
    global path_of_directory, license
    if len(sys.argv) < 3:
        sys.exit('need path and license to directory compound- pc ' + ' '.join(sys.argv) + ' ' + str(len(sys.argv)))

    path_of_directory = sys.argv[1]
    license = sys.argv[2]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all variation from database')

    load_all_pair_and_prepare_for_dictionary(csv_mapping)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
