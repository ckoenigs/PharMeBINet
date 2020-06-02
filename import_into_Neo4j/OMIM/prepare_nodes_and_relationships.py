import sys
import datetime
import csv

# dictionary from omim prefix to label
dict_prefix_to_label = {
    "Asterisk": ["gene"],
    "Plus": ["gene and phenotype", "combined"],
    "Number Sign": ["phenotype", "molecular basis known"],
    "Percent": ["phenotype or locus", "molecular basis unknown"],
    "NULL": ["Other", "mainly phenotypes with suspected mendelian basis"],
    "Caret": ["moved/removed"]
}

# dictionary omim number to dictionary of the different sources
dict_omim_number_to_dict_of_information = {}

# set header for csv
set_of_headers = set(['identifier', 'other_cyto_location'])

# set header rela for csv
set_of_headers_rela = set()


def check_for_omim_and_add_dictionary(omim_id, dictionary):
    """
    check if the omim id is not in the dictionary and if not add a list for this omim id in the dictionary
    then add the other dictionary in the list
    :param omim_id: string
    :param dictionary: dictionary
    :return:
    """
    if omim_id not in dict_omim_number_to_dict_of_information:
        dict_omim_number_to_dict_of_information[omim_id] = []
    dict_omim_number_to_dict_of_information[omim_id].append(dictionary)


def prepare_string_to_dictionary(multi_list_string, property_extra, dictionary):
    """
    get a sting with name;symbol;;name;symbol;;... and add the information into a dictionary
    :param multi_list_string: string
    :param property_extra: additional name of the property
    :param dictionary: dictionary
    """
    multi_list_string = multi_list_string.split(';; ')
    for list_string in multi_list_string:
        list_string = split_and_return_name_and_symbol(list_string)
        for key, value in list_string.items():
            if property_extra + key + 's' not in dictionary:
                set_of_headers.add(property_extra + key + 's')
                dictionary[property_extra + key + 's'] = set()
            if type(value) == str:
                dictionary[property_extra + key + 's'].add(value)
            else:
                dictionary[property_extra + key + 's'] = dictionary[property_extra + key + 's'].union(value)


def split_and_return_name_and_symbol(string):
    """
    generate dictioary from string seperated by ;
    :param string: string
    :return: dictionary with name and symbol
    """
    dict_name_symbol = {}
    if string == '':
        return dict_name_symbol
    string = string.split('; ')

    if len(string) > 2:
        dict_name_symbol['name'] = string[0]
        symbols=[]
        # nearly all are symbols only two cases where an alternative name is, here this cases will be ignored if the
        # string is longer then 2. It is still possible that a name will appear there but the manual checking shows
        # that all alternative names have more then 2 words.
        for symbol in string[1:]:
            symbol_split=symbol.split(' ')
            if len(symbol_split)<=2:
                symbols.append(symbol)
            elif 'symbol' in symbol.lower():
                symbols.append(symbol)

        dict_name_symbol['symbol'] = symbols
        # print(dict_name_symbol)
    elif len(string) == 2:
        dict_name_symbol['name'] = string[0]
        dict_name_symbol['symbol'] = [string[1]]
    else:
        dict_name_symbol['name'] = string[0]

    return dict_name_symbol


