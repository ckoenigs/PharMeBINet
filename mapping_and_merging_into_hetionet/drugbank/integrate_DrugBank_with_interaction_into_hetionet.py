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


def create_connetion_with_neo4j():
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
old_properties = ["allfields", "salt_names", "molecular_formula", "unii", "salt_uniis", "salt_inchikeys", "cas_number",
                  "synonyms", "brands", "type", "xrefs", "alternative_ids", "inchikey", "atc_codes",
                  "alternative_drugbank_ids", "food_interaction", "drugbank", "categories", "ctd", "ctd_url", "aeolus",
                  "rxnorm_cuis", "pubChem_id", "sider", "ndf_rt", "resource", "license", "inchi", "groups", "source",
                  "url", "hetionet", "identifier", "name", "merged_identifier", "sequences", "url_ctd", "pubChem",
                  "licenses", "no_further_chemical_information"]

'''
load all disease in the dictionary
has propeteries:
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


# neo4j_label_drugbank='DrugBankdrug'
neo4j_label_drugbank = 'Compound_DrugBank'

# neo4j_interaction_rela_label='interacts'
neo4j_interaction_rela_label = 'interacts_CiC'

'''
Load in all information from DrugBank.
properties:
    food_interaction
    license
    inchikey
    inchi
    name
    alternative_ids
    id
    url
    
    {identifier:'DB01148'}
