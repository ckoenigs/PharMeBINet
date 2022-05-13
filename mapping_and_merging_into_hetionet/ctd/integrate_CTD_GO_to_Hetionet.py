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


# dictionary with hetionet biological process with identifier as key and value the name
dict_biological_process_hetionet = {}
# dictionary with hetionet biological process with alternative id as key and value identifier
dict_biological_process_alternative_hetionet = {}

# dictionary with hetionet cellular component with identifier as key and value the name
dict_cellular_component_hetionet = {}
# dictionary with hetionet cellular component with alternative id as key and value identifier
dict_cellular_component_alternative_hetionet = {}

# dictionary with hetionet molecular function with identifier as key and value the name
dict_molecular_function_hetionet = {}
# dictionary with hetionet molecular function with alternative id as key and value identifier
dict_molecular_function_alternative_hetionet = {}

# dictionary go id to resource
dict_go_id_to_resource={}

'''
get information and put the into a dictionary one norma identifier and one alternative identifier to normal identifier
'''
def get_information_and_add_to_dict(label,dict_hetionet, dict_alternative_ids_hetionet):
    query = '''MATCH (n:%s) RETURN n.identifier,n.name, n.alternative_ids, n.resource'''
    query=query %(label)
    results = g.run(query)

    for identifier, name, alternative_ids, resource, in results:
        dict_hetionet[identifier] = name
        if alternative_ids:
            for alternative_id in alternative_ids:
                dict_alternative_ids_hetionet[alternative_id]=identifier
        dict_go_id_to_resource[identifier]=set(resource)

'''
load in all biological process, molecular function and cellular components from hetionet in a dictionary
'''


def load_hetionet_go_in():
    # fill dict for biological process
    get_information_and_add_to_dict('BiologicalProcess',dict_biological_process_hetionet, dict_biological_process_alternative_hetionet)

    # fill dict for molecular function
    get_information_and_add_to_dict('MolecularFunction',dict_molecular_function_hetionet, dict_molecular_function_alternative_hetionet)

    # fill dict for cellular components
    get_information_and_add_to_dict('CellularComponent',dict_cellular_component_hetionet, dict_cellular_component_alternative_hetionet)

    print('number of biological process nodes in hetionet:' + str(len(dict_biological_process_hetionet)))
    print('number of cellular component nodes in hetionet:' + str(len(dict_cellular_component_hetionet)))
    print('number of molecular function nodes in hetionet:' + str(len(dict_molecular_function_hetionet)))


# csv of nodes without ontology
file_without_ontology=open('GO/nodes_without_ontology.tsv','w')
csv_without_ontology=csv.writer(file_without_ontology,delimiter='\t')
csv_without_ontology.writerow(['id','ontology'])

'''
check if go is in hetionet or not
'''


def check_if_new_or_part_of_hetionet(hetionet_label, go_id, go_name,highestGOLevel):
    # is only used if the ontology is not existing
    found_with_alternative_id = False
    if hetionet_label is None:
        if go_id in dict_biological_process_hetionet:
            hetionet_label='Biological Process'
        elif go_id in dict_cellular_component_hetionet:
            hetionet_label="Cellular Component"
        elif go_id in dict_molecular_function_hetionet:
            hetionet_label='Molecular Function'
        elif go_id in dict_biological_process_alternative_hetionet:
            found_with_alternative_id=True
            hetionet_label = 'Biological Process'
            alternative_id=go_id
            normal_id=dict_biological_process_alternative_hetionet[alternative_id]
        elif go_id in dict_cellular_component_alternative_hetionet:
            found_with_alternative_id=True
            hetionet_label = 'Cellular Component'
            alternative_id=go_id
            normal_id=dict_cellular_component_alternative_hetionet[alternative_id]
        elif go_id in dict_molecular_function_alternative_hetionet:
            found_with_alternative_id=True
            hetionet_label = 'Molecular Function'
            alternative_id=go_id
            normal_id=dict_molecular_function_alternative_hetionet[alternative_id]
        # if this is not found in hetionet then this is an old go id
        else:
            # print('should be delete?')
            # print(go_id)
            return
            # sys.exit(go_id)
        csv_without_ontology.writerow([go_id,hetionet_label])
    [dict_hetionet, dict_alternative_id_to_hetionet, dict_ctd_in_hetionet_alternative, dict_ctd_in_hetionet] = dict_process[hetionet_label]

    # check if this id is hetionet
    if go_id in dict_hetionet:
        if go_name == dict_hetionet[go_id]:
            dict_ctd_in_hetionet[go_id] = [go_name, highestGOLevel]
        else:
            # print('same id but different names')
            # print(go_id)
            # print(go_name)
            # print(dict_hetionet[go_id])
            dict_ctd_in_hetionet[go_id] = [go_name, highestGOLevel]
    # check if it is replaced by a new go id (this id will appear in the alternative ids of the new node)
    # is add to the alternative mapped dictionary
    elif go_id in dict_alternative_id_to_hetionet:
        dict_ctd_in_hetionet_alternative[go_id]=dict_alternative_id_to_hetionet[go_id]
    # if the ontology was unknown  then the  id is add to the alternative mapped dictionary and in the tsv
    # to set the ontology
    elif found_with_alternative_id:
        dict_ctd_in_hetionet_alternative[alternative_id]=normal_id
        csv_without_ontology.writerow([alternative_id, hetionet_label])
    # nodes which are not in go anymore
    else:
        return
        # print(go_id)
        # print(hetionet_label)
        # print('not good')

'''
load all ctd genes and check if they are in hetionet or not
'''


