import sys
import datetime
import csv, re
import wget
import os.path
import gzip, io

# list of all two letter codes in the order that they are used
list_two_character_type_order = ['ID',  # identification (x1) x
                                 'AC',  # accession number(s) (>= 1)
                                 'DT',  # date (x3) x
                                 'DE',  # description (>= 1)
                                 'GN',  # gene name(s) (optional)
                                 'OS',  # organism species (>= 1)
                                 'OG',  # organelle (optional)
                                 'OC',  # organism classification (>=1)
                                 'OX',  # taxonomy cross-reference (1x) x
                                 'OH',  # organism host (optional)
                                 'RN',  # reference number (>=1)
                                 'RP',  # reference position (>=1)
                                 'RC',  # reference comment(s) (optional)
                                 'RX',  # reference cross-reference (optional)
                                 'RG',  # reference group (>=! or optional if RA line)
                                 'RA',  # reference authors (>=1 or optional if RG line)
                                 'RT',  # reference title (optional)
                                 'RL',  # reference location (>=1)
                                 'CC',  # comments or notes (optional)
                                 'DR',  # database cross-references (optional)
                                 'PE',  # protein existence (x1) x
                                 'KW',  # keywords (optional)
                                 'FT',  # feature table data (>=1 in SwissProt, optional in TrEMBL)
                                 'SQ',  # sequence header (x1) x
                                 '  ', '//']

dict_two_character_type = {
    'ID': 'identification',  # identification (x1) x
    'AC': 'accession_numbers',  # accession number(s) (>= 1)
    'DT': 'date',  # date (x3) x
    'DE': 'description',  # description (>= 1)
    'GN': 'gene_names',  # gene name(s) (optional)
    'OS': 'organism_species',  # organism species (>= 1)
    'OG': 'organelle',  # organelle (optional)
    'OC': 'organism-classification',  # organism classification (>=1)
    'OX': 'taxonomy_cross-reference',  # taxonomy cross-reference (1x) x
    'OH': 'organism_host',  # organism host (optional)
    'RN': 'reference_number',  # reference number (>=1)
    'RP': 'reference position',  # reference position (>=1)
    'RC': 'reference_comments',  # reference comment(s) (optional)
    'RX': 'reference_cross-reference',  # reference cross-reference (optional)
    'RG': 'reference group',  # reference group (>=! or optional if RA line)
    'RA': 'reference_authors',  # reference authors (>=1 or optional if RG line)
    'RT': 'reference_title',  # reference title (optional)
    'RL': 'reference location',  # reference location (>=1)
    'CC': 'comments_or_notes',  # comments or notes (optional)
    'DR': 'database_cross-references',  # database cross-references (optional)
    'PE': 'protein existence',  # protein existence (x1) x
    'KW': 'keywords',  # keywords (optional)
    'FT': 'feature_table_data',  # feature table data (>=1 in SwissProt, optional in TrEMBL)
    'SQ': 'sequence_header',  # sequence header (x1) x
    '  ': 'sequence_data',  # sequence data (>=1 multiline) x

}

# open tsv file
file = open('output/uniprot.tsv', 'w')
header = ['entry', 'status', 'sequenceLength', 'identifier', 'second_ac_numbers', 'name', 'synonyms', 'ncbi_taxid',
          'as_sequence',
          'gene_name', 'general_function', 'chromosome_location', 'pfam', 'gene_id', 'go_classifiers', 'xrefs',
          'subcellular_location', 'protein_existence', 'pubmed_ids', 'pathway', 'disease']
csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
csv_writer.writeheader()

# count_all proteins
counter = 0

# path to project dictionary
if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path')

# all queries which are used to integrate Protein with the extra labels into Hetionet
cypherfile = open('output/cypher_protein.cypher', 'w')
query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/uniProt/output/uniprot.tsv" As line Fieldterminator '\\t' Create (n:Protein_Uniprot{ '''

'''
integrate the dictionary information into the csv file
'''


