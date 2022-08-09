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

f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge.tsv", 'w', encoding="utf-8", newline='')
writer = csv.writer(f, delimiter="\t")
writer.writerow(["chemical", "disease", "nodes", "count", "resource"])
f.close()
f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge_append.tsv", 'w', encoding="utf-8", newline='')
writer = csv.writer(f, delimiter="\t")
writer.writerow(["chemical", "disease", "nodes", "count", "resource"])
f.close()

# Limit for query
LIMIT = 10000
count = 0

query = f'MATCH (c:Chemical)-[e:TREATS_CHtD]->(d:Disease) RETURN c.identifier, e, d.identifier'
b = list(g.run(query))
arr = {}
for entry in b:
    c = entry["c.identifier"]
    d = entry["d.identifier"]
    e = entry["e"]
    arr[c+"_"+d] = e["resource"];

a = [1]
while len(a) > 0:
    query = f'MATCH z=(c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)<-[e3:Event]-(r:DrugAdverseEvent_drug_indication_openFDA)<-[e4:name_synonym_merge]-(s:Disease) WITH c,collect(d) as hu,s SKIP {str(count)} LIMIT {LIMIT} RETURN c.identifier, s.identifier, hu'
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
        if entry["c.identifier"]+"_"+entry["s.identifier"] in arr:
            f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge_append.tsv", 'a', encoding="utf-8", newline='')
            writer = csv.writer(f, delimiter="\t")
            resource = ""
            for a in arr[entry["c.identifier"]+"_"+entry["s.identifier"]]:
                resource += a + "|"
            if "openFDA" in resource:
                resource = resource[:-1]
            else:
                resource += "openFDA"
            writer.writerow([entry["c.identifier"], entry["s.identifier"], l, c, resource])
            f.close()
        else:
            f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge.tsv", 'a', encoding="utf-8", newline='')
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([entry["c.identifier"], entry["s.identifier"], l, c, "openFDA"])
            f.close()
            
    count += LIMIT
    print("Done: " + str(count))

f.close()

# Cypher query erstellen
cypher = f'USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge.tsv" AS row FIELDTERMINATOR "\t" MATCH (n:Chemical), (m:Disease) WHERE n.identifier = row.chemical AND m.identifier = row.disease CREATE (n)-[:TREATS_CHtD{{nodes:split(row.nodes,"|"), count:row.count, resource:split(row.resource,"|"), source:row.resource, openfda:"yes"}}]->(m);\n'
cypher2 = f'USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge_append.tsv" AS row FIELDTERMINATOR "\t" MATCH (n:Chemical)-[e:TREATS_CHtD]->(m:Disease) WHERE n.identifier = row.chemical AND m.identifier = row.disease SET e.nodes = split(row.nodes,"|"), e.count = row.count, e.openfda="yes", e.resource = split(row.resource,"|");\n'
f = open("FDA_edges/edge_cypher.cypher", 'w', encoding="utf-8")
f.write(cypher)
f.write(cypher2)
f.close()
