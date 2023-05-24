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


def get_all_interaction_of_a_given_type(label, biogrid_label, dictionary):
    """
    Get all other nodes connected to biogrid interaction and write them into a dictionary
    :param label: string
    :param biogrid_label: string
    :param dictionary: dictionary
    :return:
    """
    query = f'Match (r:bioGrid_interaction)--(:{biogrid_label})--(n:{label}) Return r.interaction_id, n.identifier'
    results = g.run(query)
    for record in results:
        [interaction_id, other_node_id] = record.values()
        if interaction_id not in dictionary:
            dictionary[interaction_id] = {}
        if label not in dictionary[interaction_id]:
            dictionary[interaction_id][label] = set()
        dictionary[interaction_id][label].add(other_node_id)


# dictionary protein pair to dictionary with resource and interaction id and other information
dict_protein_pair_to_dictionary = {}


def get_information_from_pharmebinet():
    """
    Get pharmebinet protein-protein-interaction information
    :return:
    """
    global maximal_id

    query = '''MATCH (n:Protein)-->(a:Interaction)-->(m:Protein) Where not (a.iso_of_protein_from is not NULL or a.iso_of_protein_to is not NULL)  RETURN n.identifier, m.identifier, a.resource, a.identifier, a.interaction_ids, a.pubMed_ids;'''
    results = g.run(query)

    for record in results:
        [interactor1_het_id, interactor2_het_id, resource, interaction_id, interaction_ids_EBI,
         pubMed_ids] = record.values()
        pubMed_ids = pubMed_ids if pubMed_ids is not None else []
        dict_protein_pair_to_dictionary[
            (interactor1_het_id, interactor2_het_id)] = {'resource': resource,
                                                         'interaction_ids_EBI': interaction_ids_EBI,
                                                         'interaction_id': interaction_id, 'pubmed_ids': pubMed_ids}

    query = 'MATCH (n:Interaction) With toInteger(n.identifier ) as int_id RETURN max(int_id) as v'

    maximal_id = g.run(query).single()['v']


# dictionary_label_to file
dict_label_to_file = {}


def generate_file_and_cypher(labels):
    """
    generate cypher file and tsv file
    :return:
    """
    query = '''MATCH (p:bioGrid_interaction) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields; '''
    results = g.run(query)

    file_name = 'interaction/rela_ppi'
    file_name_update = 'interaction/rela_match_ppi'

    print(labels)

    cypher_file = open('output/cypher_edge.cypher', 'w', encoding='utf-8')

    query = '''Match (p1:Protein{identifier:line.protein_id_1}), (p2:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PiI{biogrid:'yes', source:'BioGRID', resource:['BioGRID'], url:"https://thebiogrid.org/"+line.gene_id ,license:"The MIT License"}]->(b:Interaction{ identifier:line.id, '''

    query_update = '''Match (p1:Protein{identifier:line.protein_id_1})-[a:INTERACTS_PiI]->(m:Interaction{identifier:line.id})-[b:INTERACTS_IiP]->(p2:Protein{identifier:line.protein_id_2}) Set '''

    header = ['protein_id_1', 'protein_id_2', 'id', 'dois', 'gene_id']
    for record in results:
        head = record.data()['allfields']
        header.append(head)
        if head in ['publication_source', 'throughput', 'qualifications', 'experimental_system',
                    'experimental_system_type']:
            if head != 'publication_source':
                query += head + 's:split(line.' + head + ',"|"), ' if head[
                                                                          -1] != 's' else head + ':split(line.' + head + ',"|"), '
                query_update += 'm.' + head + 's=split(line.' + head + ',"|"), ' if head[
                                                                                        -1] != 's' else 'm.' + head + '=split(line.' + head + ',"|"), '
            else:
                query += 'pubMed_ids:split(line.' + head + ',"|"), '
                query_update += 'm.pubMed_ids=split(line.' + head + ',"|"), '
        elif head in ['author', 'interaction_id', ]:
            continue
        else:
            query += head + ':line.' + head + ', '
            query_update += 'm.' + head + '=line.' + head + ', '

    query += " biogrid:'yes', dois:split(line.dois,'|'), source:'BioGRID', resource:['BioGRID'], url:'https://thebiogrid.org/'+line.gene_id ,license:'The MIT License',  node_edge:true})-[:INTERACTS_IiP{biogrid:'yes', source:'BioGRID', resource:['BioGRID'], url:'https://thebiogrid.org/'+line.gene_id ,license:'The MIT License'}]->(p2)"
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              'mapping_and_merging_into_hetionet/bioGrid/' + file_name + '.tsv',
                                              query)
    cypher_file.write(query)
    query_update += ' a.biogrid="yes",  a.resource=split(line.resource,"|"), m.dois=line.dois, m.biogrid="yes", m.resource=split(line.resource,"|"), b.biogrid="yes", b.resource=split(line.resource,"|")'
    query_update = pharmebinetutils.get_query_import(path_of_directory,
                                                     'mapping_and_merging_into_hetionet/bioGrid/' + file_name_update + '.tsv',
                                                     query_update)
    cypher_file.write(query_update)
    for label in labels:
        file_name_other = f'interaction/association_{label}.tsv'
        query = '''Match (i:Interaction{identifier:line.interaction_id}), (c:%s{identifier:line.id}) Create (i)-[:ASSOCIATES_Ia%s{license:"The MIT License (MIT)", bioGrid:"yes", source:"BioGrid", url:'https://thebiogrid.org/'+line.gene_id ,resource:["BioGrid"]}]->(c)'''
        query = query % (label, label[0])

        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  'mapping_and_merging_into_hetionet/bioGrid/' + file_name_other,
                                                  query)
        cypher_file.write(query)
        file = open(file_name_other, 'w', encoding='utf-8')
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(['interaction_id', 'id', 'gene_id'])
        dict_label_to_file[label] = csv_writer
    cypher_file.close()

    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()

    header_merge = header.copy()
    header_merge.append('resource')
    file_merge = open(file_name_update + '.tsv', 'w', encoding='utf-8')
    csv_writer_merge = csv.DictWriter(file_merge, fieldnames=header_merge, delimiter='\t')
    csv_writer_merge.writeheader()

    return csv_writer, csv_writer_merge


