import os, sys

sys.path.append("../..")
import pharmebinetutils

if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path openFDA')

if os.path.exists("FDA_mappings/to_SideEffect.tsv"):
    os.remove("FDA_mappings/to_SideEffect.tsv")
# Query zum Erstellen der neuen SideEffect Knoten.
f = open("FDA_mappings/cypher.cypher", 'w', encoding="utf-8")
create = " Create (SideEffect:SideEffect :Phenotype {identifier: line.identifier, name: line.name, resource: split(line.resource,'|'), source:'UMLS via openFDA', openfda:'yes', url:'http://identifiers.org/umls/'+line.identifier})"

create = pharmebinetutils.get_query_import(path_of_directory,
                                           f'mapping_and_merging_into_hetionet/openFDA/FDA_mappings/to_SideEffect.tsv',
                                           create)
f.write(create)
f.close()
