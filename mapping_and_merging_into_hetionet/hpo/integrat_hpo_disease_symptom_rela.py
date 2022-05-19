import sys
import datetime
import csv

sys.path.append("../..")
import create_connection_to_databases


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with neo4j database

    global g
    g = create_connection_to_databases.database_connection_neo4j()


# the general query start
query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/hpo/%s" As line FIELDTERMINATOR '\\t' 
    Match'''

# cypher file for mapping and integration
cypher_file = open('cypher/cypher_edge.cypher', 'w')

# list of all new disease-symptom pairs
list_new_disease_symptom_pairs = []

# dictionary disease-symptom with resource as value
dict_disease_symptom_pair_hetionet = {}

# dictionary  mapped pair to info
dict_mapped_pair_to_info = {}

# dictionary new pair to info
dict_new_pair_to_info = {}

# dictionary of aspects
dict_aspect = {
    'P': 'phenotypic abnormality',
    'I': 'inheritance',
    'C': 'onset and clinical course',
    'M': 'clinical modifier'
}

# dictionary evidence
dict_evidence = {
    'IEA': 'inferred from electronic annotation',
    'PCS': 'published clinical study',
    'TAS': 'traceable author statement'
}

# dictionary of all hpo symptoms
dict_hpo_symptom_to_info = {}


def load_all_hpo_symptoms_in_dictionary():
    """
    Load all hpo symptoms for freuency infos and so on
    :return:
    """
    query = '''Match (n:HPO_symptom) Return n'''
    results = g.run(query)
    for node, in results:
        identifier = node['id']
        dict_hpo_symptom_to_info[identifier] = dict(node)


def change_list_values_to_string(list_of_values):
    """
    change list or ste values to string to have a list of string
    :param list_of_values: list of string/list/set
    :return:  list of string
    """
    new_list_value = []
    for value in list_of_values:
        if type(value) in [list, set]:
            value = "|".join(value)
        new_list_value.append(value)
    return new_list_value


def get_all_already_existing_relationships():
    """
    Get all already existing relationships from hetionet
    :return:
    """
    query = '''MATCH p=(b:Disease)-[r:PRESENTS_DpS]->(a:Symptom) RETURN  b.identifier, r.resource, a.identifier;'''
    results = g.run(query)
    for disease_id, resource, symptom_id, in results:
        dict_disease_symptom_pair_hetionet[(disease_id, symptom_id)] = resource


def prepare_all_relationships_infos(properties, connection, mondo_id, symptom_id):
    """
    prepare all relationship infos into a list, the aspects are transformed into readable values and also the frequencies
    :param properties: list of strings
    :param connection: dictionary
    :param mondo_id: string
    :param symptom_id: string
    :return: list of the properties
    """
    rela_properties = [mondo_id, symptom_id]
    sources = ';'.join(connection['sources'])

    for property in properties[2:]:
        if property not in ['frequency_name', 'aspect', 'frequency_def', 'evidence_code', 'onset', 'modifier']:
            rela_properties.append(connection[property])
        elif property == 'evidence_code':
            if 'evidence_code' in connection:
                rela_properties.append([dict_evidence[x] for x in connection[property]])

        elif property == 'aspect':
            if 'aspect' in connection:
                if len(connection['aspect']) > 1:
                    sys.exit('HPO mapping has multiple aspects')
                # it should be every time one long
                for aspect in connection['aspect']:
                    if aspect in dict_aspect:
                        rela_properties.append(dict_aspect[aspect])
                    else:
                        rela_properties.append(aspect)
            else:
                rela_properties.append('')
        elif property in ['onset', 'modifier']:
            hpos = connection[property] if property in connection else []
            onsets = []
            for hpo in hpos:
                if hpo in dict_hpo_symptom_to_info:
                    node = dict_hpo_symptom_to_info[hpo]
                    onsets.append(node['name'])
                else:
                    sys.exit('onset or what ever')
            rela_properties.append('|'.join(onsets))


        elif property == 'frequency_name':
            if 'frequency_modifier' in connection:
                hpos = connection['frequency_modifier']
                frequencies = []
                def_frequencies = []
                for hpo in hpos:
                    if hpo in dict_hpo_symptom_to_info:
                        node = dict_hpo_symptom_to_info[hpo]
                        frequencies.append(node['name'])
                        definition = node['def'].replace('[]', '[' + sources + ']')
                        def_frequencies.append(definition)
                    else:
                        # hpo +=' ['+sources+']'
                        frequencies.append(hpo)
                        def_frequencies.append('')
                rela_properties.append('|'.join(frequencies))
                rela_properties.append('|'.join(def_frequencies))

            else:
                rela_properties.append('')
                rela_properties.append('')
    return rela_properties


def check_for_pair_in_dictionary(mondo, symptom_id, rela_information_list, dictionary, add_resource=None):
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
        if add_resource is not None:
            add_resource.append('HPO')
            add_resource = sorted(set(add_resource))
            rela_information_list.append('|'.join(add_resource))
        dictionary[(mondo, symptom_id)] = rela_information_list
    else:
        # print(dictionary[(mondo, symptom_id)])
        # print(rela_information_list)
        for index, value in enumerate(dictionary[(mondo, symptom_id)]):
            # should avoid the problem that the new rela info do not contain the resource info
            if len(rela_information_list) == index:
                continue
            if type(value) == str:
                if rela_information_list[index] != value:
                    if value == '':
                        dictionary[(mondo, symptom_id)][index] = rela_information_list[index]
                    elif rela_information_list[index] == '':
                        continue
                    else:
                        new_string = []
                        splitted_new_infos = rela_information_list[index].split('|')
                        for string_part in value.split('|'):
                            if not string_part in splitted_new_infos:
                                new_string.append(string_part)
                        new_string.extend(splitted_new_infos)
                        dictionary[(mondo, symptom_id)][index] = "|".join(new_string)
            else:
                if rela_information_list[index] != value:
                    if value is None:
                        value = []
                    if rela_information_list[index] is None:
                        continue

                    # print(index)
                    # print(value)
                    # print(rela_information_list[index])
                    for element in rela_information_list[index]:
                        if element != '':
                            value.append(element)
                    dictionary[(mondo, symptom_id)][index] = value


'''
generate cypher file for the disease symptom connections, but only for the pairs where hpo
has a umls cui.
'''


def generate_cypher_file_for_connection(cypher_file):
    # definition of counter
    count_new_connection = 0
    count_update_connection = 0
    counter_connection = 0

    # tsv file for relationship symptom- disease
    file_rela_new = open('mapping_files/rela_new.tsv', 'w', encoding='utf-8')
    csv_rela_new = csv.writer(file_rela_new, delimiter='\t')

    file_rela_update = open('mapping_files/rela_update.tsv', 'w', encoding='utf-8')
    csv_rela_update = csv.writer(file_rela_update, delimiter='\t')

    properties = ['disease_id', 'symptom']

    # get all properties
    query = 'MATCH (n:HPO_disease)-[p:present]-(:HPO_symptom) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
    results = g.run(query)
    query_exist = ''' (n:Disease{identifier: line.disease_id})-[r:PRESENTS_DpS]-(s:Symptom{identifier:line.symptom}) Set '''
    query_new = ''' (n:Disease{identifier: line.disease_id}), (s:Symptom{identifier:line.symptom}) Create (n)-[r:PRESENTS_DpS{'''
    for result, in results:
        if result=='sources':
            properties.append(result)
            continue
        if result != 'frequency_modifier':

            properties.append(result)
            query_exist += 'r.' + result + '=split(line.' + result + ',"|"), '
            query_new += result + ':split(line.' + result + ',"|"), '
        else:
            for x in ['frequency_name', 'frequency_def']:
                properties.append(x)
                query_exist += 'r.' + x + '=split(line.' + x + ',"|"), '
                query_new += x + ':split(line.' + x + ',"|"), '

    csv_rela_new.writerow(properties)
    other_properties = properties[:]
    other_properties.append('resource')
    csv_rela_update.writerow(other_properties)
    query_exists = query_start + query_exist + "r.hpo='yes', r.version='phenotype_annotation.tab %s', r.resource=split(line.resource,'|'), r.url='https://hpo.jax.org/app/browse/disease/'+split(line.sources,'|')[0]; \n"
    query_exists = query_exists % (path_of_directory, "mapping_files/rela_update.tsv", hpo_date)
    cypher_file.write(query_exists)
    # query = '''Match (n:Disease)-[r:PRESENTS_DpS]-(s:Symptom) Where r.hpo='yes SET r.resource=r.resource+'HPO';\n '''
    # cypher_file.write(query)

    query_new = query_start + query_new + '''version:'phenotype_annotation.tab %s',unbiased:false,source:'Human Phenontype Ontology', license:'This service/product uses the Human Phenotype Ontology (April 2021). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well.', resource:['HPO'], hpo:'yes', sources:split(line.sources,'|'),  url:'https://hpo.jax.org/app/browse/disease/'+split(line.sources,'|')[0]}]->(s);\n'''
    query_new = query_new % (path_of_directory, "mapping_files/rela_new.tsv", hpo_date)
    cypher_file.write(query_new)

    print(properties)

    query = '''Match (d:Disease)--(:HPO_disease)-[p:present]-(:HPO_symptom)--(s:Symptom) Where 'P' in p.aspect Return d.identifier, p, s.identifier'''
    results = g.run(query)
    # fill the files
    for mondo, relationship, symptom_id, in results:
        rela_information_list = prepare_all_relationships_infos(properties, relationship, mondo, symptom_id)
        if (mondo, symptom_id) in dict_disease_symptom_pair_hetionet:
            check_for_pair_in_dictionary(mondo, symptom_id, rela_information_list, dict_mapped_pair_to_info,
                                         add_resource=dict_disease_symptom_pair_hetionet[(mondo, symptom_id)])
        else:
            check_for_pair_in_dictionary(mondo, symptom_id, rela_information_list, dict_new_pair_to_info)

    for (mondo_id, symptom_id), rela_info in dict_mapped_pair_to_info.items():
        count_update_connection += 1
        rela_info = change_list_values_to_string(rela_info)
        csv_rela_update.writerow(rela_info)

    for (mondo_id, symptom_id), rela_info in dict_new_pair_to_info.items():
        count_new_connection += 1
        rela_info = change_list_values_to_string(rela_info)
        csv_rela_new.writerow(rela_info)


    print('number of new connection:' + str(count_new_connection))
    print('number of update connection:' + str(count_update_connection))
    print(counter_connection)

def get_inheritance_information_for_disease():
    query='Match (d:Disease)--(:HPO_disease)-[r]-(s:HPO_symptom) Where "I" in r.aspect Return Distinct d.identifier, s.name, r.sources'
    results=g.run(query)
    dict_disease_id_to_inheritances={}
    for disease_id, inheritance, sources, in results:
        if not disease_id in  dict_disease_id_to_inheritances:
            dict_disease_id_to_inheritances[disease_id]=set()
        dict_disease_id_to_inheritances[disease_id].add((inheritance,tuple(sources)))

    file_name='output/inheritances.tsv'
    file=open(file_name,'w')
    csv_writer=csv.writer(file,delimiter='\t')
    csv_writer.writerow(['disease_id','inheritances'])
    for disease_id, inheritances_and_source in dict_disease_id_to_inheritances.items():
        inheritances='|'.join([ x[0]+' ('+','.join(x[1])+')' for x in inheritances_and_source])
        csv_writer.writerow([disease_id,inheritances])

    query= query_start+ '(d:Disease{identifier:line.disease_id}) Set d.inheritance=split(line.inheritances,"|");\n'
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)


def main():
    print(datetime.datetime.now())

    global path_of_directory, hpo_date
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        hpo_date = sys.argv[2]
    else:
        sys.exit('need a path and hpo date')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in hpo symptoms')

    load_all_hpo_symptoms_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all existing relationships')

    get_all_already_existing_relationships()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('put all relationship information into a cypher file')

    generate_cypher_file_for_connection(cypher_file)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('inheritances')

    get_inheritance_information_for_disease()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
