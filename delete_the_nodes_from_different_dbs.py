# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 12:30:00 2017

@author: Cassandra
"""

'''
create connection to neo4j 
'''
from py2neo import Graph, authenticate
import datetime


def create_connection_with_neo4j():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


'''
first delete the different do relationships and then the nodes
'''


def delete_do_from_neo4j():
    print('relationship equal_to')
    # delete connection to the hetionet diseases
    query = 'MATCH p=()-[r:equal_to]->() Delete r'
    g.run(query)

    print('relationship is_a')
    # delete is_a relationship between do diseases
    query = 'MATCH p=()-[r:is_a]->() Delete r'
    g.run(query)

    print('node')
    # delete the nodes of do
    query = 'MATCH (n:DiseaseOntology) Detach Delete n'
    g.run(query)


'''
delete the ndf-rt information from neo4j. First delete the relationships and then the nodes.
'''


def delete_ndf_rt_from_neo4j():
    print('relationship equal_to_Disease_NDF_RT')
    # delete connection to the hetionet diseases
    query = 'MATCH p=()-[r:equal_to_Disease_NDF_RT]->() Delete r'
    g.run(query)

    print('relationship equal_to_drug_ndf_rt')
    # delete connection to the hetionet compounds
    query = 'MATCH p=()-[r:equal_to_drug_ndf_rt]->() Delete r'
    g.run(query)

    print('relationship ContraIndicates')
    # delete is_a relationship contraindicates
    query = 'MATCH p=()-[r:ContraIndicates]->() Delete r'
    g.run(query)

    print('relationship Induces')
    # delete is_a relationship induces
    query = 'MATCH p = () - [r:Induces]->() Delete r'
    g.run(query)

    print('disease node')
    # delete the disease nodes of ndf-rt
    query = 'MATCH (n:NDF_RT_disease) Delete n'
    g.run(query)

    print('drug nodes')
    # delete the drug nodes of ndf-rt
    query = 'MATCH (n:NDF_RT_drug) Delete n'
    g.run(query)


'''
Delete SIDER from neo4j. First the relationships and then the nodes
'''


def delete_sider_from_neo4j():
    print( 'relationship equal_to_SE')
    # delete connection to the hetionet side effects
    query = 'MATCH p=()-[r:equal_to_SE]->() Delete r'
    g.run(query)

    print('relationship equal_to_drug_Sider')
    # delete connection to the hetionet compounds
    query = 'MATCH p=()-[r:equal_to_drug_Sider]->() Delete r'
    g.run(query)

    print('relationship Causes')
    # delete is_a relationship causes
    query = 'MATCH p=(:drugSider)-[r:Causes]->() Delete r'
    g.run(query)

    print( 'side effect nodes')
    # delete the side effect nodes of sider
    query = 'MATCH (n:seSider) Delete n'
    g.run(query)

    print('drug nodes')
    # delete the drug nodes of sider
    query = 'MATCH (n:drugSider) Delete n'
    g.run(query)


# delete maximal number of relationships
maximal_number_of_relationships_for_deletion = 100000

'''
Delete CTD from neo4j. First the relationships and then the nodes.
'''


def delete_ctd_from_neo4j():
    print('relationship equal_to_D_Disease_CTD')
    # delete connection to the hetionet diseases
    query = 'MATCH p=()-[r:equal_to_D_Disease_CTD]->() Delete r'
    g.run(query)

    print('relationship equal_chemichal_CTD')
    # delete connection to the hetionet compounds
    query = 'MATCH p=()-[r:equal_chemichal_CTD]->() Delete r'
    g.run(query)

    print('relationship equal_to_SE_Disease_CTD')
    # delete connection from ctd disease to the hetionet side effect
    query = 'MATCH p=()-[r:equal_to_SE_Disease_CTD]->() Delete r'
    g.run(query)

    print('relationship equal_to_SE_CTD')
    # delete connection from phenotype to the hetionet side effects
    query = 'MATCH p=()-[r:equal_to_SE_CTD]->() Delete r'
    g.run(query)

    print('relationship Causes')
    # delete is_a relationship causes
    query = 'MATCH p=(:CTDchemical)-[r:Causes]->() Delete r'
    g.run(query)

    print('relationship Association')
    # delete is_a relationship association
    query = 'MATCH p=()-[r:Association]->() Return count(r)'
    results = g.run(query)
    number_of_association = results.evaluate()
    how_often_delete = number_of_association / maximal_number_of_relationships_for_deletion + 1
    for i in range(0, how_often_delete):
        query = 'MATCH p=()-[r:Association]->() With r Limit %s Delete r'
        query = query % (str(maximal_number_of_relationships_for_deletion))
        g.run(query)

    print('disease nodes')
    # delete the disease nodes of ctd
    query = 'MATCH (n:CTDdisease) Delete n'
    g.run(query)

    print('chemical nodes')
    # delete the drug nodes of ctd
    query = 'MATCH (n:CTDchemical) Delete n'
    g.run(query)

    print('phenotype nodes')
    # delete the phenotype nodes of ctd
    query = 'MATCH (n:CTDphenotype) Delete n'
    g.run(query)

'''
Delete AEOLUS from neo4j. First the relationships and then the nodes
'''


def delete_aeolus_from_neo4j():
    print( 'relationship equal_to_Aeolus_SE')
    # delete connection to the hetionet side effects
    query = 'MATCH p=()-[r:equal_to_Aeolus_SE]->() Delete r'
    g.run(query)

    print('relationship equal_to_Aeolus_drug')
    # delete connection to the hetionet compounds
    query = 'MATCH p=()-[r:equal_to_Aeolus_drug]->() Delete r'
    g.run(query)

    print('relationship Causes')
    # delete is_a relationship causes
    query = 'MATCH p=(:AeolusDrug)-[r:Causes]->() Return count(r)'
    results = g.run(query)
    number_of_association = results.evaluate()
    how_often_delete = number_of_association / maximal_number_of_relationships_for_deletion + 1
    for i in range(0, how_often_delete):
        query = 'MATCH p=(:AeolusDrug)-[r:Causes]->() With r Limit %s Delete r'
        query = query % (str(maximal_number_of_relationships_for_deletion))
        g.run(query)

    print( 'outcome nodes')
    # delete the outcome nodes of aeolus
    query = 'MATCH (n:AeolusOutcome) Delete n'
    g.run(query)

    print('drug nodes')
    # delete the drug nodes of aeolus
    query = 'MATCH (n:AeolusDrug) Delete n'
    g.run(query)


def main():
    print (datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('delete disease ontology nodes and connections')

    delete_do_from_neo4j()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('delete ndf-rt nodes and connections')

    delete_ndf_rt_from_neo4j()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('delete sider nodes and connections')

    delete_sider_from_neo4j()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('delete ctd nodes and connections')

    delete_ctd_from_neo4j()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('delete ctd nodes and connections')

    delete_aeolus_from_neo4j()

    print('#############################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
