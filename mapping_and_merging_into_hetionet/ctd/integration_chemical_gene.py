# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 11:41:20 2017

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv, sys

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


# dictionary with all pairs and properties as value
dict_chemical_gene_general = {}

# dictionary with all pairs which are associated with change of action and properties as value
dict_chemical_gene_regulation = {}

# dictionary with all pairs which are associated with binding
dict_chemical_gene_binding = {}

# dictionary with all pairs which are associated with metabolic processing
dict_chemical_gene_metabolic_processing = {}

# dictionary with all pairs which are associated with transport
dict_chemical_gene_transport = {}

# counter of relationships
count_multiple_action = 0
count_all_action = 0
count_multiple_general = 0
count_all_general = 0

# dictionary pairs of chemical,gene
dict_pairs = {}

# list of all important relationship actions
list_important_regulation = ['activity', 'expression', 'degradation']
list_important_transport = ['transport', 'secretion', 'export', 'uptake', 'import']
list_metabolic_processing = []

file = open('chemical_gene/metabolic_processing_action.csv', 'r')
for line in file:
    list_metabolic_processing.append(line.split(',')[0])

'''
sort into the the directory
'''


def integration_into_dictionary(dict_action, chemical, gene, interaction_text, gene_forms, pubMedIds,
                                interactions_actions, interaction_dict, chemical_name, gene_name, chemical_synonyms,
                                gene_symbol):
    if (chemical, gene) in dict_action:
        dict_action[(chemical, gene)][0].append(interaction_text)
        dict_action[(chemical, gene)][1].extend(gene_forms)
        dict_action[(chemical, gene)][1] = list(
            set(dict_action[(chemical, gene)][1]))
        dict_action[(chemical, gene)][2].extend(pubMedIds)
        dict_action[(chemical, gene)][2] = list(
            set(dict_action[(chemical, gene)][2]))
        dict_action[(chemical, gene)][3].append(interactions_actions)
        dict_action[(chemical, gene)][6].append(interaction_dict)
    else:
        dict_action[(chemical, gene)] = [[interaction_text], gene_forms, pubMedIds,
                                         [interactions_actions], (chemical_name, gene_name),
                                         chemical_synonyms, [interaction_dict], gene_symbol]


'''
sort into the different dictionaries and check if they are multiple relas
'''


def sort_information_in_dictionary(chemical, gene, interaction_text, gene_forms, pubMedIds, interactions_actions,
                                   chemical_name, gene_name, chemical_synonyms, action_bool,
                                   interaction_dict, gene_symbol, transport_bool, binding_bool,
                                   metabolic_processing_bool):
    global count_all_action, count_multiple_action, count_all_general, count_multiple_general
    any_actions=False
    if action_bool:
        any_actions = True
        count_all_action += 1
        integration_into_dictionary(dict_chemical_gene_regulation, chemical, gene, interaction_text, gene_forms,
                                    pubMedIds,
                                    interactions_actions, interaction_dict, chemical_name, gene_name, chemical_synonyms,
                                    gene_symbol)

    if transport_bool:
        any_actions = True
        count_all_action += 1
        integration_into_dictionary(dict_chemical_gene_transport, chemical, gene, interaction_text, gene_forms,
                                    pubMedIds,
                                    interactions_actions, interaction_dict, chemical_name, gene_name, chemical_synonyms,
                                    gene_symbol)

    if binding_bool:
        any_actions = True
        count_all_action += 1
        integration_into_dictionary(dict_chemical_gene_binding, chemical, gene, interaction_text, gene_forms,
                                    pubMedIds,
                                    interactions_actions, interaction_dict, chemical_name, gene_name, chemical_synonyms,
                                    gene_symbol)
    if metabolic_processing_bool:
        any_actions = True
        count_all_action += 1
        integration_into_dictionary(dict_chemical_gene_metabolic_processing, chemical, gene, interaction_text,
                                    gene_forms,
                                    pubMedIds,
                                    interactions_actions, interaction_dict, chemical_name, gene_name, chemical_synonyms,
                                    gene_symbol)

    count_all_general += 1
    if (chemical, gene) in dict_chemical_gene_general:
        count_multiple_general += 1
        dict_chemical_gene_general[(chemical, gene)][0].append(interaction_text)
        dict_chemical_gene_general[(chemical, gene)][1].extend(gene_forms)
        dict_chemical_gene_general[(chemical, gene)][1] = list(set(dict_chemical_gene_general[(chemical, gene)][1]))
        dict_chemical_gene_general[(chemical, gene)][2].extend(pubMedIds)
        dict_chemical_gene_general[(chemical, gene)][2] = list(set(dict_chemical_gene_general[(chemical, gene)][2]))
        dict_chemical_gene_general[(chemical, gene)][3].append(interactions_actions)
    else:
        dict_chemical_gene_general[(chemical, gene)] = [[interaction_text], gene_forms, pubMedIds,
                                                        [interactions_actions], (chemical_name, gene_name),chemical_synonyms]


