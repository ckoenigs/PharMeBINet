import sys, datetime
from requests import get
import csv, gzip, os

sys.path.append("../..")
import pharmebinetutils

# cypher file
cypher_file = open('cypher.cypher', 'a', encoding='utf-8')
cypher_file_edge = open('cypher_edge.cypher', 'a', encoding='utf-8')


def generate_nodes_files_and_cypher_queries(label, header):
    """
    generate the different node files and queries
    :return:
    """
    file_name_node_1 = 'output/' + label + '.tsv'
    file = open(file_name_node_1, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(header)
    generate_csv_file_and_prepare_cypher_queries(header, file_name_node_1, label, 'identifier')
    return csv_writer


def generate_edges_files_and_cypher_queries(label, rela_type, header):
    """
    generate the different edge files and queries
    :return:
    """
    file_name = 'output/edges/edge_go_to_' + label + '_' + rela_type + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(header)

    generate_csv_file_and_prepare_cypher_queries_edge(file_name, label, rela_type, header)
    return csv_writer


def generate_csv_file_and_prepare_cypher_queries(header, file_name, label, unique_identifier):
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
    for head in header:
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
    Gnerate cypher query to integrate the edge into neo4j.
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

# dictionary label to set of node ids
dict_label_to_set_of_ids = {}

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
    first extract and parse the gzip csv file into node csv and edge csv files.
    :param go_annotation_file_name: string
    :return:
    """

    filename = f'data/{go_annotation_file_name}.gaf.gz'
    if not os.path.exists(filename):
        url = f'http://geneontology.org/gene-associations/{go_annotation_file_name}.gaf.gz'
        filename = pharmebinetutils.download_file(url, out='data')
    file = gzip.open(filename, 'rt')

    header = ['database_node1', 'identifier_node1', 'symbol_node1', 'qualifier', 'go_id', 'db_reference',
              'evidence', 'with_from', 'aspect', 'name_1', 'synonyms_1', 'label_1', 'taxon', 'date',
              'assigned_by',
              'annotation_extension', 'gene_product_id']

    csv_reader = csv.reader(file, delimiter='\t')

    dict_label_to_tsv_writer = {}
    # dictionary form label to edge type to csv
    dict_label_to_edge_type_to_csv_file = {}
    # header edge
    header_edge = ['identifier_node1', 'qualifier', 'go_id', 'db_reference',
                   'evidence', 'with_from', 'aspect', 'date',
                   'assigned_by',
                   'annotation_extension', 'gene_product_id']
    #
    for row in csv_reader:
        # the row with one entry are only comments
        if len(row) > 1:
            label = row[11]
            if 'rna' in label.lower():
                node_properties = ['database_node1', 'identifier_node1', 'symbol_node1', 'name_1', 'synonyms_1', 'label_1']
                label = 'rna'
            else:
                node_properties = ['database_node1', 'identifier_node1', 'symbol_node1', 'name_1', 'synonyms_1']
            if not label in dict_label_to_tsv_writer:
                dict_label_to_set_of_ids[label] = set()
                dict_label_to_tsv_writer[label] = generate_nodes_files_and_cypher_queries(label, node_properties)
            row_node = []
            identifier= row[1]
            if not identifier in dict_label_to_set_of_ids[label]:
                counter=0
                dict_label_to_set_of_ids[label].add(identifier)
                for head in header:
                    if head in node_properties:
                        row_node.append(row[counter])
                    counter+=1
                dict_label_to_tsv_writer[label].writerow(row_node)

            # qualifier
            rela_type = row[3]
            rela_type = rela_type.replace('|', '_')
            if label not in dict_label_to_edge_type_to_csv_file:
                dict_label_to_edge_type_to_csv_file[label] = {}
            if rela_type not in dict_label_to_edge_type_to_csv_file[label]:
                dict_label_to_edge_type_to_csv_file[label][rela_type] = generate_edges_files_and_cypher_queries(label,
                                                                                                                rela_type,
                                                                                                                header_edge)
            row_edge = []
            counter = 0
            for head in header:
                if head in header_edge and head != 'evidence':
                    row_edge.append(row[counter])
                elif head == 'evidence':
                    row_edge.append(dict_evidence_code_to_evidence[row[counter]])
                counter += 1
            dict_label_to_edge_type_to_csv_file[label][rela_type].writerow(row_edge)


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

    for go_annotation_file_name in ['goa_human']:
        print(datetime.datetime.now())
        print('load ' + go_annotation_file_name)
        prepare_go_annotation_file(go_annotation_file_name)

    cypher_file.close()
    cypher_file_edge.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
