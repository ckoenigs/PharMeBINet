from py2neo import Graph
import MySQLdb as mdb


# connect with the neo4j database AND MYSQL
def database_connection_neo4j():
    # # authenticate("bimi:7475", "ckoenigs", "test")
    # global g
    # g = Graph("http://bimi:7475/db/data/",bolt=False,auth=("neo4j", "test"))
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))
    return g


def database_connection_RxNorm():
    conRxNorm = mdb.connect('127.0.0.1', 'ckoenigs', 'Za8p7Tf$', 'RxNorm', charset='utf8')
    return conRxNorm


def database_connection_umls():
    con = mdb.connect('127.0.0.1', 'ckoenigs', 'Za8p7Tf$', 'umls', charset='utf8')
    return con
