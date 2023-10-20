import sys
import datetime, re
import csv, json, math
import re

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


# connect with the neo4j database AND MYSQL
def database_connection():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary gene id to gene node
dict_gene_id_to_gene_node = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_genes_from_database_and_add_to_dict():
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)
    for record in results:
        gene = record.data()['n']
        identifier = gene['identifier']
        dict_gene_id_to_gene_node[identifier] = dict(gene)


cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
cypher_file_edge = open('output/cypher_edge.cypher', 'w', encoding='utf-8')

'''
Get all properties of variation and prepare properties and end of 
'''


def get_all_variation_properties():
    global query_middle
    query_middle = "{"
    query = '''MATCH (p:Variant_ClinVar) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''
    results = g.run(query)
    for record in results:
        property = record.data()['allfields']
        if property not in ['rela', 'xrefs', 'genes']:
            query_middle += property + ':n.' + property + ', '
        elif property == 'xrefs':
            query_middle += property + ':split(line.' + property + ',"|"), '
    query_middle = query_middle + ' license:"https://www.ncbi.nlm.nih.gov/home/about/policies/", source:"ClinVar", clinvar:"yes",  resource:["ClinVar"], url:"https://www.ncbi.nlm.nih.gov/clinvar/variation/"+line.identifier}) Create (m)-[:equal_to_clinvar_variant]->(n)'


'''
add query for a specific tsv to cypher file
'''


def add_query_to_cypher_file(tuples, file_name):
    this_start_query = "Match (n:Variant_ClinVar {identifier:line.identifier}) Create (m"
    for label in list(tuples):
        if '_' in label:
            label = re.sub("\_[a-z]", lambda m: m.group(0)[1].upper(), label)
        this_start_query += ':' + label + ' '
    if not 'Genotype' in tuples and not 'Haplotype' in tuples:
        this_start_query += ':GeneVariant '
    query = this_start_query + query_middle
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/clinvar/output/{file_name}.tsv',
                                              query)
    cypher_file.write(query)


'''
prepare the label remove _ and change instead letter to upper letter
'''


def prepare_label(label):
    label = label.rsplit('_', 1)[0]
    label = label[0].upper() + label[1:]

    def remove_and_made_upper_letter(match):
        '''
        "Return the match with the removed letter and upper letter"
        '''
        letter = match.group()
        if len(letter) > 1:
            letter = letter[1]
        return letter.upper()

    p = re.compile(r'{\'|\s\'|\',|\']')
    return p.sub(remove_and_made_upper_letter, label)


'''
prepare rela
'''


def prepare_rela(rela):
    p = re.compile('{[a-zA-Z]')


# dictionary tuple of labels to tsv file
dict_tuple_of_labels_to_tsv_files = {}

# file from relationship between gene and variant
file_rela = open('output/gene_variant.tsv', 'w', encoding='utf-8')
csv_rela = csv.writer(file_rela, delimiter='\t')
header_rela = ['gene_id', 'variant_id', 'resource']
csv_rela.writerow(header_rela)

divider_of_variant = 5000

'''
Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
'''


def load_all_variants_and_finish_the_files():
    query = "Match (n:Variant_ClinVar) Return count(n) as v"
    result = g.run(query)
    number_of_variant = result.single()['v']

    number_of_rounds = math.ceil(number_of_variant / divider_of_variant)
    for round_index in range(number_of_rounds):

        query = "MATCH (n:Variant_ClinVar) RETURN n, labels(n) Skip %s Limit %s"
        query = query % (round_index * divider_of_variant, divider_of_variant)

        results = g.run(query)
        for record in results:
            [node, labels] = record.values()
            node = dict(node)
            new_labels = set()
            for label in labels:
                new_label = prepare_label(label)
                new_labels.add(new_label)
            new_labels = tuple(sorted(new_labels))

            identifier = node['identifier']

            # add tuple to dict with tsv and gerenarte and add query
            if not new_labels in dict_tuple_of_labels_to_tsv_files:
                file_name = '_'.join(list(new_labels))
                file = open('output/' + file_name + '.tsv', 'w', encoding='utf-8')
                csv_writer = csv.writer(file, delimiter='\t')
                csv_writer.writerow(['identifier', 'xrefs'])

                dict_tuple_of_labels_to_tsv_files[new_labels] = csv_writer

                add_query_to_cypher_file(new_labels, file_name)
            xrefs = node['xrefs'] if 'xrefs' in node else []
            new_xrefs = []
            for xref in xrefs:
                if xref.startswith('dbSNP:'):
                    xref = xref.split(':')
                    xref = xref[0] + ':rs' + xref[1]
                new_xrefs.append(xref)

            dict_tuple_of_labels_to_tsv_files[new_labels].writerow(
                [identifier, '|'.join(go_through_xrefs_and_change_if_needed_source_name(new_xrefs, 'Variant'))])

            if 'genes' in node:
                possible_genes_rela = node["genes"].replace('\\"', '"')
                genes_infos = json.loads(possible_genes_rela)
                for gene_infos in genes_infos:
                    gene_id = gene_infos['gene_id']
                    if gene_id in dict_gene_id_to_gene_node:
                        resource = set(dict_gene_id_to_gene_node[gene_id]['resource'])
                        resource.add('ClinVar')
                        csv_rela.writerow([gene_id, identifier, '|'.join(resource)])


'''
prepare the last queries, where the variant nodes get an index and the query for the relationship between gene and variants
'''


def perpare_queries_index_and_relationships():
    cypher_file.write(pharmebinetutils.prepare_index_query('Variant', 'identifier'))

    # relationship
    query = "Match (g:Gene{identifier:line.%s}), (v:Variant{identifier:line.%s}) Set g.resource=split(line.resource,'|'), g.clinvar='yes' Create  (g)-[:HAS_GhGV{source:'ClinVar', url:'https://www.ncbi.nlm.nih.gov/clinvar/variation/'+line.%s, resource:['ClinVar'], clinvar:'yes', license:'https://www.ncbi.nlm.nih.gov/home/about/policies/'}]->(v)"
    query = query % (header_rela[0], header_rela[1], header_rela[1])
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/clinvar/output/gene_variant.tsv',
                                              query)
    cypher_file_edge.write(query)


# dictionary first label letter to rela letter
dict_first_letter_to_rela_letter = {
    'G': 'GT',
    'H': 'H',
    'V': 'GV'
}


def query_for_rela(file_name, label1, label2):
    """
    generate query for internal relationship
    :param file_name: string
    :param label1: string
    :param label2: string
    :return:
    """
    query = '''Match (g:%s{identifier:line.identifier_1}), (c:%s{identifier:line.identifier_2}) Create (g)-[:HAS_%sh%s {source:'ClinVar', resource:['ClinVar'], license:"https://www.ncbi.nlm.nih.gov/home/about/policies/", url:'https://www.ncbi.nlm.nih.gov/clinvar/variation/'+line.identifier_1, clinvar:'yes'}]->(c)'''
    query = query % (label1, label2, dict_first_letter_to_rela_letter[label1[0]],
                     dict_first_letter_to_rela_letter[label2[0]])
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/clinvar/output/{file_name}.tsv',
                                              query)
    cypher_file_edge.write(query)


def create_file(label1, label2):
    """
    generate a rela file for two labels and generate query
    :param label1: string
    :param label2: string
    :return: csv writer
    """
    file_name = label1 + '_' + label2 + '_has'
    query_for_rela(file_name, label1, label2)
    file = open('output/' + file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier_1', 'identifier_2'])
    return csv_writer


def get_variant_rela_intern(label, list_to_labels):
    """
    create and fill tsv files
    :param label: string
    :param list_to_labels: list of strings
    :return:
    """
    set_of_pairs = set()
    for other_label in list_to_labels:
        short_label1 = label.split('_')[0]
        short_label2 = other_label.split('_')[0]
        csv_writer = create_file(short_label1, short_label2)

        query = "Match (c:%s)-[:has]->(d:%s) Return c.identifier, d.identifier"
        query = query % (label, other_label)
        results = g.run(query)
        for record in results:
            [id1, id2] = record.values()
            if (id1, id2) in set_of_pairs:
                continue
            csv_writer.writerow([id1, id2])
            set_of_pairs.add((id1, id2))


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ClinVar')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all genes from database')

    load_genes_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all kind of properties of the variants')

    get_all_variation_properties()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all variation from database')

    load_all_variants_and_finish_the_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Add constraint and relationships to gene')

    perpare_queries_index_and_relationships()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Add relationships from Haplotype')

    get_variant_rela_intern('Haplotype_ClinVar', ['Variant_ClinVar'])

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Add relationships from Genotype')

    get_variant_rela_intern('Genotype_ClinVar', ['Haplotype_ClinVar', 'Variant_ClinVar'])

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
