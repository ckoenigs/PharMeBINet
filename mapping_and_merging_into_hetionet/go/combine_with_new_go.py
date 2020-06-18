# -*- coding: utf-8 -*-
"""
Created on Thr Sep 26 12:52:43 2017

@author: ckoenig
"""

'''integrate the other diseases and relationships from disease ontology in hetionet'''
from py2neo import Graph  # , authenticate
import datetime
import sys, csv
from collections import defaultdict

# disease ontology license
license = 'CC0 4.0 International'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# label of go nodes
label_go = 'go'

# dictionary new go
dict_new_go_to_node = {}

# dictionary of the new nodes
dict_new_nodes = {}

# dictionary csv files
dict_label_to_mapped_to_csv = defaultdict(dict)

# header of csv file
header = []

# header to property name
dict_header_to_property = {}

# cypher file
cypher_file = open('cypher.cypher', 'w')
cypher_file_delete = open('cypher_delete.cypher', 'w')

# bash shell for merge combined nodes
bash_shell = open('merge_nodes.sh', 'w')
bash_shell.write('#!/bin/bash\n')

'''
Get the  properties of go
'''


def get_go_properties():
    query = '''MATCH (p:go) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    result = g.run(query)
    query_nodes_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/go/%s" As line FIELDTERMINATOR '\\t' '''

    part = ''' Match (b:%s{id:line.identifier})''' % (label_go)
    query_nodes_start = query_nodes_start + part
    query_middle_mapped = ', (a:%s{identifier:line.identifier}) Set '
    query_middle_new = ' Create (a:%s{'
    query_delete_middle = ', (a:%s{identifier:line.identifier}) Detach Delete a,b;\n'
    for property, in result:
        if property in ['def', 'id', 'alt_ids','xrefs']:
            if property == 'id':
                query_middle_new += 'identifier:b.' + property + ', '
                query_middle_mapped += 'a.identifier=b.' + property + ', '
            elif property == 'alt_ids':
                query_middle_new += 'alternative_ids:b.' + property + ', '
                query_middle_mapped += 'a.alternative_ids=b.' + property + ', '
            elif property=='xrefs':
                query_middle_new += 'xrefs:split(line.' + property + ',"|"), '
                query_middle_mapped += 'a.xrefs=split(line.' + property + ',"|"), '

            else:
                query_middle_new += 'definition:b.' + property + ', '
                query_middle_mapped += 'a.definition=b.' + property + ', '
        elif property in ["namespace", "is_obsolete", "replaced_by"]:
            continue
        else:
            query_middle_new += property + ':b.' + property + ', '
            query_middle_mapped += 'a.' + property + '=b.' + property + ', '
    query_end = ''' Create (a)-[:equal_to_go]->(b);\n'''
    global query_new, query_mapped, query_delete
    # combine the different parts for mapping query
    query_mapped = query_nodes_start + query_middle_mapped + 'a.resource=a.resource+"GO", a.go="yes", a.license="' + license + '"' + query_end

    # combine the important parts of node creation
    query_new = query_nodes_start + query_middle_new + 'resource:["GO"], go:"yes", source:"Gene Ontology", url:"http://purl.obolibrary.org/obo/"+line.identifier, license:"' + license + '"})' + query_end

    # query_delete=query_nodes_start+ query_delete_middle

    # delete the obsolete nodes of go
    query_delete_go = ''' Match (b:%s) Where exists(b.is_obsolete) Detach Delete b;\n'''
    query_delete_go = query_delete_go % (label_go)
    cypher_file_delete.write(query_delete_go)
    # delete query of hetionet nodes which did not mapped
    query_delete = '''Match (a:%s) Where not (a)-[:equal_to_go]->(:''' + label_go + ''') Detach Delete a;\n'''


'''
create the csv files
'''


def create_csv_files():
    for label in dict_go_to_hetionet_label:
        for x in [True, False]:
            if x:
                file_name = 'output/integrate_go_' + label + '_mapped.tsv'
                query = query_mapped % (file_name, dict_go_to_hetionet_label[label])
            else:
                file_name = 'output/integrate_go_' + label + '.tsv'
                query = query_new % (file_name, dict_go_to_hetionet_label[label])
            cypher_file.write(query)
            file = open(file_name, 'w')
            csv_file = csv.writer(file, delimiter='\t')
            csv_file.writerow(['identifier','xrefs'])
            dict_label_to_mapped_to_csv[label][x] = csv_file

        # delete nodes which mapped but were are about to be removed
        # this can be away if I have on query which delete all nodes which has no connection to a go node
        # file_name= file_name='output/integrate_go_'+label+ '_delete.tsv'
        # query = query_delete % (file_name, dict_go_to_hetionet_label[label])
        # cypher_file.write(query)
        # file = open(file_name, 'w')
        # csv_file = csv.writer(file, delimiter='\t')
        # csv_file.writerow(['identifier'])
        # dict_label_to_mapped_to_csv[label]['delete'] = csv_file

        # delete of nodes which did not mapped
        query = query_delete % (dict_go_to_hetionet_label[label])
        cypher_file_delete.write(query)


# dictionary go namespace to node dictionary
dict_go_namespace_to_nodes = {}

