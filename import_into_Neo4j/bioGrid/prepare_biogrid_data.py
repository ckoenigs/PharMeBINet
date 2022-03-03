import sys, datetime
import csv, wget
from io import BytesIO
import io
from requests import get
from zipfile import ZipFile

# # dict gene id to infos
dict_gene_infos = {}

# set of chemical ids
set_of_chemical_ids = set()


def check_if_value_exist(line, key):
    """
    replace the - with empty value
    :param line:
    :param key:
    :return:
    """
    value = line[key]
    return value if value != '-' else ''


# cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

# cypher file for edges
cypher_file_edge = open('output/cypher_edges.cypher', 'w', encoding='utf-8')


def generate_tsv_files(keys, file_name):
    """
    generate tsv file with header and file name
    :param keys: string
    :param file_name:  string
    :return: csv writer
    """
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=keys, delimiter='\t')
    csv_writer.writeheader()

    return csv_writer


def generate_tsv_file_and_prepare_cypher_queries(keys, file_name, label, unique_identifier):
    """
    generate node file as csv. Additionaly, generate cpher query to integrate node into neo4j with index.
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    :return: csv writer
    """
    csv_writer = generate_tsv_files(keys, file_name)

    # generate node query and indices
    query = query_start + """ Create (n:%s{ """
    query = query % (path_of_directory, file_name, label)
    for head in keys:
        if head in ['synonyms', 'TREMBL_accessions', 'REFSEQ_accessions', 'swissprot_ids', 'brands', 'atc_codes']:
            query += head + ":split(line." + head + ",'|'), "
        else:
            query += head + ":line." + head + ", "
    query = query[:-2] + "});\n"
    cypher_file.write(query)
    query = 'Create Constraint On (node:%s) Assert node.%s Is Unique;\n'
    query = query % (label, unique_identifier)
    cypher_file.write(query)

    return csv_writer


def generate_tsv_file_and_prepare_cypher_queries_for_edges(keys, file_name, label1, label2, rela_type):
    """
    generate node file as tsv. Additionaly, generate cpher query to integrate node into neo4j with index.
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    :return: csv writer
    """
    csv_writer = generate_tsv_files(keys, file_name)

    # generate node query and indices
    query = query_start + """ Match  (n:%s{ """ + keys[0] + ":line." + keys[
        0] + "}), (b:%s{%s:line.%s}) Create (n)-[:%s{"
    query = query % (path_of_directory, file_name, label1, label2, keys[1], keys[1], rela_type)
    for head in keys[2:]:
        query += head + ':line.' + head + ', '
    query = query[:-2] + '}]->(b);\n'
    cypher_file_edge.write(query)

    return csv_writer


def prepare_gene_info(line, list_of_properties):
    """
    prepare gene dictionary
    :param line: tsv line
    :param list_of_properties: list of string
    :return: dictionary
    """
    properties = ['gene_id', 'gene_id_entrez', 'name', 'gene_symbol', 'synonyms', 'organism_id', 'organism']
    if len(list_of_properties) > len(properties):
        additional_part = ['swissprot_ids', 'TREMBL_accessions', 'REFSEQ_accessions']
        properties.extend(additional_part)
    gene = {}
    i = 0
    while i < len(properties):
        gene[properties[i]] = line[list_of_properties[i]] if line[list_of_properties[i]] != '-' else ''
        i += 1
    return gene


def check_on_gene_id(gene_id, gene):
    if gene_id not in dict_gene_infos:
        dict_gene_infos[gene_id] = gene
    else:
        for key, value in gene.items():
            if key in dict_gene_infos[gene_id] and value != dict_gene_infos[gene_id][key]:
                print(dict_gene_infos[gene_id])
                print(gene)
                print(key)
                sys.exit('ohno gene')
            elif key not in dict_gene_infos[gene_id]:
                dict_gene_infos[gene_id][key] = value


# query start
query_start = """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/import_into_Neo4j/bioGrid/%s" As line FIELDTERMINATOR '\\t'"""


