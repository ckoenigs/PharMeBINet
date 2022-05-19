import datetime, time
import csv, sys
import numpy as np

sys.path.append("../..")
import create_connection_to_databases

# change socket time out
# http.socket_timeout = 9999

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary with all pairs and properties as value
dict_disease_gene = {}

# list time all disease finding
list_time_all_finding_disease = []

# list time generate mondo ctd id dict
list_time_dict_mondo = []

# list time dict association
list_time_dict_association = []

# list time find association
list_time_find_association = []

# list time add to file
list_time_add_to_file = []

# dictionary disease-gene to pubmeds and resources
dict_disease_gene_to_pubmeds_and_resources = {}


def load_existing_gene_disease_pairs():
    """
    Load all existing pairs and pubmed and resource information and write it into a dictionary
    :return:
    """
    query = 'Match (b:Disease)-[r:ASSOCIATES_DaG]->(n:Gene) Return b.identifier, n.identifier, r.pubMed_ids, r.resource'
    results = g.run(query)
    for disease_id, gene_id, pubmed_ids, resources, in results:
        dict_disease_gene_to_pubmeds_and_resources[(disease_id, gene_id)] = [set(pubmed_ids),
                                                                             set(resources)] if pubmed_ids is not None else [
            set(), set(resources)]


