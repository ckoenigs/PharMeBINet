# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph#, authenticate
import datetime
import csv, time, sys
import  numpy as np


'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))



# csv files for integrate the different realtionships into hetionet
csvfile_induces = open('chemical_disease/induces.csv', 'w', encoding='utf-8')
writer_induces = csv.writer(csvfile_induces, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_induces.writerow(['ChemicalID', 'DiseaseID','omimIDs','directEvidences','pubMedIDs', 'inferenceScores','inferenceGeneSymbols'])

csvfile_treat = open('chemical_disease/treat.csv', 'w', encoding='utf-8')
writer_treat = csv.writer(csvfile_treat, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_treat.writerow(['ChemicalID', 'DiseaseID','omimIDs','directEvidences','pubMedIDs', 'inferenceScores','inferenceGeneSymbols'])

csvfile_associated = open('chemical_disease/associated.csv', 'w', encoding='utf-8')
writer_associated = csv.writer(csvfile_associated, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_associated.writerow(['ChemicalID', 'DiseaseID','omimIDs','directEvidences','pubMedIDs', 'inferenceScores','inferenceGeneSymbols'])

'''
put the information in the right csv file
'''
def add_information_into_te_different_csv_files( chemical_id,disease_id, information, csvfile):
    omimIDs = '|'.join(list(filter(bool, information[0])))
    directEvidences = '|'.join(list(filter(bool, information[1])))
    pubMedIDs = '|'.join(list(filter(bool, information[2])))
    inferenceScores = '|'.join(list(filter(bool, information[3])))
    inferenceGeneSymbols ='|'.join(list(filter(bool, information[4])))
    csvfile.writerow([chemical_id, disease_id,omimIDs,directEvidences,pubMedIDs, inferenceScores,inferenceGeneSymbols])

# csvfile_inf= open('chemical_disease/inf.csv', 'w')
# writer_inf = csv.writer(csvfile_inf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# writer_inf.writerow(['ChemicalID', 'DiseaseID', 'inferenceScores'])


# generate cypher file
cypherfile = open('chemical_disease/cypher.cypher', 'w', encoding='utf-8')

'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def generate_cypher():
    list_file_name_rela_name=[('induces','INDUCES_CiD'),('treat','TREATS_CtD'),('associated','ASSOCIATES_CaD')]

    # the general cypher file to update all chemicals and relationship which are not from aeolus
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')

    for (file_name,rela_name) in list_file_name_rela_name:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_disease/%s.csv" As line Match  (n:Chemical{identifier:line.ChemicalID}), (b:Disease{identifier:line.DiseaseID}) Merge (n)-[r:%s]->(b) On Match Set r.resource=r.resource+'CTD', r.ctd='yes', r.directEvidence=split(line.directEvidences,'|'),  r.inferenceGeneSymbol=split(line.inferenceGeneSymbols,'|'), r.inferenceScore=split(line.inferenceScores,'|'), r.pubMedIDs=split(line.pubMedIDs,'|'), r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID On Create Set r.new='yes', r.directEvidence=split(line.directEvidences,'|'), r.ctd='yes', r.pubMedIDs=split(line.pubMedIDs,'|'), r.resource=["CTD"], r.inferenceGeneSymbol=split(line.inferenceGeneSymbols,'|'), r.inferenceScore=split(line.inferenceScores,'|') , r.url_ctd='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID, r.url='http://ctdbase.org/detail.go?type=chem&acc='+line.ChemicalID , r.source="CTD", r.licence="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased=true ;\n '''
        query= query %(file_name,rela_name)
        cypherfile.write(query)

        cypher_general.write(':begin\n')
        cypher_general.write('Match (n:Chemical)-[r:'+ rela_name+']->(b:Disease) Where not exists(r.ctd) Set r.ctd="no";\n')
        cypher_general.write(':commit\n')
    cypher_general.close()

'''

'''
def get_all_important_relationships_and_write_into_files():
    # to make time statistics
    list_time_all_finding_chemical=[]
    list_time_dict_chemical=[]
    list_time_find_association=[]
    list_time_dict_association=[]
    list_time_add_to_file=[]

    # check how many ctd chemicals are mapped
    query = '''Match (n:Chemical) Where (n)-[:equal_chemical_CTD]-() or (n)-[:equal_to_CTD_chemical]-() Return count(n)'''
    results = g.run(query)
    number_of_chemical = int(results.evaluate())
    
    # query='''MATCH p=(a)-[r:equal_chemichal_CTD]->(b) Create (a)-[:equal_chemical_CTD]->(b) Delete r'''
    # g.run(query)

    
    # number_of_chemical=500

    # counter directEvidence
    counter_direct_evidence = 0
    # counter association
    counter_association = 0
    #counter marker/mechanism
    counter_marker = 0

    list_durgbank_mesh=[]
    list_mesh=[]


    print(int(number_of_chemical))
    # sys.exit()
    number_of_compound_to_work_with = 10

    # different counter
    counter = 0
    counter_of_used_rela=0
    counter_of_used_chemical=0
    counter_no_change=0
    counter_over_100=0
    counter_integrated_in_file_rela=0
    counter_multi_direct_evidence=0

    i=0

    # take only a prat of the ctd chemicals, because they have a lot of information
    while counter_of_used_chemical <number_of_chemical:
        # list of all chemicals
        all_chemicals_id = []
        # dictionary with hetionet chemical id as key and value list of ctd chemical ids
        dict_chemical_id_chemical = {}

        start = time.time()
        # compound drugbank id
        query = '''MATCH p=(a:Compound)-[r:equal_chemical_CTD]->(b:CTDchemical)  Where not exists(a.integrated_drugbank)  With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            number_of_compound_to_work_with) + ''' Set a.integrated_drugbank='yes'  RETURN a.identifier , ctd '''
        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))
        list_time_all_finding_chemical.append(time_measurement)

        # dictionary ctd chemical to drugbank id
        dict_chemical_to_drugbank={}


        start = time.time()
        # counter chemicals with drugbank ids
        count_chemicals_drugbank=0

        #go through the results
        for chemical_id, ctd_chemicals, in results:

            count_chemicals_drugbank+=1
            all_chemicals_id.extend(ctd_chemicals)
            for chemical in ctd_chemicals:
                # fill the chemical id to drugbank id dictionary
                if chemical in dict_chemical_to_drugbank:
                    dict_chemical_to_drugbank[chemical].append(chemical_id)
                else:
                    dict_chemical_to_drugbank[chemical]=[chemical_id]
                if not chemical in list_durgbank_mesh:
                    list_durgbank_mesh.append(chemical)

                # fill dictionary hetionet id to ctd chemical id
                if chemical in dict_chemical_id_chemical:
                    dict_chemical_id_chemical[chemical].append(chemical_id)
                else:
                    dict_chemical_id_chemical[chemical] = [chemical_id]
        # counter_of_used_chemical+=count_chemicals_drugbank

        # get all chemical ids in hetionet and the ctd chemicals
        query = '''MATCH p=(a:Chemical)-[r:equal_to_CTD_chemical]->(b:CTDchemical)  Where not exists(a.integrated) With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            number_of_compound_to_work_with) + ''' Set a.integrated='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        # print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))
        list_time_all_finding_chemical.append(time_measurement)

        start = time.time()
        # counter number of chmicals without drugbank id
        counter_chemicals_without_db=0
        for chemical_id, ctd_chemicals, in results:
            counter_chemicals_without_db+=1
            all_chemicals_id.extend(ctd_chemicals)
            for chemical in ctd_chemicals:
                if not chemical in list_mesh:
                    list_mesh.append(chemical)
                # fill dictionary hetionet id to ctd id
                if chemical in dict_chemical_id_chemical:
                    dict_chemical_id_chemical[chemical].append(chemical_id)
                else:
                    dict_chemical_id_chemical[chemical] = [chemical_id]

        if counter_of_used_chemical ==counter_of_used_chemical+count_chemicals_drugbank+counter_chemicals_without_db:
            counter_no_change+=1
            if counter_no_change==10:
                print('error by take all chemical')
                sys.exit('exit ctd chemical no changes in counter of used chemical')

        counter_of_used_chemical += counter_chemicals_without_db+count_chemicals_drugbank
        print(str(counter_of_used_chemical)+'/'+str(number_of_chemical))


        # print(dict_chemical_id_chemical)
        time_measurement = time.time() - start
        # print('\t Generate dictionary: %.4f seconds' % (time_measurement))
        list_time_dict_chemical.append(time_measurement)
        start = time.time()

        # print(dict_chemical_id_chemical)
        # check if not longer then 5 iteration no new  information are got it exist
        if len(all_chemicals_id)==0:
            i+=1
            if i==5:
                sys.exit('exit ctd chemical i')
        else:
            i=0

        '''
                sort all information into dict_chemical_disease
                '''

        def sort_into_dictionary(chemical_id, mondo, omimIDs, directEvidence, pubMedIDs, inferenceScore,
                                 inferenceGeneSymbol, disease_id):
            if (chemical_id, mondo) in dict_chemical_disease:
                dict_chemical_disease[(chemical_id, mondo)][0].extend(omimIDs)
                dict_chemical_disease[(chemical_id, mondo)][0] = list(
                    set(dict_chemical_disease[(chemical_id, mondo)][0]))
                dict_chemical_disease[(chemical_id, mondo)][1].append(directEvidence)
                dict_chemical_disease[(chemical_id, mondo)][1] = list(
                    set(dict_chemical_disease[(chemical_id, mondo)][1]))
                dict_chemical_disease[(chemical_id, mondo)][2].extend(pubMedIDs)
                dict_chemical_disease[(chemical_id, mondo)][2] = list(
                    set(dict_chemical_disease[(chemical_id, mondo)][2]))
                dict_chemical_disease[(chemical_id, mondo)][3].append(inferenceScore)
                dict_chemical_disease[(chemical_id, mondo)][3] = list(
                    set(dict_chemical_disease[(chemical_id, mondo)][3]))
                dict_chemical_disease[(chemical_id, mondo)][4].append(inferenceGeneSymbol)
                dict_chemical_disease[(chemical_id, mondo)][4] = list(
                    set(dict_chemical_disease[(chemical_id, mondo)][4]))
                dict_chemical_disease[(chemical_id, mondo)][5].append(disease_id)
                dict_chemical_disease[(chemical_id, mondo)][5] = list(
                    set(dict_chemical_disease[(chemical_id, mondo)][5]))
            else:
                dict_chemical_disease[(chemical_id, mondo)] = [omimIDs, [directEvidence], pubMedIDs,
                                                               [inferenceScore], [inferenceGeneSymbol], [disease_id],
                                                               []]

        all_chemicals_id = '","'.join(all_chemicals_id)
        query = '''MATCH (chemical:CTDchemical)-[r:associates_CD]->(disease:CTDdisease)--(:Disease) Where  chemical.chemical_id in ["''' + all_chemicals_id + '''"] and exists(r.directEvidence) RETURN DISTINCT chemical.chemical_id, chemical.drugBankIDs,  r, disease.mondos, disease.disease_id '''
        results = g.run(query)

        time_measurement = time.time() - start
        # print('\t Find all association: %.4f seconds' % (time_measurement))
        list_time_find_association.append(time_measurement)

        start = time.time()

        # dictionary with all pairs and properties as value
        dict_chemical_disease = {}

        for chemical_id, drugbank_ids, rela, mondos, disease_id, in results:
            counter += 1
            # if disease_id=='605552':
            #     print('blub')
            rela = dict(rela)
            omimIDs = rela['omimIDs'] if 'omimIDs' in rela else []
            directEvidence = rela['directEvidence'] if 'directEvidence' in rela else ''
            pubMedIDs = rela['pubMedIDs'] if 'pubMedIDs' in rela else []
            inferenceScore = rela['inferenceScore'] if 'inferenceScore' in rela else ''

            # take only the relationships with directEvidence and inference score over 100
            # if inferenceScore!='' and float(inferenceScore)<100 :
            #     if directEvidence!='':
            #         print('ohje direct evidence')
            #     continue
            # elif inferenceScore!='' and float(inferenceScore)>=100 :
            #     counter_over_100+=1

            if inferenceScore=='' and directEvidence=='':
                sys.exit('some rela in ctd chemical-disease has neither inference nor direct evidence ')
            elif directEvidence =='':
                continue

            counter_of_used_rela+=1

            inferenceGeneSymbol = rela['inferenceGeneSymbol'] if 'inferenceGeneSymbol' in rela else ''
            drugbank_ids= drugbank_ids if not drugbank_ids is None else []
            if chemical_id not in dict_chemical_to_drugbank and len(mondos) > 0:
                for mondo in mondos:
                    sort_into_dictionary(chemical_id, mondo, omimIDs, directEvidence, pubMedIDs, inferenceScore,
                                         inferenceGeneSymbol, disease_id)
            elif chemical_id in dict_chemical_to_drugbank and len(mondos) > 0:
                for drugbank_id in dict_chemical_to_drugbank[chemical_id]:
                    for mondo in mondos:
                        sort_into_dictionary(drugbank_id, mondo, omimIDs, directEvidence, pubMedIDs, inferenceScore,
                                             inferenceGeneSymbol, disease_id)

            if counter % 10000 == 0:
                print(counter)

                time_measurement = time.time() - start
                print('\tTake 1000 pairs: %.4f seconds' % (time_measurement))
                start = time.time()


        print('number of relationships:'+str(counter))
        print('number of used rela:'+str(counter_of_used_rela))
        print('number of relas over 100:'+str(counter_over_100))
        time_measurement = time.time() - start
        # print('\t Generate dictionary disease chemical: %.4f seconds' % (time_measurement))
        list_time_dict_association.append(time_measurement)
        start = time.time()

        print(len(dict_chemical_disease))

        for (chemical_id, disease_id), information in dict_chemical_disease.items():
            directEvidences = list(filter(bool, information[1]))
            counter_integrated_in_file_rela+=1
            # if (chemical_id,disease_id)==('DB00649','MONDO:0011565'):
            #     print('blub')
            if len(directEvidences) > 0 and directEvidences[0]!='':
                counter_direct_evidence += 1

                for directEvidence in directEvidences:
                    counter_multi_direct_evidence+=1
                    if directEvidence=='marker/mechanism':
                        counter_marker+=1
                        add_information_into_te_different_csv_files(chemical_id,disease_id,information,writer_induces)
                    else:
                        add_information_into_te_different_csv_files(chemical_id, disease_id, information,
                                                                    writer_treat)
            else:
                counter_association+=1
                add_information_into_te_different_csv_files(chemical_id, disease_id, information, writer_associated)



        time_measurement = time.time() - start
        # print('\t Add information to file: %.4f seconds' % (time_measurement))
        list_time_add_to_file.append(time_measurement)

    print('integrated relas:'+str(counter_integrated_in_file_rela))
    print('Number of directEvidence:'+str(counter_direct_evidence))
    print('Number of marker/mechanism:'+str(counter_marker))
    print('Number of  therapeutic:'+str(counter_multi_direct_evidence-counter_marker))
    print('Number of association:'+str(counter_association))

    print('number of chemicals:'+str(len(list_mesh)))
    print('number of chemicals with db:'+str(len(list_durgbank_mesh)))

    query = '''MATCH (n:Chemical) REMOVE n.integrated, n.integrated_drugbank;\n'''
    cypherfile.write(query)

    cypherfile.close()

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

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('generate  cypher file')

    generate_cypher()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Take all chemical-disease relationships and generate csv')

    get_all_important_relationships_and_write_into_files()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
