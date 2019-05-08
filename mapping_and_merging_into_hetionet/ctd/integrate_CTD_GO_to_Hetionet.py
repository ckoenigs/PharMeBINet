# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 08:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv, sys

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with hetionet biological process with identifier as key and value the name
dict_biological_process_hetionet = {}

# dictionary with hetionet cellular component with identifier as key and value the name
dict_cellular_component_hetionet = {}

# dictionary with hetionet molecular function with identifier as key and value the name
dict_molecular_function_hetionet = {}

'''
load in all biological process, molecular function and cellular components from hetionet in a dictionary
'''


def load_hetionet_go_in():
    query = '''MATCH (n:BiologicalProcess) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_biological_process_hetionet[identifier] = name

    query = '''MATCH (n:MolecularFunction) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_molecular_function_hetionet[identifier] = name

    query = '''MATCH (n:CellularComponent) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_cellular_component_hetionet[identifier] = name

    print('number of biological process nodes in hetionet:' + str(len(dict_biological_process_hetionet)))
    print('number of cellular component nodes in hetionet:' + str(len(dict_cellular_component_hetionet)))
    print('number of molecular function nodes in hetionet:' + str(len(dict_molecular_function_hetionet)))


dict_of_go_which_has_no_ontology={
    'GO:0070453':'Biological Process',
    'GO:0046035':'Biological Process',
    'GO:1902225':'Biological Process',
    'GO:0035937':'Biological Process',
    'GO:0006225':'Biological Process',
    'GO:0051320':'Biological Process',
    'GO:0071919':'Biological Process',
    'GO:0046114':'Biological Process',
    'GO:1900996':'Biological Process',
    'GO:1905691':'Biological Process',
    'GO:0006181':'Biological Process',
    'GO:1902492':'Biological Process'

}


'''
check if go is in hetionet or not
'''


def check_if_new_or_part_of_hetionet(hetionet_label, go_id, go_name,highestGOLevel):

    if hetionet_label is None:
        if go_id in dict_biological_process_hetionet:
            hetionet_label='Biological Process'
        elif go_id in dict_cellular_component_hetionet:
            hetionet_label="Cellular Component"
        elif go_id in dict_molecular_function_hetionet:
            hetionet_label='Molecular Function'
        elif go_id in dict_of_go_which_has_no_ontology:
            hetionet_label=dict_of_go_which_has_no_ontology[go_id]
        else:
            sys.exit(go_id)
    [dict_hetionet, dict_ctd_not_in_hetionet, dict_ctd_in_hetionet] = dict_processe[hetionet_label]


    if go_id in dict_hetionet:
        if go_name == dict_hetionet[go_id]:
            dict_ctd_in_hetionet[go_id] = [go_name, highestGOLevel]
        else:
            print('same id but different names')
            print(go_id)
            print(go_name)
            print(dict_hetionet[go_id])
            dict_ctd_in_hetionet[go_id] = [go_name, highestGOLevel]
    else:
        dict_ctd_not_in_hetionet[go_id] = [go_name, highestGOLevel]


# dictionary of biological_process which are not in hetionet with they properties: name
dict_ctd_biological_process_not_in_hetionet = {}

# dictionary of ctd biological_process which are in hetionet with properties: name
dict_ctd_biological_process_in_hetionet = {}

# dictionary of cellular_component which are not in hetionet with they properties: name
dict_ctd_cellular_component_not_in_hetionet = {}

# dictionary of ctd cellular_component which are in hetionet with properties: name
dict_ctd_cellular_component_in_hetionet = {}

# dictionary of molecular_function which are not in hetionet with they properties: name
dict_ctd_molecular_function_not_in_hetionet = {}

# dictionary of ctd molecular_function which are in hetionet with properties: name
dict_ctd_molecular_function_in_hetionet = {}

# dictionary with for biological_process, cellular_component, molecular_function the right dictionaries
dict_processe = {
    "Biological Process": [dict_biological_process_hetionet, dict_ctd_biological_process_not_in_hetionet,
                           dict_ctd_biological_process_in_hetionet],
    "Molecular Function": [dict_molecular_function_hetionet, dict_ctd_molecular_function_not_in_hetionet,
                           dict_ctd_molecular_function_in_hetionet],
    "Cellular Component": [dict_cellular_component_hetionet, dict_ctd_cellular_component_not_in_hetionet,
                           dict_ctd_cellular_component_in_hetionet]
}

'''
load all ctd genes and check if they are in hetionet or not
'''


def load_ctd_go_in():
    query = '''MATCH (n:CTDGO) RETURN n'''
    results = g.run(query)

    for go_node, in results:
        go_id = go_node['go_id']
        go_name = go_node['name']
        ontology = go_node['ontology']
        highestGOLevel= go_node['highestGOLevel']
        check_if_new_or_part_of_hetionet(ontology,go_id,go_name,highestGOLevel)

    print('number of existing biological process nodes:' + str(len(dict_ctd_biological_process_in_hetionet)))
    print('number of not existing biological process nodes:' + str(len(dict_ctd_biological_process_not_in_hetionet)))

    print('number of existing Molecular Function nodes:' + str(len(dict_ctd_molecular_function_in_hetionet)))
    print('number of not existing Molecular Function nodes:' + str(len(dict_ctd_molecular_function_not_in_hetionet)))

    print('number of existing Cellular Component nodes:' + str(len(dict_ctd_cellular_component_in_hetionet)))
    print('number of not existing Cellular Component nodes:' + str(len(dict_ctd_cellular_component_not_in_hetionet)))


# cypher file to integrate and update the go nodes
cypher_file = open('GO/cypher.cypher', 'w')
# delete all old
query='''begin\n MATCH p=()-[r:equal_to_CTD_go]->() Delete r;\n commit\n'''
cypher_file.write(query)

'''
Generate cypher and csv for generating the new nodes and the relationships
'''


def generate_files(file_name_addition, ontology, dict_not_in_hetionet, dict_ctd_in_hetionet):
    # add the gene which are not in hetionet in a csv file
    with open('GO/new_' + file_name_addition + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['GOID', 'GOName','highestGOLevel'])
        # add the go nodes to cypher file
        for gene_id, [name, highestGOLevel] in dict_not_in_hetionet.items():
            writer.writerow([gene_id, name,highestGOLevel])

    cypher_file.write('begin\n')
    cypher_file.write('Match (c:' + ontology + ') Where not exists(c.hetionet) Set c.hetionet="yes", c.resource=["Hetionet"];\n')
    cypher_file.write('commit\n')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/GO/new_%s.csv" As line Create (c:%s{ identifier:line.GOID, name:line.GOName, url_ctd:" http://ctdbase.org/detail.go?type=go&acc="+line.GOID ,url: "http://amigo.geneontology.org/amigo/term/"+line.GeneID, highestGOLevel:line.highestGOLevel , source:"Gene Ontology" , license:"CC BY 4.0", hetionet:"no", ctd:"yes", resource:["CTD"]});\n'''
    query = query % (file_name_addition, ontology)
    cypher_file.write(query)

    with open('GO/mapping_' + file_name_addition + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GOIDCTD', 'GOIDHetionet', 'highestGOLevel'])
        # add the go nodes to cypher file

        for gene_id, name in dict_ctd_in_hetionet.items():
            writer.writerow([gene_id, gene_id])

        for gene_id, name in dict_not_in_hetionet.items():
            writer.writerow([gene_id, gene_id])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/GO/mapping_%s.csv" As line Match (c:%s{ identifier:line.GOIDHetionet}), (n:CTDGO{go_id:line.GOIDCTD}) SET c.name=n.name, c.url_ctd=" http://ctdbase.org/detail.go?type=go&acc="+line.GOIDCTD, c.url="http://amigo.geneontology.org/amigo/term/"+line.GOIDCTD, c.highestGOLevel=n.highestGOLevel Create (c)-[:equal_to_CTD_go]->(n) With c, n, line Where c.hetionet='yes' and not c.ctd='yes' Set c.resource=c.resource+"CTD", c.ctd="yes", c.highestGOLevel=line.highestGOLevel;\n'''
    query = query % (file_name_addition, ontology)
    cypher_file.write(query)
    cypher_file.write('begin\n')
    query= '''Match (n:%s) Where not exists(n.ctd) Set n.ctd="no";\n'''
    query= query %(ontology)
    cypher_file.write(query)
    cypher_file.write('commit\n')


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all go from hetionet into a dictionary')

    load_hetionet_go_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all ctd go from neo4j into a dictionary')

    load_ctd_go_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map generate csv and cypher file for all three labels ')

    generate_files('bp', 'BiologicalProcess', dict_ctd_biological_process_not_in_hetionet,
                   dict_ctd_biological_process_in_hetionet)

    generate_files('cc', 'CellularComponent', dict_ctd_cellular_component_not_in_hetionet,
                   dict_ctd_cellular_component_in_hetionet)

    generate_files('mf', 'MolecularFunction', dict_ctd_molecular_function_not_in_hetionet,
                   dict_ctd_molecular_function_in_hetionet)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
