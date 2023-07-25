import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


dict_chemical_to_resource = {}
dict_chemical_inchi = {}
dict_chemical_inchikey = {}
dict_chemical_name = {}
dict_chemical_smiles = {}
dict_chemical_synonyms = {}
chemical_mapping = defaultdict(dict)
parentMol_mapping = defaultdict(dict)


def load_chemicals_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier, n.inchikey, n.name, n.smiles, n.resource, n.synonyms, n.inchi'''
    results = graph_database.run(query)

    for record in results:
        identifier = record.data()['n.identifier']
        inchikey = record.data()['n.inchikey']
        name = record.data()['n.name']
        smiles = record.data()['n.smiles']
        resource = record.data()['n.resource']
        synonyms = record.data()['n.synonyms']
        inchi = record.data()['n.inchi']
        dict_chemical_to_resource[identifier] = resource

        if inchikey:
            if inchikey not in dict_chemical_inchi:
                dict_chemical_inchikey[inchikey] = set()
            dict_chemical_inchikey[inchikey].add(identifier)

        if name:
            name = name.lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_name, name, identifier)

        if smiles:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_smiles, smiles, identifier)

        if inchi:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_inchi, inchi, identifier)

        if synonyms:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_synonyms, synonym.lower(), identifier)


# External references for each structure node are loaded in
dict_structureID_to_xref = defaultdict(lambda: defaultdict(set))


def load_structure_external_ref_in():
    query = '''MATCH (n:DC_Identifier)--(m:DC_Structure) RETURN id(m), n.type, n.identifier'''
    results = graph_database.run(query)

    for record in results:
        structure_id = record.data()['id(m)']
        xref_type = record.data()['n.type']
        xref_identifier = record.data()['n.identifier']
        dict_structureID_to_xref[structure_id][xref_type].add(xref_identifier)


# mappping of structure to chmical
def load_structure_in():
    query = '''MATCH (n:DC_Structure) RETURN id(n), n.inchikey, n.smiles, n.name'''
    results = graph_database.run(query)

    for record in results:
        identifier = record.data()['id(n)']
        inchikey = record.data()['n.inchikey']
        smiles = record.data()['n.smiles']
        name = record.data()['n.name']

        is_mapped = False

        if inchikey in dict_chemical_inchikey:
            is_mapped = True
            chemicals = dict_chemical_inchikey[inchikey]
            for chemical_id in chemicals:
                if chemical_id not in chemical_mapping[identifier]:
                    chemical_mapping[identifier][chemical_id] = set()
                chemical_mapping[identifier][chemical_id].add('inchikey')

        if is_mapped:
            continue

        if smiles in dict_chemical_smiles:
            is_mapped = True
            chemicals = dict_chemical_smiles[smiles]
            for chemical_id in chemicals:
                if chemical_id not in chemical_mapping[identifier]:
                    chemical_mapping[identifier][chemical_id] = set()
                chemical_mapping[identifier][chemical_id].add('smiles')

        if is_mapped:
            continue

        name = name.lower()
        if name in dict_chemical_name:
            is_mapped = True
            chemicals = dict_chemical_name[name]
            for chemical_id in chemicals:
                if chemical_id not in chemical_mapping[identifier]:
                    chemical_mapping[identifier][chemical_id] = set()
                chemical_mapping[identifier][chemical_id].add('name')

        if is_mapped:
            continue

        if name in dict_chemical_synonyms:
            is_mapped = True
            chemicals = dict_chemical_synonyms[name]
            for chemical_id in chemicals:
                if chemical_id not in chemical_mapping[identifier]:
                    chemical_mapping[identifier][chemical_id] = set()
                chemical_mapping[identifier][chemical_id].add('synonyms')

        if identifier not in chemical_mapping:
            csv_not_mapped_chemical.writerow([identifier, inchikey, name])

    for ident in chemical_mapping:
        for chem_id in chemical_mapping[ident]:
            methods = list(chemical_mapping[ident][chem_id])
            methods = '|'.join(methods)
            # chemical_id = dict_nodes_to_chemical[chem_id]
            resource = set(dict_chemical_to_resource[chem_id])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_chemical.writerow([ident, chem_id, resource, methods])


# mapping of parentmol to chemical
def load_parent_drug_molecule_in():
    query = '''MATCH (n:DC_ParentDrugMolecule) RETURN n, id(n)'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        node_id = record.data()['id(n)']
        name = node["name"]
        name = name.lower()
        inchi = node["inchi"] if "inchi" in node else ''
        inchikey = node["inchikey"] if "inchikey" in node else ''
        smiles = node["smiles"] if "smiles" in node else ''


        is_mapped = False

        # inchi
        if inchi:
            # inchis = inchi.split('=', 1)
            if inchi in dict_chemical_inchi:
                is_mapped=True
                chemicals = dict_chemical_inchi[inchi]
                for chemical_id in chemicals:
                    if chemical_id not in parentMol_mapping[node_id]:
                        parentMol_mapping[node_id][chemical_id] = set()
                    parentMol_mapping[node_id][chemical_id].add('inchi')

        if is_mapped:
            continue

        # inchikey
        if inchikey:
            if inchikey in dict_chemical_inchikey:
                is_mapped = True
                chemicals = dict_chemical_inchikey[inchikey]
                for chemical_id in chemicals:
                    if chemical_id not in parentMol_mapping[node_id]:
                        parentMol_mapping[node_id][chemical_id] = set()
                    parentMol_mapping[node_id][chemical_id].add('inchikey')

        if is_mapped:
            continue
        # smiles
        if smiles:
            if smiles in dict_chemical_smiles:
                is_mapped=True
                chemicals = dict_chemical_smiles[smiles]
                for chemical_id in chemicals:
                    if chemical_id not in parentMol_mapping[node_id]:
                        parentMol_mapping[node_id][chemical_id] = set()
                    parentMol_mapping[node_id][chemical_id].add('inchikey')
        if is_mapped:
            continue

        # name
        if name in dict_chemical_name:
            chemicals = dict_chemical_name[name]
            for chemical_id in chemicals:
                if chemical_id not in parentMol_mapping[node_id]:
                    parentMol_mapping[node_id][chemical_id] = set()
                parentMol_mapping[node_id][chemical_id].add('name')

        if node_id not in parentMol_mapping:
            csv_not_mapped_parentmol.writerow([node_id, inchi, name])

    for parent_mol_id in parentMol_mapping:
        for pm_id in parentMol_mapping[parent_mol_id]:
            methods = list(parentMol_mapping[parent_mol_id][pm_id])
            methods = '|'.join(methods)
            # chemical_id = dict_nodes_to_parent_mol[parent_mol_id]
            resource = set(dict_chemical_to_resource[pm_id])
            resource.add('DrugCentral')
            resource = '|'.join(resource)
        csv_mapped_parent_mol.writerow([parent_mol_id, pm_id, resource, methods])


