import csv
import sys
import datetime
import pandas as pd

cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

cypher_file_rela = open('output/cypher_rela.cypher', 'w', encoding='utf-8')

addition = '_ADReCSTarget'

# dictionary rela to tsv
dict_rela_to_tsv = {}


def generate_csv_file(labels, header, different_directory='', as_dict=False):
    """
    generate the tsv file for each label pair
    :param labels: tuple
    :param header: list of strings
    return csv writer and file name
    """

    dict_old_label_to_new_label = {}
    new_header = []
    for head in header:
        dict_old_label_to_new_label[head] = head.replace(' ', '_').replace(u'\ufeff', '')
        new_header.append(head.replace(' ', '_').replace(u'\ufeff', ''))

    file_name = 'output/' + different_directory + '_'.join(labels) + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    if not as_dict:
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(new_header)
    else:
        csv_writer = csv.DictWriter(file, fieldnames=new_header, delimiter='\t')
        csv_writer.writeheader()
    return csv_writer, file_name, dict_old_label_to_new_label


def combine_query(labels, file_name, query_end, identifier):
    """
    prepare cyfer query for the different nodes and write into file
    :param labels: tuple
    :param file_name: string
    :param query_end: string
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/adrecs_target/%s" As line FIELDTERMINATOR '\\t' Create (p:%s {''' + query_end
    join_addition = addition + ' :'
    query = query % (file_name, join_addition.join(labels) + addition)
    cypher_file.write(query)

    query = ''':begin \n Create Constraint On (node:%s) Assert node.%s Is Unique; \n :commit \n '''
    query = query % (join_addition.join(labels) + addition, identifier)
    cypher_file.write(query)


# label to identifier name
dict_label_to_identifier = {}


def prepare_query(labels, file_name, header, header_list, seperater, identifier):
    """
    prepare end of query and then combine all information
    :param seperater:string
    :param identifier: string
    :param labels: list
    :param file_name: string
    :param header: list
    :param header_list: list
    :return:
    """
    query_end = ''
    for head in header:
        if head in header_list:
            query_end += head + ':split(line.' + head + ',"' + seperater + '"), '
        else:
            query_end += head + ':line.' + head + ', '
    query_end = query_end[:-2] + '});\n'
    dict_label_to_identifier[labels[0]] = identifier
    combine_query(labels, file_name, query_end, identifier)


def prepare_query_rela(labe11, label2, file_name, id1, id2, rela_type, list_of_properties=[]):
    """
    prepare cypher query for rela
    :param labe11: string
    :param label2: string
    :param file_name: string
    :param id1: string
    :param id2: string
    :param rela_type: string
    :param list_of_properties: list
    :return:
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/adrecs_target/%s" As line FIELDTERMINATOR '\t' Match (p:%s{%s:line.%s}), (b:%s{%s:line.%s}) Create (p)-[:%s %s]->(b);\n'''
    if len(list_of_properties) > 0:
        properties = '{'
        for prop in list_of_properties:
            properties += prop + ':line.' + prop + ', '
        properties = properties[:-2] + '}'
    else:
        properties = ''

    query = query % (file_name, labe11 + addition, dict_label_to_identifier[labe11], id1, label2 + addition,
                     dict_label_to_identifier[label2], id2, rela_type, properties)
    cypher_file_rela.write(query)


def prepare_file_and_query_for_rela(label1, label2, id1, id2, rela_type, list_of_properties=[]):
    """
    generate tsv and and add to dictionary and generate cypher query
    :param label1: string
    :param label2: string
    :param id1: string
    :param id2: string
    :param rela_type: string
    :param list_of_properties: list
    :return:
    """
    csv_writer, file_name, dict_olt_to_new_labels = generate_csv_file([label1, label2], [id1, id2])
    dict_rela_to_tsv[rela_type] = csv_writer
    prepare_query_rela(label1, label2, file_name, id1, id2, rela_type, list_of_properties)


