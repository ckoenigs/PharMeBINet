import datetime
import csv, sys

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

# create tsv file with header
f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Symptom_Edge.tsv", 'w', encoding="utf-8", newline='')
writer = csv.writer(f, delimiter="\t")
writer.writerow(["chemical", "symptom", "nodes", "count"])

# Limit for query
LIMIT = 1000
count = 0

a = [1]

# Chemical - DrugAdverseEvent_drug_openfda - DrugAdverseEvent_drug - DrugAdverseEvent_drug_indication - Symptom
# get treat path from openFDA between chemical-symptom. Gather number of path exists and remember at least around 100
# # DrugAdverseEvent_drug_openFDA and write pair to tsv file.
while len(a) > 0:
    query = f'MATCH z=(c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)<-[e3:Event]-(r:DrugAdverseEvent_drug_indication_openFDA)<-[e4:name_synonym_merge]-(s:Symptom) WITH c,collect(d) as hu,s SKIP {str(count)} LIMIT {LIMIT} RETURN c.identifier, s.identifier, hu'
    a = list(g.run(query))
    print("Query return length: " + str(len(a)))
    for entry in a:
        l = ""
        length = 0
        # save all DrugAdverseEvent_drug_openFDA als string of Dicts with | seperated and only less than 100
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

# create Cypher query
cypher = f' MATCH (n:Chemical), (m:Symptom) WHERE n.identifier = line.chemical AND m.identifier = line.symptom CREATE (n)-[:TREATS_CHtS{{nodes:split(line.nodes,"|"), count:line.count, openfda:"yes", source:"openFDA", resource:["openFDA"]}}]->(m)'
cypher = pharmebinetutils.get_query_import(path_of_directory,
                                           f'mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_indication_Chemical_Symptom_Edge.tsv',
                                           cypher)
f = open("FDA_edges/edge_cypher.cypher", 'a', encoding="utf-8")
f.write(cypher)
f.close()
driver.close()
