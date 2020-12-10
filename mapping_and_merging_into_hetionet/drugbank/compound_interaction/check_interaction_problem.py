'''integrate the other diseases and relationships from disease ontology in hetionet'''
sys.path.append("../..")
import create_connection_to_databases, authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

'''
go through the interaction file and check if the relationship exists
'''
def load_csv(file_path):
    file=open(file_path,'r')
    csv_reader=csv.reader(file)
    next(csv_reader)
    for db1, db2, description in csv_reader:
        query='''MATCH (n:Compound{identifier:'%s'}) RETURN n.identifier''' %(db1)
        results=g.run(query)
        result=results.evaluate()
        if result is None:
            print(db1)

        query = '''MATCH (n:Compound{identifier:'%s'}) RETURN n.identifier''' % (db2)
        results = g.run(query)
        result = results.evaluate()
        if result is None:
            print(db2)




def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all hetionet compound in dictionary')

    load_csv('interaction.csv')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
