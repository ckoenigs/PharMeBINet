
import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# list of all side effect ids which are in hetionet
list_side_effect_in_hetionet = []

# dictionary with all side effects from hetionet and the new ones from sider
#  with id as key and as value a class SideEffect
dict_all_side_effect = {}

# header for file
header = ["name", "identifier", "meddraType", "conceptName"]

# tsv for new se
file_new_node = open('output/se_new.tsv', 'w')
csv_writer_new = csv.DictWriter(file_new_node, delimiter='\t', fieldnames=header)
csv_writer_new.writeheader()

'''
load all new and old information for side effects in
meddraType: string (PT or LLT)
conceptName: string
umlsIDmeddra: string (UMLS CUI for MedDRA ID)
name: string
umls_concept_id: string (UMLS CUI for label)
'''


def load_sider_in_dict():
    query = '''MATCH (n:se_Sider) RETURN n '''
    results = g.run(query)
    k = 0
    counter_new = 0
    for result, in results:
        k += 1
        meddraType = result['meddraType']
        conceptName = result['conceptName']
        umlsIDmeddra = result['umlsIDmeddra']
        name = result['name']

        dict_info = {"name": name, "identifier": umlsIDmeddra, "meddraType": meddraType, "conceptName": conceptName}
        csv_writer_new.writerow(dict_info)
        counter_new += 1

    print('size of side effects after the sider is add:' + str(len(list_side_effect_in_hetionet) + counter_new))


'''
Generate cypher file for side effect nodes
'''


def generate_cypher_file():
    cypher_file = open('output/cypher.cypher', 'w')
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/sider/output/%s.tsv" As line FIELDTERMINATOR '\\t' '''
    query_new = ''
    for head in header:
        query_new += head + ':line.' + head + ', '
    query_new = query_start + ' Match (b:se_Sider{umlsIDmeddra:line.identifier}) Create (n:SideEffect{' + query_new + ' sider:"yes", url:"http://identifiers.org/umls/"+line.identifier, resource:["SIDER"],  source: "UMLS via SIDER 4.1", license:"CC BY-NC-SA 4.0"}) Create (n)-[:equal_to_SE]->(b);\n'
    query_new = query_new % ('se_new')
    cypher_file.write(query_new)
    cypher_file.close()



'''
this start only the function the are use for generate the map cypher
'''


def integrate_side_effects():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path sider se')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in all side effect from sider in dictionary')

    load_sider_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('map sider to hetionet per cypher')

    generate_cypher_file()

    print(
        '###########################################################################################################################')


def main():
    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate sider side effects into hetionet')

    integrate_side_effects()


if __name__ == "__main__":
    # execute only if run as a script
    main()
