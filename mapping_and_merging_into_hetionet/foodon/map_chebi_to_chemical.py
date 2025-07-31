import csv
import sys
import datetime
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary name to ids
dict_name_to_id = defaultdict(set)

# dictionary synonyms to ids
dict_synonyms_to_id = defaultdict(set)

# dictionary synonyms to ids
dict_chebi_to_id = defaultdict(set)


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.synonyms, n.resource, n.xrefs'''
    results = g.run(query)

    for identifier, name, synonyms, resource, xrefs, in results:
        dict_node_id_to_resource[identifier] = resource

        name = name.lower()
        dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_synonyms_to_id[synonym].add(identifier)

        # if xrefs:
        #     for xref in xrefs:
        #         if xref.startswith('ChEBI'):
        #             dict_chebi_to_id[xref.split(':')[1]].add(identifier)
        #             if len(xref.split(':'))>2:
        #                 print('ohno', xref)

    query = '''Match p=(n:Chemical)-[r]-(m:Chemical_ChebiOntology) Return m.id, n.identifier'''
    for chebi_id, chemical_id, in g.run(query):
        dict_chebi_to_id[chebi_id.split(':')[1]].add(chemical_id)

    print('number of Chemical in database', len(dict_node_id_to_resource))


def prepare_query(file_name):
    """
    prepare query fro integration
    :param file_name:string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = '''MATCH (n:Chemical{identifier:line.db_id}), (g:FoodOn_Food{id:line.node_id}) Set n.resource=split(line.resource,"|"), n.foodon='yes' Create (n)-[:equal_foodon_chemical{how_mapped:line.how_mapped}]->(g)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/foodon/{file_name}',
                                              query)
    cypher_file.write(query)


def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id, csv_mapping, how_mapped):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    csv_mapping.writerow(
        [identifier_db, identifier_act_id,
         pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier_db], "FoodOn"),
         how_mapped])


# dictionary manual mapping
dict_manual_chebi_mapping = {
    "CHEBI:23652": "D003912",
    "CHEBI:25863": "C066957",
    "CHEBI:28436": "C017185",
    "CHEBI:31344": "DB15648",
    'CHEBI:27007': 'D014001',
    "CHEBI:30363": "D002073",
    "CHEBI:48154": "C405951"
}


def get_all_foodon_and_map(dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = 'output/mapping_chemical.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'node_id', 'resource', 'how_mapped'])

    prepare_query(file_name)

    # get data
    query = '''MATCH (n:FoodOn_Food)  Where split(n.id,':')[0] ='CHEBI'  RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    for record in results:
        node = record.data()['n']
        # rs or a name
        identifier = node['id']
        only_number_id = identifier.split(':')[1]

        names = set(node['names']) if 'names' in node else set()

        is_mapped = False

        if only_number_id in dict_chebi_to_id:
            is_mapped = True
            counter_mapping += 1
            for chemical_id in dict_chebi_to_id[only_number_id]:
                add_to_file(dict_node_id_to_resource, chemical_id, identifier, csv_mapping, 'chebi')

        if is_mapped:
            continue

        if identifier in dict_manual_chebi_mapping:
            is_mapped = True
            counter_mapping += 1
            add_to_file(dict_node_id_to_resource, dict_manual_chebi_mapping[identifier], identifier, csv_mapping,
                        'manual')

        if is_mapped:
            continue

        # if names:
        #     for name in names:
        #         name = name.lower()
        #         if name in dict_name_to_id:
        #             is_mapped = True
        #             counter_mapping += 1
        #             for drugbank_id in dict_name_to_id[name]:
        #                 add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'name_mapping')
        #
        # if is_mapped:
        #     continue

        if names:
            for name in names:
                name = name.lower()
                if name in dict_synonyms_to_id:
                    is_mapped = True
                    counter_mapping += 1
                    for drugbank_id in dict_synonyms_to_id[name]:
                        if name +'s' in dict_name_to_id:
                            if drugbank_id in dict_name_to_id[name+'s']:
                                print(':)')
                                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'synonyms_mapping')

        if not is_mapped:
            counter_not_mapped += 1
            print(' not in database :O')
            print(identifier, names)
    print('mapped:', counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path foodon')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')

    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all drugs from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_foodon_and_map(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
