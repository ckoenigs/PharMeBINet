import csv, sys
sys.path.append("../..")
import create_connection_to_databases, authenticate

authenticate("localhost:7474", "neo4j", "test")
global g
g = Graph("http://localhost:7474/db/data/")

# csvfile = open('../drugbank_interaction.tsv', 'r')
# spamreader = csv.DictReader(csvfile, delimiter='\t')
# counter=0
# dict_search={}
# dict_found=ids={}
# dict_not_found_ids={}
# for row in spamreader:
#     id1 = row['DB_ID1']
#     id2 = row['DB_ID2']
#     if not id2 in dict_search:
#         query='''MATCH (n:Compound_DrugBank) Where n.identifier='%s' or '%s' in n.alternative_drugbank_ids RETURN n.identifier''' %(id2,id2)
#         results=g.run(query)
#         result=results.evaluate()
#         if not result:
#             print(id1,id2)
#             counter+=1
#             dict_not_found_ids[id2]=1
#         else:
#             dict_found[id2]=1
#         dict_search[id2]=1
#     else:
#         if id2 in dict_not_found_ids:
#             print(id1, id2)
#             counter+=1
#
# print('not existing db interaction:'+str(counter))

csvfile = open('../drugbank_pathway_enzymes.tsv', 'r')
spamreader = csv.DictReader(csvfile, delimiter='\t')
counter=0
dict_search={}
dict_found=ids={}
dict_not_found_ids={}
for row in spamreader:
    id1 = row['pathway_id']
    id2 = row['uniprot_id']
    if not id2 in dict_search:
        query='''MATCH (n:Protein_DrugBank) Where n.identifier='%s'  RETURN n.identifier''' %(id2)
        results=g.run(query)
        result=results.evaluate()
        if not result:
            print(id1,id2)
            counter+=1
            dict_not_found_ids[id2]=1
        else:
            dict_found[id2]=1
        dict_search[id2]=1
    else:
        if id2 in dict_not_found_ids:
            print(id1, id2)
            counter+=1

print('not existing db interaction:'+str(counter))