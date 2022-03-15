# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 20:05:54 2017

@author: Cassandra
"""
import datetime
import sys

import csv


class Outcome(object):
    """
    Attribute:
        concept_code: string (MedDRA ID)
        name: string
        outcome_concept_id: string (OHDSI ID)
        snomed_outcome_concept_id: string
        vocabulary_id: string (defined the concept id: here is MedDRA)
    """

    def __init__(self, outcome_concept_id, snomed_outcome_concept_id):
        self.outcome_concept_id = outcome_concept_id
        self.snomed_outcome_concept_id = snomed_outcome_concept_id

    def set_rest_propertys(self, name, vocabulary_id, concept_code):
        self.name = name
        self.vocabulary_id = vocabulary_id
        self.concept_code = concept_code


class Drug(object):
    """
    Attribute:
        concept_code: string (RxNorm CUI)
        drug_concept_id: string (OHDSI ID)
        name: string
        vocabulary_id: string (here evertime RxNorm)
    """

    def __init__(self, drug_concept_id):
        self.drug_concept_id = drug_concept_id

    def set_name(self, name, vocabulary_id, concept_code):
        self.name = name
        self.vocabulary_id = vocabulary_id
        self.concept_code = concept_code


class Edge(object):
    """
    Attribute:
        drug_concept_id: string (OHDSI ID)
        outcome_concept_id (OHDSI ID)
        countA: string (number of continence table at position a)
        countB: string (number of continence table at position b)
        countC: string (number of continence table at position c)
        countD: string (number of continence table at position d)
        snomed_outcome_concept_id: string  muss noch raus
        drug_outcome_pair_count: string (integer)
        prr: string (proportional reporting rate: float)
        prr_95_percent_upper_confidence_limit: string (float)
        prr_95_percent_lower_confidence_limit: string (float)
        ror: string (reporting odds ration: float)
        ror_95_percent_upper_confidence_limit: string (float)
        ror_95_percent_lower_confidence_limit: string (float)

    """

    def __init__(self, drug_concept_id, outcome_concept_id, snomed_outcome_concept_id, drug_outcome_pair_count, prr,
                 prr_95_percent_upper_confidence_limit,
                 prr_95_percent_lower_confidence_limit, ror, ror_95_percent_upper_confidence_limit,
                 ror_95_percent_lower_confidence_limit):
        self.drug_concept_id = drug_concept_id
        self.outcome_concept_id = outcome_concept_id
        self.snomed_outcome_concept_id = snomed_outcome_concept_id
        self.drug_outcome_pair_count = drug_outcome_pair_count if not drug_outcome_pair_count == '\\N' else ''
        self.prr = prr if not prr == '\\N' else ''
        self.prr_95_percent_upper_confidence_limit = prr_95_percent_upper_confidence_limit if not prr_95_percent_upper_confidence_limit == '\\N' else ''
        self.prr_95_percent_lower_confidence_limit = prr_95_percent_lower_confidence_limit if not prr_95_percent_lower_confidence_limit == '\\N' else ''
        self.ror = ror if not ror == '\\N' else ''
        self.ror_95_percent_upper_confidence_limit = ror_95_percent_upper_confidence_limit if not ror_95_percent_upper_confidence_limit == '\\N' else ''
        self.ror_95_percent_lower_confidence_limit = ror_95_percent_lower_confidence_limit if not ror_95_percent_lower_confidence_limit == '\\N' else ''

    def set_contingence_table(self, a, b, c, d):
        self.countA = a if not a == '\\N' else ''
        self.countB = b if not b == '\\N' else ''
        self.countC = c if not c == '\\N' else ''
        self.countD = d if not d == '\\N' else ''


# path to data for windows
if len(sys.argv) > 1:
    # filepath= "file:///"+sys.argv[1]
    filepath = sys.argv[1]
    path_of_directory = sys.argv[2]
else:
    sys.exit('need some arguments (aeolus)')

# concept dictionary
# key:concept_id
# value: 0:concept_name,1:domain_id,2:vocabulary_id,3:concept_class_id,4:standard_concept,5:concept_code
dict_concept = {}

# dictionary primary_id to drug concept id
dict_primaryid_to_concept_id = {}

# dictionary isr to drug concept id
dict_isr_to_concept_id = {}


def check_for_entry(dictionary, case_id, drug_seq, drug_concept_id):
    """
    add concept into dictionary order by case id the drug seq and add to a set
    :param dictionary: dictionary
    :param case_id: string
    :param drug_seq: string
    :param drug_concept_id: string
    """
    if not case_id in dictionary:
        dictionary[case_id] = {}
        dictionary[case_id][drug_seq] = set([drug_concept_id])
    elif drug_seq not in dictionary[case_id]:
        dictionary[case_id][drug_seq] = set([drug_concept_id])
    else:
        dictionary[case_id][drug_seq].add(drug_concept_id)


"""
import standard case drug.tsv and put all information into the dictionary
properties file:
    1: primaryid
    2: isr
    3: drug_seq
    4: role_cod
    5: standard concept id