def integration_dict_info_into_csv(dict_information):
    # counter of all proteins which are integrated into the tsv file
    global counter, query

    for property, value in dict_information.items():

        # add all properties with the right type to the query
        if counter == 0:
            if type(value) in [list, set]:
                query += property + ':split(line.' + property + ',"|"), '
            else:
                query += property + ':line.' + property + ', '

        if type(value) == list:
            dict_information[property] = '|'.join(list(value))
        elif type(value) == set:
            dict_information[property] = '|'.join(list(value))

    csv_writer.writerow(dict_information)

    # finsih the query and write into the file
    if counter == 0:
        for head in header:
            if head not in dict_information:
                print(head)
                if head in ['disease', 'pathway']:
                    query += head + ':split(line.' + head + ',"|"), '
                else:
                    query += head + ':line.' + head + ', '
        query = query[:-2] + '});\n'
        cypherfile.write(query)
        query = 'Create Constraint On (node:Protein_Uniprot) Assert node.identifier Is Unique;\n'
        cypherfile.write(query)
    counter += 1


# def sort_function(two_character, dict_protein):
#     if

set_list_de_categories = set([])

# dictionary to replace the short form of the go classification into strings
dict_short_to_full_go = {
    'C:': 'component::',
    'F:': 'function::',
    'P:': 'process::'
}


def prepare_strings_for_list_elements(string):
    """
    prepare string for list elements
    :param string: string
    :return: string
    """
    return string.strip().replace('\n', '').replace('|', ',')


'''
extract all information from uniprot flat file  into csv
Take only proteins from human
'''


