import csv, sys
sys.path.append("../..")
import create_connection_to_databases, authenticate

authenticate("localhost:7474", "neo4j", "test")
global g
g = Graph("http://localhost:7474/db/data/")


csvfile = open('drugbank_Enzyme_DrugBank.tsv', 'r')
spamreader = csv.reader(csvfile, delimiter='\t')
counter=0
# for row in spamreader:
#     if counter==0:
#         counter+=1
#         continue
#     uniprot_id = row[2]
#     query='''MATCH (n:Enzyme_DrugBank{identifier:'%s'}) RETURN n.identifier''' %(uniprot_id)
#     results=g.run(query)
#     result=results.evaluate()
#     if not result:
#         print(uniprot_id)
#
#     counter+=1
#
# print(counter)

csvfile = open('drugbank_reaction_compound_compound.tsv', 'r')
spamreader = csv.DictReader(csvfile, delimiter='\t')
counter=0
dict_search={}
dict_found=ids={}
dict_not_found_ids={}
for row in spamreader:
    id1 = row['left_element_drugbank_id']
    id2 = row['right_element_drugbank_id']
    if not id2 in dict_search:
        query = '''MATCH (n:Compound_DrugBank) Where n.identifier='%s' or '%s' in n.alternative_drugbank_ids RETURN n.identifier''' % (
        id2, id2)
        results = g.run(query)
        result = results.evaluate()
        if not result:
            print(id1, id2)
            counter += 1
            dict_not_found_ids[id2] = 1
            print('rigth')
            continue
        else:
            dict_found[id2] = 1
        dict_search[id2] = 1
    else:
        if id2 in dict_not_found_ids:
            print(id1, id2)
            counter += 1
            print('rigth')
            continue

    if not id1 in dict_search:
        query = '''MATCH (n:Compound_DrugBank) Where n.identifier='%s' or '%s' in n.alternative_drugbank_ids RETURN n.identifier''' % (
        id1, id1)
        results = g.run(query)
        result = results.evaluate()
        if not result:
            print(id1, id1)
            counter += 1
            dict_not_found_ids[id1] = 1
        else:
            dict_found[id1] = 1
        dict_search[id1] = 1
    else:
        if id1 in dict_not_found_ids:
            print(id1, id1)
            counter += 1

print('not existing db interaction:' + str(counter))