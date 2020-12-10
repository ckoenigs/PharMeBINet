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
    global g
    g = create_connection_to_databases.database_connection_neo4j()

dict_labels_to_propety_type={}

def get_label_property_type_inforamtion():
    query='''MATCH (p) WITH distinct p, keys(p) as pKeys UNWIND pKeys as Key RETURN distinct labels(p), Key, apoc.map.get(apoc.meta.cypher.types(p), Key, [true])'''
    results= g.run(query)
    for labels, node_property, property_type, in results:
        labels=tuple(labels)
        if labels not in dict_labels_to_propety_type:
            dict_labels_to_propety_type[labels]={}
        if node_property in dict_labels_to_propety_type[labels]:
            print('ohje same property but different type')
            print(node_property)
            print(labels)
        dict_labels_to_propety_type[labels][node_property]=property_type

    # print(dict_labels_to_propety_type)
    print(datetime.datetime.utcnow())

    write = shelve.open('label_to_property_type')

    for labels, dict_prop_to_type in dict_labels_to_propety_type.items():
        labels='|'.join(sorted(labels))
        write[labels]=dict_prop_to_type

    write.close()




def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('create connection')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get types')

    get_label_property_type_inforamtion()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