def load_in_mim_titles():
    """
    0:Prefix
    1:MIM Number
    2:Preferred Title; symbol
    3:Alternative Title(s); symbol(s)
    4:Included Title(s); symbols
    :return:
    """
    file = open('data/mimTitles.txt', 'r', encoding='utf-8')
    # file = open('data/part_mimitles.txt', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    next(csv_reader)
    for line in csv_reader:

        dict_title = {}
        prefix = dict_prefix_to_label[line[0]]
        dict_title['detail_information'] = prefix
        set_of_headers.add('detail_information')

        prefered = split_and_return_name_and_symbol(line[2])
        print(line[2])
        if len(prefered) == 2:
            dict_title['name'] = prefered['name']
            dict_title['symbol'] = prefered['symbol'][0]
            if len(prefered['symbol']) > 1:
                dict_title['alternative_symbols'] = set(prefered['symbol'][1:])
        else:
            dict_title['name'] = prefered['name'] if 'name' in prefered else ''

        set_of_headers.add('name')
        set_of_headers.add('symbol')
        set_of_headers.add('alternative_symbols')

        prepare_string_to_dictionary(line[3], 'alternative_', dict_title)

        prepare_string_to_dictionary(line[4], 'included_', dict_title)

        omim_id = line[1]
        check_for_omim_and_add_dictionary(omim_id, dict_title)


def check_and_add_with_xref_source(xref, xref_label, list_to_add):
    """
    check if it has an value
    if so add to list with source name
    :param xref: string
    :param xref_label: string
    :param list_to_add: list
    """
    if xref != '':
        list_to_add.append(xref_label + ':' + xref)


def load_in_mim2gene():
    """
    0:MIM Number
    1:MIM Entry Type (see FAQ 1.3 at https://omim.org/help/faq)
    2:Entrez Gene ID (NCBI)
    3:Approved Gene Symbol (HGNC)
    4:Ensembl Gene ID (Ensembl)
    :return:
    """
    file = open('data/mim2gene.txt', 'r', encoding='utf-8')
    # file = open('data/part_mim2gene.txt', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    next(csv_reader)
    for line in csv_reader:
        dict_mim2gene = {}

        dict_mim2gene['labels'] = line[1]

        xref_list = []

        check_and_add_with_xref_source(line[2], 'NCBI_GENE', xref_list)
        check_and_add_with_xref_source(line[4], 'Ensembl', xref_list)
        dict_mim2gene['xrefs'] = xref_list
        set_of_headers.add('xrefs')

        add_information_to_dictionary(line[3], 'symbol', dict_mim2gene)

        omim_id = line[0]
        check_for_omim_and_add_dictionary(omim_id, dict_mim2gene)


def add_information_to_dictionary(string, property_name, dictionary):
    """
    add information into dictionary with a specific name if the string is not empty
    :param string: string
    :param property_name: string
    :param dictionary: dictionary
    :return:
    """
    if string != '':
        set_of_headers.add(property_name)
        dictionary[property_name] = string


def check_for_symbol_around_name(name):
    """
    check for the three different marks around the name and give back the meaning
    :param name: string
    :return: name without marks, the marks information
    """
    marks_information = ''
    if name.startswith('?'):
        marks_information = 'relationship is provisional, more infos in comments'
        name = name[1:]
    elif name.startswith('['):
        marks_information = 'nondisease, mainly genetic variations that lead to apparently abnormal laboratory test values'
        name = name[1:-1]
    elif name.startswith('{'):
        marks_information = 'indicate mutations that contribute to susceptibility to multifactorial disorders or to susceptibility to infection'
        name = name[1:-1]
    return name, marks_information


def prepare_the_mapping_key(string, dict_rela):
    """
    doing the preparation and transform to the write input
    :param string: string
    :param dict_rela: dictionary
    :return:
    """
    mapping_key = string.replace(')', '')
    dict_rela['phenotype_mapping_key'] = dict_phenotype_mapping_key_to_value[mapping_key]
    set_of_headers_rela.add('phenotype_mapping_key')


def prepare_name_and_markers_and_add_to_dict(string, dict_phenotype, dict_rela):
    """
    get from name further rela information
    :param string: string
    :param dict_phenotype: dictionary
    :param dict_rela: dictionary
    :return: name
    """
    marks_information = []
    same_name = False
    while not same_name:
        name, marks_info = check_for_symbol_around_name(string)
        if marks_info != '':
            marks_information.append(marks_info)
            string=name
        else:
            same_name = True

    dict_phenotype['name'] = name

    dict_rela['kind_of_rela'] = marks_information
    set_of_headers_rela.add('kind_of_rela')
    return name


