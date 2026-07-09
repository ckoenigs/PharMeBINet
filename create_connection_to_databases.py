import time
import neo4j
import pymysql
from bolt import bolt

mysql_host = 'totoro.local'
mysql_user='ckoenigs'
mysql_pw='Za8p7Tf$'

# connect with the neo4j database
def database_connection_neo4j_driver() -> neo4j.Driver:

    neo4j_address = f'bolt://localhost:{bolt}'
    username = 'neo4j'
    password = 'test1234'
    retries = 0
    max_retries = 10
    success = False
    while not success:
        try:
            driver = neo4j.GraphDatabase.driver(neo4j_address, auth=(username, password))
            driver.verify_connectivity()
            success = True
        except Exception as ex:
            retries += 1
            print('Error while establishing neo4j connection, trying again in 30 seconds (%s/%s)...' % (retries, max_retries))
            if retries == max_retries:
                raise ex
            else:
                time.sleep(30)
    return driver

def mysqlconnect_bindingDB():
    # To connect MySQL database
    conn = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_pw,
        db='bindingdb',
    )
    return conn

def database_connection_RxNorm():
    conn = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_pw,
        db='rxnorm',
    )
    return conn
    # conRxNorm = mdb.connect('127.0.0.1', mysql_user, mysql_pw, 'RxNorm', charset='utf8')
    # return conRxNorm


def database_connection_umls():
    conn = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_pw,
        db='umls',
    )
    return conn
    # con = mdb.connect('127.0.0.1', mysql_user, mysql_pw, 'umls', charset='utf8')
    # return con
