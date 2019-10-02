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


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


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

# cypher file
cypher_file=open('cypher.cypher','w')

'''
Get the  properties of go
'''
def get_go_properties():
    query='''MATCH (p:go) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    result=g.run(query)
    query_nodes_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/go/%s As line FIELDTERMINATOR '\\t' Match (b:%s{id:line.identifier})'''
    query_nodes_start= query_nodes_start %(label_go)
    query_middle_mapped=', (a:%s{identifier:line.identifier}) Set '
    query_middle_new=' Create (a:%s{'
    for property in result:
        if property in ['def','id','alt_ids']:
            if property=='id':
                query_middle_new+='identifier:b.'+property+', '
                query_middle_mapped+='a.identifier=b.'+property+', '
            elif property=='alt_ids':
                query_middle_new += 'alternative_ids:b.' + property + ', '
                query_middle_mapped += 'a.alternative_ids=b.' + property + ', '
            else:
                query_middle_new += 'definition:b.' + property + ', '
                query_middle_mapped += 'a.definition=b.' + property + ', '
        elif property in ["namespace","is_obsolete","replaced_by"]:
            continue
        else:
            query_middle_new += property+':b.' + property + ', '
            query_middle_mapped += 'a.'+property+'=b.' + property + ', '
    query_end=''' Create (a)-[:equal_to_go]->(b);\n'''
    global query_new, query_mapped
    query_mapped=query_nodes_start+query_middle_mapped+ 'a.resource=a.resource+"GO", a.go="yes", a.license='+license+query_end
    query_new=query_nodes_start+query_middle_new+'resource:["GO"], go."yes", source:"Gene Ontology", url:"http://purl.obolibrary.org/obo/"+line.identifier, license:'+license+query_end



'''
create the csv files
'''
def create_csv_files():
    for label in dict_go_to_hetionet_label:
        for x in [True, False]:
            if x:
                file_name='output/integrate_go_'+label+ '_mapped.tsv'
                query=query_mapped %(file_name)
            else:
                file_name='output/integrate_go_'+label+ '.tsv'
                query=query_new %(file_name)
            cypher_file.write(query)
            file=open(file_name,'w')
            csv_file=csv.writer(file,delimiter='\t')
            csv_file.writerow(['identifier'])
            dict_label_to_mapped_to_csv[label][x]=csv_file

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
check if id is in a dictionary
'''
def check_if_identifier_in_hetionet(identifier,namespace,node):
    found_id=False
    if identifier in dict_go_namespace_to_nodes[namespace]:
        if 'is_obsolete' in node:
            print('need to be delete')
            return found_id
        elif 'replaced_by' in node:
            print('relaced by what to do?')
            return found_id
        dict_label_to_mapped_to_csv[namespace].writerow(identifier)
    return True



'''
generate dictionary of hetionet
'''
def generate_dictionary():
    dict_go_namespace_to_nodes['molecular_function']=get_all_information_from_hetionet('MolecularFunction')
    dict_go_namespace_to_nodes['biological_process'] = get_all_information_from_hetionet('BiologicalProcess')
    dict_go_namespace_to_nodes['cellular_component'] = get_all_information_from_hetionet('CellularComponent')


'''
go through all go nodes and sort them into the dictionary 
'''
def go_through_go():
    query = '''Match (n:%s) Return n''' % (label_go)
    result = g.run(query)
    for node, in result:
        identifier=node['identifier']
        namespace=node['namespace']
        alternative_ids=node['alt_ids'] if 'alt_ids' in node else []
        found_id=check_if_identifier_in_hetionet(identifier,namespace,node)
        if found_id:
            continue

        for alternative_id in alternative_ids:
            found_id = check_if_identifier_in_hetionet(alternative_id, namespace, node)
            if found_id:
                continue





def main():
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
