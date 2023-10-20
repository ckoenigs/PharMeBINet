import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary with all compounds with id (drugbank id) as key and class Drugpharmebinet as value
dict_all_drug = {}

# dictionary with all aeolus drugs with key drug_concept_id (OHDSI ID) and value is class Drug_Aeolus
dict_aeolus_drugs = {}


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# path to directory
path_of_directory = ''


def generate_cypher_file():
    """
    Generate cypher file to update or create the relationships in pharmebinet
    :return:
    """
    # relationship queries
    cypher_file = open('output/cypher_rela.cypher', 'w', encoding='utf-8')

    query = ''' Match (c:Chemical{identifier:line.chemical_id}),(r:SideEffect{identifier:line.disease_sideeffect_id})  Create (c)-[:MIGHT_CAUSES_CHmcSE{license:"CC0 1.0",unbiased:false,source:'AEOLUS',countA:line.countA, prr_95_percent_upper_confidence_limit:line.prr_95_percent_upper_confidence_limit, prr:line.prr, countB:line.countB, prr_95_percent_lower_confidence_limit:line.prr_95_percent_lower_confidence_limit, ror:line.ror, ror_95_percent_upper_confidence_limit:line.ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit:line.ror_95_percent_lower_confidence_limit, countC:line.countC, drug_outcome_pair_count:line.drug_outcome_pair_count, countD:line.countD, ror_min:line.ror_min, ror_max:line.ror_max, prr_min:line.prr_min, prr_max:line.prr_max,  aeolus:'yes', resource:['AEOLUS']}]->(r)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/aeolus/drug/new_rela_se.tsv', query)
    cypher_file.write(query)

    query = ''' Match (c:Chemical{identifier:line.chemical_id}),(r:Disease{identifier:line.disease_sideeffect_id})  Create (c)-[:MIGHT_INDUCES_CHmiD{license:"CC0 1.0",unbiased:false,source:'AEOLUS',countA:line.countA, prr_95_percent_upper_confidence_limit:line.prr_95_percent_upper_confidence_limit, prr:line.prr, countB:line.countB, prr_95_percent_lower_confidence_limit:line.prr_95_percent_lower_confidence_limit, ror:line.ror, ror_95_percent_upper_confidence_limit:line.ror_95_percent_upper_confidence_limit, ror_95_percent_lower_confidence_limit:line.ror_95_percent_lower_confidence_limit, countC:line.countC, drug_outcome_pair_count:line.drug_outcome_pair_count, countD:line.countD, ror_min:line.ror_min, ror_max:line.ror_max, prr_min:line.prr_min, prr_max:line.prr_max,  aeolus:'yes', resource:['AEOLUS']}]->(r)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/aeolus/drug/new_rela_disease.tsv',
                                              query)
    cypher_file.write(query)

    cypher_file.close()


# rela tsv files
file_mapped = open('drug/mapped_rela_se.tsv', 'w', encoding='utf-8')
csv_mapped = csv.writer(file_mapped, delimiter='\t')

file_new = open('drug/new_rela_se.tsv', 'w', encoding='utf-8')
csv_new = csv.writer(file_new, delimiter='\t')

file_mapped_disease = open('drug/mapped_rela_disease.tsv', 'w', encoding='utf-8')
csv_mapped_disease = csv.writer(file_mapped_disease, delimiter='\t')

file_new_disease = open('drug/new_rela_disease.tsv', 'w', encoding='utf-8')
csv_new_disease = csv.writer(file_new_disease, delimiter='\t')

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
    query = ''' Match (c)-[:equal_to_Aeolus_drug]-(r:Aeolus_Drug)-[l:Indicates]-(:Aeolus_Outcome)--(d:%s)  Return  c.identifier,  d.identifier '''
    query = query % (label)
    results = g.run(query)

    for record in results:
        [chemical_id, outcome_id] = record.values()
        set_of_tuples.add((chemical_id, outcome_id))


def get_aeolus_connection_information_in_dict(label_search, dict_connection_information_for,
                                              dict_chemical_to_the_other_thing, set_of_indication_pairs):
    """
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
    go through all connection of the mapped aeolus drugs and remember all information in a dictionary
    :param label_search:
    :param dict_connection_information_for:
    :param dict_chemical_to_the_other_thing:
    :param set_of_indication_pairs:
    :return:
    """
    # and toFloat(l.countA)/(toFloat(l.countA)+toFloat(l.countC))>0.0001
    query = '''Match (c:Chemical{aeolus:'yes'}) With c  Match (c)-[:equal_to_Aeolus_drug]-(r:Aeolus_Drug)-[l:Causes]-(:Aeolus_Outcome)--(d:%s) Where toInteger(l.countA)>100 and toFloat(l.countA)/(toFloat(l.countA)+toFloat(l.countB))>0.001  Return c.identifier, l, d.identifier '''
    query = query % (label_search)
    results = g.run(query)
    found_something_with_query = False
    counter_all_rela = 0
    for record in results:
        [mapped_id, connection, identifier] = record.values()
        connection = dict(connection)
        counter_all_rela += 1
        # has oppsite rela!
        if (mapped_id, identifier) in set_of_indication_pairs:
            # print(mapped_id, identifier)
            continue
        found_something_with_query = True
        if mapped_id in dict_chemical_to_the_other_thing:
            dict_chemical_to_the_other_thing[mapped_id].add(identifier)
        else:
            dict_chemical_to_the_other_thing[mapped_id] = set([identifier])
        countA = int(connection['countA']) if connection['countA'] != "\\N" and connection['countA'] != '' else 0
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
                                                                                      'drug_outcome_pair_count'] != '' else 0
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
    print('number of rela:', counter_all_rela)


