import sys
import datetime
import csv, json
import re

sys.path.append("../..")
import create_connection_to_databases


# connect with the neo4j database AND MYSQL
def database_connection():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


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
                    to_dictionary[additional_name + key] = to_dictionary[additional_name + key].union(value)
                elif type(value[0]) == dict:
                    to_dictionary[additional_name + key] = to_dictionary[additional_name + key].union(
                        list_of_dictionary_to_list_of_string(value))
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
    # print(json_string)
    if '\\"' in json_string:
        json_string = json_string.replace('\\"', '"')
    else:
        json_string = re.sub("([{\[])'", '\\1"', json_string)
        json_string = re.sub("([\:,]) '", '\\1 "', json_string)
        json_string = re.sub("'([\:,\]}])", '"\\1', json_string)
    # print(json_string)
    return json.loads(json_string)


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


def dict_go_down_dict(dictionary):
    """
    a recursive function which go completely down in a dictionary and generate a string
    :param dictionary:
    :return:
    """
    for key, value in dictionary.items():
        if type(value) == str:
            return key, value
        elif type(value) == dict:
            down_name, this_value = dict_go_down_dict(value)
            return key + '_' + down_name, this_value
        elif type(value) == list:
            this_value = set()
            for content in value:
                if type(content) == str:
                    this_value.add(content)
                elif type(content) == dict:
                    for content_key, content_value in content.items():
                        this_value.add(content_key + ':' + content_value)
                else:
                    sys.exit('other content in list')
                return key, ';'.join(sorted(this_value))
        else:
            sys.exit('other type by dict down')


# dictionary pair to rela infos
dict_pair_to_rela_info = {}

# set of rela properties
set_of_rela_properties = {'variant_id', 'chemical_id', 'additional_rela_infos'}

# additional rela infos
list_of_splitable_information = [' response', ' hypersensitivity', ' resistance',
                                 ' susceptibility']  # poor metabolism of

'''
Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
'''