'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a csv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_pathway():
    counter_all_rela = 0
    counter_two = 0

    #  Where chemical.chemical_id='C025540' and gene.gene_id='2741'
    query = '''MATCH (chemical:CTDchemical)-[r:associates_CG{organism_id:'9606'}]->(gene:CTDgene) Where chemical.chemical_id='C516138' and gene.gene_id='1'  RETURN gene.gene_id, gene.name, gene.geneSymbol, r, chemical.chemical_id, chemical.name, chemical.synonyms, chemical.drugBankIDs Limit 2000'''
    results = g.run(query)

    for gene_id, gene_name, gene_symbol, rela, chemical_id, chemical_name, chemical_synonyms, drugbank_ids, in results:
        counter_all_rela += 1
        interaction_text = rela['interaction_text'] if 'interaction_text' in rela else ''
        gene_forms = rela['gene_forms'] if 'gene_forms' in rela else []
        pubMedIds = rela['pubMedIds'] if 'pubMedIds' in rela else []
        interactions_actions = rela['interactions_actions'] if 'interactions_actions' in rela else []
        drugbank_ids = drugbank_ids if not drugbank_ids is None else []

        chemical_synonyms = chemical_synonyms if not chemical_synonyms is None else []
        chemical_synonyms = filter(None, chemical_synonyms)

        interaction_dict = {}
        interaction_action = False
        transport_bool = False
        binding_bool = False
        metabolic_processing_bool = False
        for interaction in interactions_actions:
            splitter = interaction.split('^')
            if splitter[1] not in interaction_dict:
                interaction_dict[splitter[1]] = [splitter[0]]
            else:
                interaction_dict[splitter[1]].append(splitter[0])
            if splitter[1] in list_important_regulation:
                # print(interactions_actions)
                interaction_action = True
            elif splitter[1] == 'binding':
                binding_bool = True
            elif splitter[1] in list_important_transport:
                transport_bool = True
            elif splitter[1] in list_metabolic_processing:
                metabolic_processing_bool = True

        # if len(interactions_actions) > 2 and interaction_action:
        #     interaction_action = True
        # elif interaction_action and len(interactions_actions) == 2:
        #     counter_two += 1

        if len(drugbank_ids) > 0:
            for drugbank in drugbank_ids:
                sort_information_in_dictionary(drugbank, gene_id, interaction_text, gene_forms, pubMedIds,
                                               interactions_actions, chemical_name, gene_name, chemical_synonyms,
                                               interaction_action, interaction_dict, gene_symbol, transport_bool,
                                               binding_bool, metabolic_processing_bool)
        else:
            sort_information_in_dictionary(chemical_id, gene_id, interaction_text, gene_forms, pubMedIds,
                                           interactions_actions, chemical_name, gene_name, chemical_synonyms,
                                           interaction_action, interaction_dict, gene_symbol, transport_bool,
                                           binding_bool, metabolic_processing_bool)

        if counter_all_rela % 10000 == 0:
            print(counter_all_rela)

    print('number of multiple possible action:' + str(count_multiple_action))
    print('number of new possible action:' + str(count_all_action))
    print('number of multiple all:' + str(count_multiple_general))
    print('number of all:' + str(count_all_general))
    print(counter_two)


