# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph
import datetime
import csv
import sys
import html

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet drug with drugbank identifier as key and value the name
dict_drug_hetionet = {}

# dictionary with hetionet drug with drugbank identifier as key and value the inchis
dict_hetionet_inchi_drugbank_identifier = {}

# dictionary with hetionet ddrug with name as key and value the identifier
dict_drug_hetionet_names = {}

# dictionary from inchi to identifier
dict_inchi_to_identifier = {}

# dictionary from identifier to resource
dict_identifier_to_resource = {}

# dictionary from inchi to iuphar id
dict_inchi_to_iuphar_id = {}

# dictionary from iuphar_reactome to identifier
dict_iuphar_reactome_to_identifier = {}

dict_iuphar_to_inchi_hetionet = {}

dict_inchiKey_to_iuphar_id = {}

'''
load all iuphar ids and check if they are in hetionet or not
'''


def load_iuphar_ids_in():
    with open('IUPHAR/ligands.csv', newline='', encoding="utf-8") as csvfile:
        iuphar_and_inchi = csv.DictReader(csvfile, delimiter=',')
        for row in iuphar_and_inchi:
            iuphar_id = row['Ligand id']
            inchi_iuphar = row['InChI']
            inchiKey_iuphar = row['InChIKey']
            dict_inchi_to_iuphar_id[inchi_iuphar] = iuphar_id
            dict_inchiKey_to_iuphar_id[inchiKey_iuphar] = iuphar_id


'''
load in all disease from hetionet in a dictionary
'''


def load_hetionet_drug_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.inchi, n.resource;'''
    results = graph_database.run(query)

    for identifier, name, inchi_hetionet, resource, in results:
        dict_drug_hetionet[identifier] = name.lower()
        dict_identifier_to_resource[identifier] = resource
        dict_hetionet_inchi_drugbank_identifier[inchi_hetionet] = identifier
        if inchi_hetionet:
            if not inchi_hetionet in dict_inchi_to_identifier:
                dict_inchi_to_identifier[inchi_hetionet] = identifier
            else:
                print(inchi_hetionet)

        if name:
            dict_drug_hetionet_names[name.lower()] = identifier

        if inchi_hetionet in dict_inchi_to_iuphar_id:
            iuphar = dict_inchi_to_iuphar_id[inchi_hetionet]
            dict_iuphar_to_inchi_hetionet[iuphar] = inchi_hetionet

    print('number of drug nodes in hetionet:' + str(len(dict_drug_hetionet)))


# file for mapped or not mapped identifier
file_not_mapped_drug = open('drug/not_mapped_drug.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_drug, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])

file_mapped_drug = open('drug/mapped_drug.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_drug, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_hetionet', 'resource'])

'''
load all reactome drug and check if they are in hetionet or not
'''


def load_reactome_drug_in():
    global highest_identifier
    set_pair = set()
    query = '''MATCH (n:ReferenceTherapeutic_reactome) RETURN n'''
    results = graph_database.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_not_mapped = 0
    for drug_node, in results:
        iuphar_reactome = drug_node['identifier']  # IUPHAR ID
        # print(iuphar_reactome+"blub")
        drug_name = drug_node['inn'].lower() if "inn" in drug_node else drug_node[
            'inn']  # INN - international nonproprietary name
        drug_names = drug_node['name'] if "name" in drug_node else []

        if iuphar_reactome in dict_iuphar_to_inchi_hetionet:
            counter_map_with_id += 1
            hetionet_identifier = dict_hetionet_inchi_drugbank_identifier[
                dict_iuphar_to_inchi_hetionet[iuphar_reactome]]
            resource = dict_identifier_to_resource[hetionet_identifier]
            resource.append('Reactome')
            resource = list(set(resource))
            resource = '|'.join(resource)
            csv_mapped.writerow([iuphar_reactome, hetionet_identifier, resource])

        # mapping nach dem Namen
        elif drug_name in dict_drug_hetionet_names:
            counter_map_with_name += 1
            hetionet_identifier = dict_drug_hetionet_names[drug_name]
            resource = dict_identifier_to_resource[hetionet_identifier]
            resource.append('Reactome')
            resource = list(set(resource))
            resource = '|'.join(resource)
            drug_names = dict_drug_hetionet[dict_drug_hetionet_names[drug_name]]
            csv_mapped.writerow([iuphar_reactome, hetionet_identifier, resource, drug_name, drug_names])

        elif len(drug_names) > 0:
            mapped = False
            for name in drug_names:
                if name == 'IFN-&beta;1a (recombinant human)':  # IUPHAR:8339; DB00060
                    name = name.replace("IFN-&beta;1a (recombinant human)", "Interferon beta-1a")
                if name == 'IFN-&beta;1b (recombinant human)':  # IUPHAR:8340; DB00068
                    name = name.replace("IFN-&beta;1b (recombinant human)", "Interferon beta-1b")
                if name == 'Li<sup>+</sup>':  # IUPHAR:5212; DB01356
                    name = name.replace("Li<sup>+</sup>", "Lithium cation")
                name = name.lower()
                if name in dict_drug_hetionet_names:
                    mapped = True
                    counter_map_with_name += 1
                    hetionet_identifier = dict_drug_hetionet_names[name]
                    if (hetionet_identifier, iuphar_reactome) in set_pair:
                        continue
                    resource = dict_identifier_to_resource[hetionet_identifier]
                    resource.append('Reactome')
                    resource = list(set(resource))
                    resource = '|'.join(resource)
                    drug_names = dict_drug_hetionet[dict_drug_hetionet_names[name]]
                    csv_mapped.writerow([iuphar_reactome, hetionet_identifier, resource, name, drug_names])
                    set_pair.add((hetionet_identifier, iuphar_reactome))
            if not mapped:
                csv_not_mapped.writerow([iuphar_reactome, drug_names])
                counter_not_mapped += 1
        else:
            csv_not_mapped.writerow([iuphar_reactome, drug_name, drug_names])
            counter_not_mapped += 1

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('Number of not mapped drugs:', counter_not_mapped)


'''
generate connection between mapping drug of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/drug/mapped_drug.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Compound{identifier:line.id_hetionet}),(c:ReferenceTherapeutic_reactome{identifier:line.id}) CREATE (d)-[: equal_to_reactome_drug]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)

    # cypher_file.write(':begin\n')
    # query = '''MATCH (d:ReferenceTherapeutic_reactome) WHERE NOT  exists(d.reactome) SET d.reactome="no";\n '''
    # cypher_file.write(query)
    # cypher_file.write(':commit')


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome drug')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all iuphar ids into a dictionary')

    load_iuphar_ids_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all drugs from hetionet into a dictionary')

    load_hetionet_drug_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all reactome drug from neo4j into a dictionary')

    load_reactome_drug_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Integrate new drug and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
