import csv
import datetime
import sys, os
import glob
import gzip

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
import general_function_bindingDB


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary chemical id to resource and xref
dict_chemical_id_to_resource_and_xrefs = {}

# dictionary inchikey to chemical ids
dict_chemical_inchikey_to_ids = {}
# dictionary chemical id  to inchikey
dict_chemical_id_to_inchikey = {}

# dictionary synonym to chemical id
dict_chemical_synonym_to_chemical_ids = {}

# dictionary bindingdb id to chemical id
dict_bindingdb_to_chemical_ids = {}

# dictionary CHEMBL id to chemical id
dict_chembl_to_chemical_ids = {}
# dictionary smile id to chemical ids
dict_chemical_smiles = {}

# dictionary inchi_key_to_pubchem_id
dict_inchikey_to_pubchem_id = {}


def load_pubchem_inchikey_mapping():
    """
    The mappings are from this https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi manual executed.
    The one with a pubchem id will be add as new node
    :return:
    """
    for gz_file in glob.glob('chemical/*.gz'):
        with gzip.open(gz_file, 'rt') as file:
            csv_reader = csv.reader(file, delimiter='\t')
            for row in csv_reader:
                # if row[1]=='':
                #     continue
                if not row[0] in dict_inchikey_to_pubchem_id:
                    dict_inchikey_to_pubchem_id[row[0]] = set([row[1]]) if row[1] != '' else set()
                else:
                    dict_inchikey_to_pubchem_id[row[0]].add(row[1])
    print('nuber of inchikey check', len(dict_inchikey_to_pubchem_id))


def generate_new_file_and_add_cypher_query(source):
    """
    Prepare tsv file and cypher query for new nodes
    :param source:
    :return:
    """
    file_name = 'new_node.tsv'
    file = open('chemical/' + file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['id', 'pubchem_id', 'xrefs', 'name', 'smiles'])

    query = pharmebinetutils.get_all_properties_of_on_label % ('bindingDB_mono_struct_names')
    list_of_prop = []
    results = g.run(query)
    for result in results:
        [prop] = result.values()
        if prop not in ['monomerid', 'name', 'inchi_key', 'display_name', 'smiles_string',
                        'cd_smiles'] and not prop.startswith('cd_fp'):
            list_of_prop.append(prop + ':n.' + prop)
        elif prop == 'inchi_key':
            list_of_prop.append('inchikey:n.' + prop)
        elif prop == 'display_name':
            list_of_prop.append('bindingDB_id:n.' + prop)
        # elif prop=='smiles_string':
        #     list_of_prop.append('smiles:n.' + prop)

    query_cypher = 'Match (n:bindingDB_mono_struct_names{monomerid:line.id}) Create (m:Chemical{identifier:line.pubchem_id, smiles:line.smiles, name:line.name, xrefs:split(line.xrefs,"|"), url:"https://www.bindingdb.org/rwd/bind/chemsearch/marvin/MolStructure.jsp?monomerid="+line.id, source:"PubChem via BindingDB", bindingdb:"yes", resource:["BindingDB"], license:"CC BY 3.0 US Deed",  ' + ', '.join(
        list_of_prop) + '})-[:equal_binding{new:true}]->(n)'
    cypher_file_path = os.path.join(source, 'cypher.cypher')
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query_cypher = pharmebinetutils.get_query_import(path_of_directory,
                                                     file_name,
                                                     query_cypher)
    cypher_file.write(query_cypher)
    # query = 'Match (m:Chemical{identifier:line.pubchem_id}) Set m.name=line.name '
    # query = pharmebinetutils.get_query_import(path_of_directory,
    #                                           'manual_pubchem_to_name.tsv', query)
    # cypher_file.write(query)
    cypher_file.close()

    return csv_writer


def load_chemical_from_database_and_add_to_dict():
    """
    Load all Chemical from my database  and add them into a dictionary
    """
    query = "MATCH (n:Chemical) RETURN n.identifier, n.xrefs, n.resource, n.inchikey, n.name, n.synonyms, n.smiles "
    results = g.run(query)

    for record in results:
        [identifier, xrefs, resource, inchikey, name, synonyms, smiles] = record.values()
        # print(node)
        xrefs = set(xrefs) if xrefs is not None else set()
        dict_chemical_id_to_resource_and_xrefs[identifier] = [resource, xrefs]

        if inchikey:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_inchikey_to_ids, inchikey, identifier)
            dict_chemical_id_to_inchikey[identifier] = inchikey

        name = name.lower() if name else ''
        pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_synonym_to_chemical_ids, name, identifier)
        synonyms = synonyms if synonyms else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_synonym_to_chemical_ids, synonym.lower(),
                                                      identifier)
        # some manual check nodes have a wrong smile
        if smiles and not identifier in ['DB11072']:
            pharmebinetutils.add_entry_to_dict_to_set(dict_chemical_smiles, smiles, identifier)

        for xref in xrefs:
            if xref.startswith('BindingDB'):
                pharmebinetutils.add_entry_to_dict_to_set(dict_bindingdb_to_chemical_ids, xref.split(':')[1],
                                                          identifier)
            elif xref.startswith('ChEMBL'):
                pharmebinetutils.add_entry_to_dict_to_set(dict_chembl_to_chemical_ids, xref.split(':')[1],
                                                          identifier)


