import datetime
import sys, os
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')
    # g = driver.session(database='pharmebinet')

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


# dictionary symptom id to resource
dict_symptom_id_to_resource = {}

# dictionary synonym to symptom
dict_synonym_to_ids = {}

# dict umls cui to symptoms ids
dict_umls_cui_to_ids = {}


def load_symptoms_from_database_and_add_to_dict():
    """
    Load all symptoms from my database  and add them into a dictionary
    """
    query = "MATCH (n:Symptom) RETURN n"
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_symptom_id_to_resource[identifier] = node['resource']
        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, name, identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_synonym_to_ids, synonym, identifier)

        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('UMLS'):
                umls_cui = xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_umls_cui_to_ids, umls_cui, identifier)


def generate_files(path_of_directory, file_name, source, disease, label_pharmebinet):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_path = os.path.join(path_of_directory, file_name)
    header = ['node_id', 'pharmebinet_node_id', 'how_mapped']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    query = f' Match (n:symptom_{disease}{{name:line.node_id}}), (v:{label_pharmebinet}{{identifier:line.pharmebinet_node_id}})  Create (v)-[:equal_to_{label_pharmebinet.lower()}{{how_mapped:line.how_mapped}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    cypher_file.write(query)
    return csv_mapping


# dictionary manual mapping
dict_manual_mapping = {
    'Stiffness': ['HP:0001387'],
    'Dryness': ['HP:0000958'],
    'Flaking': ['HP:0040189'],
    'Thickness of plaques': ['HP:0030351', 'HP:0025474', 'HP:0200035'],
    'increased thirst': ['HP:0001959'],
    'erectile dysfunction(ED)': ['HP:0100639'],
    'unintentional weight loss': ['HP:0001824'],
    'increased urination': ['HP:0000012'],
    'Frequent bladder infections': ['HP:0100577'],
    'Frequent skin infections': ['HP:0001581'],
    'eye/sinus pain': ['HP:0200026'],
    'Eye/sinus pain': ['HP:0200026'],
'pustular skin rash':['HP:0000988'],
    'giddiness':['HP:0002321'],
'irregular pulse (in atrial fibrillation)':['HP:0032552'],
    'peripheral edema (in heart failure)':['HP:0012398'],
'weakness of proximal muscles':['HP:0003701']
}


def load_all_kaggle_symptoms_and_finish_the_files(csv_mapping, disease):
    """
    Load all kaggle symptom map to symptom and write into file
    """

    query = f"MATCH (n:symptom_{disease}) RETURN n"
    print(query)
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['name']
        name = node['name'].lower().replace('_', ' ')
        synonym = node['synonym'] if 'synonym' in node else ''

        found_mapping = False
        if name in dict_synonym_to_ids:
            found_mapping = True
            for node_id in dict_synonym_to_ids[name]:
                csv_mapping.writerow([identifier, node_id, 'name'])
        if found_mapping:
            continue
        if '('  in name:
            first_name_part = name.split('(')[0].strip()
            if first_name_part in dict_synonym_to_ids:
                found_mapping = True
                for node_id in dict_synonym_to_ids[first_name_part]:
                    csv_mapping.writerow([identifier, node_id, 'name_first_part'])
        if found_mapping:
            continue

        if synonym in dict_synonym_to_ids:
            found_mapping = True
            for node_id in dict_synonym_to_ids[synonym]:
                csv_mapping.writerow([identifier, node_id, 'synonym'])
        if found_mapping:
            continue

        found_mapping = False
        if identifier in dict_manual_mapping:
            found_mapping = True
            for node_id in dict_manual_mapping[identifier]:
                csv_mapping.writerow([identifier, node_id, 'manual'])
        if found_mapping:
            continue

        # get first hte umls with the same name
        cur = con.cursor()
        query = "Select Distinct CUI From MRCONSO Where STR='%s';"
        query = query % (name)
        cuis = set()
        rows_counter = cur.execute(query)
        node_mapped = set()
        if rows_counter > 0:
            for (cui,) in cur:
                cuis.add(cui)
                if cui in dict_umls_cui_to_ids:
                    found_mapping = True

                    for node_id in dict_umls_cui_to_ids[cui]:
                        if node_id in node_mapped:
                            continue
                        node_mapped.add(node_id)
                        csv_mapping.writerow(
                            [identifier, node_id, 'cui'])

        if found_mapping:
            continue

        if len(cuis) > 0:
            cur = con.cursor()
            query = "Select Distinct STR From MRCONSO Where CUI in ('%s');"
            query = query % ("','".join(cuis))
            rows_counter = cur.execute(query)
            node_mapped = set()
            if rows_counter > 0:
                for (synonym,) in cur:
                    if synonym in dict_synonym_to_ids:
                        found_mapping = True

                        for node_id in dict_synonym_to_ids[synonym]:
                            if node_id in node_mapped:
                                continue
                            node_mapped.add(node_id)
                            csv_mapping.writerow(
                                [identifier, node_id, 'umls-synonyms'])

        if found_mapping:
            continue

        counter_not_mapped += 1
        # print('not mapped')
        print("'%s': [],  #%s\t%s\t%s" % (identifier, name, identifier, cuis))
    print('number of not-mapped symptoms:', counter_not_mapped)
    print('number of all symptoms:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path kaggle symptom')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/kaggle_disease_prediction')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'symptom/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all symptoms from database')
    load_symptoms_from_database_and_add_to_dict()

    for disease in ['Hypothyroidism', 'Psoriasis', 'diabetes_mellitus', 'diabetes_type_1', 'diabetes_type_2',
                    'gestational_diabetes', 'fugal_infection_aspergillosis', 'fugal_infection_candidiasis',
                    'fugal_infection_cryptococcosis', 'fugal_infection_zygomycosis', 'h_d_p', 'hyperthyroidism',
                    'pneumonia']:
        print('##########################################################################')

        print(datetime.datetime.now())
        print('symptom generate cypher and tsv file')

        csv_mapping = generate_files(path_of_directory, f'mapping_symptom_{disease}.tsv', source,
                                     disease, 'Symptom')

        print('##########################################################################')

        print(datetime.datetime.now())
        print('Load all symptoms from database')
        load_all_kaggle_symptoms_and_finish_the_files(csv_mapping, disease)
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
