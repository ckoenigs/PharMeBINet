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
FDA1 = []
FDA2 = []
FDA3 = []
FDA4 = []
# Speichert die Daten aus Category.
CAT1 = {}
CAT2 = {}
CAT3 = {}
CAT4 = {}
#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_DrugRecallEnforcementReport_openfda_Chemical.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for DrugRecallEnforcementReport_openfda_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:DrugRecallEnforcementReport_openfda_openFDA) RETURN n.id, n.unii, n.generic_name, n.product_ndc;"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for Chemical ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Chemical) RETURN n.identifier, n.unii, toLower(n.name), n.synonyms, n.resource;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    if id_ is not None:
        attr_ = entry["n.unii"]
        if attr_ is not None:
            for attr in attr_:
                FDA1.append({"id": id_, "unii": attr})
        attr_ = entry["n.generic_name"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.lower()
                FDA2.append({"id": id_, "name": attr})
                FDA4.append({"id": id_, "synonym": attr})
        attr_ = entry["n.product_ndc"]
        if attr_ is not None:
            for attr in attr_:
                FDA3.append({"id": id_, "product_ndc": attr})
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
                CAT4[attr] = [id_, source_]
#######################################################################
FDA_name = "DrugRecallEnforcementReport_openfda_openFDA"
CAT_name = "Chemical"
FDA_attr = [["id", "unii"], ["id", "name"], ["id", "synonym"]]
CAT_attr = [["identifier", "unii"], ["identifier", "name"], ["identifier", "synonym"]]
_map = ["unii", "name", "synonym"]
nonmap_file_name = ["nonmapped_DrugRecallEnforcementReport_openfda_unii.tsv", "nonmapped_DrugRecallEnforcementReport_openfda_name.tsv", "nonmapped_DrugRecallEnforcementReport_openfda_synonyms.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA1, FDA2, FDA4], [CAT1, CAT2, CAT4])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "unii_name_synonym", cypher_file_name, map_file_name, path_of_directory)
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for Product ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Product) RETURN n.identifier, n.ndc_product_code, n.resource;"
b = list(g.run(query))
#######################################################################
map_file_name = "mapped_DrugRecallEnforcementReport_openfda_Product.tsv"
#######################################################################
for entry in b:
    id_ = entry["n.identifier"]
    attr_ = entry["n.ndc_product_code"]
    source_ = entry["n.resource"]
    if source_ is None:
        source_ = []
    if id_ is not None and attr_ is not None:
        CAT3[attr_] = [id_, source_]
#######################################################################
FDA_name = "DrugRecallEnforcementReport_openfda_openFDA"
CAT_name = "Product"
FDA_attr = [["id", "product_ndc"]]
CAT_attr = [["identifier", "product_ndc"]]
_map = ["product_ndc"]
nonmap_file_name = ["nonmapped_DrugRecallEnforcementReport_openfda_ndc.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA3], [CAT3])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "product_ndc", cypher_file_name, map_file_name, path_of_directory)