def load_all_BioGrid_chemical_and_finish_the_files(csv_mapping, csv_new):
    """
    Load all monomer and map to chemicals and write into tsv file
    Where (n)--(:bioGrid_interaction)
    """
    #
    query = "MATCH (n:bindingDB_mono_struct_names) Where (n)--() RETURN n.monomerid,n.inchi_key,n.cd_smiles, n.smiles_string, n.name, n.synonyms"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0

    counter_chembl = 0

    counter_inchikey_file = 0
    counter_inchikey = 0
    counter_create = 0
    batch = 150000
    file = open('chemical/chemical_inchikeys' + str(counter_inchikey_file) + '.tsv', 'w', encoding='utf-8')

    for record in results:
        [identifier, inchikey, cd_smiles, smiles_string, name, synonyms] = record.values()
        counter_all += 1

        # mapping
        found_mapping = False
        # create new node
        created_new_node = False
        dict_new_inchikey_to_id = {}

        if inchikey:
            if inchikey in dict_chemical_inchikey_to_ids:
                found_mapping = True
                for chemical_id in dict_chemical_inchikey_to_ids[inchikey]:
                    xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_and_xrefs[chemical_id][0],
                             "BindingDB"), 'inchikey', '|'.join(xrefs)])
        else:
            inchikey = ''

        if found_mapping:
            continue
        smiles = cd_smiles if cd_smiles else smiles_string
        if smiles:
            if smiles in dict_chemical_smiles:
                found_mapping = True
                for chemical_id in dict_chemical_smiles[smiles]:
                    xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_and_xrefs[chemical_id][0],
                             "BindingDB"), 'smiles', '|'.join(xrefs)])

        if found_mapping:
            continue

        name = name.lower() if name else ''
        # not in ['50133280']
        if name != '' and identifier:
            if name in dict_chemical_synonym_to_chemical_ids:
                found_mapping = True
                for chemical_id in dict_chemical_synonym_to_chemical_ids[name]:
                    if chemical_id in dict_chemical_id_to_inchikey:
                        other_inchikey = dict_chemical_id_to_inchikey[chemical_id]
                        if other_inchikey.split('-')[0] == inchikey.split('-')[0]:
                            xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                            csv_mapping.writerow(
                                [identifier, chemical_id,
                                 pharmebinetutils.resource_add_and_prepare(
                                     dict_chemical_id_to_resource_and_xrefs[chemical_id][0],
                                     "BindingDB"), 'name_part_inchikey', '|'.join(xrefs)])
                    else:
                        xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                        csv_mapping.writerow(
                            [identifier, chemical_id,
                             pharmebinetutils.resource_add_and_prepare(
                                 dict_chemical_id_to_resource_and_xrefs[chemical_id][0],
                                 "BindingDB"), 'name', '|'.join(xrefs)])

        if found_mapping:
            continue

        synonyms = synonyms if synonyms else []
        chembl_mapping = set()
        synonyms_mapping = set()
        for synonym in synonyms:
            if synonym.startswith('CHEMBL'):
                if synonym in dict_chembl_to_chemical_ids:
                    found_mapping = True
                    chembl_mapping = chembl_mapping.union(dict_chembl_to_chemical_ids[synonym])
                counter_chembl += 1
                continue
            synonym = synonym.lower()
            if synonym in dict_chemical_synonym_to_chemical_ids:
                found_mapping = True
                synonyms_mapping = synonyms_mapping.union(dict_chemical_synonym_to_chemical_ids[synonym])

        if len(chembl_mapping) > 0:
            for chemical_id in chembl_mapping:
                if chemical_id in dict_chemical_id_to_inchikey:
                    other_inchikey = dict_chemical_id_to_inchikey[chemical_id]
                    if other_inchikey.split('-')[0] == inchikey.split('-')[0]:
                        xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                        csv_mapping.writerow(
                            [identifier, chemical_id,
                             pharmebinetutils.resource_add_and_prepare(
                                 dict_chemical_id_to_resource_and_xrefs[chemical_id][0], "BindingDB"),
                             'synonym-chembl_part_inchikey', '|'.join(xrefs)])
                else:
                    xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_and_xrefs[chemical_id][0], "BindingDB"),
                         'synonym-chembl', '|'.join(xrefs)])

        elif len(synonyms_mapping) > 0 and identifier not in ['50133280']:
            for chemical_id in synonyms_mapping:
                if chemical_id in dict_chemical_id_to_inchikey:
                    other_inchikey = dict_chemical_id_to_inchikey[chemical_id]
                    if other_inchikey.split('-')[0] == inchikey.split('-')[0]:
                        xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                        csv_mapping.writerow(
                            [identifier, chemical_id,
                             pharmebinetutils.resource_add_and_prepare(
                                 dict_chemical_id_to_resource_and_xrefs[chemical_id][0], "BindingDB"),
                             'synonyms_part_inchikey', '|'.join(xrefs)])
                else:
                    xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                    csv_mapping.writerow(
                        [identifier, chemical_id,
                         pharmebinetutils.resource_add_and_prepare(
                             dict_chemical_id_to_resource_and_xrefs[chemical_id][0], "BindingDB"),
                         'synonyms', '|'.join(xrefs)])

        if found_mapping:
            continue

        #  not identifier in ['50004358']
        if identifier in dict_bindingdb_to_chemical_ids and name != '' and identifier not in ['358']:
            found_mapping = True
            for chemical_id in dict_bindingdb_to_chemical_ids[identifier]:
                xrefs = dict_chemical_id_to_resource_and_xrefs[chemical_id][1]
                csv_mapping.writerow(
                    [identifier, chemical_id,
                     pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource_and_xrefs[chemical_id][0],
                                                               "BindingDB"), 'xref', '|'.join(xrefs)])

        if found_mapping:
            continue

        if inchikey:
            if inchikey in dict_inchikey_to_pubchem_id and (len(synonyms) > 0 or name != ''):
                if inchikey in dict_new_inchikey_to_id and identifier != dict_new_inchikey_to_id[inchikey]:
                    print('ohno, better combine xrefs')

                if len(dict_inchikey_to_pubchem_id[inchikey]) == 1:
                    pubchem_id = dict_inchikey_to_pubchem_id[inchikey].pop()
                    if pubchem_id == '':
                        continue
                    counter_create += 1
                    created_new_node = True
                    if name == "":
                        possible_names = [x for x in synonyms if
                                          not 'CHEMBL' in x and not 'Example' in x and not 'CHEBI' in x and x != 'Name not given']
                        if len(possible_names) > 0:
                            name = possible_names[0]
                        else:
                            counter_not_mapped += 1
                            continue
                    csv_new.writerow(
                        [identifier, pubchem_id, 'bindingDB:' + identifier, name, smiles])

        if not created_new_node:
            counter_not_mapped += 1
            if not inchikey in dict_inchikey_to_pubchem_id and inchikey != '':
                counter_inchikey += 1
                file.write(inchikey + '\t')
                if counter_inchikey % batch == 0:
                    file.close()
                    counter_inchikey_file += 1
                    file = open('chemical/chemical_inchikeys' + str(counter_inchikey_file) + '.tsv', 'w',
                                encoding='utf-8')

    print('number of not-mapped monomer:', counter_not_mapped)
    print('number of all monomer:', counter_all)
    print('number of new:', counter_create)

    print('all with chembl synonym:', counter_chembl)


def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path bindingDB chemical')

    os.chdir(path_of_directory + "mapping_and_merging_into_hetionet/bindingDB/")
    home = os.getcwd()
    source = os.path.join(home, 'output/')
    path_of_directory = os.path.join(home, 'chemical/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pubchem information')

    load_pubchem_inchikey_mapping()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Chemical from database')
    load_chemical_from_database_and_add_to_dict()
    print("done")
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping = general_function_bindingDB.generate_files(path_of_directory, 'mapped_chemical.tsv', source,
                                                            'bindingDB_mono_struct_names', 'Chemical', ['monomerid'],
                                                            ', v.xrefs=split(line.xrefs,"|") ')
    csv_new = generate_new_file_and_add_cypher_query(source)
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all bindingDB monomer from database')
    load_all_BioGrid_chemical_and_finish_the_files(csv_mapping, csv_new)

    driver.close()
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