# csv files
csvfile_up = open('chemical_gene/relationships_upregulated_chemical_gene.csv', 'wb')
writer_upregulated = csv.writer(csvfile_up, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_upregulated.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_up_other_way_around = open('chemical_gene/relationships_upregulated_gene_chemical.csv', 'wb')
writer_upregulated_other_way_around = csv.writer(csvfile_up_other_way_around, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)
writer_upregulated_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_down = open('chemical_gene/relationships_downregulated_chemical_gene.csv', 'wb')
writer_downrgulated = csv.writer(csvfile_down, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_downrgulated.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_down_other_way_around = open('chemical_gene/relationships_downregulated_gene_chemical.csv', 'wb')
writer_downrgulated_other_way_around = csv.writer(csvfile_down_other_way_around, delimiter=',', quotechar='"',
                                                  quoting=csv.QUOTE_MINIMAL)
writer_downrgulated_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_association = open('chemical_gene/relationships_association_chemical_gene.csv', 'wb')
writer_association = csv.writer(csvfile_association, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_association.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_association_other_way_around = open('chemical_gene/relationships_association_gene_chemical.csv', 'wb')
writer_association_other_way_around = csv.writer(csvfile_association_other_way_around, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)
writer_association_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_binding = open('chemical_gene/relationships_binding_chemical_gene.csv', 'wb')
writer_binding = csv.writer(csvfile_binding, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_binding.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_binding_other_way_around = open('chemical_gene/relationships_association_gene_chemical.csv', 'wb')
writer_binding_other_way_around = csv.writer(csvfile_binding_other_way_around, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)
writer_binding_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_metabolic_processing = open('chemical_gene/relationships_metabolic_processing_chemical_gene.csv', 'wb')
writer_metabolic_processing = csv.writer(csvfile_metabolic_processing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_metabolic_processing.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_metabolic_processing_other_way_around = open('chemical_gene/relationships_association_gene_chemical.csv', 'wb')
writer_metabolic_processing_other_way_around = csv.writer(csvfile_metabolic_processing_other_way_around, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)
writer_metabolic_processing_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_transport_out = open('chemical_gene/relationships_transport_out_chemical_gene.csv', 'wb')
writer_transport_out = csv.writer(csvfile_transport_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_transport_out.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_out_other_way_around = open('chemical_gene/relationships_transport_out_gene_chemical.csv', 'wb')
writer_transport_out_other_way_around = csv.writer(csvfile_out_other_way_around, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)
writer_transport_out_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_in = open('chemical_gene/relationships_transport_in_chemical_gene.csv', 'wb')
writer_transport_in = csv.writer(csvfile_in, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_transport_in.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_in_other_way_around = open('chemical_gene/relationships_transport_in_gene_chemical.csv', 'wb')
writer_transport_in_other_way_around = csv.writer(csvfile_in_other_way_around, delimiter=',', quotechar='"',
                                                  quoting=csv.QUOTE_MINIMAL)
writer_transport_in_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_transport = open('chemical_gene/relationships_transport_chemical_gene.csv', 'wb')
writer_transport = csv.writer(csvfile_transport, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_transport.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

csvfile_transport_other_way_around = open('chemical_gene/relationships_transport_gene_chemical.csv', 'wb')
writer_transport_other_way_around = csv.writer(csvfile_transport_other_way_around, delimiter=',', quotechar='"',
                                                 quoting=csv.QUOTE_MINIMAL)
writer_transport_other_way_around.writerow(
    ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'chemical_name',
     'gene_name'])

'''
function to sort the information into the right file for activity, expression and degradation
'''


def sort_regulation_information_into_the_different_files(action, action_value, position_chemical, position_gene,
                                                         chemical, gene,
                                                         interaction_texts_string, gene_forms, pubMedIds,
                                                         interactions_actions_string, one_upregulated_other_way_around,
                                                         one_upregulated, one_downregulated_other_way_around,
                                                         one_downregulated, one_associated,
                                                         one_associated_other_way_around, chemical_name, gene_name):
    if (action in ['activity', 'expression'] and action_value == 'increases') or (
            action == 'degradation' and action_value == 'decreases'):
        dict_pairs[(chemical, gene)] = 'yes'

        if position_gene < position_chemical and not one_upregulated_other_way_around:
            writer_upregulated_other_way_around.writerow(
                [chemical, gene, interaction_texts_string, gene_forms, pubMedIds,
                 interactions_actions_string, chemical_name, gene_name])
            one_upregulated_other_way_around = True
        elif position_chemical < position_gene and not one_upregulated:
            writer_upregulated.writerow([chemical, gene, interaction_texts_string, gene_forms, pubMedIds,
                                         interactions_actions_string, chemical_name, gene_name])
            one_upregulated = True
    elif (action in ['activity', 'expression'] and action_value == 'decreases') or (
            action_value == 'degradation' and action_value == 'increases'):
        dict_pairs[(chemical, gene)] = 'yes'

        if position_gene < position_chemical and not one_upregulated_other_way_around:
            writer_downrgulated_other_way_around.writerow(
                [chemical, gene, interaction_texts_string, gene_forms, pubMedIds,
                 interactions_actions_string, chemical_name, gene_name])
            one_downregulated_other_way_around = True
        elif position_chemical < position_gene and not one_downregulated:
            writer_downrgulated.writerow([chemical, gene, interaction_texts_string, gene_forms, pubMedIds,
                                          interactions_actions_string, chemical_name, gene_name])
            one_downregulated = True
        # else:
        #
        #     print('double down')

    # elif action in ['activity', 'expression', 'degradation']:
    #     # print(chemical, gene)
    #
    #     if not one_associated and position_chemical < position_gene:
    #         writer_association.writerow([
    #             chemical, gene, interaction_texts_string, gene_forms, pubMedIds,
    #             interactions_actions_string, chemical_name, gene_name])
    #         one_associated = True
    #     elif not one_associated_other_way_around and position_gene < position_chemical:
    #         writer_association_other_way_around.writerow([
    #             chemical, gene, interaction_texts_string, gene_forms, pubMedIds,
    #             interactions_actions_string, chemical_name, gene_name])
    #         one_associated_other_way_around = True
        # else:
        #     print('double association')

    return one_upregulated, one_upregulated_other_way_around, one_downregulated, one_downregulated_other_way_around, one_associated, one_associated_other_way_around


'''
preparation of the information for the csv files
'''


def preparation_of_information(chemical, gene, interactions_actions, interaction_texts, gene_forms, pubMedIds,
                               chemical_name, chemical_synonyms):
    interactions_actions_combine = []
    interactions_actions_combine.extend(interactions_actions)
    if (chemical, gene) in dict_chemical_gene_general:
        list_pair_general = dict_chemical_gene_general[(chemical, gene)]
        interaction_texts.extend(list_pair_general[0])
        gene_forms.extend(list_pair_general[1])
        gene_forms = list(set(gene_forms))
        pubMedIds.extend(list_pair_general[2])
        pubMedIds = list(set(pubMedIds))
        interactions_actions_combine.extend(list_pair_general[3])

    interaction_texts_string = '|'.join(interaction_texts)
    gene_forms = '|'.join(gene_forms)
    pubMedIds = '|'.join(pubMedIds)
    interactions_actions_string = ''
    for interaction_list in interactions_actions_combine:
        interactions_actions_string += '|'.join(interaction_list) + ';'
    # interactions_actions_string = '|'.join(interactions_actions)
    interactions_actions_string = interactions_actions_string[0:-1]

    if not chemical_name is None and chemical_name != '':
        chemical_synonyms.insert(0, chemical_name)


    return interaction_texts, gene_forms, pubMedIds, interactions_actions_combine, interaction_texts_string, interactions_actions_string, chemical_synonyms

'''
search for chemical
'''
def search_for_chemical(chemical_name, chemical_synonyms,interaction_texts):
    found_chemical = False
    found_chemical_synonym = ''
    for chemical_synonym in chemical_synonyms:
        possible_position = interaction_texts[0].find(chemical_synonym)
        if possible_position != -1:
            found_chemical_synonym = chemical_synonym
            found_chemical = True
            break
    if not found_chemical:
        print('chemical name not found')
        print(chemical_name)
    found_chemical_synonym = found_chemical_synonym if found_chemical else chemical_name
    return found_chemical_synonym


'''
find used name for chemical and gene for text mining
'''


def find_text_name_for_chemical_and_gene(chemical_name, chemical_synonyms, gene_name, gene_symbol, interaction_texts):
    found_gene = False
    found_chemical_synonym = search_for_chemical(chemical_name, chemical_synonyms,interaction_texts)

    found_gene_synonym = ''
    possible_position = interaction_texts[0].find(gene_symbol)
    if possible_position != -1:
        found_gene_synonym = gene_symbol
        found_gene = True
    found_gene_synonym = found_gene_synonym if found_gene else gene_name

    return found_gene_synonym, found_chemical_synonym


'''
finde the position of the chemical and gene in the interaction text and return this
'''


def find_position_of_chemical_and_gene_in_text(found_chemical_synonym, found_gene_synonym, interaction_text):
    position_chemical = -1
    position_gene = -1

    found_gene = False
    found_chemical = False
    possible_position = interaction_text.find(found_chemical_synonym)
    if possible_position != -1:
        position_chemical = possible_position
        found_chemical = True
    position_chemical = default_value_position if not found_chemical else position_chemical

    possible_position = interaction_text.find(found_gene_synonym)
    if possible_position != -1:
        position_gene = possible_position
        found_gene = True
    position_gene = default_value_position if not found_gene else position_gene

    return position_chemical, position_gene


# default value if the position of chemical or gene is not found
default_value_position = 10000

'''
generate the different csv files for upregulation, downregulation and association and also the cypher file
'''


def generate_csv_and_cypher_file():
    # generate cypher file
    cypherfile = open('chemical_gene/cypher.cypher', 'w')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (c:Chemical)-[r:BINDS_CbG]->(b:Gene) Where not exists(r.hetionet) Set r.hetionet="yes", r.resource=["Hetionet"];\n')
    cypherfile.write('commit\n')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (c:Chemical)-[r:UPREGULATES_CuG]->(b:Gene) Where not exists(r.hetionet) Set r.hetionet="yes", r.resource=["Hetionet"];\n')
    cypherfile.write('commit\n')
    cypherfile.write('begin\n')
    cypherfile.write(
        'Match (c:Chemical)-[r:BINDS_CbG]->(b:Gene) Where not exists(r.hetionet) Set r.hetionet="yes", r.resource=["Hetionet"];\n')
    cypherfile.write('commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/gene_pathway/relationships.csv" As line Match (n:Gene{identifier:toInteger(line.GeneID)}), (b:Pathway{identifier:line.PathwayID}) Merge (n)-[r:PARTICIPATES_GpPW]->(b) On Create Set r.hetionet='no', r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", r.unbiased='false' On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n '''
    cypherfile.write(query)
    cypherfile.write('begin\n')
    cypherfile.write('Match (c:Chemical)-[r:BINDS_CbG]->(b:Gene) Where not exists(r.ctd) Set r.ctd="no";\n')
    cypherfile.write('commit')
    counter_only_two = 0
    counter_two_and_one = 0

    # go through all with information about up or down regulated relas
    for (chemical, gene), [interaction_texts, gene_forms, pubMedIds, interactions_actions, (chemical_name, gene_name),
                           chemical_synonyms, interaction_dicts, gene_symbol] in dict_chemical_gene_regulation.items():
        # some relationships can be switched to the general list but all data should be combined
        # because the this variables do not checked twice by general only

        interaction_texts, gene_forms, pubMedIds, interactions_actions_combine, interaction_texts_string, interactions_actions_string, chemical_synonyms = preparation_of_information(
            chemical, gene, interactions_actions, interaction_texts, gene_forms, pubMedIds, chemical_name,
            chemical_synonyms)

        # check that ich pair appears only one time in eache file
        one_upregulated = False
        one_upregulated_other_way_around = False
        one_downregulated = False
        one_downregulated_other_way_around = False
        one_associated = False
        one_associated_other_way_around = False

        counter = 0

        found_gene_synonym, found_chemical_synonym = find_text_name_for_chemical_and_gene(chemical_name,
                                                                                          chemical_synonyms, gene_name,
                                                                                          gene_symbol,
                                                                                          interaction_texts)

        for interactions_action in interactions_actions:
            position_chemical, position_gene = find_position_of_chemical_and_gene_in_text(found_chemical_synonym,
                                                                                          found_gene_synonym,
                                                                                          interaction_texts[counter])

            if len(interactions_action) > 1:
                has_at_least_one_time_two_action = True
                # print(chemical,gene)
            interaction_text = interaction_texts[counter]
            interaction_dict = interaction_dicts[counter]
            interaction_dict_keys = interaction_dict.keys()
            intersection = list(set(interaction_dict_keys).intersection(list_important_regulation))

            if not position_gene == default_value_position or not position_chemical == default_value_position:
                for part in interaction_text.split('['):
                    for smaller_part in part.split(']'):
                        # find take every time the first time when the substring appeares, so some times the chemcial appears multiple
                        # time so the order for the sub action need to be new classified
                        position_chemical_new = smaller_part.find(found_chemical_synonym)
                        position_gene_new = smaller_part.find(found_gene_synonym)
                        if position_chemical_new != -1 and position_gene_new != -1:
                            for word in smaller_part.split(' '):
                                if word in list_important_regulation:
                                    one_upregulated, one_upregulated_other_way_around, one_downregulated, one_downregulated_other_way_around, one_associated, one_associated_other_way_around = sort_regulation_information_into_the_different_files(
                                        word, interaction_dict[word], position_chemical_new,
                                        position_gene_new, chemical,
                                        gene, interaction_texts_string, gene_forms, pubMedIds,
                                        interactions_actions_string, one_upregulated_other_way_around,
                                        one_upregulated,
                                        one_downregulated_other_way_around,
                                        one_downregulated, one_associated, one_associated_other_way_around,
                                        chemical_name, gene_name)


                                    # print('complex two')
                                    # print(interactions_action)
                                    # print(interaction_text)
                                    # print(chemical_name, gene_name)
                        #     if not found_something:
                        #         one_upregulated, one_upregulated_other_way_around, one_downregulated, one_downregulated_other_way_around, one_associated, one_associated_other_way_around = sort_regulation_information_into_the_different_files(
                        #             intersection[0], 'associated', position_chemical,
                        #             position_gene, chemical,
                        #             gene, interaction_texts_string, gene_forms, pubMedIds,
                        #             interactions_actions_string, one_upregulated_other_way_around,
                        #             one_upregulated,
                        #             one_downregulated_other_way_around,
                        #             one_downregulated, one_associated, one_associated_other_way_around,
                        #             chemical_name, gene_name)
                        #
                        # else:
                        #     one_upregulated, one_upregulated_other_way_around, one_downregulated, one_downregulated_other_way_around, one_associated, one_associated_other_way_around = sort_regulation_information_into_the_different_files(
                        #         intersection[0], 'associated', position_chemical,
                        #         position_gene, chemical,
                        #         gene, interaction_texts_string, gene_forms, pubMedIds,
                        #         interactions_actions_string, one_upregulated_other_way_around,
                        #         one_upregulated,
                        #         one_downregulated_other_way_around,
                        #         one_downregulated, one_associated, one_associated_other_way_around, chemical_name,
                        #         gene_name)
            else:
                print('this exists')

            counter += 1



            # counter += 1

            # for action in interactions_action:
            #     splitter = action.split('^')
            #     one_upregulated, one_upregulated_other_way_around, one_downregulated, one_downregulated_other_way_around, one_associated, one_associated_other_way_around = sort_regulation_information_into_the_different_files(
            #         splitter[1], splitter[0], position_chemical, position_gene, chemical,
            #         gene, interaction_texts_string, gene_forms, pubMedIds,
            #         interactions_actions_string, one_upregulated_other_way_around, one_upregulated,
            #         one_downregulated_other_way_around,
            #         one_downregulated, one_associated, one_associated_other_way_around, chemical_name, gene_name)

        # go through all with information about up or down regulated relas
    # for (chemical, gene), [interaction_texts, gene_forms, pubMedIds, interactions_actions, (chemical_name, gene_name),
    #                        chemical_synonyms, interaction_dicts, gene_symbol] in dict_chemical_gene_binding.items():
    #     # some relationships can be switched to the general list but all data should be combined
    #     # because the this variables do not checked twice by general only
    #     interactions_actions_combine = []
    #     interactions_actions_combine.extend(interactions_actions)
    #     if (chemical, gene) in dict_chemical_gene_general:
    #         list_pair_general = dict_chemical_gene_general[(chemical, gene)]
    #         interaction_texts.extend(list_pair_general[0])
    #         gene_forms.extend(list_pair_general[1])
    #         gene_forms = list(set(gene_forms))
    #         pubMedIds.extend(list_pair_general[2])
    #         pubMedIds = list(set(pubMedIds))
    #         interactions_actions_combine.extend(list_pair_general[3])
    #
    #     interaction_texts_string = '|'.join(interaction_texts)
    #     gene_forms = '|'.join(gene_forms)
    #     pubMedIds = '|'.join(pubMedIds)
    #     interactions_actions_string = ''
    #     for interaction_list in interactions_actions_combine:
    #         interactions_actions_string += '|'.join(interaction_list) + ';'
    #     # interactions_actions_string = '|'.join(interactions_actions)
    #     interactions_actions_string = interactions_actions_string[0:-1]
    #
    #     if not chemical_name is None and chemical_name != '':
    #         chemical_synonyms.insert(0, chemical_name)
    #
    #     dict_pairs[(chemical, gene)] = 'yes'

    for (chemical, gene), [interaction_texts, gene_forms, pubMedIds,
                           interactions_actions, (chemical_name, gene_name), chemical_synonyms] in dict_chemical_gene_general.items():
        chemical_synonyms.insert(0,chemical_name)
        found_chemical_name_in_interaction_text= search_for_chemical(chemical_name,chemical_synonyms,interaction_texts)
        counter=0
        interactions_actions_string = ''
        cotreatment_list=[]
        for interaction_list in interactions_actions:
            interactions_actions_string += '|'.join(interaction_list) + ';'
            for interaction in interaction_list:
                if interaction.split('^')[1]=='cotreatment':
                    interaction_text=interaction_texts[counter]
                    for part_interaction_text in interaction_text.split('['):
                        for small_part in part_interaction_text.split(']'):
                            if small_part.find(found_chemical_name_in_interaction_text) != -1 and small_part.find('co-treated')!=-1:
                                cotreatment_list.append(interaction_text)


            counter+=1
        if (chemical, gene) in dict_pairs and len(cotreatment_list)==0:
            continue
        elif len(cotreatment_list)>0:
            print(interaction_text)
            print(chemical_name, gene_name)
            print(chemical,gene)
        interaction_texts = '|'.join(interaction_texts)
        gene_forms = '|'.join(gene_forms)
        pubMedIds = '|'.join(pubMedIds)

        # interactions_actions_string = '|'.join(interactions_actions)
        interactions_actions_string = interactions_actions_string[0:-1]
        # interactions_actions_string='|'.join(interactions_actions)
        writer_association.writerow([
            chemical, gene, interaction_texts, gene_forms, pubMedIds, interactions_actions_string, chemical_name,
            gene_name])


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Take all gene-pathway relationships and generate csv and cypher file')

    take_all_relationships_of_gene_pathway()
    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print(' generate csv and cypher file')

    generate_csv_and_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
