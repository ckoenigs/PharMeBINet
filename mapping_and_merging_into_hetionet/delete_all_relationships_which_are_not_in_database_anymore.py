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
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

    # authenticate("bimi:7475", "ckoenigs", "test")
    # global g
    # g = Graph("http://bimi:7475/db/data/",bolt=False)

'''
find all nodes with the source but no equal relationship and change this and delet all relationships which are from this 
source and only from this source 
'''

def delete_rela(label, source):

    csv_file = open('delete_node_relationships.csv', 'w')
    csv_file.write('nodes_with_source_but_not_up_today\n')
    relas=dict_source_rela_list[source]
    query='''Match (n:'''+label+''') Where n.'''+source+'''='yes' '''
    for rela in relas:
        query+= '''and not (n)-[:'''+rela+''']-() '''
    query += '''Return n.identifier'''
    result=g.run(query)
    counter_old_nodes=0
    for identifier, in result:
        print(identifier)
        counter_old_nodes+=1
        csv_file.write(identifier + '\n')

    print('number nodes which contains old information:'+str(counter_old_nodes))

    cypher=open('cypher.cypher','w')
    query='''Using Periodic Commit 1000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/delete_node_relationships.csv" As line Match (n:'''+label+'''{identifier:line.nodes_with_source_but_not_up_today})-[r]-() Where r.'''+source+'''='yes' and size(r.resource)=1 Set n.'''+source+'''='no' Delete r  ;\n '''
    cypher.write(query)

    query='''Using Periodic Commit 1000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/delete_node_relationships.csv" As line Match (n:'''+label+'''{identifier:line.nodes_with_source_but_not_up_today})-[r]-() Where r.'''+source+'''='yes' and size(r.resource)>1 Set r.resource= FILTER(x in r.resource Where lower(x) <> "'''+ source+'''") With n Where size(n.resource)=1 and not n.hetionet='yes' Set n.'''+source+ '''='no', n.resource= FILTER(x in n.resource Where lower(x) <> "'''+ source+'''") ;\n'''
    cypher.write(query)
    query='''Match  (n:'''+label+''') Where size(n.resource)=0 Delete n ;\n'''
    cypher.write(query)



#dictionary with all sources and the relase
dict_source_rela_list={}


def main():
    file_with_all_rela_for_database=open('equal_list.csv','r')
    reader = csv.DictReader(file_with_all_rela_for_database)
    for line in reader:
        database= line['database']
        rela= line['equal_rela_name']
        if database not in dict_source_rela_list:
            dict_source_rela_list[database]=[rela]
        else:
            dict_source_rela_list[database].append(rela)

    if len(sys.argv)!= 3:
        print('need to arguments the first should be the label and the second the database')
        print('possible databases')
        print(dict_source_rela_list.keys())
        sys.exit()

    label= sys.argv[1]
    database=sys.argv[2]
    if database not in dict_source_rela_list:
        print('database is not in hetionet')
        print('possible databases')
        print(dict_source_rela_list.keys())


    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    delete_rela(label, database)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