def generate_files_for_gene_chemical_interaction():
    """
    Prepare the tsv files and the queries for integration for chemical-gene interaction
    :return: csv writers
    """
    head_rela_file = ['gene_id', 'chemical_id', 'interaction_type', 'action']
    interaction_properties = ['interaction_id', 'author', 'pubmed_id', 'biogrid_publication_id', 'curated_by', 'method',
                              'method_description', 'notes']
    head_rela_file.extend(interaction_properties)
    file_name = 'output/chemical_gene_interaction.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(head_rela_file)

    query = query_start + ' Match (n1:bioGrid_gene{gene_id:line.gene_id}), (n2:bioGrid_chemical{chemical_id:line.chemical_id})  Create (n1)<-[:interacts{interaction_type:line.interaction_type}]-(m:bioGrid_interaction_with_chemical{'
    query = query % (path_of_directory, file_name)
    for head in interaction_properties:
        if head in ["notes"]:
            query += head + ":split(line.`" + head + "`,'|'), "
        else:
            query += head + ":line.`" + head + "`, "
    query = query[:-2] + "})<-[:interacts{action:line.action}]-(n2);\n"
    cypher_file_edge.write(query)
    query = 'Create Constraint On (node:%s) Assert node.%s Is Unique;\n'
    query = query % ('bioGrid_interaction_with_chemical', 'interaction_id')
    cypher_file_edge.write(query)

    file_name = 'output/interaction_related_gene.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer_interaction_related = csv.writer(file, delimiter='\t')
    csv_writer_interaction_related.writerow(["gene_id", "interaction_id", "interaction_type"])

    query = query_start + ' Match (n1:bioGrid_gene{gene_id:line.gene_id}), (m:bioGrid_interaction_with_chemical{interaction_id:line.interaction_id}) Create (m)-[:related_gene{interaction_type:line.interaction_type}]->(n1) ;\n'
    query = query % (path_of_directory, file_name)
    cypher_file_edge.write(query)

    csv_drug = generate_tsv_file_and_prepare_cypher_queries(
        ['chemical_id', 'name', 'synonyms', 'brands', 'source', 'source_id', 'molecular_formula', 'type', 'atc_codes',
         'cas_nummer', 'inchikey'], 'output/drug.tsv', 'bioGrid_chemical', 'chemical_id')

    return csv_writer, csv_drug, csv_writer_interaction_related


'''
https://wiki.thebiogrid.org/doku.php/biogrid_chemtab
file: BIOGRID-CHEMICALS-4.4.198.chemtab
    #BioGRID Chemical Interaction ID :rela
    BioGRID Gene ID : Gene id
    Entrez Gene ID : Gene id
    Systematic Name : Gene name
    Official Symbol : gene symbol
    Synonyms : gene synonyms
    Organism ID : gene organism id
    Organism : gene organism
    Action : [ Chemical action for this interaction] : rela chemical
    Interaction Type : [Methods such as target, enzyme, carrier, transporter, etc] : rela gene
    Author : rela
    Pubmed ID : rela
    BioGRID Publication ID : rela
    BioGRID Chemical ID : chemical id
    Chemical Name : chemical
    Chemical Synonyms : chemical
    Chemical Brands : chemical
    Chemical Source : chemical
    Chemical Source ID : chemical
    Molecular Formula : chemical
    Chemical Type: chemical
    ATC Codes: chemical
    CAS Number: chemical
    Curated By: rela
    Method : rela
    Method Description: rela
    Related BioGRID Gene ID : gene 2
    Related Entrez Gene ID : gene 2
    Related Systematic Name : gene 2
    Related Official Symbol : gen 2
    Related Synonyms : gene 2
    Related Organism ID : gene 2
    Related Organism : gene 2
    Related Type : rela gene 2
    Notes : rela
    InChIKey : chemical

'''


