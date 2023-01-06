import datetime
import os, sys, csv

import numpy as np
import pandas as pd
import sqlite3


def create_connection_to_sqllite():
    """
    Generate connection to disgenet sqlLite version
    :return:
    """
    global con
    con = sqlite3.connect('data/disgenet_2020.db')


def cypher_node(cypher_file, filename, label, properties, unique_property):
    """
    :param cypher_file: destination file to write the queries to
    :param filename: name of source file
    :param label: e.g. gene, protein_db
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param unique_property: identifier (e.g. diseaseId)
    """

    query_start = 'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:' + os.path.join(home,
                                                                                                  destination + filename) + '" As line fieldterminator "\\t" '

    query = query_start + 'Create (p:%s_DisGeNet{' % (label)
    for x in properties:
        if x in ['synonyms', 'code']:  # properties that are lists must be splitted
            query += x + ':split(line.' + x + ',"|"), '
        else:
            query += x + ':line.' + x + ', '
    # delete last comma
    query = query[:-2] + '});\n'
    cypher_file.write(query)

    query2 = 'Create Constraint On (node:%s_DisGeNet) Assert node.%s Is Unique; \n' % (label, unique_property)
    cypher_file.write(query2)
    # write everything in same file


def cypher_edge(cypher_file, filename, label, properties, id_list, edge_name):
    """
    :param cypher_file: destination file to write the queries to
    :param filename: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param id_list: the keys that are only for matching (they do not need to be part of the edge-information)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query_start = 'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:' + os.path.join(home,
                                                                                                  destination + filename) + '" As line fieldterminator "\\t" '
    query = query_start + f'Match (p1:{label[0]}_DisGeNet{{{id_list[0]}:line.{id_list[0]}}}),(p2:{label[1]}_DisGeNet{{{id_list[1]}:line.{id_list[1]}}}) Create (p1)-[:{edge_name}{{  '
    for header in properties:
        # ignore key labels (wie diseaseId)
        if header in id_list:
            continue
        elif header in ['pmid', 'sourceId','associationType','sentence']:  # properties that are lists must be splitted
            query += f'{header}:split(line.{header},"|"), '
        else:
            query += f'{header}:line.{header}, '

    query = query[:-2] + '}]->(p2);\n'
    cypher_file.write(query)


def get_proteinInfo():
    """
    subset the data into different tables
        1. Uniprot-Protein-ID
        2. Relation protein to gene

    mapa_geneid_4_uniprot_crossref: UniProtKB	GENEID
    :return: list of unique gene-ID's
    """

    name1 = 'mapa_geneid_4_uniprot_crossref.tsv.gz'
    file1 = pd.read_csv(os.path.join(source, name1), compression='gzip', sep='\t').convert_dtypes()
    # file1 = pd.read_csv(os.path.join(source, name1), sep="\t").convert_dtypes()
    # 2. Relation protein to gene; edge-information (can simply be copied, contains no duplicates)
    file1.rename(columns={'GENEID': 'geneId'},
                 inplace=True)  # need to rename column "GENEID" to "geneId" for later coherence
    file1.to_csv(destination + 'gene-protein.tsv', sep='\t', index=False)
    # 1. Uniprot-Protein-ID information
    proteins = pd.DataFrame(file1.UniProtKB.unique(), columns=['UniProtKB'])
    proteins.to_csv(destination + 'protein.tsv', sep='\t', index=False)
    # return gene-id in set for later use
    return list(set(file1['geneId']))


def prepare_sqllite_info_and_combine(query, properties, on_properties, integrated_dataframe):
    """
    Load data from sqlLite and prepare a dataframe. Merge the information into another dataframe and return this combined dataframe
    :param query: string
    :param properties: list of strings
    :param on_properties: list of strings
    :param integrated_dataframe: dataframe
    :return:  dataframe
    """
    cur = con.cursor()
    list_of_rows = []
    for row in cur.execute(query):
        list_of_rows.append(list(row))

    test_dataframe = pd.DataFrame(np.array(list_of_rows), columns=properties)
    test_dataframe = test_dataframe.fillna('')
    return integrated_dataframe.merge(test_dataframe, on=on_properties, how='left', copy=False, sort=True)


def get_geneInfo(gene_ids):
    """
    divide gene-related tables into node and edge information
        1. Gene table (node)
        2. gene-variant table (edge)
        3. gene-disease table (edge):

    all_gene_disease_pmid_associations: geneId	geneSymbol	DSI	DPI	diseaseId	diseaseName	diseaseType	diseaseClass	diseaseSemanticType	score	EI	YearInitial	YearFinal	pmid	source
    curated_gene_disease_associations: geneId	geneSymbol	DSI	DPI	diseaseId	diseaseName	diseaseType	diseaseClass	diseaseSemanticType	score	EI	YearInitial	YearFinal	NofPmids	NofSnps	source
    variant_to_gene_mappings: snpId	geneId	geneSymbol	sourceId
    :param gene_ids: list (aus mapa_geneid_4_uniprot_crossref.tsv)
    :return: list of lists
    """

    name1 = "curated_gene_disease_associations.tsv.gz"
    name2 = "variant_to_gene_mappings.tsv.gz"
    name3 = "all_gene_disease_pmid_associations.tsv.gz"
    file1 = pd.read_csv(os.path.join(source, name1), compression='gzip', sep='\t').convert_dtypes()
    file2 = pd.read_csv(os.path.join(source, name2), compression='gzip', sep='\t').convert_dtypes()
    file3 = pd.read_csv(os.path.join(source, name3), compression='gzip', sep='\t').convert_dtypes()


    # combine all sources to get list of unique gene_ids
    unique_gene_ids = pd.DataFrame()
    unique_gene_ids['geneId'] = list(set(file1['geneId']).union(*[set(file2['geneId']), set(gene_ids)]))

    unique_gene_ids_list = unique_gene_ids['geneId'].unique()

    # 1. map column gene_symbol onto new dataframe with the unique IDs
    right = file1[['geneId', 'geneSymbol', 'DSI', 'DPI']].drop_duplicates(subset=['geneId'])
    unique_gene_ids = unique_gene_ids.merge(right, on=['geneId'], how='left', copy=False, sort=True)

    unique_gene_ids = prepare_sqllite_info_and_combine('Select geneId, geneDescription, pLI From geneAttributes;',
                                                       ['geneId', 'geneDescription', 'pLI'], ['geneId'],
                                                       unique_gene_ids)
    # sys.exit()
    # save Gene-Table to tsv
    unique_gene_ids.to_csv(destination + 'gene.tsv', sep='\t', index=False, na_rep='')

    # Aggregate source info of identical variant-gene edges
    file2 = file2.drop('geneSymbol', axis=1).groupby(['snpId', 'geneId'], as_index=False).agg({'sourceId': set})
    file2['sourceId'] = file2['sourceId'].apply(lambda x: '|'.join(list(x)))
    # 2. save Gene-Variant edge info as table
    file2.to_csv(destination + 'variant-gene.tsv', sep='\t', index=False, na_rep='')

    disease_df = file3[
        ['diseaseId', 'diseaseName', 'diseaseType', 'diseaseClass', 'diseaseSemanticType']].drop_duplicates(
        keep='first')  # needed for later use
    # drop irrelevant coulumns for gene-disease edge
    file3 = file3.drop(
        columns=['geneSymbol', 'DSI', 'DPI', 'diseaseName', 'diseaseType', 'diseaseClass', 'diseaseSemanticType'])
    file1 = file1.drop(
        columns=['geneSymbol', 'DSI', 'DPI', 'diseaseName', 'diseaseType', 'diseaseClass', 'diseaseSemanticType'])
    # 3. save other part of curated gene_disease to edge-table, include pmids
    # subset all_gene_disease_associations to only curated entries
    # IDEA: Kombination von geneId&diseaseId aus file1 nehmen und auf file3 filtern
    curated = ['UNIPROT', 'CTD_human', 'ORPHANET', 'CLINGEN', 'GENOMICS_ENGLAND', 'CGI', 'PSYGENET']  # 'GWASCAT'
    file3 = file3[file3.source.isin(curated)]
    file3 = file3.dropna(subset=['pmid'])  # drop the rows that have NaN-entries in pmid
    file3 = file3.merge(file1[['geneId', 'diseaseId']], on=['geneId', 'diseaseId'], how='inner', copy=False, sort=True)

    file3 = prepare_sqllite_info_and_combine(
        'Select diseaseId, geneId, association, associationType, sentence, EL From geneDiseaseNetwork  Inner Join diseaseAttributes On diseaseAttributes.diseaseNID=geneDiseaseNetwork.diseaseNID Inner Join geneAttributes On geneAttributes.geneNID=geneDiseaseNetwork.geneNID;',
        ['diseaseId', 'geneId', 'association', 'associationType', 'sentence', 'EL'], ['diseaseId', 'geneId'],
        file3)

    # Convert dtypes of YearInitial, YearFinal, pmid to INT
    file3 = file3.convert_dtypes()

    file3.pmid = file3.pmid.astype(str)  # convert this column to string, in order to join later with pipes

    # aggregate the pmids for each gene + disease!!!
    pmidsFrame = file3.groupby(['geneId', 'diseaseId'], as_index=False).agg(
        {'pmid': set, 'associationType': set, 'association': set, 'sentence': set, 'EL': set})
    print(pmidsFrame)
    # calculate the number of entries for each list under pmid-column
    pmidsFrame['check_num'] = pmidsFrame.apply(lambda df: len(df['pmid']), axis=1)
    for column in ['pmid', 'associationType', 'association', 'sentence', 'EL']:
        pmidsFrame[column] = pmidsFrame[column].apply(lambda x: '|'.join([str(y) for y in list(filter(None, x))]))
    # Merge gene-disease table with extra pmid info
    file1 = file1.merge(pmidsFrame, on=['geneId', 'diseaseId'], how='left', copy=False, sort=True)
    # CHECKS
    # file1['check_num'] = file1['check_num'].where(file1['check_num'].notnull(), other=0.0) # set check_num to 0 where check_num is NaN
    # file1['check_num'] = file1['check_num'].apply(np.int64)
    # print(file1[['geneId', 'diseaseId', 'NofPmids', 'check_num', 'pmid']].head(20))
    # test = file1[file1['NofPmids'] != file1['check_num']]
    # print(test[['NofPmids', 'check_num', 'pmid']])
    # print(file1.iloc[284])
    # save gene-disease information as tsv
    file1.drop('check_num', axis=1).to_csv(destination + 'gene-disease.tsv', sep='\t', index=False, na_rep='')
    return [file1.diseaseId.unique(), file2.snpId.unique(), disease_df]


def get_variantInfo(snp_ids):
    """
    divide variant-related tables into node and edge information
        1. variant table (node)
        3. variant-disease table (edge)
    :param snp_ids: list (from variant_to_gene_mappings.tsv)


    curated_variant_disease_associations : snpId	chromosome	position	DSI	DPI	diseaseId	diseaseName	diseaseType	diseaseClass	diseaseSemanticType	score	EI	YearInitial	YearFinal	NofPmids	source
    all_variant_disease_pmid_associations: snpId	chromosome	position	DSI	DPI	diseaseId	diseaseName	diseaseType	diseaseClass	diseaseSemanticType	score	EI	YearInitial	YearFinal	pmid	source

    :return 1: list of unique diseaseId's (from curated_variant_disease_associations.tsv)
    :return 2: dataframe of disease-related-Information (from all_variant_disease_pmid_associations.tsv)
    """

    name1 = "curated_variant_disease_associations.tsv.gz"
    name2 = "all_variant_disease_pmid_associations.tsv.gz"
    file1 = pd.read_csv(os.path.join(source, name1), compression='gzip', sep='\t').convert_dtypes()
    file2 = pd.read_csv(os.path.join(source, name2), compression='gzip', sep='\t').convert_dtypes()

    unique_snp_ids = pd.DataFrame()
    unique_snp_ids['snpId'] = list(set(file1['snpId']).union(set(snp_ids)))
    # subset the dataframe and filter out duplicates (keep only first entry of duplicates)
    right = file1[['snpId', 'chromosome', 'position', 'DSI', 'DPI']].drop_duplicates(keep='first')
    # print(right[right['snpId'] == 'rs1000579'])
    # merge the previously subsetted df onto the unique snp-ID table
    unique_snp_ids = unique_snp_ids.merge(right, how='left', on=['snpId'], copy=False, sort=True)

    unique_snp_ids = prepare_sqllite_info_and_combine(
        'Select variantId, s, most_severe_consequence From variantAttributes;',
        ['snpId', 's', 'most_severe_consequence'], ['snpId'],
        unique_snp_ids)

    # change dtype of 'position' column to INT
    unique_snp_ids = unique_snp_ids.convert_dtypes()
    # 1. save variant (node) table
    unique_snp_ids.to_csv(destination + 'variant.tsv', sep='\t', index=False, na_rep='')

    # 2. prepare variant-disease (edge) table
    # disease_info_vartbl = file1.
    file1 = file1.drop(
        columns=['chromosome', 'position', 'DSI', 'DPI', 'diseaseName', 'diseaseType', 'diseaseClass',
                 'diseaseSemanticType'])
    disease_df = file2[
        ['diseaseId', 'diseaseName', 'diseaseType', 'diseaseClass', 'diseaseSemanticType']].drop_duplicates(
        keep='first')  # needed for later use
    file2 = file2.drop(
        columns=['chromosome', 'position', 'DSI', 'DPI', 'diseaseName', 'diseaseType', 'diseaseClass',
                 'diseaseSemanticType'])
    curated = ['GWASCAT', 'CLINVAR', 'GWASDB', 'UNIPROT', 'GWASCAT;GWASDB', 'CLINVAR;UNIPROT', 'CLINVAR;GWASCAT',
               'CLINVAR;GWASDB', 'CLINVAR;GWASCAT;GWASDB', 'GWASCAT;GWASDB;UNIPROT', 'GWASCAT;UNIPROT']
    file2 = file2[file2.source.isin(curated)]
    # drop the rows that have NaN-entries in pmid
    file2 = file2.dropna(subset=['pmid'])
    file2 = file2.merge(file1[['snpId', 'diseaseId']], on=['snpId', 'diseaseId'], how='inner', copy=False,
                        sort=True)  # include column information of other file1
    file2 = prepare_sqllite_info_and_combine(
        'Select diseaseId, variantId, association, associationType, sentence From variantDiseaseNetwork  Inner Join diseaseAttributes On diseaseAttributes.diseaseNID=variantDiseaseNetwork.diseaseNID Inner Join variantAttributes On variantAttributes.variantNID=variantDiseaseNetwork.variantNID;',
        ['diseaseId', 'snpId', 'association', 'associationType', 'sentence'], ['diseaseId', 'snpId'],
        file2)
    # Convert dtypes of YearInitial, YearFinal, pmid to INT
    file2 = file2.convert_dtypes()
    file2.pmid = file2.pmid.astype(str)  # convert column to string in order to apply join-operation later on
    # aggregate the pmids for each gene + disease!!!
    pmidsFrame = file2.groupby(['snpId', 'diseaseId'], as_index=False).agg(
        {'pmid': set, 'associationType': set, 'association': set,
         'sentence': set})  # take set to not aggregate duplicates
    # calculate the number of entries for each list under pmid-column
    pmidsFrame['check_num'] = pmidsFrame.apply(lambda df: len(df['pmid']), axis=1)
    for column in ['pmid', 'associationType', 'association', 'sentence']:
        pmidsFrame[column] = pmidsFrame[column].apply(lambda x: '|'.join([str(y) for y in list(filter(None, x))]))

    # Merge gene-disease table with extra pmid info
    file1 = file1.merge(pmidsFrame, on=['snpId', 'diseaseId'], how='left', copy=False, sort=True)
    # CHECKS
    # file1['check_num'] = file1['check_num'].where(file1['check_num'].notnull(), other=0.0)  # set check_num to 0 where check_num is NaN
    # file1['check_num'] = file1['check_num'].apply(np.int64)
    # print(file1[['snpId', 'diseaseId', 'NofPmids', 'check_num', 'pmid']].head(20))
    # test = file1[file1['NofPmids'] != file1['check_num']]
    # print(test[['NofPmids', 'check_num', 'pmid']])
    file1.drop('check_num', axis=1).to_csv(destination + 'variant-disease.tsv', sep='\t', index=False, na_rep='')
    return [file1.diseaseId.unique(), disease_df]


def get_diseaseInfo(disease_ids_genetbl, disease_ids_vartbl, disease_df_genetbl, disease_df_vartbl):
    """
    combine disease-information from two tables
    :param disease_ids_genetbl: list of unique disease_ids (from curated_gene_disease_associations.tsv)
    :param disease_ids_vartbl: list of unique disease_ids (from curated_variant_disease_associations.tsv)
    :param disease_df_genetbl: list of disease-related columns, only unqiue rows (from all_gene_disease_pmid_associations_.tsv)
    :param disease_df_vartbl: list of disease-related columns, only unique rows (from all_variant_disease_pmid_associations.tsv)
    """
    # load dataset
    name1 = 'disease_mappings.tsv.gz'
    file1 = pd.read_csv(os.path.join(source, name1), compression='gzip', sep='\t').convert_dtypes()

    # combine the unique disease-entries of both datasets
    unique_ids = pd.DataFrame()
    unique_ids['diseaseId'] = list(set(file1['diseaseId']).union(*[set(disease_ids_genetbl), set(disease_ids_vartbl)]))
    # CHECK diseaseType, Class, semanticType (für gleiche diseaseID unterschiedlich?) --> dann liste für die verschiedenen types
    # check: file2[file2['diseaseName'] == 'Heart Diseases']
    disease_df= pd.concat([disease_df_genetbl,disease_df_vartbl])
    disease_df=disease_df.drop_duplicates(keep='first')
    # merge the collected disease-info (disease_df) onto unique disease-ID's
    unique_ids = unique_ids.merge(disease_df, how='left', on=['diseaseId'], copy=False, sort=True)

    # subset file1 and combine two columns into one 'code-ID' (do not filter)
    file1['code'] = file1['vocabulary'] + ':' + file1['code']
    file1 = file1.drop('vocabulary', axis=1)
    file1.rename(columns={'name': 'diseaseName', 'vocabularyName': 'synonyms'}, inplace=True)

    # group the different source-codes and synonyms of one disease together
    # list for vocab:code on same diseaseId, list for synonyms on same diseaseId
    file1_grouped = file1.groupby(['diseaseId', 'diseaseName'], as_index=False).agg(
        {'code': set, 'synonyms': set})  # take set to not aggregate duplicates
    # convert column of sets to column of lists
    file1_grouped['code'] = file1_grouped['code'].apply(lambda x: '|'.join(list(x)))
    file1_grouped['synonyms'] = file1_grouped['synonyms'].apply(lambda x: '|'.join(list(x)))

    # combine the columns of the 2 datasets in the unique_ids table
    unique_ids = pd.merge(unique_ids, file1_grouped, on=['diseaseId', 'diseaseName'], how='left')
    unique_ids.to_csv(destination + 'disease.tsv', sep='\t', index=False, na_rep='')


def main():
    global destination
    global source
    global home

    if len(sys.argv) == 2:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need path to project (disgenet)')

    # get current working directories
    destination = 'output/'
    os.chdir(path_of_directory + 'import_into_Neo4j/DisGeNET')
    home = os.getcwd()
    source = os.path.join(home, 'data')

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Create connection to sql lite")

    create_connection_to_sqllite()

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Call gene_proteinInfo to generate Protein related info-tables")
    # return unique Gene-ID's from 'mapa_geneid_4_uniprot.tsv' as side-product for later use
    gene_ids_prottbl = get_proteinInfo()

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Call get_geneInfo for Gene related information")
    # return unique disease-ID's, snp-ID's, and disease-Information as side-product for later use
    disease_ids_genetbl, snp_ids_genetbl, disease_df_genetbl = get_geneInfo(gene_ids_prottbl)

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Call get_variantInfo for Variant related information")
    # return unique disease-ID's and DF of disease-Information as side product for later use
    disease_ids_vartbl, disease_df_vartbl = get_variantInfo(snp_ids_genetbl)

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Call get_diseaseInfo for Disease information")
    # as input it gets the unique disease-ID's from gene/variant tables (arg 1,2) +
    # the disease-information Dataframes from all_gene/all_variant tables (arg 3,4)
    get_diseaseInfo(disease_ids_genetbl, disease_ids_vartbl, disease_df_genetbl, disease_df_vartbl)

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Generate Cypher files")
    # select the files from output directory
    output_files = [f for f in os.listdir(destination) if
                    os.path.isfile(os.path.join(destination, f)) and f.endswith(".tsv")]
    output_nodes = ['disease.tsv', 'protein.tsv', 'variant.tsv', 'gene.tsv']
    output_edges = list(set(output_files) - set(output_nodes))

    cypher_file = open(destination + 'cypher.cypher', 'w', encoding='utf-8')
    for curr_file in output_nodes:
        label = curr_file.split('.', 1)[0]
        header = pd.read_csv(os.path.join(destination, curr_file), nrows=0, sep='\t').columns
        # print(f'file: {curr_file} \nlabel: {label} \nproperties: {list(header)} \nidentifier: {header[0]}\n')
        cypher_node(cypher_file, curr_file, label, list(header), header[0])

    # dictionnary with the ID's that link the two nodes for each .tsv file
    id_dict = {'variant-disease.tsv': ['snpId', 'diseaseId'], 'gene-protein.tsv': ['geneId', 'UniProtKB'],
               'gene-disease.tsv': ['geneId', 'diseaseId'], 'variant-gene.tsv': ['snpId', 'geneId']}
    edge_dict = {'variant-disease.tsv': 'associates', 'gene-protein.tsv': 'interacts', 'gene-disease.tsv': 'interacts',
                 'variant-gene.tsv': 'associates'}
    for curr_file in output_edges:
        label = curr_file.split('.', 1)[0].split(
            '-')  # split the names into list with two node entries (make sure that the order of id_dict keys and order of the keys in list match)
        header = list(pd.read_csv(os.path.join(destination, curr_file), nrows=0, sep='\t').columns)
        id_list = id_dict[curr_file]
        edge_name = edge_dict[curr_file]
        # print(f'file: {curr_file} \nlabel: {label} \nproperties: {header} \nid_list: {id_list}\n')
        cypher_edge(cypher_file, curr_file, label, header, id_list, edge_name)

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
