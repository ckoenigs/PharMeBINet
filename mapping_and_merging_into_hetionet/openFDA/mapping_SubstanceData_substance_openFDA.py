import datetime, sys

sys.path.append("../..")
import create_connection_to_databases
from mapping import *

if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path openFDA')
make_dir()
#######################################################################
print(datetime.datetime.utcnow())
print("Connecting to database neo4j ...")
global g, driver
driver = create_connection_to_databases.database_connection_neo4j_driver()
g = driver.session()
#######################################################################
# Speichert die Daten aus FDA.
FDA1 = []
FDA2 = []
FDA3 = []
# Speichert die Daten aus Category.
CAT1 = {}
CAT2 = {}
CAT3 = {}
#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_SubstanceData_substance_Chemical.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for SubstanceData_substance_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:SubstanceData_substance_openFDA) RETURN n.id, n.unii, toLower(n.name);"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for Chemical ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Chemical) RETURN n.identifier, n.unii, toLower(n.name),n.synonyms, n.resource;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    if id_ is not None:
        attr_ = entry["n.unii"]
        if attr_ is not None:
            FDA1.append({"id": id_, "unii": attr_})
        attr_ = entry["toLower(n.name)"]
        if attr_ is not None:
            FDA2.append({"id": id_, "name": attr_})
            FDA3.append({"id": id_, "synonym": attr_})
for entry in b:
    id_ = entry["n.identifier"]
    if id_ is not None:
        source_ = entry["n.resource"]
        if source_ is None:
            source_ = []
        attr_ = entry["n.unii"]
        if attr_ is not None:
            CAT1[attr_] = [id_, source_]
        attr_ = entry["toLower(n.name)"]
        if attr_ is not None:
            CAT2[attr_] = [id_, source_]
        attr_ = entry["n.synonyms"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.lower()
                CAT3[attr] = [id_, source_]
#######################################################################
FDA_name = "SubstanceData_substance_openFDA"
CAT_name = "Chemical"
FDA_attr = [["id", "unii"], ["id", "name"], ["id", "synonym"]]
CAT_attr = [["identifier", "unii"], ["identifier", "name"], ["identifier", "synonym"]]
_map = ["unii", "name", "synonym"]
nonmap_file_name = ["nonmapped_SubstanceData_substance_unii.tsv", "nonmapped_SubstanceData_substance_name.tsv",
                    "nonmapped_SubstanceData_substance_synonym.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA1, FDA2, FDA3],
           [CAT1, CAT2, CAT3])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "unii_name", cypher_file_name, map_file_name,
                 path_of_directory)
driver.close()