def load_ctd_go_in():
    query = '''MATCH (n:CTD_GO) RETURN n'''
    results = g.run(query)

    for go_node, in results:
        go_id = go_node['go_id']
        go_name = go_node['name']
        ontology = go_node['ontology']
        highestGOLevel= go_node['highestGOLevel']
        check_if_new_or_part_of_hetionet(ontology,go_id,go_name,highestGOLevel)

    print('number of existing biological process nodes:' + str(len(dict_ctd_biological_process_in_hetionet)))

    print('number of existing Molecular Function nodes:' + str(len(dict_ctd_molecular_function_in_hetionet)))

    print('number of existing Cellular Component nodes:' + str(len(dict_ctd_cellular_component_in_hetionet)))

# dictionary of ctd biological_process which are in hetionet with properties: name
dict_ctd_biological_process_in_hetionet = {}

# dictionary of ctd cellular_component which are in hetionet with properties: name
dict_ctd_cellular_component_in_hetionet = {}

# dictionary of ctd molecular_function which are in hetionet with properties: name
dict_ctd_molecular_function_in_hetionet = {}

# dictionary of ctd biological_process which are in hetionet with properties: name
dict_ctd_biological_process_in_hetionet_alternative = {}

# dictionary of ctd cellular_component which are in hetionet with properties: name
dict_ctd_cellular_component_in_hetionet_alternative = {}

# dictionary of ctd molecular_function which are in hetionet with properties: name
dict_ctd_molecular_function_in_hetionet_alternative = {}

# dictionary with for biological_process, cellular_component, molecular_function the right dictionaries
# first dictionary has all identifier in hetionet, the second has all alternative hetionet ids to there identifier,
# third list of all ctd ids which map with alternative ids, fourth dict of all ctd which mapped directly to hetionet
dict_process = {
    "Biological Process": [dict_biological_process_hetionet, dict_biological_process_alternative_hetionet, dict_ctd_biological_process_in_hetionet_alternative,
                           dict_ctd_biological_process_in_hetionet],
    "Molecular Function": [dict_molecular_function_hetionet, dict_molecular_function_alternative_hetionet, dict_ctd_molecular_function_in_hetionet_alternative,
                           dict_ctd_molecular_function_in_hetionet],
    "Cellular Component": [dict_cellular_component_hetionet,dict_cellular_component_alternative_hetionet, dict_ctd_cellular_component_in_hetionet_alternative,
                           dict_ctd_cellular_component_in_hetionet]
}

#define path to project
if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path')

# cypher file to integrate and update the go nodes
cypher_file = open('output/cypher.cypher', 'a',encoding='utf-8')
# delete all old
# query='''begin\n MATCH p=()-[r:equal_to_CTD_go]->() Delete r;\n commit\n'''
# cypher_file.write(query)
# add ontology to ctd go
query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''mapping_and_merging_into_hetionet/ctd/GO/nodes_without_ontology.tsv" As line  FIELDTERMINATOR '\\t' Match (n:CTD_GO{go_id:line.id}) SET n.ontology=line.ontology ;\n'''
cypher_file.write(query)

def add_resource(go_id):
    """
    add to a give id the ctd resource and return it as string
    :param go_id: string
    :return: string
    """
    resource=dict_go_id_to_resource[go_id]
    resource.add('CTD')
    return '|'.join(sorted(resource))

'''
Generate cypher and tsv for generating the new nodes and the relationships
'''


def generate_files(file_name_addition, ontology, dict_ctd_in_hetionet,dict_ctd_in_hetionet_alternative ):
    # generate mapped csv
    with open('GO/mapping_' + file_name_addition + '.tsv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GOIDCTD', 'GOIDHetionet', 'highestGOLevel','resource'])
        # add the go nodes to cypher file

        for go_id, name in dict_ctd_in_hetionet.items():
            writer.writerow([go_id, go_id,'',add_resource(go_id)])

        for ctd_id, hetionet_id in dict_ctd_in_hetionet_alternative.items():
            writer.writerow([ctd_id, hetionet_id,'',add_resource(hetionet_id)])

    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''mapping_and_merging_into_hetionet/ctd/GO/mapping_%s.tsv" As line  FIELDTERMINATOR '\\t' Match (c:%s{ identifier:line.GOIDHetionet}), (n:CTD_GO{go_id:line.GOIDCTD}) SET  c.url_ctd=" http://ctdbase.org/detail.go?type=go&acc="+line.GOIDCTD, c.highestGOLevel=n.highestGOLevel, c.ctd="yes", c.resource=split(line.resource,"|") Create (c)-[:equal_to_CTD_go]->(n);\n'''
    query = query % (file_name_addition, ontology)
    cypher_file.write(query)



# dictionary from ctd ontology to label and file name
dict_ctd_ontology_to_file_and_label={
    "Biological Process":('bp', 'BiologicalProcess'),
    "Cellular Component":('cc', 'CellularComponent'),
    "Molecular Function":('mf', 'MolecularFunction')
}




def main():

    print (datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())
    print('Load all go from hetionet into a dictionary')

    load_hetionet_go_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())
    print('Load all ctd go from neo4j into a dictionary')

    load_ctd_go_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())
    print('Map generate tsv and cypher file for all three labels ')

    for ontology, [dict_in_hetionet, dict_in_hetionet_alternative, dict_ctd_in_hetionet_alternative,
                           dict_ctd_in_hetionet] in dict_process.items():
        file_name,hetionet_label=dict_ctd_ontology_to_file_and_label[ontology]
        generate_files(file_name,hetionet_label, dict_ctd_in_hetionet, dict_ctd_in_hetionet_alternative)

    # delete the node which did not mapped because they are obsoleted
    cypher='MATCH (n:CTD_GO) where not (n)<-[:equal_to_CTD_go]-() Detach Delete n;\n'
    cypher_file.write(cypher)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