'''
Get all information of on label in a dictionary
'''


def get_all_information_from_hetionet(label):
    query = '''Match (n:%s) Return n''' % (label)
    result = g.run(query)

    # dictionary of nodes
    dict_nodes = {}

    for node, in result:
        identifier = node['identifier']
        dict_nodes[identifier] = dict(node)

    return dict_nodes


# dictionary go label to hetionet label
dict_go_to_hetionet_label = {
    'molecular_function': 'MolecularFunction',
    'biological_process': 'BiologicalProcess',
    'cellular_component': 'CellularComponent'
}

'''
check if id is in a dictionary
'''


def check_if_identifier_in_hetionet(identifier, namespace, node, xrefs, is_alternative_id=False):
    found_id = False
    xref_string="|".join(xrefs)
    if identifier in dict_go_namespace_to_nodes[namespace]:
        if is_alternative_id:
            return True
        if 'is_obsolete' in node:
            print('need to be delete')
            if 'replaced_by' in node:
                print('relaced by what to do?')
                return True
            # dict_label_to_mapped_to_csv[namespace]['delete'].writerow([identifier])
            return found_id
        dict_label_to_mapped_to_csv[namespace][True].writerow([identifier,xref_string])
    else:
        if 'is_obsolete' in node:
            print('need to be delete')
            return found_id
        if is_alternative_id:
            return False
        dict_label_to_mapped_to_csv[namespace][False].writerow([identifier,xref_string])
    return True


# dictionary for relationship ends
dict_relationship_ends = {
    "biological_process": 'BiB',
    "molecular_function": 'MiM',
    "cellular_component": 'CciCc'
}

'''
Get all is_a relationships for bp, cc and mf and add the into a csv file
'''


def get_is_a_relationships_and_add_to_csv(namespace):
    query = '''Match (n:go)-[:is_a]->(m:go) Where n.namespace="%s"  Return n.id,m.id;'''
    query = query % namespace
    results = g.run(query)
    file_name = 'output/integrate_go_' + namespace + '_relationship.tsv'
    file = open(file_name, 'w')
    csv_file = csv.writer(file, delimiter='\t')
    csv_file.writerow(['identifier_1', 'identifier_2'])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/go/%s" As line FIELDTERMINATOR '\\t' 
    Match (a1:%s{identifier:line.identifier_1}), (a2:%s{identifier:line.identifier_2}) Create (a1)-[:IS_A_%s{license:"CC0 4.0 International", source:"GO", unbiased:false}]->(a2);\n'''
    query = query % (file_name, dict_go_to_hetionet_label[namespace], dict_go_to_hetionet_label[namespace],
                     dict_relationship_ends[namespace])
    cypher_file.write(query)

    # go through the results
    for id1, id2, in results:
        csv_file.writerow([id1, id2])


'''
generate dictionary of hetionet
'''


def generate_dictionary():
    dict_go_namespace_to_nodes['molecular_function'] = get_all_information_from_hetionet('MolecularFunction')
    dict_go_namespace_to_nodes['biological_process'] = get_all_information_from_hetionet('BiologicalProcess')
    dict_go_namespace_to_nodes['cellular_component'] = get_all_information_from_hetionet('CellularComponent')

    get_is_a_relationships_and_add_to_csv('molecular_function')
    get_is_a_relationships_and_add_to_csv('biological_process')
    get_is_a_relationships_and_add_to_csv('cellular_component')


'''
go through all go nodes and sort them into the dictionary 
'''


def go_through_go():
    query = '''Match (n:%s) Return n''' % (label_go)
    result = g.run(query)
    for node, in result:
        identifier = node['id']
        if identifier == 'GO:0099403':
            print('jupp')
        namespace = node['namespace']
        alternative_ids = node['alt_ids'] if 'alt_ids' in node else []
        xrefs=node['xrefs'] if 'xrefs'   in node else []
        new_xref=set()
        for xref  in  xrefs:
            splitted_xref=xref.split(' ')
            if len(splitted_xref)>1:
                new_xref.add(splitted_xref[0])
            else:
                new_xref.add(xref)
        found_id = check_if_identifier_in_hetionet(identifier, namespace, node,new_xref)

        # go through the alternative ids
        for alternative_id in alternative_ids:
            found_id_alt = check_if_identifier_in_hetionet(alternative_id, namespace, node, new_xref, is_alternative_id=True)
            # if the identifier and an alternative id matched in hetionet the nodes need to be combined
            # therfore the merge process iss add into the bash file
            if found_id and found_id_alt:
                print('found id and alt id')
                text = 'python ../add_information_from_a_not_existing_node_to_existing_node.py %s %s %s\n' % (
                    alternative_id, identifier, dict_go_to_hetionet_label[namespace])
                bash_shell.write(text)
                text = '''now=$(date +"%F %T")\n echo "Current time: $now"\n'''
                bash_shell.write(text)

            elif found_id_alt:
                print('found with alternative id')


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('get go properties and generate queries')

    get_go_properties()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('create csv for all names spscae and mapped a csv')

    create_csv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('generate hetionet dictionary')

    generate_dictionary()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('load all hetionet diseases in dictionary')

    go_through_go()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