def prepare_dictionary(dictionary, counter):
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
    new_dict['id'] = counter
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}

# dictionary pair to go
dict_pair_to_go_ids = {}


def run_through_results_and_add_to_dictionary(results):
    """
    run through all results and add to the dictionaries. ALso check if have rela to go!
    :param results: neo4j result
    :return:
    """
    for record in results:
        [p1_id, rela, p2_id, gene_id] = record.values()
        rela_info = dict(rela)
        if (p1_id, p2_id) not in dict_pair_to_infos and (p2_id, p1_id) not in dict_pair_to_infos:
            dict_pair_to_infos[(p1_id, p2_id)] = []
            dict_pair_to_go_ids[(p1_id, p2_id)] = set()
        if (p2_id, p1_id) in dict_pair_to_infos:
            p1_dum = p1_id
            p1_id = p2_id
            p2_id = p1_dum

        rela_info['gene_id'] = gene_id

        dict_pair_to_infos[(p1_id, p2_id)].append(rela_info)


def load_and_prepare_biogrid_human_data():
    """
    write only rela with exp into file
    Where p1.identifier in ['P27348','Q04917'] and p2.identifier in ['P27348','Q04917']
    """

    query = '''Match (p1:Protein)--(:Gene)-[:equal_to_bioGrid_gene]-(m:bioGrid_gene)-->(r:bioGrid_interaction)-->(:bioGrid_gene)-[:equal_to_bioGrid_gene]-(:Gene)--(p2:Protein) Return p1.identifier, r, p2.identifier, m.gene_id '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)

    # to check for selfloops interaction
    query = '''Match (p1:Protein)--(:Gene)-[:equal_to_bioGrid_gene]-(m:bioGrid_gene)-->(r:bioGrid_interaction)-->(m) Return p1.identifier as p_1, r, p1.identifier as p_2, m.gene_id  '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)


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


# set of interaction id , other id pair
set_pair_interaction_and_other_id = set()


def write_information_to_other_node(biogrid_id, identifier, gene_id):
    """
    check if this interaction has connection to at least one of these other labels and write the connection into the TSV file.
    :param biogrid_id: string
    :param identifier: string
    :return:
    """
    if biogrid_id in dict_interaction_id_to_connection_to_other_nodes:
        for label, set_of_ids in dict_interaction_id_to_connection_to_other_nodes[biogrid_id].items():
            for other_id in set_of_ids:
                if not (identifier, other_id) in set_pair_interaction_and_other_id:
                    dict_label_to_file[label
                    ].writerow([identifier, other_id, gene_id])
                    set_pair_interaction_and_other_id.add((identifier, other_id))


def prepare_edges_to_other_nodes(identifier, biogrid_id_s, gene_id):
    """
    Check if type is string or set and fill the different connection files.
    :param identifier: string
    :param biogrid_id_s: string
    :return:
    """

    if type(biogrid_id_s) == str:
        write_information_to_other_node(biogrid_id_s, identifier, gene_id)
    else:
        for biogrid_id in biogrid_id_s:
            write_information_to_other_node(biogrid_id, identifier, gene_id)


