import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary
dict_protein = {}
dict_protein_to_name = {}
dict_protein_name = {}
dict_mapping_parameter = {}
dict_proteinId_to_resource = {}

def load_protein_in():
    """
    load all proteins in dictionaries.
    :return:
    """
    query = '''MATCH (n:Protein) RETURN n'''

    results = graph_database.run(query)

    #results werden einzeln durchlaufen
    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        prot_name = node["name"]

        names = node["synonyms"] if "synonyms" in node else[]

        #im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        dict_protein_to_name[identifier] = prot_name
        dict_proteinId_to_resource[identifier] = resource



        #name
        for name in names:
            if name not in dict_protein_name:
                dict_protein_name[name] = set()
            dict_protein_name[name].add(identifier)

def load_bioactivity_in():
    """
    Load the dC bioactivity nodes
    :return:
    """
    query = '''MATCH (n:DC_Bioactivity) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_proteins = set()
    dict_nodes = {}
    dict_nodes_to_protein = {}
    dict_node_to_methode = {}


    for node, node_id, in results:
        accession = node["accession"]
        if accession is not None:
            accession_nbrs = accession.split('|')
        protein_name = node["target_name"]
        organism = node["organism"]

        for accession_nr in accession_nbrs:
            if accession_nr in dict_protein_to_name:
                dict_nodes_to_protein[node_id] = accession_nr
                if node_id not in dict_node_to_methode:
                    dict_node_to_methode[node_id] = set()
                dict_node_to_methode[node_id].add('accession')
                mapped_proteins.add(node_id)

        if node_id not in mapped_proteins:
            # print(node_id, umls_cui, sct_id, disease_name)
            csv_not_mapped.writerow([node_id, accession_nr, protein_name, organism ])


    for node_id in mapped_proteins:
        methodes = list(dict_node_to_methode[node_id])
        protein_id = dict_nodes_to_protein[node_id]
        resource = set(dict_proteinId_to_resource[protein_id])
        # print(resource, protein_id)
        resource.add('DrugCentral')
        resource = '|'.join(resource)
        csv_mapped.writerow([node_id,protein_id, resource, methodes])


def generate_files():
    """
    prepare the different files.
    :return: file name
    """
    global  csv_mapped, csv_not_mapped
    # file for mapped or not mapped identifier
    #erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
    file_not_mapped_protein = open('protein/not_mapped_protein.tsv', 'w', encoding="utf-8")
    #Dateiformat wird gesetzt mit Trenner: Tabulator
    csv_not_mapped = csv.writer(file_not_mapped_protein,delimiter='\t', lineterminator='\n')
    #Header setzen
    csv_not_mapped.writerow(['id', 'accession_number', 'name', 'organismus'])

    file_name='protein/mapped_protein.tsv'
    file_mapped_protein = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_protein,delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['node_id','id_hetionet', 'resource', 'how_mapped'])
    return file_name




def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/drugcentral/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:DC_Bioactivity), (c:Protein{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_Bioactivity_drugcentral{how_mapped:line.how_mapped}]->(n); \n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)
    cypher_file.close()



def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral protein')

    print (datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()


    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("generate files")

    file_name=generate_files()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("load protein in")
    load_protein_in()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("load biodiversity")
    load_bioactivity_in()

    print(
        '###########################################################################################################################')

    generate_cypher_file(file_name)


    print (datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
