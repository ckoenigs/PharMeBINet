# -*- coding: utf-8 -*-
"""
Created on Thr Sep 26 12:52:43 2017

@author: ckoenig
"""
from mapping_and_merging_into_hetionet.drugbank.salt_to_compound_mapping_connection_to_drugs import label_of_salt

'''integrate the other diseases and relationships from disease ontology in hetionet'''
from py2neo import Graph, authenticate
import datetime
import sys,csv

# disease ontology license
license='CC0 4.0 International'

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# dictionary go namespace to node dictionary
dict_go_namespace_to_nodes={}

'''
Get all information of on label in a dictionary
'''
def get_all_information_from_hetionet(label):
    query='''Match (n:%s) Return n''' %(label)
    result=g.run(query)

    #dictionary of nodes
    dict_nodes={}

    for node, in result:
        identifier=node['identifier']
        dict_nodes[identifier]=dict(node)

    return dict_nodes
# dictionary go label to hetionet label
dict_go_to_hetionet_label={
'molecular_function':'MolecularFunction',
'biological_process':'BiologicalProcess',
'cellular_component':'CellularComponent'
}


'''
generate dictionary of hetionet
'''
def generate_dictionary():
    dict_go_namespace_to_nodes['molecular_function']=get_all_information_from_hetionet('MolecularFunction')
    dict_go_namespace_to_nodes['biological_process'] = get_all_information_from_hetionet('BiologicalProcess')
    dict_go_namespace_to_nodes['cellular_component'] = get_all_information_from_hetionet('CellularComponent')

#label of go nodes
label_go='go'

#dictionary new go
dict_new_go_to_node={}

# dictionary of the new nodes
dict_new_nodes={}

# dictionary csv files
dict_label_to_mapped_to_csv={}

#header of csv file
header=[]

#header to property name
dict_header_to_property={}

'''
Get the  properties of go
'''
def get_go_properties():
    query='''MATCH (p:go) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    result=g.run(query)
    for property in result:
        header.append(property)
        if property in ['def','id']:
            if property=='id':
                dict_header_to_property[property] = 'identifier'
            else:
                dict_header_to_property[property]='definition'
        elif property in ["namespace","is_obsolete","replaced_by"]:
            continue
        else:
            dict_header_to_property[property] = property


'''
create the csv files
'''
def create_csv_files():
    for label in dict_go_to_hetionet_label:
        for x in [True, False]:
            file_name='output/integrate_go_'+label+ '_mapped.tsv' if x else 'output/integrate_go_'+label+ '.tsv'
            file=open(file_name,'w')
            csv_file=csv.writer(file,delimiter='\t')
            dict_label_to_mapped_to_csv[label][x]=csv_file

'''
go through all go nodes and sort them into the dictionary 
'''
def go_through_go():
    query = '''Match (n:%s) Return n''' % (label_go)
    result = g.run(query)
    for node, in result:
        identifier=node['identifier']
        namespace=node['namespace']
        node_mapped=False
        if identifier in dict_go_namespace_to_nodes[namespace]:
            node_mapped=True



def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

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
