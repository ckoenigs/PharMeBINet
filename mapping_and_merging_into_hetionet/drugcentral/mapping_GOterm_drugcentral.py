import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


dict_bioPro_to_resource = {}
dict_bioPro_to_name = {}
dict_bioPro_name = {}
dict_bioPro_altID = defaultdict(set)
dict_molFu_to_resource = {}
dict_molFu_to_name = {}
dict_molFu_name = {}
dict_molFu_altID = defaultdict(set)
dict_cellCo_to_resource = {}
dict_cellCo_to_name = {}
dict_cellCo_name = {}
dict_cellCo_altID = defaultdict(set)


def load_biologicalProcess_in():
    # query ist ein String
    query = '''MATCH (n:BiologicalProcess) RETURN n'''
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        name = node["name"]
        alt_ids = node["alternative_ids"] if "alternative_ids" in node else []

        dict_bioPro_to_name[identifier] = name
        dict_bioPro_to_resource[identifier] = resource

        for alt_id in alt_ids:
            dict_bioPro_altID[alt_id].add(identifier)

        # name
        if name not in dict_bioPro_name:
            dict_bioPro_name[name] = set()
        dict_bioPro_name[name].add(identifier)


def load_cellularComponent_in():
    # query ist ein String
    query = '''MATCH (n:CellularComponent) RETURN n'''
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        name = node["name"]
        alt_ids = node["alternative_ids"] if "alternative_ids" in node else []

        dict_cellCo_to_name[identifier] = name
        dict_cellCo_to_resource[identifier] = resource

        for alt_id in alt_ids:
            dict_molFu_altID[alt_id].add(identifier)

        # name
        if name not in dict_cellCo_name:
            dict_cellCo_name[name] = set()
        dict_cellCo_name[name].add(identifier)


def load_molecularFunction_in():
    # query ist ein String
    query = '''MATCH (n:MolecularFunction) return n'''
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        name = node["name"]
        alt_ids = node["alternative_ids"] if "alternative_ids" in node else []

        dict_molFu_to_name[identifier] = name
        dict_molFu_to_resource[identifier] = resource

        for alt_id in alt_ids:
            dict_molFu_altID[alt_id].add(identifier)

        # name
        if name not in dict_molFu_name:
            dict_molFu_name[name] = set()
        dict_molFu_name[name].add(identifier)


