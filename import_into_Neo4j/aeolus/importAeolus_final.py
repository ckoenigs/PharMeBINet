# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 20:05:54 2017

@author: Cassandra
"""
import datetime
import sys
from py2neo import Graph, Path, authenticate, Node, Relationship

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
else:
    # filepath="file:///c:/Users/Cassandra/Documents/uni/Master/test/aeolus_v1/"
    filepath = "c:/Users/Cassandra/Documents/uni/Master/test/aeolus_v1/"


# concept dictionary
# key:concept_id
# value: 0:concept_name,1:domain_id,2:vocabulary_id,3:concept_class_id,4:standard_concept,5:concept_code
dict_concept = {}

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
    fobj = open(filepath + "concept.tsv")
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
    fobj = open(filepath + "standard_drug_outcome_statistics.tsv")
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
    fobj = open(filepath + "standard_drug_outcome_contingency_table.tsv")

    for line in fobj:
        splitted = line.split('\t')
        #        print(line)
        #        print(splitted)
        drug_concept_id = splitted[0]
        outcome_concept_id = splitted[1]
        count_a = splitted[2]
        count_b = splitted[3]
        count_c = splitted[4]
        count_d = splitted[5].replace('\n', '')

        dict_edge[(drug_concept_id, outcome_concept_id)].set_contingence_table(count_a, count_b, count_c, count_d)

'''
Generate a cypher file for the aeolus nodes drug and outcome and for the aeolus connection.
'''

def generate_cypher_file():
    # file counter
    i = 1
    # number of quereies in a commit block
    constrain_number = 20000
    # maximal number of queries in a file
    creation_max_in_file = 500000

    f = open('Aeolus_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
    f.write('begin \n')
    i += 1
    # query counter
    counter_create = 0
    print('outcome')
    print (datetime.datetime.utcnow())

    # put aeolus outcome queries in cypher file
    for key, value in dict_outcomes.items():
        if value.snomed_outcome_concept_id == '-':
            create_text = 'Create (:AeolusOutcome{outcome_concept_id: "%s", concept_code: "%s",  name: "%s", snomed_outcome_concept_id: "%s", vocabulary_id: "%s" });\n' % (
            key, dict_concept[key][5], dict_concept[key][0], '', dict_concept[key][2])
        else:
            create_text = 'Create (:AeolusOutcome{outcome_concept_id: "%s", concept_code: "%s",  name: "%s", snomed_outcome_concept_id: "%s", vocabulary_id: "%s" });\n' % (
            key, dict_concept[key][5], dict_concept[key][0], value.snomed_outcome_concept_id, dict_concept[key][2])

        counter_create += 1
        f.write(create_text)
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('Aeolus_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit \n begin \n')
    f.write('Create Constraint On (node:AeolusOutcome) Assert node.outcome_concept_id Is Unique; \n')
    f.write('commit \n schema await \n begin \n')

    print('drug')
    # put aeolus drug queries in cypher file
    print (datetime.datetime.utcnow())
    for key, value in dict_drugs.items():

        create_text = 'Create (:AeolusDrug{drug_concept_id: "%s", concept_code: "%s", name: "%s", vocabulary_id: "%s" });\n' % (
        key, dict_concept[key][5], dict_concept[key][0], dict_concept[key][2])
        counter_create += 1
        f.write(create_text)
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('Aeolus_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit \n begin \n')
    f.write('Create Constraint On (node:AeolusDrug) Assert node.drug_concept_id Is Unique; \n')
    f.write('commit \n schema await \n begin \n')

    print('relationships')
    # all aeolus relationships queries in cypher files
    print (datetime.datetime.utcnow())
    for key, value in dict_edge.items():

        create_text = create_text = '''Match (n1:AeolusDrug {drug_concept_id: "%s"}), (n2:AeolusOutcome {outcome_concept_id: "%s"}) Create (n1)-[:Causes{countA: "%s" , countB: "%s" , countC: "%s" , countD: "%s", drug_outcome_pair_count: "%s", prr: "%s", prr_95_percent_upper_confidence_limit: "%s", prr_95_percent_lower_confidence_limit: "%s" , ror: "%s", ror_95_percent_upper_confidence_limit: "%s" , ror_95_percent_lower_confidence_limit: "%s"}]->(n2); \n''' % (
        value.drug_concept_id, value.outcome_concept_id, value.countA, value.countB, value.countC, value.countD,
        value.drug_outcome_pair_count, value.prr, value.prr_95_percent_upper_confidence_limit,
        value.prr_95_percent_lower_confidence_limit, value.ror, value.ror_95_percent_upper_confidence_limit,
        value.ror_95_percent_lower_confidence_limit)
        counter_create += 1
        f.write(create_text)
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('Aeolus_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit')


'''
generate csv files in form to use the neo4j import tool
'''

def load_in_neo4j():
    print('drug Create')
    print (datetime.datetime.utcnow())
    f = open('outcome.csv', 'wt', newline='', encoding='utf-8')

    # csv file for outcome
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(('outcome_concept_id:ID(AeolusOutcome)', 'concept_code', 'name', 'snomed_outcome_concept_id',
                         'vocabulary_id'))
        for key, value in dict_outcomes.items():
            if value.snomed_outcome_concept_id == '-':
                writer.writerow((key, dict_concept[key][5], dict_concept[key][0], '', dict_concept[key][2]))
            # append_query='''CREATE (out%s:AeolusOutcome{concept_code: '%s', name: '%s', outcome_concept_id: %s, vocabulary_id: '%s'}) \n''' %(key,dict_concept[key][5],dict_concept[key][0],key,dict_concept[key][2] )
            else:
                writer.writerow((key, dict_concept[key][5], dict_concept[key][0], value.snomed_outcome_concept_id,
                                 dict_concept[key][2]))
            # append_query='''CREATE (out%s:AeolusOutcome{concept_code: '%s', name: '%s', outcome_concept_id: %s, snomed_outcome_concept_id: %s, vocabulary_id: '%s'}) \n''' %(key,dict_concept[key][5],dict_concept[key][0],key,value.snomed_outcome_concept_id,dict_concept[key][2] )

    finally:
        f.close()

    print('drug Create')
    print (datetime.datetime.utcnow())
    f = open('drug.csv', 'wt', newline='', encoding='utf-8')
    # csv file for drugs
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(('drug_concept_id:ID(AeolusDrug)', 'concept_code', 'name', 'vocabulary_id'))

        for key, value in dict_drugs.items():
            writer.writerow((key, dict_concept[key][5], dict_concept[key][0], dict_concept[key][2]))
    finally:
        f.close()

    print('rel Create')
    print (datetime.datetime.utcnow())

    # csv for relationships

    f = open('drug_outcome_relation.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow((':START_ID(AeolusDrug)', 'countA', 'countB', 'countC', 'countD', 'drug_outcome_pair_count',
                         'prr', 'prr_95_percent_upper_confidence_limit', 'prr_95_percent_lower_confidence_limit', 'ror',
                         'ror_95_percent_upper_confidence_limit', 'ror_95_percent_lower_confidence_limit',
                         ':END_ID(AeolusOutcome)'))

        for key, value in dict_edge.items():
            writer.writerow((value.drug_concept_id, value.countA, value.countB, value.countC, value.countD,
                             value.drug_outcome_pair_count, value.prr, value.prr_95_percent_upper_confidence_limit,
                             value.prr_95_percent_lower_confidence_limit, value.ror,
                             value.ror_95_percent_upper_confidence_limit, value.ror_95_percent_lower_confidence_limit,
                             value.outcome_concept_id))
            # print(value.drug_concept_id,value.countA, value.countB, value.countC, value.countD, value.drug_outcome_pair_count, value.prr, value.prr_95_percent_upper_confidence_limit, value.prr_95_percent_lower_confidence_limit, value.ror,value.ror_95_percent_upper_confidence_limit, value.ror_95_percent_lower_confidence_limit, value.outcome_concept_id)
            # print(key)

    finally:
        f.close()

    print('end')
    print (datetime.datetime.utcnow())


def main():


    print('start load in concept ')
    print (datetime.datetime.utcnow())

    load_concept()

    print("start drug outcome statistic ")
    print (datetime.datetime.utcnow())

    load_drug_outcome_statistic()

    print("start drug outcome contigency table")
    print (datetime.datetime.utcnow())

    load_contingency_table()

    print('load in neo4j the outcomes, drug and connections')
    print (datetime.datetime.utcnow())
    #    load_in_neo4j()

    print('load in neo4j the outcomes, drug and connections')
    print (datetime.datetime.utcnow())
    generate_cypher_file()


if __name__ == "__main__":
    # execute only if run as a script
    main()
