import csv
import os
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
g = driver.session(database='graph')
#######################################################################
# Speichert die Daten aus FDA.
FDA = []
FDA2 = []
FDA3 = []
FDA4 = []
# Speichert die Daten aus Category.
CAT = {}
CAT2 = {}
CAT3 = {}
CAT4 = {}
#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_SubstanceData_Chemical.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for SubstanceData_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:SubstanceData_openFDA) RETURN n.id, n.unii, n.structure, n.names;"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for Chemical ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Chemical) RETURN n.identifier, n.unii, toLower(n.name), n.synonyms, n.calculated_properties_kind_value_source, n.resource;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    if id_ is not None:
        attr_ = entry["n.unii"]
        if attr_ is not None:
            FDA.append({"id": id_, "unii": attr_})
        attr_ = entry["n.names"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.split(":")
                boolean1 = False
                for a in attr:
                    a = a.replace("'", "")
                    if boolean1:
                        a1 = str(a.split(",")[:-1]).replace("'", "")[2:-1]
                        a1 = a1.lower()
                        FDA2.append({"id": id_, "name": a1})
                        FDA3.append({"id": id_, "synonym": a1})
                        boolean1 = False
                    if a.endswith(" name"):
                        boolean1 = True
        attr_ = entry["n.structure"]
        if attr_ is not None:
            attr_ = attr_.split(":")
            boolean2 = False
            for a in attr_:
                a = a.replace("'", "")
                if boolean2:
                    a1 = str(a.split(",")[:-1]).replace("'", "")[2:-1]
                    FDA4.append({"id": id_, "smiles": a1})
                    boolean2 = False
                if a.endswith("smiles"):
                    boolean2 = True
for entry in b:
    id_ = entry["n.identifier"]
    if id_ is not None:
        source_ = entry["n.resource"]
        if source_ is None:
            source_ = []
        attr_ = entry["n.unii"]
        if attr_ is not None:
            CAT[attr_] = [id_, source_]
        attr_ = entry["toLower(n.name)"]
        if attr_ is not None:
            CAT2[attr_] = [id_, source_]
        attr_ = entry["n.synonyms"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.lower()
                CAT3[attr] = [id_, source_]
        attr_ = entry["n.calculated_properties_kind_value_source"]
        if attr_ is not None:
            for attr in attr_:
                if attr.startswith("SMILES"):
                    attr = attr.split("::")[1]
                    CAT4[attr] = [id_, source_]
#######################################################################
FDA_name = "SubstanceData_openFDA"
CAT_name = "Chemical"
FDA_attr = [["id", "unii"], ["id", "name"], ["id", "synonym"], ["id", "smiles"]]
CAT_attr = [["identifier", "unii"], ["identifier", "name"], ["identifier", "synonym"], ["identifier", "smiles"]]
_map = ["unii", "name", "synonym", "smiles"]
nonmap_file_name = ["nonmapped_SubstanceData_unii.tsv", "nonmapped_SubstanceData_name.tsv",
                    "nonmapped_SubstanceData_synonym.tsv", "nonmapped_SubstanceData_smiles.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA, FDA2, FDA3, FDA4],
           [CAT, CAT2, CAT3, CAT4])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "unii_name_synonym_smiles", cypher_file_name, map_file_name,
                 path_of_directory)
driver.close()
