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

# dictionary chebi to ids
dict_chebi_to_id = defaultdict(set)

# dictionary inchikey to ids
dict_inchikey_to_id = defaultdict(set)


def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.synonyms, n.resource, n.xrefs, n.inchikey'''
    results = g.run(query)

    for identifier, name, synonyms, resource, xrefs, inchikey, in results:
        xrefs = set(xrefs) if xrefs else set()
        dict_node_id_to_resource[identifier] = [resource,xrefs]

        name = name.lower()
        dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_synonyms_to_id[synonym].add(identifier)

        if inchikey:
            dict_inchikey_to_id[inchikey].add(identifier)

        for xref in xrefs:
            if xref.startswith('ChEBI'):
                dict_chebi_to_id[xref.split(':')[1]].add(identifier)
                if len(xref.split(':'))>2:
                    print('ohno', xref)

    print('number of Chemical in database', len(dict_node_id_to_resource))


def prepare_query(file_name):
    """
    prepare query fro integration
    :param file_name:string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = '''MATCH (n:Chemical{identifier:line.db_id}), (g:Chemical_ChebiOntology{id:line.node_id}) Set n.resource=split(line.resource,"|"), n.xrefs=split(line.xrefs,"|"), n.chebi='yes' Create (n)-[:equal_chebi_chemical{how_mapped:line.how_mapped}]->(g)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/chebi/{file_name}',
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
    dict_node_id_to_resource[identifier_db][1].add(identifier_act_id)
    csv_mapping.writerow(
        [identifier_db, identifier_act_id,
         pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier_db][0], "ChEBI"),
         how_mapped, '|'.join(dict_node_id_to_resource[identifier_db][1])])


def get_all_chebi_and_map(dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = 'output/mapping_chemical.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8', newline='')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'node_id', 'resource', 'how_mapped', 'xrefs'])

    prepare_query(file_name)

    # get data
    query = '''MATCH (n:Chemical_ChebiOntology)   RETURN n.id, n.name, n.synonyms, n.property_values, n.xrefs'''
    results = g.run(query)

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    for identifier, name, synonyms, property_values, xrefs, in results:
        only_number_id=identifier.split(':')[1]

        name = name.lower()

        is_mapped=False

        if property_values:
            dict_property_to_value={}
            for value in property_values:
                value = value.replace('" xsd:string','')
                key_value_pair=value.split(' "')
                dict_property_to_value[key_value_pair[0].replace('http://purl.obolibrary.org/obo/chebi/','')]=key_value_pair[1]
            if 'inchikey' in dict_property_to_value:
                if dict_property_to_value['inchikey'] in dict_inchikey_to_id:
                    is_mapped=True
                    counter_mapping += 1
                    for chemical_id in dict_inchikey_to_id[dict_property_to_value['inchikey']]:
                        add_to_file(dict_node_id_to_resource, chemical_id, identifier, csv_mapping, 'inchikey')

        if is_mapped:
            continue

        if xrefs:
            for xref in xrefs:
                if xref.startswith('DrugBank:'):
                    if xref in dict_node_id_to_resource:
                        is_mapped=True
                        counter_mapping+=1
                        add_to_file(dict_node_id_to_resource, xref, identifier, csv_mapping, 'drugbank_xref')

        if is_mapped:
            continue

        if name in dict_name_to_id:
            is_mapped=True
            counter_mapping += 1
            for drugbank_id in dict_name_to_id[name]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'name_mapping')


        if is_mapped:
            continue

        if only_number_id in dict_chebi_to_id:
            is_mapped=True
            counter_mapping+=1
            for chemical_id in dict_chebi_to_id[only_number_id]:
                add_to_file(dict_node_id_to_resource, chemical_id, identifier, csv_mapping, 'chebi')

        if is_mapped:
            continue

        if name in dict_synonyms_to_id:
            is_mapped=True
            counter_mapping += 1
            for drugbank_id in dict_synonyms_to_id[name]:
                add_to_file(dict_node_id_to_resource, drugbank_id, identifier, csv_mapping, 'synonyms_mapping')

        if not is_mapped:
            counter_not_mapped += 1
            print(' not in database :O')
            print(identifier, name)

    print('mapped:', counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path chebi')

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

    get_all_chebi_and_map(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
