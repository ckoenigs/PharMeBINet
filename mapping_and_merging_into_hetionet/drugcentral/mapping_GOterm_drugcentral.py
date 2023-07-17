import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionaries go to resource and alternative id to go ids
dict_bioPro_to_resource = {}
dict_bioPro_alt_ids = defaultdict(set)
dict_molFu_to_resource = {}
dict_molFu_alt_ids = defaultdict(set)
dict_cellCo_to_resource = {}
dict_cellCo_alt_ids = defaultdict(set)
# the mapping dictionaries go id of dictionaries mapped go id to set of mapping methods
dict_cellCo_mapping = defaultdict(dict)
dict_MolFu_mapping = defaultdict(dict)
dict_bioPro_mapping = defaultdict(dict)


def load_label_in(label, dict_label_to_resource, dict_label_alt_ids):
    """
    Load all nodes of a label extract the information and write the in the different dictionaries.
    :param label:
    :param dict_label_to_resource:
    :param dict_label_alt_ids:
    :return:
    """
    # query ist ein String
    query = f'MATCH (n:{label}) RETURN n'
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        alt_ids = node["alternative_ids"] if "alternative_ids" in node else []

        dict_label_to_resource[identifier] = resource

        for alt_id in alt_ids:
            dict_label_alt_ids[alt_id].add(identifier)


def map_to_on_label(go_id, node_id, dict_label_to_resource, dict_label_mapping, dict_label_alt_ids):
    """
    First try to map the go id to the go id from a given label and the try to map with the alternative ids. The mappings
    are added to a dictionary.
    :param go_id:
    :param node_id:
    :param dict_label_to_resource:
    :param dict_label_mapping:
    :param dict_label_alt_ids:
    :return:
    """
    if go_id in dict_label_to_resource:
        if node_id not in dict_label_mapping:
            dict_label_mapping[node_id][go_id] = set()
        dict_label_mapping[node_id][go_id].add('go_id')

    # mappend with alternative IDs
    if go_id in dict_label_alt_ids:
        go_ids_pharmebinet = dict_label_alt_ids[go_id]
        for go_id_pharmebinet in go_ids_pharmebinet:
            if node_id not in dict_label_mapping:
                dict_label_mapping[node_id][go_id_pharmebinet] = set()
            dict_label_mapping[node_id][go_id_pharmebinet].add('alt_id')


def generate_tsv_for_a_label(dict_label_mapped, dict_label_to_resource, csv_mapped):
    """
    Go through all mappings and prepare the information for the tsv file and fill content.
    :param dict_label_mapped:
    :param dict_label_to_resource:
    :return:
    """
    for node_id, dict_go_id_to_mapping_methods in dict_label_mapped.items():
        for goTerm_id, methods in dict_go_id_to_mapping_methods.items():
            methods = '|'.join(methods)
            csv_mapped.writerow([node_id, goTerm_id,
                                 pharmebinetutils.resource_add_and_prepare(dict_label_to_resource[goTerm_id],
                                                                           'DrugCentral'), methods])


def load_GO_term_in():
    """
    Map the go terms of dc to BP, CC and MF
    :return:
    """
    query = '''MATCH (n:DC_GOTerm) RETURN n, id(n)'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        node_id = record.data()['id(n)']
        type = node["type"]
        term_name = node["term"]
        go_id = node["id"]

        if type is not None:
            # biological Process
            if type == 'P':
                map_to_on_label(go_id, node_id, dict_bioPro_to_resource, dict_bioPro_mapping, dict_bioPro_alt_ids)

            # cellular Component
            if type == 'C':
                map_to_on_label(go_id, node_id, dict_cellCo_to_resource, dict_cellCo_mapping, dict_cellCo_alt_ids)

            if type == 'F':
                map_to_on_label(go_id, node_id, dict_molFu_to_resource, dict_MolFu_mapping, dict_molFu_alt_ids)

        # not_mapped.tsv erstellen
        if node_id not in dict_bioPro_mapping:
            if node_id not in dict_MolFu_mapping:
                if node_id not in dict_cellCo_mapping:
                    csv_not_mapped.writerow([node_id, go_id, type, term_name])

    # mapped tsv erstellen
    # bp
    generate_tsv_for_a_label(dict_bioPro_mapping, dict_bioPro_to_resource, csv_mapped_bioPro)
    # cc
    generate_tsv_for_a_label(dict_cellCo_mapping, dict_cellCo_to_resource, csv_mapped_cellCo)
    # mf
    generate_tsv_for_a_label(dict_MolFu_mapping, dict_molFu_to_resource, csv_mapped_molFu)


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

    query = '''MATCH (n:DC_GOTerm), (c:%s{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_%s_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query = query % (label, label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/goTerm/" + file_name,
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('dc go noods path')
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print('#####################################################################################')
    print("load biological process in")
    print(datetime.datetime.now())
    load_label_in('BiologicalProcess', dict_bioPro_to_resource, dict_bioPro_alt_ids)

    print('#####################################################################################')
    print("load cellular Component in")
    print(datetime.datetime.now())
    load_label_in('CellularComponent', dict_cellCo_to_resource, dict_cellCo_alt_ids)

    print('#####################################################################################')
    print("load molecular function in")
    print(datetime.datetime.now())

    load_label_in('MolecularFunction', dict_molFu_to_resource, dict_molFu_alt_ids)

    print('#####################################################################################')
    print("load GO term")
    print(datetime.datetime.now())
    load_GO_term_in()

    print('#####################################################################################')

    generate_cypher_file("mapped_bioPro.tsv", 'BiologicalProcess')
    generate_cypher_file("mapped_cellCo.tsv", 'CellularComponent')
    generate_cypher_file("mapped_molFu.tsv", 'MolecularFunction')


if __name__ == "__main__":
    # execute only if run as a script
    main()
