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
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global graph_database
    graph_database = Graph("http://localhost:7474/db/data/", auth= ("neo4j", "test"))


# dictionary with hetionet drug with drugbank identifier as key and value the name
dict_drug_hetionet = {}

dict_hetionet = {}

# dictionary with hetionet drug with drugbank identifier as key and value the inchis
dict_hetionet_inchi_drugbank_identifier = {}

# dictionary with hetionet ddrug with name as key and value the identifier
dict_drug_hetionet_names = {}

#dictionary from inchi to identifier
dict_inchi_to_identifier = {}

#dictionary from identifier to resource
dict_identifier_to_resource = {}

#dictionary from inchi to iuphar id
dict_inchi_to_iuphar_id = {}

#dictionary from iuphar_reactome to identifier
dict_iuphar_reactome_to_identifier = {}

dict_iuphar_to_inchi_hetionet = {}

dict_inchiKey_to_iuphar_id = {}

#dictionary from xref (ChEBI) to identifer (DrugBankIdentifier)
dict_identifier_hetionet_xref = {}


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
    query = '''MATCH (n:Chemical) WHERE not n:Product RETURN n.identifier, n.name, n.inchi, n.resource, n.xrefs;'''
    results = graph_database.run(query)

    for hetionet_identifier, name, inchi_hetionet, resource, xrefs, in results:
        dict_drug_hetionet[hetionet_identifier] = name.lower()
        dict_identifier_to_resource[hetionet_identifier] = resource
        dict_hetionet_inchi_drugbank_identifier[inchi_hetionet] = hetionet_identifier

        if inchi_hetionet:
                if not inchi_hetionet in dict_inchi_to_identifier:
                    dict_inchi_to_identifier[inchi_hetionet] = hetionet_identifier
                else:
                    print(inchi_hetionet)

        if name:
            dict_drug_hetionet_names[name.lower()] = hetionet_identifier

        if inchi_hetionet in dict_inchi_to_iuphar_id:
            iuphar = dict_inchi_to_iuphar_id[inchi_hetionet]
            dict_iuphar_to_inchi_hetionet [iuphar] = inchi_hetionet
        # ChEBI mappen
        if xrefs:
            for xref in xrefs:
                if xref.startswith('ChEBI:'):
                    dict_identifier_hetionet_xref[xref] = hetionet_identifier
                elif xref.startswith('KEGG Compound:'):
                    dict_identifier_hetionet_xref[xref] = hetionet_identifier
                elif xref.startswith('PubChem Compound:'):
                    dict_identifier_hetionet_xref[xref] = hetionet_identifier
    print('number of drug nodes in hetionet:' + str(len(dict_drug_hetionet)))



# file for mapped or not mapped identifier
file_not_mapped_drug = open('drug/not_mapped_drug.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_drug,delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id','name'])

file_mapped_drug = open('drug/mapped_drug.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_drug,delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id','id_hetionet', 'resource', 'databaseName'])


'''
load all reactome drug and check if they are in hetionet or not
'''

