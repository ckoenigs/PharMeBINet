import sys, datetime
import csv
from io import BytesIO
import io
from requests import get
from zipfile import ZipFile

# # dict gene id to infos
from _socket import herror

dict_gene_infos = {}

# set of chemical ids
set_of_chemical_ids = set()

# cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

cypher_file_edge = open('output/cypher_edge.cypher', 'w', encoding='utf-8')


def generate_csv_files(keys, file_name):
    """
    generate csv file with header and file name
    :param keys: string
    :param file_name:  string
    :return: csv writer
    """
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=keys, delimiter='\t')
    csv_writer.writeheader()

    return csv_writer


def generate_csv_file_and_prepare_cypher_queries(keys, file_name, label, unique_identifier):
    """
    generate node file as csv. Additionaly, generate cpher query to integrate node into neo4j with index.
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    :return: csv writer
    """
    csv_writer = generate_csv_files(keys, file_name)

    # generate node query and indices
    query = query_start + """ Create (n:%s_smpdb{  """
    query = query % (path_of_directory, file_name, label)
    for head in keys:
        if head in []:
            query += head + ":split(line." + head + ",'|'), "
        else:
            query += head + ":line." + head + ", "
    query = query[:-2] + "});\n"
    cypher_file.write(query)
    query = 'Create Constraint On (node:%s_smpdb) Assert node.%s Is Unique;\n'
    query = query % (label, unique_identifier)
    cypher_file.write(query)

    return csv_writer


def generate_csv_file_and_prepare_cypher_queries_edge(file_name, label, unique_identifier):
    """
    generate edge file as csv. Additionaly, generate cpher query to integrate the edge into neo4j.
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    :return: csv writer
    """
    csv_writer = generate_csv_files(['pathway_id', 'other_id'], file_name)

    # generate node query and indices
    query = query_start + """ Match (n:pathway_smpdb{ smpdb_id:line.pathway_id}), (m:%s_smpdb {%s:line.other_id}) Create (n)-[:associates]->(m);\n """
    query = query % (path_of_directory, file_name, label, unique_identifier)
    cypher_file_edge.write(query)

    return csv_writer


# query start
query_start = """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/import_into_Neo4j/smpdb/%s" As line FIELDTERMINATOR '\\t'"""

# dictionary old property name to new
dict_old_porperty_to_new = {
    'SMPDB ID': 'smpdb_id',
    'PW ID': 'pw_id',
    'Name': 'name',
    'Subject': 'category',
    'Description': 'description'
}

# set smpdb id
set_smpdb_id = set()

# set_pw_id
set_pw_id = set()

"""
smpdb_pathways.csv
SMPDB ID,
PW ID,
Name,
Subject,
Description

"""


def load_pathway_information():
    """
    load smpdb_pathways.csv and generate a new csv into output.
    :return:
    """
    url_file = 'https://smpdb.ca/downloads/smpdb_pathways.csv.zip'

    csv_writer = generate_csv_file_and_prepare_cypher_queries(dict_old_porperty_to_new.values(), 'output/pathway.tsv',
                                                              'pathway', 'smpdb_id')

    request = get(url_file)
    with ZipFile(BytesIO(request.content), 'r') as zipObj:
        f = zipObj.open(zipObj.filelist[0], 'r')
        csv_reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'))
    # file = open('smpdb_pathways.csv', 'r', encoding='utf-8')
    # csv_reader = csv.DictReader(file)
        for line in csv_reader:
            smpdb_id = line['SMPDB ID']
            if smpdb_id in set_smpdb_id:
                print('double smpdb id')
            set_smpdb_id.add(smpdb_id)
            pw_id = line['PW ID']
            if pw_id in set_pw_id:
                print('double smpdb id')
            set_pw_id.add(pw_id)

            dict_line = {}
            for key, value in dict_old_porperty_to_new.items():
                dict_line[value] = line[key]
            csv_writer.writerow(dict_line)


# dictionary old property name to new
dict_old_porperty_to_new_protein = {
    'Uniprot ID': 'uniprot_id',
    'Protein Name': 'name',
    'HMDBP ID': 'hmdbp_id',
    'DrugBank ID': 'drugbank_id',
    'GenBank ID': 'genbank_id',
    'Gene Name': 'gene_name',
    'Locus': 'locus',
}


def combine_other_node_information(dict_node, identifier, dict_nodes):
    """
    Add node information into a dictionary. If it already exists then compare information.
    :param dict_node: dictionary
    :param identifier: string
    :param dict_nodes:dictionary
    :return:
    """
    if identifier in dict_nodes:
        dict_exist_node = dict_nodes[identifier]
        for key, value in dict_node.items():
            if key in dict_exist_node and value != dict_exist_node[key] and value != '' and dict_exist_node[key] != '':
                print(key)
                print(dict_exist_node[key])
                print(value)
                print(identifier)
                print('same node but different information')
                # sys.exit('same node but different information')
            elif key in dict_exist_node and value != dict_exist_node[key] and value != '':
                dict_exist_node[key] = value
    else:
        dict_nodes[identifier] = dict_node


