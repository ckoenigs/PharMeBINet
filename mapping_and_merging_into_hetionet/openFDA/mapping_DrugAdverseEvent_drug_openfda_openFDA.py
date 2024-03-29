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
g = driver.session(database='graph')
#######################################################################
# Speichert die Daten aus FDA.
FDA2 = []
FDA3 = []
FDA4 = []
# Speichert die Daten aus Category.

CAT2 = {}
CAT3 = {}
CAT4 = {}

#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_DrugAdverseEvent_drug_openfda_Chemical.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for DrugAdverseEvent_drug_openfda_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:DrugAdverseEvent_drug_openfda_openFDA) RETURN n.id, n.generic_name,  n.product_ndc;"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for Chemical ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Chemical) RETURN n.identifier, toLower(n.name), n.synonyms, n.resource;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    if id_ is not None:
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
        attr_ = entry["toLower(n.name)"]
        if attr_ is not None:
            CAT2[attr_] = [id_, source_]
        attr_ = entry["n.synonyms"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.lower()
                CAT4[attr] = [id_, source_]
#######################################################################
FDA_name = "DrugAdverseEvent_drug_openfda_openFDA"
CAT_name = "Chemical"
FDA_attr = [["id", "name"], ["id", "synonym"]]
CAT_attr = [["identifier", "name"], ["identifier", "synonym"]]
_map = ["name", "synonym"]
nonmap_file_name = ["nonmapped_DrugAdverseEvent_drug_openfda_name.tsv",
                    "nonmapped_DrugAdverseEvent_drug_openfda_synonym.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA2, FDA4], [CAT2, CAT4])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "name_synonym", cypher_file_name, map_file_name,
                 path_of_directory)
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for Product ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Product) RETURN n.identifier, n.ndc_product_code, n.resource;"
b = list(g.run(query))
#######################################################################
map_file_name = "mapped_DrugAdverseEvent_drug_openfda_Product.tsv"
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
FDA_name = "DrugAdverseEvent_drug_openfda_openFDA"
CAT_name = "Product"
FDA_attr = [["id", "product_ndc"]]
CAT_attr = [["identifier", "product_ndc"]]
_map = ["product_ndc"]
nonmap_file_name = ["nonmapped_DrugAdverseEvent_drug_openfda_ndc.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA3], [CAT3])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "product_ndc", cypher_file_name, map_file_name,
                 path_of_directory)
driver.close()