def load_reactome_drug_in(label):
    global highest_identifier
    set_pair = set()
    query = '''MATCH (n:ReferenceEntity_reactome)--(h:%s) WHERE n.databaseName in [ "ChEBI", "IUPHAR" , "COMPOUND", "PubChem Compound"] RETURN n, h'''
    query = query %(label)
    results = graph_database.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_mapping_with_iuphar = 0
    counter_mapping_with_chebi = 0
    counter_mapping_with_pubchem = 0
    counter_mapping_with_kegg = 0
    mapped = False
    for reference_node, drug_node, in results:
        identifier_reactome = reference_node['identifier']  if "identifier" in reference_node else []
        drug_name = reference_node['inn'].lower() if "inn" in reference_node else reference_node['inn']            #INN - international nonproprietary name
        drug_names = reference_node['name'] if "name" in reference_node else []
        databaseName = reference_node['databaseName'] if "databaseName" in reference_node else []
        displayName = reference_node["displayName"] if "displayName" in reference_node else ""
        alternative_drug_name = drug_node["name"] if "name" in drug_node else []

        # xrefs: add prefixes
        if databaseName == "ChEBI":
            database_identifier = "ChEBI:" + identifier_reactome
        elif databaseName == "COMPOUND":
            database_identifier = "KEGG Compound:" + identifier_reactome
        elif databaseName == "PubChem Compound":
            database_identifier = "PubChem Compound:" + identifier_reactome

        #mapping IUPHAR
        if databaseName == "IUPHAR":
            if identifier_reactome in dict_iuphar_to_inchi_hetionet:
                counter_map_with_id += 1
                counter_mapping_with_iuphar +=1
                hetionet_identifier = dict_hetionet_inchi_drugbank_identifier[dict_iuphar_to_inchi_hetionet[identifier_reactome]]
                resource = dict_identifier_to_resource[hetionet_identifier]
                resource.append('Reactome')
                resource = list(set(resource))
                resource = '|'.join(resource)
                csv_mapped.writerow([identifier_reactome, hetionet_identifier, resource, databaseName])
                mapped = True

        #mapping xrefs: ChEBI, KEGG & PubChem
        elif (databaseName == "ChEBI" or databaseName == "COMPOUND" or databaseName == "PubChem Compound") \
                and database_identifier in dict_identifier_hetionet_xref:
            counter_map_with_id += 1
            if databaseName == "ChEBI":
                counter_mapping_with_chebi += 1
            if databaseName == "COMPOUND":
                counter_mapping_with_kegg += 1
            if databaseName == "PubChem Compound":
                counter_mapping_with_pubchem += 1
            hetionet_identifier = dict_identifier_hetionet_xref[database_identifier]
            resource = dict_identifier_to_resource[hetionet_identifier]
            resource.append('Reactome')
            resource = list(set(resource))
            resource = '|'.join(resource)
            csv_mapped.writerow([identifier_reactome, hetionet_identifier, resource, databaseName])
            mapped = True

        #mapping with name
        elif drug_name in dict_drug_hetionet_names:
            counter_map_with_name += 1
            hetionet_identifier = dict_drug_hetionet_names[drug_name]
            resource = dict_identifier_to_resource[hetionet_identifier]
            resource.append('Reactome')
            resource = list(set(resource))
            resource = '|'.join(resource)
            drug_names = dict_drug_hetionet[dict_drug_hetionet_names[drug_name]]
            csv_mapped.writerow([identifier_reactome, hetionet_identifier, resource, drug_name, drug_names, "NAME"])
            mapped = True

        #mapping with alternative_names
        if not mapped:
            #counter_map_with_name += 1
            for name in alternative_drug_name:
                if name in dict_drug_hetionet_names:
                    counter_map_with_name += 1
                    hetionet_identifier = dict_drug_hetionet_names[drug_name]
                    resource = dict_identifier_to_resource[hetionet_identifier]
                    resource.append('Reactome')
                    resource = list(set(resource))
                    resource = '|'.join(resource)
                    drug_names = dict_drug_hetionet[dict_drug_hetionet_names[drug_name]]
                    csv_mapped.writerow([identifier_reactome, hetionet_identifier, resource, drug_name, drug_names, "NAME_DRUG"])
                    mapped = True


        #html-exceptions in reactome
        if len(drug_names)>0 and not mapped:
            mapped = False
            for name in drug_names:
                if name == 'IFN-&beta;1a (recombinant human)':                                  # IUPHAR:8339; DB00060
                    name = name.replace("IFN-&beta;1a (recombinant human)", "Interferon beta-1a")
                if name == 'IFN-&beta;1b (recombinant human)':                                  # IUPHAR:8340; DB00068
                    name = name.replace("IFN-&beta;1b (recombinant human)", "Interferon beta-1b")
                if name == 'Li<sup>+</sup>':                                                    # IUPHAR:5212; DB01356
                    name = name.replace("Li<sup>+</sup>", "Lithium cation")
                name = name.lower()
                if name in dict_drug_hetionet_names:
                    mapped = True
                    counter_map_with_name += 1
                    hetionet_identifier = dict_drug_hetionet_names[name]
                    if (hetionet_identifier,identifier_reactome) in set_pair:
                        continue
                    resource = dict_identifier_to_resource[hetionet_identifier]
                    resource.append('Reactome')
                    resource = list(set(resource))
                    resource = '|'.join(resource)
                    drug_names = dict_drug_hetionet[dict_drug_hetionet_names[name]]
                    csv_mapped.writerow([identifier_reactome, hetionet_identifier, resource, name, drug_names, "NAME"])
                    mapped = True
                    set_pair.add((hetionet_identifier,identifier_reactome))
            if not mapped:
                csv_not_mapped.writerow([identifier_reactome, drug_name, drug_names, databaseName])
        else:
            csv_not_mapped.writerow([identifier_reactome, drug_name, drug_names, databaseName])

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('number of mapping with IUPHAR-ID: ' + str(counter_mapping_with_iuphar))
    print('number of mapping with KEGG-ID: ' + str(counter_mapping_with_kegg))
    print('number of mapping with ChEBI-ID : ' + str(counter_mapping_with_chebi))
    print('number of mapping with PubChem Compound-ID: ' + str(counter_mapping_with_pubchem))

'''
generate connection between mapping drug of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''

def create_cypher_file():
    cypher_file = open('output/cypher_mapping2.cypher','w', encoding="utf-8")
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/drug/mapped_drug.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Chemical{identifier:line.id_hetionet}),(c:ReferenceEntity_reactome{identifier:line.id}) CREATE (d)-[: equal_to_reactome_drug]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query=query %(path_of_directory)
    cypher_file.write(query)

    # cypher_file.write(':begin\n')
    # query = '''MATCH (d:ReferenceEntity_reactome) WHERE NOT  exists(d.reactome) SET d.reactome="no";\n '''
    # cypher_file.write(query)
    # cypher_file.write(':commit\n')

def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome drug')
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()
    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.utcnow())
    print('Load all iuphar ids into a dictionary')

    load_iuphar_ids_in()

    print(
        '_.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')

    print (datetime.datetime.utcnow())
    print('Load all drugs from hetionet into a dictionary')

    load_hetionet_drug_in()


    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print (datetime.datetime.utcnow())
    print('Load all reactome drug from neo4j into a dictionary')

    for label in ["Drug_reactome", "PhysicalEntity_reactome"]:
        load_reactome_drug_in(label)


    print(
        '_.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')

    print (datetime.datetime.utcnow())
    print('Integrate new drug and connect them to reactome ')

    create_cypher_file()

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
