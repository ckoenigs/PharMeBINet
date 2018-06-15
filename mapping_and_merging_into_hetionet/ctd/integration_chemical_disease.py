# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv, time, sys
import  numpy as np


'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# csv files for integrate the different realtionships into hetionet
csvfile_induces = open('chemical_disease/induces.csv', 'wb')
writer_induces = csv.writer(csvfile_induces, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_induces.writerow(['ChemicalID', 'DiseaseID','omimIDs','directEvidences','pubMedIDs', 'inferenceScores','inferenceGeneSymbols'])

csvfile_treat = open('chemical_disease/treat.csv', 'wb')
writer_treat = csv.writer(csvfile_treat, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_treat.writerow(['ChemicalID', 'DiseaseID','omimIDs','directEvidences','pubMedIDs', 'inferenceScores','inferenceGeneSymbols'])

csvfile_associated = open('chemical_disease/associated.csv', 'wb')
writer_associated = csv.writer(csvfile_associated, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_associated.writerow(['ChemicalID', 'DiseaseID','omimIDs','directEvidences','pubMedIDs', 'inferenceScores','inferenceGeneSymbols'])

'''
put the information in the right csv file
'''
def add_information_into_te_different_csv_files( (chemical_id,disease_id), information, csvfile):
    omimIDs = '|'.join(filter(bool, information[0]))
    directEvidences = '|'.join(filter(bool, information[1]))
    pubMedIDs = '|'.join(filter(bool, information[2]))
    inferenceScores = '|'.join(filter(bool, information[3]))
    inferenceGeneSymbols ='|'.join(filter(bool, information[4]))
    csvfile.writerow([chemical_id, disease_id,omimIDs,directEvidences,pubMedIDs, inferenceScores,inferenceGeneSymbols])


'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_pathway():
    # generate cypher file
    cypherfile = open('chemical_disease/cypher.cypher', 'w')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (n:Chemical)-[r:TREATS_CtD]->(b:Disease) Where not exists(r.hetionet) Set r.hetionet="yes";\n')
    cypherfile.write('commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/induces.csv" As line Match (n:Chemical{identifier:line.ChemicalID})-[r:INDUCES_CiD]->(b:Disease{identifier:line.DiseaseID}) Where r.ctd='no' Set r.how_often=r.how_often+1 , r.resource=r.resource+'CTD';\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/induces.csv" As line Match (n:Chemical{identifier:line.ChemicalID}), (b:Disease{identifier:line.DiseaseID}) Merge (n)-[r:INDUCES_CiD]->(b) On Create Set r.ndf_rt='no', r.directEvidence=split('|',line.directEvidences), r.ctd='yes', r.pubMedIDs=split('|',line.pubMedIDs), r.resource=["CTD"], r.how_often=1, r.inferenceGeneSymbol=split('|',line.inferenceGeneSymbols), r.inferenceScore=split('|',line.inferenceScores) , r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, r.url='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID , r.source="CTD", r.licence="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='true' On Match SET r.ctd='yes', r.directEvidence=split('|',line.directEvidences),  r.inferenceGeneSymbol=split('|',line.inferenceGeneSymbols), r.inferenceScore=split('|',line.inferenceScores), r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID ;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/treat.csv" As line Match (n:Chemical{identifier:line.ChemicalID})-[r:TREATS_CtD]->(b:Disease{identifier:line.DiseaseID}) Where r.ctd='no' Set r.how_often=r.how_often+1 , r.resource=r.resource+'CTD';\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/treat.csv" As line Match (n:Chemical{identifier:line.ChemicalID}), (b:Disease{identifier:line.DiseaseID}) Merge (n)-[r:TREATS_CtD]->(b) On Create Set r.htionet='no', r.directEvidence=split('|',line.directEvidences), r.ctd='yes', r.pubMedIDs=split('|',line.pubMedIDs), r.resource=["CTD"], r.how_often=1, r.inferenceGeneSymbol=split('|',line.inferenceGeneSymbols), r.inferenceScore=split('|',line.inferenceScores) , r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, r.url='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID , r.source="CTD", r.licence="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='true' On Match SET r.ctd='yes', r.directEvidence=split('|',line.directEvidences),  r.inferenceGeneSymbol=split('|',line.inferenceGeneSymbols), r.inferenceScore=split('|',line.inferenceScores), r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID ;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/associated.csv" As line Match (n:Chemical{identifier:line.ChemicalID})-[r:Associates_CaD]->(b:Disease{identifier:line.DiseaseID}) Where r.ctd='no' Set r.how_often=r.how_often+1 , r.resource=r.resource+'CTD';\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/associated.csv" As line Match (n:Chemical{identifier:line.ChemicalID}), (b:Disease{identifier:line.DiseaseID}) Merge (n)-[r:Associates_CaD]->(b) On Create Set r.directEvidence=split('|',line.directEvidences), r.ctd='yes', r.pubMedIDs=split('|',line.pubMedIDs), r.resource=["CTD"], r.how_often=1, r.inferenceGeneSymbol=split('|',line.inferenceGeneSymbols), r.inferenceScore=split('|',line.inferenceScores) , r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, r.url='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID , r.source="CTD", r.licence="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='true' On Match SET r.ctd='yes', r.directEvidence=split('|',line.directEvidences),  r.inferenceGeneSymbol=split('|',line.inferenceGeneSymbols), r.inferenceScore=split('|',line.inferenceScores), r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID ;\n '''
    cypherfile.write(query)
    cypherfile.write('begin\n')
    cypherfile.write('Match (n:Chemical)-[r:TREATS_CtD]->(b:Disease) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypherfile.write('commit')
    cypherfile.write('begin\n')
    cypherfile.write('Match (n:Chemical)-[r:INDUCES_CiD]->(b:Disease) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypherfile.write('commit')

    # to make time statistics
    list_time_all_finding_chemical=[]
    list_time_dict_chemical=[]
    list_time_find_association=[]
    list_time_dict_association=[]
    list_time_add_to_file=[]

    query = '''Match (n:Chemical) Return count(n)'''
    results = g.run(query)
    number_of_disease = int(results.evaluate())
    
    query='''MATCH p=(a)-[r:equal_chemichal_CTD]->(b) Create (a)-[:equal_chemical_CTD]->(b) Delete r'''
    g.run(query)

    
    # number_of_disease=100

    # counter directEvidence
    counter_directEvidence = 0

    # counter inferences
    counter_inferences = 0

    print(int(number_of_disease))
    # sys.exit()
    number_of_compound_to_work_with = 10

    count_multiple_pathways = 0
    count_possible_relas = 0
    counter = 0
    counter_of_used_chemical=0

    while counter_of_used_chemical < number_of_disease:

        start = time.time()
        query = '''MATCH p=(a)-[r:equal_chemical_CTD]->(b)  Where not exists(a.integrated_drugbank)   With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            number_of_compound_to_work_with) + ''' Set a.integrated_drugbank='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))
        list_time_all_finding_chemical.append(time_measurement)
        all_chemicals_id = []
        dict_chemical_id_chemical = {}
        start = time.time()
        for chemical_id, ctd_chemicals, in results:
            all_chemicals_id.extend(ctd_chemicals)
            for chemical in ctd_chemicals:
                if chemical in dict_chemical_id_chemical:
                    dict_chemical_id_chemical[chemical].append(chemical_id)
                else:
                    dict_chemical_id_chemical[chemical] = [chemical_id]

        query = '''MATCH p=(a)-[r:equal_to_CTD_chemical]->(b)  Where not exists(a.integrated)   With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            number_of_compound_to_work_with) + ''' Set a.integrated='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))
        list_time_all_finding_chemical.append(time_measurement)

        start = time.time()
        for chemical_id, ctd_chemicals, in results:
            all_chemicals_id.extend(ctd_chemicals)
            for chemical in ctd_chemicals:
                if chemical in dict_chemical_id_chemical:
                    dict_chemical_id_chemical[chemical].append(chemical_id)
                else:
                    dict_chemical_id_chemical[chemical] = [chemical_id]

        print(dict_chemical_id_chemical)
        time_measurement = time.time() - start
        print('\t Generate dictionary: %.4f seconds' % (time_measurement))
        list_time_dict_chemical.append(time_measurement)
        start = time.time()

        print(dict_chemical_id_chemical)

        all_chemicals_id = '","'.join(all_chemicals_id)
        query = '''MATCH (chemical:CTDchemical)-[r:associates_CD]->(disease:CTDdisease) Where not disease.mondos=[] and chemical.chemical_id in ["''' + all_chemicals_id + '''"] RETURN chemical.chemical_id, chemical.drugBankIDs, r, disease.mondos, disease.disease_id '''
        results = g.run(query)

        time_measurement = time.time() - start
        print('\t Find all association: %.4f seconds' % (time_measurement))
        list_time_find_association.append(time_measurement)

        start = time.time()

        # dictionary with all pairs and properties as value
        dict_chemical_disaese = {}

        for chemical_id, drugbank_ids, rela, mondos, disease_id, in results:
            counter += 1
            rela = dict(rela)
            omimIDs = rela['omimIDs'] if 'omimIDs' in rela else []
            directEvidence = rela['directEvidence'] if 'directEvidence' in rela else ''
            pubMedIDs = rela['pubMedIDs'] if 'pubMedIDs' in rela else []
            inferenceScore = rela['inferenceScore'] if 'inferenceScore' in rela else ''
            inferenceGeneSymbol = rela['inferenceGeneSymbol'] if 'inferenceGeneSymbol' in rela else ''
            drugbank_ids= drugbank_ids if not drugbank_ids is None else []
            if len(drugbank_ids) == 0 and len(mondos) > 0:
                for mondo in mondos:
                    if (chemical_id, mondo) in dict_chemical_disaese:
                        dict_chemical_disaese[(chemical_id, mondo)][0].extend(omimIDs)
                        dict_chemical_disaese[(chemical_id, mondo)][0] = list(
                            set(dict_chemical_disaese[(chemical_id, mondo)][0]))
                        dict_chemical_disaese[(chemical_id, mondo)][1].append(directEvidence)
                        dict_chemical_disaese[(chemical_id, mondo)][1] = list(
                            set(dict_chemical_disaese[(chemical_id, mondo)][1]))
                        dict_chemical_disaese[(chemical_id, mondo)][2].extend(pubMedIDs)
                        dict_chemical_disaese[(chemical_id, mondo)][2] = list(
                            set(dict_chemical_disaese[(chemical_id, mondo)][2]))
                        dict_chemical_disaese[(chemical_id, mondo)][3].append(inferenceScore)
                        dict_chemical_disaese[(chemical_id, mondo)][3] = list(
                            set(dict_chemical_disaese[(chemical_id, mondo)][3]))
                        dict_chemical_disaese[(chemical_id, mondo)][4].append(inferenceGeneSymbol)
                        dict_chemical_disaese[(chemical_id, mondo)][4] = list(
                            set(dict_chemical_disaese[(chemical_id, mondo)][4]))
                        dict_chemical_disaese[(chemical_id, mondo)][5].append(disease_id)
                        dict_chemical_disaese[(chemical_id, mondo)][5]=list(set(dict_chemical_disaese[(chemical_id, mondo)][5]))
                    else:
                        dict_chemical_disaese[(chemical_id, mondo)] = [omimIDs,[directEvidence], pubMedIDs,
                                                                       [inferenceScore], [inferenceGeneSymbol], [disease_id],[]]
            elif len(drugbank_ids) > 0 and len(mondos) > 0:
                for drugbank_id in drugbank_ids:
                    for mondo in mondos:
                        if (drugbank_id, mondo) in dict_chemical_disaese:
                            dict_chemical_disaese[(drugbank_id, mondo)][0].extend(omimIDs)
                            dict_chemical_disaese[(drugbank_id, mondo)][0] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][0]))
                            dict_chemical_disaese[(drugbank_id, mondo)][1].append(directEvidence)
                            dict_chemical_disaese[(drugbank_id, mondo)][1] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][1]))
                            dict_chemical_disaese[(drugbank_id, mondo)][2].extend(pubMedIDs)
                            dict_chemical_disaese[(drugbank_id, mondo)][2] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][2]))
                            dict_chemical_disaese[(drugbank_id, mondo)][3].append(inferenceScore)
                            dict_chemical_disaese[(drugbank_id, mondo)][3] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][3]))
                            dict_chemical_disaese[(drugbank_id, mondo)][4].append(inferenceGeneSymbol)
                            dict_chemical_disaese[(drugbank_id, mondo)][4] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][4]))
                            dict_chemical_disaese[(drugbank_id, mondo)][5].append(disease_id)
                            dict_chemical_disaese[(drugbank_id, mondo)][5] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][5]))
                            dict_chemical_disaese[(drugbank_id, mondo)][6].append(chemical_id)
                            dict_chemical_disaese[(drugbank_id, mondo)][6] = list(
                                set(dict_chemical_disaese[(drugbank_id, mondo)][6]))
                        else:
                            dict_chemical_disaese[(drugbank_id, mondo)] = [omimIDs, [directEvidence], pubMedIDs,
                                                                           [inferenceScore], [inferenceGeneSymbol],
                                                                           [disease_id],[chemical_id]]

            if counter % 10000 == 0:
                print(counter)

                time_measurement = time.time() - start
                print('\tTake 1000 pairs: %.4f seconds' % (time_measurement))
                start = time.time()

        time_measurement = time.time() - start
        print('\t Generate dictionary disease chemical: %.4f seconds' % (time_measurement))
        list_time_dict_association.append(time_measurement)
        start = time.time()

        counter_direct_evidence=0
        for (chemical_id, disease_id), information in dict_chemical_disaese.items():
            directEvidences = filter(bool, information[1])
            if len(directEvidences) > 0:
                counter_direct_evidence+=1
                for directEvidence in directEvidences:
                    if directEvidence=='marker/mechanism':
                        add_information_into_te_different_csv_files((chemical_id,disease_id),information,writer_induces)
                    else:
                        add_information_into_te_different_csv_files((chemical_id, disease_id), information,
                                                                    writer_treat)
            else:
                add_information_into_te_different_csv_files((chemical_id, disease_id), information, writer_associated)



        time_measurement = time.time() - start
        print('\t Add information to file: %.4f seconds' % (time_measurement))
        list_time_add_to_file.append(time_measurement)

        counter_of_used_chemical += number_of_compound_to_work_with*2


    print('number of new rela:'+str(count_possible_relas))
    print('number of relationships which appears multiple time:'+str(count_multiple_pathways))

    query = '''MATCH (n:Disease) REMOVE n.integrated, n.integrated_drugbank'''
    g.run(query)

    print('Average finding disease:' + str(np.mean(list_time_all_finding_chemical)))
    print('Average dict monde:' + str(np.mean(list_time_dict_chemical)))
    print('Average finding association:' + str(np.mean(list_time_find_association)))
    print('Min finding association:' + str(min(list_time_find_association)))
    print('Max finding association:' + str(max(list_time_find_association)))
    print('Average dict association:' + str(np.mean(list_time_dict_association)))
    print('Average add to file:' + str(np.mean(list_time_add_to_file)))




def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Take all chemical-disease relationships and generate csv and cypher file')

    take_all_relationships_of_gene_pathway()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
