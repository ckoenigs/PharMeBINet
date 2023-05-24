import json
import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# cypher file
cypher_file = open("output/cypher_edge.cypher", "w", encoding="utf-8")

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def cypher_edge(file_name, label1, label2, properties, edge_name):
    """
    :param cypher_file: destination file to write the queries to
    :param file_name: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param id_list: the keys that are only for matching (they do not need to be part of the edge-information)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query = f'Match (p1:{label1}{{identifier:line.id1}}),(p2:{label2}{{identifier:line.id2}}) Create (p1)-[:{edge_name}{{ '
    for header in properties:
        if header in ["strong", "weak", "predict", "RNAInterID"]:
            if header!="RNAInterID":
                query += header + ':split(line.' + header + ',"|"), '
            else:

                query += header + 's:split(line.' + header + ',"|"), '
        else:
            query += f'{header}:line.{header}, '

    query = query + ' source:"RNAinter", resource:["RNAinter"], license:"Provide data for non-commercial use, distribution, or reproduction in any medium, only if you properly cite the original work.",rnainter:"yes", url:"http://www.rnainter.org/"}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/RNAinter/{file_name}',
                                              query)
    cypher_file.write(query)


def edges_new():
    print("######### load_from_database ##################")
    names = ["dna", "Gene", "compound", "Chemical", "protein", "Protein", "rna", "RNA"]
    score = 0.5
    i = 0

    LIMIT = 20000
    while i < len(names):
        print(names[i])
        print(datetime.datetime.now())
        file_name = 'output/RNA_' + names[i + 1] + '_edges.tsv'
        counter = 0
        with open(file_name, 'w', newline='') as tsv_file:
            writer = csv.writer(tsv_file, delimiter='\t')
            writer.writerow(["id1", "id2", "score", "strong", "weak", "predict", "RNAInterID"])
            current_counter = LIMIT
            index = 0
            while current_counter == LIMIT:
                query = 'MATCH z=(m:RNA)--(:rna_RNAInter)-[r]-(:%s_RNAInter)--(n:%s) WHERE toFloat(r.score) >= %s WITH m, collect(r) as edge, n  SKIP %s Limit %s  RETURN n.identifier, m.identifier, edge' % (
                    names[i], names[i + 1], score, str(index * LIMIT), str(LIMIT))
                a = list(g.run(query))
                current_counter = 0
                index += 1

                for entry in a:
                    current_counter += 1
                    counter += 1
                    entry_score = 0
                    list_strong = list_weak = list_predict = list_id = ""

                    for x in entry["edge"]:
                        e = dict(x)
                        if "strong" in e.keys():
                            for s in e["strong"]:
                                if s not in list_strong:
                                    list_strong = list_strong + "|" + s
                        if "weak" in e.keys():
                            for s in e["weak"]:
                                if s not in list_weak:
                                    list_weak = list_weak + "|" + s
                        if "predict" in e.keys():
                            for s in e["predict"]:
                                if s not in list_predict:
                                    list_predict = list_predict + "|" + s

                        list_id = list_id + "|" + e["RNAInterID"]
                        entry_score = entry_score + float(e["score"])

                    writer.writerow([entry['n.identifier'], entry['m.identifier'], (entry_score / len(entry["edge"])),
                                     list_strong[1:], list_weak[1:], list_predict[1:], list_id[1:]])

                    if counter % 500000 == 0:
                        print(counter)
                        print(datetime.datetime.now())

        edge_name = "ASSOCIATES_" + names[i + 1][0] + 'aR' if names[i + 1] != 'Chemical' else "ASSOCIATES_CHaR"
        cypher_edge(file_name, names[i + 1], "RNA", ["score", "strong", "weak", "predict", "RNAInterID"], edge_name)
        i += 2
        print("number of edges", counter)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnadinter edge')
    create_connection_with_neo4j()
    edges_new()
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