def load_all_rela_drug_response_and_finish_the_files():
    """
    Go through all information and prepare them for writing into csv file
    :return:
    """
    global set_of_rela_properties

    # {identifier:'DB00860'} {identifier:'225969'} {identifier:'226021'} {identifier:'DB00864'}
    query = "MATCH (v:Variant)--(:Variant_ClinVar)-[r]-(:trait_set_DrugResponse_ClinVar)--(n:trait_DrugResponse_ClinVar)--(a:Chemical) RETURN v.identifier, r, type(r), n.name, a.identifier"
    results = g.run(query)
    print(query)
    counter_rela = 0
    for variant_id, rela_info, rela_type, respose_name, chemical_id, in results:
        print(variant_id)
        print(chemical_id)
        counter_rela += 1

        rela_info = dict(rela_info)

        dict_rela_combinde = {}
        additiona_infos = ''
        if ' - ' in respose_name:
            dict_rela_combinde['additional_rela_infos'] = '|'.join(sorted(respose_name.split(' - ')[1].split(',')))
            additiona_infos = dict_rela_combinde['additional_rela_infos'].strip()
        elif not 'response' in respose_name and rela_type == 'variation_to_disease' and ' ' in respose_name:
            rela_type = respose_name.rsplit(' ', 1)[1]
        # print(dict(rela_info))
        for key, value in rela_info.items():
            if 'citations' == key:
                # value is a list
                dict_rela_combinde[key] = value
            elif 'citations_info' == key:
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
                    dict_rela_combinde[key] = set_of_attributes

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
            elif key == 'observations':
                if type(value) == list:
                    for obervations in value:
                        # print(obervations)
                        dict_or_list_observations = transform_json_string_to_dict(obervations)
                        if type(dict_or_list_observations) == dict:
                            if 'observation' in dict_or_list_observations:
                                observation = dict_or_list_observations['observation']
                                observation_as_list = []
                                for ob_key, ob_value in observation.items():
                                    if 'sample' == ob_key:
                                        # print(ob_value)
                                        # if len(ob_value)>1:
                                        #     sys.exit('sample has more information :O')
                                        for key_sample, value_sample in ob_value.items():
                                            observation_as_list.append(ob_key + '_' + key_sample + ':' + value_sample)
                                    elif ob_key == 'methods':
                                        observation_as_list.append(ob_key + ':[' + ','.join(ob_value) + ']')
                                    elif ob_key == 'observation_data_multiple':
                                        # seems like do not contain any usefull information
                                        continue
                                        # print('')
                                        # print(ob_value)
                                    else:
                                        print(ob_key)
                                        print(ob_value)
                                # print(observation_as_list)
                                dict_rela_combinde['observation'] = '|'.join(observation_as_list)

                        else:
                            print('obser')
                            print(dict_or_list_observations)
                elif type(value) == str:
                    h = 1
                    json_infos = transform_json_string_to_dict(value)
                    for key, values in json_infos.items():
                        property_name = key + '_observations'
                        list_of_obs = []
                        for observation in values:
                            list_ob_info = []
                            for ob, ob_info in observation.items():
                                for pro_name, value in ob_info.items():
                                    if type(value) == list:
                                        if type(value[0]) == str:
                                            list_ob_info.append(pro_name + ':' + ';'.join(value))
                                        else:
                                            dict_proper = {}
                                            for dictionary in value:
                                                property, this_value = dict_go_down_dict(dictionary)
                                                if not property in dict_proper:
                                                    dict_proper[property] = set()
                                                dict_proper[property].add(this_value)
                                            list_of_pro = [x + ':' + ';'.join(y) for x, y in dict_proper.items()]
                                            list_ob_info.extend(list_of_pro)


                                    elif type(value) == dict:
                                        pro_name, this_value = dict_go_down_dict(value)
                                        list_ob_info.append(pro_name + ':' + this_value)
                                    else:
                                        print(';)')
                                        print(value)
                                list_of_obs.append('|'.join(list_ob_info))
                    dict_rela_combinde[property_name] = list_of_obs


                else:
                    sys.exit('observation has more then 2 types')
            elif key in ['xrefs', 'comments']:
                dict_rela_combinde[key] = value
            elif type(value) == str:
                dict_rela_combinde[key] = value
            else:
                print(key)
                print(value)
                sys.exit('info not included')
        # check for none values!
        # print(dict_rela_combinde)
        # sys.exit()
        set_of_rela_properties = set_of_rela_properties.union(dict_rela_combinde.keys())
        if (variant_id, chemical_id, rela_type, additiona_infos) not in dict_pair_to_rela_info:
            dict_pair_to_rela_info[(variant_id, chemical_id, rela_type, additiona_infos)] = []
        dict_pair_to_rela_info[(variant_id, chemical_id, rela_type, additiona_infos)].append(dict_rela_combinde)
    print(set_of_rela_properties)
    print('number of relas of clinvar:', counter_rela)


# dictionary rela type to csv file
dict_rela_type_to_csv = {}

# set of all properties which are a list
set_of_list_properties = set()


