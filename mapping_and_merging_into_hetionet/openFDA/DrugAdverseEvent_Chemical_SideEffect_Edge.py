import datetime
import csv
import json, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
from mapping import *

if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path openFDA')

print(datetime.datetime.now())
print("Connecting to database neo4j ...")
global g, driver
driver = create_connection_to_databases.database_connection_neo4j_driver()
g = driver.session(database='graph')

print(datetime.datetime.now())
print("Fetching data ...")

# create file with header
f = open("FDA_edges/DrugAdverseEvent_Chemical_SideEffect_Edge.tsv", 'w', encoding="utf-8", newline='')
writer = csv.writer(f, delimiter="\t")
writer.writerow(["chemical", "sideeffect", "nodes", "count"])

# Limit for query
LIMIT = 10000
count = 0

a = [1]
# Chemical - DrugAdverseEvent_drug_openfda - DrugAdverseEvent_drug - DrugAdverseEvent - DrugAdverseEvent_reaction - SideEffect
# get Chemical-SE pairs and count the number of path and remember maximal 100 DrugAdverseEvent_openFDA in the edge
while len(a) > 0:
    query = f'MATCH z=(c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)-[e3:Event]->(p:DrugAdverseEvent_openFDA)<-[e4:Event]-(r:DrugAdverseEvent_reaction_openFDA)<-[e5:name_merge]-(s:SideEffect) WITH c,collect(p) as hu,s SKIP {str(count)} LIMIT {LIMIT} RETURN c.identifier, s.identifier, hu'
    a = list(g.run(query))
    print("Query return length: " + str(len(a)))
    for entry in a:
        c = len(entry["hu"])
        l = ""
        lenght = 0
        # go through all DrugAdverseEvent_openFDA of a pair and combine them
        for e in entry["hu"]:
            if lenght < 100:
                l += str(dict(e)) + "|"
            else:
                break
            lenght += 1
        l = l[:-1]
        writer.writerow([entry["c.identifier"], entry["s.identifier"], l, c])

    count += LIMIT
    print("Done: " + str(count))
    if count % 100000 == 0:
        print(datetime.datetime.now())

f.close()

# create cypher query
cypher = f' MATCH (n:Chemical), (m:SideEffect) WHERE n.identifier = line.chemical AND m.identifier = line.sideeffect CREATE (n)-[:openFDA{{nodes:split(line.nodes,"|"), count:line.count, openfda:"yes"}}]->(m)'
f = open("FDA_edges/edge_cypher.cypher", 'a', encoding="utf-8")

cypher = pharmebinetutils.get_query_import(path_of_directory,
                                          f'mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_Chemical_SideEffect_Edge.tsv',
                                          cypher)
f.write(cypher)

driver.close()

print(datetime.datetime.now())
