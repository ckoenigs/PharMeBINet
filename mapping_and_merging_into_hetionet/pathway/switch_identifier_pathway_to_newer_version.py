import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# sys.path.append('../../drugbank/')

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with pharmebinet genes with identifier as key and value the name
dict_genes_pharmebinet = {}

# label of pathways
label_pathway = 'pathway_multi'

'''
load in all pathways from pharmebinet in a dictionary
'''


def load_genes_into_dict():
    query = '''MATCH (n:Gene) RETURN n.identifier,n.name'''
    results = g.run(query)

    for record in results:
        [identifier, name] = record.values()
        dict_genes_pharmebinet[identifier] = name

    print('number of pathway nodes in pharmebinet:' + str(len(dict_genes_pharmebinet)))


# header of the node tsv
header = []

# extra property
extra_property = 'all_mapped_ids'

'''
get the properties of pathway and make the list for the header of the tsv file
however ignore the properties with genes, because this information will be in the relationships 
'''


def get_pathway_properties():
    query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    query = query % (label_pathway)
    result = g.run(query)
    for property in result:
        property = property.data()['l']
        if property.find('gene') == -1:
            header.append(property)
    header.append('name')
    header.append(extra_property)
    header.append('resource')


# cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
# query to delete all old pathways
query = 'MATCH (n:Pathway) Detach Delete n;\n'
cypher_file.write(query)

# dictionary pathway name from pathway list an the identifier plus the source
dict_name_to_pc_or_wp_identifier = {}

# dictionary with own id from pc to name, pcid and sourc
dict_own_id_to_pcid_and_other = {}

# dictionary of identifier to nodes information
dict_id_to_node = {}

# tsv files for nodes and relationship
file_node = open('output/node.tsv', 'w', encoding='utf-8')
csv_node = csv.writer(file_node, delimiter='\t')

file_rela = open('output/rela.tsv', 'w', encoding='utf-8')
csv_rela = csv.writer(file_rela, delimiter='\t')
rela_header = ['gene_id', 'pathway_id']
csv_rela.writerow(rela_header)

# dictionary rela
dict_rela = {}

'''
load all pathway from neo4j
'''


def load_in_all_pathways():
    #
    query = '''MATCH (n:%s) RETURN n ''' % (label_pathway)
    results = g.run(query)

    untitle_name_id = 0
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_id_to_node[identifier] = dict(node)

        # fill dictionary with name to rest
        names = node['synonyms']
        for name in names:
            name = name.lower()
            if name == 'untitled':
                name = untitle_name_id
                untitle_name_id += 1
            if not name in dict_name_to_pc_or_wp_identifier:
                dict_name_to_pc_or_wp_identifier[name] = [dict(node)]
            else:
                dict_name_to_pc_or_wp_identifier[name].append(dict(node))
                # print( dict_name_to_pc_or_wp_identifier[name])

        for gene_id in node['genes']:
            gene_id = gene_id
            if gene_id in dict_genes_pharmebinet:
                dict_rela[(str(gene_id), identifier)] = 1
                # csv_rela.writerow([str(gene_id),identifier])

    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))


'''
combine the information of the different sources
'''


def combine_information_from_different_sources(list_of_nodes):
    dict_combined_information = defaultdict(set)
    for node in list_of_nodes:
        source = node['source']
        for key, value in node.items():
            if key == 'license':
                value = source + ':' + value
            if type(value) != list:
                dict_combined_information[key].add(value)
            else:
                dict_combined_information[key] = dict_combined_information[key].union(value)
    # dict_combined_information['source']=', '.join(dict_combined_information['source'])
    # dict_combined_information['license'] = ', '.join(dict_combined_information['license'])
    # maybe replace the sets with list or transform into string
    return dict_combined_information


# dictionary the old pc id to the new one
dict_old_pc_to_new = {}

# properties which are a list
list_list_properties = set([])

'''
Prepare value
'''


def prepare_value(value, head, combined_node):
    if head == 'identifier':
        if combined_node:
            identifier = value.pop()
            for old_id in value:
                dict_old_pc_to_new[old_id] = identifier
            value = identifier
    if type(value) in [list, set]:
        list_list_properties.add(head)
        if head == 'xrefs':
            value = go_through_xrefs_and_change_if_needed_source_name(value, 'Pathway')
        value = '|'.join(value)
    return value


'''
prepare the values for the list of properties
'''


