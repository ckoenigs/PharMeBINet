import datetime
import csv
import sys
import ast

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary with pharmebinet drug with drugbank identifier as key and value the name
dict_drug_pharmebinet = {}

dict_pharmebinet = {}

# dictionary with pharmebinet drug with drugbank identifier as key and value the inchis
dict_pharmebinet_inchi_drugbank_identifier = {}

# dictionary with pharmebinet ddrug with name as key and value the identifier
dict_drug_pharmebinet_names = {}

# dictionary from inchi to identifier
dict_inchi_to_identifier = {}

# dictionary from identifier to resource
dict_identifier_to_resource = {}

# dictionary from inchi to iuphar id
dict_inchi_to_iuphar_id = {}

# dictionary from iuphar_reactome to identifier
dict_iuphar_reactome_to_identifier = {}

dict_iuphar_to_inchi_pharmebinet = {}

dict_inchiKey_to_iuphar_id = {}

# dictionary from xref (ChEBI) to identifer (DrugBankIdentifier)
dict_identifier_pharmebinet_xref = {}

'''
load all iuphar ids and check if they are in pharmebinet or not 
'''


def load_iuphar_ids_in():
    with open('IUPHAR/ligands.csv', newline='', encoding="utf-8") as csvfile:
        iuphar_and_inchi = csv.DictReader(csvfile, delimiter=',')
        for row in iuphar_and_inchi:
            iuphar_id = row['Ligand ID']
            inchi_iuphar = row['InChI']
            inchiKey_iuphar = row['InChIKey']
            dict_inchi_to_iuphar_id[inchi_iuphar] = iuphar_id
            dict_inchiKey_to_iuphar_id[inchiKey_iuphar] = iuphar_id


'''
load in all disease from pharmebinet in a dictionary
'''


