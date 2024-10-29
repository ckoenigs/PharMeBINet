import datetime
import sys, csv

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')



# list of properties  which have a list element
list_properties_with_list_elements = ['gene_symbols', 'synonyms', 'xrefs', 'map_location', 'feature_type']


# dictionary from ncbi property to pharmebinet property name
dict_ncbi_property_to_pharmebinet_property = {
    "full_name_from_nomenclature_authority": 'name',
    "symbol": 'gene_symbol',
    "symbol_from_nomenclature_authority": 'gene_symbols',
    "dbxrefs": 'xrefs'
}

dict_pharmebinet_property_to_ncbi_property = dict(map(reversed, dict_ncbi_property_to_pharmebinet_property.items()))

# list of found gene ids, because i think not all gene ids from pharmebinet exists anymore
found_gene_ids = []


def add_value_into_dict_with_list_or_not(dict_insert, head, question_header, dict_with_values):
    # gene Symobole sind keine Liste, muss noch geaendert werden und Feature_type ist leer
    if question_header in dict_with_values:
        if head in list_properties_with_list_elements:
            if head == 'xrefs':
                dict_with_values[question_header] = go_through_xrefs_and_change_if_needed_source_name(
                    dict_with_values[question_header], 'Gene')
            dict_insert[head] = '|'.join(dict_with_values[question_header])
        else:
            dict_insert[head] = dict_with_values[question_header]


'''
load ncbi tsv file in and write only the important lines into a new tsv file for integration into Neo4j
'''


def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():
    header = ['identifier', 'name', 'description', 'chromosome', 'gene_symbols', 'synonyms', 'feature_type',
              'type_of_gene', 'map_location', 'xrefs', 'gene_symbol']
    file = open('output/genes.tsv', 'w')
    writer = csv.DictWriter(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                            fieldnames=header)
    writer.writeheader()

    cypher_file = open('output/cypher.cypher', 'w')
    query = '''Match (n:Gene_Ncbi {identifier:line.identifier}) Create (g:Gene{identifier:line.identifier, %s   '''

    on_create_string = ''
    for head in header:
        if head != 'identifier':
            if head == 'gene_symbols':
                part = head + ':'
            else:
                part = head.lower() + ':'
            if head in list_properties_with_list_elements:
                part += 'split(line.' + head + ',"|"), '
            else:
                part += 'line.' + head + ', '
            query += part
            on_create_string += part
    query =query %on_create_string
    query += 'ncbi:"yes", resource:["NCBI"], source:"Entrez Gene",  license:"https://www.ncbi.nlm.nih.gov/home/about/policies/", url:"http://identifiers.org/ncbigene/"+line.identifier, ncbi:"yes"}) Create (n)<-[:equal_to_ncbi_gene]-(g)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ncbi_gene/output/genes.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.write(pharmebinetutils.prepare_index_query('Gene','identifier'))
    cypher_file.write(pharmebinetutils.prepare_index_query_text('Gene', 'name'))
    cypher_file.close()

    query = '''MATCH (n:Gene_Ncbi) RETURN n.identifier, n.full_name_from_nomenclature_authority, n;'''
    results = g.run(query)
    counter_not_same_name = 0
    counter_all = 0
    counter_all_in_pharmebinet = 0
    counter_mapped_and_similar_names=0
    for record in results:
        [gene_id, name, node] = record.values()
        counter_all += 1
        # make a dictionary from the node
        node = dict(node)
        # generate on list of gene symbols
        gene_symbol = set([])

        # synonyms from other designations
        set_of_synoynmys_from_designation = set()

        # remove the empty values '-' and combine the list of other designations and symbols, and symbol_from-Nomeclature_authority and symbol
        for property, value in node.items():

            if type(value) == list:
                list_of_values = []
                for value_part in value:
                    if value_part != '-':
                        list_of_values.append(value_part)
                node[property] = list_of_values
            else:
                if value == '-':
                    node[property] = ''

            if property == 'other_designations' and len(list_of_values) != 0:
                set_of_synoynmys_from_designation = set_of_synoynmys_from_designation.union(value)
            elif property == 'symbol_from_nomenclature_authority' and value != '-':
                gene_symbol.add(value)
            elif property == 'symbol' and value != '-':
                gene_symbol.add(value)
                node[property] = value

        # make one list
        node['symbol_from_nomenclature_authority'] = list(gene_symbol)
        symbols_ncbi = [x.lower() for x in list(gene_symbol)]
        synonyms = node['synonyms'] if 'synonyms' in node else []
        synonyms = list(set_of_synoynmys_from_designation.union(synonyms))
        synonyms = [x.lower() for x in synonyms]

        if name is None or name == '-':
            # print('has no name')
            if 'description' not in node or node['description'] == '-' or node['description'] == '':
                print('description is also empty')
                node['description'] = ''
            node['full_name_from_nomenclature_authority'] = node['description']


        dict_for_insert_into_tsv = {}
        for head in header:
            if head in dict_pharmebinet_property_to_ncbi_property:
                add_value_into_dict_with_list_or_not(dict_for_insert_into_tsv, head,
                                                     dict_pharmebinet_property_to_ncbi_property[head], node)

            else:
                if head in node:
                    add_value_into_dict_with_list_or_not(dict_for_insert_into_tsv, head,
                                                         head, node)
        writer.writerow(dict_for_insert_into_tsv)

    print('number of all genes:' + str(counter_all))
    print('counter of all genes already in pharmebinet:' + str(counter_all_in_pharmebinet))
    print('counter not the same name:' + str(counter_not_same_name))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gnerate a tsv file with only the pharmebinet genes')

    load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
