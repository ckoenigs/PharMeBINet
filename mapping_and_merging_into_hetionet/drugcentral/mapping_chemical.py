from py2neo import Graph
import datetime
import csv
import sys
import html
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()




dict_chemical_to_resource = {}
dict_chemical_inchi = {}
dict_chemical_inchikey = {}
dict_chemical_name = {}
dict_chemical_smiles = {}
dict_chemical_rxrNorm ={}
dict_chemical_chembl = {}
dict_chemical_kegg = {}
dict_chemical_chebi = {}
dict_chemical_pubChem = {}





def load_chemicals_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.inchikey, n.name, n.smiles, n.resource, n.xrefs'''
    results = graph_database.run(query)

    for identifier, inchikey, name, smiles, resource, xrefs, in results:
        dict_chemical_to_resource[identifier] = resource


        if inchikey:
            if inchikey not in dict_chemical_inchi:
                dict_chemical_inchikey[inchikey] = set()
            dict_chemical_inchikey[inchikey].add(identifier)

        if name:
            name = name.lower()
            if name not in dict_chemical_name:
                dict_chemical_name[name] = set()
            dict_chemical_name[name].add(identifier)

        if xrefs:
            for ref in xrefs:
                # RxRNorm
                if ref.startswith("RxNorm_CUI"):
                    rxrNorm_ref = ref.split(':')
                    if rxrNorm_ref[1] not in dict_chemical_rxrNorm:
                        dict_chemical_rxrNorm[rxrNorm_ref[1]] = set()
                    dict_chemical_rxrNorm[rxrNorm_ref[1]].add(identifier)

                if ref.startswith("ChEBI"):
                    chebi_ref = ref.split(':')
                    if chebi_ref[1] not in dict_chemical_chebi:
                        dict_chemical_chebi[chebi_ref[1]] = set()
                    dict_chemical_chebi[chebi_ref[1]].add(identifier)

                if ref.startswith("ChEMBL"):
                    chembl_ref = ref.split(':')
                    if chembl_ref[1] not in dict_chemical_chembl:
                        dict_chemical_chembl[chembl_ref[1]] = set()
                    dict_chemical_chembl[chembl_ref[1]].add(identifier)

                if ref.startswith("KEGG"):
                    kegg_ref = ref.split(':')
                    if kegg_ref[1] not in dict_chemical_kegg:
                        dict_chemical_kegg[kegg_ref[1]] = set()
                    dict_chemical_kegg[kegg_ref[1]].add(identifier)

                if ref.startswith("PubChem"):
                    pubChem_ref = ref.split(':')
                    if  pubChem_ref[1] not in dict_chemical_pubChem:
                        dict_chemical_pubChem[ pubChem_ref[1]] = set()
                    dict_chemical_pubChem[ pubChem_ref[1]].add(identifier)



        # geht nicht, es kann nicht auf smiles zugegriffen werden
        if smiles:
            print(smiles)
            smile = smiles.split('::')
            if smile[1] not in dict_chemical_smiles:
                dict_chemical_smiles[smile[1]] = set()
            dict_chemical_smiles[smile[1]].add(identifier)




dict_structureID_to_xref = defaultdict(lambda: defaultdict(set))
def load_structure_external_ref_in():
    query = '''MATCH (n:DC_Identifier)--(m:DC_Structure) RETURN id(m), n.type, n.identifier'''
    results = graph_database.run(query)

    for structure_id, xref_type, xref_identifier, in results:
        dict_structureID_to_xref[structure_id][xref_type].add(xref_identifier)


def load_structure_in():
    query = '''MATCH (n:DC_Structure) RETURN id(n), n.inchikey, n.smiles, n.name, n.resource'''
    results = graph_database.run(query)

    mapped_chemicals = set()
    dict_nodes_to_chemical = {}
    dict_node_to_methode = {}

    for identifier, inchikey, smiles, name, resource, in results:

        # #inchi
        # if inchi:
        #     # inchis = inchi.split('=', 1)
        #     if inchi in dict_chemical_inchi:
        #         chemicals = dict_chemical_inchi[inchi]
        #         for chemical_id in chemicals:
        #             dict_nodes_to_chemical[identifier] = chemical_id
        #
        #             if identifier not in dict_node_to_methode:
        #                 dict_node_to_methode[identifier] = set()
        #             dict_node_to_methode[identifier].add('inchi')
        #             mapped_chemicals.add(identifier)

        #inchikey
        if inchikey in dict_chemical_inchikey:
            chemicals = dict_chemical_inchikey[inchikey]
            for chemical_id in chemicals:
                dict_nodes_to_chemical[identifier] = chemical_id

                if identifier not in dict_node_to_methode:
                    dict_node_to_methode[identifier] = set()
                dict_node_to_methode[identifier].add('inchikey')
                mapped_chemicals.add(identifier)

        #smiles
        if smiles in dict_chemical_smiles:
            chemicals = dict_chemical_smiles[smiles]
            for chemical_id in chemicals:
                dict_nodes_to_chemical[identifier] = chemical_id

                if identifier not in dict_node_to_methode:
                    dict_node_to_methode[identifier] = set()
                dict_node_to_methode[identifier].add('smiles')
                mapped_chemicals.add(identifier)

        #name

        name = name.lower()
        if name == "tryparsamide":
            print("****")
        if name in dict_chemical_name:
            chemicals = dict_chemical_name[name]
            for chemical_id in chemicals:
                dict_nodes_to_chemical[identifier] = chemical_id

                if identifier not in dict_node_to_methode:
                    dict_node_to_methode[identifier] = set()
                dict_node_to_methode[identifier].add('name')
                mapped_chemicals.add(identifier)

        # xref
        xrefs = dict_structureID_to_xref[identifier]
        for xref in xrefs:


            if xref == 'DRUGBANK_ID':
                drugBank_ids = dict_structureID_to_xref[identifier][xref]
                for drugBank_id in drugBank_ids:
                    if drugBank_id in dict_chemical_to_resource:
                        dict_nodes_to_chemical[identifier] = drugBank_id
                        if identifier not in dict_node_to_methode:
                            dict_node_to_methode[identifier] = set()
                        dict_node_to_methode[identifier].add('DB_id')
                        mapped_chemicals.add(identifier)

            if xref == 'RXNORM':
                rxrnorm_ids = dict_structureID_to_xref[identifier][xref]
                for rxrnorm_id in rxrnorm_ids:
                    if rxrnorm_id in dict_chemical_rxrNorm:
                        chemicals = dict_chemical_rxrNorm[rxrnorm_id]
                        for chemical_id in chemicals:
                            dict_nodes_to_chemical[identifier] = chemical_id

                            if identifier not in dict_node_to_methode:
                                dict_node_to_methode[identifier] = set()
                            dict_node_to_methode[identifier].add('rxrnorm')
                            mapped_chemicals.add(identifier)


            if xref == "CHEBI":
                #print("*****")
                chebi_ids = dict_structureID_to_xref[identifier][xref]
                for chebi_id in chebi_ids:
                    if chebi_id in dict_chemical_chebi:
                        print("*******")
                        chemicals = dict_chemical_chebi[chebi_id]
                        for chemical_id in chemicals:
                            dict_nodes_to_chemical[identifier] = chemical_id

                            if identifier not in dict_node_to_methode:
                                dict_node_to_methode[identifier] = set()
                            dict_node_to_methode[identifier].add('chebi')
                            mapped_chemicals.add(identifier)

            if xref == "KEGG_DRUG":
                kegg_ids = dict_structureID_to_xref[identifier][xref]
                for kegg_id in kegg_ids:
                    if kegg_id in dict_chemical_kegg:
                        chemicals = dict_chemical_kegg[kegg_id]
                        for chemical_id in chemicals:
                            dict_nodes_to_chemical[identifier] = chemical_id

                            if identifier not in dict_node_to_methode:
                                dict_node_to_methode[identifier] = set()
                            dict_node_to_methode[identifier].add('kegg')
                            mapped_chemicals.add(identifier)

            if xref == 'ChEMBL_ID':
                chembl_ids = dict_structureID_to_xref[identifier][xref]
                for chembl_id in chembl_ids:
                    if chembl_id in dict_chemical_chembl:
                        chemicals = dict_chemical_chembl[chembl_id]
                        for chemical_id in chemicals:
                            dict_nodes_to_chemical[identifier] = chemical_id

                            if identifier not in dict_node_to_methode:
                                dict_node_to_methode[identifier] = set()
                            dict_node_to_methode[identifier].add('chembl')
                            mapped_chemicals.add(identifier)


            if xref == 'PUBCHEM_CID':
                pubChem_ids = dict_structureID_to_xref[identifier][xref]
                for pubChem_id in pubChem_ids:
                    if pubChem_id in dict_chemical_pubChem:
                        chemicals = dict_chemical_pubChem[pubChem_id]
                        for chemical_id in chemicals:
                            dict_nodes_to_chemical[identifier] = chemical_id

                            if identifier not in dict_node_to_methode:
                                dict_node_to_methode[identifier] = set()
                            dict_node_to_methode[identifier].add('pubChem')
                            mapped_chemicals.add(identifier)

        if identifier not in mapped_chemicals:
            csv_not_mapped.writerow([identifier,inchikey, name])

        # if identifier in mapped_chemicals:
        #     print(identifier)

    for chem_id in mapped_chemicals:
        methodes = list(dict_node_to_methode[chem_id])
        chemical_id = dict_nodes_to_chemical[chem_id]
        resource = set(dict_chemical_to_resource[chemical_id])
        resource.add('DrugCentral')
        resource = '|'.join(resource)
        csv_mapped_chemical.writerow([identifier, chemical_id, resource, methodes])





# file for mapped or not mapped identifier
#erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_chemical = open('chemical/not_mapped_chemical.tsv', 'w', encoding="utf-8")
#Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_chemical,delimiter='\t', lineterminator='\n')
#Header setzen
csv_not_mapped.writerow(['id', 'inchikey', 'name'])
file_mapped_chemical = open('chemical/mapped_chemical.tsv', 'w', encoding="utf-8")
csv_mapped_chemical = csv.writer(file_mapped_chemical,delimiter='\t', lineterminator='\n')
csv_mapped_chemical.writerow(['node_id','id_hetionet', 'resource', 'how_mapped'])




def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w')
    # es gibt keine mappings zu Chemical, daher ist der cypher file nur für Pharmacological class erstellt
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugcentral/chemical/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:DC_Structure), (c:Chemical{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_Structure_drugcentral{how_mapped:line.how_mapped}]->(n); \n'''
    query = query % (path_of_directory,file_name)
    cypher_file.write(query)
    cypher_file.close()





def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral chemical')
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()
    print("load chemicals in")
    load_chemicals_in()

    print('xref in')
    load_structure_external_ref_in()

    print("load structure in")
    load_structure_in()

    generate_cypher_file('mapped_chemical.tsv')


    print(
        '###########################################################################################################################')


    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()