def prepare_file_and_query_for_node(labels, label, header, list_of_list_properties, list_symbole, identifier,
                                    as_dict=False):
    """
    prepare file and and cypher query
    :param labels: string
    :param label: string
    :param header: list string
    :param list_of_list_properties: list string
    :param list_symbole: string
    :param as_dict: boolean
    :return: dictionary old label to new
    """
    csv_writer, file_name, dict_old_to_new_label = generate_csv_file([labels], header, as_dict=as_dict)
    dict_label_to_csv_writer[labels] = csv_writer
    prepare_query([label], file_name, list(dict_old_to_new_label.values()), list_of_list_properties, list_symbole,
                  identifier)
    return dict_old_to_new_label


def prepare_dataframe(dataframe):
    """
    prepare data frame
    :param dataframe:
    :return: data frame
    """

    dataframe = dataframe.replace('(-)', '')
    dataframe = dataframe.replace('---', '')
    dataframe = dataframe.replace('Not Available', '')
    dataframe = dataframe.fillna('')
    dataframe = dataframe.replace(to_replace=r'^-$', value='', regex=True)
    dataframe = dataframe.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return dataframe


# set of target_drug_pairs
set_of_target_drug_pairs = set()

# dictionary_drug_name to information
dict_drug_name_to_information = {}

# dictionary label to csv_writer
dict_label_to_csv_writer = {}

# dictionary adr id to dictionary of infos
dict_adr_id_to_dict_infos = {}

# set_of_toxicities
set_of_toxicties = set()


