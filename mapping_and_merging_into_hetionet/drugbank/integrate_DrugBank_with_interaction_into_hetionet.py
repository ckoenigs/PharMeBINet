# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 16:07:43 2018

@author: ckoenig
"""

from py2neo import Graph, authenticate
import datetime
import sys, csv

# reload(sys)
# sys.setdefaultencoding("utf-8")

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary of all compounds with key the drugbank id and list of url, name, inchi, inchikey, food interaction,
# alternative ids
dict_compounds = {}

# list drugbank ids of all compounds which are already in Hetionet in hetionet
list_compounds_in_hetionet = []

# dictionary drugbank ids of all compounds which are already in Hetionet in hetionet with the resource list
dict_compounds_in_hetionet = {}

# old_properties
old_properties = []

# new compound properties
list_new_properties = []

# neo4j_label_drugbank='DrugBankdrug'
neo4j_label_drugbank = 'Compound_DrugBank'

# neo4j_interaction_rela_label='interacts'
neo4j_interaction_rela_label = 'interacts_CiC'

# set of properties which are list element
set_of_list_properties = set([])

'''
Get all properties of the hetionet compounds and durgbank compounds and use them to generate the csv files
'''


def get_mondo_properties_and_generate_csv_files():
    # get the properties of the compounds in hetionet
    query = '''MATCH (p:Compound) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''
    result = g.run(query)
    for property, in result:
        old_properties.append(property)

    # fill the list with all properties in drugbank and not in Hetionet
    query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys
            UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
            RETURN allfields;''' % (neo4j_label_drugbank)
    result = g.run(query)
    for property, in result:
        if property not in old_properties:
            list_new_properties.append(property)

    list_new_properties.append('xrefs')
    global all_properties
    all_properties = list(set(old_properties).union(list_new_properties))

    # generate csv files
    global csv_update, csv_new, csv_update_alt

    new_nodes = open('output/new_nodes.csv', 'w')
    csv_new = csv.DictWriter(new_nodes, delimiter='\t', fieldnames=all_properties)
    csv_new.writeheader()

    all_properties_and_additional = all_properties[:]
    all_properties_and_additional.append('doid')

    update_nodes = open('output/update_nodes.csv', 'w')
    csv_update = csv.DictWriter(update_nodes, delimiter='\t', fieldnames=all_properties_and_additional)
    csv_update.writeheader()

    all_properties_alternative = all_properties[:]
    all_properties_alternative.append('alternative_id')

    update_nodes_alt = open('output/update_nodes_alt.csv', 'w')
    csv_update_alt = csv.DictWriter(update_nodes_alt, delimiter='\t', fieldnames=all_properties_alternative)
    csv_update_alt.writeheader()


'''
load all disease in the dictionary
has properties:
name 
identifier
source
license
url
'''


def load_all_hetionet_compound_in_dictionary():
    query = '''Match (n:Compound) RETURN n '''
    results = g.run(query)
    for compound, in results:
        list_compounds_in_hetionet.append(compound['identifier'])
        dict_compounds_in_hetionet[compound['identifier']] = dict(compound)
    print('size of compound in Hetionet before the rest of DrugBank is added: ' + str(len(list_compounds_in_hetionet)))

# the new table for unii drugbank pairs
unii_drugbank_table_file = open('data/map_unii_to_drugbank_id.tsv', 'w')
csv_unii_drugbank_table=csv.writer(unii_drugbank_table_file,delimiter='\t')
csv_unii_drugbank_table.write(['unii','drugbank_id'])


'''
Load in all information from DrugBank.
and generate unii-durgbank table file 
'''


def load_all_DrugBank_compound_in_dictionary():
    query = '''Match (n:''' + neo4j_label_drugbank + ''') RETURN n '''
    print(query)
    results = g.run(query)
    for compound, in results:
        all_information = dict(compound)
        id = compound['identifier']
        if 'unii' in compound:
            unii= compound['unii']
            csv_unii_drugbank_table.writerow([unii,id])
        if id == 'DB13179':
            print('huh')
        dict_compounds[id] = all_information
    print('size of drugbank: ' + str(len(dict_compounds)))


# dictionary with (durg1, drug2) and url, description
dict_interact_relationships_with_infos = {}

'''
load all the is_a relationships from MonDO into a dictionary with the resource
'''


def load_in_all_interaction_connection_from_drugbank_in_dict():
    # query = '''MATCH p=(a)-[r:'''+neo4j_interaction_rela_label+''']->(b) RETURN a.identifier,r.url, r.describtion ,b.identifier  '''
    query = '''MATCH p=(a:%s)-[r:''' + neo4j_interaction_rela_label + ''']->(b:%s) RETURN a.identifier, r.description ,b.identifier '''
    query = query % (neo4j_label_drugbank, neo4j_label_drugbank)
    print(query)
    results = g.run(query)
    print(datetime.datetime.utcnow())
    counter_interactions = 0
    counter_multiple = 0
    for compound1_id, description, compound2_id, in results:
        counter_interactions += 1
        if (compound1_id, compound2_id) in dict_interact_relationships_with_infos:
            dict_interact_relationships_with_infos[(compound1_id, compound2_id)].append(description)
            counter_multiple += 1
        elif (compound2_id, compound1_id) in dict_interact_relationships_with_infos:
            dict_interact_relationships_with_infos[(compound2_id, compound1_id)].append(description)
            counter_multiple += 1
        else:
            dict_interact_relationships_with_infos[(compound1_id, compound2_id)] = [description]

    print(counter_interactions)
    print('number of double interaction:' + str(counter_multiple))
    print('number of interaction:' + str(len(dict_interact_relationships_with_infos)))

#bash shell for merge doids into the mondo nodes
bash_shell=open('merge_nodes.sh','w')
bash_shell.write('#!/bin/bash\n')


# label_of_alternative_ids='alternative_ids' old one
label_of_alternative_ids = 'alternative_drugbank_ids'
# dictionary of drugbank id and to the used ids in Hetionet
dict_drugbank_to_alternatives = {}

# show wich properties are not in the old compounds or in the new compounds
list_not_fiting_properties = set([])

'''
Integrate all DrugBank id into Hetionet
'''


def integrate_DB_compound_information_into_hetionet():
    # count already existing compound
    counter_already_existing_compound = 0
    # count all new drugbank compounds
    counter_new_compound = 0

    #show which nodes are multiple time in hetionet
    file_combined_drugbanks = open('compound_interaction/combine_file.txt', 'w')
    list_set_key_with_values_length_1 = set([])

    # merge list of xrefs
    list_merge_xrefs = ['external_identifiers', 'xrefs']

    # integrate or add Hetionet compounds
    for drugbank_id, information in dict_compounds.items():
        list_merge_xref_values = set([])
        if drugbank_id == 'DB13179':
            print('huh')
        if drugbank_id == 'DB00536':
            print('unii')

        if label_of_alternative_ids in information:
            alternative_ids = information[label_of_alternative_ids]
        else:
            alternative_ids = []
        alternative_ids.append(drugbank_id)
        # search for intersection between new db id + alternative ids and hetionet compounds ids
        intersection = list(set(alternative_ids).intersection(list_compounds_in_hetionet))
        # at least on of the new drugbank ids is in hetionet
        if len(intersection) > 0:
            counter_already_existing_compound += 1

            # add the intersection drugbank to the alternative dictionary
            # shows if more then one appears two time
            multiple_db_ids = False
            # alternative id is integrated
            alternative_id_integrated = False
            # more the one mapped to one node
            if len(intersection) > 1:
                dict_drugbank_to_alternatives[drugbank_id] = intersection
                intersection_string = ''
                for db in intersection:
                    intersection_string += db + ' '
                file_combined_drugbanks.write(intersection_string[0:-1] + '\n')
                print('intersection')
                print(intersection)
                multiple_db_ids = True
                # sys.exit('intersection')
            # the alternative id mapped
            elif intersection[0] != drugbank_id:
                dict_drugbank_to_alternatives[drugbank_id] = intersection
                alternative_id_integrated = True
                print('problem')
                print(drugbank_id)
                print(intersection)

            drug_id = intersection[0]
            if multiple_db_ids:
                # it would cause errors if not the node with the same id is updated and the other one is merged
                if drugbank_id in intersection:
                    drug_id=drugbank_id
                    intersection.remove(drug_id)
                else:
                    intersection.remove(drug_id)
                # write into bash file which nodes need to be combined
                for alternative_drug_id in intersection:
                    text = 'python ../add_information_from_a_not_existing_node_to_existing_node.py %s %s %s\n' % (
                        alternative_drug_id, drugbank_id, 'Compound')
                    bash_shell.write(text)
                    text = '''now=$(date +"%F %T")
                        echo "Current time: $now"\n'''
                    bash_shell.write(text)

            dict_info_prepared = {}
            for key, property in information.items():
                # to merge the information into one both information must be combine
                if key in list_merge_xrefs:
                    list_merge_xref_values = list_merge_xref_values.union(property)
                    continue

                if type(property) == list:
                    set_of_list_properties.add(key)
                    if key in dict_compounds_in_hetionet[drug_id]:
                        # this is only for one time, because I integrated the food interaction  sometimes wrong
                        # if key != 'food_interaction':
                        property.extend(dict_compounds_in_hetionet[drug_id][key])
                        property = list(set(property))
                    elif key not in list_new_properties and key not in old_properties:
                        list_not_fiting_properties.add(key)
                    if key == label_of_alternative_ids:
                        property.append(drugbank_id)
                        property = list(set(property))
                    dict_info_prepared[key] = '|'.join(property).encode('utf-8').replace('"', "'")
                else:
                    if key in dict_compounds_in_hetionet[drug_id]:
                        # in the most cases if the values are different take the newest on
                        if dict_compounds_in_hetionet[drug_id][key] != property:

                            if key == 'unii':
                                # only this three the older fits better
                                if drug_id in ['DB11200', 'DB10360', 'DB09561']:
                                    property = dict_compounds_in_hetionet[drug_id][key]
                        # else:
                        #     print('same property')
                            # print('for a key')
                            # print(key)
                            # print(property)
                        dict_info_prepared[key] = property.encode('utf-8').replace('"', "'")

                    elif key not in list_new_properties and not key in old_properties:
                        list_not_fiting_properties.add(key)
                    else:
                        dict_info_prepared[key] = property.encode('utf-8').replace('"', "'")

                dict_info_prepared['xrefs'] = '|'.join(list_merge_xref_values).encode('utf-8')
                if alternative_id_integrated:
                    dict_info_prepared['alternative_id'] = drug_id
                    csv_update_alt.writerow(dict_info_prepared)

                else:
                    csv_update.writerow(dict_info_prepared)


        else:
            # create a new node
            counter_new_compound += 1
            dict_info_prepared = {}
            for key, property in information.items():

                # to merge the information into one both information must be combinate
                if key in list_merge_xrefs:
                    list_merge_xref_values = list_merge_xref_values.union(property)
                    continue
                if type(property) == list:
                    set_of_list_properties.add(key)
                    if key == label_of_alternative_ids:
                        property = list(set(property))

                    dict_info_prepared[key] = '|'.join(property).encode('utf-8').replace('"', "'")
                else:
                    dict_info_prepared[key] = property.encode('utf-8').replace('"', "'")

            combinded_merge_string = '|'.join(list_merge_xref_values)
            dict_info_prepared['xrefs'] = combinded_merge_string

            csv_new.writerow(dict_info_prepared)

    print(list_set_key_with_values_length_1)
    print('already existing compound:' + str(counter_already_existing_compound))
    print('new compound:' + str(counter_new_compound))

    if len(list_not_fiting_properties) > 0:
        print(list_not_fiting_properties)
        sys.exit('not fitting')


'''
Create cypher file
'''


def create_cypher_file():
    # cypher file
    cypher_file = open('cypher.cypher', 'w')

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/output/%s.csv" As line Fieldterminator '\\t' Match (a:%s{identifier:line.identifier})'''
    query_create = ''
    query_update = ''
    for property in all_properties:
        # this is for all similar
        if property in ['resource', 'license', 'source', 'url']:
            continue
        if property in set_of_list_properties:
            query_create += property + ':split(line.' + property + ',"|"), '
            query_update += 'b.' + property + '=split(line.' + property + ',"|"), '
        else:
            query_create += property + ':line.' + property + ', '
            query_update += 'b.' + property + '=line.' + property + ', '

    query_update_alternativ = query_start + ', (b:Compound{identifier:line.alternative_id}) Set b.drugbank="yes", ' + query_update + 'b.resource=b.resource+"DrugBank", b.url="http://www.drugbank.ca/drugs/"+line.identifier, b.license="CC BY-NC 4.0" Create (b)-[:equal_to_drugbank]->(a);\n'
    query_update_alternativ = query_update_alternativ % ('update_nodes_alt', neo4j_label_drugbank)
    cypher_file.write(query_update_alternativ)

    query_update = query_start + ', (b:Compound{identifier:line.identifier}) Set b.drugbank="yes", ' + query_update + 'b.resource=b.resource+"DrugBank", b.url="http://www.drugbank.ca/drugs/"+line.identifier, b.license="CC BY-NC 4.0" Create (b)-[:equal_to_drugbank]->(a);\n'
    query_update = query_update % ('update_nodes', neo4j_label_drugbank)
    cypher_file.write(query_update)

    query_create = query_start + 'Create (b:Compound{identifier:line.identifier, drugbank:"yes", ' + query_create + 'resource:["DrugBank"], url:"http://www.drugbank.ca/drugs/"+line.identifier, license:"CC BY-NC 4.0"}) Create (b)-[:equal_to_drugbank]->(a);\n'
    query_create = query_create % ('new_nodes', neo4j_label_drugbank)
    cypher_file.write(query_create)


'''
Generate the the interaction file and the cypher file to integrate the information from the csv into neo4j
'''


def generation_of_interaction_file():
    # generate cypher file for interaction
    counter_connection = 0

    counter_both_alternative = 0
    one_alternative = 0
    count_no_alternative = 0

    g_csv = open('compound_interaction/interaction.csv', 'w')
    csv_writer = csv.writer(g_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['db1', 'db2', 'description'])
    cypherfile = open('compound_interaction/cypher_interaction.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/compound_interaction/interaction.csv" As line Match (c1:Compound{identifier:line.db1}), (c2:Compound{identifier:line.db2}) Create (c1)-[:INTERACTS_CiC{source:"DrugBank", unbiased:'false', resource:['DrugBank'], url:line.url, license:'CC BY-NC 4.0', description:split(line.description,'|')}]->(c2);\n '''
    cypherfile.write(query)
    cypherfile.close()

    print(dict_drugbank_to_alternatives)

    set_alt = set([])
    counter_all_interaction = 0

    for (compound1, compound2), description in dict_interact_relationships_with_infos.items():

        counter_all_interaction += len(description)
        description = list(set(description))
        description = '|'.join(description)
        if not compound2 in dict_drugbank_to_alternatives and not compound1 in dict_drugbank_to_alternatives:
            count_no_alternative += 1
            counter_connection += 1
            description = description.encode('utf-8')
            csv_writer.writerow([compound1, compound2, description])
        elif compound2 in dict_drugbank_to_alternatives:
            if compound1 in dict_drugbank_to_alternatives:
                counter_both_alternative += 1
                set_alt.add(compound1)
                set_alt.add(compound2)
                for drug2 in dict_drugbank_to_alternatives[compound2]:
                    for drug1 in dict_drugbank_to_alternatives[compound1]:
                        description = description.encode('utf-8')
                        csv_writer.writerow([drug1, drug2, description])
                        counter_connection += 1

            else:
                one_alternative += 1
                for drug2 in dict_drugbank_to_alternatives[compound2]:
                    set_alt.add(compound2)
                    description = description.encode('utf-8')
                    csv_writer.writerow([compound1, drug2, description])
                    counter_connection += 1
        else:
            one_alternative += 1
            for drug1 in dict_drugbank_to_alternatives[compound1]:
                set_alt.add(compound1)
                description = description.encode('utf-8')
                csv_writer.writerow([drug1, compound2, description])
                counter_connection += 1

    print(counter_connection)
    print('one has the alternative id in Hetionet:' + str(one_alternative))
    print('both have the alternative id in Hetionet:' + str(counter_both_alternative))
    print('both are in Hetionet with normal id:' + str(count_no_alternative))
    print('counter of all interaction:' + str(counter_all_interaction))
    print(set_alt)


def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all properties of compound and drugbank compound and use the information to genreate csv files')

    get_mondo_properties_and_generate_csv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all hetionet compound in dictionary')

    load_all_hetionet_compound_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all DrugBank compounds in dictionary')

    load_all_DrugBank_compound_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all connection in dictionary')

    load_in_all_interaction_connection_from_drugbank_in_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('integrate drugbank into hetionet')

    integrate_DB_compound_information_into_hetionet()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('create cypher queries and cypher file')

    create_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('generate cypher file for interaction')

    generation_of_interaction_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