def integrate_connection_from_aeolus_in_pharmebinet(dict_connection_information_for, csv_new):
    """
    update and generate the relationship CAUSES_CcSE.
    go through all drugbank ID identifier pairs anf combine the information of multiple drugbank Id identifier pairs
    Next step is to check if this connection already exists in pharmebinet, if true then update the relationship
    if false generate the connection with the properties license, unbiased, source, url, the other properties that aeolus has
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
    :param dict_connection_information_for:
    :param csv_new:
    :return:
    """
    number_of_new_connection = 0

    count = 0

    for (mapped_id, identifier), information_lists in dict_connection_information_for.items():
        count += 1
        more_than_one_entry = True if len(information_lists[1]) > 1 else False
        # average of count A
        countA = str(sum(information_lists[0]) / float(len(information_lists[0]))) if more_than_one_entry else str(
            sum(information_lists[0]))
        # average prr 95% upper
        prr_95_percent_upper_confidence_limit = str(
            sum(information_lists[1]) / float(len(information_lists[1]))) if more_than_one_entry else str(
            sum(information_lists[1]))
        # average prr
        prr = str(sum(information_lists[2]) / float(len(information_lists[2]))) if more_than_one_entry else str(
            sum(information_lists[2]))
        # minmum prr
        prr_min = str(min(information_lists[2]))
        # maximu prr
        prr_max = str(max(information_lists[2]))
        # average of count B
        countB = str(sum(information_lists[3]) / float(len(information_lists[3]))) if more_than_one_entry else str(
            sum(information_lists[3]))
        # average prr 95 % lower
        prr_95_percent_lower_confidence_limit = str(
            sum(information_lists[4]) / float(len(information_lists[4]))) if more_than_one_entry else str(
            sum(information_lists[4]))
        # average ror
        ror = str(sum(information_lists[5]) / float(len(information_lists[5]))) if more_than_one_entry else str(
            sum(information_lists[5]))
        # minmum ror
        ror_min = str(min(information_lists[5]))
        # maximum ror
        ror_max = str(max(information_lists[5]))
        # average of ror 95% lower
        ror_95_percent_upper_confidence_limit = str(
            sum(information_lists[6]) / float(len(information_lists[6]))) if more_than_one_entry else str(
            sum(information_lists[6]))
        # average of ror 95% lower
        ror_95_percent_lower_confidence_limit = str(
            sum(information_lists[7]) / float(len(information_lists[7]))) if more_than_one_entry else str(
            sum(information_lists[7]))
        # average of count C
        countC = str(sum(information_lists[8]) / float(len(information_lists[8]))) if more_than_one_entry else str(
            sum(information_lists[8]))
        # average of drug outcome pair
        drug_outcome_pair_count = str(
            sum(information_lists[9]) / float(len(information_lists[9]))) if more_than_one_entry else str(
            sum(information_lists[9]))
        # average of count D
        countD = str(sum(information_lists[10]) / float(len(information_lists[10]))) if more_than_one_entry else str(
            sum(information_lists[10]))

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

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(datetime.datetime.now())
    print('Generate cypher file')

    generate_cypher_file()

    number_of_compounds_at_once = 100

    set_of_indication_pairs = set()
    get_indications('Disease', set_of_indication_pairs)
    get_indications('SideEffect', set_of_indication_pairs)

    global dict_connection_information, dict_connection_information_to_disease, dict_chemical_to_side_effects, dict_chemical_to_diseases
    dict_connection_information = {}
    dict_connection_information_to_disease = {}
    dict_connection_information_to_disease = {}
    dict_chemical_to_side_effects = {}
    dict_chemical_to_diseases = {}

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('get the aeolus information')

    get_aeolus_connection_information_in_dict('SideEffect', dict_connection_information, dict_chemical_to_side_effects,
                                              set_of_indication_pairs)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    get_aeolus_connection_information_in_dict('Disease', dict_connection_information_to_disease,
                                              dict_chemical_to_diseases, set_of_indication_pairs)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate connection into pharmebinet')

    integrate_connection_from_aeolus_in_pharmebinet(dict_connection_information, csv_new)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('integrate aeolus connection into tsv for integration into  pharmebinet')

    integrate_connection_from_aeolus_in_pharmebinet(dict_connection_information_to_disease, csv_new_disease)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
