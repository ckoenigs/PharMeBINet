import csv
import sys
import datetime

sys.path.append("../..")
import pharmebinetutils
import create_connection_to_databases

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


def create_connection_with_neo4j_and_mysql():
    """
    create a connection with neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


# dictionary name to ids
dict_name_to_id = {}
# dictionary meddra to ids
dict_meddra_to_id = {}


def integrate_information_into_dict(dict_node_id_to_resource, dict_node_id_to_xrefs):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:SideEffect) RETURN n.identifier, n.name, n.synonyms, n.resource, n.xrefs'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, resource, xrefs] = record.values()
        dict_node_id_to_resource[identifier] = resource
        dict_node_id_to_xrefs[identifier] = xrefs if xrefs else []
        name = name.lower() if name else ''
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_id,name,identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_id,synonym,identifier)

        for xref in dict_node_id_to_xrefs[identifier]:
            if xref.startswith('MedDRA'):
                meddra_id=xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_meddra_to_id,meddra_id,identifier)


    print('number of Side effects in database', len(dict_node_id_to_resource))


def prepare_query(file_name, file_name_new_mapped, file_name_new, db_label, adrecs_label, db_id, adrecs_id_internal, adrecs_id):
    """
    prepare query for integration
    :param file_name:string
    :param db_label: string
    :param adrecs_label: string
    :param db_id: string
    :param adrecs_id_internal:string
    :param adrecs_id: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = ''' MATCH (n:%s{identifier:line.%s}), (g:%s{%s:line.%s, adrecs_id:line.other_adrecs_id}) Set n.resource=split(line.resource,"|"), n.adrecs='yes', n.xrefs=split(line.xrefs,"|") Create (n)-[:equal_adrecs_%s{how_mapped:line.how_mapped}]->(g)'''
    query = query % (db_label, db_id, adrecs_label, adrecs_id_internal, adrecs_id, db_label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/{director}/{file_name}', query)
    cypher_file.write(query)

    query_start = f' Create (n:SideEffect{{identifier:line.umls_id, name:line.name, synonyms:split(line.synonyms,"|"), source:"UMLS via ADReCS", resource:["ADReCS"], license:"", url:"http://bioinf.xmu.edu.cn/ADReCS/adrSummary.jsp?adr_id="+line.id, xrefs:split(line.xrefs,"|")}})  '
    query_start = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/{director}/{file_name_new}',
                                                    query_start)
    cypher_file.write(query_start)

    query_start = f' Match (g:{adrecs_label}{{{adrecs_id_internal}:line.{adrecs_id}, adrecs_id:line.other_adrecs_id}}), (n:SideEffect{{identifier:line.umls_id}})  Create (n)<-[:equal_to_adrecs_adr]-(g)'
    query_start = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/{director}/{file_name_new_mapped}',
                                                    query_start)
    cypher_file.write(query_start)


def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id, other_adrecs_id, csv_mapping, how_mapped,
                xref_disease):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    xref_disease.append("ADReCS:" + other_adrecs_id)
    xref_disease = go_through_xrefs_and_change_if_needed_source_name(xref_disease, 'disease')
    xref_string = '|'.join(xref_disease)
    csv_mapping.writerow([identifier_db, identifier_act_id, other_adrecs_id,
                          pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier_db], 'ADReCS'),
                          how_mapped, xref_string])


