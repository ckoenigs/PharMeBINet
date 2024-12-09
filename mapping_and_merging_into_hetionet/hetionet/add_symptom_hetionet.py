import sys, csv
import datetime

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def database_connection():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def generate_csv_files():
    """
    Generate TSV file for new added nodes
    :return:
    """
    # generate tsv files
    global tsv_map_nodes

    # tsv with nodes which needs to be updated
    map_node_file = open('output/symptoms.tsv', 'w', encoding='utf-8')
    tsv_map_nodes = csv.writer(map_node_file, delimiter='\t')
    tsv_map_nodes.writerow(['id'])


# dictionary mondo id to mondo name
dict_mondo_id_to_name = {}

'''
generate cypher queries to integrate and merge symptom nodes and create the subclass relationships
'''


def generate_cypher_queries():
    # cypher file to integrate mondo
    with open('output/cypher.cypher', 'a', encoding='utf-8') as cypher_file:

        query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys
                    UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
                    RETURN allfields as l;''' % ("Symptom_hetionet")
        result = g.run(query)
        query = ''' Match (a:Symptom_hetionet{identifier:line.id}) Create (b:Symptom{identifier:line.id, hetionet:"yes", resource:["Hetionet"], source:"MeSH via Hetionet", %s}) Create (b)-[:equal_to_hetionet_symptom]->(a) '''
        list_prop = []
        for record in result:
            prop = record.data()['l']
            if not prop in ['identifier', 'source']:
                list_prop.append(f'{prop}:a.{prop}')

        query = query % (", ".join(list_prop))
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  'mapping_and_merging_into_hetionet/hetionet/output/symptoms.tsv',
                                                  query)
        cypher_file.write(query)
        cypher_file.write(pharmebinetutils.prepare_index_query('Symptom', 'identifier'))
        cypher_file.write(pharmebinetutils.prepare_index_query_text('Symptom', 'name'))
        cypher_file.close()


def mapping_hetionet_symptom():
    query = 'MATCH (n:Symptom_hetionet) RETURN n.identifier'
    results = g.run(query)
    for record in results:
        [identifier] = record.values()

        tsv_map_nodes.writerow([identifier])


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all properties from mondo and put them as header into the tsv files ')

    generate_csv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate cypher file')

    generate_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare symptom')

    mapping_hetionet_symptom()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
