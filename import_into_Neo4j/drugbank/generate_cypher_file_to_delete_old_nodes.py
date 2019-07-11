# -*- coding: utf-8 -*-
import datetime, sys
from py2neo import Graph, authenticate


'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# if to many node of a label exists then only 10000 nodes should be delete at once
number_of_node_or_rela_to_delete=10000

#cypher file to delete nodes
cypher_file=open('delete_nodes.cypher','w')

# list of all nodes which should be deleted
list_of_labels_to_delete=['Protein_DrugBank','Metabolite_DrugBank','Mutated_enzyme_gene_DrugBank','Pathway_DrugBank','PharmacologicClass_DrugBank','Product_DrugBank','Salt_DrugBank','Compound_DrugBank']

'''
as input it get the relationship type, 
then it check which kind of nodes are in this relationship
next check out how many relationships of this type exists
then add the delete queries to the cypher file 
'''
def add_delete_query_rela(rela_type):
    #get the nodes label
    query = '''Match (a)-[r:%s]->(b) RETURN Distinct labels(a), labels(b)''' % (rela_type)
    results = g.run(query)
    first_label=''
    second_label=''
    for label_list_1, label_list_2, in results:
        for label in label_list_1:
            if label in list_of_labels_to_delete:
                first_label=label
        for label in label_list_2:
            if label in list_of_labels_to_delete:
                second_label = label

    query = '''Match (:%s)-[r:%s]->(:%s) Return count(r)''' % (first_label,rela_type,second_label)
    results = g.run(query)
    counter = results.evaluate()
    query = '''MATCH (:%s)-[r:%s]->(:%s) With r Limit %s Delete r; \n''' % (first_label,rela_type,second_label,str(number_of_node_or_rela_to_delete))
    for i in range(0, counter / number_of_node_or_rela_to_delete + 1):
        # cypher_file.write('begin\n')
        cypher_file.write(query)
        # cypher_file.write('commit\n')


'''
first check number of nodes in neo4j and depending on the number one or more cypher queries to delete this nodes are add 
to the cypher file 
'''
def add_delete_query(label):
    query='''Match (n:%s) Return count(n)''' %(label)
    results=g.run(query)
    counter=results.evaluate()
    query='''MATCH (n:%s) With n Limit %s Detach Delete n;\n''' %(label,str(number_of_node_or_rela_to_delete))
    for i in range(0,counter/number_of_node_or_rela_to_delete+1):
        # cypher_file.write('begin\n')
        cypher_file.write(query)
        # cypher_file.write('commit\n')





def main():
    print (datetime.datetime.utcnow())
    print('create connection to neo4j')

    create_connection_with_neo4j()
    print(sys.argv)
    if len(sys.argv)>1:
        list_of_labels_to_delete=sys.argv[1].split(',')
        if len(sys.argv)>2:
            rela_list = sys.argv[2].split(',')
    else:
        sys.exit('this needs at least as first parameter a list of node labes which should be seperated by a comma, possible is to hand in a list of relationships')

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('remove queries for relationships')

    for rela in rela_list:
        add_delete_query_rela(rela)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('delete detach multiple labels')

    for label in list_of_labels_to_delete:
        add_delete_query(label)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
