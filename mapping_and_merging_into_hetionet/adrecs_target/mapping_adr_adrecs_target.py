import csv
import sys
import datetime


sys.path.append("../..")
import pharmebinetutils
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

# dictionary name to ids
dict_name_to_id={}

def integrate_information_into_dict(dict_node_id_to_resource):
    """
    get all node ids from the database
    :return:
    """
    query = '''MATCH (n:SideEffect) RETURN n.identifier, n.name, n.synonyms, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, resource]= record.values()
        dict_node_id_to_resource[identifier] = resource

        name = name.lower()
        if name not in dict_name_to_id:
            dict_name_to_id[name] = set()
        dict_name_to_id[name].add(identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                if synonym not in dict_name_to_id:
                    dict_name_to_id[synonym] = set()
                dict_name_to_id[synonym].add(identifier)


    print('number of Side effects in database', len(dict_node_id_to_resource))


def prepare_query(file_name, file_name_new, db_label, adrecs_label, db_id,adrecs_id_internal, adrecs_id):
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
    query = ''' MATCH (n:%s{identifier:line.%s}), (g:%s{%s:line.%s}) Set n.resource=split(line.resource,"|"), n.adrecs_target='yes' Create (n)-[:equal_adrecs_target_%s{how_mapped:line.how_mapped}]->(g)'''
    query = query % ( db_label, db_id,adrecs_label, adrecs_id_internal, adrecs_id, db_label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/{director}/{file_name}', query)
    cypher_file.write(query)

    query= f' Match (g:{adrecs_label}{{{adrecs_id_internal}:line.{adrecs_id}}})  Merge (n:SideEffect{{identifier:line.umls_id}}) On Create Set  n.name=g.ADR_TERM, n.source="UMLS via ADReCS-Target", n.adrecs_target="yes", n.resource=["ADReCS-Target"], n.license="", n.url="" Create (n)<-[:equal_to_adrecs_target_adr]-(g)'

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/{director}/{file_name_new}', query)
    cypher_file.write(query)

def add_to_file(dict_node_id_to_resource, identifier_db, identifier_act_id,csv_mapping, how_mapped):
    """
    add resource and write mapping pair in tsv file
    :param dict_node_id_to_resource: dictionary
    :param identifier_db: string
    :param identifier_act_id: string
    :param csv_mapping: csv writer
    :return:
    """
    resource = set(dict_node_id_to_resource[identifier_db])
    resource.add('ADReCS-Target')
    resource = sorted(resource)
    csv_mapping.writerow([identifier_db, identifier_act_id, '|'.join(resource), how_mapped])

def get_all_adrecs_target_and_map(db_label,  dict_node_id_to_resource):
    """
    prepare files and write information into files
    :return:
    """

    # prepare files
    file_name = db_label.lower() + '/mapping.tsv'
    mapping_file = open(file_name, 'w', encoding='utf-8')
    csv_mapping = csv.writer(mapping_file, delimiter='\t')
    csv_mapping.writerow(['db_id', 'act_id', 'resource', 'how_mapped'])


    file_name_new = db_label.lower() + '/new.tsv'
    new_file = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(new_file, delimiter='\t')
    csv_new.writerow(['umls_id', 'act_id'])

    prepare_query(file_name, file_name_new, db_label, 'adr_ADReCSTarget','db_id','identifier','act_id')

    # get data
    query = '''MATCH (n:adr_ADReCSTarget) RETURN n'''
    results = g.run(query)

    # counter mapping
    counter_mapping=0
    counter_not_mapped=0
    for record in results:
        node=record.data()['n']
        #rs or a name
        name = node['ADR_TERM'].lower()
        # remove the inclusive and exclusive information from name
        name= name.split(' (incl')[0].split('  (excl')[0]
        identifier= node['identifier']
        if name  in dict_name_to_id:
            counter_mapping+=1
            for other_identifier in dict_name_to_id[name]:
                add_to_file(dict_node_id_to_resource, other_identifier, identifier, csv_mapping, 'name_mapping')

        else:
            # print(' not in database :O')
            # print(identifier, name)
            cur = con.cursor()
            query = ("Select  Distinct CUI  From MRCONSO Where  STR= '%s';")
            change_name=name.replace('\'','')
            query = query % (change_name)
            rows_counter = cur.execute(query)
            mapped_cuis=set()
            new_cuis=set()
            if rows_counter > 0:
                for (cui,) in cur:
                    if cui in dict_node_id_to_resource:
                        mapped_cuis.add(cui)
                    else:
                        new_cuis.add(cui)
                if len(mapped_cuis)>0:
                    print('mapped')
                    counter_mapping+=1
                    for other_identifier in mapped_cuis:
                        add_to_file(dict_node_id_to_resource, other_identifier, identifier, csv_mapping, 'cui_mapping')
                else:
                    counter_not_mapped+=1
                    umls_cui=new_cuis.pop()
                    csv_new.writerow([umls_cui,identifier])

            else:
                # print('no connection')
                counter_not_mapped+=1
    print('mapped:',counter_mapping)
    print('number of not mapped drugs:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        director = sys.argv[2]
    else:
        sys.exit('need a path adrecs-target and directory')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare for each label the files')


    # dict node id to resource
    dict_node_id_to_resource = {}

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all SE from database')

    integrate_information_into_dict(dict_node_id_to_resource)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare file and write information of mapping in it')

    get_all_adrecs_target_and_map('SideEffect',dict_node_id_to_resource)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