def prepare_dictionary(dictionary):
    """
    Prepare in dictionary list or sets to string
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) in [list, set]:
            value = '|'.join([str(x) for x in value])
        new_dict[key] = value
    return new_dict


# set of ditop2 ids
set_ditop2_ids = set()

# set of ditop and adr pairs
dict_ditop_to_other_entities = {}

# set of all adr ids where same id but some information are different
set_of_all_adr_ids_where_difference = set()


def check_on_adr_information(identifier, dict_of_properties):
    """
    Check if id already exist or not and if so check if there exists complications!
    :param identifier:
    :param dict_of_properties:
    :return:
    """
    if identifier not in dict_adr_id_to_dict_infos:
        dict_adr_id_to_dict_infos[identifier] = dict_of_properties
    else:

        for key, value in dict_of_properties.items():

            if key == 'ADRECS_ID':
                if type(dict_adr_id_to_dict_infos[identifier][key]) == str:
                    dict_adr_id_to_dict_infos[identifier][key] = set([dict_adr_id_to_dict_infos[identifier][key]])
                dict_adr_id_to_dict_infos[identifier][key].add(value)
                continue
            if key == 'ADR_TERM':
                # are the same string but different writting with lower case
                continue

            if value != dict_adr_id_to_dict_infos[identifier][key]:
                set_of_all_adr_ids_where_difference.add(identifier)
                print('ohno different properties ;(')
                print(identifier)
                print(key)
                print(value)
                print(dict_adr_id_to_dict_infos[identifier][key])
                sys.exit()


def prepare_adrs():
    """"
    prepare the adr file for adr tsv and cypher
    DITOP2_ID	ADR_ID	ADRECS_ID	ADR_TERM	TOXICITY_DETAIL	ORGAISM	DATA_SOURCE

    """
    adrs = pd.read_excel('data/ALLTOXI_INFO.xlsx', index_col=None, sheet_name='all1')
    # print(adrs.head())
    header = list(adrs.columns)
    # print(header)
    # make the empty
    adr_properties = header[::]
    adr_properties.remove('DITOP2_ID')
    adr_properties.remove('ORGAISM')
    adr_properties.remove('DATA_SOURCE')
    adr_properties.remove('TOXICITY_DETAIL')

    header_adrs = adr_properties[::]
    header_adrs.append('identifier')

    # prepare dataframe
    adrs = prepare_dataframe(adrs)

    # variant information
    dict_old_to_new_label = prepare_file_and_query_for_node('adr', 'adr', header_adrs, ['ADRECS_ID'], '|', 'identifier',
                                                            as_dict=True)

    # ditop2 information
    header_ditop = ['DITOP2_ID', 'ORGAISM', 'DATA_SOURCE']
    prepare_file_and_query_for_node('ditop2', 'ditop2', header_ditop, [], ';', 'DITOP2_ID')

    # toxity information
    header_toxity = ['TOXICITY_DETAIL']
    prepare_file_and_query_for_node('toxicity', 'toxicity', header_toxity, [], ';', 'TOXICITY_DETAIL')

    # rela preparation
    prepare_file_and_query_for_rela('ditop2', 'adr', 'DITOP2_ID', 'identifier', 'ditop_adrs')

    # rela preparation
    prepare_file_and_query_for_rela('ditop2', 'toxicity', 'DITOP2_ID', 'TOXICITY_DETAIL', 'ditop_toxities')

    # all protein where some difference appears which were not considered
    set_of_all_protein_ids_where_difference = set()

    # rela info set
    dict_ditop_to_other_entities['ditop_adr'] = set()
    dict_ditop_to_other_entities['ditop_toxicity'] = set()

    for index, row in adrs.iterrows():

        ditop2 = row['DITOP2_ID']
        if ditop2 not in set_ditop2_ids:
            ditop_list = [row[x] for x in header_ditop]
            dict_label_to_csv_writer['ditop2'].writerow(ditop_list)
        set_ditop2_ids.add(ditop2)

        toxicity = row['TOXICITY_DETAIL']

        if toxicity not in set_of_toxicties:
            dict_label_to_csv_writer['toxicity'].writerow([toxicity])
            set_of_toxicties.add(toxicity)

        if (ditop2, toxicity) not in dict_ditop_to_other_entities['ditop_toxicity']:
            dict_ditop_to_other_entities['ditop_toxicity'].add((ditop2, toxicity))
            dict_rela_to_tsv['ditop_toxities'].writerow([ditop2, toxicity])

        # # adr node
        # if row['ADR_TERM'] != '':
        #     identifier = row['ADR_TERM'].lower()
        # else:
        #     continue

        if row['ADR_TERM'] != '' and row['ADR_ID'] != '':
            identifier = row['ADR_ID'] if row['ADR_ID'] != '' else row['ADR_TERM'].lower()
        else:
            continue

        if (ditop2, identifier) not in dict_ditop_to_other_entities['ditop_adr']:
            dict_ditop_to_other_entities['ditop_adr'].add((ditop2, identifier))
            dict_rela_to_tsv['ditop_adrs'].writerow([ditop2, identifier])

        dict_of_properties = {
            dict_old_to_new_label[node_property]: row[node_property] for node_property in adr_properties}
        dict_of_properties['identifier'] = identifier

        check_on_adr_information(identifier, dict_of_properties)

    print(set_of_all_protein_ids_where_difference)
    print('length of ditop', len(set_ditop2_ids))
    print('length name', len(dict_adr_id_to_dict_infos))


def prepare_drug():
    """"
    prepare the drug file for durg tsv and cypher, also seperate the drug to target information!
    Target_ID	BADD_DID	DrugBank_ID	Drug Name	Description	ATC	KEGG	PubChem	Drug_Synonym	NDC	Brand
    Indications	Molecular_Formula	CAS

    """
    drugs = pd.read_excel('data/ALLDRUG_INFO.xlsx', index_col=None, )
    # print(drugs.head())
    header = list(drugs.columns)
    # print(header)
    drug_properties = header[::]
    drug_properties.remove('Target_ID')

    # prepare dataframe
    drugs = prepare_dataframe(drugs)

    # prepare file and cypher query
    prepare_file_and_query_for_node('drug', 'drug', drug_properties, ['ATC', 'Drug_Synonym', 'NDC', 'Brand'], ';',
                                    'Drug_Name')

    # prepare rela ditop2 (target) to drug
    prepare_file_and_query_for_rela('ditop2', 'drug', 'DITOP2_ID', 'Drug_Name', 'ditop_drug')

    # rela preparation
    dict_ditop_to_other_entities['ditop_drug'] = set()

    for index, row in drugs.iterrows():
        drug_name = row['Drug Name'].lower()
        row['Drug Name'] = drug_name
        ditop2_id = row['Target_ID']
        if ditop2_id not in set_ditop2_ids:
            print('not in ditpot :O')
            print(ditop2_id)

        if (ditop2_id, drug_name) not in dict_ditop_to_other_entities['ditop_drug']:
            dict_ditop_to_other_entities['ditop_drug'].add((ditop2_id, drug_name))
            dict_rela_to_tsv['ditop_drug'].writerow([ditop2_id, drug_name])

        list_of_properties = [row[drug_property] for drug_property in drug_properties]

        if drug_name not in dict_drug_name_to_information:
            dict_drug_name_to_information[drug_name] = list_of_properties
            dict_label_to_csv_writer['drug'].writerow(list_of_properties)
        elif dict_drug_name_to_information[drug_name] != list_of_properties:
            print('ohno different properties ;(')
            print(drug_name)


# set of gene ids
set_of_gene_ids = set()

# path to gene tsv
file_name_gene = 'output/genes.tsv'


def prepare_genes():
    """"
    prepare the drug file for durg tsv and cypher, also seperate the drug to target information!
    GENE_ID	GENE_SYMBOL	GENE_FULL_NAME	SYNONYMS	CHROMOSOME	MAP_LOCATION	TYPE_OF_GENE	OTHER_DESIGNATIONS	DBXREFS

    """
    global set_of_gene_ids

    genes = pd.read_excel('data/ADRAlert_LINCS_Gene_inf.xlsx', index_col=None, )
    # print(genes.head())
    header = list(genes.columns)
    header = [x.replace(' ', '_') if type(x) == str else x for x in header]
    # print(header)
    # prepare dataframe
    genes = prepare_dataframe(genes)

    # prepare file and cypher query
    prepare_file_and_query_for_node('gene', 'gene', header, ['SYNONYMS', 'OTHER_DESIGNATIONS', 'DBXREFS'], '|',
                                    'GENE_ID')

    for index, row in genes.iterrows():
        dict_label_to_csv_writer['gene'].writerow(row)
        gene_id = row['GENE_ID']
        set_of_gene_ids.add(gene_id)


def prepare_variants():
    """"
    prepare the drug file for durg tsv and cypher, also seperate the drug to target information!
    BADD_TID	Variation_ID	UNIPROT_AC	Gene_Name	Gene_ID	Uniprot_ID	Class	Chrom	ChromStart	ChromEnd	Strand	Observed	Alleles	AlleleFreqs	PMID	Link	Data_Source

    """
    global set_of_gene_ids

    variants = pd.read_excel('data/SNP_Variation_INFO.xlsx', index_col=None, )
    # print(variants.head())
    header = list(variants.columns)
    # print(header)
    # make the empty
    variant_properties = header[::]
    variant_properties.remove('BADD_TID')
    variant_properties.remove('UNIPROT_AC')
    variant_properties.remove('Gene_Name')
    variant_properties.remove('Gene_ID')
    variant_properties.remove('Uniprot_ID')
    # prepare dataframe
    variants = prepare_dataframe(variants)

    # variant information

    dict_old_to_new_label = prepare_file_and_query_for_node('variants', 'variant', variant_properties,
                                                            ['PMID', 'Link', 'Data_Source'], ';', 'Variation_ID',
                                                            as_dict=True)

    # all variants where some difference appears which were not considered
    set_of_all_variant_ids_where_difference = set()

    # dictionary to consider all variant id to there infos
    dict_variant_id_to_infos = {}

    # dict variant rela pairs
    dict_variant_rela_pairs = {}
    dict_variant_rela_pairs['variant_gene'] = set()
    dict_variant_rela_pairs['variant_protein'] = set()

    dict_ditop_to_other_entities['ditop_variant'] = set()

    # rela preparation
    prepare_file_and_query_for_rela('ditop2', 'variant', 'BADD_TID', 'Variation_ID', 'ditop_variant')
    prepare_file_and_query_for_rela('variant', 'gene', 'Variation_ID', 'Gene_ID', 'variant_gene')
    prepare_file_and_query_for_rela('variant', 'protein', 'Variation_ID', 'UNIPROT_AC', 'variant_protein')

    for index, row in variants.iterrows():

        badd_tid = row['BADD_TID']
        if badd_tid not in set_ditop2_ids:
            print('not in ditpot :O')
            print(badd_tid)

        # variant node
        variant_id = row['Variation_ID']

        if not (badd_tid, variant_id) in dict_ditop_to_other_entities['ditop_variant']:
            dict_ditop_to_other_entities['ditop_variant'].add((badd_tid, variant_id))
            dict_rela_to_tsv['ditop_variant'].writerow([badd_tid, variant_id])

        # rela to gene
        gene_ids = row['Gene_ID']
        if gene_ids != '':
            counter = 0
            for gene_id in str(gene_ids).split(';'):
                if not int(gene_id) in set_of_gene_ids:
                    dict_label_to_csv_writer['gene'].writerow([ gene_id, '' ,row['Gene_Name']])
                    set_of_gene_ids.add(int(gene_id))
                if not (variant_id, gene_id) in dict_variant_rela_pairs['variant_gene']:
                    dict_variant_rela_pairs['variant_gene'].add((variant_id, gene_id))
                    dict_rela_to_tsv['variant_gene'].writerow([variant_id, gene_id])

                counter += 1

        protein_ids = row['UNIPROT_AC']
        if protein_ids != '':
            counter = 0
            for protein_id in protein_ids.split(';'):
                if protein_id == '-':
                    counter += 1
                    continue
                if protein_id not in dict_protein_id_to_dict_infos:
                    dict_info = {'UNIPROT_AC': protein_id, 'UNIPROT_ID': row['Uniprot_ID'].split(';')[counter]}
                    dict_label_to_csv_writer['protein'].writerow(dict_info)
                    dict_protein_id_to_dict_infos[protein_id] = []
                if not (variant_id, protein_id) in dict_variant_rela_pairs['variant_protein']:
                    dict_variant_rela_pairs['variant_protein'].add((variant_id, protein_id))
                    dict_rela_to_tsv['variant_protein'].writerow([variant_id, protein_id])
                counter += 1

        dict_of_properties = {dict_old_to_new_label[node_property]: row[node_property] for node_property in
                              variant_properties}

        if variant_id not in dict_variant_id_to_infos:
            dict_variant_id_to_infos[variant_id] = dict_of_properties
        else:

            for key, value in dict_of_properties.items():
                if key == 'PMID':
                    if type(dict_variant_id_to_infos[variant_id][key]) != set:
                        if dict_variant_id_to_infos[variant_id][key] == '':
                            dict_variant_id_to_infos[variant_id][key] = set()
                        else:
                            dict_variant_id_to_infos[variant_id][key] = set(
                                [int(dict_variant_id_to_infos[variant_id][key])])
                    if value == '':
                        continue
                    dict_variant_id_to_infos[variant_id][key].add(int(value))
                    continue
                if key in ['Link', 'Data_Source']:
                    if type(dict_variant_id_to_infos[variant_id][key]) != set:
                        dict_variant_id_to_infos[variant_id][key] = set(
                            [dict_variant_id_to_infos[variant_id][key]])

                    dict_variant_id_to_infos[variant_id][key].add(value)
                    continue

                # manual checked the position and strand
                if key in ['ChromEnd', 'ChromStart']:
                    if variant_id in ['rs17739794', 'rs6575353', 'rs3129900']:
                        if value > dict_variant_id_to_infos[variant_id][key]:
                            dict_variant_id_to_infos[variant_id][key] = value
                        continue
                    if variant_id == 'rs9274407':
                        if key == 'ChromEnd':
                            dict_variant_id_to_infos[variant_id][key] = 32665055
                        else:
                            dict_variant_id_to_infos[variant_id][key] = 32665055
                        continue
                if key == 'Strand' and variant_id == 'rs924607':
                    dict_variant_id_to_infos[variant_id][key] = '-'
                    continue

                if value != dict_variant_id_to_infos[variant_id][key]:
                    set_of_all_variant_ids_where_difference.add(variant_id)
                    print('ohno different properties ;(')
                    print(variant_id)
                    print(key)
                    print(value)
                    print(dict_variant_id_to_infos[variant_id][key])

    for _, dict_info in dict_variant_id_to_infos.items():
        dict_info = prepare_dictionary(dict_info)
        dict_label_to_csv_writer['variants'].writerow(dict_info)

    print(set_of_all_variant_ids_where_difference)


# dictionary protein id to dictionary of infos
dict_protein_id_to_dict_infos = {}


def prepare_proteins():
    """"
    prepare the protein file for protein tsv and cypher
    RID	UNIPROT_AC	UNIPROT_ID	Protein names	Gene names	GeneID	Function	String

    """
    global set_of_gene_ids

    protein = pd.read_excel('data/DITOP_PROTEIN_INFO.xlsx', index_col=None, )
    # print(protein.head())
    header = list(protein.columns)
    # print(header)
    # make the empty
    protein_properties = header[::]
    protein_properties.remove('RID')
    protein_properties.remove('String')
    protein_properties.remove('Gene names')
    protein_properties.remove('GeneID')

    # prepare dataframe
    protein = prepare_dataframe(protein)

    # variant information
    dict_old_to_new_label = prepare_file_and_query_for_node('protein', 'protein', protein_properties, [], ';',
                                                            'UNIPROT_AC', as_dict=True)

    # all protein where some difference appears which were not considered
    set_of_all_protein_ids_where_difference = set()

    # dict protein rela pairs
    dict_protein_rela_pairs = {}
    dict_protein_rela_pairs['protein_gene'] = set()

    dict_ditop_to_other_entities['ditop_protein'] = set()

    # rela preparation
    prepare_file_and_query_for_rela('ditop2', 'protein', 'RID', 'UNIPROT_AC', 'ditop_protein')
    prepare_file_and_query_for_rela('protein', 'gene', 'UNIPROT_AC', 'GeneID', 'protein_gene')

    for index, row in protein.iterrows():

        rid = row['RID']
        if not rid in set_ditop2_ids:
            print('not in ditop')
            print(rid)

        # protein node
        protein_id = row['UNIPROT_AC']
        if not (rid, protein_id) in dict_ditop_to_other_entities['ditop_protein']:
            dict_ditop_to_other_entities['ditop_protein'].add((rid, protein_id))
            dict_rela_to_tsv['ditop_protein'].writerow([rid, protein_id])

        gene_id = row['GeneID']
        if gene_id != '':
            if not int(gene_id) in set_of_gene_ids:
                dict_label_to_csv_writer['gene'].writerow([ gene_id])
                set_of_gene_ids.add(int(gene_id))
            if not (protein_id, gene_id) in dict_protein_rela_pairs['protein_gene']:
                dict_protein_rela_pairs['protein_gene'].add((protein_id, gene_id))
                dict_rela_to_tsv['protein_gene'].writerow([protein_id, gene_id])

        dict_of_properties = {
            dict_old_to_new_label[node_property]: row[node_property] for node_property in protein_properties}

        if protein_id not in dict_protein_id_to_dict_infos:
            dict_protein_id_to_dict_infos[protein_id] = dict_of_properties
        else:

            for key, value in dict_of_properties.items():
                if type(value) == str:
                    if value in dict_protein_id_to_dict_infos[protein_id][key]:
                        continue
                    elif dict_protein_id_to_dict_infos[protein_id][key] in value:
                        dict_protein_id_to_dict_infos[protein_id][key] = value
                        continue
                    elif len(value) > len(dict_protein_id_to_dict_infos[protein_id][key]):
                        dict_protein_id_to_dict_infos[protein_id][key] = value
                        continue
                    else:
                        continue

                if value != dict_protein_id_to_dict_infos[protein_id][key]:
                    set_of_all_protein_ids_where_difference.add(protein_id)
                    print('ohno different properties ;(')
                    print(protein_id)
                    print(key)
                    print(value)
                    print(dict_protein_id_to_dict_infos[protein_id][key])

    for _, dict_info in dict_protein_id_to_dict_infos.items():
        dict_info = prepare_dictionary(dict_info)
        dict_label_to_csv_writer['protein'].writerow(dict_info)

    print(set_of_all_protein_ids_where_difference)


def prepare_protein_drug_adr():
    """"
    prepare the protein file for protein drug adr tsv and cypher
    BADD_TID	ADR_ID	ADReCS ID	ADR Term	Uniprot AC	Drug_Name

    """
    protein_drug_adr = pd.read_excel('data/P_D_A.xlsx', index_col=None, )
    # print(protein.head())
    header = list(protein_drug_adr.columns)
    print(header)

    # prepare dataframe
    protein_drug_adr = prepare_dataframe(protein_drug_adr)

    # not mapped
    set_not_existing = set()
    set_adr = set()

    for index, row in protein_drug_adr.iterrows():

        ditop = row['BADD_TID']
        if not ditop in set_ditop2_ids:
            print('not in ditop')
            print(ditop)

        adr_id = row['ADR_ID'] if row['ADR_ID'] != '' else row['ADR Term'].lower()
        if (ditop, adr_id) not in dict_ditop_to_other_entities['ditop_adr']:
            new_dict = {'identifier': adr_id, 'ADR_ID': row['ADR_ID'], 'ADR_TERM': row['ADR Term'],
                        'ADRECS_ID': row['ADReCS ID']}
            check_on_adr_information(adr_id, new_dict)

            dict_ditop_to_other_entities['ditop_adr'].add((ditop, adr_id))
            dict_rela_to_tsv['ditop_adrs'].writerow([ditop, adr_id])

        # connection to protein
        uniprot_id = row['Uniprot AC']
        if not (ditop, uniprot_id) in dict_ditop_to_other_entities['ditop_protein']:
            print('in p_a_d protein')
            print((ditop, uniprot_id))
            dict_rela_to_tsv['ditop_protein'].writerow([ditop, uniprot_id])
            dict_ditop_to_other_entities['ditop_protein'].add((ditop, uniprot_id))

        drug_name = row['Drug_Name'].lower()

        if (ditop, drug_name) not in dict_ditop_to_other_entities['ditop_drug']:
            if drug_name not in dict_drug_name_to_information:
                dict_label_to_csv_writer['drug'].writerow(['', '', drug_name])
                dict_drug_name_to_information[drug_name] = []

            dict_ditop_to_other_entities['ditop_drug'].add((ditop, drug_name))
            dict_rela_to_tsv['ditop_drug'].writerow([ditop, drug_name])

    # print(len(set_not_existing))
    # print(set_not_existing)
    # print(len(set_adr),set_adr)


def prepare_variant_drug_adr():
    """"
    prepare the file for variant drug adr tsv and cypher
    BADD_TID	ADR_ID	ADReCS ID	ADR Term	Variation	Drug_Name

    """
    protein_drug_adr = pd.read_excel('data/V_D_A.xlsx', index_col=None, )
    # print(protein.head())
    header = list(protein_drug_adr.columns)
    print(header)

    # prepare dataframe
    protein_drug_adr = prepare_dataframe(protein_drug_adr)

    for index, row in protein_drug_adr.iterrows():

        ditop = row['BADD_TID']
        if not ditop in set_ditop2_ids:
            print('not in ditop')
            print(ditop)

        adr_id = row['ADR_ID'] if row['ADR_ID'] != '' else row['ADR Term'].lower()

        if (ditop, adr_id) not in dict_ditop_to_other_entities['ditop_adr']:
            new_dict = {'identifier': adr_id, 'ADR_ID': row['ADR_ID'], 'ADR_TERM': row['ADR Term'],
                        'ADRECS_ID': row['ADReCS ID']}
            check_on_adr_information(adr_id, new_dict)

            dict_ditop_to_other_entities['ditop_adr'].add((ditop, adr_id))
            dict_rela_to_tsv['ditop_adrs'].writerow([ditop, adr_id])

        # connection to protein
        variant_id = row['Variation']
        if not (ditop, variant_id) in dict_ditop_to_other_entities['ditop_variant']:
            print('in v_a_d variant')
            print((ditop, variant_id))

        drug_name = row['Drug_Name'].lower()

        if (ditop, drug_name) not in dict_ditop_to_other_entities['ditop_drug']:

            if drug_name not in dict_drug_name_to_information:
                dict_label_to_csv_writer['drug'].writerow(['', '', drug_name])
                dict_drug_name_to_information[drug_name] = []

            dict_ditop_to_other_entities['ditop_drug'].add((ditop, drug_name))
            dict_rela_to_tsv['ditop_drug'].writerow([ditop, drug_name])


def prepare_adr_gene_drug_rela():
    """"
        prepare the ADRAlert2GENE2ID file for gene drug adr tsv and cypher
        ADR ID	Drug_Name	GeneID	ADReCS ID	ADR Term
        In this file the ADR ID and ADReCS ID are switched!
    """
    global set_of_gene_ids

    gene_drug_adr = pd.read_excel('data/ADRAlert2GENE2ID.xlsx', index_col=None, )
    # print(protein.head())
    header = list(gene_drug_adr.columns)
    print(header)

    # prepare dataframe
    protein_drug_adr = prepare_dataframe(gene_drug_adr)

    # counter_triple_relationship
    counter_triple_relationship = 0

    # association information
    header_association = ['id']
    prepare_file_and_query_for_node('association', 'association', header_association, [], ';', 'id')

    # prepare association rela
    prepare_file_and_query_for_rela('association', 'adr', 'id', 'identifier', 'association_adrs')
    prepare_file_and_query_for_rela('association', 'drug', 'id', 'Drug_Name', 'association_drug')
    prepare_file_and_query_for_rela('association', 'gene', 'id', 'Gene_ID', 'association_gene')

    already_not_in = set()

    for index, row in protein_drug_adr.iterrows():
        counter_triple_relationship += 1

        dict_label_to_csv_writer['association'].writerow([counter_triple_relationship])

        # switched in file between ADR ID and ADReCS ID
        adr_id = row['ADReCS ID'] if row['ADReCS ID'] != '' else row['ADR Term'].lower()

        new_dict = {'identifier': adr_id, 'ADR_ID': row['ADReCS ID'], 'ADRECS_ID': row['ADR ID'],
                    'ADR_TERM': row['ADR Term']}
        check_on_adr_information(adr_id, new_dict)

        # write rela between adr and association
        dict_rela_to_tsv['association_adrs'].writerow([counter_triple_relationship, adr_id])

        gene_id = row['GeneID']

        if not int(gene_id) in set_of_gene_ids:
            dict_label_to_csv_writer['gene'].writerow([ gene_id])
            set_of_gene_ids.add(int(gene_id))

        # write rela between gene and association
        dict_rela_to_tsv['association_gene'].writerow([counter_triple_relationship, gene_id])

        # check on drug
        drug_name = row['Drug_Name'].lower()
        if drug_name=='':
            continue

        if drug_name not in dict_drug_name_to_information:
            dict_label_to_csv_writer['drug'].writerow(['', '', drug_name])
            dict_drug_name_to_information[drug_name] = []

        # write rela between gene and association
        dict_rela_to_tsv['association_drug'].writerow([counter_triple_relationship, drug_name])


def write_adr_csv_file():
    """
    Because information for adr are combined in the end the information are need to be written down
    :return:
    """
    for _, dict_info in dict_adr_id_to_dict_infos.items():
        new_dict = prepare_dictionary(dict_info)
        dict_label_to_csv_writer['adr'].writerow(new_dict)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        print(path_of_directory)
    else:
        sys.exit('need a path adrecs-target')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse adr to tsv')

    prepare_adrs()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse drug to tsv')

    prepare_drug()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse genes to tsv')

    prepare_genes()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse protein to tsv')

    prepare_proteins()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse variant to tsv')

    prepare_variants()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse protein drug adr')

    prepare_protein_drug_adr()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse variant drug adr')

    prepare_variant_drug_adr()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse adr drug protein')

    prepare_adr_gene_drug_rela()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('write adr information into tsv')

    write_adr_csv_file()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
