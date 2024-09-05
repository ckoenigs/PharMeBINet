import datetime
import os, sys, csv

import numpy as np
import pandas as pd
import sqlite3

sys.path.append("../..")
import pharmebinetutils


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

    query = 'Create (p:%s_DisGeNet{' % (label)
    for x in properties:
        if x in ['synonyms', 'code']:  # properties that are lists must be splitted
            query += x + ':split(line.' + x + ',"|"), '
        elif x in ['diseaseClass']:
            query += x + ':split(line.' + x + ',","), '
        else:
            query += x + ':line.' + x + ', '
    # delete last comma
    query = query[:-2] + '})'
    query = pharmebinetutils.get_query_import(home, destination + filename, query)
    cypher_file.write(query)

    cypher_file.write(pharmebinetutils.prepare_index_query(label + '_DisGeNet', unique_property))
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

    query = f'Match (p1:{label[0]}_DisGeNet{{{id_list[0]}:line.{id_list[0]}}}),(p2:{label[1]}_DisGeNet{{{id_list[1]}:line.{id_list[1]}}}) Create (p1)-[:{edge_name}{{  '
    for header in properties:
        # ignore key labels (wie diseaseId)
        if header in id_list:
            continue
        elif header in ['pmid', 'sourceId', 'associationType',
                        'sentence','years']:  # properties that are lists must be splitted
            query += f'{header}:split(line.{header},"|"), '
        elif header == 'NofSnps':
            query += header + 'String:line.' + header + ', '
        else:
            query += f'{header}:line.{header}, '

    query = query[:-2] + '}]->(p2)'
    query = pharmebinetutils.get_query_import(home, destination + filename, query)
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


