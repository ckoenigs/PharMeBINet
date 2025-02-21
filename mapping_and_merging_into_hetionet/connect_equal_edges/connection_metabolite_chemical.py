import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j_mysql():
    """
    create connection to neo4j and mysql
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


set_chemical_ids = set()
dict_inchikey_to_chemical_id = {}
dict_name_to_chemical_id = {}
dict_synonym_to_chemical_id = {}


def load_chemicals():
    """
    Load all chemical ids into a set
    :return:
    """
    query = 'Match (n:Chemical) Return n.identifier, n.alternative_ids, n.inchikey, n.name, n.synonyms'
    for identifier, alternative_ids, inchikey, name, synonyms, in g.run(query):
        set_chemical_ids.add(identifier)
        if inchikey:
            pharmebinetutils.add_entry_to_dict_to_set(dict_inchikey_to_chemical_id, inchikey, identifier)
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_id, name.lower(), identifier)
        if synonyms:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_chemical_id, synonym.lower(), identifier)

    print('number of chemicals:', len(set_chemical_ids))


def load_and_map_metabolite():
    """
    Load and map metabolite to chemical
    :return:
    """
    file_name = 'output/metabolite_chemical.tsv'
    with open('output/cypher.cypher','a',encoding='utf-8') as f:
        cypher_query = ''' Match (n:Metabolite{identifier:line.metabolite_id}), (m:Compound{identifier:line.chemical_id})  Create (n)-[:EQUAL_MeC{mapping:line.mapped, source:'PharMeBINet', resource:['PharMeBINet'], pharmebinet:'yes', license:'CC0 1.0'}]->(m)'''
        cypher_query = pharmebinetutils.get_query_import(path_of_directory,
                                                         f'mapping_and_merging_into_hetionet/connect_equal_edges/{file_name}',
                                                         cypher_query)
        f.write(cypher_query)
    with open(file_name, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter='\t')
        csv_writer.writerow(['metabolite_id', 'chemical_id', 'mapped'])
        counter_mapped = 0
        counter = 0

        query = 'Match (n:Metabolite) Return n.identifier, n.xrefs, n.inchikey, n.name, n.synonyms'
        for identifier, xrefs, inchikey, name, synonyms, in g.run(query):
            counter += 1
            is_mapped = False
            if inchikey in dict_inchikey_to_chemical_id:
                counter_mapped += 1
                is_mapped = True
                for chemical_id in dict_inchikey_to_chemical_id[inchikey]:
                    csv_writer.writerow([identifier, chemical_id, 'InChIKey'])

            if is_mapped:
                continue

            if xrefs:
                set_drugbank = set()
                set_pubchem = set()
                for xref in xrefs:
                    if xref.startswith('DrugBank:'):
                        drugbank_id = xref.split(':')[1]
                        if drugbank_id in set_chemical_ids:
                            set_drugbank.add(drugbank_id)
                    elif xref.startswith('PubChem Compound:'):
                        pubchem_id = xref.split(':')[1]
                        if pubchem_id in set_chemical_ids:
                            set_pubchem.add(pubchem_id)
                if len(set_drugbank) > 0 or len(set_pubchem) > 0:
                    is_mapped = True
                    counter_mapped += 1
                    name = name.lower()
                    intersection = set()
                    if name in dict_name_to_chemical_id:
                        set_chemicals_with_name = dict_name_to_chemical_id[name]
                        intersection_drugbank = set_chemicals_with_name.intersection(set_drugbank)
                        intersection_pubchem = set_chemicals_with_name.intersection(set_pubchem)
                        intersection = intersection_drugbank.union(intersection_pubchem)
                    if len(intersection) > 0:
                        for chemical_id in intersection:
                            csv_writer.writerow([identifier, chemical_id, 'pubchem_or_drugbank_with_name'])
                    elif len(set_drugbank) > 0:
                        for chemical_id in set_drugbank:
                            csv_writer.writerow([identifier, chemical_id, 'drugbank'])
                    elif len(set_pubchem) > 0:
                        for chemical_id in set_pubchem:
                            csv_writer.writerow([identifier, chemical_id, 'pubchem'])

            if is_mapped:
                continue

            if name in dict_name_to_chemical_id:
                counter_mapped += 1
                is_mapped = True
                for chemical_id in dict_name_to_chemical_id[name]:
                    csv_writer.writerow([identifier, chemical_id, 'name_name'])

            if is_mapped:
                continue

            if name in dict_synonym_to_chemical_id:
                counter_mapped += 1
                is_mapped = True
                for chemical_id in dict_synonym_to_chemical_id[name]:
                    csv_writer.writerow([identifier, chemical_id, 'name_synonym'])

            if is_mapped:
                continue
            if synonyms:
                for synonym in synonyms:
                    synonym = synonym.lower
                    if synonym in dict_name_to_chemical_id:

                        is_mapped = True
                        for chemical_id in dict_name_to_chemical_id[synonym]:
                            csv_writer.writerow([identifier, chemical_id, 'synonym_name'])

            if is_mapped:
                counter_mapped += 1
                continue

        print('number of mapped metabolite', counter_mapped)
        print('number of metabolite', counter)


def main():
    global path_of_directory

    # path to to project
    if len(sys.argv) == 2:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path for connection of se,s,d')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in chemical from pharmebinet')

    load_chemicals()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in metabolite and map to chemical')

    load_and_map_metabolite()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
