import sys, datetime
from io import BytesIO
from requests import get
import pandas as pd

sys.path.append("../..")
import pharmebinetutils

# cypher file
cypher_file = open('cypher.cypher', 'a', encoding='utf-8')
cypher_file_edge = open('cypher_edge.cypher', 'a', encoding='utf-8')


def generate_csv_file_and_prepare_cypher_queries(keys, file_name, label, unique_identifier):
    """
    generate node file as csv. Additionaly, generate cpher query to integrate node into neo4j with index.
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    :return: csv writer
    """

    # generate node query and indices
    query = """ Create (n:%s_go{  """
    query = query % (label)
    for head in keys:
        head_short = head.split('_')[0]
        if head_short in ['synonyms']:
            query += head_short + ":split(line." + head + ",'|'), "
        else:
            query += head_short + ":line." + head + ", "
    query = query[:-2] + "})"
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/GO/{file_name}', query)
    cypher_file.write(query)
    cypher_file.write(pharmebinetutils.prepare_index_query(label + '_go', unique_identifier))


def generate_csv_file_and_prepare_cypher_queries_edge(file_name, label, rela_type, rela_properties):
    """
    Gnerate cpher query to integrate the edge into neo4j.
    :param file_name: string
    :param label: string
    :param rela_type: string
    :param rela_properties: list
    """

    # generate node query and indices
    query = """ Match (n:go{ id:line.go_id}), (m:%s_go {identifier:line.identifier_node1}) Create (m)-[:%s{"""
    for head in rela_properties:
        if head in ['identifier_node1', 'go_id']:
            continue
        if head in ['db_reference', 'with_from', 'annotation_extension', 'assigned_by', 'gene_product_id', 'date']:
            query += head + ":split(line." + head + ",'|'), "
        else:
            query += head + ":line." + head + ", "

    query = query[:-2] + "}]->(n)"
    query = query % (label, rela_type)
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/GO/{file_name}', query)
    cypher_file_edge.write(query)


dict_evidence_code_to_evidence = {
    # experimental evidence
    'EXP': 'Inferred from Experiment',
    'IDA': 'Inferred from Direct Assay',
    'IPI': 'Inferred from Physical Interaction',
    'IMP': 'Inferred from Mutant Phenotype',
    'IGI': 'Inferred from Genetic Interaction',
    'IEP': 'Inferred from Expression Pattern',
    'HTP': 'Inferred from High Throughput Experiment',
    'HDA': 'Inferred from High Throughput Direct Assay',
    'HMP': 'Inferred from High Throughput Mutant Phenotype',
    'HGI': 'Inferred from High Throughput Genetic Interaction',
    'HEP': 'Inferred from High Throughput Expression Pattern',
    # Phylogenetically-inferred annotations
    'IBA': 'Inferred from Biological aspect of Ancestor',
    'IBD': 'Inferred from Biological aspect of Descendant',
    'IKR': 'Inferred from Key Residues',
    'IRD': 'Inferred from Rapid Divergence',
    # Computational analysis evidence codes
    'ISS': 'Inferred from Sequence or structural Similarity',
    'ISO': 'Inferred from Sequence Orthology',
    'ISA': 'Inferred from Sequence Alignment',
    'ISM': 'Inferred from Sequence Model',
    'IGC': 'Inferred from Genomic Context',
    'RCA': 'Inferred from Reviewed Computational Analysis',
    # Author statement evidence codes
    'TAS': 'Traceable Author Statement',
    'NAS': 'Non-traceable Author Statement',
    # Curator statement evidence codes
    'IC': 'Inferred by Curator (IC)',
    'ND': 'No biological Data available (ND)',
    # Electronic annotation evidence code
    'IEA': 'Inferred from Electronic Annotation'
}

# dictionary label to node dataframe
dict_label_to_node_dataframe = {}

# dictionary label and rela name to dataframe
dict_label_rela_name_to_dataframe = {}

"""
1	DB	required	1	UniProtKB	 node1
2	DB Object ID	required	1	P12345	 node1
3	DB Object Symbol	required	1	PHO3	 node1
4	Qualifier	required	1 or 2	NOT|involved_in	 rela_type
5	GO ID	required	1	GO:0003993	 node2
6	DB:Reference (|DB:Reference)	required	1 or greater	PMID:2676709	  rela
7	Evidence Code	required	1	IMP	 rela
8	With (or) From	optional	0 or greater	GO:0000346	 rela
9	Aspect	required	1	F	 not needed
10	DB Object Name	optional	0 or 1	Toll-like receptor 4	node1
11	DB Object Synonym (|Synonym)	optional	0 or greater	hToll	Tollbooth node1
12	DB Object Type	required	1	protein	 node1 label
13	Taxon(|taxon)	required	1 or 2	taxon:9606	 not needed
14	Date	required	1	20090118	 rela
15	Assigned By	required	1	SGD	 rela
16	Annotation Extension	optional	0 or greater	part_of(CL:0000576)	 rela
17	Gene Product Form ID rela
"""