def get_Node_information(query, properties):
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
    return test_dataframe


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
    file2 = pd.read_csv(os.path.join(source, name2), compression='gzip', sep='\t').convert_dtypes()

    # combine all sources to get list of unique gene_ids
    unique_gene_ids = get_Node_information(
        'Select geneId, geneName, geneDescription, pLI, DSI, DPI From geneAttributes;',
        ['geneId', 'geneSymbol', 'geneDescription', 'pLI', 'DSI', 'DPI'])

    unique_gene_ids['geneId'] = list(set(unique_gene_ids['geneId']).union(*[set(file2['geneId']), set(gene_ids)]))

    unique_gene_ids_list = unique_gene_ids['geneId'].unique()

    # sys.exit()
    # save Gene-Table to tsv
    unique_gene_ids = unique_gene_ids.replace('NA','')
    unique_gene_ids.to_csv(destination + 'gene.tsv', sep='\t', index=False, na_rep='')

    # Aggregate source info of identical variant-gene edges
    file2 = file2.drop('geneSymbol', axis=1).groupby(['snpId', 'geneId'], as_index=False).agg({'sourceId': set})
    file2['sourceId'] = file2['sourceId'].apply(lambda x: '|'.join(list(x)))
    # 2. save Gene-Variant edge info as table
    file2 = file2.replace('NA', '')
    file2.to_csv(destination + 'variant-gene.tsv', sep='\t', index=False, na_rep='')

    disease_df = get_Node_information(
        'Select diseaseId,diseaseName, type, group_concat(diseaseClass.diseaseClass) FROM diseaseAttributes LEFT OUTER JOIN disease2class On diseaseAttributes.diseaseNID=disease2class.diseaseNID LEFT OUTER JOIN diseaseClass On diseaseClass.diseaseClassNID=disease2class.diseaseClassNID Group BY diseaseAttributes.diseaseNID ;',
        ['diseaseId', 'diseaseName', 'diseaseType', 'diseaseClass'])

    disease_df = disease_df.drop_duplicates(
        keep='first')  # needed for later use
    # 3. save other part of curated gene_disease to edge-table, include pmids
    # subset all_gene_disease_associations to only curated entries
    # IDEA: Kombination von geneId&diseaseId aus file1 nehmen und auf file3 filtern
    curated = ['UNIPROT', 'CTD_human', 'ORPHANET', 'CLINGEN', 'GENOMICS_ENGLAND', 'CGI', 'PSYGENET']  # 'GWASCAT'
    curated_string = "','".join(curated)

    gene_disease_df = get_Node_information(
        f'Select diseaseId, geneId, source, association, associationType, sentence, pmid, score, EL, EI, year From geneDiseaseNetwork Inner Join diseaseAttributes On diseaseAttributes.diseaseNID=geneDiseaseNetwork.diseaseNID Inner Join geneAttributes On geneAttributes.geneNID=geneDiseaseNetwork.geneNID Where source in (\'{curated_string}\') ;',
        ['diseaseId', 'geneId', 'source', 'association', 'associationType', 'sentence', 'pmid', 'score', 'EL', 'EI',
         'years'])

    # Convert dtypes of YearInitial, YearFinal, pmid to INT
    gene_disease_df = gene_disease_df.convert_dtypes()

    gene_disease_df = gene_disease_df.replace('NA', '')

    gene_disease_df.pmid = gene_disease_df.pmid.astype(
        str)  # convert this column to string, in order to join later with pipes

    # aggregate the pmids for each gene + disease!!!
    pmidsFrame = gene_disease_df.groupby(['geneId', 'diseaseId'], as_index=False).agg(
        {'pmid': set, 'source': set, 'associationType': set, 'association': set, 'sentence': set, 'EL': set,
         'score': set, 'EI': set, 'years': set})
    # calculate the number of entries for each list under pmid-column
    pmidsFrame['NofPmids'] = pmidsFrame.apply(lambda df: len(list(filter(None, df['pmid']))), axis=1)

    print(pmidsFrame[['pmid', 'NofPmids']])
    for column in ['pmid', 'associationType', 'association', 'sentence', 'EL', 'source', 'score', 'EI', 'years']:
        pmidsFrame[column] = pmidsFrame[column].apply(lambda x: '|'.join([str(y) for y in list(filter(None, x))]))
    print(pmidsFrame['pmid'])
    print('end gene')
    # CHECKS
    # file1['check_num'] = file1['check_num'].where(file1['check_num'].notnull(), other=0.0) # set check_num to 0 where check_num is NaN
    # file1['check_num'] = file1['check_num'].apply(np.int64)
    # print(file1[['geneId', 'diseaseId', 'NofPmids', 'check_num', 'pmid']].head(20))
    # test = file1[file1['NofPmids'] != file1['check_num']]
    # print(test[['NofPmids', 'check_num', 'pmid']])
    # print(file1.iloc[284])
    # save gene-disease information as tsv

    pmidsFrame = pmidsFrame.replace('NA', '')
    pmidsFrame.to_csv(destination + 'gene-disease.tsv', sep='\t', index=False, na_rep='')
    return [pmidsFrame.diseaseId.unique(), file2.snpId.unique(), disease_df]


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

    unique_snp_ids = get_Node_information(
        'Select variantId, s, most_severe_consequence, chromosome, coord, DSI, DPI From variantAttributes;',
        ['snpId', 's', 'most_severe_consequence','chromosome', 'position', 'DSI', 'DPI'])

    # change dtype of 'position' column to INT
    unique_snp_ids = unique_snp_ids.convert_dtypes()
    unique_snp_ids['snpId'] = list(set(unique_snp_ids['snpId']).union(set(snp_ids)))
    unique_snp_ids =unique_snp_ids[['snpId', 's', 'most_severe_consequence','chromosome', 'position', 'DSI', 'DPI']].drop_duplicates(keep='first')
    # 1. save variant (node) table

    unique_snp_ids = unique_snp_ids.replace('NA', '')
    unique_snp_ids.to_csv(destination + 'variant.tsv', sep='\t', index=False, na_rep='')

    # 2. prepare variant-disease (edge) table
    # disease_info_vartbl = file1.


    curated = ['GWASCAT', 'CLINVAR', 'GWASDB', 'UNIPROT']
    curated_string = "','".join(curated)

    disease_variant_df = get_Node_information(
        f'Select diseaseId, variantId, association, associationType, sentence, source, pmid, score, EI, year From variantDiseaseNetwork  Inner Join diseaseAttributes On diseaseAttributes.diseaseNID=variantDiseaseNetwork.diseaseNID Inner Join variantAttributes On variantAttributes.variantNID=variantDiseaseNetwork.variantNID Where source in (\'{curated_string}\') ;',
        ['diseaseId', 'snpId', 'association', 'associationType', 'sentence', 'source', 'pmid', 'score', 'EI', 'years'])
    # Convert dtypes of YearInitial, YearFinal, pmid to INT
    disease_variant_df = disease_variant_df.convert_dtypes()
    disease_variant_df.pmid = disease_variant_df.pmid.astype(str)  # convert column to string in order to apply join-operation later on
    disease_variant_df = disease_variant_df.replace('NA', '')
    # aggregate the pmids for each variant + disease!!!
    pmidsFrame = disease_variant_df.groupby(['snpId', 'diseaseId'], as_index=False).agg(
        {'pmid': set, 'associationType': set, 'association': set,
         'sentence': set, 'source':set, 'pmid':set, 'score':set, 'EI':set, 'years':set})  # take set to not aggregate duplicates
    # calculate the number of entries for each list under pmid-column
    pmidsFrame['NofPmids'] = pmidsFrame.apply(lambda df: len(list(filter(None,df['pmid']))), axis=1)
    for column in ['pmid', 'associationType', 'association', 'sentence','source', 'score', 'EI', 'years']:
        pmidsFrame[column] = pmidsFrame[column].apply(lambda x: '|'.join([str(y) for y in list(filter(None, x))]))

    # CHECKS
    # file1['check_num'] = file1['check_num'].where(file1['check_num'].notnull(), other=0.0)  # set check_num to 0 where check_num is NaN
    # file1['check_num'] = file1['check_num'].apply(np.int64)
    # print(file1[['snpId', 'diseaseId', 'NofPmids', 'check_num', 'pmid']].head(20))
    # test = file1[file1['NofPmids'] != file1['check_num']]
    # print(test[['NofPmids', 'check_num', 'pmid']])
    pmidsFrame = pmidsFrame.replace('NA', '')
    pmidsFrame.to_csv(destination + 'variant-disease.tsv', sep='\t', index=False, na_rep='')
    return pmidsFrame.diseaseId.unique()


