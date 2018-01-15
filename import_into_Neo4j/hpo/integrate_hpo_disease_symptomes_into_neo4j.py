# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:14:27 2017

@author: cassandra
"""

from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
from itertools import groupby

reload(sys)
# set default encoding on utf-8
sys.setdefaultencoding('utf-8')

# dictionary with pair(disease_id, HPO id) and qualifier, db_reference, evidence code, frequency modifier
dict_disease_symptom_hpo_pair_to_information = {}

# list of all disease IDs
list_disease_ids = []

# list of all hpo symptoms ids
list_symptoms_ids = []

# file counter
file_counter = 1
# maximal number of queries for a commit block
constrain_number = 20000
# maximal number of queries in a file
creation_max_in_file = 1000000

# open cypher file
cypher_file = open('integrate_hpo_into_neo4j_' + str(file_counter) + '.cypher', 'w')
cypher_file.write('begin \n')

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
    6 	Evidence code: 	how the information was gathered
    7 	Onset modifier: A term-id from the HPO-sub-ontology below the term “Age of onset” (HP:0003674). 	
    8 	Frequency modifier: A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279) 	
    9 	With: can have information  about characteristics 
    10 	Aspect: only with O (Phenotypic abnormality) 	
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
    for line in f:

        splitted = line.split('\t')
        db_disease = splitted[0]
        db_disease_id = splitted[1]
        db_disease_name = splitted[2].lower()
        qualifier = splitted[3]
        hpo_id = splitted[4]
        reference_id = splitted[5]
        evidence_code = splitted[6]
        frequency_modi = splitted[8]
        aspect = splitted[10]
        # O stands for phenotypic abnormality
        if aspect != 'O':
            continue
        dict_disease_symptom_hpo_pair_to_information[(db_disease+':'+db_disease_id, hpo_id)] = [qualifier, reference_id, evidence_code,
                                                                                 frequency_modi]
        # remember the different frequency identifier
        if not frequency_modi in dict_hpo_frequency:
            dict_hpo_frequency[frequency_modi] = []

        if not hpo_id in list_symptoms_ids:
            list_symptoms_ids.append((hpo_id))

        # many diseases have more than one abnormal phenotype, but the disease need to be added only one time
        if db_disease_id in list_disease_ids:
            continue

        create_text = 'Create (:HPOdisease{id: "%s" , name: "%s", source: "%s"});\n' % (
            db_disease + ':' + db_disease_id, db_disease_name, db_disease)

        # add disease id to list
        list_disease_ids.append(db_disease+':'+db_disease_id)

        counter_create += 1
        cypher_file.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            cypher_file.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                cypher_file.close()
                cypher_file = open('integrate_hpo_into_neo4j_' + str(file_counter) + '.cypher', 'w')
                cypher_file.write('begin \n')
                file_counter += 1
            else:
                cypher_file.write('begin \n')

    cypher_file.write('commit \n begin \n')
    cypher_file.write('Create Constraint On (node:HPOdisease) Assert node.id Is Unique; \n')
    cypher_file.write('commit \n begin \n')

    print('number of disease symptoms relationships:' + str(len(dict_disease_symptom_hpo_pair_to_information)))
    print('number of hpo:' + str(len(list_symptoms_ids)))
    print('number of disease:' + str(len(list_disease_ids)))


# use to delimet between the blocks
def is_data(line):
    return True if line.strip() else False


# file path to HPO data source
file_name = 'hpo.obo'

'''
group the hpo terms together and get the information from the different terms
and integrate the symptoms which are part of the disease-symptom relationship.
'''


def get_hpo_information_and_map_to_umls():
    # counter of queries
    counter_create = 0

    global cypher_file
    global file_counter
    with open(file_name) as f:
        for (key, group) in groupby(f, is_data):
            #            print(key)
            if key:
                header = group.next().rstrip('\n')

                if header.find('[Term]') == -1:
                    continue

                use_full_hpo_id = True
                # is a frequency information
                is_a_frequency_information = False
                # dictionary for all values
                dict_all_info = {}
                # go through all properties of the hpo id
                for info in group:
                    (key_term, value) = [element.strip() for element in info.split(":", 1)]
                    # check if the id is part of at least one relationship
                    if key_term == 'id':
                        if (not value in list_symptoms_ids) and (not value in dict_hpo_frequency):
                            use_full_hpo_id = False
                            break
                        elif value in dict_hpo_frequency:
                            is_a_frequency_information = True
                    # for som properties more than one value appears
                    if not key_term in dict_all_info:
                        dict_all_info[key_term] = [value]
                    else:
                        dict_all_info[key_term].append(value)
                #                    print(key_term)
                #                    print(value)

                # only for useful hpo ids
                if use_full_hpo_id:
                    if not is_a_frequency_information:
                        create_text = 'Create (:HPOsymptom{'
                        # add all properties to node which hpo has
                        for key, list_information in dict_all_info.items():
                            modify_list_informationan = []
                            for info in list_information:
                                info = info.replace('"', '').replace("'", "").replace("\\", "")
                                modify_list_informationan.append(info)
                            create_text = create_text + key + ": '" + "|".join(modify_list_informationan) + "' ,"
                        create_text = create_text[0:-1] + '});\n'
                        counter_create += 1
                        cypher_file.write(create_text)
                        # test if a new commit block or new file need to be generated
                        if counter_create % constrain_number == 0:
                            cypher_file.write('commit \n')
                            if counter_create % creation_max_in_file == 0:
                                cypher_file.close()
                                cypher_file = open('integrate_hpo_into_neo4j_' + str(file_counter) + '.cypher', 'w')
                                cypher_file.write('begin \n')
                                file_counter += 1
                            else:
                                cypher_file.write('begin \n')
                    else:
                        identifier = dict_all_info['id'][0]
                        name = dict_all_info['name'][0]
                        definition = dict_all_info['def'][0]
                        dict_hpo_frequency[identifier] = [name, definition]
    print(counter_create)
    cypher_file.write('commit \n begin \n')
    cypher_file.write('Create Constraint On (node:HPOsymptom) Assert node.id Is Unique; \n')
    cypher_file.write('commit \n begin \n')


'''
generate cypher file for the disease symptom connections, but only for the pairs where hpo
has a umls cui.
'''


def add_connection_to_cypher_file():
    # count connection queries
    counter_connection = 0
    global cypher_file
    global file_counter

    for (disease_id, hpo_id), information in dict_disease_symptom_hpo_pair_to_information.items():

        qualifier = information[0]
        reference_id = information[1]
        evidence_code = information[2]
        frequency_modi = information[3]
        frequency_name = dict_hpo_frequency[frequency_modi][0] if frequency_modi != '' else ''
        frequency_definition = dict_hpo_frequency[frequency_modi][1] if frequency_modi != '' else ''
        url = 'http://compbio.charite.de/hpoweb/showterm?disease=' + reference_id

        query = '''MATCH (n:HPOdisease{id:"%s"}),(s:HPOsymptom{id:"%s"}) 
            Create (n)-[:present{version:'phenotype_annotation.tab 2017-10-09 10:47',unbiased:'false',source:'%s',qualifier:'%s', efidence_code:'%s', frequency_modifier:'%s', frequency_definition:'%s', url:"%s"}]->(s); \n  '''
        query = query % (
        disease_id, hpo_id, reference_id, qualifier, evidence_code, frequency_name, frequency_definition, url)

        counter_connection += 1
        cypher_file.write(query)
        if counter_connection % constrain_number == 0:
            cypher_file.write('commit \n')
            if counter_connection % creation_max_in_file == 0:
                cypher_file.close()
                cypher_file = open('integrate_hpo_into_neo4j_' + str(file_counter) + '.cypher', 'w')
                cypher_file.write('begin \n')
                file_counter += 1
            else:
                cypher_file.write('begin \n')

    cypher_file.write('commit')


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather disease symptoms pairs and add disease to cypher file')
    gather_all_disease_symptom_information_from_HPO()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather symptoms information and integrate symptoms into neo4j')

    get_hpo_information_and_map_to_umls()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship information into a cypher file')

    add_connection_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
