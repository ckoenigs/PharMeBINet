import sys
import datetime
import csv

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

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


cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')


def add_query_to_cypher_file(omim_label, database_label, rela_name_addition, file_name, integer_id=False):
    """
    add query for a specific tsv to cypher file
    """
    if integer_id:
        this_start_query = "Match (n:%s {identifier:line.identifier}), (m:%s{identifier:toInteger(line.database_id)})"
    else:
        this_start_query = "Match (n:%s {identifier:line.identifier}), (m:%s{identifier:line.database_id}) "
    this_start_query += "Set m.resource=split(line.resource,'|'), m.omim='yes' Create (m)-[:equal_to_omim_%s{how_mapped:line.how_mapped}]->(n)"
    query = this_start_query % (omim_label, database_label, rela_name_addition)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/omim/{file_name}',
                                              query)
    cypher_file.write(query)


def create_query_for_phenotype(label, file_name):
    """
    create the query for Phenotype by getting the properties form omim
    :param label:string
    :param file_name:string
    :return:
    """
    query_create = 'Match  (n:%s {identifier:line.identifier}) Create (p:Phenotype {'
    query = 'MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'
    query = query % label
    results = g.run(query)
    for record in results:
        property = record.data()['l']
        if property != 'alternative_names':
            query_create += property + ':n.' + property + ', '
        else:
            query_create += 'synonyms:n.' + property + ', '
    query_create += ' license:"https://www.omim.org/help/agreement", url:"https://www.omim.org/entry/"+line.identifier , source:"OMIM", resource:["OMIM"], omim:"yes"}) Create (p)-[:equal_to_omim{how_mapped:"new"}]->(n)'
    query_create = query_create % (label)

    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/omim/{file_name}',
                                                     query_create)
    cypher_file.write(query_create)


# dictionary_omim_gene_id_to_node
dict_omim_id_to_node = {}

# dictionary of mapping tuples
dict_of_mapped_tuples = {}

# set of not mapped omim gene ids
set_not_mapped_ids = set()

# file header
file_header = ['identifier', 'database_id', 'resource', 'xrefs', 'how_mapped']


def prepare_tsv_files(file_name, header):
    """
    generate a tsv file in a given path with a given header
    :param file_name: string
    :param header: string
    :return:
    """
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(header)

    return csv_writer


def add_mapped_one_to_tsv_file(dict_node_info, omim_id, mapped_id, csv_writer, mapping_dict, how_mapped, is_int=False):
    """
Get the xrefs information from the existing nodes. Add the omim id to the xrefs. Also, add OMIM to resource and write information into tsv file.
        :param dict_node_info:
        :param omim_id: string
        :param mapped_id:string
        :param csv_writer:csv writer
        :param mapping_dict: dictionary
        :param how_mapped:string
        :param is_int:
        :return:
        """
    if is_int:
        dict_node = dict_node_info[int(mapped_id)]
    else:
        dict_node = dict_node_info[mapped_id]

    xrefs = dict_node['xrefs'] if 'xref' not in dict_node else []
    xrefs.append('OMIM' + ':' + omim_id)
    xrefs = go_through_xrefs_and_change_if_needed_source_name(
        xrefs, 'Gene') if is_int else go_through_xrefs_and_change_if_needed_source_name(
        xrefs, 'Disease')

    resource = dict_node['resource']
    resource.append('OMIM')
    resource = list(set(resource))
    csv_writer.writerow([omim_id, mapped_id, "|".join(resource), "|".join(xrefs), how_mapped])
    mapping_dict[(omim_id, mapped_id)] = 1


# dictionary disease id to disease node
dict_disease_id_to_disease_node = {}

# dictionary omim id to disease ids
dict_omim_id_to_disease_ids = {}

# dictionary name to disease ids
dict_name_to_disease_ids = {}

# dictionary gene id to gene node
dict_gene_id_to_gene_node = {}


def load_genes_from_database_and_add_to_dict():
    """
    Load all Genes from my database  and add them into a dictionary
    """
    query = "MATCH (n:Gene) RETURN n"
    results = g.run(query)
    for record in results:
        gene = record.data()['n']
        identifier = gene['identifier']
        dict_gene_id_to_gene_node[identifier] = dict(gene)


