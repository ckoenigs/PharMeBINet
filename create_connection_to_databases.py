import MySQLdb as mdb
from neo4j import GraphDatabase


# connect with the neo4j database
def database_connection_neo4j_driver():
    driver = GraphDatabase.driver('neo4j://localhost:7687', auth=('neo4j', 'test1234'))
    return driver


def database_connection_RxNorm():
    conRxNorm = mdb.connect('127.0.0.1', 'ckoenigs', 'Za8p7Tf$', 'RxNorm', charset='utf8')
    return conRxNorm


def database_connection_umls():
    con = mdb.connect('127.0.0.1', 'ckoenigs', 'Za8p7Tf$', 'umls', charset='utf8')
    return con
