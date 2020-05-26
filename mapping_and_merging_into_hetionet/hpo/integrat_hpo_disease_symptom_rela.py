from py2neo import Graph
import sys
import datetime, time
import csv
from _collections import defaultdict


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with neo4j database

    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# the general query start
query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%s/master_database_change/mapping_and_merging_into_hetionet/hpo/%s" As line FIELDTERMINATOR '\\t' 
    Match'''

# cypher file for mapping and integration
cypher_file = open('cypher_edge.cypher', 'w')

# list of all new disease-symptom pairs
list_new_disease_symptom_pairs = []

# dictionary disease-symptom with resource as value
dict_disease_symptom_pair_hetionet = {}

# dictionary  mapped pair to info
dict_mapped_pair_to_info = {}

# dictionary new pair to info
dict_new_pair_to_info = {}

# dictionary of aspects
dict_aspect={
    'P':'phenotypic abnormality',
    'I':'inheritance',
    'C':'onset and clinical course',
    'M':'clinical modifier'
}

# dictionary of all hpo symptoms
dict_hpo_symptom_to_info={}

def load_all_hpo_symptoms_in_dictionary():
    """
    Load all hpo symptoms for freuency infos and so on
    :return:
    """
    query='''Match (n:HPOsymptom) Return n'''
    results=g.run(query)
    for node, in results:
        identifier= node['id']
        dict_hpo_symptom_to_info[identifier]=dict(node)


def get_all_already_existing_relationships():
    """
    Get all already existing relationships from hetionet
    :return:
    """
    query = '''MATCH p=(b:Disease)-[r:PRESENTS_DpS]->(a:Symptom) RETURN  b.identifier, r.resource, a.identifier;'''
    results = g.run(query)
    for disease_id, resource, symptom_id, in results:
        dict_disease_symptom_pair_hetionet[(disease_id, symptom_id)] = resource

def prepare_all_relationships_infos(properties,connection):
    """
    prepare all relationship infos into a list, the aspects are transformed into readable values and also the frequencies
    :param properties: list of strings
    :param connection: dictionary
    :return: list of the properties
    """
    rela_properties = []
    for property in properties:
        if property not in ['frequency_modifier', 'aspect']:
            rela_properties.append(connection[property])
        elif property == 'aspect':
            if 'aspect' in connection:
                if len(connection['aspect']) > 1:
                    sys.exit('HPO mapping has multiple aspects')
                for aspect in connection['aspect']:
                    if aspect in dict_aspect:
                        rela_properties.append(dict_aspect[aspect])
                    else:
                        rela_properties.append(aspect)
            else:
                rela_properties.append('')
        elif property=='frequency_modifier':
            node = dict_hpo_symptom_to_info[connection[property]]
            rela_properties.append(node['name'])
            rela_properties.append(node['def'])
    return rela_properties

def check_for_pair_in_dictionary(mondo,symptom_id, rela_information_list , dictionary):
    '''
    check if the pair is already in dictionary or not
    if not generate pair in dictionary
    :param mondo: string
    :param symptom_id: string
    :param rela_information_list: list of strings
    :param dictionary: dictionary
    :return:
    '''
    if not (mondo, symptom_id) in dictionary:
        dictionary[(mondo, symptom_id)] = rela_information_list
    else:
        print(mondo)
        print(symptom_id)
        print(rela_information_list)
        print(dictionary[(mondo, symptom_id)])
        sys.exit('multiple information rela')

'''
generate cypher file for the disease symptom connections, but only for the pairs where hpo
has a umls cui.
'''


def generate_cypher_file_for_connection(cypher_file):
    # definition of counter
    count_new_connection = 0
    count_update_connection = 0
    counter_connection = 0

    # csv file for relationship symptom- disease
    file_rela_new = open('mapping_files/rela_new.tsv', 'w', encoding='utf-8')
    csv_rela_new = csv.writer(file_rela_new, delimiter='\t')

    file_rela_update = open('mapping_files/rela_update.tsv', 'w', encoding='utf-8')
    csv_rela_update = csv.writer(file_rela_update, delimiter='\t')

    properties = ['disease_id', 'symptom']

    # get all properties
    query = 'MATCH (n:HPOdisease)-[p:present]-(:HPOsymptom) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
    results = g.run(query)
    query_exist = ''' (n:Disease{identifier: line.disease_id})-[r:PRESENTS_DpS]-(s:Symptom{identifier:line.symptom}) Set '''
    query_new = ''' (n:Disease{identifier: line.disease_id}), (s:Symptom{identifier:line.symptom}) Create (n)-[r:PRESENTS_DpS{'''
    for result, in results:
        if result != 'frequency_modifier':

            properties.append(result)
            query_exist += 'r.' + result + '=split(line.' + result + ',"|"), '
            query_new += result + ':split(line.' + result + ',"|"), '
        else:
            for x in ['frequence_name', 'frequence_def']:
                properties.append(x)
                query_exist += 'r.' + x + '=split(line.' + x + ',"|"), '
                query_new += x + ':split(line.' + x + ',"|"), '

    csv_rela_new.writerow(properties)
    csv_rela_update.writerow(properties)
    query_exists = query_start + query_exist + "r.hpo='yes', r.version='phenotype_annotation.tab 2019-11-08', r.resource=r.resource+'HPO', r.url='http://compbio.charite.de/hpoweb/showterm?disease='+line.source; \n"
    query_exists = query_exists % (path_of_directory, "mapping_files/rela_update.tsv")
    cypher_file.write(query_exists)
    query = '''Match (n:Disease)-[r:PRESENTS_DpS]-(s:Symptom) Where r.hpo='yes SET r.resource=r.resource+'HPO';\n '''
    cypher_file.write(query)

    query_new = query_start + query_new + '''version:'phenotype_annotation.tab 2019-11-08',unbiased:'false',source:'Human Phenontype Ontology', resource:['HPO'], hpo:'yes', url:'http://compbio.charite.de/hpoweb/showterm?disease='+line.source}]->(s);\n'''
    query_new = query_new % (path_of_directory, "mapping_files/rela_new.tsv")
    cypher_file.write(query_new)

    print(properties)

    query = '''Match (d:Disease)--(:HPOdisease)-[p:present]-(:HPOsymptom)--(s:Symptom) Return d.identifier, p, s.identifier'''
    results = g.run(query)
    # fill the files
    for mondo, relationship, symptom_id, in results:
        rela_information_list=prepare_all_relationships_infos(properties,relationship)
        if (mondo, symptom_id) in dict_disease_symptom_pair_hetionet:
            check_for_pair_in_dictionary(mondo,symptom_id,rela_information_list,dict_mapped_pair_to_info)
        else:
            check_for_pair_in_dictionary(mondo,symptom_id,rela_information_list,dict_new_pair_to_info)
        # for hpo_disease_id in hpo_disease_ids:
        #     query = '''MATCH p=(:HPOdisease{id:"%s"})-[r:present]->(b) RETURN r, b.id '''
        #     query = query % (hpo_disease_id)
        #     results = g.run(query)
        #
        #     for connection, hpo_id, in results:
        #         # some hpo did not map to mesh
        #         if hpo_id in dict_hpo_to_mesh_ids:
        #             mesh_ids = dict_hpo_to_mesh_ids[hpo_id]
        #             if len(mesh_ids) > 0:
        #
        #
        #                 for mesh_id in mesh_ids:
        #
        #                     all_properties = [mondo, mesh_id]
        #                     all_properties.extend(rela_properties)
        #
        #                     if (mondo, mesh_id) in list_new_disease_symptom_pairs:
        #                         continue
        #                     elif mesh_id in dict_new_mesh_ids:
        #                         counter_connection += 1
        #                         count_new_connection += 1
        #                         csv_rela_new.writerow(all_properties)
        #                         list_new_disease_symptom_pairs.append((mondo, mesh_id))
        #                     else:
        #                         counter_connection += 1
        #                         query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
        #                         Set n.hpo='yes' Return l '''
        #                         query = query % (mondo, mesh_id)
        #                         result = g.run(query)
        #                         first_entry = result.evaluate()
        #                         # create new relationship
        #                         if first_entry == None:
        #                             csv_rela_new.writerow(all_properties)
        #                             # query = '''MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"})
        #                             # Create (n)-[:PRESENTS_DpS{version:'phenotype_annotation.tab 2019-11-08',unbiased:'false',source:'%s',qualifier:'%s', efidence_code:'%s', frequency_modifier:'%s',  resource:['HPO'],hetionet:'no',do:'no', hpo:'yes', url:"%s"}]->(s); \n '''
        #                             count_new_connection += 1
        #                             list_new_disease_symptom_pairs.append((mondo, mesh_id))
        #
        #                         else:
        #                             # query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
        #                             # Set l.hpo='yes', l.version='phenotype_annotation.tab 2017-10-09 10:47', l.source='%s', l.qualifier='%s', l.efidence_code='%s', l.frequency_modifier='%s',l.resource=["%s"], l.url="%s"; \n'''
        #                             count_update_connection += 1
        #                             csv_rela_update.writerow(all_properties)

    # query = ''' MATCH ()-[l:PRESENTS_DpS]->(s:Symptom) Where not exists(l.hpo) Set l.hpo='no'; \n '''
    # cypher_file.write(query)
    # cypher_file.write('commit \n')
    #                   ' begin \n')
    # cypher_file.write('Match (n:Disease) Where not exists(n.hpo) Set n.hpo="no"; \n')
    # cypher_file.write('commit')

    print('number of new connection:' + str(count_new_connection))
    print('number of update connection:' + str(count_update_connection))
    print(counter_connection)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in hpo symptoms')

    load_all_hpo_symptoms_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all existing relationships')

    get_all_already_existing_relationships()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship information into a cypher file')

    generate_cypher_file_for_connection(cypher_file)

    print('##########################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()
