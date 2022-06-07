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
global g
g = create_connection_to_databases.database_connection_neo4j()
#######################################################################
# Speichert die Daten aus FDA.
FDA = []
# Speichert die Daten aus Category.
CAT = {}
#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_SubstanceData_moieties_Chemical.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for SubstanceData_moieties_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:SubstanceData_moieties_openFDA) RETURN n.id, n.smiles;"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for Chemical ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Chemical) RETURN n.identifier, n.calculated_properties_kind_value_source, n.resource;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    if id_ is not None:
        attr_ = entry["n.smiles"]
        if attr_ is not None:
            FDA.append({"id": id_, "smiles": attr_})
for entry in b:
    id_ = entry["n.identifier"]
    if id_ is not None:
        source_ = entry["n.resource"]
        if source_ is None:
            source_ = []
        attr_ = entry["n.calculated_properties_kind_value_source"]
        if attr_ is not None:
            for attr in attr_:
                if attr.startswith("SMILES"):
                    attr = attr.split("::")[1]
                    CAT[attr] = [id_, source_]
#######################################################################
FDA_name = "SubstanceData_moieties_openFDA"
CAT_name = "Chemical"
FDA_attr = [["id", "smiles"]]
CAT_attr = [["identifier", "smiles"]]
_map = ["smiles"]
nonmap_file_name = ["nonmapped_SubstanceData_moieties_smiles.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA], [CAT])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "smiles", cypher_file_name, map_file_name, path_of_directory)