'''


def load_all_DrugBank_compound_in_dictionary():
    query = '''Match (n:''' + neo4j_label_drugbank + ''') RETURN n '''
    print(query)
    results = g.run(query)
    for compound, in results:
        # food_interaction = compound['food_interaction']
        # inchikey = compound['inchikey']
        # inchi = compound['inchi']
        # name = compound['name']
        all_information = dict(compound)
        # alternative_ids = compound['alternative_ids']
        id = compound['identifier']
        # url = compound['url']
        dict_compounds[id] = all_information
    print('size of drugbank: ' + str(len(dict_compounds)))


# dictionary with (durg1, drug2) and url, description
dict_interact_relationships_with_infos = {}

'''
load all the is_a relationships from MonDO into a dictionary with the resource
'''


def load_in_all_interaction_connection_from_drugbank_in_dict():
    # query = '''MATCH p=(a)-[r:'''+neo4j_interaction_rela_label+''']->(b) RETURN a.identifier,r.url, r.describtion ,b.identifier  '''
    query = '''MATCH p=(a:Compound_DrugBank)-[r:''' + neo4j_interaction_rela_label + ''']->(b:Compound_DrugBank) RETURN a.identifier, r.description ,b.identifier '''
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


# label_of_alternative_ids='alternative_ids' old one
label_of_alternative_ids = 'alternative_drugbank_ids'
# dictionary of drugbank id and to the used ids in Hetionet
dict_drugbank_to_alternatives = {}

list_new_properties = ['classification_kingdom', 'description', 'classification_subclass', 'packagers_name_url',
                       'classification_superclass', 'general_references_textbooks_isbn_citation',
                       'general_references_links_title_url', 'classification_class', 'classification_description',
                       'calculated_properties_kind_value_source', 'affected_organisms', 'ahfs_codes', 'absorption',
                       'manufacturers', 'protein_binding', 'prices_description_cost_unit', 'state',
                       'volume_of_distribution', 'indication', 'synthesis_reference', 'metabolism',
                       'classification_direct_parent', 'mixtures_name_ingredients',
                       'patents_number_country_approved_expires_pediatric_extension', 'mechanism_of_action',
                       'half_life', 'external_links_resource_url', 'msds', 'fda_label', 'clearance',
                       'experimental_properties_kind_value_source', 'general_references_articles_pubmed_citation',
                       'pharmacodynamics', 'external_identifiers', 'route_of_elimination',
                       'dosages_form_route_strength', 'toxicity', u'pdb_entries', u'atc_code_levels',
                       u'categories_category_mesh_id', u'international_brands_name_company', 'ChEMBL',
                       'classification_substituent', 'classification_alternative_parent']


#file with all node cypher
file_counter=1
start_node='compound_interaction/node_cypher_'
file_all_node_cypher=open(start_node+str(file_counter)+'.cypher','w')
file_counter+=1
file_all_node_cypher.write('begin\n')
counter_all_nodes=0
maximal_commits=5000
maximal_commits_file=20000

list_not_fiting_properties = set([])

file_empty_value = open('compound_interaction/empty_value.csv', 'w')
writer_empty = csv.writer(file_empty_value, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_empty.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])
file_unii_different = open('compound_interaction/different_uniis.csv', 'w')
writer_uniis = csv.writer(file_unii_different, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_uniis.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])
file_names_different = open('compound_interaction/different_names.csv', 'w')
writer_names = csv.writer(file_names_different, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_names.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])
file_inchikey_different = open('compound_interaction/different_inchikey.csv', 'w')
writer_inchikeys = csv.writer(file_inchikey_different, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_inchikeys.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])
file_inchi_different = open('compound_interaction/different_inchi.csv', 'w')
writer_inchis = csv.writer(file_inchi_different, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_inchis.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])
file_types_different = open('compound_interaction/different_types.csv', 'w')
writer_types = csv.writer(file_types_different, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_types.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])
file_casnumber_different = open('compound_interaction/different_casnumber.csv', 'w')
writer_casnumbers = csv.writer(file_casnumber_different, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_casnumbers.writerow(['Drugbank_id', 'property', 'old_value', 'new_value'])

'''
Integrate all DrugBank id into Hetionet
'''


def integrate_DB_compound_information_into_hetionet():
    global counter_all_nodes, file_counter ,file_all_node_cypher
    # count already existing compound
    counter_already_existing_compound = 0
    # count all new drugbank compounds
    counter_new_compound = 0

    file_combined_drugbanks = open('compound_interaction/combine_file.txt', 'w')
    list_set_key_with_values_length_1 = set([])

    # merge list of xrefs
    list_merge_xrefs=['external_identifiers','xrefs']


    # integrate or add Hetionet compounds
    for drugbank_id, information in dict_compounds.items():
        list_merge_xref_values = set([])
        if drugbank_id=='DB11864':
            print('huh')

        # food_interaction = information[4]
        # inchikey = information[3]
        # inchi = information[2]
        # name = information[1]
        # alternative_ids = information[5].split('|')
        # url = information[0]
        # alternative ids
        if label_of_alternative_ids in information:
            alternative_ids = information[label_of_alternative_ids]
        else:
            alternative_ids = []
        alternative_ids.append(drugbank_id)
        intersection = list(set(alternative_ids).intersection(list_compounds_in_hetionet))
        if len(intersection) > 0:
            counter_already_existing_compound += 1

            # add the intersection drugbank to the alternative dictionary
            if len(intersection) > 1:
                dict_drugbank_to_alternatives[drugbank_id] = intersection
                intersection_string = ''
                for db in intersection:
                    intersection_string += db + ' '
                file_combined_drugbanks.write(intersection_string[0:-1] + '\n')
                print(intersection)
                # sys.exit('intersection')
            elif intersection[0] != drugbank_id:
                dict_drugbank_to_alternatives[drugbank_id] = intersection
                print(drugbank_id)
                print(intersection)


            for drug_id in intersection:
                resource = dict_compounds_in_hetionet[drug_id]['resource']
                # print(dict_compounds_in_hetionet[drug_id])
                # print(resource)
                resource.append('DrugBank')

                resource = list(set(resource))
                resource = "','".join(resource)
                query = ''' Match (n:Compound{identifier:"%s"}), (b:''' + neo4j_label_drugbank + '''{identifier:"%s"}) 
                Set  n.drugbank="yes",'''
                query = query % (drug_id, drugbank_id)
                for key, property in information.items():
                    # to merge the information into one both information must be combinate
                    if key in list_merge_xrefs:
                        list_merge_xref_values=list_merge_xref_values.union(property)
                        continue

                    part = ''
                    if type(property) == list:
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
                        property = [x.replace('"', "'").replace('\\', '\\\\') for x in property]
                        list_string = '","'.join(property)
                        part = ''' n.%s=["%s"],'''
                        part = part % (key, list_string)
                    else:
                        if key == 'identifier':
                            continue
                        if key in dict_compounds_in_hetionet[drug_id]:
                            if dict_compounds_in_hetionet[drug_id][key] != property:
                                if key == 'license':
                                    property = dict_compounds_in_hetionet[drug_id][key]
                                # the new values are good !!!!!!
                                # elif dict_compounds_in_hetionet[drug_id][key]=='' or  property=='':
                                #     print('one is empty thw ne values are good')
                                # most time the new values are the better fitting values
                                elif key == 'unii':
                                    # only this three the older fits better
                                    if drug_id in ['DB11200', 'DB10360', 'DB09561']:
                                        property = dict_compounds_in_hetionet[drug_id][key]
                                    # writer_uniis.writerow(
                                    #     [drugbank_id, key, dict_compounds_in_hetionet[drug_id][key], property])
                                # the new names fit better or has greek letter format
                                # elif key=='name':
                                #     writer_names.writerow(
                                #         [drugbank_id, key, dict_compounds_in_hetionet[drug_id][key], property])
                                # the new values are better so only take the new once
                                # elif key=='inchikey':
                                #     writer_inchikeys.writerow(
                                #         [drugbank_id, key, dict_compounds_in_hetionet[drug_id][key], property])
                                # the new are better or the same !!!
                                # elif key=='inchi':
                                #     writer_inchis.writerow(
                                #         [drugbank_id, key, dict_compounds_in_hetionet[drug_id][key], property])
                                # the new types are better fitting
                                # elif key == 'type':
                                #     writer_types.writerow(
                                #         [drugbank_id, key, dict_compounds_in_hetionet[drug_id][key], property])
                                # the new values fit better then the old values
                                # elif key == 'cas_number':
                                #     writer_casnumbers.writerow(
                                #         [drugbank_id, key, dict_compounds_in_hetionet[drug_id][key], property])
                                # else:
                                #     print(drugbank_id)
                                #     print(dict_compounds_in_hetionet[drug_id][key])
                                #     print(property)
                                #     print(key)
                                #     sys.exit('not the same')
                        elif key not in list_new_properties and not key in old_properties:
                            list_not_fiting_properties.add(key)
                            # sys.exit(key)
                        # if '\\' in property:
                        #     property=property.replace('\"','\\"')
                        #     print(property)
                        property = property.replace('"', "'").replace('\\', '\\\\')
                        part = ''' n.%s="%s",'''
                        part = part % (key, property)
                    query += part
                combinde_merge_string='","'.join(list_merge_xref_values)
                query += ''' n.xrefs=["%s"] ''' %(combinde_merge_string)
                query +=  ''' Create (n)-[:equal_to_drugbank]->(b);\n'''
                file_all_node_cypher.write(query.encode('utf-8'))
                counter_all_nodes+=1
                if counter_all_nodes%maximal_commits==0 and counter_all_nodes%maximal_commits_file==0:
                    file_all_node_cypher.write('commit')
                    file_all_node_cypher = open(start_node + str(file_counter) + '.cypher', 'w')
                    file_counter += 1
                    file_all_node_cypher.write('begin\n')
                elif counter_all_nodes%maximal_commits==0 :

                    print(counter_all_nodes)
                    file_all_node_cypher.write('commit\nbegin\n')
                # g.run(query)
        else:
            # create a new node
            counter_new_compound += 1
            query = '''Match  (b:''' + neo4j_label_drugbank + '''{identifier:"%s"})
                                                Create (n:Compound{identifier:"%s", resource:['DrugBank'], source:"DrugBank", license:"CC BY-NC 4.0", ctd:'no', aeolus:'no', ndf_rt:'no', hetionet:'no', drugbank:'yes', sider:'no', '''

            query = query % (drugbank_id, drugbank_id)
            for key, property in information.items():
                # to merge the information into one both information must be combinate
                if key in list_merge_xrefs:
                    list_merge_xref_values = list_merge_xref_values.union(property)
                    continue
                if type(property) == list:
                    if key == 'alternative_ids':
                        property = list(set(property))

                    property = [x.replace('"', "'").replace('\\', '\\\\') for x in property]
                    list_string = '","'.join(property)
                    part = ''' %s:["%s"],'''
                    part = part % (key, list_string)
                else:
                    if key == 'identifier':
                        continue
                    part = ''' %s:"%s",'''
                    property = property.replace('"', "'").replace('\\', '\\\\')
                    part = part % (key, property)
                query += part

            combinded_merge_string = '","'.join(list_merge_xref_values)
            query += ''' n.xrefs=["%s"] ''' % (combinded_merge_string)

            query +=  '''})  Create (n)-[:equal_to_drugbank]->(b);\n'''
            file_all_node_cypher.write(query.encode('utf-8'))
            counter_all_nodes += 1
            if counter_all_nodes % maximal_commits == 0 and counter_all_nodes % maximal_commits_file == 0:
                file_all_node_cypher.write('commit')
                file_all_node_cypher = open(start_node+str(file_counter) + '.cypher', 'w')
                file_counter += 1
                file_all_node_cypher.write('begin\n')
            elif counter_all_nodes % maximal_commits == 0:

                print(counter_all_nodes)
                file_all_node_cypher.write('commit\nbegin\n')
            # g.run(query)

    print(list_set_key_with_values_length_1)
    print('already existing compound:' + str(counter_already_existing_compound))
    print('new compound:' + str(counter_new_compound))

    # so that the last queries are also execute
    file_all_node_cypher.write('commit')
    file_all_node_cypher.close()

    if len(list_not_fiting_properties) > 0:
        print(list_not_fiting_properties)
        sys.exit('not fitting')


'''
Generate the the interaction file and the cypher file to integrate the information from the csv into neo4j
'''


def genration_of_interaction_file():
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

    create_connetion_with_neo4j()

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

    print('generate cypher file for interaction')

    genration_of_interaction_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
