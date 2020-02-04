"""
Created on Tue Feb 04 08:40:47 2020

@author: ckoenigs
"""
from py2neo import Graph
import datetime
import sys, csv


# dictionary with all compounds with id (drugbank id) as key and class DrugHetionet as value
dict_all_drug = {}

# dictionary with all aeolus drugs with key drug_concept_id (OHDSI ID) and value is class Drug_Aeolus
dict_aeolus_drugs = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j():
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    # g = Graph("http://localhost:7474/db/data/")
    g = Graph("http://bimi:7475/db/data/", bolt=False, auth=("neo4j", "test"))

# path to directory
path_of_directory = ''

# rela csv files
file_mapped=open('drug/mapped_rela_se.csv','w',encoding='utf-8')
csv_mapped=csv.writer(file_mapped)

file_new=open('drug/new_rela_se.csv','w',encoding='utf-8')
csv_new=csv.writer(file_new)


file_mapped_disease=open('drug/mapped_rela_disease.csv','w',encoding='utf-8')
csv_mapped_disease=csv.writer(file_mapped_disease)

file_new_disease=open('drug/new_rela_disease.csv','w',encoding='utf-8')
csv_new_disease=csv.writer(file_new_disease)

header=['chemical_id','disease_sideeffect_id', "countA","prr_95_percent_upper_confidence_limit","prr","countB","prr_95_percent_lower_confidence_limit","ror","ror_95_percent_upper_confidence_limit","ror_95_percent_lower_confidence_limit","countC","drug_outcome_pair_count","countD","ror_min","ror_max","prr_min","prr_max"]
csv_mapped.writerow(header)
csv_new.writerow(header)
csv_mapped_disease.writerow(header)
csv_new_disease.writerow(header)


# connection infos between a drug-side effect pair
dict_connection_information = {}
# connection infos between a drug-disease pair
dict_connection_information_to_disease={}


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


def get_aeolus_connection_information_in_dict(query_search,dict_connection_information_for, number_of_compound_to_work_with,property_label):
    query = '''Match (c:Compound{aeolus:'yes'}) Where not exists(c.%s)  Set c.%s='yes' Return c.identifier Limit ''' + str(
        number_of_compound_to_work_with) + ''' Match (c:Compound)-[:equal_to_Aeolus_drug]-(r) With c, collect(r.drug_concept_id) as aeolus_ids Return c.identifier, aeolus_ids '''
    query=query %(property_label,property_label)
    results = g.run(query)
    for mapped_id, drug_concept_ids, in results:
        string_drug_concept_ids='","'.join()
        query_search = query_search % (drug_concept_ids)
        results = g.run(query_search)

        for connection, identifier, in results:
            countA = int(connection['countA']) if connection['countA'] != '\N' else 0
            prr_95_percent_upper_confidence_limit = float(connection['prr_95_percent_upper_confidence_limit']) if \
                connection['prr_95_percent_upper_confidence_limit'] != '\N' else 0
            prr = float(connection['prr']) if connection['prr'] != '\N' else 0
            countB = float(connection['countB']) if connection['countB'] != '\N' else 0
            prr_95_percent_lower_confidence_limit = float(connection['prr_95_percent_lower_confidence_limit']) if \
                connection['prr_95_percent_lower_confidence_limit'] != '\N' else 0
            ror = float(connection['ror']) if connection['ror'] != '\N' else 0
            ror_95_percent_upper_confidence_limit = float(connection['ror_95_percent_upper_confidence_limit']) if \
                connection['ror_95_percent_upper_confidence_limit'] != '\N' else 0
            ror_95_percent_lower_confidence_limit = float(connection['ror_95_percent_lower_confidence_limit']) if \
                connection['ror_95_percent_lower_confidence_limit'] != '\N' else 0
            countC = float(connection['countC']) if connection['countC'] != '\N' else 0
            drug_outcome_pair_count = float(connection['drug_outcome_pair_count']) if connection[
                                                                                          'drug_outcome_pair_count'] != '\N' else 0
            countD = float(connection['countD']) if connection['countD'] != '\N' else 0

    #            mapped_id=dict_aeolus_drugs[drug_concept_id].mapped_id

        if not (mapped_id, identifier) in dict_connection_information_for:
            dict_connection_information_for[(mapped_id, identifier)] = [[countA],
                                                               [prr_95_percent_upper_confidence_limit], [prr],
                                                               [countB],
                                                               [prr_95_percent_lower_confidence_limit], [ror],
                                                               [ror_95_percent_upper_confidence_limit],
                                                               [ror_95_percent_lower_confidence_limit],
                                                               [countC], [drug_outcome_pair_count], [countD]]
        else:
            dict_connection_information_for[(mapped_id, identifier)][0].append(countA)
            dict_connection_information_for[(mapped_id, identifier)][1].append(prr_95_percent_upper_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][2].append(prr)
            dict_connection_information_for[(mapped_id, identifier)][3].append(countB)
            dict_connection_information_for[(mapped_id, identifier)][4].append(prr_95_percent_lower_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][5].append(ror)
            dict_connection_information_for[(mapped_id, identifier)][6].append(ror_95_percent_upper_confidence_limit)
            dict_connection_information_for[(mapped_id, identifier)][7].append(ror_95_percent_lower_confidence_limit)
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


