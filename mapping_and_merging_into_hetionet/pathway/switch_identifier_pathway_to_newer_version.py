# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph#, authenticate
import datetime
import csv
import sys
from collections import  defaultdict

# sys.path.append('../../drugbank/')
# from add_information_from_a_not_existing_node_to_existing_node import merge_information_from_one_node_to_another

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", )
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))


# dictionary with hetionet genes with identifier as key and value the name
dict_genes_hetionet = {}

# label of pathways
label_pathway='pathway_multi'

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    query = '''MATCH (n:Gene) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_genes_hetionet[identifier] = name

    print('number of pathway nodes in hetionet:' + str(len(dict_genes_hetionet)))

#header of the node csv
header=[]

# extra property
extra_property='all_mapped_ids'

'''
get the properties of pathway and make the list for the header of the csv file
however ignore the properties with genes, because this information will be in the relationships 
'''
def get_pathway_properties():
    query='''MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    query= query % (label_pathway)
    result=g.run(query)
    for property, in result:
        if property.find('gene')==-1:
            header.append(property)

    header.append(extra_property)

# version string pc
version_string='PC11_'

# cypher file
cypher_file=open('cypher.cypher','w')
#query to delete all old pathways
query='MATCH (n:Pathway) Detach Delete n;\n'
cypher_file.write(query)

# dictionary pathway name from pathway list an the identifier plus the source
dict_name_to_pc_or_wp_identifier = {}


# dictionary with own id from pc to name, pcid and sourc
dict_own_id_to_pcid_and_other={}

#dictionary of identifier to nodes information
dict_id_to_node={}

# csv files for nodes and relationship
file_node=open('output/node.tsv','w')
csv_node=csv.writer(file_node,delimiter='\t')

file_rela=open('output/rela.tsv','w')
csv_rela=csv.writer(file_rela,delimiter='\t')
rela_header=['gene_id','pathway_id']
csv_rela.writerow(rela_header)

#dictionary rela
dict_rela={}

'''
load all pathway from neo4j
'''


def load_in_all_pathways():

    #
    query = '''MATCH (n:%s) RETURN n ''' %(label_pathway)
    results = g.run(query)

    for node, in results:
        identifier=node['identifier']
        if identifier=='PC11_755':
            print('huhu')
        dict_id_to_node[identifier]=dict(node)

        # fill dictionary with name to rest
        names=node['names']
        for name in names:
            if not name in dict_name_to_pc_or_wp_identifier:
                dict_name_to_pc_or_wp_identifier[name]=[dict(node)]
            else:
                dict_name_to_pc_or_wp_identifier[name].append(dict(node))
                # print( dict_name_to_pc_or_wp_identifier[name])

        for gene_id in node['genes']:
            gene_id=int(gene_id)
            if gene_id in dict_genes_hetionet:
                dict_rela[(str(gene_id),identifier)]=1
                # csv_rela.writerow([str(gene_id),identifier])




    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))


'''
combine the information of the different sources
'''
def combine_information_from_different_sources(list_of_nodes):
    dict_combined_information=defaultdict(set)
    for node in list_of_nodes:
        for key, value in node.items():
            if type(value)!=list:
                dict_combined_information[key].add(value)
            else:
                dict_combined_information[key]=dict_combined_information[key].union(value)
    #maybe replace the sets with list or transform into string
    return dict_combined_information

# dictionary the old pc id to the new one
dict_old_pc_to_new={}

# properties which are a list
list_list_properties=set([])

'''
Prepare value
'''
def prepare_value(value, head, combined_node):
    if head == 'identifier':
        identifier_s=value
        if combined_node:
            identifier = value.pop()
            for old_id in value:
                dict_old_pc_to_new[old_id] = identifier
            value = identifier
    if type(value) in [list, set]:
        list_list_properties.add(head)
        value = '|'.join(value)
    return value.encode('utf-8')