def extract_info_rela_and_other_node(csv_edge, csv_writer, url_file, identifier_name, dict_old_porperty_to_new_node,
                                     dict_node_id_to_node_info, set_pathway_node_pair):
    request = get(url_file)
    with ZipFile(BytesIO(request.content), 'r') as zipObj:
    # with ZipFile(zip_name, 'r') as zipObj:
        for zip_info in zipObj.filelist:
            f = zipObj.open(zip_info, 'r')
            csv_reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'))
            for line in csv_reader:
                # print(line)
                # get an identifier for node (in protein at least some have only dugbank id
                identifier = line[identifier_name[0]] if line[identifier_name[0]] != '' else line[identifier_name[1]]
                if identifier == '':
                    # identifier=line['DrugBank ID']
                    print(line)

                # prepare node information into a dictionary and combine existing information
                dict_node = {'identifier': identifier}
                for key, value in dict_old_porperty_to_new_node.items():
                    dict_node[value] = line[key]
                combine_other_node_information(dict_node, identifier, dict_node_id_to_node_info)

                pathway_id = line['SMPDB ID']
                # check if it has not a athway id which did not exists in the pathway file
                if pathway_id not in set_smpdb_id:
                    print('ohje, a pathway which is not in pathways :(')

                # do not write duplicate edges in csv
                if (pathway_id, identifier) in set_pathway_node_pair:
                    # print('double pair pathway_protein')
                    # print(pathway_id, identifier)
                    continue

                # prepare edge information and write into csv
                set_pathway_node_pair.add((pathway_id, identifier))
                edge = {'pathway_id': pathway_id, 'other_id': identifier}
                csv_edge.writerow(edge)

    # write node information into csv file
    for dict_node in dict_node_id_to_node_info.values():
        csv_writer.writerow(dict_node)


# set of protein ids to protein infos
dict_protein_id_to_info = {}

# set pathway-protein-pair
set_pathway_protein_pair = set()

"""
Protein -  Pathway csv
SMPDB ID : pathway,
Pathway Name: pathway,
Pathway Subject: Pathway,
Uniprot ID: protein,
Protein Name: protein,
HMDBP ID: protein,
DrugBank ID: protein,
GenBank ID: protein,
Gene Name: protein,
Locus:protein
"""


def prepare_pathway_protein_csv():
    """
    Generate csv file for Protein with additional cypher query. Then prepare csv file and query for pathway-protein.
    Next, extract informationform zip and add to node and edge.
    :return:
    """
    url_file = 'https://smpdb.ca/downloads/smpdb_proteins.csv.zip'

    header_node = list(dict_old_porperty_to_new_protein.values())
    header_node.append('identifier')
    csv_writer = generate_csv_file_and_prepare_cypher_queries(header_node, 'output/protein.tsv',
                                                              'protein', 'identifier')
    csv_edge = generate_csv_file_and_prepare_cypher_queries_edge('output/pathway_protein.tsv', 'protein', 'identifier')

    # 'smpdb_proteins.csv.zip'
    extract_info_rela_and_other_node(csv_edge, csv_writer, url_file, ['Uniprot ID', 'DrugBank ID'],
                                     dict_old_porperty_to_new_protein, dict_protein_id_to_info,
                                     set_pathway_protein_pair)


# dictionary property from csv to property in new csv file
dict_old_porperty_to_new_metabolite = {
    'Metabolite ID': 'metabolite_id',
    'Metabolite Name': 'name',
    'HMDB ID': 'hmdb_id',
    'KEGG ID': 'kegg_id',
    'ChEBI ID': 'chebi_id',
    'DrugBank ID': 'drugbank_id',
    'CAS': 'cas',
    'Formula': 'formula',
    'IUPAC': 'iupac',
    'SMILES': 'smiles',
    'InChI': 'inchi',
    'InChI Key': 'inchi_key'
}


# set of metabolite ids to metabolite infos
dict_metabolite_id_to_info = {}

# set pathway-metabolite-pair
set_pathway_metabolite_pair = set()

"""
smpdb_metabolites.csv.zip
SMPDB ID : pathway
Pathway Name :pathway
Pathway Subject	: pathway
Metabolite ID: metabolite
Metabolite Name: metabolite	
HMDB ID: metabolite	
KEGG ID	: metabolite
ChEBI ID: metabolite	
DrugBank ID: metabolite	
CAS	: metabolite
Formula	: metabolite
IUPAC	: metabolite
SMILES	: metabolite
InChI	: metabolite
InChI Key: metabolite

"""


def prepare_pathway_metabolite_csv():
    """
    Generate csv file for Protein with additional cypher query. Then prepare csv file and query for pathway-protein.
    Next, extract informationform zip and add to node and edge.
    :return:
    """
    url_file = 'https://smpdb.ca/downloads/smpdb_metabolites.csv.zip'

    header_node = list(dict_old_porperty_to_new_metabolite.values())
    header_node.append('identifier')
    csv_writer = generate_csv_file_and_prepare_cypher_queries(header_node, 'output/metabolite.tsv',
                                                              'metabolite', 'identifier')
    csv_edge = generate_csv_file_and_prepare_cypher_queries_edge('output/pathway_metabolite.tsv', 'metabolite', 'identifier')

    # 'smpdb_metabolites.csv.zip'
    extract_info_rela_and_other_node(csv_edge, csv_writer, url_file, ['Metabolite ID', ''],
                                     dict_old_porperty_to_new_metabolite, dict_metabolite_id_to_info,
                                     set_pathway_metabolite_pair) # DrugBank ID


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path SMPDB')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load pathway information')

    load_pathway_information()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load pathway-protein interaction')

    prepare_pathway_protein_csv()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load pathway-metabolite interaction')

    prepare_pathway_metabolite_csv()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
