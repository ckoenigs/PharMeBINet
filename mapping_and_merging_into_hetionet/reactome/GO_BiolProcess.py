from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with pharmebinet gobiolproc with identifier as key and value the name
dict_gobiolproc_pharmebinet_identifier = {}

# dictionary with pharmebinet gobiolproc with identifier as key and value the xrefs
dict_gobiolproc_pharmebinet_identifier_xrefs = {}

# dictionary with pharmebinet gobiolproc with name as key and value the identifier
dict_gobiolproc_pharmebinet_alt_ids = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary from gobiolprocId_id to resource
dict_gobiolprocId_to_resource = {}

'''
load in all gobiolproc from pharmebinet in a dictionary
'''


def load_pharmebinet_gobiolproc_in():
    # query ist ein String
    query = '''MATCH (n:BiologicalProcess) RETURN n.identifier, n.alternative_ids, n.resource'''
    # query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    # graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for identifier, alt_ids, resource, in results:
        # im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        # dict_gobiolproc_pharmebinet_identifier[identifier] = names
        dict_gobiolprocId_to_resource[identifier] = resource
        identifier = identifier.replace("GO:", "")
        dict_gobiolproc_pharmebinet_identifier[identifier] = 1
        if alt_ids:
            for alt_id in alt_ids:
                dict_gobiolproc_pharmebinet_alt_ids[alt_id.replace("GO:", "")] = identifier

    print('number of gobiolproc nodes in pharmebinet:' + str(len(dict_gobiolproc_pharmebinet_identifier)))
    print('number of gobiolproc nodes in pharmebinet:' + str(len(dict_gobiolproc_pharmebinet_identifier)))


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_gobiolproc = open('gobiolproc/not_mapped_gobiolproc.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_gobiolproc, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['id'])

file_mapped_gobiolproc = open('gobiolproc/mapped_gobiolproc.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_gobiolproc, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_pharmebinet', 'resource'])

'''
load all reactome gobiolproc and check if they are in pharmebinet or not
'''


def load_reactome_gobiolproc_in():
    query = '''MATCH (n:GO_BiologicalProcess_reactome) RETURN n'''
    results = graph_database.run(query)

    # zähler wie oft id mapt
    counter_map_with_id = 0
    # counter_map_with_name = 0
    for gobiolproc_node, in results:
        gobiolproc_id = gobiolproc_node['accession']  # hier ist nur die nr...?
        resource = gobiolproc_node['resource']
        # pathways_name = pathways_node['displayName'].lower()
        # pathways_name=pathways_name.encode("utf-8")

        # check if the reactome pathway id is part in the pharmebinet idOwn
        if gobiolproc_id in dict_gobiolproc_pharmebinet_identifier:
            counter_map_with_id += 1
            # if len(dict_own_id_to_pcid_and_other[pathways_id]) > 1:
            #     print('multiple für identifier')

            csv_mapped.writerow([gobiolproc_id, "GO:" + gobiolproc_id, pharmebinetutils.resource_add_and_prepare(
                dict_gobiolprocId_to_resource["GO:" + gobiolproc_id],
                'Reactome')])  # erster eintrag reactome, zweiter pharmebinet
        elif gobiolproc_id in dict_gobiolproc_pharmebinet_alt_ids:
            csv_mapped.writerow([gobiolproc_id, "GO:" + gobiolproc_id, pharmebinetutils.resource_add_and_prepare(
                dict_gobiolprocId_to_resource["GO:" + dict_gobiolproc_pharmebinet_alt_ids[gobiolproc_id]], 'Reactome')])
        else:
            csv_not_mapped.writerow([gobiolproc_id])
            # file_not_mapped_pathways.write(pathways_id+ '\t' +pathways_name+ '\t' + pathways_id_type+ '\n' )

    # print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    # print(dict_mapped_source)


'''
generate connection between mapping gobiolproc of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    # mappt die Knoten, die es in pharmebinet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/reactome/gobiolproc/mapped_gobiolproc.tsv" As line FIELDTERMINATOR "\\t"
     Match (d: BiologicalProcess {identifier: line.id_pharmebinet}),(c:GO_BiologicalProcess_reactome{accession:line.id}) Create (d)-[: equal_to_reactome_gobiolproc]->(c)  SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all BiologicalProcess from pharmebinet into a dictionary')

    load_pharmebinet_gobiolproc_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all reactome GO_BiologicalProcess from neo4j into a dictionary')

    load_reactome_gobiolproc_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate new GO_BiologicalProcess and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
