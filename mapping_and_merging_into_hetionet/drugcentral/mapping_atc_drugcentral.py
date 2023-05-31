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


dict_PharmaClassId_to_resource = {}
dict_pharma_atc = {}
dict_pharma_name = {}
dict_compound_atc = {}
dict_compoundId_to_resource = {}
dict_compound_name = {}
dict_atc_mapping = defaultdict(dict)
dict_compound_mapping = defaultdict(dict)


def load_pharmacological_class_in():
    query = '''MATCH (n:PharmacologicClass) RETURN n'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        pharma_name = node["name"] if "name" in node else []
        atc_codes = node["atc_codes"] if "atc_codes" in node else []
        synonyms = node["synonyms"] if "synonyms" in node else []

        for atc_code in atc_codes:
            pharmebinetutils.add_entry_to_dict_to_set(dict_pharma_atc,atc_code, identifier)

        for synonym in synonyms:
            synonym = synonym.lower()
            if synonym not in dict_pharma_name:
                dict_pharma_name[synonym] = set()
            dict_pharma_name[synonym].add(identifier)

        pharma_name = pharma_name.lower()
        if pharma_name not in dict_pharma_name:
            dict_pharma_name[pharma_name] = set()
        dict_pharma_name[pharma_name].add(identifier)

        dict_PharmaClassId_to_resource[identifier] = resource


def load_compound_in():
    query = '''MATCH (n:Compound) RETURN n'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        atc_codes = node["atc_codes"] if "atc_codes" in node else []

        if atc_codes:
            for atc_code in atc_codes:
                if atc_code not in dict_compound_atc:
                    dict_compound_atc[atc_code] = set()
                dict_compound_atc[atc_code].add(identifier)

        # compound_name = compound_name.lower()
        # if compound_name not in dict_pharma_name:
        #     dict_compound_name[compound_name] = set()
        # dict_compound_name[compound_name].add(identifier)

        dict_compoundId_to_resource[identifier] = resource


def load_atc_in():
    query = '''MATCH (n:DC_ATC) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_pharma_atc = set()
    mapped_compound_atc = set()

    for record in results:
        node_id = record.data()['id(n)']
        node = record.data()['n']
        name = node["name"]
        name = name.lower()
        code = node["code"]
        level = node["level"]

        if level == 5:
            if code in dict_compound_atc:
                compound_atc = dict_compound_atc[code]
                for compound_atc_id in compound_atc:
                    if compound_atc_id not in dict_compound_mapping[node_id]:
                        dict_compound_mapping[node_id][compound_atc_id] = set()
                    dict_compound_mapping[node_id][compound_atc_id].add('code')
                    mapped_compound_atc.add(node_id)
        else:
            continue

        if code in dict_pharma_atc:
            pharma_atc = dict_pharma_atc[code]
            for pharma_atc_id in pharma_atc:
                if pharma_atc_id not in dict_atc_mapping[node_id]:
                    dict_atc_mapping[node_id][pharma_atc_id] = set()
                dict_atc_mapping[node_id][pharma_atc_id].add('code')
                mapped_pharma_atc.add(node_id)

        elif name in dict_pharma_name:
            atc_names = dict_pharma_name[name]
            for atc_id in atc_names:
                if atc_id not in dict_atc_mapping[node_id]:
                    dict_atc_mapping[node_id][atc_id] = set()
                dict_atc_mapping[node_id][atc_id].add('name')
                mapped_pharma_atc.add(node_id)

            if node_id not in mapped_compound_atc:
                if node_id not in mapped_pharma_atc:
                    csv_not_mapped.writerow([node_id, code, name])

    for node_id in mapped_pharma_atc:
        for atc_id in dict_atc_mapping[node_id]:
            methodes = list(dict_atc_mapping[node_id][atc_id])
            methodes = '|'.join(methodes)
            resource = set(dict_PharmaClassId_to_resource[atc_id])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_pharma_atc.writerow([node_id, atc_id, resource, methodes])

    # for atc_ID in mapped_compound_atc:
    for node_id in mapped_compound_atc:
        for atc_ID in dict_compound_mapping[node_id]:
            methodes = list(dict_compound_mapping[node_id][atc_ID])
            methodes = '|'.join(methodes)
            resource = set(dict_compoundId_to_resource[atc_ID])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_compound_atc.writerow([node_id, atc_ID, resource, methodes])


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_atc = open('atc/not_mapped_atc.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_atc, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['id', 'code', 'name'])
file_mapped_pharma_atc = open('atc/mapped_pharma_atc.tsv', 'w', encoding="utf-8")
csv_mapped_pharma_atc = csv.writer(file_mapped_pharma_atc, delimiter='\t', lineterminator='\n')
csv_mapped_pharma_atc.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])

file_mapped_compound_atc = open('atc/mapped_compound_atc.tsv', 'w', encoding="utf-8")
csv_mapped_compound_atc = csv.writer(file_mapped_compound_atc, delimiter='\t', lineterminator='\n')
csv_mapped_compound_atc.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])


def generate_cyper_file(file_namePharma, file_nameCompound):
    cypher_file = open('output/cypher.cypher', 'a')

    query_Pharma = '''MATCH (n:DC_ATC), (c:PharmacologicClass{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_atc_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query_Pharma = pharmebinetutils.get_query_import(path_of_directory,
                                                     "mapping_and_merging_into_hetionet/drugcentral/atc/" + file_namePharma,
                                                     query_Pharma)
    cypher_file.write(query_Pharma)

    query_Compound = '''MATCH (n:DC_ATC), (c:Compound{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_atc_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query_Compound = pharmebinetutils.get_query_import(path_of_directory,
                                                       "mapping_and_merging_into_hetionet/drugcentral/atc/" + file_nameCompound,
                                                       query_Compound)
    cypher_file.write(query_Compound)

    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path dc atc')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')
    create_connection_with_neo4j()

    print("load pharmacological Class in")
    load_pharmacological_class_in()

    print("load compound in")
    load_compound_in()

    print("load atc in")
    load_atc_in()

    generate_cyper_file("mapped_pharma_atc.tsv", "mapped_compound_atc.tsv")

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
