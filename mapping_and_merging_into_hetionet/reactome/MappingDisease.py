# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet disease with identifier as key and value the name
dict_disease_hetionet = {}

# dictionary with hetionet disease with identifier as key and value the xrefs
dict_disease_hetionet_xrefs = {}

# dictionary with hetionet disease with name as key and value the identifier
dict_disease_hetionet_names = {}

#dictionary from own id to new identifier
dict_doid_id_to_identifier = {}

#dictionary from pathway_id to resource
dict_diseaseId_to_resource = {}

'''
load in all disease from hetionet in a dictionary
'''


def load_hetionet_disease_in():
    #query ist ein String
    query = '''MATCH (n:Disease) RETURN n.identifier, n.name, n.doids, n.resource'''
    #Where not (n:ExternalOntology)
    #graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    #n.synonyms als liste durchlaufen und vergleichen um letzten Hit noch zu bekommen?!
    results = graph_database.run(query)

    #results werden einzeln durchlaufen
    for identifier, name, doids, resource, in results:
        # if identifier == "MONDO:0005244":
        #     print("Egal was")
        #im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        dict_disease_hetionet[identifier] = name
        dict_diseaseId_to_resource[identifier] = resource
        dict_disease_hetionet_xrefs[identifier] = doids
        if doids:
            #geht die Liste idOwns in neo4j durch und baut das dictionary auf an identifiern (von externen Identifier ist idOwn
            for doid in doids:
                #if-scheife kann auch gelöscht werden, wenn niemals der else-Fall eintritt
                if not doid in dict_doid_id_to_identifier:
                    doid = doid.replace("DOID:", "")
                    dict_doid_id_to_identifier[doid] = identifier
                else:
                    print(doid)

        if name:
            dict_disease_hetionet_names[name.lower()] = identifier

    print('number of disease nodes in hetionet:' + str(len(dict_disease_hetionet)))

# file for mapped or not mapped identifier
#erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
#Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_disease,delimiter='\t', lineterminator='\n')
#Header setzen
csv_not_mapped.writerow(['id','name'])

file_mapped_disease = open('disease/mapped_disease.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_disease,delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id','id_hetionet', 'resource', 'reactome_name','pathway_name'])

'''
load all reatome disease and check if they are in hetionet or not
'''


def load_reactome_disease_in():
    global highest_identifier
    query = '''MATCH (n:Disease_reactome) RETURN n'''
    results = graph_database.run(query)

    #zähler wie oft id mapt und und oft der name mapt
    counter_map_with_id = 0
    counter_map_with_name = 0
    for disease_node, in results:
        disease_id = disease_node['identifier']
        if disease_id=='104':
            print('huh')
        disease_name = disease_node['displayName'].lower()
        # if disease_id == "0060053":
        #     print("Egal was 2")
        # check if the reactome pathway id is part in the hetionet idOwn
        #mapping nach dem identifier
        if disease_id in dict_doid_id_to_identifier:
            counter_map_with_id += 1
            disease_names = dict_disease_hetionet[dict_doid_id_to_identifier[disease_id]]
            #PC_11_Zahl Nummer wird im Dictionary nachgeschaut
            hetionet_identifier=dict_doid_id_to_identifier[disease_id]
            #Liste von idOwns wird nach dem PC_11_Zahl durchsucht und als String aneinandergehängt (join)
            #als Trennungssymbol wird | genutzt
            resource = set(dict_diseaseId_to_resource[hetionet_identifier])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            csv_mapped.writerow([disease_id, hetionet_identifier, resource])

        #mapping nach dem Namen
        elif disease_name in dict_disease_hetionet_names:
            counter_map_with_name += 1
            print(disease_id)
            print('mapped with name')
            print(dict_disease_hetionet_names[disease_name])
            print(disease_name)
            hetionet_identifier = dict_disease_hetionet_names[disease_name]
            resource = set(dict_diseaseId_to_resource[hetionet_identifier])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            disease_names = dict_disease_hetionet[dict_disease_hetionet_names[disease_name]]
            csv_mapped.writerow([disease_id,hetionet_identifier, resource, disease_name,disease_names ])

        #übrige Knoten, die nicht mappen, werden neu erstellt und bekommen neuen Identifier PC_11_Zahl
        #dafür braucht man die höchte Zahl +1, damit keiner überschrieben wird
        else:
            csv_not_mapped.writerow([disease_id, disease_name])

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))

'''
generate connection between mapping disease of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    #mappt die Knoten, die es in hetionet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/disease/mapped_disease.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Disease{identifier:line.id_hetionet}),(c:Disease_reactome{identifier:line.id}) CREATE (d)-[: equal_to_reactome_disease]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query= query % (path_of_directory)
    cypher_file.write(query)


    # cypher_file.write(':begin\n')
    # query = '''MATCH (d:Disease_reactome) WHERE NOT  exists(d.reactome) SET d.reactome="no";\n '''
    # cypher_file.write(query)
    # cypher_file.write(':commit\n')

def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all disease from hetionet into a dictionary')

    load_hetionet_disease_in()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all reactome disease from neo4j into a dictionary')

    load_reactome_disease_in()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Integrate new disease and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