def load_chemical_interaction_and_seperate_information():
    url_file='https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/BIOGRID-4.4.200/BIOGRID-CHEMICALS-4.4.200.chemtab.zip'


    csv_writer, csv_drug, csv_related_interaction = generate_files_for_gene_chemical_interaction()

    interaction_types = set()
    actions = set()

    request = get(url_file)
    with ZipFile(BytesIO(request.content), 'r') as zipObj:
        f = zipObj.open(zipObj.filelist[0], 'r')
        csv_reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'), delimiter='\t')

        counter = 0
        counter_human=0
        for line in csv_reader:
            counter += 1
            if counter % 5000 == 0:
                print(counter)
            interaction_type = line['Interaction Type']
            action = line['Action']
            interaction_types.add(interaction_type)
            actions.add(action)
            chemical_id = line['BioGRID Chemical ID']
            chemical = {'chemical_id': check_if_value_exist(line, 'BioGRID Chemical ID'),
                        'name': check_if_value_exist(line, 'Chemical Name'),
                        'synonyms': check_if_value_exist(line, 'Chemical Synonyms'),
                        'brands': check_if_value_exist(line, 'Chemical Brands'),
                        'source': check_if_value_exist(line, 'Chemical Source'),
                        'source_id': check_if_value_exist(line, 'Chemical Source ID'),
                        'molecular_formula': check_if_value_exist(line, 'Molecular Formula'),
                        'type': check_if_value_exist(line, 'Chemical Type'),
                        'atc_codes': check_if_value_exist(line, 'ATC Codes'),
                        'cas_nummer': check_if_value_exist(line, 'CAS Number'),
                        'inchikey': check_if_value_exist(line, 'InChIKey'),
                        }
            if chemical_id not in set_of_chemical_ids:
                csv_drug.writerow(chemical)
                set_of_chemical_ids.add(chemical_id)

            gene_id_1 = line['BioGRID Gene ID']
            gene_properties_1 = ['BioGRID Gene ID', 'Entrez Gene ID', 'Systematic Name', 'Official Symbol', 'Synonyms',
                                 'Organism ID', 'Organism']
            gene_1 = prepare_gene_info(line, gene_properties_1)
            if gene_1['organism_id'] != '9606':
                continue
            check_on_gene_id(gene_id_1, gene_1)

            gene_id_2 = line['Related BioGRID Gene ID']
            gene_properties_2 = ['Related BioGRID Gene ID', 'Related Entrez Gene ID', 'Related Systematic Name',
                                 'Related Official Symbol', 'Related Synonyms', 'Related Organism ID', 'Related Organism']
            gene_2 = prepare_gene_info(line, gene_properties_2)
            if gene_2['organism_id'] != '9606' and gene_2['organism_id']!='':
                continue
            check_on_gene_id(gene_id_2, gene_2)

            list_of_rela_gene_chemical = [gene_id_1, chemical_id, interaction_type, action]
            for prop in ["#BioGRID Chemical Interaction ID", "Author", "Pubmed ID", "BioGRID Publication ID", "Curated By",
                         "Method", "Method Description", "Notes"]:
                list_of_rela_gene_chemical.append(check_if_value_exist(line, prop))
            csv_writer.writerow(list_of_rela_gene_chemical)

            if gene_id_2!='-':
                csv_related_interaction.writerow([gene_id_2, line["#BioGRID Chemical Interaction ID"], line['Related Type']])
            counter_human+=1
    print(interaction_types)
    print(actions)
    print('number of interaction:',counter)
    print('counter interaction all human:',counter_human)


def prepare_split_line_dictionary(line, header):
    """
    Prepare ontology information of line into a dictionary
    :param line: tsv line
    :param header: list of strings
    :return: dictionary
    """
    dict_line_splitted = {}
    for head in header:
        string_ontology = line[head]
        if string_ontology != '-':
            dict_line_splitted[head] = ['' if x == '-' else x.split('^') for x in string_ontology.split('|')]
        else:
            dict_line_splitted[head] = None
    return dict_line_splitted


# dictionary ontology name to node names
dict_ontology_name_to_node_name = {
    'Ontology Term Names': 'name',
    'Ontology Term Categories': 'category',
    'Ontology Term Qualifier IDs': 'qualifier_ids',
    'Ontology Term Qualifier Names': 'qualifier_names',
    'Ontology Term Types': 'type'
}
# set of distinct ontologies categories
set_ontologies_categories = set()

# set of all properties of ontology nodes
set_of_ontology_nodes = set([])

# dictionary category to csv-writer
dict_category_to_csv_writer = {}

# dictionary category edges to tsv file
dict_category_to_edge_tsv_file = {}

# dictionary category to dictionary node id to node information
dict_category_to_dict_node_id_to_properties = {}