def prepare_go_annotation_file(go_annotation_file_name):
    """
    firs extract and pars the gzip csv file into a pandas dataframe. Add header. Get the label of the other node. Then
    prepare the node csv by make it identifier unique and write it into  tsv and generate cypher query. The prepare
    different rela type files.
    :param go_annotation_file_name: string
    :return:
    """
    url = 'http://geneontology.org/gene-associations/%s.gaf.gz' % go_annotation_file_name

    request = get(url)
    dataframe_csv = pd.read_csv(BytesIO(request.content), compression='gzip', sep='\t', comment='!',
                                header=None)
    # dataframe_csv = pd.read_csv(go_annotation_file_name + '.gaf.gz', compression='gzip', sep='\t', comment='!',
    #                             header=None)
    # dataframe_csv = pd.read_csv('goa_human.gaf', sep='\t', comment='!', header=None)
    dataframe_csv.columns = ['database_node1', 'identifier_node1', 'symbol_node1', 'qualifier', 'go_id', 'db_reference',
                             'evidence', 'with_from', 'aspect', 'name_1', 'synonyms_1', 'label_1', 'taxon', 'date',
                             'assigned_by',
                             'annotation_extension', 'gene_product_id']
    print(dataframe_csv.head())
    # print(dataframe_csv['annotation_extension'].unique())
    print(dataframe_csv['label_1'].unique())
    labels = dataframe_csv['label_1'].unique()
    if len(labels) > 1:
        print('multiple labels :O')
        node_properties = ['database_node1', 'identifier_node1', 'symbol_node1', 'name_1', 'synonyms_1', 'label_1']
        label = 'rna'
    else:
        node_properties = ['database_node1', 'identifier_node1', 'symbol_node1', 'name_1', 'synonyms_1']
        label = labels[0]

    # prepare node 1 information and tsv file
    node1_frame = dataframe_csv[node_properties].copy()
    node1_frame = node1_frame.drop_duplicates(subset=['identifier_node1'])
    print(node1_frame.head())

    if label not in dict_label_to_node_dataframe:
        dict_label_to_node_dataframe[label] = node1_frame
    else:
        # dict_label_to_node_dataframe[label] = dict_label_to_node_dataframe[label].append(node1_frame).drop_duplicates(
        #     subset=['identifier_node1'])
        dict_label_to_node_dataframe[label] = pd.concat(
            [dict_label_to_node_dataframe[label], node1_frame]).drop_duplicates(
            subset=['identifier_node1'])

    # remove node 1, node 2 (except of identifier) and taxon infos of rela csv
    dataframe_csv = dataframe_csv.drop(
        columns=['database_node1', 'symbol_node1', 'name_1', 'synonyms_1', 'label_1', 'aspect', 'taxon'])
    #
    # print(dataframe_csv['qualifier'].unique())
    # result_dataframe=dataframe_csv[dataframe_csv['identifier_node1']=='Q9BYF1']
    # print('#test blub', labels)
    # print(result_dataframe.head())
    #
    # file_name = 'edge_go_to_' + label  + '.tsv'
    # result_dataframe.to_csv(file_name, sep='\t', index=False)

    # prepare the different
    for rela_type in dataframe_csv['qualifier'].unique():
        part_dataframe = dataframe_csv[dataframe_csv['qualifier'] == rela_type].copy()
        part_dataframe['evidence'] = part_dataframe['evidence'].map(dict_evidence_code_to_evidence)
        # part_dataframe.drop(columns=['qualifier'])
        rela_type = rela_type.replace('|', '_')
        if (label, rela_type) not in dict_label_rela_name_to_dataframe:
            dict_label_rela_name_to_dataframe[(label, rela_type)] = part_dataframe
        else:
            # print('number of row, columns before:',dict_label_rela_name_to_dataframe[(label, rela_type)].shape , rela_type)
            # dict_label_rela_name_to_dataframe[(label, rela_type)] = dict_label_rela_name_to_dataframe[
            #     (label, rela_type)].append(part_dataframe).drop_duplicates()
            dict_label_rela_name_to_dataframe[(label, rela_type)] = pd.concat([dict_label_rela_name_to_dataframe[
                                                                                   (label, rela_type)],
                                                                               part_dataframe]).drop_duplicates()
            # print('number of row, columns after:' , dict_label_rela_name_to_dataframe[(label, rela_type)].shape)


def generate_nodes_files_and_cypher_queries():
    """
    generate the different node files.
    :return:
    """
    for label, dataframe in dict_label_to_node_dataframe.items():
        file_name_node_1 = 'output/' + label + '.tsv'
        dataframe.to_csv(file_name_node_1, sep='\t', index=False)
        generate_csv_file_and_prepare_cypher_queries(dataframe, file_name_node_1, label, 'identifier')


def generate_edges_files_and_cypher_queries():
    """
    generate the different node files.
    :return:
    """
    for (label, rela_type), part_dataframe in dict_label_rela_name_to_dataframe.items():
        file_name = 'output/edges/edge_go_to_' + label + '_' + rela_type + '.tsv'
        part_dataframe.to_csv(file_name, sep='\t', index=False)
        generate_csv_file_and_prepare_cypher_queries_edge(file_name, label, rela_type, list(part_dataframe))


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path go annotation')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load')

    for go_annotation_file_name in ['goa_human', 'goa_human_complex', 'goa_human_isoform', 'goa_human_rna']:
        print(datetime.datetime.now())
        print('load ' + go_annotation_file_name)
        prepare_go_annotation_file(go_annotation_file_name)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate node files and queries')

    generate_nodes_files_and_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate edge files and queries')

    generate_edges_files_and_cypher_queries()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