def prepare_dictionary_with_strings_values(dictionary):
    """
    go through a dictionary and check out which properties are lists/sets and transform into string
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dictionary = {}
    for key, value in dictionary.items():
        if type(value) in [set, list]:
            set_of_list_properties.add(key)
            value = '|'.join(value)
        new_dictionary[key] = value
    return new_dictionary


# cypher file
cypher_file = open('variant_drug/cypher.cypher', 'w', encoding='utf-8')


def generate_cypher_file_and_csv(rela_type):
    """
    Generate cypher file and csv
    :param rela_type: string
    :return: csv dict
    """
    file_name = 'variant_drug/' + rela_type + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=list(set_of_rela_properties), delimiter='\t')
    csv_writer.writeheader()

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/clinvar/%s" As line FIELDTERMINATOR '\\t' 
            Match (c:Chemical{identifier:line.chemical_id}), (t:Variant{identifier:line.variant_id})  Create (c)<-[:%s {'''
    for property in set_of_rela_properties:
        if property in ['variant_id', 'chemical_id']:
            continue
        elif property in ['clinical_significance_description', 'attributes', 'clinical_significance_date',
                          'clinical_significance_comments', 'comments', 'xrefs', 'ClinVar_assertion_observations',
                          'clinical_significance_citations', 'citations', 'assertion',
                          'clinical_significance_review_status', 'additional_rela_infos', 'citations_info',
                          'observation', 'clinical_significance_citations_info']:
            if property not in ['assertion', 'observation']:
                query_start += property + ':split(line.' + property + ',"|"), '
            else:
                query_start += property + 's:split(line.' + property + ',"|"), '
        else:
            query_start += property + ':line.' + property + ', '

    query = query_start + '''resource:['ClinVar'], source:'ClinVar', clinvar:'yes', license:'https://www.ncbi.nlm.nih.gov/home/about/policies/', url:"https://www.ncbi.nlm.nih.gov/clinvar/variation/"+line.variant_id}]-(t);\n '''
    query = query % (path_of_directory, file_name, rela_type)
    cypher_file.write(query)

    return csv_writer


# dictionary rela type to rela type new name
dict_rela_type_to_new_name = {
    "variation_to_disease": "ASSOCIATES",
    "confers_resistance": "CONFERS_RESISTANCE",
    "hypersensitivity": "IS_RISK_FACTOR_WITH",
    "resistance": "CONFERS_RESISTANCE",
    'confers_sensitivity': "CONFERS_SENSITIVITY"
}

# dictionary rela name to end
dict_rela_name_to_rela_end = {
    "ASSOCIATES": "_VaCH",
    "CONFERS_RESISTANCE": "_VcrCH",
    "IS_RISK_FACTOR_WITH": "_VirfwCH",
    "CONFERS_RESISTANCE": "_VcrCH",
    'CONFERS_SENSITIVITY': '_VcsCH'
}


def prepare_csv_file():
    """
    prepare the different rela files and generate cypher queries
    :return:
    """
    counter_not_used_edges=0
    for (variant_id, chemical_id, rela_type, additional_information), list_of_dict in dict_pair_to_rela_info.items():
        if rela_type in dict_rela_type_to_new_name:
            rela_type = dict_rela_type_to_new_name[rela_type]
            rela_end = dict_rela_name_to_rela_end[rela_type]
            if additional_information != '' and additional_information.lower() != 'other':
                rela_type = rela_type + '_TO_' + additional_information.replace('|', '_').upper()
                rela_type = rela_type.replace(' ', '').replace('/', '_')
            rela_type += rela_end
        else:
            print(rela_type)

        if rela_type not in dict_rela_type_to_csv:
            csv_writer = generate_cypher_file_and_csv(rela_type)
            dict_rela_type_to_csv[rela_type] = csv_writer
        if len(list_of_dict) == 1:
            dict_info = list_of_dict[0]
            dict_info['variant_id'] = variant_id
            dict_info['chemical_id'] = chemical_id
            if "no assertion criteria provided" not in dict_info['clinical_significance_review_status']:
                dict_rela_type_to_csv[rela_type].writerow(prepare_dictionary_with_strings_values(dict_info))
            else:
                counter_not_used_edges+=1

        else:
            combinde_dictionary = {}
            combinde_dictionary['variant_id'] = variant_id
            combinde_dictionary['chemical_id'] = chemical_id
            for dictionary in list_of_dict:
                for key, value in dictionary.items():
                    if not key in combinde_dictionary:
                        combinde_dictionary[key] = value
                    else:
                        if value != combinde_dictionary[key]:
                            if key in ['citations', 'xrefs']:
                                combinde_dictionary[key] = set(combinde_dictionary[key]).union(value)
                                continue
                            elif key in ['clinical_significance_date', 'clinical_significance_review_status',
                                         'clinical_significance_description', 'assertion',
                                         'clinical_significance_comments', 'clinical_significance_citations']:
                                combinde_dictionary[key] = combinde_dictionary[key].union(value)
                                continue
                            elif key in ['accession_reference_ClinVar_assertion', 'accession_ClinVar_assertion',
                                         'title', 'observation']:
                                combinde_dictionary[key] = set([combinde_dictionary[key]]).add(value)
                                continue
                            else:
                                print(':::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
                                print(variant_id)
                                print(chemical_id)
                                print(key)
                                print(value)
                                print(type(value))
                                print(combinde_dictionary[key])
                                # sys.exit()

            if "no assertion criteria provided" not in combinde_dictionary['clinical_significance_review_status']:
                dict_rela_type_to_csv[rela_type].writerow(prepare_dictionary_with_strings_values(combinde_dictionary))
            else:
                counter_not_used_edges+=1
    print(set_of_list_properties)
    print('number of edges which are not used:',counter_not_used_edges)


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
    print('get all kind of properties of the drug response')

    prepare_csv_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
