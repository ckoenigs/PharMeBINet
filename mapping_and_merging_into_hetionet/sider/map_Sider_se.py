import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    # create connection to neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# list of all side effect ids which are in pharmebinet
list_side_effect_in_pharmebinet = []

# dictionary with all side effects from pharmebinet and the new ones from sider
#  with id as key and as value a class SideEffect
dict_all_side_effect = {}

# header for file
header = ["name", "identifier", "meddraType", "conceptName"]

# tsv for new se
file_new_node = open('output/se_new.tsv', 'w')
csv_writer_new = csv.DictWriter(file_new_node, delimiter='\t', fieldnames=header)
csv_writer_new.writeheader()


def load_sider_in_dict():
    """
    load all new and old information for side effects in
    meddraType: string (PT or LLT)
    conceptName: string
    umlsIDmeddra: string (UMLS CUI for MedDRA ID)
    name: string
    umls_concept_id: string (UMLS CUI for label)
    :return:
    """
    query = '''MATCH (n:se_Sider) RETURN n '''
    results = g.run(query)
    k = 0
    counter_new = 0
    for record in results:
        result = record.data()['n']
        k += 1
        meddraType = result['meddraType'] if 'meddraType' in result else ''
        conceptName = result['conceptName'] if 'conceptName' in result else ''
        umlsIDmeddra = result['umlsIDmeddra']
        name = result['name']

        dict_info = {"name": name, "identifier": umlsIDmeddra, "meddraType": meddraType, "conceptName": conceptName}
        csv_writer_new.writerow(dict_info)
        counter_new += 1

    print('size of side effects after the sider is add:' + str(len(list_side_effect_in_pharmebinet) + counter_new))


def generate_cypher_file():
    # Generate cypher file for side effect nodes
    cypher_file = open('output/cypher.cypher', 'w')
    query_new = ''
    for head in header:
        if head == 'conceptName':
            continue
            query_new += 'synonyms:[line.' + head + '], '
        query_new += head + ':line.' + head + ', '
    query_new = ' Match (b:se_Sider{umlsIDmeddra:line.identifier}) Create (n:SideEffect{' + query_new + ' sider:"yes", url:"http://identifiers.org/umls/"+line.identifier, resource:["SIDER"],  source: "UMLS via SIDER 4.1", license:"CC BY-NC-SA 4.0"}) Create (n)-[:equal_to_SE]->(b)'
    query_new = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/sider/output/se_new.tsv',
                                                  query_new)
    cypher_file.write(query_new)
    query_new = ' Match   (n:SideEffect{identifier:line.identifier}) Where line.conceptName is not NULL Set n.synonyms=[line.conceptName]'
    query_new = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/sider/output/se_new.tsv',
                                                  query_new)
    cypher_file.write(query_new)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path sider se')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all side effect from sider in dictionary')

    load_sider_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map sider to pharmebinet per cypher')

    generate_cypher_file()

    print(
        '###########################################################################################################################')

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