def prepare_ontology_infos(line, interaction_id):
    global set_of_ontology_nodes
    ontology_infs_properties = ['Ontology Term Names', 'Ontology Term Categories', 'Ontology Term Qualifier IDs',
                                'Ontology Term Qualifier Names', 'Ontology Term Types']
    ontology_term_ids = line['Ontology Term IDs']
    if ontology_term_ids != '-':
        list_nodes = []
        dict_line = prepare_split_line_dictionary(line, ontology_infs_properties)
        splitted_ontology_terms_ids = ontology_term_ids.split("|")
        for i in range(len(splitted_ontology_terms_ids)):
            node_id = splitted_ontology_terms_ids[i]
            dict_node = {}
            dict_node['id'] = node_id
            for head in ontology_infs_properties:
                if dict_line[head]:
                    dict_node[dict_ontology_name_to_node_name[head]] = '|'.join(dict_line[head][i])
            category = dict_node['category']
            if category not in set_ontologies_categories:
                header_ontology = ['id', 'category', 'name']
                category_replace = category.replace(' ', '_')
                csv_node = generate_tsv_file_and_prepare_cypher_queries(header_ontology,
                                                                        'output/' + category_replace + '.tsv',
                                                                        'bioGrid_' + category_replace, 'id')
                dict_category_to_csv_writer[category] = csv_node
                set_ontologies_categories.add(category)
                dict_category_to_dict_node_id_to_properties[category] = {}

                edge_keys = ['interaction_id', 'id', 'type', 'qualifier_names', 'qualifier_ids']
                csv_edge = generate_tsv_file_and_prepare_cypher_queries_for_edges(edge_keys,
                                                                                  'output/interaction_' + category_replace + '.tsv',
                                                                                  'bioGrid_interaction',
                                                                                  'bioGrid_' + category_replace,
                                                                                  'associates')
                dict_category_to_edge_tsv_file[category] = csv_edge
            dict_edge = {
                'interaction_id': interaction_id,
                'id': node_id
            }
            for prop in ['type', 'qualifier_names', 'qualifier_ids']:
                if prop in dict_node:
                    dict_edge[prop] = dict_node[prop]
                    del dict_node[prop]
            dict_category_to_edge_tsv_file[category].writerow(dict_edge)

            set_of_ontology_nodes = set_of_ontology_nodes.union(dict_node.keys())
            if node_id not in dict_category_to_dict_node_id_to_properties[category]:
                dict_category_to_dict_node_id_to_properties[category][node_id] = dict_node
                dict_category_to_csv_writer[category].writerow(dict_node)
            else:
                for key, value in dict_category_to_dict_node_id_to_properties[category][node_id].items():
                    if key in dict_node and dict_node[key] != value:
                        print(dict_node)
                        print(dict_category_to_dict_node_id_to_properties[category][node_id])
                        print(key)
                        print('ohno')


# dictionary gene_gene_interaction file name to neo4j property
dict_gene_gene_interaction_file_name_to_neo4j_property = {
    "#BioGRID Interaction ID": "interaction_id",
    "Experimental System": "experimental_system",
    "Experimental System Type": "experimental_system_type",
    "Author": "author",
    "Publication Source": "publication_source",
    "Throughput": "throughput",
    "Score": "score",
    "Modification": "modification",
    "Qualifications": "qualifications",
    "Tags": "tags",
    "Source Database": "source_database"
}


def prepare_file_and_query_for_gene_gene_interaction():
    """
    Prepare gene-gene interaction file and the cypher query
    :return: csv writer
    """
    head_rela_file = ['gene_id1', 'gene_id2']
    head_rela_file.extend(dict_gene_gene_interaction_file_name_to_neo4j_property.values())
    file_name = 'output/gene_gene_interaction.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(head_rela_file)

    query = query_start + ' Match (n1:bioGrid_gene{gene_id:line.gene_id1}), (n2:bioGrid_gene{gene_id:line.gene_id2})   Create (n1)-[:interacts]->(m:bioGrid_interaction{'
    query = query % (path_of_directory, file_name)
    for head in dict_gene_gene_interaction_file_name_to_neo4j_property.values():
        if head in ["throughput", "qualifications", "tags"]:
            query += head + ":split(line." + head + ",'|'), "
        else:
            query += head + ":line." + head + ", "
    query = query[:-2] + "})-[:interacts]->(n2);\n"
    cypher_file_edge.write(query)
    query = 'Create Constraint On (node:%s) Assert node.%s Is Unique;\n'
    query = query % ('bioGrid_interaction', 'interaction_id')
    cypher_file_edge.write(query)

    return csv_writer


