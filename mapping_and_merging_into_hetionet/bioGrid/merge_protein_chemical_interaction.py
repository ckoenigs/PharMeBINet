import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary protein pair to dictionary with resource and interaction id and other information
dict_pair_chemical_protein_to_resource_and_pubmed = {}


def get_information_from_pharmebinet():
    """
    Get pharmebinet chemical-protein-interaction information
    :return:
    """
    global maximal_id

    query = '''MATCH (n:Chemical)-[a]->(m:Protein)  RETURN n.identifier, m.identifier, a.resource,  a.pubMed_ids, type(a);'''
    results = g.run(query)

    for record in results:
        [chemical_id, protein_id, resource, pubMed_ids, type_rela] = record
        pubMed_ids = pubMed_ids if pubMed_ids is not None else []
        dict_pair_chemical_protein_to_resource_and_pubmed[
            (chemical_id, protein_id, type_rela)] = {'resource': resource, 'pubmed_ids': pubMed_ids}


# dictionary_label_to file
dict_edge_type_to_file = {}


def generate_file_and_cypher():
    """
    generate cypher file and tsv file
    :return:
    """
    query = '''MATCH (p:bioGrid_interaction_with_chemical) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields; '''
    results = g.run(query)

    file_name = 'interaction/rela_chemical_protein'
    file_name_update = 'interaction/rela_match_chemical_protein'

    cypher_file = open('output/cypher_edge.cypher', 'a', encoding='utf-8')

    query_middle = ''
    query_middle_update = ''
    header = ['id_1', 'id_2', 'gene_id']
    for record in results:
        head = record.data()['allfields']
        header.append(head)
        if head in ['pubmed_id', 'notes']:
            if head != 'pubmed_id':
                query_middle += head + ':split(line.' + head + ',"|"), '
                query_middle_update += 'a.' + head + '=split(line.' + head + ',"|"), '
            else:
                query_middle += 'pubMed_ids:split(line.' + head + ',"|"), '
                query_middle_update += 'a.pubMed_ids=split(line.' + head + ',"|"), '
        elif head in ['author', 'interaction_id', 'biogrid_publication_id']:
            continue
        else:
            query_middle += head + ':line.' + head + ', '
            query_middle_update += 'a.' + head + '=line.' + head + ', '

    for rela_type in dict_chemical_type_to_rela_type.values():
        rename_file_name = file_name + rela_type
        query = '''Match (p1:Chemical{identifier:line.id_1}), (p2:Protein{identifier:line.id_2}) Create (p1)-[:%s{biogrid:'yes', source:'BioGRID', resource:['BioGRID'], url:"https://thebiogrid.org/"+line.gene_id ,license:"The MIT License", '''
        query = query % (rela_type)

        query += query_middle[:-2] + '}]->(p2)'

        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  'mapping_and_merging_into_hetionet/bioGrid/' + rename_file_name + '.tsv',
                                                  query)
        cypher_file.write(query)

        rename_file_name_update = file_name_update + rela_type
        query_update = '''Match (p1:Chemical{identifier:line.id_1})-[a:%s]->(p2:Protein{identifier:line.id_2}) Set '''
        query_update = query_update % (rela_type)
        query_update += query_middle_update + 'a.biogrid="yes",  a.resource=split(line.resource,"|")'
        query_update = pharmebinetutils.get_query_import(path_of_directory,
                                                         'mapping_and_merging_into_hetionet/bioGrid/' + rename_file_name_update + '.tsv',
                                                         query_update)
        cypher_file.write(query_update)

        file = open(rename_file_name + '.tsv', 'w', encoding='utf-8')
        csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
        csv_writer.writeheader()

        dict_edge_type_to_file[rela_type] = csv_writer

        header_merge = header.copy()
        header_merge.append('resource')
        file_merge = open(rename_file_name_update + '.tsv', 'w', encoding='utf-8')
        csv_writer_merge = csv.DictWriter(file_merge, fieldnames=header_merge, delimiter='\t')
        csv_writer_merge.writeheader()
        dict_edge_type_to_file[rela_type + 'update'] = csv_writer_merge
    cypher_file.close()

    return csv_writer, csv_writer_merge