def load_disease_from_database_and_add_to_dict():
    """
    Load all Disease from my database  and add them into a dictionary
    """
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_disease_id_to_disease_node[identifier] = dict(node)
        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('OMIM:'):
                omim_id = xref.split(':')[1]
                if omim_id not in dict_omim_id_to_disease_ids:
                    dict_omim_id_to_disease_ids[omim_id] = []
                dict_omim_id_to_disease_ids[omim_id].append(identifier)
        name = node['name'].lower()
        if name not in dict_name_to_disease_ids:
            dict_name_to_disease_ids[name] = set()
        dict_name_to_disease_ids[name].add(identifier)
        if 'synonyms' in node:
            for synonym in node['synonyms']:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                if synonym not in dict_name_to_disease_ids:
                    dict_name_to_disease_ids[synonym] = set()
                dict_name_to_disease_ids[synonym].add(identifier)
    print("number of omim to disease:" + str(len(dict_omim_id_to_disease_ids)))


# dictionary omim id to phenotype node
dict_omim_id_to_phenotype = {}

# dictionary mapped tuple to counter
dict_mapped_phenotype_disease_tuple = {}


def load_phenotype_from_omim_and_map():
    query = "MATCH (n:predominantly_phenotypes_omim) Where not n:phenotype_omim and not n:gene_omim RETURN n, labels(n)"
    results = g.run(query)

    # generate tsv file
    file = open("gene/mapping.tsv", 'a', encoding='utf-8')
    csv_writer_gene = csv.writer(file, delimiter='\t')

    file_name = "disease/mapping_2.tsv"
    csv_writer = prepare_tsv_files(file_name, file_header)

    file_name_not_mapped = "disease/not_mapping_2.tsv"
    csv_writer_not = prepare_tsv_files(file_name_not_mapped, ['identifier', 'name', 'detail_information', 'xrefs'])

    counter_mapped = 0
    counter_not_mapped = 0
    counter_different_names = 0

    # generate query
    add_query_to_cypher_file('predominantly_phenotypes_omim', 'Disease', 'disease', file_name)
    create_query_for_phenotype('predominantly_phenotypes_omim', file_name_not_mapped)
    for record in results:
        [node, labels] = record.values()
        identifier = node['identifier']
        name = node['name'].lower() if 'name' in node else ''
        synonyms = [x.lower() for x in node['alternative_names']] if 'alternative_names' in node else []
        synonyms.append(name)

        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('NCBI_GENE:'):
                ncbi_id = xref.split(':')[1]
                if int(ncbi_id) in dict_gene_id_to_gene_node:

                    if (identifier, ncbi_id) not in dict_of_mapped_tuples:
                        add_mapped_one_to_tsv_file(dict_gene_id_to_gene_node, identifier, ncbi_id, csv_writer_gene,
                                                   dict_of_mapped_tuples, 'gene_id', is_int=True)

        dict_omim_id_to_phenotype[identifier] = dict(node)
        if identifier in dict_omim_id_to_disease_ids:
            counter_mapped += 1
            for mondo_id in dict_omim_id_to_disease_ids[identifier]:
                disease_node = dict_disease_id_to_disease_node[mondo_id]
                disease_synoynms = [x.lower() for x in disease_node['synonyms']] if 'synonyms' in disease_node else []
                if 'name' in disease_node:
                    disease_synoynms.append(disease_node['name'].lower())
                if len(set(synonyms).intersection(disease_synoynms)) == 0:
                    counter_different_names += 1
                    print('different names')
                    print(synonyms)
                    print(disease_synoynms)
                    print((identifier, mondo_id))
                add_mapped_one_to_tsv_file(dict_disease_id_to_disease_node, identifier, mondo_id, csv_writer,
                                           dict_mapped_phenotype_disease_tuple, 'omim_id')
        else:

            name = node['name'].lower() if 'name' in node else ''
            if name in dict_name_to_disease_ids:
                counter_mapped += 1
                for mondo_id in dict_name_to_disease_ids[name]:
                    add_mapped_one_to_tsv_file(dict_disease_id_to_disease_node, identifier, mondo_id, csv_writer,
                                               dict_mapped_phenotype_disease_tuple, 'name')

            else:
                counter_not_mapped += 1
                xrefs = node['xrefs'] if 'xrefs' in node else []
                detail_information = node['detail_information'] if 'detail_information' in node else []
                csv_writer_not.writerow([identifier, name, detail_information, xrefs])
    print('number of mapped phenotypes:' + str(counter_mapped))
    print('number of not mapped phenotypes:' + str(counter_not_mapped))
    print('number of different names:', counter_different_names)


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
    print('Load all disease from database')

    load_disease_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all gene from database')

    load_genes_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all omim phenotypes from database and map')

    load_phenotype_from_omim_and_map()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