'''
https://wiki.thebiogrid.org/doku.php/biogrid_tab_version_3.0
file: BIOGRID-ORGANISM-Homo_sapiens 
    #BioGRID Interaction ID : rela
    Entrez Gene Interactor A :gene 1
    Entrez Gene Interactor B : gene 2
    BioGRID ID Interactor A: gene 1
    BioGRID ID Interactor B: gene 2
    Systematic Name Interactor A : gene 1
    Systematic Name Interactor B : gene 2
    Official Symbol Interactor A : gene 1
    Official Symbol Interactor B : gene 2
    Synonyms Interactor A : gene 1
    Synonyms Interactor B : gene 2
    Experimental System : rela
    Experimental System Type : rela
    Author : rela
    Publication Source : rela
    Organism ID Interactor A : gene 1
    Organism ID Interactor B : gene 2
    Throughput : rela
    Score : rela 
    Modification : rela
    Qualifications : rela
    Tags : rela (only -)
    Source Database  : rela
    SWISS-PROT Accessions Interactor A  : gene 1
    TREMBL Accessions Interactor A  : gene 1
    REFSEQ Accessions Interactor A  : gene 1
    SWISS-PROT Accessions Interactor B  : gene 2
    TREMBL Accessions Interactor B : gene 2
    REFSEQ Accessions Interactor B : gene 2
    Ontology Term IDs : nodes
    Ontology Term Names :nodes
    Ontology Term Categories :nodes
    Ontology Term Qualifier IDs: nodes
    Ontology Term Qualifier Names : nodes
    Ontology Term Types :nodes
    Organism Name Interactor A
    Organism Name Interactor B

'''


def load_protein_interaction_and_seperate_information():
    """
    Parse the Biogrid-organism-homo sapiens
    :return:
    """
    url_file='https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/BIOGRID-4.4.200/BIOGRID-ORGANISM-4.4.200.tab3.zip'

    csv_writer_interaction = prepare_file_and_query_for_gene_gene_interaction()

    counter = 0
    counter_human=0
    request = get(url_file)
    with ZipFile(BytesIO(request.content), 'r') as zipObj:
        file_name='BIOGRID-ORGANISM-Homo_sapiens-4.4.200.tab3.txt'
        # for zip_info in zipObj.filelist:
        #     if zip_info.filename!=file_name:
        #         continue
        f = zipObj.open(file_name, 'r')
        csv_reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'), delimiter='\t')
        for line in csv_reader:
            counter += 1

            gene_id_1 = line['BioGRID ID Interactor A']
            gene_properties_1 = ['BioGRID ID Interactor A', 'Entrez Gene Interactor A', 'Systematic Name Interactor A',
                                 'Official Symbol Interactor A', 'Synonyms Interactor A', 'Organism ID Interactor A',
                                 'Organism Name Interactor A', 'SWISS-PROT Accessions Interactor A',
                                 'TREMBL Accessions Interactor A', 'REFSEQ Accessions Interactor A']
            gene_1 = prepare_gene_info(line, gene_properties_1)
            if gene_1['organism_id'] != '9606':
                continue
            check_on_gene_id(gene_id_1, gene_1)

            gene_id_2 = line['BioGRID ID Interactor B']
            gene_properties_2 = ['BioGRID ID Interactor B', 'Entrez Gene Interactor B', 'Systematic Name Interactor B',
                                 'Official Symbol Interactor B', 'Synonyms Interactor B', 'Organism ID Interactor B',
                                 'Organism Name Interactor B', 'SWISS-PROT Accessions Interactor B',
                                 'TREMBL Accessions Interactor B', 'REFSEQ Accessions Interactor B']
            gene_2 = prepare_gene_info(line, gene_properties_2)
            if gene_2['organism_id'] != '9606':
                continue
            check_on_gene_id(gene_id_2, gene_2)

            counter_human+=1

            list_interaction_info = [gene_id_1, gene_id_2]
            for key in dict_gene_gene_interaction_file_name_to_neo4j_property.keys():
                list_interaction_info.append(check_if_value_exist(line,key))
            csv_writer_interaction.writerow(list_interaction_info)

            edge_id = line['#BioGRID Interaction ID']

            prepare_ontology_infos(line, edge_id)
            if counter % 100000 == 0:
                print(counter)
    print(set_ontologies_categories)
    print(set_of_ontology_nodes)

    print('number of interaction:',counter)
    print('counter interaction all human:',counter_human)


def prepare_gene_file():
    """
    generate tsv file for gene
    :return:
    """
    header = ['gene_id', 'gene_id_entrez', 'name', 'gene_symbol', 'synonyms', 'organism_id', 'organism',
              'swissprot_ids',
              'TREMBL_accessions', 'REFSEQ_accessions']
    csv_gene = generate_tsv_file_and_prepare_cypher_queries(header, 'output/gene.tsv', 'bioGrid_gene', 'gene_id')
    for gene_id, dict_gene in dict_gene_infos.items():
        csv_gene.writerow(dict_gene)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path BioGRID')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load chemical-gene interaction')

    load_chemical_interaction_and_seperate_information()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load gene-gene interaction')

    load_protein_interaction_and_seperate_information()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate gene file')

    prepare_gene_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
