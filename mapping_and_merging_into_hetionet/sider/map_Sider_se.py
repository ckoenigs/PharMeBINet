# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 15:16:45 2019

@author: Cassandra
"""
import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# list of all side effect ids which are in hetionet
list_side_effect_in_hetionet = []

# dictionary with all side effects from hetionet and the new ones from sider
#  with id as key and as value a class SideEffect
dict_all_side_effect = {}

# create csv for sider se effects which includes the already existing nodes which need to be updated and the new generated nodes
file_update_node = open('output/se_update.csv', 'w')
header = ["name", "identifier", "meddraType", "conceptName"]
csv_writer_update = csv.DictWriter(file_update_node, delimiter='\t', fieldnames=header)
csv_writer_update.writeheader()

file_new_node = open('output/se_new.csv', 'w')
csv_writer_new = csv.DictWriter(file_new_node, delimiter='\t', fieldnames=header)
csv_writer_new.writeheader()

'''
load in all side effects from hetionet
has properties:
    license
    identifier
    name
    source
    url
'''


def load_side_effects_from_hetionet_in_dict():
    query = '''MATCH (n:SideEffect) RETURN n '''
    results = g.run(query)
    for result, in results:
        list_side_effect_in_hetionet.append(result['identifier'])
        sideEffect = dict(result)
        dict_all_side_effect[result['identifier']] = sideEffect
    print('size of side effects before the sider is add:' + str(len(list_side_effect_in_hetionet)))


'''
load all new and old information for side effects in
meddraType: string (PT or LLT)
conceptName: string
umlsIDmeddra: string (UMLS CUI for MedDRA ID)
name: string
umls_concept_id: string (UMLS CUI for label)
'''


def load_sider_in_dict():
    query = '''MATCH (n:se_Sider) RETURN n '''
    results = g.run(query)
    k = 0
    counter_new = 0
    for result, in results:
        k += 1
        meddraType = result['meddraType']
        conceptName = result['conceptName']
        umlsIDmeddra = result['umlsIDmeddra']
        name = result['name']

        dict_info = {"name": name, "identifier": umlsIDmeddra, "meddraType": meddraType, "conceptName": conceptName}
        if not umlsIDmeddra in dict_all_side_effect:
            sideEffect = ('CC BY-NC-SA 4.0', umlsIDmeddra, name, 'UMLS via SIDER 4.1',
                          'http://identifiers.org/umls/' + umlsIDmeddra)
            csv_writer_new.writerow(dict_info)
            counter_new += 1
        else:
            csv_writer_update.writerow(dict_info)

    print('size of side effects after the sider is add:' + str(len(list_side_effect_in_hetionet) + counter_new))


'''
Generate cypher file for side effect nodes
'''


def generate_cypher_file():
    cypher_file = open('output/cypher.cypher', 'w')
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/sider/output/%s.csv" As line FIELDTERMINATOR '\\t' '''
    query_new = ''
    query_update = ''
    for head in header:
        query_new += head + ':line.' + head + ', '
        if not head == 'identifier':
            query_update += 'n.' + head + '=line.' + head + ', '
    query_update = query_start + ' Match (b:se_Sider{umlsIDmeddra:line.identifier}), (n:SideEffect{identifier:line.identifier}) Set ' + query_update + ' n.sider="yes", n.resource=n.resource+"SIDER" Create (n)-[:equal_to_SE]->(b);\n'
    query_update = query_update % ('se_update')
    cypher_file.write(query_update)
    query_new = query_start + ' Match (b:se_Sider{umlsIDmeddra:line.identifier}) Create (n:SideEffect{' + query_new + ' sider:"yes", url:"http://identifiers.org/umls/"+line.identifier, resource:["SIDER"],  source: "UMLS via SIDER 4.1", license:"CC BY-NC-SA 4.0"}) Create (n)-[:equal_to_SE]->(b);\n'
    query_new = query_new % ('se_new')
    cypher_file.write(query_new)
    cypher_file.close()

    # add query to update disease nodes with do='no'
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = ''':begin\n Match (n:SideEffect) Where not exists(n.sider) Set n.sider="no";\n :commit\n '''
    cypher_general.write(query)
    cypher_general.close()


'''
this start only the function the are use for generate the map cypher
'''


def integrate_side_effects():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path sider se')

    print(datetime.datetime.utcnow())
    print('Load in all side effect from hetionet in dictionary')

    load_side_effects_from_hetionet_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in all side effect from sider in dictionary')

    load_sider_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('map sider to hetionet per cypher')

    generate_cypher_file()

    print(
        '###########################################################################################################################')


def main():
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Integrate sider side effects into hetionet')

    integrate_side_effects()


if __name__ == "__main__":
    # execute only if run as a script
    main()
