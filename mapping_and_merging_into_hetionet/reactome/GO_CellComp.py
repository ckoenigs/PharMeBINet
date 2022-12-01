
from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with pharmebinet gocellcomp with identifier as key and value the name
dict_gocellcomp_pharmebinet_identifier = {}

# dictionary with pharmebinet gocellcomp with identifier as key and value the xrefs
dict_gocellcomp_pharmebinet_identifier_xrefs = {}

# dictionary with pharmebinet gocellcomp with name as key and value the identifier
dict_gocellcomp_pharmebinet_alt_ids = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary from gocellcomp_id to resource
dict_gocellcompId_to_resource = {}

'''
load in all gocellcomp from pharmebinet in a dictionary
'''


def load_pharmebinet_gocellcomp_in():
    # query ist ein String
    query = '''MATCH (n:CellularComponent) RETURN n.identifier, n.alternative_ids, n.resource'''
    # graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for identifier, alt_ids, resource, in results:
        # im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        # dict_gobiolproc_pharmebinet_identifier[identifier] = names
        dict_gocellcompId_to_resource[identifier] = resource
        identifier = identifier.replace("GO:", "")
        dict_gocellcomp_pharmebinet_identifier[identifier] = 1
        if alt_ids:
            for alt_id in alt_ids:
                dict_gocellcomp_pharmebinet_alt_ids[alt_id.replace("GO:", "")] = identifier

    print('number of gocellcomp nodes in pharmebinet:' + str(len(dict_gocellcomp_pharmebinet_identifier)))


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_gocellcomp = open('gocellcomp/not_mapped_gocellcomp.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_gocellcomp, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['id'])

file_mapped_gocellcomp = open('gocellcomp/mapped_gocellcomp.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_gocellcomp, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_pharmebinet', 'resource'])

'''
load all reactome gocellcomp and check if they are in pharmebinet or not
'''


def load_reactome_gocellcomp_in():
    query = '''MATCH (n:GO_CellularComponent_reactome) RETURN n'''
    results = graph_database.run(query)

    # zähler wie oft id mapt
    counter_map_with_id = 0
    # counter_map_with_name = 0
    for gocellcomp_node, in results:
        gocellcomp_id = gocellcomp_node['accession']  # hier ist nur die nr...?
        resource = gocellcomp_node['resource']

        # check if the reactome pathway id is part in the pharmebinet idOwn
        if gocellcomp_id in dict_gocellcomp_pharmebinet_identifier:
            counter_map_with_id += 1
            # if len(dict_own_id_to_pcid_and_other[pathways_id]) > 1:
            #     print('multiple für identifier')
            print('id')
            resource = set(dict_gocellcompId_to_resource["GO:" + gocellcomp_id])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            csv_mapped.writerow(
                [gocellcomp_id, "GO:" + gocellcomp_id, resource])  # erster eintrag reactome, zweiter pharmebinet
        elif gocellcomp_id in dict_gocellcomp_pharmebinet_alt_ids:
            resource = set(dict_gocellcompId_to_resource["GO:" + dict_gocellcomp_pharmebinet_alt_ids[gocellcomp_id]])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            csv_mapped.writerow([gocellcomp_id, "GO:" + gocellcomp_id, resource])
        else:
            csv_not_mapped.writerow([gocellcomp_id])
            # file_not_mapped_pathways.write(pathways_id+ '\t' +pathways_name+ '\t' + pathways_id_type+ '\n' )

    # print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    # print(dict_mapped_source)


'''
generate connection between mapping gocellcomp of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    # mappt die Knoten, die es in pharmebinet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/reactome/gocellcomp/mapped_gocellcomp.tsv" As line FIELDTERMINATOR "\\t"
     Match (d: CellularComponent{identifier: line.id_pharmebinet}),(c:GO_CellularComponent_reactome{accession:line.id}) Create (d)-[: equal_to_reactome_gocellcomp]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
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
    print('Load all CellularComponent from pharmebinet into a dictionary')

    load_pharmebinet_gocellcomp_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all reactome GO_CellularComponent from neo4j into a dictionary')

    load_reactome_gocellcomp_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate new GO_CellularComponent and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
