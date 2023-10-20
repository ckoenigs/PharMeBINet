import sys
import datetime
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def database_connection():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


cypher_file = open('output/cypher_rela.cypher', 'w', encoding='utf-8')

# dictionary first letter to rela letters
dict_first_letter_to_rela_letter = {
    'D': 'D',
    'P': 'PT'
}

query_start = '''Match (g:Gene{identifier:line.%s}),(to:%s{identifier:line.%s}) Merge (g)<-[r:ASSOCIATES_%saG]-(to) On Create Set r.resource=['OMIM'], r.source='OMIM', r.url="https://www.omim.org/entry/"+line.%s , r.omim='yes', r.license='https://www.omim.org/help/agreement', %s On Match Set r.resource=r.resource+'OMIM', r.omim="yes", %s '''


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
        RETURN allfields as l; '''
    results = g.run(query)

    query_merge = ""
    for record in results:
        key = record.data()['l']
        query_merge += "r." + key + '=split(line.' + key + ",'|'), "
        header_start.append(key)

    query_merge = query_merge[:-2]
    combine_cypher = query_start
    combine_cypher = combine_cypher % (header_start[0], to_label, header_start[1],
                                       dict_first_letter_to_rela_letter[to_label[0]], 'omim_id', query_merge,
                                       query_merge)

    combine_cypher = pharmebinetutils.get_query_import(path_of_directory,
                                                       f'mapping_and_merging_into_hetionet/omim/{file}',
                                                       combine_cypher)

    cypher_file.write(combine_cypher)


def prepare_tsv_files(label):
    """
    generate a tsv file in a given path with a given header
    :param label: string
    :return:
    """
    file_name = 'rela/gene_' + label + '_rela.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    file_header = ['gene_id', 'to_id', 'omim_id']
    prepare_cypher_query(file_name, file_header, label)
    csv_writer.writerow(file_header)

    return csv_writer, file_header


# dictionary gene-disease: rela info
dict_gene_disease = {}

# dictionary gene-phenotype: rela info
dict_gene_phenotype = {}


def put_pair_in_dictionary(gene_id, rela, to_id, dictionary, omim_id):
    """
    add gene-x pair in the dictionary with value the relationship infos
    :param gene_id: string
    :param rela: dictionary/object
    :param to_id: string
    :param dictionary: dictionary
    :param omim_id: string
    :return:
    """
    if not (gene_id, to_id) in dictionary:
        new_dictionary_rela = {}
        for key, value in dict(rela).items():
            if type(value) == list:
                new_dictionary_rela[key] = set(value)
            else:
                new_dictionary_rela[key] = set([value])
        new_dictionary_rela['omim_id'] = omim_id
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
    query = "MATCH (g:Gene)--(n:gene_omim)-[r:associates]-(h)--(p) Where 'Disease' in labels(p) or 'Phenotype' in labels(p) RETURN g.identifier, r, p.identifier, labels(p), n.identifier"
    results = g.run(query)

    for record in results:
        [gene_id, rela, to_id, to_labels, omim_id] = record.values()
        if 'Disease' in to_labels:
            put_pair_in_dictionary(gene_id, rela, to_id, dict_gene_disease, omim_id)
        else:
            put_pair_in_dictionary(gene_id, rela, to_id, dict_gene_phenotype, omim_id)


def prepare_set_to_string(set_of_lists):
    """
    transform set to a list and then to a joined string
    :param set_of_lists: set
    :return: string
    """
    return "|".join(list(set_of_lists))


def generate_tsv_and_cypher_file(label, dictionary):
    """
    generate tsv and fill it and also generate cypher query
    :param label: string
    :param dictionary: dictionary
    :return:
    """
    csv_writer, header = prepare_tsv_files(label)
    for (gene_id, to_id), properties in dictionary.items():
        list_information = [gene_id, to_id, properties['omim_id']]
        # add properties in the right order
        for key in header[3:]:
            list_information.append(
                prepare_set_to_string(properties[key])) if key in properties else list_information.append('')
        csv_writer.writerow(list_information)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path omim')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Gene mapping')

    load_all_omim_gene_phenotypes()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Prepare rela to disease as cypher query and tsv file')

    generate_tsv_and_cypher_file('Disease', dict_gene_disease)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Prepare rela to phenotyp as cypher query and tsv file')

    generate_tsv_and_cypher_file('Phenotype', dict_gene_phenotype)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