"""


def load_standard_case_drug():
    file = open(filepath + 'standard_case_drug.tsv', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    for line in csv_reader:
        primaryid = line[0]
        isr = line[1]
        drug_seq = line[2]
        concept_id = line[4]
        if primaryid != '':
            check_for_entry(dict_primaryid_to_concept_id, primaryid, drug_seq, concept_id)
        else:
            check_for_entry(dict_isr_to_concept_id, isr, drug_seq, concept_id)


# to have every induce tuple only one time
set_induce_tuples = set()


def check_for_drug_concepts_and_write_into_file(dictionary, case_id, csv_writer, drug_seq, indication_concept_id):
    """
    check for case drugs and write into file
    :param dictionary: dictionary
    :param case_id: string
    :param csv_writer: csv writer
    :param drug_seq: string
    :param indication_concept_id: string
    """
    if case_id in dictionary:
        if drug_seq in dictionary[case_id]:
            if len(dictionary[case_id][drug_seq]) > 1:
                print(dictionary[case_id][drug_seq])
            for drug_concept_id in dictionary[case_id][drug_seq]:
                if (drug_concept_id, indication_concept_id) in set_induce_tuples:
                    continue
                csv_writer.writerow([drug_concept_id, indication_concept_id])
                set_induce_tuples.add((drug_concept_id, indication_concept_id))


"""
import standard_case_indication.tsv and put all information into the dictionary
properties file:
    0: primaryid
    1: isr
    2: indi_drug_seq
    3: indi_pt
    4: indication concept id
    5: snomed indication concept id
