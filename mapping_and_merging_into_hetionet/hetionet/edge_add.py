import datetime
import csv
import sys

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
    graph_database = driver.session()


def load_pharmebinet_pharmebinet_node_in(csv_file, pharmebinet_node_label1, pharmebinet_node_label2, hetionet_label_1,
                                         hetionet_label_2, relationship):
    """
    load in all pathways from pharmebinet in a dictionary
    """
    query = '''MATCH (p:%s)-[]-(r:%s)-[v:%s]->(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, v'''
    query = query % (pharmebinet_node_label1, hetionet_label_1, relationship, hetionet_label_2, pharmebinet_node_label2)
    print(query)
    results = graph_database.run(query)
    counter = 0
    dict_pair_to_edges = {}
    # for id1, id2, order, stoichiometry, in results:
    for record in results:
        [node_id1, node_id2, v] = record.values()
        if not (node_id1, node_id2) in dict_pair_to_edges:
            dict_pair_to_edges[(node_id1, node_id2)] = []
        dict_pair_to_edges[(node_id1, node_id2)].append(dict(v))

    for (node1, node2), rela_infos in dict_pair_to_edges.items():
        if len(rela_infos) > 1:
            dict_all={}
            dict_all['id1']=node1
            dict_all['id2']=node2
            for rela_info in rela_infos:
                for key, value in rela_info.items():
                    if not key in dict_all:
                        dict_all[key] = value
                    else:
                        if value != dict_all[key]:
                            print('ohno')
        else:
            dict_all=rela_infos[0]
            dict_all['id1']=node1
            dict_all['id2']=node2
        for key, value in dict_all.items():
            if type(value) in [list, set]:
                dict_all[key]='|'.join(value)
        csv_file.writerow(dict_all)

    print(f'number of {pharmebinet_node_label1}-{pharmebinet_node_label2} relationships in pharmebinet:' + str(
        len(dict_pair_to_edges)))


def check_relationships_and_generate_file(pharmebinet_label1, pharmebinet_label2, hetionet_label1, hetionet_label2,
                                          rela_hetionet, rela_type, directory):
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + f'/{pharmebinet_label1}_{pharmebinet_label2}_{rela_type}.tsv'

    query = '''MATCH (:%s)-[p:%s]->(:%s) WITH DISTINCT keys(p) AS keys
                       UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
                       RETURN allfields as l;'''
    query = query % (hetionet_label1, rela_hetionet, hetionet_label2)
    result = graph_database.run(query)
    if rela_type!='ASSOCIATES_GaD':
        query = f'Match (a:{pharmebinet_label1}{{identifier:line.id1}}), (b:{pharmebinet_label2}{{identifier:line.id2}}) Create (a)-[:{rela_type}{{%s , hetionet:"yes", resource:["Hetionet"]}}]->(b)'
    else:
        query = f'Match (a:{pharmebinet_label1}{{identifier:line.id1}}), (b:{pharmebinet_label2}{{identifier:line.id2}}) Create (b)-[:{rela_type}{{%s , hetionet:"yes", resource:["Hetionet"]}}]->(a)'
    list_prop = []
    header = ['id1', 'id2']
    for record in result:
        prop = record.data()['l']
        if prop not in ['source','sources']:
            list_prop.append(f'{prop}:line.{prop}')
        elif prop == 'source':
            list_prop.append(f'{prop}:line.{prop}+" via Hetionet"')
        else:
            list_prop.append(f'{prop}:split(line.{prop},"|"), source:replace(line.{prop},"|",",") +" via Hetionet"')


        header.append(prop)

    query = query % (', '.join(list_prop))
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hetionet/{file_name}',
                                              query)
    cypher_file.write(query)

    file_rela = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.DictWriter(file_rela, delimiter='\t', lineterminator='\n', fieldnames=header)
    csv_mapped.writeheader()

    load_pharmebinet_pharmebinet_node_in(csv_mapped, pharmebinet_label1, pharmebinet_label2, hetionet_label1,
                                         hetionet_label2, rela_hetionet)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


def main():
    global path_of_directory, license
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path and license hetionet edge')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: pharmebinet label 1;  1: hetionet label 1; 2: hetionet label 2; 3: PharMeBINet label 2; 4: rela in hetionet;
    # 5: rela in PharMeBINet
    list_of_combinations = [
        ['Disease', 'Disease_hetionet', 'Symptom_hetionet', 'Symptom', 'PRESENTS_DpS', 'PRESENTS_DpS'],
        ['Disease', 'Disease_hetionet', 'Gene_hetionet', 'Gene', 'ASSOCIATES_DaG', 'ASSOCIATES_GaD'],
        ['Disease', 'Disease_hetionet', 'Gene_hetionet', 'Gene', 'UPREGULATES_DuG', 'UPREGULATES_DuG'],
        ['Disease', 'Disease_hetionet', 'Gene_hetionet', 'Gene', 'DOWNREGULATES_DdG', 'DOWNREGULATES_DdG'],
        ['Disease', 'Disease_hetionet', 'Anatomy_hetionet', 'Anatomy', 'LOCALIZES_DlA', 'LOCALIZES_DlA'],
        ['Disease', 'Disease_hetionet', 'Disease_hetionet', 'Disease', 'RESEMBLES_DrD', 'RESEMBLES_DrD'],
        ['Anatomy', 'Anatomy_hetionet', 'Gene_hetionet', 'Gene', 'EXPRESSES_AeG', 'EXPRESSES_AeG'],
        ['Anatomy', 'Anatomy_hetionet', 'Gene_hetionet', 'Gene', 'DOWNREGULATES_AdG', 'DOWNREGULATES_AdG'],
        ['Anatomy', 'Anatomy_hetionet', 'Gene_hetionet', 'Gene', 'UPREGULATES_AuG', 'UPREGULATES_AuG'],
        ['Gene', 'Gene_hetionet', 'Gene_hetionet', 'Gene', 'INTERACTS_GiG', 'INTERACTS_GiG'],
        ['Gene', 'Gene_hetionet', 'Gene_hetionet', 'Gene', 'COVARIES_GcG', 'COVARIES_GcG'],
        ['Gene', 'Gene_hetionet', 'Gene_hetionet', 'Gene', 'REGULATES_GrG', 'REGULATES_GrG'],

    ]

    directory = 'edges'
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding="utf-8")

    for list_element in list_of_combinations:
        pharmebinet_label1 = list_element[0]
        hetionet_label1 = list_element[1]
        hetionet_label2 = list_element[2]
        pharmebinet_label2 = list_element[3]
        rela_hetionet = list_element[4]
        rela_type = list_element[5]
        check_relationships_and_generate_file(pharmebinet_label1, pharmebinet_label2, hetionet_label1, hetionet_label2,
                                              rela_hetionet, rela_type, directory)
    cypher_file.close()
    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