'''
fill the node csv file by going through the name dictionary and maybe they nodes with the same name will be merges to one node
'''
def generate_node_csv():
    csv_node.writerow(header)

    counter_double_names=0
    counter_multiple=0
    for name, list_of_nodes in dict_name_to_pc_or_wp_identifier.items():
        if len(list_of_nodes)==1:
            list_info=[]
            node=list_of_nodes[0]

            for head in header:
                value=node[head] if head in node else ''
                if head=='identifier':
                    identifier=value
                elif head==extra_property:
                    value=identifier
                #prepare the value for csv
                value=prepare_value(value,head,False)
                list_info.append(value)
            csv_node.writerow(list_info)
        else:
            counter_double_names+=1
            if len(list_of_nodes)>2:
                counter_multiple+=1
                print(list_of_nodes)
                print(len(list_of_nodes))
            dict_combined=combine_information_from_different_sources(list_of_nodes)

            list_info = []
            for head in header:
                value = dict_combined[head] if head in dict_combined else ''
                if head=='identifier':
                    identifier='|'.join(value)
                elif head==extra_property:
                    value=identifier
                #prepare the value for csv
                value=prepare_value(value,head,True)


                list_info.append(value)
            csv_node.writerow(list_info)
            # node1=list_of_nodes[0]
            # node2=list_of_nodes[1]
            # genes_1=node1['genes']
            # genes_2 = node2['genes']
            # source_1=node1['source']
            # source_2=node2['source']
            # intersection=set(genes_1).intersection(genes_2)
            # if len(genes_1)>len(genes_2):
            #     if len(intersection)!=len(genes_2):
            #         print(node1['identifier'])
            #         print(node2['identifier'])
            #         print(source_1)
            #         print(source_2)
            #         # print(genes_2)
            #         # print(intersection)
            #         print(set(genes_2).difference(intersection))
            #         print('not the same genes')
            #         if source_1==source_2:
            #             print('same source')
            #             print(node1['idOwn']) if 'idOwn' in node1 else ''
            #             print(node2['idOwn']) if 'idOwn' in node2 else ''
            # else:
            #     if len(intersection)!=len(genes_1):
            #         print(node1['identifier'])
            #         print(node2['identifier'])
            #         print(source_1)
            #         print(source_2)
            #         # print(genes_1)
            #         # print(intersection)
            #         print(set(genes_1).difference(intersection))
            #         print('not the same genes')
            #         if source_1==source_2:
            #             print(node1['idOwn']) if 'idOwn' in node1 else ''
            #             print(node2['idOwn']) if 'idOwn' in node2 else ''

    print('number of duplicated once:'+str(counter_double_names))
    print('number of multies:'+str(counter_multiple))

'''
generate rela csv and cypher file
'''
def generate_rela_csv_and_cypher_queries():
    for (gene_id, identifier) in dict_rela.keys():
        # depending if the identifier is removed or not the correct identifier is written into the csv file
        if not identifier in dict_old_pc_to_new:
            csv_rela.writerow([gene_id, identifier])
        else:
            #it made sense that nodes which are combined to one has similare genes and to avoid duplication first check
            # if this is already in the dictionary
            if not (gene_id, dict_old_pc_to_new[identifier]) in dict_rela:
                csv_rela.writerow([gene_id, dict_old_pc_to_new[identifier]])

    # general start of queries
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/pathway/output/%s.tsv" As line FIELDTERMINATOR '\\t' '''
    #generate cypher for node creation
    query_node_middle='Create (n:Pathway{'
    for head in header:
        if head in list_list_properties:
            query_node_middle+=head+':split(line.'+head+',"|"), '
        else:
            query_node_middle += head + ':line.' + head + ', '
    query_node=query_start+ query_node_middle[:-2]+', pathway:"yes"}) ;\n'
    query_node=query_node %('node')

    cypher_file.write(query_node)

    # query equal to
    query_equal=query_start+' Match (b:%s ), (n:Pathway{identifier:line.identifier}) Where b.identifier in split(line.%s,"|") Create (n)-[:equal_to_multi_pathways]->(b) Set n.pathway="yes";\n'
    query_equal=query_equal %('node',label_pathway,extra_property)
    cypher_file.write(query_equal)

    # cypher query for relationships
    query_rela_middle='Match '
    for head in rela_header:
        if head.split('_')[0]=='gene':
            query_rela_middle+= '(g:Gene{identifier:toInt(line.'+head+')}) ,'
        else:
            query_rela_middle += '(p:Pathway{identifier:line.' + head + '}) ,'
    query_rela=query_start+query_rela_middle[:-2]+ 'Create (g)-[:PARTICIPATES_GpPW{license:p.license, source:p.source, unbiased:false, url:p.url}]->(p);\n'
    query_rela=query_rela %('rela')
    cypher_file.write(query_rela)

# path to directory
path_of_directory=''

    
    
def main():
    global path_of_directory
    if len(sys.argv)>1:
        path_of_directory=sys.argv[1]
    else:
        sys.exit('need a path')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from hetionet into a dictionary')

    load_hetionet_pathways_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('load pathway properties')

    get_pathway_properties()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from d. himmelstein into a dictionary')

    load_in_all_pathways()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Generate csv for switch identifier and ')

    generate_node_csv()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Generate csv for rela ')

    generate_rela_csv_and_cypher_queries()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()