def fill_the_list_of_properties(head, value, identifiers, resource, name, list_info):
    combine_node = False
    if head == 'identifier':
        identifiers = value
        if type(value) in [list, set]:
            identifiers = value.copy()
            combine_node = True
    elif head == 'license':
        if type(value) != str:
            value = ','.join(value)
    elif head == extra_property:
        value = identifiers
    elif head == 'source':
        if type(value) in [list, set]:
            list_value = list(sorted([x.capitalize() for x in value]))
            value = ",".join(list_value)
            resource = list_value
        else:
            value = value.capitalize()
            resource = [value]
    elif head == 'synonyms':
        name = value.pop()
        name = name if name != 'untitled' else ''
    elif head == 'url':
        if type(value) != str:
            value = ' , '.join(value)
    elif head == 'name':
        value = name
    elif head == 'resource':
        value = resource

    # prepare the value for tsv
    value = prepare_value(value, head, combine_node)
    list_info.append(value)
    return identifiers, name, resource


'''
fill the node tsv file by going through the name dictionary and maybe they nodes with the same name will be merges to one node
'''


def generate_node_tsv():
    csv_node.writerow(header)

    counter_double_names = 0
    counter_multiple = 0
    for name, list_of_nodes in dict_name_to_pc_or_wp_identifier.items():
        identifiers = ''
        resource = []
        if len(list_of_nodes) == 1:
            list_info = []
            node = list_of_nodes[0]

            for head in header:
                value = node[head] if head in node else ''
                identifiers, name, resource = fill_the_list_of_properties(head, value, identifiers, resource, name,
                                                                          list_info)
            csv_node.writerow(list_info)
        else:
            counter_double_names += 1
            if len(list_of_nodes) > 2:
                counter_multiple += 1
                print(list_of_nodes)
                print(len(list_of_nodes))
            dict_combined = combine_information_from_different_sources(list_of_nodes)

            licenses = dict_combined['license']

            list_info = []
            for head in header:
                value = dict_combined[head] if head in dict_combined else ''
                identifiers, name, resource = fill_the_list_of_properties(head, value, identifiers, resource, name,
                                                                          list_info)
            csv_node.writerow(list_info)

    print('number of duplicated once:' + str(counter_double_names))
    print('number of multies:' + str(counter_multiple))


# all gene pathway pairs which exists
all_existing_pairs = set()

'''
generate rela tsv and cypher file
'''


def generate_rela_tsv_and_cypher_queries():
    for (gene_id, identifier) in dict_rela.keys():
        # depending if the identifier is removed or not the correct identifier is written into the tsv file
        if not identifier in dict_old_pc_to_new and not (gene_id, identifier) in all_existing_pairs:
            csv_rela.writerow([gene_id, identifier])
            all_existing_pairs.add((gene_id, identifier))
        elif identifier in dict_old_pc_to_new and not (gene_id, dict_old_pc_to_new[identifier]) in all_existing_pairs:
            csv_rela.writerow([gene_id, dict_old_pc_to_new[identifier]])
            all_existing_pairs.add((gene_id, dict_old_pc_to_new[identifier]))

    # general start of queries
    # generate cypher for node creation
    query_node_middle = 'Create (n:Pathway{'
    for head in header:
        if head in list_list_properties and head != 'source':
            query_node_middle += head + ':split(line.' + head + ',"|"), '
        else:
            query_node_middle += head + ':line.' + head + ', '
    query_node = query_node_middle[:-2] + ', combined_wikipathway_and_pathway_common:"yes"})'
    query_node = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/pathway/output/node.tsv',
                                                   query_node)
    cypher_file.write(query_node)
    cypher_file.write(pharmebinetutils.prepare_index_query('Pathway','identifier'))
    cypher_file.write(pharmebinetutils.prepare_index_query_text('Pathway', 'name'))

    # query equal to
    query_equal = ' Match (b:%s ), (n:Pathway{identifier:line.identifier}) Where b.identifier in split(line.%s,"|") Create (n)-[:equal_to_multi_pathways]->(b)'
    query_equal = query_equal % (label_pathway, extra_property)
    query_equal = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/pathway/output/node.tsv',
                                                    query_equal)
    cypher_file.write(query_equal)

    # cypher query for relationships
    query_rela_middle = 'Match '
    for head in rela_header:
        if head.split('_')[0] == 'gene':
            query_rela_middle += '(g:Gene{identifier:line.' + head + '}) ,'
        else:
            query_rela_middle += '(p:Pathway{identifier:line.' + head + '}) ,'
    query_rela = query_rela_middle[
                 :-2] + ' Create (g)-[:PARTICIPATES_IN_GpiPW{license:p.license, source:p.source, unbiased:false, url:p.url, resource:p.resource, combined_wikipathway_and_pathway_common:"yes"}]->(p)'
    query_rela = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/pathway/output/rela.tsv',
                                                   query_rela)
    cypher_file.write(query_rela)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all pathways from pharmebinet into a dictionary')

    load_genes_into_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('load pathway properties')

    get_pathway_properties()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all pathways from neo4j into a dictionary')

    load_in_all_pathways()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Generate tsv for switch identifier and ')

    generate_node_tsv()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Generate tsv for rela ')

    generate_rela_tsv_and_cypher_queries()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