def load_GO_term_in():
    query = '''MATCH (n:DC_GOTerm) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_bioPro = set()
    mapped_cellCo = set()
    mapped_molFu = set()
    dict_nodes_to_term = {}
    dict_node_to_methode = {}

    for node, node_id, in results:
        type = node["type"]
        term_name = node["term"]
        go_id = node["id"]
        count = 0

        if type is not None:
            # biological Process
            if type == 'P':
                if go_id in dict_bioPro_to_name:
                    dict_nodes_to_term[node_id] = set([go_id])
                    if node_id not in dict_node_to_methode:
                        dict_node_to_methode[node_id] = set()
                    dict_node_to_methode[node_id].add('go_id')
                    mapped_bioPro.add(node_id)

                # mappen mit alternative IDs
                if go_id in dict_bioPro_altID:
                    dict_nodes_to_term[node_id] = dict_bioPro_altID[go_id]
                    if node_id not in dict_node_to_methode:
                        dict_node_to_methode[node_id] = set()
                    dict_node_to_methode[node_id].add('alt_id')
                    mapped_bioPro.add(node_id)

            # cellular Component
            if type == 'C':
                if go_id in dict_cellCo_to_name:
                    dict_nodes_to_term[node_id] = set([go_id])
                    if node_id not in dict_node_to_methode:
                        dict_node_to_methode[node_id] = set()
                    dict_node_to_methode[node_id].add('go_id')
                    mapped_cellCo.add(node_id)

                # mappen mit alternative ID
                if go_id in dict_cellCo_altID:
                    dict_nodes_to_term[node_id] = dict_cellCo_altID[go_id]
                    if node_id not in dict_node_to_methode:
                        dict_node_to_methode[node_id] = set()
                    dict_node_to_methode[node_id].add('alt_id')
                    mapped_cellCo.add(node_id)

            # moleculaar Function
            if type == 'F':
                if go_id in dict_molFu_to_name:
                    dict_nodes_to_term[node_id] = set([go_id])
                    if node_id not in dict_node_to_methode:
                        dict_node_to_methode[node_id] = set()
                    dict_node_to_methode[node_id].add('go_id')
                    mapped_molFu.add(node_id)

                # mappen mit alternative ID
                if go_id in dict_molFu_altID:
                    dict_nodes_to_term[node_id] = dict_molFu_altID[go_id]
                    if node_id not in dict_node_to_methode:
                        dict_node_to_methode[node_id] = set()
                    dict_node_to_methode[node_id].add('alt_id')
                    mapped_molFu.add(node_id)

        # not_mapped.tsv erstellen
        if node_id not in mapped_bioPro:
            if node_id not in mapped_cellCo:
                if node_id not in mapped_molFu:
                    csv_not_mapped.writerow([node_id, go_id, type, term_name])

    # mapped tsv erstellen
    for node_id in mapped_bioPro:
        methodes = list(dict_node_to_methode[node_id])
        goTerm_ids = dict_nodes_to_term[node_id]
        for goTerm_id in goTerm_ids:
            resource = set(dict_bioPro_to_resource[goTerm_id])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_bioPro.writerow([node_id, goTerm_id, resource, methodes])

    for node_id in mapped_cellCo:
        methodes = list(dict_node_to_methode[node_id])
        goTerm_ids = dict_nodes_to_term[node_id]
        for goTerm_id in goTerm_ids:
            resource = set(dict_cellCo_to_resource[goTerm_id])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_cellCo.writerow([node_id, goTerm_id, resource, methodes])

    for node_id in mapped_molFu:
        methodes = list(dict_node_to_methode[node_id])
        goTerm_ids = dict_nodes_to_term[node_id]
        for goTerm_id in goTerm_ids:
            resource = set(dict_molFu_to_resource[goTerm_id])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_molFu.writerow([node_id, goTerm_id, resource, methodes])


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_goTerm = open('goTerm/not_mapped_goTerm.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_goTerm, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['node_id, id', 'type', 'name'])

file_mapped_bioPro = open('goTerm/mapped_bioPro.tsv', 'w', encoding="utf-8")
csv_mapped_bioPro = csv.writer(file_mapped_bioPro, delimiter='\t', lineterminator='\n')
csv_mapped_bioPro.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])

file_mapped_cellCo = open('goTerm/mapped_cellCo.tsv', 'w', encoding="utf-8")
csv_mapped_cellCo = csv.writer(file_mapped_cellCo, delimiter='\t', lineterminator='\n')
csv_mapped_cellCo.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])

file_mapped_molFu = open('goTerm/mapped_molFu.tsv', 'w', encoding="utf-8")
csv_mapped_molFu = csv.writer(file_mapped_molFu, delimiter='\t', lineterminator='\n')
csv_mapped_molFu.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])


def generate_cypher_file(file_name, label):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugcentral/goTerm/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:DC_GOTerm), (c:%s{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_%s_drugcentral{how_mapped:line.how_mapped}]->(n); \n'''
    query = query % (path_of_directory, file_name, label, label.lower())
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral go')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')


    create_connection_with_neo4j()

    print('#####################################################################################')
    print("load biological process in")
    print(datetime.datetime.now())
    load_biologicalProcess_in()

    print('#####################################################################################')
    print("load cellular Component in")
    print(datetime.datetime.now())
    load_cellularComponent_in()

    print('#####################################################################################')
    print("load molecular function in")
    print(datetime.datetime.now())
    load_molecularFunction_in()

    print('#####################################################################################')
    print("load GO term")
    print(datetime.datetime.now())
    load_GO_term_in()

    print('#####################################################################################')

    # cypher files für die jeweiligen Entitäten, 2 sind auskommentiert, da alle Fuktionen dieselbe cypher file erstellen
    generate_cypher_file("mapped_bioPro.tsv", 'BiologicalProcess')
    generate_cypher_file("mapped_cellCo.tsv", 'CellularComponent')
    generate_cypher_file("mapped_molFu.tsv", 'MolecularFunction')


if __name__ == "__main__":
    # execute only if run as a script
    main()
