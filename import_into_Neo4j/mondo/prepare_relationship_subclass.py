# -*- coding: utf-8 -*-
"""
Created on Fri Feb 2 07:23:43 2018
@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import sys, csv

reload(sys)
sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

#csv files where subclass relationships need to be combined
file=open('subclass_rela.csv','w')
csv_writer=csv.writer(file,delimiter='\t')
header=['disease_id_1','disease_id_2','lbl','isDefinedBy','equivalentOriginalNodeSourceTarget']
csv_writer.writerow(header)

# cypher file to delete double subclass rela and update rela
cypher=open('cypher_rela.cypher','w')

# queries for deletion and create combined relationship
query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/mondo/subclass_rela.csv" As line FIELDTERMINATOR '\\t' Match (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.disease_id_1})-[r:subClassOf]->(b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.disease_id_2}) Delete r;\n '''
cypher.write(query)
query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/mondo/subclass_rela.csv" As line FIELDTERMINATOR '\\t' Match (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.disease_id_1}), (b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.disease_id_2}) Create (a)-[:subClassOf{lbl:line.lbl, isDefinedBy:line.isDefinedBy, equivalentOriginalNodeSourceTarget:split(line.equivalentOriginalNodeSourceTarget,'|')  }]->(b)  ;\n '''
cypher.write(query)
cypher.close()

'''
First prepare mondo-disease, because some has multiple subClassOf from the different  source and this information are 
combined in one relationship
'''


def prepare_subClassOf_relationships():
    # get all nodes with multiple subClassOf relationship
    query = '''Match p=(a:disease)-[r:subClassOf]->(b:disease) With a,b,type(r) as t, count(r) as coun Where coun >1 Return a.`http://www.geneontology.org/formats/oboInOwl#id` ,b.`http://www.geneontology.org/formats/oboInOwl#id` '''
    result = g.run(query)

    #count the pairs of multiple subClass relationships
    counter_pairs_with_multiple_sub_class_rela=0
    for mondo_id_a, mondo_id_b, in result:
        counter_pairs_with_multiple_sub_class_rela+=1
        query = '''Match p=(a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[r:subClassOf]->(b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:'%s'})  Return r '''
        query= query %(mondo_id_a,mondo_id_b)
        defined = 'http://purl.obolibrary.org/obo/upheno/monarch.owl'
        result = g.run(query)

        dict_orginal_source_target = []

        number_rela=0
        for rela, in result:
            number_rela+=1
            original_source = rela['equivalentOriginalNodeSource'] if 'equivalentOriginalNodeSource' in rela else ''
            original_target = rela['equivalentOriginalNodeTarget'] if 'equivalentOriginalNodeTarget' in rela else ''
            combined = '(' + original_source + ',' + original_target + ')'
            dict_orginal_source_target.append(combined)
            if rela['isDefinedBy'] != defined:
                print(rela['isDefinedBy'])
                break

        original_source_target='|'.join(dict_orginal_source_target)
        csv_writer.writerow([mondo_id_a, mondo_id_b, rela['lbl'], rela['isDefinedBy'], original_source_target])
        if counter_pairs_with_multiple_sub_class_rela % 1000==0:
            print(counter_pairs_with_multiple_sub_class_rela)
            print(datetime.datetime.utcnow())
    print('total number of pairs with multiple connection:'+str(counter_pairs_with_multiple_sub_class_rela))



def main():
    print(datetime.datetime.utcnow())
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('prepare subClassOf relationships')

    prepare_subClassOf_relationships()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()