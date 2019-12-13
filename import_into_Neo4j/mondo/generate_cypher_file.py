# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 09:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph#, authenticate
import sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

# connect with the neo4j database
def database_connection():

    # authenticate("localhost:7474", )
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))

'''
Generate cypher file with APOC
'''
def generate_cypher_file_with_apoc():
    # generate cypher file for the most of the mondo nodes with their relationships
    #file:/
    query = '''call apoc.export.cypher.query("MATCH (n:disease)-[r]->(b:disease)  RETURN n,r,b","/home/cassandra/Documents/Project/master_database_change/import_into_Neo4j/mondo/mondo.cypher", {batchSize:10000, format:'cypher-shell'}); '''
    #this is query for cypher shell, but this do not work realy for neo4j 3.2.9
    # query='''call apoc.export.cypher.query("MATCH (n:disease)-[r]->(b:disease) Where n.`http://www.geneontology.org/formats/oboInOwl#id` contains 'MONDO' and b.`http://www.geneontology.org/formats/oboInOwl#id` contains 'MONDO' RETURN n,r,b","'''+save_path+'''mondo.cypher", {batchSize:10000,format:'cypher-shell'}); '''
    g.run(query)

    # the only nod that has no connection to another disease node with a mondo id (MONDO:0013239)
    # query= '''call apoc.export.cypher.query("MATCH (n:disease) Where n.`http://www.geneontology.org/formats/oboInOwl#id`='MONDO:0013239' Return n","/home/cassandra/Documents/Project/master_database_change/import_into_Neo4j/mondo/single_node_without_connection.cypher", {batchSize:10, format:'cypher-shell'} ); '''
    # g.run(query)

    cypher_file_remove_nodes=open('remove_nodes_without_mondo.cypher','w')
    query='''MATCH (b:disease) Where not b.`http://www.geneontology.org/formats/oboInOwl#id` contains 'MONDO' Detach Delete b;'''
    cypher_file_remove_nodes.write(query)
    cypher_file_remove_nodes.close()


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate cypher file')

    # if len(sys.argv)==2:
    generate_cypher_file_with_apoc()
    # else:
    #     print('Need a path as argument to save the cypher file, the pathe and the file name.')
    #     print(len(sys.argv))

    print('##########################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()