def prepareMappedEdges(p1, p2, list_of_dict, csv_merge):
    """
    Prepare the mapped information to one edge and writ it into a csv file
    :param p1: string
    :param p2: string
    :param list_of_dict:list of dictionaries
    :param csv_merge: csv writer
    :return:
    """
    identifier = dict_protein_pair_to_dictionary[(p1, p2)]['interaction_id']
    pubmed_ids = set(dict_protein_pair_to_dictionary[(p1, p2)]['pubmed_ids'])
    dois = set()
    if len(list_of_dict) == 1:
        final_dictionary = list_of_dict[0]
    else:
        final_dictionary = prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2)
    final_dictionary['resource'] = pharmebinetutils.resource_add_and_prepare(
        dict_protein_pair_to_dictionary[(p1, p2)]['resource'], 'BioGRID')
    gene_id = final_dictionary['gene_id'] if type(final_dictionary['gene_id']) == str else final_dictionary[
        'gene_id'].pop()
    prepare_edges_to_other_nodes(identifier, final_dictionary['interaction_id'], gene_id)
    if type(final_dictionary['publication_source']) != str:
        for pubmed_id in final_dictionary['publication_source']:
            split_pubmed = pubmed_id.split(':')
            if split_pubmed[0] == 'PUBMED':
                pubmed_ids.add(split_pubmed[1])
            elif split_pubmed[0] == 'DOI':
                dois.add(split_pubmed[1])
            else:
                print('ohno', split_pubmed)
    else:
        split_pubmed = final_dictionary['publication_source'].split(':')
        if split_pubmed[0] == 'PUBMED':
            pubmed_ids.add(split_pubmed[1])
        elif split_pubmed[0] == 'DOI':
            dois.add(split_pubmed[1])
        else:
            print('ohno', split_pubmed)
    final_dictionary['publication_source'] = pubmed_ids
    final_dictionary['dois'] = dois

    final_dictionary['protein_id_1'] = p1
    final_dictionary['protein_id_2'] = p2
    csv_merge.writerow(prepare_dictionary(final_dictionary, identifier))
    return identifier


# set of added pairs
set_of_added_pair = set()


def write_info_into_files(labels):
    """
    Check if a pair exist already in Pharmebinet or not and prepare the information for this.
    :return:
    """
    csv_writer, csv_merge = generate_file_and_cypher(labels)
    counter = maximal_id
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        if (p1, p2) in dict_protein_pair_to_dictionary:
            identifier = prepareMappedEdges(p1, p2, list_of_dict, csv_merge)
        elif (p2, p1) in dict_protein_pair_to_dictionary:
            identifier = prepareMappedEdges(p2, p1, list_of_dict, csv_merge)
        else:
            # consider only one direction
            if (p1, p2) in set_of_added_pair or (p2, p1) in set_of_added_pair:
                continue
            counter += 1
            identifier = counter
            if len(list_of_dict) == 1:
                final_dictionary = list_of_dict[0]
            else:
                # print('multi')
                final_dictionary = prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2)

            pubmed_ids = set()
            dois = set()
            if type(final_dictionary['publication_source']) == str:
                split_pubmed = final_dictionary['publication_source'].split(':')
                if split_pubmed[0] == 'PUBMED':
                    pubmed_ids.add(split_pubmed[1])
                elif split_pubmed[0] == 'DOI':
                    dois.add(split_pubmed[1])
                else:
                    print('ohno', split_pubmed)
            else:
                for pubmed in final_dictionary['publication_source']:
                    split_pubmed = pubmed.split(':')
                    if split_pubmed[0] == 'PUBMED':
                        pubmed_ids.add(split_pubmed[1])
                    elif split_pubmed[0] == 'DOI':
                        dois.add(split_pubmed[1])
                    else:
                        print('ohno', split_pubmed)

            final_dictionary['publication_source'] = pubmed_ids
            final_dictionary['dois'] = dois
            final_dictionary['protein_id_1'] = p1
            final_dictionary['protein_id_2'] = p2

            csv_writer.writerow(prepare_dictionary(final_dictionary, identifier))
            set_of_added_pair.add((p1, p2))

        if counter % 10000 == 0:
            print(counter)


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
    print('get ppi information')

    get_information_from_pharmebinet()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('get other pharmebinet information')

    dict_label_to_label = {
        'BiologicalProcess': 'bioGrid_biological_process',
        'CellularComponent': 'bioGrid_cellular_component',
        'Chemical': 'bioGrid_chemical',
        'Disease': 'bioGrid_disease'
    }
    dict_interaction_id_to_connection_to_other_nodes = {}
    for label, biogrid_label in dict_label_to_label.items():
        get_all_interaction_of_a_given_type(label, biogrid_label, dict_interaction_id_to_connection_to_other_nodes)

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('load bioGrid human data')

    load_and_prepare_biogrid_human_data()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('prepare files')

    write_info_into_files(dict_label_to_label.keys())

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
