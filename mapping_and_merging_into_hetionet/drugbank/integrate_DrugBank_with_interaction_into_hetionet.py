# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 16:07:43 2018

@author: ckoenig
"""

'''integrate the other diseases and relationships from disease ontology in hetionet'''
from py2neo import Graph, authenticate
import datetime
import sys

# reload(sys)
# sys.setdefaultencoding("utf-8")

# sys.path.append('../Aeolus/')
sys.path.append('../aeolus/')

# from synonyms_cuis import search_for_synonyms_cuis
import get_drugbank_information

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
        dict_compounds_in_hetionet[compound['identifier']] = compound['resource']
    print('size of compound in Hetionet before the rest of DrugBank is added: ' + str(len(list_compounds_in_hetionet)))


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
'''


def load_all_DrugBank_compound_in_dictionary():
    query = '''Match (n:DrugBankdrug) RETURN n '''
    results = g.run(query)
    for compound, in results:
        food_interaction = compound['food_interaction']
        inchikey = compound['inchikey']
        inchi = compound['inchi']
        name = compound['name']
        alternative_ids = compound['alternative_ids']
        id = compound['id']
        url = compound['url']
        dict_compounds[id] = [url, name, inchi, inchikey, food_interaction, alternative_ids]
    print('size of drugbank: ' + str(len(dict_compounds)))


# dictionary with (durg1, drug2) and url, description
dict_interact_relationships_with_infos = {}

'''
load all the is_a relationships from MonDO into a dictionary with the resource
'''


def load_in_all_connection_from_mondo_in_dict():
    query = '''MATCH p=(a)-[r:interacts]->(b) RETURN a.id,r.url, r.describtion ,b.id  '''
    results = g.run(query)
    for compound1_id, url, description, compound2_id, in results:
        dict_interact_relationships_with_infos[(compound1_id, compound2_id)] = [url, description]

    print('number of interaction:' + str(len(dict_interact_relationships_with_infos)))


# dictionary of drugbank id and to the used ids in Hetionet
dict_drugbank_to_alternatives = {}

'''
Integrate all DrugBank id into Hetionet and generate Cypher file for interaction of DrugBank IDs into Hetionet
'''


def integrate_DB_information_into_hetionet():
    # prepare the search if a drugbank has no further information
    get_drugbank_information.load_all_drugbank_ids_in_dictionary()
    # file counter
    file_counter = 1
    # maximal number of queries for a commit block
    constrain_number = 20000
    # maximal number of queries in a file
    creation_max_in_file = 1000000

    # integrate or add Hetionet compounds
    for drugbank_id, information in dict_compounds.items():
        food_interaction = information[4]
        inchikey = information[3]
        inchi = information[2]
        name = information[1]
        alternative_ids = information[5].split('|')
        url = information[0]
        # alternative ids
        alternative_ids.append(drugbank_id)
        intersection = list(set(alternative_ids).intersection(list_compounds_in_hetionet))
        if len(intersection) > 0:
            dict_drugbank_to_alternatives[drugbank_id]=intersection
            for drug_id in intersection:
                resource = dict_compounds_in_hetionet[drug_id]
                # print(dict_compounds_in_hetionet[drug_id])
                # print(resource)
                resource.append('DrugBank')

                resource = list(set(resource))
                resource = "','".join(resource)
                query = ''' Match (n:Compound{identifier:"%s"}), (b:DrugBankdrug{id:"%s"})
                 Set n.food_interaction="%s" , n.resource=['%s'], n.drugbank="yes", n.alternative_drugbank_ids="%s"
                 Create (n)-[:equal_to_drugbank]->(b);'''
                query = query % (drug_id, drugbank_id, food_interaction, resource, information[5])
                g.run(query)
        else:
            # create a new node

            [name2, inchi2, inchikey2] = get_drugbank_information.get_drugbank_information(drugbank_id)
            if name2 == '':
                query = '''Match  (b:DrugBankdrug{id:"%s"})
                                                Create (n:Compound{identifier:"%s", inchikey:"%s",  inchi:"%s", resource:['DrugBank'], source:"DrugBank", url:"%s",  name:"%s", food_interaction:"%s", alternative_drugbank_ids:"%s",license:"CC BY-NC 4.0", ctd:'no', aeolus:'no', ndf_rt:'no', hetionet:'no', drugbank:'yes', sider:'no', no_further_chemical_information:'yes'})
                                                Create (n)-[:equal_to_drugbank]->(b);'''
            else:
                query = '''Match  (b:DrugBankdrug{id:"%s"})
                                Create (n:Compound{identifier:"%s", inchikey:"%s", inchi:"%s", resource:['DrugBank'], source:"DrugBank", url:"%s", name:"%s", food_interaction:"%s", alternative_drugbank_ids:"%s",  license:"CC BY-NC 4.0", ctd:'no', aeolus:'no', ndf_rt:'no', hetionet:'no', drugbank:'yes', sider:'no'})
                                Create (n)-[:equal_to_drugbank]->(b);'''

            query = query % (drugbank_id, drugbank_id, inchikey, inchi, url, name, food_interaction, information[5])
            g.run(query)

    # generate cypher file for interaction
    counter_connection = 0

    h = open('map_connection_of_drugbank_in_hetionet_' + str(file_counter) + '.cypher', 'w')
    file_counter += 1

    for (compound1, compound2), [url, description] in dict_interact_relationships_with_infos.items():
        if not compound2 in dict_drugbank_to_alternatives and not compound1 in dict_drugbank_to_alternatives:
            query = ''' Match (c1:Compound{identifier:"%s"}), (c2:Compound{identifier:"%s"})
                        Create (c1)-[:INTERACTS_CiC{source:"DrugBank", unbiased:'false', resource:['DrugBank'], url:"%s", license:'CC BY-NC 4.0', description:"%s"}]->(c2); \n'''
            query = query % (compound1, compound2, url, description)
            counter_connection += 1
            h.write(query)
            if counter_connection % constrain_number == 0:
                h.write('commit \n')
                if counter_connection % creation_max_in_file == 0:
                    h.close()
                    h = open('map_connection_of_drugbank_in_hetionet_' + str(file_counter) + '.cypher', 'w')
                    h.write('begin \n')
                    file_counter += 1
                else:
                    h.write('begin \n')
        elif compound2 in dict_drugbank_to_alternatives:
            if compound1 in dict_drugbank_to_alternatives:
                for drug2 in  dict_drugbank_to_alternatives[compound2]:
                    for drug1 in dict_drugbank_to_alternatives[compound1]:
                        query = ''' Match (c1:Compound{identifier:"%s"}), (c2:Compound{identifier:"%s"})
                                Create (c1)-[:INTERACTS_CiC{source:"DrugBank", unbiased:'false', resource:['DrugBank'], url:"%s", license:'CC BY-NC 4.0', description:"%s"}]->(c2); \n'''
                        query = query % (drug1, drug2, url, description)
                        counter_connection += 1
                        h.write(query)
                        if counter_connection % constrain_number == 0:
                            h.write('commit \n')
                            if counter_connection % creation_max_in_file == 0:
                                h.close()
                                h = open('map_connection_of_drugbank_in_hetionet_' + str(file_counter) + '.cypher', 'w')
                                h.write('begin \n')
                                file_counter += 1
                            else:
                                h.write('begin \n')

            else:
                for drug2 in  dict_drugbank_to_alternatives[compound2]:
                    query = ''' Match (c1:Compound{identifier:"%s"}), (c2:Compound{identifier:"%s"})
                            Create (c1)-[:INTERACTS_CiC{source:"DrugBank", unbiased:'false', resource:['DrugBank'], url:"%s", license:'CC BY-NC 4.0', description:"%s"}]->(c2); \n'''
                    query = query % (compound1, drug2, url, description)
                    counter_connection += 1
                    h.write(query)
                    if counter_connection % constrain_number == 0:
                        h.write('commit \n')
                        if counter_connection % creation_max_in_file == 0:
                            h.close()
                            h = open('map_connection_of_drugbank_in_hetionet_' + str(file_counter) + '.cypher', 'w')
                            h.write('begin \n')
                            file_counter += 1
                        else:
                            h.write('begin \n')
        else:
            for drug1 in dict_drugbank_to_alternatives[compound1]:
                query = ''' Match (c1:Compound{identifier:"%s"}), (c2:Compound{identifier:"%s"})
                        Create (c1)-[:INTERACTS_CiC{source:"DrugBank", unbiased:'false', resource:['DrugBank'], url:"%s", license:'CC BY-NC 4.0', description:"%s"}]->(c2); \n'''
                query = query % (drug1, drug2, url, description)
                counter_connection += 1
                h.write(query)
                if counter_connection % constrain_number == 0:
                    h.write('commit \n')
                    if counter_connection % creation_max_in_file == 0:
                        h.close()
                        h = open('map_connection_of_drugbank_in_hetionet_' + str(file_counter) + '.cypher', 'w')
                        h.write('begin \n')
                        file_counter += 1
                    else:
                        h.write('begin \n')

    h.write('commit')
    h.close()


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

    load_in_all_connection_from_mondo_in_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('integrate disease ontology into hetionet')

    integrate_DB_information_into_hetionet()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