def integrate_connection_from_aeolus_in_hetionet(dict_connection_information_for, query,csv_new, csv_mapped):
    number_of_new_connection = 0
    number_of_updated_connection = 0


    for (mapped_id, identifier), information_lists in dict_connection_information_for.items():
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

        query = query % (mapped_id, identifier)
        connections_exist = g.run(query)
        first_connection = connections_exist.evaluate()
        if first_connection == None:
            csv_new.writerow([mapped_id, identifier, countA, prr_95_percent_upper_confidence_limit, prr, countB,
                             prr_95_percent_lower_confidence_limit, ror, ror_95_percent_upper_confidence_limit,
                             ror_95_percent_lower_confidence_limit, countC, drug_outcome_pair_count, countD, ror_min,
                             ror_max, prr_min, prr_max])
            number_of_new_connection += 1
        else:
            resource = first_connection['resource'] if first_connection['resource'] != None else []
            if not 'AEOLUS' in resource:
                resource.append('AEOLUS')
            resource = '|'.join(resource)
            how_often = str(int(first_connection['how_often_appears']) + 1) if first_connection['how_often_appears'] != None else '1'
            csv_mapped.writerow([mapped_id, identifier, countA, prr_95_percent_upper_confidence_limit, prr, countB,
                             prr_95_percent_lower_confidence_limit, ror, ror_95_percent_upper_confidence_limit,
                             ror_95_percent_lower_confidence_limit, countC, drug_outcome_pair_count, countD, how_often,
                             resource, ror_min, ror_max, prr_min, prr_max])
            number_of_updated_connection += 1


    print('number of new connection:' + str(number_of_new_connection))
    print('number of update connection:' + str(number_of_updated_connection))


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    query='''Match (c:Compound{aeolus:'yes'}) Return count(c) '''
    number_of_compound_nodes_which_are_connect_with_aeolus=0
    results=g.run(query)
    for number, in results:
        number_of_compound_nodes_which_are_connect_with_aeolus=number

    number_of_compounds_at_once=100

    running_times=int(number_of_compound_nodes_which_are_connect_with_aeolus/number_of_compounds_at_once)+1

    # because every aeolus drug has so many relationships only part for part can be integrated
    for x in range(0, running_times):
        print(x)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('get the aeolus information')

        query = '''Match (n:AeolusDrug)-[l:Causes]->(r:AeolusOutcome)--(b:SideEffect) Where n.drug_concept_id in ["%s"] Return l,b.identifier '''
        get_aeolus_connection_information_in_dict( query ,dict_connection_information, number_of_compounds_at_once,'integrated')

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())

        query = '''Match (n:AeolusDrug)-[l:Causes]->(r:AeolusOutcome)--(b:Disease) Where n.drug_concept_id in ["%s"]  Return l,b.identifier '''
        get_aeolus_connection_information_in_dict(query,dict_connection_information_to_disease,number_of_compounds_at_once,'integrated_disease')

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Integrate connection into hetionet')


        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('integrate aeolus drugs into hetionet')
        integrate_connection_from_aeolus_in_hetionet(dict_connection_information, '''Match (c:Compound{identifier:"%s"})-[l:CAUSES_CcSE]-(r:SideEffect{identifier:"%s"}) Return l ''' ,csv_new, csv_mapped)

        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())

        integrate_connection_from_aeolus_in_hetionet(dict_connection_information,'''Match (c:Compound{identifier:"%s"})-[l:INDUCES_CcD]-(r:Disease{identifier:"%s"}) Return l ''', csv_new_disease, csv_mapped_disease)

    # all the cuases relationship which are not in aeolus get the property aeolus='no'
    h = open('cypher_map/map_connection_of_aeolus_in_hetionet.cypher', 'a')
    h.write('begin \n')
    cypher_exra.write('begin \n')

    query = ''' Match ()-[l:CAUSES_CcSE]-() Where not exists(l.aeolus)
        Set l.aeolus='no'; \n '''
    h.write(query)
    cypher_exra.write(query)
    h.write('commit')
    cypher_exra.write('commit')
    h.close()
    query='''Match (c:Compound) Where exists(c.integrated) Remove c.integrated'''
    g.run(query)

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