# tsv for structure
# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_chemical = open('chemical/not_mapped_chemical.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped_chemical = csv.writer(file_not_mapped_chemical, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped_chemical.writerow(['id', 'inchikey', 'name'])
file_mapped_chemical = open('chemical/mapped_chemical.tsv', 'w', encoding="utf-8")
csv_mapped_chemical = csv.writer(file_mapped_chemical, delimiter='\t', lineterminator='\n')
csv_mapped_chemical.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])

# tsv for parentmol
# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_parent_mol = open('chemical/not_mapped_parent_mol.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped_parentmol = csv.writer(file_not_mapped_parent_mol, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped_parentmol.writerow(['id', 'inchi', 'name'])
file_mapped_parent_mol = open('chemical/mapped_parent_mol.tsv', 'w', encoding="utf-8")
csv_mapped_parent_mol = csv.writer(file_mapped_parent_mol, delimiter='\t', lineterminator='\n')
csv_mapped_parent_mol.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])


def generate_cypher_file(file_name_structure, file_name_parentmol):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')
    # es gibt keine mappings zu Chemical, daher ist der cypher file nur für Pharmacological class erstellt

    # structure
    query = '''MATCH (n:DC_Structure), (c:Chemical{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_Structure_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/chemical/" + file_name_structure,
                                              query)
    cypher_file.write(query)

    # parentmol
    query = '''MATCH (n:DC_ParentDrugMolecule), (c:Chemical{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_ParentDrugMolecule_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/chemical/" + file_name_parentmol,
                                              query)
    cypher_file.write(query)

    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path dc chemical')
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()
    print("load chemicals in")
    load_chemicals_in()

    print('xref in')
    load_structure_external_ref_in()

    print("load structure in")
    load_structure_in()

    print("load parent drug molecule in")
    load_parent_drug_molecule_in()

    generate_cypher_file('mapped_chemical.tsv', 'mapped_parent_mol.tsv')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
