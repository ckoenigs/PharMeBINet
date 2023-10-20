import sys
import datetime, time
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


def generate_cypher_queries_and_tsv_files():
    """
    generate cypher queries and tsv files
    :return: csv writer for mapping and new
    """
    set_header_for_files = ['efo_id', 'pharmebinet_id', 'resource', 'how_mapped']
    # tsv file for mapping disease
    file_name_mapped = 'output/disease_mapped.tsv'
    file_disease_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_disease_mapped = csv.writer(file_disease_mapped, delimiter='\t')
    csv_disease_mapped.writerow(set_header_for_files)

    # cypher file for mapping and integration
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

    query_match = '''Match (s:Disease{identifier:line.pharmebinet_id }) , (n:efo{id:line.efo_id}) Set s.efo='yes',  s.resource=split(line.resource,"|")  Create (s)-[:equal_to_efo_diseases{how_mapped:line.how_mapped}]->(n)'''
    query_match = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/efo/{file_name_mapped}',
                                                    query_match)
    cypher_file.write(query_match)

    return csv_disease_mapped


## dictionary of disease id to resource
dict_of_pharmebinet_to_resource = {}

# dictionary name_to_disease
dict_name_to_disease_ids = {}

# dictionary efo id to disease ids
dict_efo_id_to_disease_ids = {}

# dictionary orphanet id to disease ids
dict_orphanet_id_to_disease_ids = {}


def get_all_diseases_and_add_to_dict():
    """
    Get al disease from pharmebinet and put this information into a dictionary
    :return:
    """
    query = '''MATCH (n:Disease) RETURN n  '''
    results = g.run(query)

    # add all diseases to dictioanry
    for record in results:
        result = record.data()['n']
        identifier = result['identifier']

        dict_of_pharmebinet_to_resource[identifier] = result['resource']

        name = result['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_disease_ids, name, identifier)

        xrefs = result['xrefs'] if 'xrefs' in result else []
        for xref in xrefs:
            if xref.startswith('EFO:'):
                pharmebinetutils.add_entry_to_dict_to_set(dict_efo_id_to_disease_ids, xref, identifier)
            elif xref.startswith('Orphanet'):
                pharmebinetutils.add_entry_to_dict_to_set(dict_orphanet_id_to_disease_ids, xref, identifier)



def map_efo_disease_and_to_pharmebinet(csv_mapped):
    """
    Load first the first efo disease nod an map this. and then for each lower level map the node to disease.
    :return:
    """

    count_mapped = 0
    counter = 0

    file=open('output/not_mapped.tsv','w',encoding='utf-8')
    csv_not_mapped=csv.writer(file,delimiter='\t')
    csv_not_mapped.writerow(['id'])

    # efo EFO:0000408 id disease
    query = 'Match (m:efo{id:"EFO:0000408"} )  RETURN m.id, m.names, m.xrefs'
    results = g.run(query)
    for record in results:
        counter += 1
        [node_id, names, xrefs] = record.values()
        if xrefs is not None:
            for xref in xrefs:
                if xref.startswith('MONDO:'):
                    if xref in dict_of_pharmebinet_to_resource:
                        count_mapped += 1
                        csv_mapped.writerow([node_id, xref, pharmebinetutils.resource_add_and_prepare(
                            dict_of_pharmebinet_to_resource[xref], 'EFO'), 'xref'])

    query_nodes = 'MATCH (n:efo)-[:is_a]->(m:efo ) Where n.is_obsolete is NULL and m.id in ["%s"] RETURN n.id, n.names, n.xrefs, n.synonyms'

    dict_nodes = {}

    level = 1
    dict_level_to_ids = {level: set(['EFO:0000408'])}

    while level in dict_level_to_ids:
        new_query = query_nodes
        new_query = new_query % ('","'.join(dict_level_to_ids[level]))
        results = g.run(new_query)
        set_ids_of_level = set()
        for record in results:
            [node_id, names, xrefs, synonyms] = record.values()
            # EFO:0005932 is animal disease
            if node_id in dict_nodes or node_id=='EFO:0005932':
                continue
            counter += 1
            set_ids_of_level.add(node_id)
            dict_nodes[node_id] = (names, xrefs)

            # found one
            found_one = False

            if node_id.startswith('MONDO:'):
                if node_id in dict_of_pharmebinet_to_resource:
                    count_mapped += 1
                    found_one = True
                    csv_mapped.writerow([node_id, node_id, pharmebinetutils.resource_add_and_prepare(
                        dict_of_pharmebinet_to_resource[node_id], 'EFO'), 'id'])

            if found_one:
                continue

            if xrefs is not None:
                for xref in xrefs:
                    if xref.startswith('MONDO:'):
                        if xref in dict_of_pharmebinet_to_resource:
                            found_one = True
                            csv_mapped.writerow([node_id, xref, pharmebinetutils.resource_add_and_prepare(
                                dict_of_pharmebinet_to_resource[xref], 'EFO'), 'xref'])

            if found_one:
                count_mapped += 1
                continue

            if node_id.startswith('Orphanet:'):
                if node_id in dict_orphanet_id_to_disease_ids:
                    for disease_id in dict_orphanet_id_to_disease_ids[node_id]:
                        found_one = True
                        csv_mapped.writerow([node_id, disease_id, pharmebinetutils.resource_add_and_prepare(
                            dict_of_pharmebinet_to_resource[disease_id], 'EFO'), 'Orphanet'])

            if found_one:
                count_mapped += 1
                continue

            for name in names:
                name = name.lower()
                if name in dict_name_to_disease_ids:
                    found_one = True
                    for mondo_id in dict_name_to_disease_ids[name]:
                        csv_mapped.writerow([node_id, mondo_id, pharmebinetutils.resource_add_and_prepare(
                            dict_of_pharmebinet_to_resource[mondo_id], 'EFO'), 'name'])

            if found_one:
                count_mapped += 1
                continue

            csv_not_mapped.writerow([node_id])

        if len(set_ids_of_level) == 0:
            break
        level += 1
        dict_level_to_ids[level] = set_ids_of_level

    print('number of mapped nodes:', count_mapped)
    print('number of disease', counter)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate dictionary from diseases of pharmebinet')

    get_all_diseases_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate files and cypher queries')

    csv_mapped = generate_cypher_queries_and_tsv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('map hpo diseases to mesh or umls cui and integrated them into pharmebinet')

    map_efo_disease_and_to_pharmebinet(csv_mapped)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
