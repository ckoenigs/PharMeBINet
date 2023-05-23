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
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def get_the_constraints_and_write_into_file():
    """
    get all constraint and check if the node exists
    if so write constraint into file
    :return:
    """
    shell_file = open('shell_import_pharmebinet.sh', 'w', encoding='utf-8')
    shell_file.write(''' # define import tool
import_tool=$1
# define path to pharmebinet
path_to_pharmebinet=$2\n\n''')

    import_tool = 'java -jar $import_tool.jar -i $path_to_pharmebinet"PharMeBiNet_finished.graphml"  -e bolt://localhost:7687 --username neo4j --password test1234  --modify-edge-labels false --indices "%s"'

    query = 'SHOW INDEXES'
    results = g.run(query)
    list_indices = []
    for record in results:
        [id, name, state, populationPercent, type, entityType, labelsOrTypes, properties, indexProvider,
         owningConstraint] = record.values()
        if labelsOrTypes:
            for label in labelsOrTypes:
                if '_' in label or not label[0].isupper():
                    continue
                print(label)
                for prop in properties:
                    if prop not in ['identifier', 'name']:
                        print(label, prop)
                        sys.exit('mysteries label without identifier :Onx8Q7U9g'
                                 '')

                    list_indices.append(label + '.' + prop)
    import_tool = import_tool % (';'.join(list_indices))
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

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
