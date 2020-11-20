import time

from databaseConnection import query, generateConnection

STOP_AFTER = 50000  # so many nodes will be deleted, then will the program exit
BATCH_SIZE = 20  # how many nodes deleted per query (large BATCH-size->more memory effort)

# Note that apperently the database will not be reduced in size but instead grow due to logs (in the order of GB=> there are settings to reduce the number of logs)

# all nodelabels to delete
TODELETE = ['Summation_reactome', 'LiteratureReference_reactome']


time1 = time.time()
# db = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))
db = generateConnection()
stop = False

totalDeletes = 0

for i in TODELETE:
    if stop:
        break
    time_0 = time.time()

    # how many nodes are there to delete?
    q = 'MATCH (n:' + i + ')RETURN count(*)'
    # result = db.run(q).to_table()
    result = db.session().read_transaction(query, q)
    time_1 = time.time()
    print(result[0][0], "of type", i, ", query took", time_1 - time_0)

    # delete them
    count = result[0][0]
    if (count > 0):
        nowDel = 0
        while nowDel < count:
            if totalDeletes + nowDel > STOP_AFTER:
                stop = True
                break
            time_4 = time.time()
            q = 'MATCH (n:' + i + ') WITH n LIMIT %s DETACH DELETE n' % (BATCH_SIZE)
            db.session().read_transaction(query, q)
            nowDel += BATCH_SIZE
            time_5 = time.time()
            # print('Deleted circa', BATCH_SIZE, 'Nodes of type', i, 'of', nowDel, 'in time', time_5 - time_4)
        time_2 = time.time()
        print('CHAPTER Deleted', count, 'Nodes of type', i, "in time", time_2 - time_1)
        totalDeletes += count

time2 = time.time()
print("TotalDeletes:", totalDeletes)

timex = time.time()

print("Total time", timex - time1)
