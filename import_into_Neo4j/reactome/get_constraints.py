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


def get_the_constraints_and_write_into_file():
    """
    get all constraint and check if the node exists
    if so write constraint into file
    :return:
    """

    file_with_constraints = open('output/constraint.txt', 'w', encoding='utf-8')


    # version <=5.X
    query = 'SHOW INDEXES'
    results = g.run(query)
    # query = '''CALL db.indexes '''  # also possible after 4.2.x: SHOW INDEXES
    # results = g.run(query)
    indices = ''

    for record in results:
        # Call db.indexes
        # [id, name, state, populationPercent, uniqueness, type, entityType, labelsOrTypes, properties,
        #  provider] = record.values()
        print(record.values())
        [id,name,state,populationPercent,type,entityType,labelsOrTypes,properties,indexProvider,owningConstraint] = record.values()
        print(labelsOrTypes)
        if labelsOrTypes:
            for label in labelsOrTypes:
                for property in properties:
                    indices += label + suffix + '.' + property + ';'
    print(indices)


def main():
    global suffix
    if len(sys.argv) < 2:
        sys.exit('need a suffix')
    suffix = sys.argv[1]
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