def check_for_omim_id(string):
    """
    check if the string contains a omim id which is a number and has the length of 6
    :param string: string
    :return: part of the name and the omim id
    """
    name_part = ''
    omim_id = ''
    if string.isdigit():
        if len(string) == 6:
            omim_id = string
            return name_part, omim_id
    return string, omim_id


def check_before_the_bracket(string):
    """
    check for the string in  front of the bracket for name and omim id information
    :param string: string
    :return: return part of name and omim id
    """
    name = ''
    string_split = string.rsplit(' ', 1)
    if len(string_split) == 2:
        name += string_split[0]
        name_part, omim_id = check_for_omim_id(string_split[1])
        name += ' ' + name_part
    else:
        name_part, omim_id = check_for_omim_id(string)
        name += name_part
    return name, omim_id


def work_with_name_omim_and_mapping_key(omim_key_part, name, dict_rela, omim_id, with_comma=True):
    """
    separate omim id and mapping key, add the different information in the different dictionaries
    :param omim_key_part: string
    :param name: string
    :param dict_rela: dictionary
    :return: omim id of phenotype
    """
    global unkown_counter
    dict_phenotype = {}
    dict_phenotype['labels'] = 'phenotype'
    omim_id_phenotype_and_mapping_key = omim_key_part.split(' (')
    name_part, omim_id_phenotype = check_before_the_bracket(omim_id_phenotype_and_mapping_key[0])
    is_digital = True

    if omim_id_phenotype == '':
        is_digital = False
    if name_part != '':
        if with_comma:
            name += ', ' + name_part
        else:
            name = name_part

        # print(omim_id_phenotype)
        # print('thought a string is a omim id ;(')
        unkown_counter += 1
        omim_id_phenotype = 'unkown_' + str(unkown_counter)

    # rela
    prepare_the_mapping_key(omim_id_phenotype_and_mapping_key[1], dict_rela)

    # name
    name = prepare_name_and_markers_and_add_to_dict(name, dict_phenotype, dict_rela)
    if not is_digital:
        if name.lower() not in dict_unknown_phenotype_name_to_id:
            dict_unknown_phenotype_name_to_id[name.lower()] = omim_id_phenotype
        else:
            omim_id_phenotype = dict_unknown_phenotype_name_to_id[name.lower()]

    check_for_omim_and_add_dictionary(omim_id_phenotype, dict_phenotype)
    return omim_id_phenotype


def separate_information_of_string(string, dict_rela, omim_id):
    """
    recursive function to get all inheritance information and also the rest
    :param string: string
    :param dict_rela:  dictionary
    :return:  omim_id
    """
    splitted_string = string.rsplit(', ', 1)
    if '(' in splitted_string[1]:
        return work_with_name_omim_and_mapping_key(splitted_string[1], splitted_string[0],
                                                   dict_rela, omim_id)
    else:
        if 'inheritance' not in dict_rela:
            dict_rela['inheritance'] = []
            set_of_headers_rela.add('inheritance')
        dict_rela['inheritance'].append(splitted_string[1])
        return separate_information_of_string(splitted_string[0], dict_rela, omim_id)


# dictionary_of_unkown_pehnotype_name_to_new_id
dict_unknown_phenotype_name_to_id = {}

# counter for generate unknown ids
unkown_counter = 0


