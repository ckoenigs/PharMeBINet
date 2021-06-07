import time
import sys
from databaseConnection import query, generateConnection

STOP_AFTER = 50000  # so many nodes will be deleted, then will the program exit

STOP_AFTER_RELA = 3000000

# dictionary label to list [is_index (True, false), ... ] ..=  property (index) else ..= constraint name
dict_label_to_index_constraint_infos = {}

# Note that apperently the database will not be reduced in size but instead grow due to logs (in the order of GB=> there
# are settings to reduce the number of logs)

# all node source to delete
TODELETE = {'sider', 'ctd', 'ndfrt', 'aeolus', 'drugbank', 'ncbi', 'efo', 'hpo', 'uniprot', 'multi', 'go', 'dc',
            'diseaseontology', 'mondo', 'clinvar', 'omim', 'reactome', 'adrecstarget', 'iid', 'medrt', 'pharmgkb'}

# dictionary label to batch size
dict_label_to_batch_size = {
    'CTD_chemical': '125',
    'DatabaseObject_reactome': '125'
}

# dictionary where first relationships are delete
dict_label_to_batch_size_rela = {

    'CTD_disease': '10000',
    'CTD_gene': '50000'
}

time1 = time.time()
# db = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))
db = generateConnection()
stop = False

# preparation for remove index/constraints
q = 'CALL db.indexes;'
results = db.session().read_transaction(query, q)

for index_id, name, state, populationPercent, uniqueness, index_type, entityType, labelsOrTypes, properties, provider in results:
    label = labelsOrTypes[0]
    if name.startswith('constraint'):
        infos = [False, name]
    else:
        infos = [True, properties[0]]
    if label not in dict_label_to_index_constraint_infos:
        dict_label_to_index_constraint_infos[label] = []
    dict_label_to_index_constraint_infos[label].append(infos)

query_remove_index = 'Drop Index On :%s(%s)'
query_remove_constraint_with_constraint_name = 'DROP CONSTRAINT %s'

# start of delete nodes and indices/constraints
totalDeletes = 0

q = 'call db.labels();'
results = db.session().read_transaction(query, q)

# all not removed labels
not_removed = set()
# all removed labels
removed_labels = set()

for label in results:
    time_0 = time.time()
    label = label[0]
    # print(label)
    if label[0].isupper():
        splitted = label.lower().split('_')
        if len(splitted) == 1:
            not_removed.add(label)
            continue
        intersection = TODELETE.intersection(splitted)
        if len(intersection) == 0:
            print('has a _ but no source?')
            print(label)
            not_removed.add(label)
            continue
        else:
            print('multiple _ but not a source?')
            # continue
    print(label)
    removed_labels.add(label)

    # how many nodes are there to delete?
    q = 'MATCH (n:' + label + ')RETURN count(*)'
    # result = db.run(q).to_table()
    result = db.session().read_transaction(query, q)
    time_1 = time.time()
    print(result[0][0], "of type", label, ", query took", time_1 - time_0)

    # delete them
    count = result[0][0]
    if count > 0:
        time_4 = time.time()
        if label in dict_label_to_batch_size:
            nowDel = 0
            while nowDel < count:
                if totalDeletes + nowDel > STOP_AFTER:
                    stop = True
                    break
                time_4 = time.time()
                q = 'MATCH (n:%s) WITH n LIMIT %s DETACH DELETE n' % (label, dict_label_to_batch_size[label])
                db.session().write_transaction(query, q)
                nowDel += int(dict_label_to_batch_size[label])
                time_5 = time.time()
            # batch=dict_label_to_batch_size[label]
            time_2 = time.time()
            print('CHAPTER Deleted', nowDel, 'Nodes of type', label, "in time", time_2 - time_1)
            totalDeletes += count
        elif label in dict_label_to_batch_size_rela:
            # if label in ['CTD_disease']: # , 'CTD_gene'
            #     continue
            q = 'MATCH p=(n:' + label + ')--() RETURN count(p)'
            # result = db.run(q).to_table()
            result = db.session().read_transaction(query, q)
            time_1 = time.time()
            print(result[0][0], "of rela from ", label, ", query took", time_1 - time_0)
            # if label == 'CTD_disease':
            #     continue
            # delete them
            count_rela = result[0][0]
            rela_batch = dict_label_to_batch_size_rela[label]
            rela_delete = 0

            nowDel = 0
            while nowDel < count_rela:
                if nowDel > STOP_AFTER_RELA:
                    stop = True
                    break
                time_4 = time.time()
                q = 'MATCH (n:%s)-[r]-() WITH r LIMIT %s DETACH DELETE r' % (label, rela_batch)
                db.session().write_transaction(query, q)
                nowDel += int(dict_label_to_batch_size_rela[label])
                time_5 = time.time()
            # while (rela_delete<count)
            if not stop:
                batch = '200'
                q = "CALL apoc.periodic.iterate('MATCH (n:%s) RETURN n', 'DETACH DELETE n', {batchSize:%s})" % (
                    label, batch)
                db.session().write_transaction(query, q)
                time_5 = time.time()
                # print('Deleted circa', BATCH_SIZE, 'Nodes of type', i, 'of', nowDel, 'in time', time_5 - time_4)
                time_2 = time.time()
                print('CHAPTER Deleted', count, 'Nodes of type', label, "in time", time_2 - time_1)
                totalDeletes += count
        else:
            batch = '200'
            q = "CALL apoc.periodic.iterate('MATCH (n:%s) RETURN n', 'DETACH DELETE n', {batchSize:%s})" % (
            label, batch)
            print(q)
            db.session().write_transaction(query, q)
            time_5 = time.time()
            # print('Deleted circa', BATCH_SIZE, 'Nodes of type', i, 'of', nowDel, 'in time', time_5 - time_4)
            time_2 = time.time()
            print('CHAPTER Deleted', count, 'Nodes of type', label, "in time", time_2 - time_1)
            totalDeletes += count
    if label in dict_label_to_index_constraint_infos:
        for [is_index, name_property] in dict_label_to_index_constraint_infos[label]:
            if is_index:
                q = query_remove_index % (label, name_property)
            else:
                q = query_remove_constraint_with_constraint_name % name_property
            db.session().write_transaction(query, q)
    if totalDeletes > STOP_AFTER or stop:
        break

time2 = time.time()
print("TotalDeleltes:", totalDeletes)

timex = time.time()
print(not_removed)
print('removed labels:', removed_labels)

print("Total time", timex - time1)
