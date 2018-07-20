# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv, time, sys
import numpy as np

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", "neo4j", "test")
    # global g
    # g = Graph("http://localhost:7474/db/data/")
    # create connection to server
    authenticate("bimi:7475", "ckoenigs", "test")
    global g
    g = Graph("http://bimi:7475/db/data/", bolt=False)


# csv files for bp. mf, cc
bp_file = open('chemical_go/bp.csv', 'w')
bp_writer = csv.writer(bp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
bp_writer.writerow(['ChemicalID', 'GOID', 'targetTotalQty', 'backgroundTotalQty','backgroundMatchQty','correctedPValue','pValue','targetMatchQty','chemicalID'])

mf_file = open('chemical_go/mf.csv', 'w')
mf_writer = csv.writer(mf_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
mf_writer.writerow(['ChemicalID', 'GOID',  'targetTotalQty', 'backgroundTotalQty','backgroundMatchQty','correctedPValue','pValue','targetMatchQty','chemicalID'])

cc_file = open('chemical_go/cc.csv', 'w')
cc_writer = csv.writer(cc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
cc_writer.writerow(['ChemicalID', 'GOID',  'targetTotalQty', 'backgroundTotalQty','backgroundMatchQty','correctedPValue','pValue','targetMatchQty','chemicalID'])

# dictionary with for biological_process, cellular_component, molecular_function the right file
dict_processe = {
    "Biological Process": bp_writer,
    "Molecular Function": mf_writer,
    "Cellular Component": cc_writer
}

# dictionary counter for bp, cc, mf
dict_processe_counter = {
    "Biological Process": 0,
    "Molecular Function": 0,
    "Cellular Component": 0
}

'''
put the information in the right csv file
'ChemicalID', 'GOID', 'targetTotalQtys', 'backgroundTotalQtys','backgroundMatchQtys','correctedPValues','pValues','targetMatchQtys','chemicalID'
'''


def add_information_into_te_different_csv_files((chemical_id, go_id), information, csvfile):
    correctedPValues = list(information[0])
    targetTotalQtys = list(information[1])
    backgroundMatchQtys = list(information[2])
    targetMatchQtys = list(information[3])
    pValues = list(information[4])
    backgroundTotalQtys = list(information[5])
    chemicaL_mesh_id= list(information[6])


    targetTotalQtys = '|'.join(filter(bool, targetTotalQtys))
    backgroundTotalQtys = '|'.join(filter(bool, backgroundTotalQtys))
    backgroundMatchQtys = '|'.join(filter(bool, backgroundMatchQtys))
    correctedPValues = '|'.join(filter(bool, correctedPValues))
    pValues = '|'.join(filter(bool, pValues))
    targetMatchQtys = '|'.join(filter(bool, targetMatchQtys))
    chemicaL_mesh_id = '|'.join(filter(bool, chemicaL_mesh_id))
    csvfile.writerow(
        [chemical_id, go_id, targetTotalQtys, backgroundTotalQtys, backgroundMatchQtys, correctedPValues, pValues, targetMatchQtys, chemicaL_mesh_id])


'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_pathway():
    # generate cypher file
    cypherfile = open('chemical_go/cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_go/bp.csv" As line Match (n:Chemical{identifier:line.ChemicalID}), (b:BiologicalProcess{identifier:line.GOID}) Merge (n)-[r:ASSOCIATES_CaBP]->(b) On Create Set r.hetionet='no', r.targetTotalQty=split(line.targetTotalQty, '|'), r.backgroundTotalQty=split(line.backgroundTotalQty,'|'), r.backgroundMatchQty=split(line.backgroundMatchQty,'|'), r.correctedPValue=split(line.correctedPValue,'|'), r.pValue=split(line.pValue,'|'), r.targetMatchQty=split(line.targetMatchQty,'|'), r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=chem&acc="+split(line.chemicalID,'|')(0), r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.targetTotalQty=split(line.targetTotalQty, '|'), r.backgroundTotalQty=split(line.backgroundTotalQty,'|'), r.backgroundMatchQty=split(line.backgroundMatchQty,'|'), r.correctedPValue=split(line.correctedPValue,'|'), r.pValue=split(line.pValue,'|'), r.targetMatchQty=split(line.targetMatchQty,'|'), r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=chem&acc="+split(line.chemicalID,'|')(0);\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_go/mf.csv" As line Match (n:Chemical{identifier:line.ChemicalID}), (b:MolecularFunction{identifier:line.GOID}) Merge (n)-[r:ASSOCIATES_CaMF]->(b) On Create Set r.hetionet='no', r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.diseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID;\n '''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/chemical_go/cc.csv" As line Match (n:Chemical{identifier:line.ChemicalID}), (b:CellularComponent{identifier:line.GOID}) Merge (n)-[r:ASSOCIATES_CaCC]->(b) On Create Set r.hetionet='no', r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.diseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.inferenceGeneQty=line.inferenceGeneQty,r.inferenceGeneSymbols=line.inferenceGeneSymbols, r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID;\n '''
    cypherfile.write(query)


    # to make time statistics
    list_time_all_finding_chemical = []
    list_time_dict_chemical = []
    list_time_find_association = []
    list_time_dict_association = []
    list_time_add_to_file = []

    query = '''Match (n:Chemical) Where (n)-[:equal_chemical_CTD]-() or (n)-[:equal_to_CTD_chemical]-() Return count(n)'''
    results = g.run(query)
    number_of_disease = int(results.evaluate())
    # number_of_disease=200


    list_durgbank_mesh = []
    list_mesh = []

    print(int(number_of_disease))
    # sys.exit()
    number_of_compound_to_work_with = 10

    counter = 0
    counter_of_used_chemical = 0

    old_number = 100000000000000

    while counter_of_used_chemical < number_of_disease:
        old_number = counter_of_used_chemical
        all_chemicals_id = []
        dict_chemical_id_chemical = {}

        start = time.time()
        query = '''MATCH p=(a)-[r:equal_chemical_CTD]->(b)  Where not exists(a.integrated_drugbank)  With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            number_of_compound_to_work_with) + ''' Set a.integrated_drugbank='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))
        list_time_all_finding_chemical.append(time_measurement)

        start = time.time()
        # counter chemicals with drugbank ids
        count_chemicals_drugbank = 0
        for chemical_id, ctd_chemicals, in results:

            count_chemicals_drugbank += 1
            all_chemicals_id.extend(ctd_chemicals)
            for chemical in ctd_chemicals:
                if not chemical in list_durgbank_mesh:
                    list_durgbank_mesh.append(chemical)
                if chemical in dict_chemical_id_chemical:
                    dict_chemical_id_chemical[chemical].append(chemical_id)
                else:
                    dict_chemical_id_chemical[chemical] = [chemical_id]
        counter_of_used_chemical += count_chemicals_drugbank

        query = '''MATCH p=(a)-[r:equal_to_CTD_chemical]->(b)  Where not exists(a.integrated) With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            number_of_compound_to_work_with) + ''' Set a.integrated='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))
        list_time_all_finding_chemical.append(time_measurement)

        start = time.time()
        # counter number of chmicals without drugbank id
        counter_chemicals_without_db = 0
        for chemical_id, ctd_chemicals, in results:
            counter_chemicals_without_db += 1
            all_chemicals_id.extend(ctd_chemicals)
            for chemical in ctd_chemicals:
                if not chemical in list_mesh:
                    list_mesh.append(chemical)
                if chemical in dict_chemical_id_chemical:
                    dict_chemical_id_chemical[chemical].append(chemical_id)
                else:
                    dict_chemical_id_chemical[chemical] = [chemical_id]

        counter_of_used_chemical += counter_chemicals_without_db


        time_measurement = time.time() - start
        print('\t Generate dictionary: %.4f seconds' % (time_measurement))
        list_time_dict_chemical.append(time_measurement)
        start = time.time()

        all_chemicals_id = '","'.join(all_chemicals_id)
        query = '''MATCH (chemical:CTDchemical)-[r:affects_CGO]->(go:CTDGO) Where chemical.chemical_id in ["''' + all_chemicals_id + '''"] RETURN chemical.chemical_id, chemical.drugBankIDs, r, go.go_id, go.ontology '''
        results = g.run(query)

        time_measurement = time.time() - start
        print('\t Find all association: %.4f seconds' % (time_measurement))
        list_time_find_association.append(time_measurement)

        start = time.time()

        # dictionary with all pairs and properties as value
        dict_chemical_go = {}

        for chemical_id, drugbank_ids, rela, go_id, ontology, in results:
            counter += 1
            rela = dict(rela)
            correctedPValue = rela['correctedPValue'] if 'correctedPValue' in rela else ''
            targetTotalQty = rela['targetTotalQty'] if 'targetTotalQty' in rela else ''
            backgroundMatchQty = rela['backgroundMatchQty'] if 'backgroundMatchQty' in rela else []
            targetMatchQty = rela['targetMatchQty'] if 'targetMatchQty' in rela else ''
            pValue = rela['pValue'] if 'pValue' in rela else ''
            backgroundTotalQty = rela['backgroundTotalQty'] if 'backgroundTotalQty' in rela else ''
            drugbank_ids = drugbank_ids if not drugbank_ids is None else []
            if len(drugbank_ids) >0:
                for drugbank_id in drugbank_ids:
                    if (drugbank_id, go_id) in dict_chemical_go:
                        dict_chemical_go[(drugbank_id, go_id)][0].add(correctedPValue)
                        dict_chemical_go[(drugbank_id, go_id)][1].add(targetTotalQty)
                        dict_chemical_go[(drugbank_id, go_id)][2].add(backgroundMatchQty)
                        dict_chemical_go[(drugbank_id, go_id)][3].add(targetMatchQty)
                        dict_chemical_go[(drugbank_id, go_id)][4].add(pValue)
                        dict_chemical_go[(drugbank_id, go_id)][5].add(backgroundTotalQty)
                        dict_chemical_go[(drugbank_id, go_id)][6].add(ontology)
                        dict_chemical_go[(drugbank_id, go_id)][7].add(chemical_id)
                        # print('drugbank')
                        # print(drugbank_id, go_id)
                        # print(dict_chemical_go[(drugbank_id, go_id)])
                    else:
                        dict_chemical_go[(drugbank_id, go_id)] = [set([correctedPValue]), set([targetTotalQty]), set([backgroundMatchQty]),
                                                                       set([targetMatchQty]), set([pValue]),
                                                                       set([backgroundTotalQty]),set([ontology]), set([chemical_id])]
                        dict_processe_counter[ontology] += 1
            else:
                if (chemical_id, go_id) in dict_chemical_go:
                    dict_chemical_go[(chemical_id, go_id)][0].add(correctedPValue)
                    dict_chemical_go[(chemical_id, go_id)][1].add(targetTotalQty)
                    dict_chemical_go[(chemical_id, go_id)][2].add(backgroundMatchQty)
                    dict_chemical_go[(chemical_id, go_id)][3].add(targetMatchQty)
                    dict_chemical_go[(chemical_id, go_id)][4].add(pValue)
                    dict_chemical_go[(chemical_id, go_id)][5].add(backgroundTotalQty)
                    dict_chemical_go[(chemical_id, go_id)][6].add(ontology)
                    dict_chemical_go[(chemical_id, go_id)][6].add(chemical_id)
                    print('mesh')
                    print(dict_chemical_go[(chemical_id, go_id)])
                else:
                    dict_chemical_go[(chemical_id, go_id)] = [set([correctedPValue]), set([targetTotalQty]), set([backgroundMatchQty]),
                                                                       set([targetMatchQty]), set([pValue]),
                                                                       set([backgroundTotalQty]),set([ontology]), set([chemical_id])]
                dict_processe_counter[ontology] += 1

            if counter % 10000 == 0:
                print(counter)

                time_measurement = time.time() - start
                print('\tTake 10000 pairs: %.4f seconds' % (time_measurement))
                start = time.time()
                print('number of chemicals:'+str(counter_of_used_chemical))
                if counter % 1000000:
                    print(datetime.datetime.utcnow())

        print('number of relationships:' + str(counter))
        time_measurement = time.time() - start
        print('\t Generate dictionary go-chemical: %.4f seconds' % (time_measurement))
        list_time_dict_association.append(time_measurement)
        start = time.time()

        print(len(dict_chemical_go))

        for (chemical_id, go_id), information in dict_chemical_go.items():
            ontologys=list(information[6])
            # directEvidences = filter(bool, list(information[1]))
            for ontology in ontologys:
                add_information_into_te_different_csv_files((chemical_id,go_id),information,dict_processe[ontology])


        time_measurement = time.time() - start
        print('\t Add information to file: %.4f seconds' % (time_measurement))
        list_time_add_to_file.append(time_measurement)


    print('number of chemicals:' + str(len(list_mesh)))
    print('number of chemicals with db:' + str(len(list_durgbank_mesh)))

    query = '''MATCH (n:Chemical) REMOVE n.integrated, n.integrated_drugbank'''
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
    print('Take all chemical-go relationships and generate csv and cypher file')

    take_all_relationships_of_gene_pathway()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
