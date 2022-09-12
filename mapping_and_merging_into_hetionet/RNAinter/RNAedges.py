import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# cypher file
cypher_file=open("cypher.cypher","w",encoding="utf-8")

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

def cypher_edge(filename, label1, label2, properties, edge_name):
    """
    :param cypher_file: destination file to write the queries to
    :param filename: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param id_list: the keys that are only for matching (they do not need to be part of the edge-information)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query_start = 'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:///'+filename+'" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:{label1}{{identifier:line.id1}}),(p2:{label2}{{identifier:line.id2}}) Create (p1)-[:{edge_name}{{  '
    for header in properties:
            query += f'{header}:line.{header}, '
    query = query[:-2]+'}]->(p2);\n'
    cypher_file.write(query)

def edges():
    print("######### load_from_database ##################")
    names = ["dna", "Gene", "compound", "Chemical", "protein", "Protein"]
    i=0

    LIMIT = 200000
    while i < len(names):
        print(names[i])
        print(datetime.datetime.now())
        file_name = 'RNA_' + names[i + 1] + '_edges.tsv'
        counter=0
        with open(file_name, 'w', newline='') as tsv_file:
            fieldnames = ["id1", "id2", "RNAInterID", "score", "strong", "weak", "predict"]
            writer = csv.DictWriter(tsv_file, fieldnames=fieldnames,delimiter='\t',restval='')
            writer.writeheader()
            current_counter=LIMIT
            index=0
            while current_counter==LIMIT:
                query = "MATCH (n:%s)--(:%s_RNAInter)-[r]-(rna_RNAInter)--(m:RNA) With n,r,m SKIP %s Limit %s RETURN n.identifier, m.identifier, r" % (names[i + 1], names[i],str(index*LIMIT) , str(LIMIT))
                result = g.run(query)
                current_counter=0
                index+=1
                for id1, id2, edge, in result:
                    current_counter+=1
                    counter+=1
                    edgeinfo = dict(edge)
                    edgeinfo["id1"]=id1
                    edgeinfo["id2"]=id2
                    writer.writerow(edgeinfo)
                    if counter%500000==0:
                        print(counter)
                        print(datetime.datetime.now())

        cypher_edge(file_name, names[i + 1], "RNA", ["RNAInterID", "score", "strong", "weak", "predict"],"associate_RNA_" + names[i + 1])
        i += 2
        print("number of edges", counter)

def main():
    create_connection_with_neo4j()
    edges()

if __name__ == "__main__":
    # execute only if run as a script
    main()
