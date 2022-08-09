import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
from mapping import *

if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path openFDA')

print(datetime.datetime.utcnow())
print("Connecting to database neo4j ...")
global g
g = create_connection_to_databases.database_connection_neo4j()

print(datetime.datetime.utcnow())
print("Fetching data ...")

f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Symptom_Edge.tsv", 'w', encoding="utf-8", newline='')
writer = csv.writer(f, delimiter="\t")
writer.writerow(["chemical", "symptom", "nodes", "count"])

# Limit for query
LIMIT = 1000
count = 0

a = [1]
while len(a) > 0:
    query = f'MATCH z=(c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)<-[e3:Event]-(r:DrugAdverseEvent_drug_indication_openFDA)<-[e4:name_synonym_merge]-(s:Symptom) WITH c,collect(d) as hu,s SKIP {str(count)} LIMIT {LIMIT} RETURN c.identifier, s.identifier, hu'
    a = list(g.run(query))
    print("Query return length: " + str(len(a)))
    for entry in a:
        l = ""
        length = 0
        for e in entry["hu"]:
            if length < 100:
                d = {}
                for a in e:
                    d[a] = e[a]
                l += str(d) + "|"
            length += 1
        l = l[:-1]
        c = len(entry["hu"])
        writer.writerow([entry["c.identifier"], entry["s.identifier"], l, c])
    count += LIMIT
    print("Done: " + str(count))

f.close()

# Cypher query erstellen
cypher = f'USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_indication_Chemical_Symptom_Edge.tsv" AS row FIELDTERMINATOR "\t" MATCH (n:Chemical), (m:Symptom) WHERE n.identifier = row.chemical AND m.identifier = row.symptom CREATE (n)-[:TREATS_CHtS{{nodes:split(row.nodes,"|"), count:row.count, openfda:"yes", source:"openFDA", resource:["openFDA"]}}]->(m);'
f = open("FDA_edges/edge_cypher.cypher", 'a', encoding="utf-8")
f.write(cypher)
f.close()
