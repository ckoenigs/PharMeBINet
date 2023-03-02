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

print(datetime.datetime.utcnow())
print("Connecting to database neo4j ...")
global g, driver
driver = create_connection_to_databases.database_connection_neo4j_driver()
g = driver.session()

print(datetime.datetime.utcnow())
print("Fetching data ...")

# create the tsv files for existing and not existing edges
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

# gather the existing treat paths between chemical and disease and write them into a dictionary
query = f'MATCH (c:Chemical)-[e:TREATS_CHtD]->(d:Disease) RETURN c.identifier, e, d.identifier'
b = list(g.run(query))
arr = {}
for entry in b:
    c = entry["c.identifier"]
    d = entry["d.identifier"]
    e = entry["e"]
    arr[c + "_" + d] = e["resource"];

a = [1]
# Chemical - DrugAdverseEvent_drug_openfda - DrugAdverseEvent_drug - DrugAdverseEvent_drug_indication - Disease
# get treat path from openFDA between chemical-disease . Gather number of path exists and remember at least around 100
# DrugAdverseEvent_drug_openFDA. The check if pair exist or not and write in the right tsv file.
while len(a) > 0:
    query = f'MATCH z=(c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)<-[e3:Event]-(r:DrugAdverseEvent_drug_indication_openFDA)<-[e4:name_synonym_merge]-(s:Disease) WITH c,collect(d) as hu,s SKIP {str(count)} LIMIT {LIMIT} RETURN c.identifier, s.identifier, hu'
    a = list(g.run(query))
    print("Query return length: " + str(len(a)))
    for entry in a:
        l = ""
        length = 0
        for e in entry["hu"]:
            # save all DrugAdverseEvent_drug_openFDA als string of Dicts with | seperated and only less than 100
            if length < 100:
                d = {}
                for a in e:
                    d[a] = e[a]
                l += str(d) + "|"
            else:
                break
            length += 1
        l = l[:-1]
        c = len(entry["hu"])
        #  Check if pair already exist or not and write into the right file
        if entry["c.identifier"] + "_" + entry["s.identifier"] in arr:
            f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge_append.tsv", 'a', encoding="utf-8",
                     newline='')
            writer = csv.writer(f, delimiter="\t")
            resource = ""
            for a in arr[entry["c.identifier"] + "_" + entry["s.identifier"]]:
                resource += a + "|"
            if "openFDA" in resource:
                resource = resource[:-1]
            else:
                resource += "openFDA"
            writer.writerow([entry["c.identifier"], entry["s.identifier"], l, c, resource])
            f.close()
        else:
            f = open("FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge.tsv", 'a', encoding="utf-8",
                     newline='')
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([entry["c.identifier"], entry["s.identifier"], l, c, "openFDA"])
            f.close()

    count += LIMIT
    print("Done: " + str(count))

f.close()

# Cypher query erstellen
cypher = f' MATCH (n:Chemical), (m:Disease) WHERE n.identifier = line.chemical AND m.identifier = line.disease CREATE (n)-[:TREATS_CHtD{{nodes:split(line.nodes,"|"), count:line.count, resource:split(line.resource,"|"), source:line.resource, openfda:"yes"}}]->(m)'
cypher = pharmebinetutils.get_query_import(path_of_directory,
                                           f'mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge.tsv',
                                           cypher)
cypher2 = f' MATCH (n:Chemical)-[e:TREATS_CHtD]->(m:Disease) WHERE n.identifier = line.chemical AND m.identifier = line.disease SET e.nodes = split(line.nodes,"|"), e.count = line.count, e.openfda="yes", e.resource = split(line.resource,"|")'
cypher2 = pharmebinetutils.get_query_import(path_of_directory,
                                            f'mapping_and_merging_into_hetionet/openFDA/FDA_edges/DrugAdverseEvent_indication_Chemical_Disease_Edge_append.tsv',
                                            cypher2)
f = open("FDA_edges/edge_cypher.cypher", 'w', encoding="utf-8")
f.write(cypher)
f.write(cypher2)
f.close()

driver.close()
