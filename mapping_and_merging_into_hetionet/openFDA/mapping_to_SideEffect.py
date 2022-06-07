import os,sys
if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path openFDA')

if os.path.exists("FDA_mappings/to_SideEffect.tsv"):
    os.remove("FDA_mappings/to_SideEffect.tsv")
# Query zum Erstellen der neuen SideEffect Knoten.
f = open("FDA_mappings/cypher.cypher", 'w', encoding="utf-8")
create = "USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM 'file:"
create += path_of_directory + "mapping_and_merging_into_hetionet/openFDA/FDA_mappings/to_SideEffect.tsv"
create += "' AS row FIELDTERMINATOR '\\t' CREATE"
create += " (SideEffect:SideEffect {identifier: row.identifier, name: row.name, resource: split(row.resource,'|')});\n"
f.write(create)
f.close()
