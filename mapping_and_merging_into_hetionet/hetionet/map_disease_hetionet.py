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


'''
Get all properties of the mondo disease and create the tsv files
'''


def get_mondo_properties_and_generate_csv_files():

    # generate tsv files
    global  tsv_map_nodes

    # tsv with nodes which needs to be updated
    map_node_file = open('output/map_nodes.tsv', 'w', encoding='utf-8')
    tsv_map_nodes = csv.writer(map_node_file, delimiter='\t')
    tsv_map_nodes.writerow(['id','doid','how_mapped'])




# dictionary mondo id to mondo name
dict_mondo_id_to_name = {}


'''
generate cypher queries to integrate and merge disease nodes and create the subclass relationships
'''


def generate_cypher_queries():
    # cypher file to integrate mondo
    with open('output/cypher.cypher', 'a', encoding='utf-8') as cypher_file:
        query = ''' Match (a:Disease_hetionet{identifier:line.doid}), (b:Disease{identifier:line.id}) Create (b)-[:equal_to_hetionet_disease{how_mapped:line.how_mapped}]->(a) '''

        query= pharmebinetutils.get_query_import(path_of_directory,'mapping_and_merging_into_hetionet/hetionet/output/map_nodes.tsv',query)
        cypher_file.write(query)

# dictionary mondo to resource
dict_mondo_to_resource={}

# dictionary doid to mondo
dict_doid_to_mondo ={}


# dictionary name to mondo
dict_name_to_mondo ={}

'''
Load in all disease ontology ids with external identifier and alternative id
also check for mapping between do and mondo
'''


def load_in_all_disease_in_dictionary():
    """
    Load all disease from PharMeBINet
    :return:
    """
    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for record in results:
        disease = record.data()['n']
        mondo_id = disease['identifier']
        dict_mondo_to_resource[mondo_id]=set(disease['resource'])

        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        for xref in xrefs:
            if xref.startswith('DOID:'):
                pharmebinetutils.add_entry_to_dict_to_set(dict_doid_to_mondo, xref, mondo_id)

        name = disease['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_mondo, name, mondo_id)


def mapping_hetionet_disease():
    query= 'MATCH (n:Disease_hetionet) RETURN n'
    results = g.run(query)
    counter=0
    counter_mapped=0
    for record in results:
        counter+=1
        disease = record.data()['n']
        doid=disease['identifier']
        name= disease['name'].lower()

        is_mapped=False

        if doid in dict_doid_to_mondo:
            for mondo_id in dict_doid_to_mondo[doid]:
                is_mapped=True
                tsv_map_nodes.writerow([mondo_id,doid,'DOID'])

        if is_mapped:
            counter_mapped+=1
            continue

        if name in dict_name_to_mondo:
            for mondo_id in dict_name_to_mondo[name]:
                is_mapped = True
                tsv_map_nodes.writerow([mondo_id, doid, 'name'])

        if is_mapped:
            counter_mapped += 1
            continue

    print('all hetionet disease:', counter)
    print('mapped:',counter_mapped)



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

    get_mondo_properties_and_generate_csv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate cypher file')

    generate_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load disease')

    load_in_all_disease_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('map disease')

    mapping_hetionet_disease()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
