# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:14:27 2017

@author: cassandra
"""

import sys
import datetime, csv

# reload(sys)
# set default encoding on utf-8
# sys.setdefaultencoding('utf-8')

# dictionary with pair(disease_id, HPO id) and qualifier, db_reference, evidence code, frequency modifier
dict_disease_symptom_hpo_pair_to_information = {}

# list of all disease IDs
list_disease_ids = []

# list of all hpo symptoms ids
list_symptoms_ids = []

# path to directory
path_of_directory = ''
if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path')

# csv file for disease node
writer = open('disease.csv', 'w', encoding='utf-8')
csv_writer = csv.writer(writer)
list_of_disease_properties = ['id', 'name', 'source']
csv_writer.writerow(list_of_disease_properties)

# csv file for the relationships
list_of_rela_properties = ['disease_id', 'phenotype_id', 'qualifier', 'evidence_code', 'source', 'frequency_modifier',
                           'aspect']
writer_rela = open('rela_disease_phenotyp.csv', 'w', encoding='utf-8')
csv_writer_rela = csv.writer(writer_rela)
csv_writer_rela.writerow(list_of_rela_properties)

# cypher file
cypher_file = open('cypher.cypher', 'a')
query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/hpo/disease.csv" As line Create (:HPOdisease{'''
for property in list_of_disease_properties:
    if property == 'name':
        query += property + ':split(line.' + property + ',"|"), '
        continue
    query += property + ':line.' + property + ', '
query = query[:-2] + '});\n'
cypher_file.write(query)
cypher_file.write(':begin\n')
cypher_file.write('Create Constraint On (node:HPOdisease) Assert node.id Is Unique; \n')
cypher_file.write(':commit \n')
# query for relationships
query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/hpo/rela_disease_phenotyp.csv" As line MATCH (n:HPOdisease{id:line.disease_id}),(s:HPOsymptom{id:line.phenotype_id}) Create (n)-[:present{source:split(line.source,'|'),qualifier:split(line.qualifier,'|'), evidence_code:split(line.evidence_code,'|'), reference_id:split(line.reference_id,'|'), frequency_modifier:split(line.frequency_modifier,'|'), aspect:split(line.aspect,'|')}]->(s); \n '''
cypher_file.write(query)

# dictionary with all hpo identifier for frequency
dict_hpo_frequency = {}

'''
load all disease-symptom information in and remember the relationships 
file:
    0 	DB 	
    1 	DB_Object_ID 	
    2 	DB_Name 	
    3 	Qualifier: can be NOT, Secondary, MILD, Moderate, Severe, can be multiple  
    4 	HPO ID 	
    5 	DB:Reference: source of the information	
    6 	Evidence code: 	how the information was gathered This required field indicates the level of evidence supporting the annotation. 
        Annotations that have been extracted by parsing the Clinical Features sections of the omim.txt file are assigned the evidence code IEA (inferred from electronic annotation). 
        Please note that you need to contact OMIM in order to reuse these annotations in other software products. Other codes include PCS for published clinical study.
        This should be used for information extracted from articles in the medical literature. 
        Generally, annotations of this type will include the PubMed id of the published study in the DB_Reference field. 
        ICE can be used for annotations based on individual clinical experience. This may be appropriate for disorders with a limited amount of published data. 
        This must be accompanied by an entry in the DB:Reference field denoting the individual or center performing the annotation together with an identifier. 
        For instance, GH:007 might be used to refer to the seventh such annotation made by a specialist from Gotham Hospital (assuming the prefix GH has been registered with the HPO). 
        Finally we have TAS, which stands for “traceable author statement”, usually reviews or disease entries (e.g. OMIM) that only refers to the original public
    7 	Onset modifier: A term-id from the HPO-sub-ontology below the term “Age of onset” (HP:0003674). 	
    8 	Frequency modifier: A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279) 	
    9 	With: can have information  about characteristics 
    10 	Aspect:  one of P (Phenotypic abnormality), I (inheritance), C (onset and clinical course). This field is mandatory; cardinality 1
        It also exists M and empty but this are not defined?
    11 	Synonym: can have synonyms for disease or disorder 	
    12 	Date 	
    13 	Assigned by 	
'''


def gather_all_disease_symptom_information_from_HPO():
    f = open('phenotype_annotation.tab', 'r')
    # count all queries
    counter_create = 0

    global file_counter
    global cypher_file
    next(f)
    for line in f:

        splitted = line.split('\t')
        db_disease = splitted[0]
        db_disease_id = splitted[1]
        db_disease_name = splitted[2].lower().split(';;')
        qualifier = splitted[3]
        hpo_id = splitted[4]
        reference_id = splitted[5].split(';')
        evidence_code = splitted[6]
        frequency_modi = splitted[8]
        aspect = splitted[10]

        # # aspect M stands for a not known aspect, so I filter them out
        # if aspect == 'M':
        #     continue
        if (db_disease + ':' + db_disease_id, hpo_id) in dict_disease_symptom_hpo_pair_to_information:
            dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)]['qualifier'].add(
                qualifier)
            dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)]['reference_id'] = \
                dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)][
                    'reference_id'].union(reference_id)
            dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)][
                'evidence_code'].add(
                evidence_code)
            dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)][
                'frequency_modi'].add(
                frequency_modi)
            dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)]['aspect'].add(
                aspect)
        else:
            dict_disease_symptom_hpo_pair_to_information[(db_disease + ':' + db_disease_id, hpo_id)] = {
                'qualifier': set([qualifier]),
                'reference_id': set(reference_id),
                'evidence_code': set([evidence_code]),
                'frequency_modi': set([frequency_modi]), 'aspect': set([aspect])}
        # csv_writer_rela.writerow([db_disease+':'+db_disease_id, hpo_id,db_disease, qualifier, evidence_code,
        #                                                                          frequency_modi,aspect])

        if not hpo_id in list_symptoms_ids:
            list_symptoms_ids.append((hpo_id))

        # many diseases have more than one abnormal phenotype, but the disease need to be added only one time
        if db_disease + ':' + db_disease_id in list_disease_ids:
            continue
        # write disease into csv
        csv_writer.writerow([db_disease + ':' + db_disease_id, '|'.join(db_disease_name), db_disease])

        # add disease id to list
        list_disease_ids.append(db_disease + ':' + db_disease_id)

    print('number of disease symptoms relationships:' + str(len(dict_disease_symptom_hpo_pair_to_information)))
    print('number of hpo:' + str(len(list_symptoms_ids)))
    print('number of disease:' + str(len(list_disease_ids)))


'''
Write the combined relationship information into csv
'''


def write_rela_info_into_csv():
    for (db_disease, hpo_id), dict_rela_info in dict_disease_symptom_hpo_pair_to_information.items():
        info_list = [db_disease, hpo_id]
        info_list.append('|'.join(filter(None, dict_rela_info['qualifier'])))
        info_list.append('|'.join(filter(None, dict_rela_info['evidence_code'])))
        info_list.append('|'.join(filter(None, dict_rela_info['reference_id'])))
        info_list.append('|'.join(filter(None, dict_rela_info['frequency_modi'])))
        info_list.append('|'.join(filter(None, dict_rela_info['aspect'])))
        csv_writer_rela.writerow(info_list)


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather disease symptoms pairs and add disease to cypher file')
    gather_all_disease_symptom_information_from_HPO()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('combine the rela information and add them to the csv')
    write_rela_info_into_csv()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