def prepare_phenotype_gene_relationships(omim_id, phenotypes, comments):
    if phenotypes != '':
        for phenotype in phenotypes.split('; '):
            dict_rela = {}
            dict_rela['comments'] = comments
            set_of_headers_rela.add('comments')
            # phenotype: name (can contain ,), omim_id (number)[, Inheritance ]
            split_name_omim_or_inheritance = phenotype.rsplit(', ', 1)
            if len(split_name_omim_or_inheritance) > 1:
                omim_phenotype_id = separate_information_of_string(phenotype, dict_rela, omim_id)
            else:
                omim_phenotype_id = work_with_name_omim_and_mapping_key(phenotype, '', dict_rela, omim_id,
                                                                        with_comma=False)

            if (omim_id, omim_phenotype_id) not in dict_relationships:
                dict_relationships[(omim_id, omim_phenotype_id)] = []
            # else:
            #     print('double in one file')
            #     print((omim_id, omim_phenotype_id))
            dict_relationships[(omim_id, omim_phenotype_id)].append(dict_rela)


# dictionary of gene phenotype relationships
dict_relationships = {}

# dictionary phenotype mapping key to value
dict_phenotype_mapping_key_to_value = {
    '1': "the disorder is placed on the map based on its association with a gene, but the underlying defect is not known.",
    '2': "the disorder has been placed on the map by linkage; no mutation has been found.",
    '3': "the molecular basis for the disorder is known; a mutation has been found in the gene.",
    '4': "a contiguous gene deletion or duplication syndrome, multiple genes are deleted or duplicated causing the phenotype."
}


def load_in_genemap2():
    """
        0:Chromosome
        1:Genomic Position Start
        2:Genomic Position End
        3:Cyto Location
        4:Computed Cyto Location
        5:MIM Number
        6:Gene Symbols
        7:Gene Name
        8:Approved Symbol
        9:Entrez Gene ID
        10:Ensembl Gene ID
        11:Comments
        12:Phenotypes
        13:Mouse Gene Symbol/ID

        """
    file = open('data/genemap2.txt', 'r', encoding='utf-8')
    # file = open('data/part_genemap2.txt', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    next(csv_reader)
    counter = 0
    for line in csv_reader:
        counter += 1
        dict_genemap2 = {}
        dict_genemap2['labels'] = 'gene'
        # print(line)

        add_information_to_dictionary(line[0], 'chromosome', dict_genemap2)
        add_information_to_dictionary(line[1], 'genomic_start_position', dict_genemap2)
        add_information_to_dictionary(line[2], 'genomic_start_position', dict_genemap2)
        add_information_to_dictionary(line[3], 'cyto_location', dict_genemap2)
        add_information_to_dictionary(line[4], 'computed_cyto_location', dict_genemap2)
        add_information_to_dictionary(line[7], 'name', dict_genemap2)
        add_information_to_dictionary(line[8], 'symbol', dict_genemap2)

        if line[6] != '':
            set_symobls = set()
            for symbol in line[6].split(', '):
                set_symobls.add(symbol)
            dict_genemap2['alternative_symbols'] = set_symobls

        xref_list = []
        check_and_add_with_xref_source(line[9], 'NCBI_GENE', xref_list)
        check_and_add_with_xref_source(line[10], 'Ensembl', xref_list)
        dict_genemap2['xrefs'] = xref_list
        set_of_headers.add('xrefs')
        comments = line[11]

        omim_id = line[5]

        prepare_phenotype_gene_relationships(omim_id, line[12], comments)

        check_for_omim_and_add_dictionary(omim_id, dict_genemap2)
        if counter%1000==0:
            print(counter)
            print(len(dict_relationships))
            print('huhu')


def check_for_name_in_dictionary_if_same_id(omim_id, name):
    """
    check if the phenotype has the same id as the gene and if not check if it is with the name already in the unknown
    dictionary
    :param omim_id: string
    :param name: string
    :return: omim id
    """
    omim_id_phenotype = ''
    if omim_id in dict_omim_number_to_dict_of_information:
        for dictionary in dict_omim_number_to_dict_of_information[omim_id]:
            if 'name' in dictionary:
                if name.lower() == dictionary['name'].lower():
                    omim_id_phenotype = omim_id
                    return omim_id_phenotype
            if 'alternative_names' in dictionary:
                for synonym in dictionary['alternative_names']:
                    if name.lower() == synonym.lower():
                        omim_id_phenotype = omim_id
                        return omim_id_phenotype
        if omim_id_phenotype == '':
            if name.lower() in dict_unknown_phenotype_name_to_id:
                omim_id = dict_unknown_phenotype_name_to_id[name.lower()]
                return omim_id_phenotype
            else:
                print('not mapped to omim id')
    else:
        print('omim not existing')
        sys.exit('not mapped to omim id')
    return omim_id_phenotype


