from py2neo import Graph, authenticate
import sys
import datetime


# connect with the neo4j database
def database_connection():

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

'''
load all information for one id
'''
def load_information_from_neo4j_for_one_id(id, label):
    query='''Match (b:%s {identifier:'%s'}) Return b;''' %(label,id)
    results= g.run(query)
    if results:
        for result, in results:
            output=dict(result)
            return output

    else:
        print('identifier %s or label %s are not ok' %(id,label))

'''
compare both dictionaries with each other 
'''
def compare_both_nodes(dict_1, dict_2):
    dict_properties={}
    # first check on the properties on dictionary on if the have the same properties
    for property, value in dict_1.items():
        dict_properties[property]=1
        if property in dict_2:
            if dict_2[property]!= value:
                print('For property '+property+' are the values not the same')
                print('for node 1:')
                print(value)
                print('For node 2:')
                print(dict_2[property])
        else:
            print('The property '+property+' is not existing in node 2')

    # now check if the second one has some properties which node 1 not has.
    for property in dict_2.keys():
        if property not in dict_properties:
            print('The property ' + property + ' is not existing in node 1')
            dict_properties[property]=1
        else:
            dict_properties[property]+=1


'''
the method
'''
def main():
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather the parameters')

    if len(sys.argv) != 4:
        sys.exit('the programm need a label, ID1 and ID2 to compare')

    label = sys.argv[1]
    id1 = sys.argv[2]
    id2 = sys.argv[3]

    print('node 1:'+id1)
    print('node 2:'+id2)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connect to neo4j')

    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get information from neo4j')


    dict_id1=load_information_from_neo4j_for_one_id(id1, label)
    dict_id2 = load_information_from_neo4j_for_one_id(id2, label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('compare the information')


    compare_both_nodes(dict_id1,dict_id2)


    print('##########################################################################')

    print(datetime.datetime.utcnow())

if __name__ == "__main__":
    # execute only if run as a script
    main()