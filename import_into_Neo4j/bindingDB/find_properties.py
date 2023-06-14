import pymysql
from itertools import combinations


def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password="password",
        db='BindingDB',
    )
    cursor = conn.cursor()
    return cursor


def create_dict(keys, values):
    pair_list = []
    for i in range(len(keys)):
        pair_list.append((keys[i], values[i]))
    d = {k:v for (k,v) in pair_list}
    return d


def find_intersection(tuple):
    list1 = tuple[0]
    list2 = tuple[1]
    l = list(set(list1).intersection(list2))
    return l


def get_pairs(elements):
    pairs = list(combinations(elements, 2))
    return pairs


def get_lists_to_compare(pair, dict):
    l1 = dict.get(pair[0])
    l2 = dict.get(pair[1])
    res = (l1, l2)
    return res


def properties_in_common(pairs, dict):
    res = {}
    for pair in pairs:
        tpl = get_lists_to_compare(pair, dict)
        l = find_intersection(tpl)
        if len(l) > 0:
            res.update({pair: l})
    return res


if __name__ == "__main__":
    cur = mysqlconnect()
    cur.execute("SHOW TABLES")
    output = cur.fetchall()
    tables = []
    properties = []
    for i in output:
        tables.append(i[0])
    directory = "tsv_from_mysql/"
    for table in tables:
        query ="SHOW COLUMNS FROM " + table
        cur.execute(query)
        output = cur.fetchall()
        tab_property = []
        for i in output:
            tab_property.append(i[0])
        properties.append(tab_property)
    dic = create_dict(tables, properties)
    pairs_to_compare = get_pairs(tables)
    l = properties_in_common(pairs_to_compare, dic)
    for key, value in l.items():
        print(str(key) + ': ' + str(value))





