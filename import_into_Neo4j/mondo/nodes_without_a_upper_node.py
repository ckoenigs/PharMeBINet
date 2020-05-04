from py2neo import Graph#, authenticate
import datetime
import csv

# connect with the neo4j database
def database_connection():
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))

'''
find all nodes which are not 'disease' but have no upper node
'''
def generate_file_with_nodes_without_upper_nodes():
    query='''MATCH (n:disease) Where not n.`http://www.geneontology.org/formats/oboInOwl#id`='MONDO:0000001' and not (n)-[:subClassOf]->() RETURN n.`http://www.geneontology.org/formats/oboInOwl#id`, n.label'''
    results=g.run(query)
    with open('nodes_without_upper_nodes.csv', 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ID', 'name'])
        for id, name, in results:
            writer.writerow([id, name])

def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate file with all nodes which has no upper node ')

    generate_file_with_nodes_without_upper_nodes()


    print('##########################################################################')


    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
