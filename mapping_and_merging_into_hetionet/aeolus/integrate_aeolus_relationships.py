"""
Created on Tue Feb 04 08:40:47 2020

@author: ckoenigs
"""
import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

# dictionary with all compounds with id (drugbank id) as key and class DrugHetionet as value
dict_all_drug = {}

# dictionary with all aeolus drugs with key drug_concept_id (OHDSI ID) and value is class Drug_Aeolus
dict_aeolus_drugs = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# path to directory
path_of_directory = ''

'''
Generate cypher file to update or create the relationships in hetionet
'''


def generate_cypher_file():
    # relationship queries
    cypher_file = open('cypher_rela.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/aeolus/drug/new_rela_se.csv" As line Match (c:Chemical{identifier:line.chemical_id}),(r:SideEffect{identifier:line.disease_sideeffect_id})  Create (c)-[:MIGHT_CAUSES_CmcSE{license:"CC0 1.0",unbiased:false,source:'AEOLUS',countA:line.countA, prr_95_percent_upper_confidence_limit:line.prr_95_percent_upper_confidence_limit, prr:line.prr, countB:line.countB, prr_95_percent_lower_confidence_limit:line.prr_95_percent_lower_confidence_limit, ror:line.ror, ror_95_percent_upper_confidence_limit:line.ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit:line.ror_95_percent_lower_confidence_limit, countC:line.countC, drug_outcome_pair_count:line.drug_outcome_pair_count, countD:line.countD, ror_min:line.ror_min, ror_max:line.ror_max, prr_min:line.prr_min, prr_max:line.prr_max,  aeolus:'yes', resource:['AEOLUS']}]->(r); \n'''
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/aeolus/drug/new_rela_disease.csv" As line Match (c:Chemical{identifier:line.chemical_id}),(r:Disease{identifier:line.disease_sideeffect_id})  Create (c)-[:MIGHT_INDUCES_CmiD{license:"CC0 1.0",unbiased:false,source:'AEOLUS',countA:line.countA, prr_95_percent_upper_confidence_limit:line.prr_95_percent_upper_confidence_limit, prr:line.prr, countB:line.countB, prr_95_percent_lower_confidence_limit:line.prr_95_percent_lower_confidence_limit, ror:line.ror, ror_95_percent_upper_confidence_limit:line.ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit:line.ror_95_percent_lower_confidence_limit, countC:line.countC, drug_outcome_pair_count:line.drug_outcome_pair_count, countD:line.countD, ror_min:line.ror_min, ror_max:line.ror_max, prr_min:line.prr_min, prr_max:line.prr_max,  aeolus:'yes', resource:['AEOLUS']}]->(r); \n'''
    cypher_file.write(query)

    query = ''':begin\n Match (c:Chemical) Where exists(c.integrated) Remove c.integrated;\n :commit\n'''
    cypher_file.write(query)

    query = ''':begin\n Match (c:Chemical) Where exists(c.integrated_disease) Remove c.integrated_disease;\n :commit\n'''
    cypher_file.write(query)

    cypher_file.close()

    # # the general cypher file to update all chemicals and relationship which are not from aeolus
    # cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    #
    # # # all the cuases relationship which are not in aeolus get the property aeolus='no'
    # # query = ''':begin\n Match (a:Chemical)-[l:CAUSES_CcSE]-(:SideEffect) Where not exists(l.aeolus) Set l.aeolus='no'; \n :commit\n  '''
    # # cypher_general.write(query)
    # #
    # # query = ''':begin\n Match (a:Chemical)-[l:INDUCES_CiD]-(:Disease) Where not exists(l.aeolus) Set l.aeolus='no'; \n :commit\n  '''
    # # cypher_general.write(query)
    # #
    # # cypher_general.close()


# rela csv files
file_mapped = open('drug/mapped_rela_se.csv', 'w', encoding='utf-8')
csv_mapped = csv.writer(file_mapped)

file_new = open('drug/new_rela_se.csv', 'w', encoding='utf-8')
csv_new = csv.writer(file_new)

file_mapped_disease = open('drug/mapped_rela_disease.csv', 'w', encoding='utf-8')
csv_mapped_disease = csv.writer(file_mapped_disease)

file_new_disease = open('drug/new_rela_disease.csv', 'w', encoding='utf-8')
csv_new_disease = csv.writer(file_new_disease)

header = ['chemical_id', 'disease_sideeffect_id', "countA", "prr_95_percent_upper_confidence_limit", "prr", "countB",
          "prr_95_percent_lower_confidence_limit", "ror", "ror_95_percent_upper_confidence_limit",
          "ror_95_percent_lower_confidence_limit", "countC", "drug_outcome_pair_count", "countD", "resource", "ror_min",
          "ror_max", "prr_min", "prr_max"]
csv_mapped.writerow(header)
csv_new.writerow(header)
csv_mapped_disease.writerow(header)
csv_new_disease.writerow(header)

# connection infos between a drug-side effect pair
dict_connection_information = {}
# connection infos between a drug-disease pair
dict_connection_information_to_disease = {}

# dictionary chemical to diseases
dict_chemical_to_diseases = {}
# dictionary chemical to side effects
dict_chemical_to_side_effects = {}

def get_indications(label, set_of_tuples):
    """
    get all pair which has an indication connection and add to set
    :param label: string
    """
    query=''' Match (c)-[:equal_to_Aeolus_drug]-(r:AeolusDrug)-[l:Indicates]-(:AeolusOutcome)--(d:%s)  Return  c.identifier,  d.identifier '''
    query = query %(label)
    results=g.run(query)

    for chemical_id, outcome_id, in results:
        set_of_tuples.add((chemical_id,outcome_id))

'''       
dictionary connection (drug ID , SE) and list of information
0:countA	
1:prr_95_percent_upper_confidence_limit	
2:prr	
3:countB	
4:prr_95_percent_lower_confidence_limit	
5:ror	
6:ror_95_percent_upper_confidence_limit	
7:ror_95_percent_lower_confidence_limit	
8:countC	
9:drug_outcome_pair_count	
10.countD
'''

'''
go through all connection of the mapped aeolus drugs and remember all information in a dictionary
'''


def get_aeolus_connection_information_in_dict(label_search, dict_connection_information_for,
                                              number_of_compound_to_work_with, property_label,
                                              dict_chemical_to_the_other_thing, set_of_indication_pairs):
    query = '''Match (c:Chemical{aeolus:'yes'}) Where not exists(c.%s)  Set c.%s='yes' With c Limit ''' + str(
        number_of_compound_to_work_with) + ''' Match (c)-[:equal_to_Aeolus_drug]-(r:AeolusDrug)-[l:Causes]-(:AeolusOutcome)--(d:%s) Where toInteger(l.countA)>100 Return c.identifier, l, d.identifier '''
    query = query % (property_label, property_label, label_search)
    results = g.run(query)
    found_something_with_query = False
    for mapped_id, connection, identifier, in results:
        if (mapped_id, identifier) in set_of_indication_pairs:
            print(mapped_id, identifier)
            continue
        found_something_with_query = True
        if mapped_id in dict_chemical_to_the_other_thing:
            dict_chemical_to_the_other_thing[mapped_id].add(identifier)
        else:
            dict_chemical_to_the_other_thing[mapped_id] = set([identifier])
        countA = int(connection['countA']) if connection['countA'] != "\\N" and connection[''] != '' else 0
        prr_95_percent_upper_confidence_limit = float(connection['prr_95_percent_upper_confidence_limit']) if \
            connection['prr_95_percent_upper_confidence_limit'] != "\\N" and connection[
                'prr_95_percent_upper_confidence_limit'] != '' else 0
        prr = float(connection['prr']) if connection['prr'] != "\\N" and connection['prr'] != '' else 0
        countB = float(connection['countB']) if connection['countB'] != "\\N" and connection['countB'] != '' else 0
        prr_95_percent_lower_confidence_limit = float(connection['prr_95_percent_lower_confidence_limit']) if \
            connection['prr_95_percent_lower_confidence_limit'] != "\\N" and connection[
                'prr_95_percent_lower_confidence_limit'] != '' else 0
        ror = float(connection['ror']) if connection['ror'] != "\\N" and connection['ror'] != '' else 0
        ror_95_percent_upper_confidence_limit = float(connection['ror_95_percent_upper_confidence_limit']) if \
            connection['ror_95_percent_upper_confidence_limit'] != "\\N" and connection[
                'ror_95_percent_upper_confidence_limit'] != '' else 0
        ror_95_percent_lower_confidence_limit = float(connection['ror_95_percent_lower_confidence_limit']) if \
            connection['ror_95_percent_lower_confidence_limit'] != "\\N" and connection[
                'ror_95_percent_lower_confidence_limit'] != '' else 0
        countC = float(connection['countC']) if connection['countC'] != "\\N" and connection['countC'] != '' else 0
        drug_outcome_pair_count = float(connection['drug_outcome_pair_count']) if connection[
                                                                                      'drug_outcome_pair_count'] != "\\N" and \
                                                                                  connection[
                                                                                      ''] != 'drug_outcome_pair_count' else 0
        countD = float(connection['countD']) if connection['countD'] != "\\N" and connection['countD'] != '' else 0

        #            mapped_id=dict_aeolus_drugs[drug_concept_id].mapped_id

        if not (mapped_id, identifier) in dict_connection_information_for:
            dict_connection_information_for[(mapped_id, identifier)] = [[countA],
                                                                        [prr_95_percent_upper_confidence_limit],
                                                                        [prr],
                                                                        [countB],
                                                                        [prr_95_percent_lower_confidence_limit],
                                                                        [ror],
                                                                        [ror_95_percent_upper_confidence_limit],
                                                                        [ror_95_percent_lower_confidence_limit],
                                                                        [countC], [drug_outcome_pair_count],
                                                                        [countD]]
        else:
            dict_connection_information_for[(mapped_id, identifier)][0].append(countA)
            dict_connection_information_for[(mapped_id, identifier)][1].append(
                prr_95_percent_upper_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][2].append(prr)
            dict_connection_information_for[(mapped_id, identifier)][3].append(countB)
            dict_connection_information_for[(mapped_id, identifier)][4].append(
                prr_95_percent_lower_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][5].append(ror)
            dict_connection_information_for[(mapped_id, identifier)][6].append(
                ror_95_percent_upper_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][7].append(
                ror_95_percent_lower_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][8].append(countC)
            dict_connection_information_for[(mapped_id, identifier)][9].append(drug_outcome_pair_count)
            dict_connection_information_for[(mapped_id, identifier)][10].append(countD)


'''
update and generate the relationship CAUSES_CcSE.
go through all drugbank ID identifier pairs anf combine the information of multiple drugbank Id identifier pairs
Next step is to check if this connection already exists in Hetionet, if true then update the relationship
if false generate the connection with the properties licence, unbiased, source, url, the other properties that aeolus has
countA	
prr_95_percent_upper_confidence_limit	
prr	
prr_min
prr_max
countB	
prr_95_percent_lower_confidence_limit	
ror	
ror_min
ror_max
ror_95_percent_upper_confidence_limit	
ror_95_percent_lower_confidence_limit	
countC	
drug_outcome_pair_count	
countD
'''


def integrate_connection_from_aeolus_in_hetionet(dict_connection_information_for,  csv_new):
    number_of_new_connection = 0

    count = 0

    for (mapped_id, identifier), information_lists in dict_connection_information_for.items():
        count += 1
        # average of count A
        countA = str(sum(information_lists[0]) / float(len(information_lists[0])))
        # average prr 95% upper
        prr_95_percent_upper_confidence_limit = str(sum(information_lists[1]) / float(len(information_lists[1])))
        # average prr
        prr = str(sum(information_lists[2]) / float(len(information_lists[2])))
        # minmum prr
        prr_min = str(min(information_lists[2]))
        # maximu prr
        prr_max = str(max(information_lists[2]))
        # average of count B
        countB = str(sum(information_lists[3]) / float(len(information_lists[3])))
        # average prr 95 % lower
        prr_95_percent_lower_confidence_limit = str(sum(information_lists[4]) / float(len(information_lists[4])))
        # average ror
        ror = str(sum(information_lists[5]) / float(len(information_lists[5])))
        # minmum ror
        ror_min = str(min(information_lists[5]))
        # maximum ror
        ror_max = str(max(information_lists[5]))
        # average of ror 95% lower
        ror_95_percent_upper_confidence_limit = str(sum(information_lists[6]) / float(len(information_lists[6])))
        # average of ror 95% lower
        ror_95_percent_lower_confidence_limit = str(sum(information_lists[7]) / float(len(information_lists[7])))
        # average of count C
        countC = str(sum(information_lists[8]) / float(len(information_lists[8])))
        # average of drug outcome pair
        drug_outcome_pair_count = str(sum(information_lists[9]) / float(len(information_lists[9])))
        # average of count D
        countD = str(sum(information_lists[10]) / float(len(information_lists[10])))

        csv_new.writerow([mapped_id, identifier, countA, prr_95_percent_upper_confidence_limit, prr, countB,
                          prr_95_percent_lower_confidence_limit, ror, ror_95_percent_upper_confidence_limit,
                          ror_95_percent_lower_confidence_limit, countC, drug_outcome_pair_count, countD, "AEOLUS",
                          ror_min, ror_max, prr_min, prr_max])
        number_of_new_connection += 1

    print('number of new connection:' + str(number_of_new_connection))
    print('all rela:', count)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(datetime.datetime.utcnow())
    print('Generate cypher file')

    generate_cypher_file()

    query = '''Match (c:Chemical{aeolus:'yes'}) Return count(c) '''
    number_of_compound_nodes_which_are_connect_with_aeolus = 0
    results = g.run(query)
    for number, in results:
        number_of_compound_nodes_which_are_connect_with_aeolus = number

    number_of_compounds_at_once = 100

    set_of_indication_pairs=set()
    get_indications('Disease',set_of_indication_pairs)
    get_indications('SideEffect', set_of_indication_pairs)

    running_times = int(number_of_compound_nodes_which_are_connect_with_aeolus / number_of_compounds_at_once) + 1

    # because every aeolus drug has so many relationships only part for part can be integrated
    for x in range(0, running_times):
        print(x)
        global dict_connection_information, dict_connection_information_to_disease, dict_chemical_to_side_effects, dict_chemical_to_diseases
        dict_connection_information = {}
        dict_connection_information_to_disease = {}
        dict_chemical_to_side_effects = {}
        dict_chemical_to_diseases = {}

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('get the aeolus information')

        get_aeolus_connection_information_in_dict('SideEffect', dict_connection_information,
                                                  number_of_compounds_at_once,
                                                  'integrated', dict_chemical_to_side_effects, set_of_indication_pairs)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())

        get_aeolus_connection_information_in_dict('Disease', dict_connection_information_to_disease,
                                                  number_of_compounds_at_once, 'integrated_disease',
                                                  dict_chemical_to_diseases, set_of_indication_pairs)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Integrate connection into hetionet')

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('integrate aeolus connection into csv for integration into  hetionet')
        integrate_connection_from_aeolus_in_hetionet(dict_connection_information, csv_new)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())

        integrate_connection_from_aeolus_in_hetionet(dict_connection_information_to_disease, csv_new_disease)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
