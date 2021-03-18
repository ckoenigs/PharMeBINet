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
writer = open('output/disease.csv', 'w', encoding='utf-8')
csv_writer = csv.writer(writer)
list_of_disease_properties = ['id', 'name', 'source']
csv_writer.writerow(list_of_disease_properties)

# csv file for the relationships
list_of_rela_properties = ['disease_id', 'phenotype_id', 'qualifier', 'evidence_code', 'source', 'frequency_modifier',
                           'aspect', 'onset', 'sex', 'modifier', 'biocuration']
writer_rela = open('output/rela_disease_phenotyp.csv', 'w', encoding='utf-8')
csv_writer_rela = csv.writer(writer_rela)
csv_writer_rela.writerow(list_of_rela_properties)

# cypher file
cypher_file = open('cypher.cypher', 'a')
query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/hpo/output/disease.csv" As line Create (:HPO_disease{'''
for property in list_of_disease_properties:
    if property == 'name':
        query += property + ':split(line.' + property + ',"|"), '
        continue
    query += property + ':line.' + property + ', '
query = query[:-2] + '});\n'
cypher_file.write(query)
cypher_file.write(':begin\n')
cypher_file.write('Create Constraint On (node:HPO_disease) Assert node.id Is Unique; \n')
cypher_file.write(':commit \n')
# query for relationships
query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/hpo/output/rela_disease_phenotyp.csv" As line MATCH (n:HPO_disease{id:line.disease_id}),(s:HPO_symptom{id:line.phenotype_id}) Create (n)-[:present{'''

for property in list_of_rela_properties:
    if property in ['disease_id', 'phenotype_id']:
        continue
    query+= property+':split(line.'+property+',"|"), '
query= query[:-2]+'''}]->(s); \n '''
cypher_file.write(query)

# dictionary with all hpo identifier for frequency
dict_hpo_frequency = {}

'''
load all disease-symptom information in and remember the relationships 
file:
    0 	DatabaseId 	
    1 	DB_Name 		
    2 	Qualifier: can be NOT, Secondary, MILD, Moderate, Severe, can be multiple  
    4 	HPO ID 	
    5 	DB:Reference: source of the information	
    6 	Evidence code: 	This required field indicates the level of evidence supporting the annotation. The HPO project 
            currently uses three evidence codes.
            IEA (inferred from electronic annotation): Annotations extracted by parsing the Clinical Features sections 
                of the Online Mendelian Inheritance in Man resource are assigned the evidence code “IEA”.
            PCS (published clinical study) is used for used for information extracted from articles in the medical 
                literature. Generally, annotations of this type will include the pubmed id of the published study in the
                DB_Reference field.
            TAS (traceable author statement) is used for information gleaned from knowledge bases such as OMIM or 
                Orphanet that have derived the information frm a published source.
    7 	Onset modifier: A term-id from the HPO-sub-ontology below the term “Age of onset” (HP:0003674). 	
    8 	Frequency modifier: There are three allowed options for this field. (A) A term-id from the HPO-sub-ontology 
        below the term “Frequency” (HP:0040279). (since December 2016 ; before was a mixture of values). The terms for 
        frequency are in alignment with Orphanet. * (B) A count of patients affected within a cohort. For instance, 7/13 
        would indicate that 7 of the 13 patients with the specified disease were found to have the phenotypic 
        abnormality referred to by the HPO term in question in the study refered to by the DB_Reference; (C) A 
        percentage value such as 17%.	
    8   Sex: MALE or FEMALE
    10 	Modifier: A term-id from the HPO-sub-ontology below the term “Clinical modifier” 
    11 	Aspect:   one of P (Phenotypic abnormality), I (inheritance), C (onset and clinical course), 
        M (clinical modifier). This field is mandatory; cardinality 1.
            Terms with the P aspect are located in the Phenotypic abnormality subontology.
            Terms with the I aspect are from the Inheritance subontology.
            Terms with the C aspect are located in the Clinical course subontology, which includes onset, mortality, 
                and other terms related to the temporal aspects of disease.
            Terms with the M aspect are located in the Clinical Modifier subontology.
    12 	BiocurationBy: This refers to the biocurator who made the annotation and the date on which the annotation was 
        made; the date format is YYYY-MM-DD. The first entry in this field refers to the creation date. Any additional 
        biocuration is recorded following a semicolon. So, if Joseph curated on July 5, 2012, and Suzanna curated on 
        December 7, 2015, one might have a field like this: HPO:Joseph[2012-07-05];HPO:Suzanna[2015-12-07]. It is 
        acceptable to use ORCID ids. This field is mandatory, cardinality 1	
'''


def gather_all_disease_symptom_information_from_HPO():
    f = open('phenotype.hpoa', 'r')
    # count all queries
    csv_reader = csv.reader(f, delimiter='\t')

    global file_counter
    global cypher_file
    next(csv_reader)
    for line in csv_reader:
        db_disease_id = line[0]
        db_disease_name = line[1].lower().split(';;')
        qualifier = line[2]
        hpo_id = line[3]
        reference_id = line[4].split(';')
        evidence_code = line[5]
        onset = line[6]
        frequency_modi = line[7]
        sex = line[8].lower()
        modifier = line[9].split(';')
        aspect = line[10]
        biocuration = line[11].split(';')

        if (db_disease_id, hpo_id) in dict_disease_symptom_hpo_pair_to_information:
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['qualifier'].add(
                qualifier)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['reference_id'] = \
                dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['reference_id'].union(
                    reference_id)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)][
                'evidence_code'].add(evidence_code)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['sex'].add(sex)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['onset'].add(onset)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['frequency_modifier'].add(frequency_modi)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['aspect'].add(aspect)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['biocuration'] = \
                dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)][
                    'biocuration'].union(biocuration)
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)]['modifier'] = \
                dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)][
                    'modifier'].union(modifier)
        else:
            dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)] = {
                'qualifier': set([qualifier]), 'biocuration': set(biocuration),
                'reference_id': set(reference_id), 'modifier': set(modifier),
                'evidence_code': set([evidence_code]), 'sex': set([sex]), 'onset': set([onset]),
                'frequency_modifier': set([frequency_modi]), 'aspect': set([aspect])}
            # print(dict_disease_symptom_hpo_pair_to_information[(db_disease_id, hpo_id)])
        # csv_writer_rela.writerow([db_disease+':'+db_disease_id, hpo_id,db_disease, qualifier, evidence_code,
        #                                                                          frequency_modi,aspect])

        if not hpo_id in list_symptoms_ids:
            list_symptoms_ids.append((hpo_id))

        # many diseases have more than one abnormal phenotype, but the disease need to be added only one time
        if db_disease_id in list_disease_ids:
            continue
        # write disease into csv
        csv_writer.writerow([db_disease_id, '|'.join(db_disease_name), db_disease_id.split(':')[0]])

        # add disease id to list
        list_disease_ids.append(db_disease_id)

    print('number of disease symptoms relationships:' + str(len(dict_disease_symptom_hpo_pair_to_information)))
    print('number of hpo:' + str(len(list_symptoms_ids)))
    print('number of disease:' + str(len(list_disease_ids)))


'''
Write the combined relationship information into csv
'''


def write_rela_info_into_csv():
    for (db_disease, hpo_id), dict_rela_info in dict_disease_symptom_hpo_pair_to_information.items():
        info_list = [db_disease, hpo_id]
        # print(dict_rela_info)
        for property in list_of_rela_properties:
            if property in ['disease_id', 'phenotype_id']:
                continue
            elif property=='source':
                property='reference_id'
            info_list.append('|'.join(filter(None, dict_rela_info[property])))
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
