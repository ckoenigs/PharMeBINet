import datetime
import csv, time, sys
import numpy as np

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# tsv files for integrate the different realtionships into pharmebinet
csvfile_induces = open('chemical_disease/induces.tsv', 'w', encoding='utf-8')
writer_induces = csv.writer(csvfile_induces, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_induces.writerow(
    ['ChemicalID', 'DiseaseID', 'omimIDs', 'directEvidences', 'pubMed_ids', 'inferenceScores', 'inferenceGeneSymbols'])

csvfile_treat = open('chemical_disease/treat.tsv', 'w', encoding='utf-8')
writer_treat = csv.writer(csvfile_treat, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_treat.writerow(
    ['ChemicalID', 'DiseaseID', 'omimIDs', 'directEvidences', 'pubMed_ids', 'inferenceScores', 'inferenceGeneSymbols'])

csvfile_associated = open('chemical_disease/associated.tsv', 'w', encoding='utf-8')
writer_associated = csv.writer(csvfile_associated, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_associated.writerow(
    ['ChemicalID', 'DiseaseID', 'omimIDs', 'directEvidences', 'pubMed_ids', 'inferenceScores', 'inferenceGeneSymbols'])

'''
put the information in the right tsv file
'''


def add_information_into_te_different_tsv_files(chemical_id, disease_id, information, csvfile):
    omimIDs = '|'.join(list(filter(bool, information[0])))
    directEvidences = '|'.join(list(filter(bool, information[1])))
    pubMed_ids = '|'.join(list(filter(bool, information[2])))
    inferenceScores = '|'.join(list(filter(bool, information[3])))
    inferenceGeneSymbols = '|'.join(list(filter(bool, information[4])))
    csvfile.writerow(
        [chemical_id, disease_id, omimIDs, directEvidences, pubMed_ids, inferenceScores, inferenceGeneSymbols])


# csvfile_inf= open('chemical_disease/inf.tsv', 'w')
# writer_inf = csv.writer(csvfile_inf, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# writer_inf.writerow(['ChemicalID', 'DiseaseID', 'inferenceScores'])


# generate cypher file
cypherfile = open('output/cypher_edge.cypher', 'a', encoding='utf-8')

'''
get all relationships between gene and pathway, take the pharmebinet identifier an save all important information in a tsv
also generate a cypher file to integrate this information 
'''


def generate_cypher():
    list_file_name_rela_name = [('induces', 'INDUCES_CHiD'),
                                ('treat', 'TREATS_CHtD')]  # ,('associated', 'ASSOCIATES_CHaD')

    for (file_name, rela_name) in list_file_name_rela_name:
        query = ''' Match  (n:Chemical{identifier:line.ChemicalID}), (b:Disease{identifier:line.DiseaseID}) Merge (n)-[r:%s]->(b) On Match Set r.resource=r.resource+'CTD', r.ctd='yes', r.directEvidences=split(line.directEvidences,'|'),  r.inferenceGeneSymbol=split(line.inferenceGeneSymbols,'|'), r.inferenceScore=split(line.inferenceScores,'|'), r.pubMed_ids=split(line.pubMed_ids,'|'), r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID On Create Set r.directEvidences=split(line.directEvidences,'|'), r.ctd='yes', r.pubMed_ids=split(line.pubMed_ids,'|'), r.resource=["CTD"], r.inferenceGeneSymbol=split(line.inferenceGeneSymbols,'|'), r.inferenceScore=split(line.inferenceScores,'|') , r.url='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2024 NC State University. All rights reserved.", r.unbiased=true  '''
        query = query % (rela_name)

        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/ctd/chemical_disease/{file_name}.tsv',
                                                  query)
        cypherfile.write(query)


'''

'''


def get_all_important_relationships_and_write_into_files():
    # to make time statistics
    list_time_all_finding_chemical = []
    list_time_dict_chemical = []
    list_time_find_association = []
    list_time_dict_association = []
    list_time_add_to_file = []

    # counter directEvidence
    counter_direct_evidence = 0
    # counter association
    counter_association = 0
    # counter marker/mechanism
    counter_marker = 0

    # sys.exit()
    number_of_compound_to_work_with = 10

    # different counter
    counter = 0
    counter_of_used_rela = 0
    counter_integrated_in_file_rela = 0
    counter_multi_direct_evidence = 0

    start = time.time()
    # compound drugbank id
    query = '''MATCH p=(a:Compound)-[r:equal_chemical_CTD]->(b:CTD_chemical)   RETURN a.identifier , b.chemical_id '''
    # print(query)
    # sys.exit()
    results = g.run(query)
    time_measurement = time.time() - start
    print('\tget all mapped compound: %.4f seconds' % (time_measurement))
    list_time_all_finding_chemical.append(time_measurement)

    # dictionary ctd chemical to drugbank id
    dict_chemical_to_drugbank = {}

    start = time.time()
    # counter chemicals with drugbank ids
    count_chemicals_drugbank = 0

    # go through the results
    for record in results:
        [chemical_id, ctd_chemical_id] = record.values()

        count_chemicals_drugbank += 1
        # fill the chemical id to drugbank id dictionary
        if ctd_chemical_id in dict_chemical_to_drugbank:
            dict_chemical_to_drugbank[ctd_chemical_id].append(chemical_id)
        else:
            dict_chemical_to_drugbank[ctd_chemical_id] = [chemical_id]

    # print(dict_chemical_id_chemical)
    time_measurement = time.time() - start
    # print('\t Generate dictionary: %.4f seconds' % (time_measurement))
    list_time_dict_chemical.append(time_measurement)
    start = time.time()

    '''
            sort all information into dict_chemical_disease
            '''

    def sort_into_dictionary(chemical_id, mondo, omimIDs, directEvidence, pubMed_ids, inferenceScore,
                             inferenceGeneSymbol, disease_id):
        tuple_ids = (chemical_id, mondo)
        if tuple_ids in dict_chemical_disease:
            dict_chemical_disease[tuple_ids][0].extend(omimIDs)
            dict_chemical_disease[tuple_ids][0] = list(
                set(dict_chemical_disease[tuple_ids][0]))
            dict_chemical_disease[tuple_ids][1].append(directEvidence)
            dict_chemical_disease[tuple_ids][1] = list(
                set(dict_chemical_disease[(chemical_id, mondo)][1]))
            dict_chemical_disease[tuple_ids][2].extend(pubMed_ids)
            dict_chemical_disease[tuple_ids][2] = list(
                set(dict_chemical_disease[(chemical_id, mondo)][2]))
            dict_chemical_disease[tuple_ids][3].append(inferenceScore)
            dict_chemical_disease[tuple_ids][3] = list(
                set(dict_chemical_disease[tuple_ids][3]))
            dict_chemical_disease[tuple_ids][4].append(inferenceGeneSymbol)
            dict_chemical_disease[tuple_ids][4] = list(
                set(dict_chemical_disease[tuple_ids][4]))
            dict_chemical_disease[tuple_ids][5].append(disease_id)
            dict_chemical_disease[tuple_ids][5] = list(
                set(dict_chemical_disease[tuple_ids][5]))
        else:
            dict_chemical_disease[tuple_ids] = [omimIDs, [directEvidence], pubMed_ids,
                                                [inferenceScore], [inferenceGeneSymbol], [disease_id],
                                                []]

    query = '''MATCH (chemical:CTD_chemical)-[r:associates_CD]->(disease:CTD_disease) Where (disease)--(:Disease) and r.directEvidence is not NULL and r.pubMed_ids is not NULL RETURN chemical.chemical_id,   r, disease.mondos, disease.disease_id '''
    results = g.run(query)

    time_measurement = time.time() - start
    print('\t Find all association: %.4f seconds' % (time_measurement))
    list_time_find_association.append(time_measurement)

    start = time.time()

    # dictionary with all pairs and properties as value
    dict_chemical_disease = {}

    for record in results:
        [chemical_id, rela, mondos, disease_id] = record.values()
        counter += 1
        # if disease_id=='605552':
        #     print('blub')
        rela = dict(rela)
        omimIDs = rela['omimIDs'] if 'omimIDs' in rela else []
        directEvidence = rela['directEvidence']
        pubMed_ids = rela['pubMed_ids'] if 'pubMed_ids' in rela else []
        inferenceScore = rela['inferenceScore'] if 'inferenceScore' in rela else ''

        counter_of_used_rela += 1

        inferenceGeneSymbol = rela['inferenceGeneSymbol'] if 'inferenceGeneSymbol' in rela else ''
        if chemical_id not in dict_chemical_to_drugbank and len(mondos) > 0:
            for mondo in mondos:
                sort_into_dictionary(chemical_id, mondo, omimIDs, directEvidence, pubMed_ids, inferenceScore,
                                     inferenceGeneSymbol, disease_id)
        elif chemical_id in dict_chemical_to_drugbank and len(mondos) > 0:
            for drugbank_id in dict_chemical_to_drugbank[chemical_id]:
                for mondo in mondos:
                    sort_into_dictionary(drugbank_id, mondo, omimIDs, directEvidence, pubMed_ids, inferenceScore,
                                         inferenceGeneSymbol, disease_id)

        # print('number of relationships:' + str(counter))
        # print('number of used rela:' + str(counter_of_used_rela))
        # print('number of relas over 100:' + str(counter_over_100))
        time_measurement = time.time() - start
        # print('\t Generate dictionary disease chemical: %.4f seconds' % (time_measurement))
        list_time_dict_association.append(time_measurement)
        start = time.time()

        if counter % 10000 == 0:
            print('had now 10000 again:', counter)
            print(datetime.datetime.now())

        # print(len(dict_chemical_disease))

    for (chemical_id, disease_id), information in dict_chemical_disease.items():
        directEvidences = list(filter(bool, information[1]))
        counter_integrated_in_file_rela += 1
        # if (chemical_id,disease_id)==('DB00649','MONDO:0011565'):
        #     print('blub')
        if len(directEvidences) > 0 and directEvidences[0] != '':
            counter_direct_evidence += 1

            for directEvidence in directEvidences:
                counter_multi_direct_evidence += 1
                if directEvidence == 'marker/mechanism':
                    counter_marker += 1
                    add_information_into_te_different_tsv_files(chemical_id, disease_id, information,
                                                                writer_induces)
                else:
                    add_information_into_te_different_tsv_files(chemical_id, disease_id, information,
                                                                writer_treat)
        else:
            counter_association += 1
            add_information_into_te_different_tsv_files(chemical_id, disease_id, information, writer_associated)

    time_measurement = time.time() - start
    # print('\t Add information to file: %.4f seconds' % (time_measurement))
    list_time_add_to_file.append(time_measurement)

    print('integrated relas:' + str(counter_integrated_in_file_rela))
    print('Number of directEvidence:' + str(counter_direct_evidence))
    print('Number of marker/mechanism:' + str(counter_marker))
    print('Number of  therapeutic:' + str(counter_multi_direct_evidence - counter_marker))
    print('Number of association:' + str(counter_association))

    print('Average finding disease:' + str(np.mean(list_time_all_finding_chemical)))
    print('Average dict monde:' + str(np.mean(list_time_dict_chemical)))
    print('Average finding association:' + str(np.mean(list_time_find_association)))
    print('Min finding association:' + str(min(list_time_find_association)))
    print('Max finding association:' + str(max(list_time_find_association)))
    print('Average dict association:' + str(np.mean(list_time_dict_association)))
    print('Average add to file:' + str(np.mean(list_time_add_to_file)))


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('generate  cypher file')

    generate_cypher()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Take all chemical-disease relationships and generate tsv')

    get_all_important_relationships_and_write_into_files()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
