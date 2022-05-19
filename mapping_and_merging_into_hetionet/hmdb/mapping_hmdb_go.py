# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 08:41:20 2018

@author: ckoenigs
"""

import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


'''
get information and put the into a dictionary one norma identifier and one alternative identifier to normal identifier
'''


def get_information_and_add_to_dict(label, dict_hetionet, dict_alternative_ids_hetionet):
    query = '''MATCH (n:%s) RETURN n.identifier,n.name, n.alternative_ids'''
    query = query % (label)
    results = g.run(query)

    for identifier, name, alternative_ids in results:
        dict_hetionet[identifier] = name
        if alternative_ids:
            for alternative_id in alternative_ids:
                if alternative_id not in dict_alternative_ids_hetionet:
                    dict_alternative_ids_hetionet[alternative_id]=set()
                dict_alternative_ids_hetionet[alternative_id].add(identifier)


# csv of nodes without ontology
file_without_ontology = open('go/nodes_without_ontology.tsv', 'w')
csv_without_ontology = csv.writer(file_without_ontology, delimiter='\t')
csv_without_ontology.writerow(['id', 'ontology','name'])


def load_hmdb_data_in_an_map_to_database(label, dict_hetionet, dict_alternative_ids_hetionet, csv_writer):
    """

    :param label:
    :param dict_hetionet:
    :param dict_alternative_ids_hetionet:
    :param csv_writer:
    :return:
    """
    query = '''MATCH (n:%s) RETURN n''' % label
    results = g.run(query)

    counter_mapped=0
    counter_not_mapped = 0


    for go_node, in results:
        go_id = go_node['identifier']
        go_name = go_node['description']

        if go_id in dict_hetionet:
            csv_writer.writerow([go_id,go_id,'identifier'])
            counter_mapped+=1
        elif go_id in dict_alternative_ids_hetionet:
            counter_mapped+=1
            for real_go_id in dict_alternative_ids_hetionet[go_id]:
                csv_writer.writerow([go_id, real_go_id, 'alternative_id'])
        else:
            counter_not_mapped+=1
            csv_without_ontology.writerow([go_id,label, go_name])

    print('number of mapped nodes:',counter_mapped)
    print('number of not mapped nodes:', counter_not_mapped)

# cypher file to integrate and update the go nodes
cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')


def generate_files(label, label_hmdb):
    """
    Generate tsv file for mapping ang prepar query for integrate the mapping.
    :param label: string
    :param label_hmdb: string
    :return: csv writer
    """
    # generate mapped csv
    file_name = 'go/mapping_' + label_hmdb + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    writer = csv.writer(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GOIDHMDB', 'GOIDHetionet','how_mapped'])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/hmdb/%s" As line  Fieldterminator '\\t'  Match (c:%s{ identifier:line.GOIDHetionet}), (n:%s{identifier:line.GOIDHMDB}) SET  c.hmdb="yes", c.resource=c.resource+'HMDB' Create (c)-[:equal_to_hmdb_go{how_mapped:line.how_mapped}]->(n);\n'''
    query = query % (file_name, label, label_hmdb)
    cypher_file.write(query)

    return writer


def main():
    global path_of_directory
    # define path to project
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    list_tuple_labels = [('BiologicalProcess', 'Biologicalprocess_HMDB'),
                         ('CellularComponent', 'Cellularcomponent_HMDB'),
                         ('MolecularFunction', 'Molecularfunction_HMDB')]

    for (label, hmdb_label) in list_tuple_labels:
        dict_hetionet = {}
        dict_alternative_ids_hetionet = {}
        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Load all go from hetionet into a dictionary')

        get_information_and_add_to_dict(label, dict_hetionet, dict_alternative_ids_hetionet)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Prepare cypher query and tsv file')

        csv_writer = generate_files(label, hmdb_label)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('Load all hmdb '+hmdb_label+' from neo4j into a dictionary')

        load_hmdb_data_in_an_map_to_database(hmdb_label,dict_hetionet, dict_alternative_ids_hetionet, csv_writer)



    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

if __name__ == "__main__":
    # execute only if run as a script
    main()
