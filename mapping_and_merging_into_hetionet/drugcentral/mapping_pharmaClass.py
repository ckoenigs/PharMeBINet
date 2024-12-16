import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session(database='graph')


# dictionary pc id to resource
dict_PharmaClassId_to_resource = {}
# dictionary mesh cui to pc identifiers
dict_pharma_mesh_cui = {}
# dictionary name to pc identifiers
dict_pharma_name = {}
# dictionary node id to dictionary pc id to set of mapping methods
dict_pharma_mapping = defaultdict(dict)


def load_pharmacological_class_in():
    """
    Load PC and generate different pc dictionaries
    :return:
    """
    query = '''MATCH (n:PharmacologicClass) RETURN n'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        pharma_name = node["name"] if "name" in node else []
        names = node["synonyms"] if "synonyms" in node else []
        xrefs = node["xrefs"] if "xrefs" in node else []

        if not names:
            names = pharma_name
        else:
            names.append(pharma_name)

        dict_PharmaClassId_to_resource[identifier] = resource

        for ref in xrefs:
            # Mesh
            if ref.startswith("MeSH"):
                uc_ref = ref.split(':')
                if uc_ref[1] not in dict_pharma_mesh_cui:
                    dict_pharma_mesh_cui[uc_ref[1]] = set()
                dict_pharma_mesh_cui[uc_ref[1]].add(identifier)

        # name
        for name in names:
            name = name.lower()
            if name not in dict_pharma_name:
                dict_pharma_name[name] = set()
            dict_pharma_name[name].add(identifier)


def load_pharmaClass_in():
    """
    Load PharmClass not the one with FDA because they are already include and map to PC
    :return:
    """
    query = '''MATCH (n:DC_PharmaClass) where n.source<>'FDA' RETURN n, id(n)'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        node_id = record.data()['id(n)']
        name = node["name"]
        name = name.lower()
        source = node["source"]
        code = node["code"]
        synonyms = node["synonyms"] if "synonyms" in node else []

        if source == "MeSH":
            if code in dict_pharma_mesh_cui:
                pharma_classes = dict_pharma_mesh_cui[code]
                for pharma_class_id in pharma_classes:
                    if pharma_class_id not in dict_pharma_mapping[node_id]:
                        dict_pharma_mapping[node_id][pharma_class_id] = set()
                    dict_pharma_mapping[node_id][pharma_class_id].add('mesh')

        if source == "FDA":
            if code in dict_PharmaClassId_to_resource:
                if code not in dict_pharma_mapping[node_id]:
                    dict_pharma_mapping[node_id][code] = set()
                dict_pharma_mapping[node_id][code].add('fda')

        if name in dict_pharma_name:
            pharma_classes = dict_pharma_name[name]
            for pharma_class_id in pharma_classes:
                if pharma_class_id not in dict_pharma_mapping[node_id]:
                    dict_pharma_mapping[node_id][pharma_class_id] = set()
                dict_pharma_mapping[node_id][pharma_class_id].add('name')

        for synonym in synonyms:
            synonym = synonym.lower()
            if synonym in dict_pharma_name:
                pharma_classes = dict_pharma_name[synonym]
                for pharma_class_id in pharma_classes:
                    if pharma_class_id not in dict_pharma_mapping[node_id]:
                        dict_pharma_mapping[node_id][pharma_class_id] = set()
                    dict_pharma_mapping[node_id][pharma_class_id].add('synonym')

        if node_id not in dict_pharma_mapping:
            csv_not_mapped.writerow([node_id, code, source, name])

    for node_id, dict_pc_to_methods in dict_pharma_mapping.items():
        for pharma_id, methods in dict_pc_to_methods.items():
            methods = '|'.join(methods)
            csv_mapped.writerow([node_id, pharma_id,
                                 pharmebinetutils.resource_add_and_prepare(dict_PharmaClassId_to_resource[pharma_id],
                                                                           'DrugCentral'), methods])


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_pharma = open('pharmaClass/not_mapped_pharmaClass.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_pharma, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['id', 'code', 'source', 'name'])

file_mapped_pharmaClass = open('pharmaClass/mapped_pharmaClass.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_pharmaClass, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])

file_mapped_chemical = open('pharmaClass/mapped_chemical.tsv', 'w', encoding="utf-8")
csv_mapped_chem = csv.writer(file_mapped_chemical, delimiter='\t', lineterminator='\n')
csv_mapped_chem.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])


def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')
    # es gibt keine mappings zu Chemical, daher ist der cypher file nur für Pharmacological class erstellt
    query = '''MATCH (n:DC_PharmaClass), (c:PharmacologicClass{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_PharmaClass_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/pharmaClass/" + file_name,
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path dc pc')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(20 * '##')
    print(datetime.datetime.now())
    print("load pharmacological Class in")

    load_pharmacological_class_in()

    print(20 * '##')
    print(datetime.datetime.now())
    print("load pharmaClass in")

    load_pharmaClass_in()

    print(20 * '##')
    print(datetime.datetime.now())
    print("generate cypher queries")

    generate_cypher_file('mapped_pharmaClass.tsv')

    print(20 * '##')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