def get_all_adrecs_and_map(db_label, dict_node_id_to_resource, dict_node_id_to_xrefs):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    # mapping file
    file_name = db_label.lower() + '/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'act_id', 'other_adrecs_id', 'resource', 'how_mapped', 'xrefs'])

    # file for new generated SE (without ADReCS node connection)
    file_name_new = db_label.lower() + '/new.tsv'
    new_file = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(new_file, delimiter='\t')
    csv_new.writerow(['umls_id', 'name', 'synonyms', 'id', 'xrefs'])

    # for connection between new generated node and the different ADReCS adr nodes (multiple mapping
    file_name_new_mapped = db_label.lower() + '/new_map.tsv'
    new_file_mapped = open(file_name_new_mapped, 'w', encoding='utf-8')
    csv_new_mapped = csv.writer(new_file_mapped, delimiter='\t')
    csv_new_mapped.writerow(['umls_id', 'act_id', 'other_adrecs_id'])

    prepare_query(file_name, file_name_new_mapped, file_name_new, db_label, 'ADReCS_ADR', 'db_id', 'id', 'act_id')

    # get data
    query = '''MATCH (n:ADReCS_ADR) RETURN n'''
    results = g.run(query)

    dict_new_node_id_to_properties = {}

    # counter mapping
    counter_mapping = 0
    counter_not_mapped = 0
    for record in results:
        node = record.data()['n']
        # rs or a name
        name = node['term'].lower()
        identifier = node['id']
        adrecs_id = node['adrecs_id']
        meddra_id= node['meddra_code']
        if name in dict_name_to_id:
            counter_mapping += 1
            for other_identifier in dict_name_to_id[name]:
                add_to_file(dict_node_id_to_resource, other_identifier, identifier, adrecs_id, csv_mapping,
                            'name_mapping', dict_node_id_to_xrefs[other_identifier])


        else:
            # print(' not in database :O')
            # print(identifier, name)
            cur = con.cursor()
            query = ("Select  Distinct CUI  From MRCONSO Where  STR= '%s';")
            change_name = name.replace('\'', '')
            query = query % (change_name)
            rows_counter = cur.execute(query)
            mapped_cuis = set()
            new_cuis = set()
            mapped=False
            if rows_counter > 0:
                for (cui,) in cur:
                    if cui in dict_node_id_to_resource:
                        mapped_cuis.add(cui)
                    else:
                        new_cuis.add(cui)
                if len(mapped_cuis) > 0:
                    mapped=True
                    counter_mapping += 1
                    for other_identifier in mapped_cuis:
                        add_to_file(dict_node_id_to_resource, other_identifier, identifier, adrecs_id, csv_mapping,
                                    'cui_mapping', dict_node_id_to_xrefs[other_identifier])

            if mapped:
                continue

            if meddra_id in dict_meddra_to_id:
                counter_mapping += 1
                mapped=True
                for other_identifier in dict_meddra_to_id[meddra_id]:
                    add_to_file(dict_node_id_to_resource, other_identifier, identifier, adrecs_id, csv_mapping,
                                'meddra_mapping', dict_node_id_to_xrefs[other_identifier])
            if mapped:
                continue

            if len(new_cuis)>0:
                counter_not_mapped += 1
                umls_cui = new_cuis.pop()
                csv_new_mapped.writerow([umls_cui, identifier, adrecs_id])
                synonyms = node['synonyms'] if 'synonyms' in node else []
                if umls_cui in dict_new_node_id_to_properties:
                    dict_new_node_id_to_properties[umls_cui]['synonyms'] = dict_new_node_id_to_properties[umls_cui][
                        'synonyms'].union(synonyms)
                    dict_new_node_id_to_properties[umls_cui]['synonyms'].add(node['term'])
                    dict_new_node_id_to_properties[umls_cui]['xrefs'].add("ADReCS:" + adrecs_id)
                else:
                    dict_new_node_id_to_properties[umls_cui] = {'name': node['term'], 'id': identifier,
                                                                    'xrefs': set(["ADReCS:" + adrecs_id]),
                                                                    'synonyms': set(synonyms)}

            else:
                # print('no connection')
                counter_not_mapped += 1

    for umls_cui, properties in dict_new_node_id_to_properties.items():
        csv_new.writerow([umls_cui, properties['name'], '|'.join(properties['synonyms']), properties['id'],
                          '|'.join(properties['xrefs'])])
    print('mapped:', counter_mapping)
    print('number of not mapped adr:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director, dict_node_id_to_xrefs
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        director = sys.argv[2]
    else:
        sys.exit('need a path adrecs and directory')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')

    # dict node id to resource
    dict_node_id_to_resource = {}
    # dict node id to xrefs
    dict_node_id_to_xrefs = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all SE from database')

    integrate_information_into_dict(dict_node_id_to_resource, dict_node_id_to_xrefs)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_adrecs_and_map('SideEffect', dict_node_id_to_resource, dict_node_id_to_xrefs)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
