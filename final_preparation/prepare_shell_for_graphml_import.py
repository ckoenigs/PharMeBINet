import sys
import datetime

sys.path.append("..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()



def get_the_constraints_and_write_into_file():
    """
    get all constraint and check if the node exists
    if so write constraint into file
    :return:
    """
    shell_file=open('shell_import_pharmebinet.sh','w', encoding='utf-8')
    shell_file.write(''' # define import tool
import_tool=$1
# define path to pharmebinet
path_to_pharmebinet=$2\n\n''')

    import_tool='java -jar $import_tool.jar -i $path_to_pharmebinet"PharMeBiNet_finished.graphml"  -e bolt://localhost:7687 --username neo4j --password test  --modify-edge-labels false --indices "%s"'

    query='''CALL db.indexes ''' # also possible after 4.2.x: SHOW INDEXES
    results= g.run(query)
    list_indices=[]
    for id, name, state, populationPercent, uniqueness, type, entityType, labelsOrTypes, properties, provider, in results:
        for label in labelsOrTypes:
            if '_' in label or not label[0].isupper():
                continue
            print(label)
            for property in properties:
                list_indices.append(label+'.'+property)
    import_tool= import_tool %(';'.join(list_indices))
    shell_file.write(import_tool)
    



def main():
    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get constraints')

    get_the_constraints_and_write_into_file()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
