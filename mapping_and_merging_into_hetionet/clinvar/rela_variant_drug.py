from py2neo import Graph
import sys
import datetime, re
import csv, json


# connect with the neo4j database AND MYSQL
def database_connection():
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


def go_through_a_dictionary_add_info_into_another(from_dict, to_dictionary, additional_name='', asString=False):
    """
    go through a dictionary and add information into another dictionary
    :param from_dict: dictionary
    :param to_dictionary: dictionary
    :param additional_name: string
    """
    if not asString:
        for key, value in from_dict.items():
            if value is None:
                continue
            if not additional_name + key in to_dictionary:
                to_dictionary[additional_name + key] = set()
            if type(value) == list:
                if type(value[0]) == str:
                    to_dictionary[additional_name + key].union(value)
                elif type(value[0]) == dict:
                    to_dictionary[additional_name + key].union(list_of_dictionary_to_list_of_string(value))
                else:
                    print('another type for dictionary')
                    sys.exit('ohje dictionary transport info')
            else:
                to_dictionary[additional_name + key].add(value)
    else:
        for key, value in from_dict.items():
            if value is None:
                continue
            to_dictionary[additional_name + key] = value


def transform_json_string_to_dict(json_string):
    """
    replace unneeded sights from string and transform to string
    :param json_string: string
    :return: dictionary
    """
    if '\\"' in json_string:
        value = json_string.replace('\\"', '"')
    else:
        value = json_string.replace("'", "\"")

    return json.loads(value)


def list_of_dictionary_to_list_of_string(list_of_dict):
    """transform a list of dictionary with only only level below to a list of strings
    :param list_of_dict:list
    :returns list
    """
    list_of_stings = []
    for string_dict in list_of_dict:
        if type(string_dict) == str:
            string_dict = transform_json_string_to_dict(string_dict)
        list_of_infos_from_dict = []
        for type_key, property in string_dict.items():
            list_of_infos_from_dict.append(type_key + ':' + property)
        list_of_stings.append(';'.join(list_of_infos_from_dict))
    return list_of_stings


def go_trough_dict_to_give_infos_into_string_without_key(dictionary_attribute, to_set):
    """
    give all contains into a set without considere the key
    :param list_of_dict: dict
    :param to_set: set
    :returns set
    """
    for key_attribute, attribute_list in dictionary_attribute.items():
        if key_attribute != 'attribute':
            print('different attribute :O')
            print(key_attribute)
        to_set = to_set.union(attribute_list)
    return to_set


'''
Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
'''


def load_all_rela_drug_response_and_finish_the_files():
    cypher_file = open('output/cypher_drug.cypher', 'w', encoding='utf-8')

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/clinvar/output/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (c:Chemical{identifier:line.chemical_id}), (t:trait_DrugResponse_ClinVar{identifier:line.clinvar_id}) Create (c)-[:equal_to_clinvar_drug]->(t);\n '''
    query_start = query_start % (path_of_directory, 'chemical_drug')
    cypher_file.write(query_start)

    query = "MATCH (v:Variant)--(:Variant_ClinVar)-[r]-(:trait_set_DrugResponse_ClinVar)--(n:trait_DrugResponse_ClinVar)--(a:Chemical) RETURN v.identifier, r, type(r), n.name, a.identifier"
    results = g.run(query)
    print(query)
    for variant_id, rela_info, rela_type, respose_name, chemical_id, in results:
        rela_info = dict(rela_info)
        # print(dict(rela_info))
        dict_rela_combinde = {}
        for key, value in rela_info.items():
            if 'citations' == key:
                dict_rela_combinde[key] = list_of_dictionary_to_list_of_string(value)
            elif key == 'clinical_significance':
                value = transform_json_string_to_dict(value)
                if 'reference_ClinVar_assertion' in value:
                    for assertion_key, dict_value in value.items():
                        go_through_a_dictionary_add_info_into_another(dict_value, dict_rela_combinde,
                                                                      additional_name=key + '_')
                else:
                    go_through_a_dictionary_add_info_into_another(value, dict_rela_combinde, additional_name=key + '_')
            elif key == 'attributes':
                set_of_attributes = set()
                for attributes_list in value:
                    attributes_list = transform_json_string_to_dict(attributes_list)
                    if 'reference_ClinVar_assertion' in attributes_list:
                        for _, list_of_attributes in attributes_list.items():
                            for attribute_dict in list_of_attributes:
                                set_of_attributes = go_trough_dict_to_give_infos_into_string_without_key(
                                    attribute_dict, set_of_attributes)
                    else:
                        set_of_attributes = go_trough_dict_to_give_infos_into_string_without_key(attributes_list,
                                                                                                        set_of_attributes)
                    dict_rela_combinde[key]=set_of_attributes

            elif key == 'assertion':
                set_assertion = set()
                if ':' in value:
                    dict_assertion = transform_json_string_to_dict(value)
                    for _, assertion_value in dict_assertion.items():
                        set_assertion.add(assertion_value)
                else:
                    set_assertion.add(value)
                dict_rela_combinde[key] = set_assertion
            elif key == 'accession_clinvar':
                value = transform_json_string_to_dict(value)
                go_through_a_dictionary_add_info_into_another(value, dict_rela_combinde, additional_name='accession_',
                                                              asString=True)
            elif key=='observations':
                if type(value)== list:
                    for obervations in value:
                        # print(obervations)
                        dict_or_list_observations=transform_json_string_to_dict(obervations)
                        if type(dict_or_list_observations)==dict:
                            if 'observation' in dict_or_list_observations:
                                observation=dict_or_list_observations['observation']
                                observation_as_list=[]
                                for ob_key, ob_value in observation.items():
                                    if 'sample' ==ob_key:
                                        # print(ob_value)
                                        # if len(ob_value)>1:
                                        #     sys.exit('sample has more information :O')
                                        for key_sample, value_sample in ob_value.items():
                                            observation_as_list.append(ob_key+'_'+key_sample+':'+value_sample)
                                    elif ob_key=='methods':
                                        observation_as_list.append(ob_key+':['+','.join(ob_value)+']')
                                    elif ob_key=='observation_data_multiple':
                                        print(ob_value)
                                    # else:
                                    #     print(ob_key)
                                    #     print(ob_value)
                                # print(observation_as_list)
                elif type(value)==str:
                    h=1
                    # print(value)
                else:
                    sys.exit('observation has mor then 2 types')
            elif key in ['xrefs', 'title', 'comments']:
                dict_rela_combinde[key] = value

        #     else:
        #         print(key)
        #         print(value)
        # check for none values!
        # print(dict_rela_combinde)
        # sys.exit()


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ClinVar')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all kind of properties of the drug response')

    load_all_rela_drug_response_and_finish_the_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
