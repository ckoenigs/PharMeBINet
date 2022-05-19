import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

# disease ontology license
license = 'CC BY 4.0'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary tsv files
dict_label_to_label_to_rela_to_tsv = defaultdict(dict)

# header of tsv file
header = ['go_id', 'other_id']

# cypher file
cypher_file = open('output/cypher_edge.cypher', 'w')

# dictionary for relationship ends
dict_relationship_ends = {
    "BiologicalProcess": 'BP',
    "MolecularFunction": 'MF',
    "CellularComponent": 'CC',
    "Protein": 'P',
    "Gene": 'G'
}


def get_go_rela_properties():
    """
    Get the rela properties and prepare the rela cypher query and the tsv header list.
    :return:
    """
    query = '''MATCH (:protein_go)-[p]-(:go) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    result = g.run(query)
    query_nodes_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/go/%s" As line FIELDTERMINATOR '\\t' '''

    part = ''' Match (b:%s{identifier:line.go_id}), (c:%s{identifier:line.other_id}) Create (c)-[:%s{'''
    for property, in result:
        if property in ['db_reference', 'with_from', 'annotation_extension', 'xrefs', 'gene_product_id', 'date',
                        'assigned_by', 'evidence']:
            if property == 'db_reference':
                part += 'pubMed_ids:split(line.pubmed_ids,"|"), '
                header.append('pubmed_ids')
                continue
            elif property == 'evidence':
                part += property + 's:split(line.' + property + ',"|"), '
                header.append(property)
                continue
            part += property + ':split(line.' + property + ',"|"), '
        else:
            if property not in ['gene_product_id', 'qualifier']:
                part += property + ':line.' + property + ', '
            else:
                part += 'not:line.' + property + ', '
        header.append(property)
    global query_rela

    # combine the important parts of node creation
    query_rela = query_nodes_start + part + 'resource:["GO"], go:"yes", source:"Gene Ontology", url:"http://purl.obolibrary.org/obo/"+line.go_id, license:"' + license + '"}]->(b);\n'


def create_tsv_file(go_label, other_label, rela_type):
    """
    Generate tsv files for given labels and rela type. Also the cypher query is prepared and add to the cypher file.
    :param go_label: string
    :param other_label: string
    :param rela_type: string
    :return:
    """
    file_name = 'edge_go_protein_gene/%s_%s_%s.tsv' % (go_label, other_label, rela_type)
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, delimiter='\t', fieldnames=header)
    csv_writer.writeheader()

    rela_type_neo4j = rela_type.upper() + '_' + dict_relationship_ends[other_label] + ''.join(
        [x[0].lower() for x in rela_type.split('_')]) + dict_relationship_ends[go_label]

    query = query_rela % (file_name, go_label, other_label, rela_type_neo4j)
    cypher_file.write(query)

    dict_label_to_label_to_rela_to_tsv[go_label][other_label][rela_type] = csv_writer


def write_rela_info_into_file(go_id, other_id, rela, go_label, other_label, rela_type):
    """
    Prepare rela information and write into tsv file
    :param go_id: string
    :param other_id: string
    :param rela: dictionary
    :param go_label: string
    :param other_label: string
    :param rela_type: string
    :return:
    """
    dict_rela = {'go_id': go_id, 'other_id': other_id}
    for prop, value in rela.items():
        if prop == 'db_reference':
            pubmed_ids = set()
            for entry in value:
                if entry.startswith('PMID:'):
                    pubmed_ids.add(entry.split(':', 1)[1])
            dict_rela['pubmed_ids'] = '|'.join(pubmed_ids)
            continue

        if type(value) != str:
            value = '|'.join(value)
        elif prop == 'qualifier':
            if value.startswith('NOT|'):
                value = True
            else:
                value = ''

        dict_rela[prop] = value

    dict_label_to_label_to_rela_to_tsv[go_label][other_label][rela_type].writerow(dict_rela)


# dictionary label to other label to rela type_to_pairs_ to rela info
dict_label_to_label_to_rela_type_pairs_to_rela_info = defaultdict(dict)



def check_for_difference_in_rela_information(dict_first, dict_new_rela_info, go_id, other_id):
    """

    :param dict_first:
    :param dict_new_rela_info:
    :param go_id:
    :param other_id:
    :return:
    """

    for key, value in dict_new_rela_info.items():
        if key in dict_first and value != dict_first[key]:
            if key in ['db_reference', 'annotation_extension', 'assigned_by', 'with_from', 'gene_product_id',
                        'date']:
                dict_first[key].extend(value)
                continue
            elif key in ['evidence'] and type(dict_first[key]) != set:
                dict_first[key] = set([dict_first[key]])
                dict_first[key].add(value)
                continue
            elif key in ['evidence']:
                dict_first[key].add(value)
                continue
            print('different data ', key, go_id, other_id)
            print(value)
            print(dict_first[key])
        elif key not in dict_first:
            if key == 'annotation_extension':
                dict_first[key] = value
                continue
            print(go_id, other_id)
            print('new data ', key)
            print(value)


'''
go through all go nodes and sort them into the dictionary 
'''


def get_all_relationship_pairs(go_label, other_label):
    query = '''Match (n:%s)--(:go)-[r]-(:protein_go)--(m:%s) Return n.identifier, m.identifier, type(r), r''' % (
        go_label, other_label)
    result = g.run(query)
    dict_label_to_label_to_rela_to_tsv[go_label][other_label] = {}
    dict_label_to_label_to_rela_type_pairs_to_rela_info[go_label][other_label] = {}
    counter_double = 0
    for go_id, other_id, rela_type, rela, in result:
        if rela_type not in dict_label_to_label_to_rela_to_tsv[go_label][other_label]:
            create_tsv_file(go_label, other_label, rela_type)
            dict_label_to_label_to_rela_type_pairs_to_rela_info[go_label][other_label][rela_type] = {}
        rela = dict(rela)
        if (go_id, other_id) in dict_label_to_label_to_rela_type_pairs_to_rela_info[go_label][other_label][rela_type]:
            check_for_difference_in_rela_information(
                dict_label_to_label_to_rela_type_pairs_to_rela_info[go_label][other_label][rela_type][
                    (go_id, other_id)], rela, go_id, other_id)
            counter_double += 1
            continue
        dict_label_to_label_to_rela_type_pairs_to_rela_info[go_label][other_label][rela_type][(go_id, other_id)] = rela
    print('counter of double rela:', counter_double)


def write_the_combined_rela_into_files():
    """
    Write the combined rela information into the right tsv files
    :return:
    """
    for go_label, dict_other_label_to_rela_type_pairs_to_rela_info in dict_label_to_label_to_rela_type_pairs_to_rela_info.items():
        for other_label, dict_rela_type_pairs_to_rela_info in dict_other_label_to_rela_type_pairs_to_rela_info.items():
            for rela_type, dict_pairs_to_rela_info in dict_rela_type_pairs_to_rela_info.items():
                for (go_id, other_id), rela in dict_pairs_to_rela_info.items():
                    write_rela_info_into_file(go_id, other_id, rela, go_label, other_label, rela_type)


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

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('get all rela properties and prepare query')

    get_go_rela_properties()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('go through all gos rela in dictionary')

    for go_label in ['BiologicalProcess', 'MolecularFunction', 'CellularComponent']:
        for other_label in ['Protein', 'Gene']:
            print(go_label, other_label)

            get_all_relationship_pairs(go_label, other_label)
        #     break
        # break

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('write combined rela information into tsv files')

    write_the_combined_rela_into_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
