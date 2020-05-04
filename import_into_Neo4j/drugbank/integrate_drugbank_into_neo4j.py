# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:49:17 2018

@author: Cassandra
"""
from py2neo import Graph, authenticate
import datetime
import sys, csv
import pandas as pd

# dictionary for every drug with all information about this:name, inchikey, inchi, food interaction, alternative ids
dict_drug_info = {}

# dictionary for every drug interaction: with def as value
dict_drug_interaction_info = {}

# dictionary alternative id to id
dict_alternative_to_id = {}

'''
This takes all information from Drugbank and sort them in the different dictionaries 
0: drugbank_id	
1: alternative drugbank ids
2: name	
3: type	
4: cas_number
5: groups	
6: atc_codes	
7: categories	
8: inchikey	
9: inchi	
10: inchikeys	
11: synonyms	
12:unii	
13:uniis	
14:external_identifiers	
15:extra_names	
16:brands	
17:molecular_forula	
18:molecular_formular_experimental	
/19:gene_sequence	
/20:amino_acid_sequence	
19:sequence	
20:drug_interaction	
21:drug_interaction_description	
22:food_interaction
23:toxicty
24:targets
25:transporter
26:pathways
27:dosages
28:snps
29:enzymes
30:carriers
31:description
'''


def get_drugbank_information(drugbank_file):
    node_cypher=open('node_cypher.cypher','w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/'''+drugbank_file+ '''" As line FIELDTERMINATOR '\\t' Create (c:DrugBankdrug{ id:line.drugbank_id, name: line.name, inchikey:line.inchikey , inchi: line.inchi,  food_interaction: line.food_interaction, url: 'http://www.drugbank.ca/drugs/'+line.drugbank_id, license:"CC BY-NC 4.0", alternative_ids:split(line.drugbank_ids,'|') ,type:line.type, cas_number:line.cas_number, groups:split(line.groups,'|'), atc_codes:split(line.atc_codes,'|'), categories:split(line.categories,'|'), salt_inchikeys:split(line.inchikeys,'|'), synonyms:split(line.synonyms,'|'), unii:line.unii, salt_uniis:split(line.uniis,'|') , xrefs:split(line.external_identifiers,'|'), brands:split(line.brands,'|'), salt_names:split(line.extra_names,'|'), molecular_formula:line.molecular_formula, sequences:split(line.sequences,'|')}) ;\n'''
    node_cypher.write(query)
    edge_cypher = open('edge_cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/csv_drug_interaction.csv" As line Match (drug1:DrugBankdrug{id: line.Drug1}), (drug2:DrugBankdrug{id: line.Drug2}) Create (drug1)-[:interacts{url: 'http://www.drugbank.ca/drugs/' + line.Drug1 , description: line.description}] ->(drug2); \n'''
    edge_cypher.write(query)

    # drugbank tsv
    f = open(drugbank_file, 'r')
    tsv_reader= pd.read_csv(f, sep='\t')

    # new file for drug interaction
    csvfile= open('csv_drug_interaction.csv','w')
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Drug1', 'Drug2', 'description'])
    for index, line in tsv_reader.iterrows():
        # print(line)
        drugbank_id = line['drugbank_id']
        # print(line)
        # print('blub')
        # print(line['drug_interaction'])
        if type(line['drug_interaction'])==float:
            continue
        drug_interaction = line['drug_interaction'].split('|')
        drug_interaction_description = line['drug_interaction_description'].split('|')

        i=0
        for interaction in drug_interaction:
            if not (interaction,drugbank_id) in dict_drug_interaction_info:
                writer.writerow([drugbank_id,interaction,drug_interaction_description[i]])
                dict_drug_interaction_info[(drugbank_id,interaction)]=drug_interaction_description[i]
            i+=1





    print('number of different drugbank ids:' + str(len(dict_drug_info)))
    print('number of different interaction ids:' + str(len(dict_drug_interaction_info)))


'''
Generate cypher file for drugbank information
'''


def generate_cypher_file():
    i = 1
    # number of queries for a commit block
    constrain_number = 20000

    # number of quereies in a file
    creation_max_in_file = 1000000

    f = open('DrugBank_database_' + str(i) + '.cypher', 'w')
    f.write('begin \n')
    i += 1

    #    h=open('Sider_update_edges.cypher','w',encoding="utf-8")
    #    h.write('begin \n')

    # first add all queries with sider drugs
    counter_create = 0
    print('drug Create')
    print (datetime.datetime.utcnow())
    for identifier, info_list in dict_drug_info.items():
        url = 'http://www.drugbank.ca/drugs/' + identifier
        create_text = 'Create (:DrugBankdrug{id: "%s" , name: "%s", inchikey: "%s", inchi: "%s",  food_interaction: "%s", url: "%s", license:"CC BY-NC 4.0", alternative_ids: "%s"} ); \n' % (
            identifier, info_list[0], info_list[1], info_list[2], info_list[3], url, info_list[4])
        # print(create_text)
        counter_create += 1
        f.write(create_text)
        #        if counter_create>2:
        #            break
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('DrugBank_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit \n begin \n')
    # set stitch stereo ID as key and unique
    f.write('Create Constraint On (node:DrugBankdrug) Assert node.id Is Unique; \n')
    f.write('commit \n schema await \n begin \n')
    print('number of new nodes:' + str(counter_create))
    number_of_new_nodes = counter_create

    count_interaction_with_removed_drugbank_ids = 0
    # i=0
    print('edges Create')
    print (datetime.datetime.utcnow())

    for (drug_id1, drug_id2), describtion in dict_drug_interaction_info.items():
        # i+=1
        url = 'http://www.drugbank.ca/drugs/' + drug_id1

        if drug_id1 not in dict_alternative_to_id or drug_id2 not in dict_alternative_to_id:
            count_interaction_with_removed_drugbank_ids += 1
            continue
        drug_id1 = dict_alternative_to_id[drug_id1]
        drug_id2 = dict_alternative_to_id[drug_id2]
        create_text = ''' Match (drug1:DrugBankdrug{id: "%s"}), (drug2:DrugBankdrug{id: "%s"})
        Create (drug1)-[:interacts{url: "%s" , description: "%s"}] ->(drug2); \n''' % (
            drug_id1, drug_id2, url, describtion)
        # print(create_text)
        #        print(query)
        counter_create += 1
        f.write(create_text)
        #        if counter_create>2:
        #            break
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('DrugBank_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
        # if i==5000:
        #     break
    f.write('commit')
    print('number of interaction edges:' + str(counter_create - number_of_new_nodes))
    print('number of interaction where one drugbank id was removed from the database:' + str(
        count_interaction_with_removed_drugbank_ids))


def main():
    print (datetime.datetime.utcnow())
    print('import drugbank information')
    if len(sys.argv)< 2:
        print('need drugbank file')
        sys.exit()
    get_drugbank_information(sys.argv[1])

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('generate cypher file')

    #generate_cypher_file()

    print('#############################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
