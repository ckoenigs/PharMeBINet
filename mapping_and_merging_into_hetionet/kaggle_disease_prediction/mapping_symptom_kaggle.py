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


def generate_files(path_of_directory, file_name, source, label_kaggle, label_pharmebinet):
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
    query = f' Match (n:{label_kaggle}{{name:line.node_id}}), (v:{label_pharmebinet}{{identifier:line.pharmebinet_node_id}})  Create (v)-[:equal_to_kaggle_{label_pharmebinet.lower()}{{how_mapped:line.how_mapped}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    cypher_file.write(query)
    return csv_mapping


# dictionary_manual mapping
dict_manual_mapping = {
    'continuous_sneezing': ['HP:0025095'],
    'burning_micturition': ['HP:0100518'],
    'spotting_urination': ['HP:0002907', 'HP:0012587'],
    'irregular_sugar_level': ['HP:0011015'],
    'high_fever': ['HP:0033031'],
    'yellowish_skin': ['HP:0000952'],
    'yellow_urine': ['HP:0040321'],
    'yellowing_of_eyes': ['HP:0032106'],
    'swelled_lymph_nodes': ['HP:0002716'],
    'blurred_and_distorted_vision': ['HP:0000622'],
    'phlegm': ['HP:0032016'],
    'C0700184': ['HP:0033050'],
    'redness_of_eyes': ['HP:0025337'],
    'pain_in_anal_region': ['HP:0500005'],
    'bruising': ['HP:0000978'],
    'puffy_face_and_eyes': ['HP:0500011', 'HP:0000629'],
    'excessive_hunger': ['HP:0002591'],
    'drying_and_tingling_lips': ['HP:0040181'],
    'loss_of_balance': ['HP:0002172'],
    'bladder_discomfort': ['HP:0000014'],
    'foul_smell_ofurine': ['HP:0012088'],
    'red_spots_over_body': ['HP:0000979'],
    'belly_pain': ['HP:0002027'],
'abnormal_menstruation': ['HP:0000140'],
'watering_from_eyes': ['HP:0009926'],
}
'''
'nodal_skin_eruptions': [],  #nodal skin eruptions	nodal_skin_eruptions	set()
'ulcers_on_tongue': [],  #ulcers on tongue	ulcers_on_tongue	set()
'cold_hands_and_feets': [],  #cold hands and feets	cold_hands_and_feets	set()
'patches_in_throat': [],  #patches in throat	patches_in_throat	set()
'pain_behind_the_eyes': [],  #pain behind the eyes	pain_behind_the_eyes	set()
'swelling_of_stomach': [],  #swelling of stomach	swelling_of_stomach	set()
'throat_irritation': [],  #throat irritation	throat_irritation	{'C0700184'}
'sinus_pressure': [],  #sinus pressure	sinus_pressure	{'C0848633'}
'congestion': [],  #congestion	congestion	{'C0700148'}
'weakness_in_limbs': [],  #weakness in limbs	weakness_in_limbs	set()

'pain_during_bowel_movements': [],  #pain during bowel movements	pain_during_bowel_movements	set()

'irritation_in_anus': [],  #irritation in anus	irritation_in_anus	set()

'swollen_legs': [],  #swollen legs	swollen_legs	{'C0581394'}
'swollen_blood_vessels': [],  #swollen blood vessels	swollen_blood_vessels	set()

'swollen_extremeties': [],  #swollen extremeties	swollen_extremeties	set()

'extra_marital_contacts': [],  #extra marital contacts	extra_marital_contacts	set()

'swelling_joints': [],  #swelling joints	swelling_joints	set()
'movement_stiffness': [],  #movement stiffness	movement_stiffness	set()
'spinning_movements': [],  #spinning movements	spinning_movements	set()
 
'unsteadiness': [],  #unsteadiness	unsteadiness	{'C0427108'}
'weakness_of_one_body_side': [],  #weakness of one body side	weakness_of_one_body_side	set()


'continuous_feel_of_urine': [],  #continuous feel of urine	continuous_feel_of_urine	set()
'passage_of_gases': [],  #passage of gases	passage_of_gases	set()
'internal_itching': [],  #internal itching	internal_itching	set()
'toxic_look_(typhos)': [],  #toxic look (typhos)	toxic_look_(typhos)	set()
'altered_sensorium': [],  #altered sensorium	altered_sensorium	set()



'dischromic_patches': [],  #dischromic patches	dischromic_patches	set()

'family_history': [],  #family history	family_history	{'C0241889'}
'mucoid_sputum': [],  #mucoid sputum	mucoid_sputum	{'C0577978'}
'rusty_sputum': [],  #rusty sputum	rusty_sputum	set()
'visual_disturbances': [],  #visual disturbances	visual_disturbances	{'C0547030'}
'receiving_blood_transfusion': [],  #receiving blood transfusion	receiving_blood_transfusion	set()
'receiving_unsterile_injections': [],  #receiving unsterile injections	receiving_unsterile_injections	set()
'stomach_bleeding': [],  #stomach bleeding	stomach_bleeding	set()
'distention_of_abdomen': [],  #distention of abdomen	distention_of_abdomen	set()
'history_of_alcohol_consumption': [],  #history of alcohol consumption	history_of_alcohol_consumption	set()
'blood_in_sputum': [],  #blood in sputum	blood_in_sputum	set()
'prominent_veins_on_calf': [],  #prominent veins on calf	prominent_veins_on_calf	set()
'painful_walking': [],  #painful walking	painful_walking	set()
'pus_filled_pimples': [],  #pus filled pimples	pus_filled_pimples	set()
'scurring': [],  #scurring	scurring	set()
'silver_like_dusting': [],  #silver like dusting	silver_like_dusting	set()
'small_dents_in_nails': [],  #small dents in nails	small_dents_in_nails	set()
'inflammatory_nails': [],  #inflammatory nails	inflammatory_nails	set()
'red_sore_around_nose': [],  #red sore around nose	red_sore_around_nose	set()
'yellow_crust_ooze': [],  #yellow crust ooze	yellow_crust_ooze	set()
'prognosis': [],  #prognosis	prognosis	{'C0033325', 'C3854082'}
'''


def load_all_kaggle_symptoms_and_finish_the_files(csv_mapping):
    """
    Load all kaggle symptom map to symptom and write into file
    """

    query = "MATCH (n:kaggle_symptom) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['name']
        name = node['name'].lower().replace('_', ' ')

        found_mapping = False
        if name in dict_synonym_to_ids:
            found_mapping = True
            for node_id in dict_synonym_to_ids[name]:
                csv_mapping.writerow([identifier, node_id, 'name'])
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

    print('##########################################################################')

    print(datetime.datetime.now())
    print('symptomrate cypher and tsv file')

    csv_mapping = generate_files(path_of_directory, 'mapping_symptom.tsv', source,
                                 'kaggle_symptom', 'Symptom')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all kaggle symptoms from database')
    load_all_kaggle_symptoms_and_finish_the_files(csv_mapping)
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
