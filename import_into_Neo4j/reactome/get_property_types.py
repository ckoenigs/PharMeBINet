import sys
import datetime
import shelve

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


dict_labels_to_propety_type = {}


def get_label_property_type_inforamtion():
    query = '''MATCH (p) WITH distinct p, keys(p) as pKeys UNWIND pKeys as Key RETURN distinct labels(p), Key, apoc.map.get(apoc.meta.cypher.types(p), Key, [true])'''
    results = g.run(query)
    for record in results:
        [labels, node_property, property_type] = record.values()
        labels = tuple(labels)
        if labels not in dict_labels_to_propety_type:
            dict_labels_to_propety_type[labels] = {}
        if node_property in dict_labels_to_propety_type[labels]:
            print('ohje same property but different type')
            print(node_property)
            print(labels)
        dict_labels_to_propety_type[labels][node_property] = property_type

    # print(dict_labels_to_propety_type)
    print(datetime.datetime.now())

    write = shelve.open('label_to_property_type')

    for labels, dict_prop_to_type in dict_labels_to_propety_type.items():
        labels = '|'.join(sorted(labels))
        write[labels] = dict_prop_to_type

    write.close()


def main():
    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get types')

    get_label_property_type_inforamtion()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