"""


def load_standard_case_indication():
    file = open(filepath + 'standard_case_indication.tsv', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    write_file = open('output/indications.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(write_file)
    csv_writer.writerow(['drug_concept_id', 'indication_concept_id'])
    for line in csv_reader:
        primaryid = line[0]
        isr = line[1]
        drug_seq = line[2]
        indication_concept_id = line[4]
        if primaryid != '':
            check_for_drug_concepts_and_write_into_file(dict_primaryid_to_concept_id, primaryid, csv_writer, drug_seq,
                                                        indication_concept_id)
        else:
            check_for_drug_concepts_and_write_into_file(dict_isr_to_concept_id, isr, csv_writer, drug_seq,
                                                        indication_concept_id)


#
'''
import concept.tsv and put all information into the dictionary
properties file:
    1: concept_id
    2: concept name
    3: domain_id
    4: vocabulary_id (ex:Mesh, snomed-ct)
    5: concept_class_id
    6: standard_concept 
    7: concept_code	
    8: valid_start_date	
    9: valid_end_date
    10: invalid_reason
'''


def load_concept():
    # fobj=open(filepath+ "test_concept.tsv")
    fobj = open(filepath + "concept.tsv", 'r', encoding='utf-8')
    i = 1
    j = 1
    for line in fobj:
        splitted = line.split('\t')
        concept_id = splitted[0]
        concept_name = splitted[1]
        domain_id = splitted[2]
        vocabulary_id = splitted[3]
        concept_class_id = splitted[4]
        standard_concept = splitted[5]
        concept_code = splitted[6].replace('\n', '')
        dict_concept[concept_id] = [concept_name, domain_id, vocabulary_id, concept_class_id, standard_concept,
                                    concept_code]
        i += 1
        if i == 1000000 * j:
            j += 1
            print(i)


# dictionary of all edges with (drug_concept_id, outcome_concept_id) as key and class Edge as value
dict_edge = {}
# dictionary with drug_concept_id as key and class drug as value
dict_drugs = {}
# dictionary with outcome_concept_id as key and class outcome as value
dict_outcomes = {}

'''
import standard_drug_outcome_statistics.tsv and put information in the dictionaries
properties of file:
     1: drug_concept_id   
     2: outcome_concept_id 
     3: snomed_outcome_concept_id    
     4: case_count
     5: prr
     6: prr_95_percent_upper_confidence_limit
     7: prr_95_percent_lower_confidence_limit
     8: ror
     9: ror_95_percent_upper_confidence_limit
    10: ror_95_percent_lower_confidence_limit
'''


def load_drug_outcome_statistic():
    # fobj=open(filepath+ "test_standard_drug_outcome_statistics.tsv")
    fobj = open(filepath + "standard_drug_outcome_statistics.tsv", "r", encoding='utf-8')
    i = 1
    j = 1
    for line in fobj:
        splitted = line.split('\t')
        drug_concept_id = splitted[0]

        outcome_concept_id = splitted[1]
        snomed_outcome_concept_id = splitted[2] if splitted[2] != '\\N' else '-'
        drug_outcome_pair_count = splitted[3]
        prr = splitted[4]
        prr_95_percent_upper_confidence_limit = splitted[5]
        prr_95_percent_lower_confidence_limit = splitted[6]
        ror = splitted[7]
        ror_95_percent_upper_confidence_limit = splitted[8]
        ror_95_percent_lower_confidence_limit = splitted[9].replace('\n', '')

        drug = Drug(drug_concept_id)
        dict_drugs[drug_concept_id] = drug

        outcome = Outcome(outcome_concept_id, snomed_outcome_concept_id)
        dict_outcomes[outcome_concept_id] = outcome

        edge_class = Edge(drug_concept_id, outcome_concept_id, snomed_outcome_concept_id, drug_outcome_pair_count, prr,
                          prr_95_percent_upper_confidence_limit, prr_95_percent_lower_confidence_limit, ror,
                          ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit)
        dict_edge[(drug_concept_id, outcome_concept_id)] = edge_class
        i += 1

        if i == 1000000 * j:
            j += 1
            print(i)

    print('number of edges:' + str(len(dict_edge)))


#
'''
import standard_drug_outcome_contigency_table.tsv and update the dictionary with edges
properties of file:
     1: drug_concept_id   
     2: outcome_concept_id 
     3: count_a
     4: count_b
     5: count_c
     6: count_d
'''


def load_contingency_table():
    # fobj=open(filepath+ "test_standard_drug_outcome_contingency_table.tsv")
    fobj = open(filepath + "standard_drug_outcome_contingency_table.tsv", "r", encoding='utf-8')

    for line in fobj:
        splitted = line.split('\t')
        #        print(line)
        #        print(splitted)
        drug_concept_id = splitted[0]
        outcome_concept_id = splitted[1]
        if drug_concept_id == '766814' and outcome_concept_id == '37520987':
            print('huu')
        count_a = splitted[2]
        count_b = splitted[3]
        count_c = splitted[4]
        if drug_concept_id == '800878':
            if count_c == '':
                print(outcome_concept_id)
        count_d = splitted[5].replace('\n', '')

        dict_edge[(drug_concept_id, outcome_concept_id)].set_contingence_table(count_a, count_b, count_c, count_d)


'''
generate tsv files in form to use the neo4j-shell and generate cypher file
'''


def create_csv_and_cypher_file_neo4j():
    # cypher file to integrate aeolus into Neo4j
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

    print('drug Create')
    print(datetime.datetime.now())
    file_name_outcome = 'output/outcome.tsv'
    # f = open(file_name_outcome, 'w', newline='', encoding='utf-8')
    f = open(file_name_outcome, 'w', encoding='utf-8')

    # add cypher wuery to cypher file to integrate outcome
    cypher_outcome = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/aeolus/''' + file_name_outcome + '''" As line FIELDTERMINATOR '\\t' Create (:Aeolus_Outcome{outcome_concept_id:line.outcome_concept_id , concept_code: line.concept_code,  name: line.name, snomed_outcome_concept_id: line.snomed_outcome_concept_id, vocabulary_id: line.vocabulary_id });\n'''
    cypher_file.write(cypher_outcome)
    cypher_file.write(':begin \n')
    cypher_file.write('Create Constraint On (node:Aeolus_Outcome) Assert node.outcome_concept_id Is Unique; \n')
    cypher_file.write(':commit \n Call db.awaitIndexes(300) ; \n ')
    # tsv file for outcome
    try:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(('outcome_concept_id', 'concept_code', 'name', 'snomed_outcome_concept_id',
                         'vocabulary_id'))
        for key, value in dict_outcomes.items():
            if value.snomed_outcome_concept_id == '-':
                writer.writerow((key, dict_concept[key][5], dict_concept[key][0], '', dict_concept[key][2]))
            # append_query='''CREATE (out%s:Aeolus_Outcome{concept_code: '%s', name: '%s', outcome_concept_id: %s, vocabulary_id: '%s'}) \n''' %(key,dict_concept[key][5],dict_concept[key][0],key,dict_concept[key][2] )
            else:
                writer.writerow((key, dict_concept[key][5], dict_concept[key][0], value.snomed_outcome_concept_id,
                                 dict_concept[key][2]))
            # append_query='''CREATE (out%s:Aeolus_Outcome{concept_code: '%s', name: '%s', outcome_concept_id: %s, snomed_outcome_concept_id: %s, vocabulary_id: '%s'}) \n''' %(key,dict_concept[key][5],dict_concept[key][0],key,value.snomed_outcome_concept_id,dict_concept[key][2] )

    finally:
        f.close()

    print('drug Create')
    print(datetime.datetime.now())
    file_name_drug = 'output/drug.tsv'
    f = open(file_name_drug, 'w', encoding='utf-8')

    # add cypher query to cypher file for integration of drugs
    # add cypher wuery to cypher file to integrate outcome
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/aeolus/''' + file_name_drug + '''" As line FIELDTERMINATOR '\\t' Create (:Aeolus_Drug{drug_concept_id: line.drug_concept_id, concept_code: line.concept_code, name: line.name, vocabulary_id: line.vocabulary_id });\n'''
    cypher_file.write(query)
    cypher_file.write(' :begin \n')
    cypher_file.write('Create Constraint On (node:Aeolus_Drug) Assert node.drug_concept_id Is Unique; \n')
    cypher_file.write(':commit \n Call db.awaitIndexes(300) ; \n ')

    # tsv file for drugs
    try:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(('drug_concept_id', 'concept_code', 'name', 'vocabulary_id'))

        for key, value in dict_drugs.items():
            writer.writerow((key, dict_concept[key][5], dict_concept[key][0], dict_concept[key][2]))
    finally:
        f.close()

    print('rel Create')
    print(datetime.datetime.now())

    # tsv for relationships
    file_name_drug_outcome = 'output/drug_outcome_relation.tsv'
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/aeolus/''' + file_name_drug_outcome + '''" As line FIELDTERMINATOR '\\t' Match (n1:Aeolus_Drug {drug_concept_id: line.drug_id}), (n2:Aeolus_Outcome {outcome_concept_id: line.adr_id}) Create (n1)-[:Causes{countA: line.countA , countB: line.countB , countC: line.countC , countD: line.countD, drug_outcome_pair_count: line.drug_outcome_pair_count, prr: line.prr, prr_95_percent_upper_confidence_limit: line.prr_95_percent_upper_confidence_limit , prr_95_percent_lower_confidence_limit: line.prr_95_percent_lower_confidence_limit , ror: line.ror , ror_95_percent_upper_confidence_limit: line.ror_95_percent_upper_confidence_limit , ror_95_percent_lower_confidence_limit: line.ror_95_percent_lower_confidence_limit}]->(n2); \n'''
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/aeolus/output/indications.tsv" As line FIELDTERMINATOR '\\t' Match (n1:Aeolus_Drug {drug_concept_id: line.drug_concept_id}), (n2:Aeolus_Outcome {outcome_concept_id: line.indication_concept_id}) Create (n1)-[:Indicates]->(n2); \n'''
    cypher_file.write(query)

    f = open(file_name_drug_outcome, 'w', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, delimiter='\t')
        writer.writerow(('drug_id', 'countA', 'countB', 'countC', 'countD', 'drug_outcome_pair_count',
                         'prr', 'prr_95_percent_upper_confidence_limit', 'prr_95_percent_lower_confidence_limit', 'ror',
                         'ror_95_percent_upper_confidence_limit', 'ror_95_percent_lower_confidence_limit',
                         'adr_id'))

        for key, value in dict_edge.items():
            writer.writerow((value.drug_concept_id, value.countA, value.countB, value.countC, value.countD,
                             value.drug_outcome_pair_count, value.prr, value.prr_95_percent_upper_confidence_limit,
                             value.prr_95_percent_lower_confidence_limit, value.ror,
                             value.ror_95_percent_upper_confidence_limit, value.ror_95_percent_lower_confidence_limit,
                             value.outcome_concept_id))

    finally:
        f.close()

    print('end')
    print(datetime.datetime.now())


def main():
    print('start load in case drug ')
    load_standard_case_drug()

    print('start load in case indication and generate drug-indication file ')
    load_standard_case_indication()

    print('start load in concept ')
    print(datetime.datetime.now())

    load_concept()

    print("start drug outcome statistic ")
    print(datetime.datetime.now())

    load_drug_outcome_statistic()

    print("start drug outcome contigency table")
    print(datetime.datetime.now())

    load_contingency_table()

    print('create tsv and cypher file to integrate aeolus int neo4j')
    print(datetime.datetime.now())
    create_csv_and_cypher_file_neo4j()


if __name__ == "__main__":
    # execute only if run as a script
    main()
