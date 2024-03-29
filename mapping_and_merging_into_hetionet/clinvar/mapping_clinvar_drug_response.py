import sys
import datetime
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def database_connection():
    """
    Create connection to Neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary chemical name/synonyms to chemical id
dict_chemical_name_to_chemical_id = {}

# dictionary chemical id to resource
dict_chemical_id_to_resource = {}


def load_chemicals_from_database_and_add_to_dict():
    """
    Load all chemicals from my database  and add them into a dictionary
    :return:
    """
    query = "MATCH (n:Chemical) RETURN n"
    results = g.run(query)
    for record in results:
        chemical = record.data()['n']
        identifier = chemical['identifier']
        name = chemical['name'].lower()
        dict_chemical_id_to_resource[identifier] = set(chemical['resource'])
        if not name in dict_chemical_name_to_chemical_id:
            dict_chemical_name_to_chemical_id[name] = set()
        dict_chemical_name_to_chemical_id[name].add(identifier)
        synonyms = chemical['synonyms'] if 'synonyms' in chemical else []
        for synonym in synonyms:
            synonym = synonym.lower()
            if not synonym in dict_chemical_name_to_chemical_id:
                dict_chemical_name_to_chemical_id[synonym] = set()
            dict_chemical_name_to_chemical_id[synonym].add(identifier)


# file from mapping between drug response and chemical
file_rela = open('drug/chemical_drug.tsv', 'w', encoding='utf-8')
csv_rela = csv.writer(file_rela, delimiter='\t')
header_rela = ['chemical_id', 'clinvar_id', 'resource']
csv_rela.writerow(header_rela)

# list of splitibale information
# susceptibility=allergy, susceptibility=
list_of_splitable_information = [' response', ' hypersensitivity', ' resistance',
                                 ' susceptibility', ', poor metabolism of']  # poor metabolism of


def split_name_to_to_only_name(name):
    """
    split with different words to get the drug as return
    :param name:
    :return:
    """
    for element in list_of_splitable_information:
        name = name.split(element)[0]
    return name


def load_all_drug_response_and_finish_the_files():
    """
    Load all drug response an try to map it to chemical. Then write into TSV file.
    :return:
    """
    cypher_file = open('drug/cypher_drug.cypher', 'w', encoding='utf-8')

    query_start = '''Match (c:Chemical{identifier:line.chemical_id}), (t:trait_DrugResponse_ClinVar{identifier:line.clinvar_id}) Set c.clinvar='yes', c.resource=split(line.resource,"|") Create (c)-[:equal_to_clinvar_drug]->(t) '''
    query_start = pharmebinetutils.get_query_import(path_of_directory,
                                                    'mapping_and_merging_into_hetionet/clinvar/drug/chemical_drug.tsv',
                                                    query_start)
    cypher_file.write(query_start)

    query = "MATCH (n:trait_DrugResponse_ClinVar) RETURN n"
    counter = 0
    all = 0
    counter_disease = 0
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        all += 1
        identifier = node['identifier']
        name = node['name'].lower() if 'name' in node else ''
        name_short = split_name_to_to_only_name(name)
        if name_short in dict_chemical_name_to_chemical_id:
            counter += 1
            for chemical_id in dict_chemical_name_to_chemical_id[name_short]:
                resource = dict_chemical_id_to_resource[chemical_id]
                resource.add('ClinVar')
                resource = '|'.join(resource)
                csv_rela.writerow([chemical_id, identifier, resource])

    print('number of mapped drug response:', counter)
    print('number of all:', all)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ClinVar')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all chemicals from database')

    load_chemicals_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all kind of properties of the drug response')

    load_all_drug_response_and_finish_the_files()
    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
