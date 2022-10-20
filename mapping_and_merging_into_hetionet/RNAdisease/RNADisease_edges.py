import csv, sys
import datetime, json
sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# cypher file
cypher_file=open("output/cypher_edge.cypher","w",encoding="utf-8")

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

def cypher_edge(file_name, label1, label2,properties, edge_name):
    """
    :param cypher_file: destination file to write the queries to
    :param file_name: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param id_list: the keys that are only for matching (they do not need to be part of the edge-information)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAdisease/{file_name}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:{label1}{{identifier:line.id1}}),(p2:{label2}{{identifier:line.id2}}) Create (p1)-[:{edge_name}{{ '
    for header in properties:
            query += f'{header}:split(line.{header},"|")}}]->(p2);\n'
    cypher_file.write(query)


def edges():
    names = ["Disease","Symptom"]
    score = 0.8
    i = 0

    LIMIT = 20000
    while i < len(names):
        print(names[i])
        print(datetime.datetime.now())
        file_name = 'output/RNADisease_RNA_' + names[i] + '_edges.tsv'
        counter = 0
        with open(file_name, 'w', newline='') as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            writer.writerow(["id1", "id2", "associate"])
            current_counter = LIMIT
            index = 0
            while current_counter == LIMIT:
                query = "MATCH (n:RNA)--(:rna_RNADisease)-[r]-(:disease_RNADisease)--(m:%s) WHERE toFloat(r.score) >= %s WITH n, collect(r) as edge, m  SKIP %s Limit %s  RETURN n.identifier, m.identifier, edge" % (names[i],score, str(index * LIMIT), str(LIMIT))

                a = list(g.run(query))
                current_counter = 0
                index += 1

                for entry in a:
                    current_counter += 1
                    counter += 1
                    t = ""
                    for e in entry["edge"]:
                        b = dict(e)
                        t = t + "|" + json.dumps(b)

                    writer.writerow([entry['n.identifier'], entry['m.identifier'], t[1:]])

                    if counter % 100000 == 0:
                        print(counter)
                        print(datetime.datetime.now())


        cypher_edge(file_name, "RNA",  names[i], ["associate"], "associate_RNA_" + names[i])
        i += 1
        print("number of edges", counter)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnadisease')
    create_connection_with_neo4j()
    edges()

if __name__ == "__main__":
    # execute only if run as a script
    main()