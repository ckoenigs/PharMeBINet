from neo4j import GraphDatabase


def generateConnection():
    db = GraphDatabase.driver("bolt://localhost:7687",auth=("neo4j","test"),encrypted=False)
    return db


def query(tx, q):
    return list(tx.run(q).values())  # etwas unschön, aber das einfachste