def separate_in_name_omim_marker(phenotype, dict_rela, dict_node):
    """
    separate the information from sting and add them to the different information.
    :param phenotype: string
    :param dict_rela: dictionary
    :param dict_node: dictionary
    :return: return the normal name and the maybe found omim id
    """
    split_name_omim_and_mapping_key = phenotype.rsplit(', ', 1)
    omim_id = ''
    if len(split_name_omim_and_mapping_key) == 2:

        name = split_name_omim_and_mapping_key[0]
        split_name_or_omim_and_mapping_key = split_name_omim_and_mapping_key[1].split(' (')
        # for the case that 'name, (number)'
        if len(split_name_or_omim_and_mapping_key) > 1:
            mapping_key = split_name_or_omim_and_mapping_key[1]
            name_part, omim_id = check_before_the_bracket(split_name_or_omim_and_mapping_key[0])
            if name_part != '':
                name += ', ' + split_name_or_omim_and_mapping_key[0]
        else:
            mapping_key = split_name_omim_and_mapping_key[1].replace('(', '')
    else:
        split_name_and_mapping_key = phenotype.split(' (')
        name_part, omim_id = check_before_the_bracket(split_name_and_mapping_key[0])
        name = name_part
        mapping_key = split_name_and_mapping_key[1]

    # rela
    prepare_the_mapping_key(mapping_key, dict_rela)

    # name
    name = prepare_name_and_markers_and_add_to_dict(name, dict_node, dict_rela)

    return name, omim_id


def load_in_morbidmap():
    """

    0:Phenotype
    1:Gene Symbols
    2:MIM Number
    3:Cyto Location
    :return:
    """
    file = open('data/morbidmap.txt', 'r', encoding='utf-8')
    # file = open('data/part_morbidmap.txt', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    next(csv_reader)
    for line in csv_reader:
        dict_rela = {}
        dict_phenotype = {}
        dict_phenotype['labels'] = 'phenotype'

        phenotype = line[0]
        name, omim_id_phenotype = separate_in_name_omim_marker(phenotype, dict_rela, dict_phenotype)

        omim_id = line[2]
        gene_symbols = line[1].split(', ')
        cyto_location = line[3]

        dict_gene = {}
        dict_gene['labels'] = 'gene'
        dict_gene['alternative_symbols'] = gene_symbols
        dict_gene['cyto_location'] = cyto_location

        check_for_omim_and_add_dictionary(omim_id, dict_gene)

        if omim_id_phenotype == '':
            omim_id_phenotype = check_for_name_in_dictionary_if_same_id(omim_id, name)
            if omim_id_phenotype == '':
                print(line)
                print('ohje still no omim id for phenotype')
                continue

        check_for_omim_and_add_dictionary(omim_id_phenotype, dict_phenotype)

        if (omim_id, omim_id_phenotype) not in dict_relationships:
            dict_relationships[(omim_id, omim_id_phenotype)] = []
        dict_relationships[(omim_id, omim_id_phenotype)].append(dict_rela)


def add_properties_to_query(set_of_header, query, list_of_list_element):
    """
    go through all properties and add them to query depending on if they are list or not
    :param set_of_header: set of strings
    :param query: string
    :param list_of_list_element: list of strings
    :return: query
    """
    for property in set_of_header:
        if property in list_of_list_element:
            query += property + ':split(line.' + property + ',"|"), '
        else:
            query += property + ': line.' + property + ', '
    return query[:-2]