def get_diseaseInfo(disease_ids_genetbl, disease_ids_vartbl, disease_df):
    """
    combine disease-information from two tables
    :param disease_ids_genetbl: list of unique disease_ids (from curated_gene_disease_associations.tsv)
    :param disease_ids_vartbl: list of unique disease_ids (from curated_variant_disease_associations.tsv)
    :param disease_df_genetbl: list of disease-related columns, only unqiue rows (from all_gene_disease_pmid_associations_.tsv)
    """
    # load dataset
    name1 = 'disease_mappings.tsv.gz'
    file1 = pd.read_csv(os.path.join(source, name1), compression='gzip', sep='\t').convert_dtypes()
    name2 ='disease_mappings_to_attributes.tsv.gz'
    file2 = pd.read_csv(os.path.join(source, name2), compression='gzip', sep='\t').convert_dtypes()

    # combine the unique disease-entries of both datasets
    unique_ids = pd.DataFrame()
    unique_ids['diseaseId'] = list(set(file1['diseaseId']).union(*[set(disease_ids_genetbl), set(disease_ids_vartbl)]))
    # CHECK diseaseType, Class, semanticType (für gleiche diseaseID unterschiedlich?) --> dann liste für die verschiedenen types
    # check: file2[file2['diseaseName'] == 'Heart Diseases']
    disease_df = disease_df.drop_duplicates(keep='first')
    # merge the collected disease-info (disease_df) onto unique disease-ID's
    unique_ids = unique_ids.merge(disease_df, how='left', on=['diseaseId'], copy=False, sort=True)

    # subset file1 and combine two columns into one 'code-ID' (do not filter)
    file1['code'] = file1['vocabulary'] + ':' + file1['code']
    file1 = file1.drop('vocabulary', axis=1)
    file1.rename(columns={'name': 'diseaseName', 'vocabularyName': 'synonyms'}, inplace=True)
    file1 = file1.replace('NA', '')

    # group the different source-codes and synonyms of one disease together
    # list for vocab:code on same diseaseId, list for synonyms on same diseaseId
    file1_grouped = file1.groupby(['diseaseId', 'diseaseName'], as_index=False).agg(
        {'code': set, 'synonyms': set})  # take set to not aggregate duplicates
    # convert column of sets to column of lists
    file1_grouped['code'] = file1_grouped['code'].apply(lambda x: '|'.join(list(x)))
    file1_grouped['synonyms'] = file1_grouped['synonyms'].apply(lambda x: '|'.join(list(x)))

    file2 = file2.drop(
        columns=['umlsSemanticTypeId', 'doClassName', 'doClassId', 'hpoClassName', 'hpoClassId', 'diseaseClassNameMSH', 'diseaseClassMSH',
                 'type','name'])
    file2 = file2.rename(columns={'umlsSemanticTypeName':'diseaseSemanticType'})


    # combine the columns of the 2 datasets in the unique_ids table
    unique_ids = pd.merge(unique_ids, file1_grouped, on=['diseaseId', 'diseaseName'], how='left')
    unique_ids = pd.merge(unique_ids, file2, on=['diseaseId'], how='left')
    unique_ids = unique_ids.replace('NA', '')
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
    disease_ids_vartbl = get_variantInfo(snp_ids_genetbl)

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Call get_diseaseInfo for Disease information")
    # as input it gets the unique disease-ID's from gene/variant tables (arg 1,2) +
    # the disease-information Dataframes from all_gene/all_variant tables (arg 3,4)
    get_diseaseInfo(disease_ids_genetbl, disease_ids_vartbl, disease_df_genetbl)

    print(datetime.datetime.now())

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("Generate Cypher files")


    cypher_file_edge = open(destination + 'cypher_edge.cypher', 'w', encoding='utf-8')

    # dictionnary with the ID's that link the two nodes for each .tsv file
    edge_dict = {'variant-disease.tsv': ['associates', ['snpId', 'diseaseId']],
                 'gene-protein.tsv': ['interacts', ['geneId', 'UniProtKB']],
                 'gene-disease.tsv': ['interacts', ['geneId', 'diseaseId']],
                 'variant-gene.tsv': ['associates', ['snpId', 'geneId']]}
    for curr_file, list_typ_list_prop in edge_dict.items():
        # split the names into list with two node entries (make sure that the order of id_dict keys and order of the keys in list match)
        labels = curr_file.split('.', 1)[0].split('-')
        header = list(pd.read_csv(os.path.join(destination, curr_file), nrows=0, sep='\t').columns)
        id_list = list_typ_list_prop[1]
        edge_name = list_typ_list_prop[0]
        # print(f'file: {curr_file} \nlabel: {label} \nproperties: {header} \nid_list: {id_list}\n')
        cypher_edge(cypher_file_edge, curr_file, labels, header, id_list, edge_name)

    output_nodes = ['disease.tsv', 'protein.tsv', 'variant.tsv', 'gene.tsv']

    cypher_file = open(destination + 'cypher.cypher', 'w', encoding='utf-8')
    for curr_file in output_nodes:
        label = curr_file.split('.', 1)[0]
        header = pd.read_csv(os.path.join(destination, curr_file), nrows=0, sep='\t').columns
        # print(f'file: {curr_file} \nlabel: {label} \nproperties: {list(header)} \nidentifier: {header[0]}\n')
        cypher_node(cypher_file, curr_file, label, list(header), header[0])
        query =f'Match (p:{label}_DisGeNet) Where not (p)--() Delete p;\n'
        cypher_file_edge.write(query)

    cypher_file.close()
    cypher_file_edge.close()
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
