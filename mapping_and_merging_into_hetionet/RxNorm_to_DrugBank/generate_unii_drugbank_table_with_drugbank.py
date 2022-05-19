import datetime
import sys, csv
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

'''
generate af file with only drugbank and unii IDs
'''

def generate_tsv_file():
    # generate csv file
    file_map = open('results/map_unii_to_drugbank_id_and_inchikey.tsv', 'w', encoding='utf-8')
    csv_writer=csv.writer(file_map,delimiter='\t')
    csv_writer.writerow(['unii','drugbank_id','inchikey'])

    # query for getting the information
    query='''MATCH (n:Compound_DrugBank) RETURN n.identifier, n.unii, n.inchikey '''
    result=g.run(query)

    # run through the results and fill file
    for  identifier, unii, inchikey, in result:
        csv_writer.writerow([unii,identifier, inchikey])

    # file map close
    file_map.close()



def main():

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all properties of compound and drugbank compound and use the information to genreate tsv files')

    generate_tsv_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
