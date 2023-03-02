import datetime, sys

sys.path.append("../..")
import create_connection_to_databases
from mapping import *

if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path rnaCentral')
make_dir()
#######################################################################
print(datetime.datetime.utcnow())
print("Connecting to database neo4j ...")
global g, driver
driver = create_connection_to_databases.database_connection_neo4j_driver()
g = driver.session()
#######################################################################
# Speichert die Daten aus FDA.
FDA = []
# Speichert die Daten aus Category.
CAT = {}
#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_DrugAdverseEvent_reaction_SideEffect.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for DrugAdverseEvent_reaction_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:DrugAdverseEvent_reaction_openFDA) RETURN n.id, toLower(n.reactionmeddrapt);"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for SideEffect ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:SideEffect) RETURN n.identifier, toLower(n.name), n.resource;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    attr_ = entry["toLower(n.reactionmeddrapt)"]
    if id_ is not None and attr_ is not None:
        attr_ = attr_.replace("^", "'")
        FDA.append({"id": id_, "name": attr_})
for entry in b:
    id_ = entry["n.identifier"]
    attr_ = entry["toLower(n.name)"]
    source_ = entry["n.resource"]
    if source_ is None:
        source_ = []
    if id_ is not None and attr_ is not None:
        CAT[attr_] = [id_, source_]
#######################################################################
FDA_name = "DrugAdverseEvent_reaction_openFDA"
CAT_name = "SideEffect"
FDA_attr = [["id", "name"]]
CAT_attr = [["identifier", "name"]]
_map = ["name"]
nonmap_file_name = ["nonmapped_DrugAdverseEvent_reaction_reaction.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA], [CAT])
#######################################################################
#######################################################################
print(datetime.datetime.utcnow())
print("Connecting to database umls ...")
c = create_connection_to_databases.database_connection_umls()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for umls ...")
query = "SELECT CUI, STR FROM MRCONSO"
global cur
cur = c.cursor()
cur.execute(query)
#######################################################################
map_others(cur, CAT, "nonmapped_DrugAdverseEvent_reaction_reaction",
           "mapped_DrugAdverseEvent_reaction_SideEffect")
#######################################################################
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "name", cypher_file_name, map_file_name, path_of_directory)
driver.close()
