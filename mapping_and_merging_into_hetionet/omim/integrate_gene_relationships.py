import sys
import datetime
import csv

sys.path.append("../..")
import create_connection_to_databases


def database_connection():
    """
    create connection to neo4j
    :return:
    """
    global g
    g = create_connection_to_databases.database_connection_neo4j()


cypher_file = open('output/cypher_rela.cypher', 'w', encoding='utf-8')

query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/omim/%s" As line FIELDTERMINATOR '\\t' 
    Match (g:Gene{identifier:line.%s}),(to:%s{identifier:line.%s}) Merge (g)<-[r:ASSOCIATES_%saG]-(to) On Create Set r.resource=['OMIM'], r.source='OMIM', r.omim='yes', r.license='Copyright® 1966-2020 Johns Hopkins University', %s On Match Set r.resource=r.resource+'OMIM', r.omim="yes", %s ;\n'''


def prepare_cypher_query(file, header_start, to_label):
    """
    generate the different cypher files for Disease and Phenotyp
    :param file: string
    :param header_start: list with two entries
    :param to_label: string
    :return:
    """
    query = '''MATCH (n:gene_omim)-[p]-(h) Where 'phenotype_omim' in labels(h) or 'predominantly_phenotypes_omim' in labels(h) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields; '''
    result = g.run(query)

    query_merge = ""
    for key, in result:
        query_merge += "r." + key + '=split(line.' + key + ",'|'), "
        header_start.append(key)

    query_merge = query_merge[:-2]
    combine_cypher = query_start
    combine_cypher = combine_cypher % (
        path_of_directory, file, header_start[0], to_label, header_start[1], to_label[0], query_merge, query_merge)

    cypher_file.write(combine_cypher)


def prepare_csv_files(label):
    """
    generate a csv file in a given path with a given header
    :param label: string
    :return:
    """
    file_name = 'rela/gene_' + label + '_rela.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    file_header = ['gene_id', 'to_id']
    prepare_cypher_query(file_name, file_header, label)
    csv_writer.writerow(file_header)

    return csv_writer, file_header


# dictionary gene-disease: rela info
dict_gene_disease = {}

# dictionary gene-phenotype: rela info
dict_gene_phenotype = {}


def put_pair_in_dictionary(gene_id, rela, to_id, dictionary):
    """
    add gene-x pair in the dictionary with value the relationship infos
    :param gene_id: string
    :param rela: dictionary/object
    :param to_id: string
    :param dictionary: dictionary
    :return:
    """
    if not (gene_id, to_id) in dictionary:
        new_dictionary_rela = {}
        for key, value in dict(rela).items():
            if type(value) == list:
                new_dictionary_rela[key] = set(value)
            else:
                new_dictionary_rela[key] = set([value])

        dictionary[(gene_id, to_id)] = new_dictionary_rela
    else:
        print('ohje multiple edges')
        print(gene_id, to_id)
        for key, value in dict(rela).items():
            if key in dictionary[(gene_id, to_id)]:
                if type(value) == list:
                    dictionary[(gene_id, to_id)][key].union(value)
                else:
                    dictionary[(gene_id, to_id)][key].add(value)
            else:
                if type(value) == list:
                    dictionary[(gene_id, to_id)][key] = set(value)
                else:
                    dictionary[(gene_id, to_id)][key] = {value}


def load_all_omim_gene_phenotypes():
    """
    load all genes, association rela, disease or phenotype id and the labels
    """
    # {identifier:'604260'}
    query = "MATCH (g:Gene)--(n:gene_omim)-[r:associates]-(h)--(p) Where 'Disease' in labels(p) or 'Phenotype' in labels(p) RETURN g.identifier, r, p.identifier, labels(p)"
    results = g.run(query)

    for gene_id, rela, to_id, to_labels in results:
        if 'Disease' in to_labels:
            put_pair_in_dictionary(gene_id, rela, to_id, dict_gene_disease)
        else:
            put_pair_in_dictionary(gene_id, rela, to_id, dict_gene_phenotype)


def prepare_set_to_string(set_of_lists):
    """
    transform set to a list and then to a joined string
    :param set_of_lists: set
    :return: string
    """
    return "|".join(list(set_of_lists))


def generate_csv_and_cypher_file(label, dictionary):
    """
    generate csv and fill it and also generate cypher query
    :param label: string
    :param dictionary: dictionary
    :return:
    """
    csv_writer, header = prepare_csv_files(label)
    for (gene_id, to_id), properties in dictionary.items():
        list_information = [gene_id, to_id]
        # add properties in the right order
        for key in header[2:]:
            list_information.append(
                prepare_set_to_string(properties[key])) if key in properties else list_information.append('')
        csv_writer.writerow(list_information)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path omim')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Gene mapping')

    load_all_omim_gene_phenotypes()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Prepare rela to disease as cypher query and csv file')

    generate_csv_and_cypher_file('Disease', dict_gene_disease)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Prepare rela to phenotyp as cypher query and csv file')

    generate_csv_and_cypher_file('Phenotype', dict_gene_phenotype)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