def extract_information():
    first_two_letter = ''
    dict_protein = {}
    position_line = 0
    is_human = True
    counter_all = 0
    counter_human = 0
    # first two letter were sq and the sequence are the lines below
    sq_before = False
    in_multiple_lines = False
    in_multiple_line_string = ''
    in_multiple_line_property = ''
    in_multiple_line_property_type_list = False

    # to get multiple line information of Function (general function) or subcellular location and nned to be which property
    general_function = False
    subcellular_location = False
    disease = False
    pathway = False

    print(sys.argv)
    # download url of swissprot

    if not os.path.exists('database/uniprot_sprot.dat.gz'):
        print('download')
        url_data = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz'
        # download ncbi human genes
        filename = wget.download(url_data, out='database/')
    else:
        filename = 'database/uniprot_sprot.dat.gz'

    unzip_file = open('database/uniprot_sprot.dat', 'w', encoding='utf-8')

    filename_without_gz = filename.rsplit('.', 1)[0]
    # file = open(filename_without_gz, 'wb')
    with io.TextIOWrapper(gzip.open(filename, 'rb')) as f:
        # file_uniprot = open(sys.argv[1], 'r')
        # with open('database/part.dat', 'r', encoding='utf-8') as f:

        for line in f:
            unzip_file.write(line)

            two_split = line.split('   ', 1)
            # if ',\n' in line:
            #     print(line)
            #     continue
            two_first_letter = line[0:2]

            # this is the end of one entry
            if two_first_letter == '//':
                counter_all += 1
                # print(dict_protein)

                sq_before = False
                if is_human:
                    counter_human += 1
                    integration_dict_info_into_csv(dict_protein)
                else:
                    is_human = True
                # sys.exit('first')
                dict_protein = {}
                position_line = 0

                # to get multiple line information of Function (general function) or subcellular location and nned to be which property
                general_function = False
                subcellular_location = False
                disease = False
                pathway = False

            # all the other information
            else:
                # ID   EntryName Status; SequenceLength.
                if position_line == 0:
                    values = re.sub('\s{2,}', ' ', two_split[1])
                    id_rest = values.split(' ', 1)
                    entry = id_rest[0]
                    status_seq = id_rest[1].split('; ')
                    status = status_seq[0]
                    seq_len = status_seq[1].split('.')[0]
                    dict_protein['entry'] = entry
                    dict_protein['status'] = status
                    dict_protein['sequenceLength'] = seq_len
                    position_line += 1
                # ac-numbers
                elif position_line == 1:
                    two_split[1] = two_split[1].replace(';\n', '')
                    if two_split[1].startswith('Q12851'):
                        print('test')
                    all_access_number = two_split[1].split('; ')
                    ac_list = set([])
                    for counter, ac_number in enumerate(all_access_number):
                        if counter == 0:
                            dict_protein['identifier'] = ac_number
                            # print(ac_number)

                        else:
                            ac_list.add(ac_number)
                    dict_protein['second_ac_numbers'] = list(ac_list)
                    position_line += 1
                # sometimes the information of one property are in multiple lines
                #
                elif in_multiple_lines:
                    # has more than one multiple line
                    if ',\n' in line:
                        if in_multiple_line_property == 'gene_name':
                            continue
                        print('multi multi')
                        in_multiple_line_string += two_split[1].replace('\n', '')
                    # end of one multiple line combination
                    else:
                        if in_multiple_line_property == 'gene_name':
                            if not '{' in two_split[1] and '}' in two_split[1]:
                                print('no new information')
                                print(two_split[1])
                            elif two_split[1].count('}') > 1:
                                print('no new information')
                                print(two_split[1])
                            else:
                                in_multiple_line_string += two_split[1].replace(';\n', '')
                                print('new informations')
                                print(two_split[1])
                        else:
                            in_multiple_line_string += two_split[1].replace(';\n', '')
                            print(in_multiple_line_property)
                            print('new informations')
                            print(two_split[1])

                        in_multiple_lines = False
                        if in_multiple_line_property_type_list:
                            if in_multiple_line_property in dict_protein:
                                dict_protein[in_multiple_line_property].add(in_multiple_line_string)
                            else:
                                dict_protein[in_multiple_line_property] = {in_multiple_line_string}
                        else:
                            dict_protein[in_multiple_line_property] = in_multiple_line_string
                # description
                elif two_first_letter == 'DE':
                    value = two_split[1]
                    if ': ' in value:
                        set_list_de_categories.add(value.split(': ')[0])
                        if value.split(': ')[0] == 'RecName':
                            subcategory_split = value.split(': ')[1].split('=')
                            if subcategory_split[0] == 'Full':
                                dict_protein['name'] = subcategory_split[1].replace(';\n', '')
                            elif subcategory_split[0] == 'Short':
                                if not 'synonyms' in dict_protein:
                                    dict_protein['synonyms'] = {
                                        subcategory_split[1].replace(';\n', '').replace('|', ';')}
                                else:
                                    dict_protein['synonyms'].add(
                                        subcategory_split[1].replace(';\n', '').replace('|', ';'))
                            # EC seems not to exists so I will exclude this from the file butl let this code included maybe i will need this later
                            else:
                                print({subcategory_split[1].replace(';\n', '')})
                                if not 'ecs' in dict_protein:
                                    dict_protein['ecs'] = {subcategory_split[1].replace(';\n', '')}
                                else:
                                    dict_protein['ecs'].add(subcategory_split[1].replace(';\n', ''))
                        elif value.split(': ')[0] == 'AltName':
                            subcategory_split = value.split(': ')[1].split('=')
                            # EC seems not to exists so I will exclude this from the file butl let this code included maybe i will need this later
                            if subcategory_split[0] == 'EC':
                                print({subcategory_split[1].replace(';\n', '')})
                                if not 'ecs' in dict_protein:
                                    dict_protein['ecs'] = {subcategory_split[1].replace(';\n', '')}
                                else:
                                    dict_protein['ecs'].add(subcategory_split[1].replace(';\n', ''))
                            else:
                                if not 'synonyms' in dict_protein:
                                    dict_protein['synonyms'] = {
                                        subcategory_split[1].replace(';\n', '').replace('|', ';')}
                                else:
                                    dict_protein['synonyms'].add(
                                        subcategory_split[1].replace(';\n', '').replace('|', ';'))



                # taxonomy cross-reference
                # OX  Taxonomy_database_qualifier=Taxonomic code;
                # ncbi_taxid=9606 == human
                # test if not multiple ox are in one line
                # position_line==8
                elif two_first_letter == 'OX':
                    source_value = two_split[1].split('=')
                    if len(source_value) > 2:
                        print(line)
                        sys.exit('OX')
                    # it is only ncbi_taxid in swissprot
                    # if source_value[0]!='ncbi_taxid':
                    #     print(line)
                    #     sys.exit('OX')
                    if not source_value[1].startswith('9606;') and not source_value[1].startswith('9606 {'):
                        is_human = False
                        dict_protein['ncbi_taxid'] = source_value[1].split(';')[0]
                    else:
                        dict_protein['ncbi_taxid'] = source_value[1].split(';')[0]
                        # sys.exit()
                    position_line += 1

                # CC   Comments and notes
                elif two_first_letter == 'CC':
                    if '-!-' in two_split[1]:
                        property_value = two_split[1].split(': ')
                        if property_value[0] == '-!- FUNCTION':
                            dict_protein['general_function'] = property_value[1].replace('\n', '')
                            general_function = True
                            subcellular_location = False
                            disease = False
                            pathway = False
                        elif property_value[0] == '-!- DISEASE':
                            if disease:
                                dict_protein['disease'].append(prepare_strings_for_list_elements(property_value[1]))
                            else:
                                dict_protein['disease'] = [prepare_strings_for_list_elements(property_value[1])]
                            general_function = False
                            subcellular_location = False
                            disease = True
                            pathway = False
                        elif property_value[0] == '-!- PATHWAY':
                            list_infos = list(filter(None, prepare_strings_for_list_elements(property_value[1]).split(';')))
                            if pathway:
                                dict_protein['pathway'].extend(list_infos)
                            else:
                                dict_protein['pathway'] = list_infos
                            general_function = False
                            subcellular_location = False
                            disease = False
                            pathway = True
                        elif property_value[0] == '-!- SUBCELLULAR LOCATION':
                            property_value[1]=property_value[1].replace('. Note',' Note')
                            list_infos = list(filter(None, prepare_strings_for_list_elements(property_value[1]).split('.')))
                            if subcellular_location:
                                dict_protein['subcellular_location'].extend(list_infos)
                            else:
                                dict_protein['subcellular_location'] = list_infos
                            general_function = False
                            subcellular_location = True
                            disease = False
                            pathway = False
                        else:
                            general_function = False
                            subcellular_location = False
                            disease = False
                            pathway = False


                    elif general_function:

                        dict_protein['general_function'] += ' ' + two_split[1].strip().replace('\n', '')
                    elif subcellular_location:
                        two_split[1]=two_split[1].replace('. Note',' Note')
                        prepared_list = list(filter(None, prepare_strings_for_list_elements(two_split[1]).split('.')))
                        dict_protein['subcellular_location'][-1] += ' ' + prepared_list[0]
                        dict_protein['subcellular_location'].extend(prepared_list[1:])
                    elif disease:
                        dict_protein['disease'][-1] += ' ' + prepare_strings_for_list_elements(two_split[1])
                    elif pathway:
                        prepared_list = list(filter(None, prepare_strings_for_list_elements(two_split[1]).split(';')))
                        dict_protein['pathway'][-1] += ' ' + prepared_list[0]
                        dict_protein['pathway'].extend(prepared_list[1:])

                # Protein existence
                # PE   Level:Evidence;
                elif two_first_letter == 'PE':
                    general_function = False
                    level_evidence = two_split[1].split(': ')
                    if len(level_evidence) > 2:
                        print(line)
                        sys.exit('PE')
                    dict_protein['protein_existence'] = level_evidence[1].replace(';\n', '')
                    position_line += 1

                # reference cross-reference (optional)
                # can also appear multiple time
                elif two_first_letter == 'RX':
                    splitted_cross_refs = two_split[1].split('; ')
                    if not len(splitted_cross_refs) > 1:
                        splitted_cross_refs = two_split[1].split(';')
                    if 'pubmed_ids' in dict_protein:
                        list_pubmed_ids = dict_protein['pubmed_ids']
                    else:
                        list_pubmed_ids = []
                    for cross_ref in splitted_cross_refs:
                        split_property_value = cross_ref.split('=')
                        if split_property_value[0] == 'PubMed':
                            list_pubmed_ids.append(split_property_value[1])
                    dict_protein['pubmed_ids'] = list_pubmed_ids

                # GN: gene name(s) (optional)
                # only the one with name
                elif two_first_letter == 'GN':
                    property = two_split[1].split('=')
                    if dict_protein['identifier'] == 'P30493':
                        print('huhu')
                    if property[0] == 'Name':

                        if ',\n' in two_split[1]:
                            in_multiple_lines = True
                            in_multiple_line_string = \
                                property[1].split(';')[0].replace('\n', '').replace('|', ';').split('{')[0].rstrip()
                            in_multiple_line_property = 'gene_name'
                            in_multiple_line_property_type_list = True
                        else:
                            gene_name = property[1].split(';')[0].replace('\n', '').replace('|', ';').split(' {')[
                                0].rstrip()

                            if not 'gene_name' in dict_protein:
                                dict_protein['gene_name'] = {gene_name}
                            else:
                                dict_protein['gene_name'].add(gene_name)
                            # print(property)
                            # print(line)
                            # print(property[1].split(';'))
                            synonyms = property[1].split(';')[1].split('=')
                            if synonyms[0] == ' Synonyms':
                                for synonym in property[2].split(', '):
                                    # print(property)
                                    dict_protein['gene_name'].add(
                                        synonym.split(';')[0].replace(';\n', '').replace('|', ';').split(' {')[
                                            0].rstrip())
                                    # if not 'synonyms' in dict_protein:
                                    #     dict_protein['synonyms'] = {synonym.replace(';\n', '')}
                                    # else:
                                    #     dict_protein['synonyms'].add(synonym.replace(';\n', ''))
                # database cross-references (optional)
                elif two_first_letter == 'DR':
                    xref_infos = two_split[1].split('; ')
                    if xref_infos[0] not in ['Pfam', 'GeneID']:
                        if 'xrefs' in dict_protein:
                            dict_protein['xrefs'].add(xref_infos[0] + ':' + xref_infos[1])
                        else:
                            dict_protein['xrefs'] = {xref_infos[0] + ':' + xref_infos[1]}
                    elif xref_infos[0] == 'Pfam':
                        if 'pfam' in dict_protein:
                            dict_protein['pfam'].add(xref_infos[1] + ':' + xref_infos[2])
                        else:
                            dict_protein['pfam'] = {xref_infos[1] + ':' + xref_infos[2]}
                    else:
                        if 'gene_id' in dict_protein:
                            dict_protein['gene_id'].add(xref_infos[1])
                        else:
                            dict_protein['gene_id'] = {xref_infos[1]}

                    if xref_infos[0] in ['GO', 'Proteomes']:
                        if xref_infos[0] == 'GO':
                            for short, full in dict_short_to_full_go.items():
                                if short == xref_infos[2][0:2]:
                                    xref_infos[2] = xref_infos[2].replace(short, full, 1)
                                    break
                            if 'go_classifiers' in dict_protein:
                                dict_protein['go_classifiers'].add(xref_infos[2])
                            else:
                                dict_protein['go_classifiers'] = {xref_infos[2]}
                        else:
                            if 'chromosome_location' in dict_protein:
                                dict_protein['chromosome_location'].add(xref_infos[2].replace('.\n', ''))
                            else:
                                dict_protein['chromosome_location'] = {xref_infos[2].replace('.\n', '')}

                # sequence header (x1)
                elif two_first_letter == 'SQ':
                    dict_protein['as_sequence'] = two_split[1].replace("\n", "")[:-1] + ':'
                    sq_before = True
                # sequence lines
                elif sq_before:
                    dict_protein['as_sequence'] += line.replace(" ", "").replace("\n", "")

                else:
                    position_line += 1

    print('all swiss prot proteins:' + str(counter_all))
    print('all swiss prot human proteins:' + str(counter_human))
    print(set_list_de_categories)


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('extract information')

    extract_information()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
