import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
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

# open the cypher file
f = open("FDA_edges/edge_cypher.cypher", 'a', encoding="utf-8")
f.close()

# Chemical - SubstanceData_relationships_substance - SubstanceData - Chemical
query = f'MATCH z=(c:Chemical)-[e1:unii_name_merge]->(o:SubstanceData_relationships_substance_openFDA)-[e2:Event]->(d:SubstanceData_openFDA)<-[e3:unii_name_synonym_smiles_merge]-(s:Chemical) RETURN c.identifier, s.identifier, e2.type'
a = list(g.run(query))
print("Query return length: " + str(len(a)))

# set of created file names
files = set()
# go through results.
for entry in a:

    # Speciel symbols are removed from edge type.
    # name: The first part of the type is the edge type
    # type_: If a second part exists then it is a additional edge property in the edge
    tp = entry["e2.type"]
    tp = tp.replace("/", "_").replace(" ", "_")
    name = tp.split("->")[0]
    name = name.replace("-", "_")
    try:
        type_ = tp.split("->")[1]
    except:
        type_ = ""

    # If for a edge type (name) no file exists a new tsv file is generated and a fitting cypher query is added to
    # cypher file.
    if name not in files:
        f = open("FDA_edges/SubstanceData_Chemical_Chemical_Edge_" + name + ".tsv", 'w', encoding="utf-8", newline='')
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["id1", "id2", "type"])
        f.close()
        # Cypher Eintrag für Datei erstellen
        f = open("FDA_edges/edge_cypher.cypher", 'a', encoding="utf-8")
        cypher = f' MATCH (n:Chemical), (m:Chemical) WHERE n.identifier = line.id1 AND m.identifier = line.id2 CREATE (n)-[:{name}{{additional_type:line.type, openfda:"yes", resource:["openFDA"], source:"openFDA"}}]->(m)'
        cypher = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/openFDA/FDA_edges/SubstanceData_Chemical_Chemical_Edge_{name}.tsv',
                                                   cypher)
        f.write(cypher)
        f.close()
        files.add(name)
    # write into the write file
    f = open("FDA_edges/SubstanceData_Chemical_Chemical_Edge_" + name + ".tsv", 'a', encoding="utf-8", newline='')
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([entry["c.identifier"], entry["s.identifier"], type_])
    f.close()

driver.close()