# list of list element for nodes
list_of_list_elements_node = ['alternative_names', 'alternative_symbols', 'included_names',
                              'included_symbols', 'xrefs', 'detail_information']


def prepare_queries(query_start):
    """
    generate the different queries
    :return: node query and edge query
    """
    query_node = query_start + " Create (n:%s_omim {"
    query_node = add_properties_to_query(set_of_headers, query_node, list_of_list_elements_node)
    query_node += '});\n'

    query_edge = query_start + ' Match (a:%s_omim{identifier:line.id_1}), (b:%s_omim{identifier:line.id_2}) Create (a)-[:%s{'
    query_edge = add_properties_to_query(set_of_headers_rela, query_edge,
                                         ['inheritance', 'kind_of_rela', 'phenotype_mapping_key'])
    query_edge += '}]->(b);\n'
    set_of_headers_rela.add('id_1')
    set_of_headers_rela.add('id_2')

    return query_node, query_edge


def prepare_labels(label):
    """
    prepared the label  into separated label by / and/or replace space with _
    :param label
    :return: list of strings
    """
    new_labels = []
    if '/' in label:
        labels = label.split('/')
        labels = [label.replace(' ', '_') for label in labels]
        new_labels.extend(labels)
    else:
        label = label.replace(' ', '_')
        new_labels.append(label)
    return new_labels


# cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
query_constraint = '''Create Constraint On (node:%s_omim) Assert node.identifier Is Unique;\n'''
set_of_existing_constrains = set()


def add_node_query_to_cypher(labels, query_node, file_name):
    """
    generate the queries for the different labels
    :param labels: list of strings
    :param query_node: string
    :param file_name: string
    :return:
    """
    string_labels = '_omim :'.join(labels)
    query_node = query_node % (file_name, string_labels)
    cypher_file.write(query_node)
    for label in labels:
        if not label in set_of_existing_constrains:
            one_constraint = query_constraint % label
            cypher_file.write(one_constraint)
            set_of_existing_constrains.add(label)


# dictionary labels to csv file
dict_labels_to_csv = {}


def dict_to_csv(dict_node, labels, query_node, omim_id):
    """
    add the different dictionaries to csv file
    if the tuple of labels do not exists a new csv file is generated and also the cypher query
    :param dict_node: dictionary
    :param labels: list of strings
    :param query_node: string
    :param omim_id: string
    :return:
    """
    tuple_labels = tuple(labels)
    if tuple_labels not in dict_labels_to_csv:
        file_name = "output/" + "_".join(labels) + '.tsv'
        file = open(file_name, 'w', encoding='utf-8')
        csv_writer = csv.DictWriter(file, fieldnames=list(set_of_headers), delimiter='\t')
        csv_writer.writeheader()
        dict_labels_to_csv[tuple_labels] = csv_writer
        if 'moved' not in labels:
            add_node_query_to_cypher(labels, query_node, file_name)

    del dict_node['labels']
    dict_node['identifier'] = omim_id
    for property in list_of_list_elements_node:
        dict_node[property] = "|".join(list(dict_node[property])) if property in dict_node else ''
    dict_labels_to_csv[tuple_labels].writerow(dict_node)


def add_problem_case_to_dict(key, dictionary, value, dictionary_problems):
    """
    add problem case to dictionary
    :param key: string
    :param dictionary: dictionary of node or rela 
    :param value: string
    :param dictionary_problems: dictionary of problems
    :return: true for problem and false for ok
    """
    if key not in dictionary_problems:
        dictionary_problems[key] = list()
    if (value, dictionary[key]) not in dictionary_problems[key]:
        dictionary_problems[key].append((value, dictionary[key]))
    return True


# check for a key if the  values are equal, but only for the one which are not prepared in other ways
dict_same_label_different_values = {}

