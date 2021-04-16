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


def get_the_constraints_and_write_into_file():
    """
    get all constraint and check if the node exists
    if so write constraint into file
    :return:
    """
    query = '''CALL db.constraints'''

    file_with_constraints = open('output/constraint.txt', 'w', encoding='utf-8')
    results = g.run(query)
    # version 4.0.3
    # for index_name, description, in results:
    # version 4.2.5
    for index_name, description, details,  in results:
        splitted = description.split(':')
        label = splitted[1].split(' )')[0]
        query = "Match (n:%s) Return n Limit 1;" % (label)
        count_result = g.run(query)
        has_result = count_result.evaluate()
        if has_result is not None:
            print(label)
            print(has_result)
            file_with_constraints.write(description+'\n')
    file_with_constraints.close()

    query='''CALL db.indexes ''' # also possible after 4.2.x: SHOW INDEXES
    results= g.run(query)
    indices=''

    for id, name, state, populationPercent, uniqueness, type, entityType, labelsOrTypes, properties, provider, in results:
        for label in labelsOrTypes:
            for property in properties:
                indices+=label+suffix+'.'+property+';'
    print(indices)



def main():
    global suffix
    if len(sys.argv)<2:
        sys.exit('need a suffix')
    suffix=sys.argv[1]
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('create connection')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get constraints')

    get_the_constraints_and_write_into_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
