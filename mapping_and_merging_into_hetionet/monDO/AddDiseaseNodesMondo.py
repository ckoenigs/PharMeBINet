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


# mondo properties
mondo_prop = []

# set of excluded mondo ids which are not human ids
set_of_non_human_ids = set()


def get_all_non_human_ids():
    """
    Get all non human disease (MONDO:0005583) nodes and add them to a set
    :return:
    """
    # disease with id MONDO:0005583  is "non-human animal disease" nearly all are only animal disease, but I found out
    # that the one with DOID are animal disease which a human can also have.
    query = '''Match p=(n:disease{id:'MONDO:0005583'})<-[:is_a*]-(a:disease)  Where Not ANY(x in a.xrefs Where x starts with 'DOID') Return Distinct a.id '''
    set_of_non_human_ids.add('MONDO:0005583')
    print(query)
    results = g.run(query)
    for record in results:
        [identifier] = record.values()
        set_of_non_human_ids.add(identifier)


# list of excluded properties from mondo
list_exclude_properties = ['related', 'creation_date', 'created_by', 'seeAlso']

'''
Get all properties of the mondo disease and create the tsv files
'''


def get_mondo_properties_and_generate_csv_files():
    query = '''MATCH (n:disease) Where n.is_obsolete is NULL WITH DISTINCT keys(n) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''
    result = g.run(query)
    for property in result:
        mondo_prop.append(property.data()['allfields'])

    # mondo get an additional property
    mondo_prop.append('umls_cuis')

    # generate tsv files
    global tsv_new_nodes, tsv_map_nodes, tsv_rela
    # tsv with new nodes
    new_node_file = open('output/new_nodes.tsv', 'w', encoding='utf-8')
    tsv_new_nodes = csv.DictWriter(new_node_file, delimiter='\t', fieldnames=mondo_prop)
    tsv_new_nodes.writeheader()

    # tsv with relatioships
    rela_file = open('output/rela.tsv', 'w', encoding='utf-8')
    tsv_rela = csv.writer(rela_file, delimiter='\t')
    tsv_rela.writerow(['id_1', 'id_2'])


'''
This get an dictionary and preperate this that it can be integrated into the tsv file
'''


def prepare_dict_for_csv_file(info):
    # dictionary of the integrated information
    dict_info_csv = {}

    for key, property in info.items():

        # if key in list_properties_which_should_be_an_array:
        if type(property) == list:
            list_of_list_prop.add(key)
            property_string = '|'.join(property)
            dict_info_csv[key] = property_string

            if len(property) > 0 and type(property[0]) == int:
                print('int list')
                print(property)
        else:
            # query = query + ''' n.%s="%s",'''
            # query = query % (key, property)
            if type(property) == int:
                print('int')
                print(key)
            dict_info_csv[key] = property
    return dict_info_csv



'''
Load MonDO disease in dictionary
Where n.`http://www.geneontology.org/formats/oboInOwl#id` ='MONDO:0010168'
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:disease) Where n.is_obsolete is NULL and n.id starts with "MONDO" RETURN n'''
    results = g.run(query)
    for record in results:
        disease = record.data()['n']
        monDo_id = disease['id']
        if monDo_id in set_of_non_human_ids:
            continue
        if len(disease['names'])>1:
            sys.exit('multiple names')
        disease_info = dict(disease)
        xrefs = disease_info['xrefs'] if 'xrefs' in disease_info else []
        xrefs.append(monDo_id)
        xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, 'disease')
        disease_info['xrefs']=xrefs
        tsv_new_nodes.writerow(prepare_dict_for_csv_file(disease_info))



# cypher file to integrate mondo
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')


# cypher file to integrate mondo
cypher_file_rela = open('output/cypher_rela.cypher', 'w', encoding='utf-8')


# list_properties in mondo
list_of_list_prop = set([])

'''
generate cypher queries to integrate and merge disease nodes and create the subclass relationships
'''


def generate_cypher_queries():
    query_start = ''' Match (a:disease{id:line.id}) '''

    query_end = '''Create (n)-[:equal_to_monDO]->(a)'''
    query_new = ''
    for property in mondo_prop:
        if property not in list_of_list_prop:
            if property in ['created_by', 'subsets']:
                continue
            if property == 'iri':
                query_new += 'url:line.' + property + ', '
                continue
            if property == 'id':
                query_new += 'identifier:line.' + property + ', '
                continue
            if property == 'def':
                query_new += 'definition:line.' + property + ', '
                continue

            query_new += property + ':line.' + property + ', '
        else:
            if property == 'alt_ids':
                query_new += 'alternative_ids:split(line.' + property + ', "|"), '
                continue
            if property == 'names':
                query_new += 'name:line.' + property + ', '
                continue
            query_new += property + ':split(line.' + property + ', "|"), '

    query_new = query_start + 'Create (n:Disease :Phenotype{' + query_new + 'mondo:"yes", resource:["MonDO"], url:"https://monarchinitiative.org/disease/"+ line.id , license:"CC-BY-SA 3.0", source:"MonDO"}) ' + query_end
    query_new = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/monDO/output/new_nodes.tsv',
                                                  query_new)
    cypher_file.write(pharmebinetutils.prepare_index_query("Disease","identifier"))
    cypher_file.write(pharmebinetutils.prepare_index_query_text('Disease', 'name'))
    cypher_file.write(pharmebinetutils.prepare_index_query("Phenotype","identifier"))
    cypher_file.write(pharmebinetutils.prepare_index_query_text('Phenotype', 'name'))
    cypher_file.write(query_new)

    cypher_file.close()
    query_rela = ''' Match (a:Disease{identifier:line.id_1}),(b:Disease{identifier:line.id_2}) Create (a)-[r:IS_A_DiaD{ unbiased:false, url:"https://monarchinitiative.org/disease/"+ line.id_1,  source:"Monarch Disease Ontology", resource:['MonDO'] , mondo:'yes', license:"CC-BY-SA 3.0"}]->(b) '''
    query_rela = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/monDO/output/rela.tsv',
                                                   query_rela)
    cypher_file_rela.write(query_rela)
    cypher_file_rela.close()






'''
add the rela information into
'''


def generate_csv_file_for_relationship():
    # query to get the rela information
    query = ''' Match (a:disease)-[r:is_a]->(b:disease) Return a.id, b.id'''
    results = g.run(query)

    # counter of relationship
    counter_of_relationships = 0

    # go through all rela and add the information into the tsv file
    for record in results:
        [child_id, parent_id] = record.values()
        counter_of_relationships += 1
        tsv_rela.writerow([child_id, parent_id])

    print('number of relationships:' + str(counter_of_relationships))


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
    print('generate list of non human disease')

    get_all_non_human_ids()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all properties from mondo and put them as header into the tsv files ')

    get_mondo_properties_and_generate_csv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate cypher file')

    generate_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate cypher file for subclassof relationship  ')

    generate_csv_file_for_relationship()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