def prepare_dictionary(dictionary):
    """
    prepare the list values in dictionary to strings
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) in [list, set]:
            value = '|'.join(value)
        new_dict[key] = value
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}

# dictionary for rela type
dict_chemical_type_to_rela_type = {
    "inhibitor": "INHIBITS_CHiP",
    "unknown": "ASSOCIATES_CHaP",
    "modulator": "REGULATES_CHrP",
    "activator": "UPREGULATES_CHuP"
}


def load_and_prepare_biogrid_human_data():
    """
    write only rela with exp into file
    """

    query = '''Match p=(s:Protein)--(:Gene)--(n:bioGrid_gene)-[o:interacts]-(r:bioGrid_interaction_with_chemical)-[q]-(:bioGrid_chemical)--(m:Chemical) Where r.curated_by<>'DRUGBANK' and not (r)-[:related_gene]-(:bioGrid_gene) Return s.identifier,m.identifier, o.interaction_type, q.action, r, n.gene_id'''
    results = g.run(query)
    for record in results:
        [protein_id, chemical_id, protein_action_type, chemical_action_type, rela, gene_id] = record.values()
        if protein_action_type != 'target':
            sys.exit('other protein action type );')

        if chemical_action_type not in dict_chemical_type_to_rela_type:
            sys.exit('other chemical action type );')
        rela_info = dict(rela)
        if (chemical_id, protein_id, protein_action_type, chemical_action_type) not in dict_pair_to_infos:
            dict_pair_to_infos[(chemical_id, protein_id, protein_action_type, chemical_action_type)] = []

        rela_info['gene_id'] = gene_id

        dict_pair_to_infos[(chemical_id, protein_id, protein_action_type, chemical_action_type)].append(rela_info)


# set of key where different information appeare
set_of_keys_with_different_values = set()


def prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2):
    """
    Prepare if multiple edges exists for a pair a combined information edge.
    :param list_of_dict: list of dicitonaries
    :param p1: string
    :param p2: string
    :return:
    """
    new_dict = {}
    for dictionary in list_of_dict:
        for key, value in dictionary.items():
            if not key in new_dict:
                new_dict[key] = value
            elif new_dict[key] != value:
                # print(p1)
                # print(p2)
                if key not in set_of_keys_with_different_values:
                    print(key)
                    print(value)
                    print(new_dict[key])
                    set_of_keys_with_different_values.add(key)
                if type(value) == list:
                    set_value = set(value)
                    set_value = set_value.union(new_dict[key])
                    new_dict[key] = list(set_value)
                else:
                    if type(new_dict[key]) != set:
                        new_dict[key] = set([new_dict[key]])
                    new_dict[key].add(value)
    return new_dict


def prepareMappedEdges(p1, p2, rela_type, list_of_dict):
    """
    Prepare the mapped information to one edge and writ it into a csv file
    :param p1: chemical id
    :param p2: sprotein id
    :param list_of_dict:list of dictionaries
    :return:
    """
    pubmed_ids = set(dict_pair_chemical_protein_to_resource_and_pubmed[(p1, p2, rela_type)]['pubmed_ids'])
    if len(list_of_dict) == 1:
        final_dictionary = list_of_dict[0]
    else:
        final_dictionary = prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2)
    final_dictionary['resource'] = pharmebinetutils.resource_add_and_prepare(
        dict_pair_chemical_protein_to_resource_and_pubmed[(p1, p2, rela_type)]['resource'], 'BioGRID')
    gene_id = final_dictionary['gene_id'] if type(final_dictionary['gene_id']) == str else final_dictionary[
        'gene_id'].pop()
    if type(final_dictionary['pubmed_id']) != str:
        for pubmed_id in final_dictionary['pubmed_id']:
            pubmed_ids.add(pubmed_id)
    else:
        pubmed_ids.add(final_dictionary['pubmed_id'])

    final_dictionary['pubmed_id'] = pubmed_ids
    final_dictionary['gene_id'] = gene_id

    final_dictionary['id_1'] = p1
    final_dictionary['id_2'] = p2
    dict_edge_type_to_file[rela_type + 'update'].writerow(prepare_dictionary(final_dictionary))


# set of added pairs
set_of_added_pair = set()


def write_info_into_files():
    """
    Check if a pair exist already in Pharmebinet or not and prepare the information for this.
    :return:
    """
    csv_writer, csv_merge = generate_file_and_cypher()
    for (p1, p2, protein_action_type, chemical_action_type), list_of_dict in dict_pair_to_infos.items():
        rela_type = dict_chemical_type_to_rela_type[chemical_action_type]
        if (p1, p2, rela_type) in dict_pair_chemical_protein_to_resource_and_pubmed:
            prepareMappedEdges(p1, p2, rela_type, list_of_dict)
        else:
            if len(list_of_dict) == 1:
                final_dictionary = list_of_dict[0]
            else:
                # print('multi')
                final_dictionary = prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2)

            pubmed_ids = set()
            if type(final_dictionary['pubmed_id']) != str:
                for pubmed_id in final_dictionary['pubmed_id']:
                    pubmed_ids.add(pubmed_id)
            else:
                pubmed_ids.add(final_dictionary['pubmed_id'])

            final_dictionary['pubmed_id'] = pubmed_ids
            gene_id = final_dictionary['gene_id'] if type(final_dictionary['gene_id']) == str else \
                final_dictionary['gene_id'][
                    0]
            final_dictionary['gene_id'] = gene_id
            final_dictionary['id_1'] = p1
            final_dictionary['id_2'] = p2

            dict_edge_type_to_file[rela_type].writerow(prepare_dictionary(final_dictionary))
            set_of_added_pair.add((p1, p2))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory, dict_interaction_id_to_connection_to_other_nodes
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate connection to neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('get chemical-protein information')

    get_information_from_pharmebinet()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('load bioGrid human data')

    load_and_prepare_biogrid_human_data()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('prepare files')

    write_info_into_files()
    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