'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a tsv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_disease():
    # generate cypher file
    cypherfile = open('output/cypher_edge.cypher', 'a', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + \
            '''mapping_and_merging_into_hetionet/ctd/gene_disease/relationships.tsv" As line  FIELDTERMINATOR '\\t' Match (n:Gene{identifier:line.GeneID}), (b:Disease{identifier:line.DiseaseID}) Merge (b)-[r:ASSOCIATES_DaG]->(n) On Create Set  r.ctd='yes', r.url="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.resource=["CTD"], r.source="CTD", r.inferences=split(line.inferences,'|'), r.pubMed_ids=split(line.pubMed_ids,'|'), r.directEvidences=split(line.directEvidence,'|') ,r.omimIDs=split(line.omimIDs,'|'), r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2021 NC State University. All rights reserved.", r.unbiased=toBoolean(line.unbiased) On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID, r.unbiased=toBoolean(line.unbiased), r.inferences=split(line.inferences,'|'), r.pubMed_ids=split(line.pubMed_ids,'|'), r.directEvidences=split(line.directEvidence,'|') ,r.omimIDs=split(line.omimIDs,'|'), r.resource=split(line.resources,'|') ;\n '''
    cypherfile.write(query)

    csvfile = open('gene_disease/relationships.tsv', 'w', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GeneID', 'DiseaseID', 'inferences', 'pubMed_ids', 'directEvidence', 'omimIDs', 'unbiased', 'resources'])

    # counter directEvidence
    counter_directEvidence = 0

    # counter inferences
    counter_inferences = 0

    # sys.exit()
    number_of_compound_to_work_with = 10

    counter_of_used_disease = 0
    count_multiple_pathways = 0
    count_possible_relas = 0
    counter_all = 0
    counter_direct_evidence = 0

    start = time.time()
    # and a.identifier='MONDO:0013604'
    query = '''MATCH p=(a:Disease)-[r]->(b:CTD_disease) RETURN a.identifier , b.disease_id '''

    # print(query)
    # sys.exit()
    results = g.run(query)
    time_measurement = time.time() - start
    print('\tTake ' + str(number_of_compound_to_work_with) + ' disease: %.4f seconds' % (time_measurement))
    list_time_all_finding_disease.append(time_measurement)

    dict_disease_id_mondo = {}
    start = time.time()
    for mondo, ctd_disease_id, in results:
        if ctd_disease_id in dict_disease_id_mondo:
            dict_disease_id_mondo[ctd_disease_id].append(mondo)
        else:
            dict_disease_id_mondo[ctd_disease_id] = [mondo]

    time_measurement = time.time() - start
    print('\t Generate dictionary: %.4f seconds' % (time_measurement))
    list_time_dict_mondo.append(time_measurement)

    start = time.time()

    # print(dict_disease_id_mondo)

    query = '''MATCH (disease:CTD_disease)<-[r:associates_GD]-(gene:CTD_gene) Where (gene)--(:Gene) and (disease)--(:Disease) and exists(r.directEvidence) and exists(r.pubMed_ids)  RETURN Distinct gene.gene_id, r, disease.disease_id '''
    results = g.run(query)

    time_measurement = time.time() - start
    print('\t Find all association: %.4f seconds' % (time_measurement))
    list_time_find_association.append(time_measurement)
    start = time.time()
    # dictionary with all pairs and properties as value
    dict_disease_gene = {}

    for gene_id, rela, disease_id, in results:
        counter_all += 1
        rela = dict(rela)
        inferenceChemicalName = rela['inferenceChemicalName'] if 'inferenceChemicalName' in rela else ''
        inferenceScore = rela['inferenceScore'] if 'inferenceScore' in rela else ''
        directEvidence = rela['directEvidence'] if 'directEvidence' in rela else ''
        pubMed_ids = set(rela['pubMed_ids']) if 'pubMed_ids' in rela else set()
        omimIDs = set(rela['omimIDs']) if 'omimIDs' in rela else set()

        counter_direct_evidence += 1
        for mondo in dict_disease_id_mondo[disease_id]:
            tuple_ids = (gene_id, mondo)
            if inferenceScore == '' and inferenceChemicalName == '':
                inference_info = ''
            elif inferenceScore == '':
                print('inference score empty but name not')
                inference_info = inferenceChemicalName
            elif inferenceChemicalName == '':
                print('inference name empty but score not')
                inference_info = inferenceScore
            else:
                inference_info = inferenceChemicalName + ':' + inferenceScore

            if not (gene_id, mondo) in dict_disease_gene:
                resource=set(['CTD'])
                if (mondo,gene_id) in dict_disease_gene_to_pubmeds_and_resources:
                    resource=resource.union(dict_disease_gene_to_pubmeds_and_resources[(mondo,gene_id)][1])
                    pubMed_ids=pubMed_ids.union(dict_disease_gene_to_pubmeds_and_resources[(mondo,gene_id)][0])

                dict_disease_gene[tuple_ids] = [{inference_info},
                                                {directEvidence}, pubMed_ids, omimIDs, resource]
                count_possible_relas += 1
            else:
                dict_disease_gene[tuple_ids][0].add(inference_info)
                dict_disease_gene[tuple_ids][1].add(directEvidence)
                dict_disease_gene[tuple_ids][2]=dict_disease_gene[tuple_ids][2].union(pubMed_ids)
                dict_disease_gene[tuple_ids][3]=dict_disease_gene[tuple_ids][3].union(omimIDs)

                count_multiple_pathways += 1

        if counter_all % 10000 == 0:
            print(counter_all)

    time_measurement = time.time() - start
    print('\t Generate dictionary disease gene: %.4f seconds' % (time_measurement))
    list_time_dict_association.append(time_measurement)
    start = time.time()
    for (gene_id, mondo), [inferences, directEvidence, pubMed_ids, omimIDs,resources] in dict_disease_gene.items():
        inferences_string = '|'.join(filter(bool, inferences))
        directEvidence_string = '|'.join(filter(bool, directEvidence))
        pubMed_ids_string = '|'.join(filter(bool, pubMed_ids))
        omimIDs_string = '|'.join(filter(bool, omimIDs))
        resources='|'.join(sorted(resources))

        if len(directEvidence) == 0:
            sys.exit('if this happend that it has an error in disease-gene edge')
            counter_inferences += 1
            writer.writerow(
                [gene_id, mondo, inferences_string, pubMed_ids_string, directEvidence_string, omimIDs_string,
                 'false'])

        else:
            counter_directEvidence += 1
            writer.writerow(
                [gene_id, mondo, inferences_string, pubMed_ids_string, directEvidence_string, omimIDs_string,
                 'true', resources])

    time_measurement = time.time() - start
    print('\t Add information to file: %.4f seconds' % (time_measurement))
    list_time_add_to_file.append(time_measurement)

    counter_of_used_disease += number_of_compound_to_work_with

    print('Average finding disease:' + str(np.mean(list_time_all_finding_disease)))
    print('Average dict monde:' + str(np.mean(list_time_dict_mondo)))
    print('Average finding association:' + str(np.mean(list_time_find_association)))
    print('Min finding association:' + str(min(list_time_find_association)))
    print('Max finding association:' + str(max(list_time_find_association)))
    print('Average dict association:' + str(np.mean(list_time_dict_association)))
    print('Average add to file:' + str(np.mean(list_time_add_to_file)))

    print('number of direct evidence rela:' + str(counter_directEvidence))
    print('number of inferences rela:' + str(counter_inferences))
    print(counter_all)
    print(counter_direct_evidence)
    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ctd d-g')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load existings disease-gene pairs')

    load_existing_gene_disease_pairs()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Take all gene-disease relationships and generate tsv and cypher file')

    take_all_relationships_of_gene_disease()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