# dictionary omim id to node
dict_omim_id_to_node = {}


def combine_the_node_information(query_node):
    """
    combine the information from the different files to one dictionary and add to csv file, also if not exist add the
    fitting cypher query to cypher file
    :param query_node: string
    :return:
    """
    for omim_id, info_list in dict_omim_number_to_dict_of_information.items():
        dict_node = {}
        for dictionary in info_list:
            for key, value in dictionary.items():
                if key in dict_node and dict_node[key] != value:
                    if key == 'symbol':
                        if 'alternative_symbols' not in dict_node:
                            dict_node['alternative_symbols'] = set()
                        dict_node['alternative_symbols'].add(value)
                        continue
                    if key == 'alternative_symbols':
                        dict_node['alternative_symbols'] = set(dict_node['alternative_symbols']).union(value)
                        continue
                    if type(value) == str:
                        if value.lower() == dict_node[key].lower():
                            continue
                    if key == 'name':
                        if 'alternative_names' not in dict_node:
                            dict_node['alternative_names'] = set()
                        dict_node['alternative_names'].add(value)
                        continue
                    if key == 'cyto_location':
                        dict_node['other_cyto_location'] = dict_node['cyto_location']
                        dict_node['cyto_location'] = value
                        continue

                    # print(omim_id)
                    # print(value)
                    # print(dict_node[key])
                    add_problem_case_to_dict(key, dict_node, value, dict_same_label_different_values)
                    continue
                dict_node[key] = value
        labels = prepare_labels(dict_node['labels'])

        dict_to_csv(dict_node, labels, query_node, omim_id)

        dict_node['labels'] = labels
        dict_omim_id_to_node[omim_id] = dict_node

    dict_omim_number_to_dict_of_information.clear()

    print('number of nodes:' + str(len(dict_omim_id_to_node)))

    print(dict_same_label_different_values.keys())
    for key, lists in dict_same_label_different_values.items():
        print(key + ':' + str(len(lists)))


def check_for_digit(string, dictionary_id_to_label):
    """
    check if the string is an integer and if so add to list
    :param string: string
    :param dictionary_id_to_label: dictionary
    :return: 
    """
    if string.isdigit():
        labels = dict_omim_id_to_node[string]['labels']
        dictionary_id_to_label[string] = labels


def check_labels_if_removed(labels_gene, omim_id):
    """
    check if the omim id was moved or removed and return the True or the new node ids
    :param labels_gene: list of labels
    :param omim_id: string
    :return: dict of existing omims to there labels, removed true or false
    """
    dict_omim_id_to_labels = {}
    removed = False
    if 'removed' in labels_gene:
        name = dict_omim_id_to_node[omim_id]['name']
        if 'TO' in name:
            split_name = name.split('TO ')
            if ' AND ' in split_name[1]:
                split_with_and = split_name[1].split(' AND ')
                check_for_digit(split_with_and[1], dict_omim_id_to_labels)
                if ',' in split_with_and[0]:
                    for omim_id_remove in split_with_and[0].split(','):
                        omim_id_remove = omim_id_remove.strip()
                        check_for_digit(omim_id_remove, dict_omim_id_to_labels)
                else:
                    check_for_digit(split_with_and[0], dict_omim_id_to_labels)
            else:
                check_for_digit(split_name[1], dict_omim_id_to_labels)
        else:
            removed = True
    else:
        dict_omim_id_to_labels[omim_id] = labels_gene

    return dict_omim_id_to_labels, removed


# dictionary label pair to the csv file
dict_label_pair_to_csv_file = {}


def add_rela_query(file_name, label_1, label_2, query_rela):
    query_rela = query_rela % (file_name, label_1, label_2, 'associates')
    cypher_file.write(query_rela)


