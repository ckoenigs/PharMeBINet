from py2neo import Graph
import sys
import datetime, re
import csv, json


# connect with the neo4j database AND MYSQL
def database_connection():
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# dictionary gene id to gene node
dict_gene_id_to_gene_node = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_genes_from_database_and_add_to_dict():
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)
    for gene, in results:
        identifier = gene['identifier']
        dict_gene_id_to_gene_node[identifier] = dict(gene)


cypher_file = open('output/cypher_variants.cypher', 'w', encoding='utf-8')

query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/clinvar/output/%s.tsv" As line FIELDTERMINATOR '\\t' 
    Match '''

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
    for property, in results:
        if property not in ['rela']:
            query_middle += property + ':n.' + property + ', '
    query_middle = query_middle + ' license:"CC0 1.0", source:"ClinVar", clinvar:"yes",  resource:["ClinVar"], url:"https://www.ncbi.nlm.nih.gov/clinvar/variation/"+line.identifier}) Create (m)-[:equal_to_clinvar_variant]->(n);\n'


'''
add query for a specific csv to cypher file
'''


def add_query_to_cypher_file(tuples, file_name):
    this_start_query = query_start + "(n:Variant_ClinVar {identifier:line.identifier}) Create (m"
    this_start_query = this_start_query % (path_of_directory, file_name)
    for label in list(tuples):
        this_start_query += ':' + label + ' '
    query = this_start_query + query_middle
    cypher_file.write(query)


'''
prepare the label remove _ and change instead letter to upper letter
'''


def prepare_label(label):
    label = label.rsplit('_', 1)[0].capitalize()

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


# dictionary tuple of lables to csv file
dict_tuple_of_labels_to_csv_files = {}

# file from relationship between gene and variant
file_rela = open('output/gene_variant.tsv', 'w', encoding='utf-8')
csv_rela = csv.writer(file_rela, delimiter='\t')
header_rela = ['gene_id', 'variant_id']
csv_rela.writerow(header_rela)

'''
Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
'''


def load_all_variants_and_finish_the_files():
    query = "MATCH (n:Variant_ClinVar) RETURN n, labels(n)"
    results = g.run(query)
    for node, lables, in results:
        new_labels = set()
        for label in lables:
            new_label = prepare_label(label)
            new_labels.add(new_label)
        new_labels = tuple(sorted(new_labels))

        identifier = node['identifier']

        # add tuple to dict with csv and gerenarte and add query
        if not new_labels in dict_tuple_of_labels_to_csv_files:
            file_name = '_'.join(list(new_labels))
            file = open('output/' + file_name + '.tsv', 'w', encoding='utf-8')
            csv_writer = csv.writer(file, delimiter='\t')
            csv_writer.writerow(['identifier'])

            dict_tuple_of_labels_to_csv_files[new_labels] = csv_writer

            add_query_to_cypher_file(new_labels, file_name)
        dict_tuple_of_labels_to_csv_files[new_labels].writerow([identifier])

        if 'rela' in node:
            relationship_infos = json.loads(node["rela"].replace('\\"', '"'))
            for rela in relationship_infos:
                symbols = rela['symbols'] if 'symbols' in rela else []
                xrefs = rela['xrefs'] if 'xrefs' in rela else []
                found_gene = False
                for xref in xrefs:
                    if xref.startswith('Gene'):
                        gene_id = xref.split(':')[1]
                        if gene_id in dict_gene_id_to_gene_node:
                            gene_symbols = set(dict_gene_id_to_gene_node[gene_id]['geneSymbol'])
                            found_gene = True
                            # in clivar is a different gene symbol which is in the gene synonyms
                            # if len(gene_symbols.intersection(symbols))==0:
                            #     print(identifier)
                            #     print(gene_id)
                            #     print(dict_gene_id_to_gene_node[gene_id])
                            #     print('different gene symbols')
                            csv_rela.writerow([str(gene_id), identifier])
                # all the not found is because they are linked to removed or replaced genes
                # if not found_gene:
                #     print(identifier)
                #     print('non gene found')
                #     print(rela)




'''
prepare the last queries, where the variant nodes get an index and the query for the relationship between gene and variants
'''


def perpare_queries_index_and_relationships():
    query = "CREATE CONSTRAINT ON (n:Variant) ASSERT n.identifier IS UNIQUE;\n"
    cypher_file.write(query)

    # relationship
    query = query_start + "(g:Gene{identifier:line.%s}), (v:Variant{identifier:line.%s}) Create  (g)-[:HAS_GhV{source:'ClinVar', resource:['ClinVar'], clinvar:'yes'}]->(v);\n"
    query = query % (path_of_directory, 'gene_variant', header_rela[0], header_rela[1])
    cypher_file.write(query)


def query_for_rela(file_name, label1, label2):
    """
    generate query for internal relationship
    :param file_name: string
    :param label1: string
    :param label2: string
    :return:
    """
    query = query_start + ''' (g:%s{identifier:line.identifier_1}), (c:%s{identifier:line.identifier_2}) Create (g)-[:HAS_%sh%s {source:'ClinVar', resource:['ClinVar'], license:"CC0 1.0", url:'https://www.ncbi.nlm.nih.gov/clinvar/variation/'+line.indetifier_1}]->(c);'''
    query = query % (path_of_directory, file_name, label1, label2, label1[0], label2[0])
    cypher_file.write(query)


def create_file(label1, label2):
    """
    generate a rela file for two labels and generate query
    :param label1: string
    :param label2: string
    :return: csv writer
    """
    file_name = label1 + '_' + label2
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
    for other_label in list_to_labels:
        short_label1 = label.split('_')[0]
        short_label2 = other_label.split('_')[0]
        csv_writer = create_file(short_label1, short_label2)

        query = "Match (c:%s)-[:has]->(d:%s) Return c.identifier, d.identifier"
        query = query % (label, other_label)
        results = g.run(query)
        for id1, id2, in results:
            csv_writer.writerow([id1, id2])

def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ClinVar')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all genes from database')

    load_genes_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all kind of properties of the variants')

    get_all_variation_properties()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all variation from database')

    load_all_variants_and_finish_the_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Add constraint and relationships to gene')

    perpare_queries_index_and_relationships()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Add relationships from Haplotype')

    get_variant_rela_intern('Haplotype_ClinVar',['Variant_ClinVar'])

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Add relationships from Genotype')

    get_variant_rela_intern('Genotype_ClinVar',['Variant_ClinVar', 'Haplotype_ClinVar'])

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
