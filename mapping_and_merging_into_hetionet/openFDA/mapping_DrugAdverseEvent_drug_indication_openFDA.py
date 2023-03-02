import datetime, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
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
FDA = []
FDA2 = []
FDA3 = []
FDA4 = []
# Speichert die Daten aus Category.
CAT = {}
CAT2 = {}
CAT3 = {}
CAT4 = {}
CAT5 = {}
#######################################################################
cypher_file_name = "cypher.cypher"
map_file_name = "mapped_DrugAdverseEvent_drug_indication_Disease.tsv"
#######################################################################
# f = open("FDA_mappings/"+cypher_file_name, 'w')
# f.close()
#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for DrugAdverseEvent_drug_indication_openFDA ...")
# FDA Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:DrugAdverseEvent_drug_indication_openFDA) RETURN n.id, toLower(n.drugindication);"
a = list(g.run(query))
print(datetime.datetime.utcnow())
print("Fetching data for Disease ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Disease) RETURN n.identifier, toLower(n.name), n.synonyms, n.resource, n.umls_cuis;"
b = list(g.run(query))
#######################################################################
for entry in a:
    id_ = entry["n.id"]
    attr_ = entry["toLower(n.drugindication)"]
    if id_ is not None and attr_ is not None:
        attr_ = attr_.replace("^", "'")
        FDA.append({"id": id_, "name": attr_})
        FDA2.append({"id": id_, "synonym": attr_})
for entry in b:
    id_ = entry["n.identifier"]
    if id_ is not None:
        source_ = entry["n.resource"]
        if source_ is None:
            source_ = []
        attr_ = entry["toLower(n.name)"]
        if attr_ is not None:
            CAT[attr_] = [id_, source_]
        attr_ = entry["n.synonyms"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.lower()
                attr = pharmebinetutils.prepare_obo_synonyms(attr)
                CAT2[attr] = [id_, source_]
        attr_ = entry["n.umls_cuis"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.split(":")[1]
                CAT5[attr] = [id_, source_]
#######################################################################
FDA_name = "DrugAdverseEvent_drug_indication_openFDA"
CAT_name = "Disease"
FDA_attr = [["id", "name"], ["id", "synonym"]]
CAT_attr = [["identifier", "name"], ["identifier", "synonym"]]
_map = ["name", "synonym"]
nonmap_file_name = ["nonmapped_DrugAdverseEvent_drug_indication_name.tsv",
                    "nonmapped_DrugAdverseEvent_drug_indication_synonyms.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA, FDA2], [CAT, CAT2])
#######################################################################
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "name_synonym", cypher_file_name, map_file_name,
                 path_of_directory)

#######################################################################
print(datetime.datetime.utcnow())
print("Fetching data for Symptom ...")
# Category Daten abrufen und anschließend als Dictionary speichern.
query = "MATCH (n:Symptom) RETURN n.identifier, toLower(n.name), n.synonyms, n.resource;"
b = list(g.run(query))
#######################################################################
map_file_name = "mapped_DrugAdverseEvent_drug_indication_Symptom.tsv"
#######################################################################
f = open("FDA_mappings/nonmapped_DrugAdverseEvent_drug_indication_name.tsv", 'r', encoding="utf-8")
header = f.readline()
reader = csv.reader(f, delimiter="\t")
for entry in reader:
    FDA3.append({"id": entry[0], "name": entry[1]})
    FDA4.append({"id": entry[0], "synonym": entry[1]})
f.close()
for entry in b:
    id_ = entry["n.identifier"]
    if id_ is not None:
        source_ = entry["n.resource"]
        if source_ is None:
            source_ = []
        attr_ = entry["toLower(n.name)"]
        if attr_ is not None:
            CAT3[attr_] = [id_, source_]
        attr_ = entry["n.synonyms"]
        if attr_ is not None:
            for attr in attr_:
                attr = attr.lower()
                attr = pharmebinetutils.prepare_obo_synonyms(attr)
                CAT4[attr] = [id_, source_]
#######################################################################
FDA_name = "DrugAdverseEvent_drug_indication_openFDA"
CAT_name = "Symptom"
FDA_attr = [["id", "name"], ["id", "synonym"]]
CAT_attr = [["identifier", "name"], ["identifier", "synonym"]]
_map = ["name", "synonym"]
nonmap_file_name = ["nonmapped_DrugAdverseEvent_drug_indication_name2.tsv",
                    "nonmapped_DrugAdverseEvent_drug_indication_synonyms2.tsv"]
make_mapping_file(map_file_name, "id", "identifier")
fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, [FDA3, FDA4], [CAT3, CAT4])
make_cypher_file(FDA_name, CAT_name, "id", "identifier", "name_synonym", cypher_file_name, map_file_name,
                 path_of_directory)
#######################################################################
f = open("FDA_mappings/nonmapped_DrugAdverseEvent_drug_indication_name.tsv", 'r', encoding="utf-8")
header = f.readline()
reader = csv.reader(f, delimiter="\t")
FDA = {}
for entry in reader:
    FDA[entry[1]] = entry[0]
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
CUI = {}
for (cui_, str_) in cur:
    CUI[str_.lower()] = cui_
f = open("FDA_mappings/mapped_DrugAdverseEvent_drug_indication_Disease.tsv", 'a', encoding="utf-8", newline='')
writer = csv.writer(f, delimiter="\t")
f2 = open("FDA_mappings/nonmapped_DrugAdverseEvent_drug_indication_name.tsv", 'w', encoding="utf-8", newline='')
writer2 = csv.writer(f2, delimiter="\t")
writer2.writerow(["id", "name"])
for entry in FDA:
    if entry in CUI:
        if CUI[entry] in CAT5:
            resource = CAT5[CUI[entry]][1]
            resource.append("openFDA")
            resource = "|".join(sorted(set(resource), key=lambda s: s.lower()))
            writer.writerow([FDA[entry], CAT5[CUI[entry]][0], "umls", resource])
        else:
            writer2.writerow([FDA[entry], entry])
    else:
        writer2.writerow([FDA[entry], entry])
f.close()
f2.close()
driver.close()
