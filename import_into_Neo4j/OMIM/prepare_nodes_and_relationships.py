import sys
import datetime
import csv

# dictionary from omim prefix to label
dict_prefix_to_label = {
    "Asterisk": ["gene"],
    "Plus": ["gene", "phenotype"],
    "Number Sign": ["phenotype", "molecular basis known"],
    "Percent": ["Phenotype or locus", "molecular basis unknown"],
    "NULL": ["Other", "mainly phenotypes with suspected mendelian basis"],
    "Caret": ["moved/removed"]
}

# dictionary omim number to dictionary of the different sources
dict_omim_number_to_dict_of_information = {}

# set header for csv
set_of_headers = set()


def check_for_omim_and_add_duictionary(omim_id, dictionary):
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
                dictionary[property_extra + key + 's'] = []
            dictionary[property_extra + key + 's'].append(value)


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
        # todo check how often this happend
        print('string with more then one ; ;(')
        print(string)
    elif len(string) == 2:
        dict_name_symbol['name'] = string[0]
        dict_name_symbol['symbol'] = string[1]
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
        dict_title['labels'] = prefix

        prefered = split_and_return_name_and_symbol(line[2])
        if len(prefered) == 2:
            dict_title['name'] = prefered['name']
            dict_title['symbol'] = prefered['symbol']
        else:
            dict_title['name'] = prefered['name'] if 'name' in prefered else ''

        set_of_headers.add('name')
        set_of_headers.add('symbol')

        prepare_string_to_dictionary(line[3], 'alternative_', dict_title)

        prepare_string_to_dictionary(line[4], 'included_', dict_title)

        omim_id = line[1]
        check_for_omim_and_add_duictionary(omim_id, dict_title)


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
        check_for_omim_and_add_duictionary(omim_id, dict_mim2gene)


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


def prepare_phenotype_gene_relationships(omim_id, phenotypes):
    if phenotypes != '':
        for pheneotyp in phenotypes.split('; '):
            # phenotype: name (can contain ,), omim_id (number)[, Inheritance ]
            print(pheneotyp)


# dictionary of gene phenotype relationships
dict_relationships = {}

# dictionary phenotype mapping key to value
dict_phenotype_mapping_key_to_value = {
    1: "the disorder is placed on the map based on its association with a gene, but the underlying defect is not known.",
    2: "the disorder has been placed on the map by linkage; no mutation has been found.",
    3: "the molecular basis for the disorder is known; a mutation has been found in the gene.",
    4: "a contiguous gene deletion or duplication syndrome, multiple genes are deleted or duplicated causing the phenotype."
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
    # file = open('data/genemap2.txt', 'r', encoding='utf-8')
    file = open('data/part_genemap2.txt', 'r', encoding='utf-8')
    csv_reader = csv.reader(file, delimiter='\t')
    next(csv_reader)
    for line in csv_reader:
        dict_genemap2 = {}
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
            dict_genemap2['alternative_symbols'] = list(set_symobls)

        xref_list = []
        check_and_add_with_xref_source(line[9], 'NCBI_GENE', xref_list)
        check_and_add_with_xref_source(line[10], 'Ensembl', xref_list)
        dict_genemap2['xrefs'] = xref_list
        set_of_headers.add('xrefs')
        # print(line[11])

        print(line[12])

        omim_id = line[5]
        check_for_omim_and_add_duictionary(omim_id, dict_genemap2)


dict_same_label_different_values = {}


def combine_the_node_information():
    for omim_id, info_list in dict_omim_number_to_dict_of_information.items():
        dict_node = {}
        for dictionary in info_list:
            for key, value in dictionary.items():
                if key in dict_node and dict_node[key] != value:
                    if key not in dict_same_label_different_values:
                        dict_same_label_different_values[key] = list()
                    if (value, dict_node[key]) not in dict_same_label_different_values[key]:
                        dict_same_label_different_values[key].append((value, dict_node[key]))
                    continue
                dict_node[key] = value
    print(dict_same_label_different_values.keys())
    for key, lists in dict_same_label_different_values.items():
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
    print('Combine node information')

    combine_the_node_information()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