def load_pharmebinet_drug_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.name, n.inchi, n.resource, n.xrefs;'''
    results = graph_database.run(query)

    for record in results:
        [pharmebinet_identifier, name, inchi_pharmebinet, resource, xrefs] = record.values()
        dict_drug_pharmebinet[pharmebinet_identifier] = name.lower()
        dict_identifier_to_resource[pharmebinet_identifier] = resource
        dict_pharmebinet_inchi_drugbank_identifier[inchi_pharmebinet] = pharmebinet_identifier

        if inchi_pharmebinet:
            if not inchi_pharmebinet in dict_inchi_to_identifier:
                dict_inchi_to_identifier[inchi_pharmebinet] = pharmebinet_identifier
            else:
                print(inchi_pharmebinet)

        if name:
            dict_drug_pharmebinet_names[name.lower()] = pharmebinet_identifier

        if inchi_pharmebinet in dict_inchi_to_iuphar_id:
            iuphar = dict_inchi_to_iuphar_id[inchi_pharmebinet]
            dict_iuphar_to_inchi_pharmebinet[iuphar] = inchi_pharmebinet
        # ChEBI, KEGG, PubChem mappen
        if xrefs:
            for xref in xrefs:
                if xref.startswith('ChEBI:'):
                    dict_identifier_pharmebinet_xref[xref] = pharmebinet_identifier
                elif xref.startswith('KEGG Compound:'):
                    dict_identifier_pharmebinet_xref[xref] = pharmebinet_identifier
                elif xref.startswith('PubChem Compound:'):
                    dict_identifier_pharmebinet_xref[xref] = pharmebinet_identifier
    print('number of drug nodes in pharmebinet:' + str(len(dict_drug_pharmebinet)))


# file for mapped or not mapped identifier
file_not_mapped_drug = open('drug/not_mapped_drug.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_drug, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id', 'name'])

file_mapped_drug = open('drug/mapped_drug.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_drug, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_pharmebinet', 'resource', 'how_mapped', 'databaseName'])

'''
load all reactome drug and check if they are in pharmebinet or not
'''

set_pair = set()


def load_reactome_drug_in(label):
    global highest_identifier
    query = '''MATCH (n:ReferenceEntity_reactome)--(h:%s) WHERE n.databaseName in [ "ChEBI", "IUPHAR" , "COMPOUND", "PubChem Compound", "Guide to Pharmacology"] RETURN n, h'''
    query = query % (label)
    results = graph_database.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    for record in results:
        [reference_node, drug_node] = record.values()
        mapped = False
        identifier_reactome = reference_node['identifier'] if "identifier" in reference_node else []
        drug_name = reference_node['inn'].lower() if "inn" in reference_node else ''
        drug_names = ast.literal_eval(reference_node['name']) if "name" in reference_node else []
        databaseName = reference_node['databaseName'] if "databaseName" in reference_node else []
        alternative_drug_name = ast.literal_eval(drug_node["name"]) if "name" in drug_node else []
        dbId = reference_node["dbId"]

        # xrefs: add prefixess
        if databaseName == "ChEBI":
            database_identifier = "ChEBI:" + identifier_reactome
        elif databaseName == "COMPOUND":
            database_identifier = "KEGG Compound:" + identifier_reactome
        elif databaseName == "PubChem Compound":
            database_identifier = "PubChem Compound:" + identifier_reactome

        # mapping IUPHAR
        if databaseName == "IUPHAR" or databaseName == 'Guide to Pharmacology':
            if identifier_reactome in dict_iuphar_to_inchi_pharmebinet:
                pharmebinet_identifier = dict_pharmebinet_inchi_drugbank_identifier[
                    dict_iuphar_to_inchi_pharmebinet[identifier_reactome]]
                if (pharmebinet_identifier, dbId) in set_pair:
                    continue
                counter_map_with_id += 1
                csv_mapped.writerow([dbId, pharmebinet_identifier, pharmebinetutils.resource_add_and_prepare(
                    dict_identifier_to_resource[pharmebinet_identifier], 'Reactome'), 'IUPHAR', drug_name,
                                     databaseName])
                mapped = True
                set_pair.add((pharmebinet_identifier, dbId))


        # mapping:  PubChem-direct identifier
        elif (databaseName == "PubChem Compound") \
                and identifier_reactome in dict_identifier_to_resource:
            if (identifier_reactome, dbId) in set_pair:
                continue
            counter_map_with_id += 1
            csv_mapped.writerow([dbId, identifier_reactome, pharmebinetutils.resource_add_and_prepare(
                dict_identifier_to_resource[identifier_reactome], 'Reactome'), 'direct_pubchem', drug_name,
                                 databaseName])
            mapped = True
            set_pair.add((identifier_reactome, dbId))


        # mapping xrefs: ChEBI, KEGG & PubChem
        elif (databaseName == "ChEBI" or databaseName == "COMPOUND" or databaseName == "PubChem Compound") \
                and database_identifier in dict_identifier_pharmebinet_xref:
            pharmebinet_identifier = dict_identifier_pharmebinet_xref[database_identifier]
            if (pharmebinet_identifier, dbId) in set_pair:
                continue
            counter_map_with_id += 1
            csv_mapped.writerow([dbId, pharmebinet_identifier, pharmebinetutils.resource_add_and_prepare(
                dict_identifier_to_resource[pharmebinet_identifier], 'Reactome'), databaseName, drug_name,
                                 databaseName])
            mapped = True
            set_pair.add((pharmebinet_identifier, dbId))


        # mapping with name
        if drug_name in dict_drug_pharmebinet_names and not mapped:
            pharmebinet_identifier = dict_drug_pharmebinet_names[drug_name]
            if (pharmebinet_identifier, dbId) in set_pair:
                continue
            counter_map_with_name += 1
            drug_names = dict_drug_pharmebinet[dict_drug_pharmebinet_names[drug_name]]
            csv_mapped.writerow([dbId, pharmebinet_identifier, pharmebinetutils.resource_add_and_prepare(
                dict_identifier_to_resource[pharmebinet_identifier], 'Reactome'), "NAME", drug_name, drug_names])
            mapped = True
            set_pair.add((pharmebinet_identifier, dbId))

        # mapping with alternative_names
        if not mapped:
            for name in alternative_drug_name:
                name = name.lower()
                if name in dict_drug_pharmebinet_names:
                    pharmebinet_identifier = dict_drug_pharmebinet_names[name]
                    if (pharmebinet_identifier, dbId) in set_pair:
                        continue
                    counter_map_with_name += 1
                    drug_names = dict_drug_pharmebinet[dict_drug_pharmebinet_names[name]]
                    csv_mapped.writerow([dbId, pharmebinet_identifier, pharmebinetutils.resource_add_and_prepare(
                        dict_identifier_to_resource[pharmebinet_identifier], 'Reactome'), "NAME_DRUG", name,
                                         drug_names])
                    mapped = True
                    set_pair.add((pharmebinet_identifier, dbId))

        # html-exceptions in reactome
        if len(drug_names) > 0 and not mapped:
            for name in drug_names:
                if name == 'IFN-&beta;1a (recombinant human)':  # IUPHAR:8339; DB00060
                    name = name.replace("IFN-&beta;1a (recombinant human)", "Interferon beta-1a")
                if name == 'IFN-&beta;1b (recombinant human)':  # IUPHAR:8340; DB00068
                    name = name.replace("IFN-&beta;1b (recombinant human)", "Interferon beta-1b")
                if name == 'Li<sup>+</sup>':  # IUPHAR:5212; DB01356
                    name = name.replace("Li<sup>+</sup>", "Lithium cation")
                name = name.lower()
                if name in dict_drug_pharmebinet_names:
                    pharmebinet_identifier = dict_drug_pharmebinet_names[name]
                    if (pharmebinet_identifier, dbId) in set_pair:
                        continue
                    counter_map_with_name += 1
                    drug_names = dict_drug_pharmebinet[dict_drug_pharmebinet_names[name]]
                    csv_mapped.writerow([dbId, pharmebinet_identifier, pharmebinetutils.resource_add_and_prepare(
                        dict_identifier_to_resource[pharmebinet_identifier], 'Reactome'), "NAME_HTML", drug_name,
                                         drug_names])
                    mapped = True
                    set_pair.add((pharmebinet_identifier, dbId))

            if not mapped:
                csv_not_mapped.writerow([identifier_reactome, drug_name, drug_names, databaseName])
        if not mapped:
            csv_not_mapped.writerow([identifier_reactome, drug_name, drug_names, databaseName])

    print('----------------------------------------------------------------------------------------')
    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('----------------------------------------------------------------------------------------')


'''
generate connection between mapping drug of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher_mapping2.cypher', 'w', encoding="utf-8")
    query = ''' MATCH (d:Chemical{identifier:line.id_pharmebinet}),(c:ReferenceEntity_reactome{dbId:toInteger(line.id)}) CREATE (d)-[:equal_to_reactome_drug{how_mapped:line.how_mapped}]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/reactome/drug/mapped_drug.tsv',
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome drug')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()
    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())
    print('Load all iuphar ids into a dictionary')

    load_iuphar_ids_in()

    print(
        '__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')

    print(datetime.datetime.now())
    print('Load all drugs from pharmebinet into a dictionary')

    load_pharmebinet_drug_in()

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())
    print('Load all reactome drug from neo4j into a dictionary')

    for label in ["Drug_reactome", "PhysicalEntity_reactome"]:
        load_reactome_drug_in(label)

    print(
        '__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')

    print(datetime.datetime.now())
    print('Integrate new drug and connect them to reactome ')

    create_cypher_file()

    driver.close()

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
