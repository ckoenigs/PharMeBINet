import datetime, time
import csv, sys

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


'''
get all relationships between gene and pathway, take the pharmebinet identifier and gaather all information in a dictionary 
'''


def take_all_relationships_of_gene_disease():
    # generate cypher file
    cypherfile = open('chemical_pathway/cypher.cypher', 'w')

    query = ''' Match (n:Pathway{identifier:line.PathwayID}), (b:Chemical{identifier:line.ChemicalID}) Merge (b)-[r:ASSOCIATES_CaP]->(n) On Create Set  r.ctd='yes', r.correctedPValues=split(line.correctedPValues,'|') , r.targetTotalQtys=split(line.targetTotalQtys,'|'), r.backgroundMatchQtys=split(line.backgroundMatchQtys,'|'), r.targetMatchQtys=split(line.targetMatchQtys,'|'), r.pValues=split(line.pValues,'|'), r.backgroundTotalQtys=split(line.backgroundTotalQtys,'|'), r.url_ctd="http://ctdbase.org/detail.go?type=chem&acc="+line.ChemicalID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2024 NC State University. All rights reserved.", r.unbiased=false On Match SET r.ctd='yes', r.correctedPValues=split(line.correctedPValues,'|') , r.targetTotalQtys=split(line.targetTotalQtys,'|'), r.backgroundMatchQtys=split(line.backgroundMatchQtys,'|'), r.targetMatchQtys=split(line.targetMatchQtys,'|'), r.pValues=split(line.pValues,'|'), r.backgroundTotalQtys=split(line.backgroundTotalQtys,'|'), r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID  '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/chemical_pathway/relationships.tsv',
                                              query)
    cypherfile.write(query)

    csvfile = open('chemical_pathway/relationships.tsv', 'wb')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(
        ['PathwayID', 'ChemicalID', 'correctedPValues', 'targetTotalQtys', 'backgroundMatchQtys', 'targetMatchQtys',
         'pValues', 'backgroundTotalQtys'])

    query = '''Match (c:Chemical) Where (c)-[:equal_chemical_CTD]-() or (c)-[:equal_to_CTD_chemical]-() Return count(c) as v'''
    result = g.run(query)
    number_of_chemicals = int(result.single()['v'])
    print(number_of_chemicals)
    # number_of_chemicals=100
    limit_number = 100
    start = time.time()

    count_multiple_pathways = 0
    count_possible_relas = 0
    counter_all = 0

    counter_number_of_used_chemicals = 0
    i = 0
    old_counter = 0

    while counter_number_of_used_chemicals < number_of_chemicals:
        print(counter_number_of_used_chemicals)

        all_chemicals_id = []

        start = time.time()
        query = '''MATCH p=(a)-[r:equal_chemical_CTD]->(b)  Where a.integrated_drugbank is NULL With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            limit_number) + ''' Set a.integrated_drugbank='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake ' + str(limit_number) + ' compound: %.4f seconds' % (time_measurement))

        start = time.time()
        # counter chemicals with drugbank ids
        count_chemicals_drugbank = 0
        dict_ctd_chemical_to_drugbank = {}
        for record in results:
            [chemical_id, ctd_chemicals] = record.values()

            count_chemicals_drugbank += 1
            all_chemicals_id.extend(ctd_chemicals)
            for ctd_chemical in ctd_chemicals:
                if ctd_chemical not in dict_ctd_chemical_to_drugbank:
                    dict_ctd_chemical_to_drugbank[ctd_chemical] = [chemical_id]
                else:
                    dict_ctd_chemical_to_drugbank[ctd_chemical].append(chemical_id)
        counter_number_of_used_chemicals += count_chemicals_drugbank

        query = '''MATCH p=(a)-[r:equal_to_CTD_chemical]->(b)  Where a.integrated is NULL With  a, collect(b.chemical_id) As ctd Limit ''' + str(
            limit_number) + ''' Set a.integrated='yes'  RETURN a.identifier , ctd '''

        # print(query)
        # sys.exit()
        results = g.run(query)
        time_measurement = time.time() - start
        # print('\tTake ' + str(number_of_compound_to_work_with) + ' compound: %.4f seconds' % (time_measurement))

        start = time.time()
        # counter number of chmicals without drugbank id
        counter_chemicals_without_db = 0
        for record in results:
            [chemical_id, ctd_chemicals] = record.values()
            counter_chemicals_without_db += 1
            all_chemicals_id.extend(ctd_chemicals)

        counter_number_of_used_chemicals += counter_chemicals_without_db

        if counter_number_of_used_chemicals == old_counter:
            i += 1
            if i == 5:
                sys.exit()
        else:
            old_counter = counter_number_of_used_chemicals
            i = 0

        # dictionary with all pairs and properties as value
        dict_chemical_pathway = {}

        # counter_number_of_used_chemicals+=limit_number
        all_chemicals_id = '","'.join(all_chemicals_id)
        query = '''MATCH (chemical)-[r:associates_CP]->(pathway) Where chemical.chemical_id in ["''' + all_chemicals_id + '''"]  With  collect({pwid:pathway.pharmebinet_id, backgroundTotalQty: r.backgroundTotalQty, pValue:r.pValue, targetMatchQty:r.targetMatchQty, backgroundMatchQty:r.backgroundMatchQty, targetTotalQty:r.targetTotalQty, correctedPValue:r.correctedPValue }) As relas, chemical RETURN  chemical.chemical_id, chemical.drugBankIDs, relas '''
        # query = '''MATCH (chemical)-[r:associates_CP]->(pathway) Where chemical.chemical_id in ["''' + all_chemicals_id + '''"]  With  collect({pwid:pathway.pharmebinet_id, backgroundTotalQty: r.backgroundTotalQty, pValue:r.pValue, targetMatchQty:r.targetMatchQty, backgroundMatchQty:r.backgroundMatchQty, targetTotalQty:r.targetTotalQty, correctedPValue:r.correctedPValue }) As relas, chemical Limit ''' + str(
        #     limit_number) + ''' Set chemical.integrated='yes'  RETURN  chemical.chemical_id, chemical.drugBankIDs, relas '''
        # query ='''MATCH (chemical)-[r:associates_CP]->(pathway) Where not exists(chemical.integrated) and chemical.chemical_id='D006844' With  collect({pwid:pathway.pharmebinet_id, backgroundTotalQty: r.backgroundTotalQty, pValue:pathway.pValue, targetMatchQty:pathway.targetMatchQty, backgroundMatchQty:pathway.backgroundMatchQty, targetTotalQty:pathway.targetTotalQty, correctedPValue:pathway.correctedPValue }) As relas, chemical Limit '''+str(limit_number)+''' Set chemical.integrated='yes'  RETURN  chemical.chemical_id, chemical.drugBankIDs, relas '''
        # query = '''MATCH (chemical)-[r:associates_CP]->(pathway) Where not exists(chemical.integrated) and chemical.chemical_id='D006844' With chemical, r, pathway Limit '''+str(limit_number)+''' Set chemical.integrated='yes' RETURN pathway.pharmebinet_id, r, chemical.chemical_id, chemical.drugBankIDs '''
        # print(query)
        results = g.run(query)
        time_measurement = time.time() - start
        print('\tTake  compound: %.4f seconds' % (time_measurement))

        for record in results:
            [chemical_id, drugbank_ids, relas] = record.values()
            for rela in relas:
                counter_all += 1

                correctedPValue = rela['correctedPValue'] if 'correctedPValue' in rela else ''
                targetTotalQty = rela['targetTotalQty'] if 'targetTotalQty' in rela else ''
                backgroundMatchQty = rela['backgroundMatchQty'] if 'backgroundMatchQty' in rela else ''
                targetMatchQty = rela['targetMatchQty'] if 'targetMatchQty' in rela else ''
                pValue = rela['pValue'] if 'pValue' in rela else ''
                backgroundTotalQty = rela['backgroundTotalQty'] if 'backgroundTotalQty' in rela else ''
                pathway_id = rela['pwid']

                drugbank_ids = drugbank_ids if not drugbank_ids is None else []
                # if len(drugbank_ids)>0:
                if chemical_id in dict_ctd_chemical_to_drugbank:
                    for drugbank_id in dict_ctd_chemical_to_drugbank[ctd_chemical]:
                        if not (pathway_id, drugbank_id) in dict_chemical_pathway:
                            count_possible_relas += 1
                            dict_chemical_pathway[(pathway_id, drugbank_id)] = [[correctedPValue], [targetTotalQty],
                                                                                [backgroundMatchQty], [targetMatchQty],
                                                                                [pValue],
                                                                                [backgroundTotalQty]]
                        else:
                            count_multiple_pathways += 1
                            dict_chemical_pathway[(pathway_id, drugbank_id)][0].append(correctedPValue)
                            dict_chemical_pathway[(pathway_id, drugbank_id)][1].append(targetTotalQty)
                            dict_chemical_pathway[(pathway_id, drugbank_id)][2].append(backgroundMatchQty)
                            dict_chemical_pathway[(pathway_id, drugbank_id)][3].append(targetMatchQty)
                            dict_chemical_pathway[(pathway_id, drugbank_id)][4].append(pValue)
                            dict_chemical_pathway[(pathway_id, drugbank_id)][5].append(backgroundTotalQty)
                            # print(dict_chemical_pathway[(pathway_id, drugbank_id)])
                else:
                    if not (pathway_id, chemical_id) in dict_chemical_pathway:
                        count_possible_relas += 1
                        dict_chemical_pathway[(pathway_id, chemical_id)] = [[correctedPValue], [targetTotalQty],
                                                                            [backgroundMatchQty], [targetMatchQty],
                                                                            [pValue],
                                                                            [backgroundTotalQty]]
                    else:
                        count_multiple_pathways += 1
                        dict_chemical_pathway[(pathway_id, chemical_id)][0].append(correctedPValue)
                        dict_chemical_pathway[(pathway_id, chemical_id)][1].append(targetTotalQty)
                        dict_chemical_pathway[(pathway_id, chemical_id)][2].append(backgroundMatchQty)
                        dict_chemical_pathway[(pathway_id, chemical_id)][3].append(targetMatchQty)
                        dict_chemical_pathway[(pathway_id, chemical_id)][4].append(pValue)
                        dict_chemical_pathway[(pathway_id, chemical_id)][5].append(backgroundTotalQty)
                        # print(dict_chemical_pathway[(pathway_id, chemical_id)])

                if count_possible_relas % 100000 == 0:
                    print('relas')
                    print(count_possible_relas)
                    print(counter_all)
                    print(datetime.datetime.now())
                    print(counter_number_of_used_chemicals)

        for (pathway_id, mondo), [correctedPValues, targetTotalQtys, backgroundMatchQtys, targetMatchQtys, pValues,
                                  backgroundTotalQtys] in dict_chemical_pathway.items():
            correctedPValues = filter(bool, list(set(correctedPValues)))
            correctedPValues = '|'.join(correctedPValues)
            targetTotalQtys = filter(bool, list(set(targetTotalQtys)))
            targetTotalQtys = '|'.join(targetTotalQtys)
            backgroundMatchQtys = filter(bool, list(set(backgroundMatchQtys)))
            backgroundMatchQtys = '|'.join(backgroundMatchQtys)
            targetMatchQtys = filter(bool, list(set(targetMatchQtys)))
            targetMatchQtys = '|'.join(targetMatchQtys)
            pValues = filter(bool, list(set(pValues)))
            pValues = '|'.join(pValues)
            backgroundTotalQtys = filter(bool, list(set(backgroundTotalQtys)))
            backgroundTotalQtys = '|'.join(backgroundTotalQtys)
            writer.writerow(
                [pathway_id, mondo, correctedPValues, targetTotalQtys, backgroundMatchQtys, targetMatchQtys, pValues,
                 backgroundTotalQtys])
        # if counter_number_of_used_chemicals%1000==0:
        #     print(counter_number_of_used_chemicals)

    print(counter_all)
    print(counter_number_of_used_chemicals)
    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))
    query = '''Match (c:Chemical) Remove c.integrated, c.integrated_drugbank '''
    g.run(query)


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
    print('Take all gene-pathway relationships and generate tsv and cypher file')

    take_all_relationships_of_gene_disease()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