def write_to_csv_rela(omim_id, labels, phenotype_omim_id, phenotype_labels, dict_combined_rela, query_rela):
    """
    prepare the dictionary with the ids and add to csv file
    generate the csv file for each label tuple and add cypher query to cypher file
    :param omim_id: string
    :param labels: list
    :param phenotype_omim_id: string
    :param phenotype_labels: list
    :param dict_combined_rela: dictionary
    :param query_rela: string
    :return:
    """
    gene_label = labels[0]
    phenotype_label = phenotype_labels[0]
    dict_combined_rela['id_1'] = omim_id
    dict_combined_rela['id_2'] = phenotype_omim_id
    if (gene_label, phenotype_label) not in dict_label_pair_to_csv_file:
        file_name = 'output/' + gene_label + '_' + phenotype_label + '_rela.tsv'
        file = open(file_name, 'w', encoding='utf-8')
        csv_writer = csv.DictWriter(file, delimiter='\t', fieldnames=list(set_of_headers_rela))
        csv_writer.writeheader()
        dict_label_pair_to_csv_file[(gene_label, phenotype_label)] = csv_writer
        add_rela_query(file_name, gene_label, phenotype_label, query_rela)

    dict_label_pair_to_csv_file[(gene_label, phenotype_label)].writerow(dict_combined_rela)


dict_same_rela_properties = {}


def prepare_and_add_relationships(query_edge):
    """
    combine the dictionaries information and check if both nodes exist
    :param query_edge: string
    :return:
    """
    counter = 0
    for (omim_id, phenotype_omim_id), list_of_dicts in dict_relationships.items():
        labels_gene = dict_omim_id_to_node[omim_id]['labels']
        dict_omim_ids_to_labels, removed = check_labels_if_removed(labels_gene, omim_id)
        if removed:
            continue
        labels_phenotype = dict_omim_id_to_node[phenotype_omim_id]['labels']
        dict_phenotype_omim_ids_to_labels, removed = check_labels_if_removed(labels_phenotype, phenotype_omim_id)
        if removed:
            continue
        dict_combined_rela = {}
        for dict_info in list_of_dicts:
            for key, value in dict_info.items():
                if key in dict_combined_rela and dict_combined_rela[key] != value and (
                        (type(value) == str and value != '') or (type(value) == list and len(value) > 0)):
                    if key == 'kind_of_rela':
                        dict_combined_rela[key] = set(dict_combined_rela[key] ).union(value)
                        continue
                    if key == 'phenotype_mapping_key':
                        dict_combined_rela[key] = dict_combined_rela[key] + '|' + value
                        continue
                    add_problem_case_to_dict(key, dict_combined_rela, value, dict_same_rela_properties)
                    continue
                if type(value) == str and value != '':
                    dict_combined_rela[key] = value
                elif type(value) == list:
                    dict_combined_rela[key] = value

        for key, value in dict_combined_rela.items():
            if type(value) in [list, set]:
                dict_combined_rela[key] = '|'.join(list(value))

        for omim_id, labels in dict_omim_ids_to_labels.items():
            for phenotype_omim_id, phenotype_labels in dict_phenotype_omim_ids_to_labels.items():
                counter += 1
                write_to_csv_rela(omim_id, labels, phenotype_omim_id, phenotype_labels, dict_combined_rela, query_edge)

    print('number of relationships:' + str(counter))
    print(dict_same_rela_properties.keys())
    for key, lists in dict_same_rela_properties.items():
        print(key + ':' + str(len(lists)))


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path omim')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load mimTitles in dictionary')
    load_in_mim_titles()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load mim2genes')

    load_in_mim2gene()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load genemap2')

    load_in_genemap2()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load morbidmap')

    load_in_morbidmap()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Prepare the cypher queries')

    # query start
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/OMIM/%s"  As line FIELDTERMINATOR '\t' '''

    query_node, query_edge = prepare_queries(query_start)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Combine node information')

    combine_the_node_information(query_node)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Combine rela information')

    prepare_and_add_relationships(query_edge)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
