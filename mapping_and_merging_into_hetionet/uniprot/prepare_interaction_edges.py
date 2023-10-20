import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary pairs to info
dict_pairs_to_info = {}


def combine_info(tuple_ids_and_iso, rela):
    """
    Combine the information
    :param tuple_ids_and_iso:
    :param rela:
    :return:
    """
    for prop in ['number_of_experiments', 'interaction_ids']:  # ,  'iso_of_protein_to', 'iso_of_protein_from'
        if prop not in ['interaction_ids', 'number_of_experiments']:
            dict_pairs_to_info[tuple_ids_and_iso][prop].add(rela[prop])
        else:
            dict_pairs_to_info[tuple_ids_and_iso][prop] = \
                dict_pairs_to_info[tuple_ids_and_iso][prop].union(rela[prop])


def get_pairs_information():
    """
    Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
    :return:
    """
    # only the interaction in the same organism {identifier:'Q13627'}
    query = """Match (n:Protein_Uniprot)-[r]->(p:Protein_Uniprot) Where r.organismsDiffer='false' Return Distinct n.identifier, r, p.identifier """
    results = g.run(query)

    for record in results:
        [protein_id1, rela, protein_id2] = record.values()
        iso_of_protein_from = rela['iso_of_protein_from'] if 'iso_of_protein_from' in rela else ''
        iso_of_protein_to = rela['iso_of_protein_to'] if 'iso_of_protein_to' in rela else ''

        if (protein_id1, protein_id2, iso_of_protein_from, iso_of_protein_to) in dict_pairs_to_info:
            # print(protein_id1,protein_id2)
            combine_info((protein_id1, protein_id2, iso_of_protein_from, iso_of_protein_to), rela)

        elif (protein_id2, protein_id1, iso_of_protein_to, iso_of_protein_from) in dict_pairs_to_info:
            combine_info((protein_id2, protein_id1, iso_of_protein_to, iso_of_protein_from), rela)

        else:
            dict_rela = {}
            for prop in ['number_of_experiments', 'interaction_ids']:  #:,'iso_of_protein_to','iso_of_protein_from'
                if prop not in ['interaction_ids', 'number_of_experiments']:
                    dict_rela[prop] = {rela[prop]}
                else:
                    dict_rela[prop] = set(rela[prop])
            dict_pairs_to_info[(protein_id1, protein_id2, iso_of_protein_from, iso_of_protein_to)] = dict_rela


def write_info_into_tsv_file():
    # generate a file with all uniprots to
    file_name = 'output/protein_interaction.tsv'
    file_gene_disease = open(file_name, 'w')
    csv_gene_disease = csv.writer(file_gene_disease, delimiter='\t')
    csv_gene_disease.writerow(
        ['protein_id1', 'protein_id2', 'interaction_id', 'interaction_ids', 'iso_of_protein_to', 'iso_of_protein_from',
         'number_of_experiments'])

    # query gene-disease association

    file_cypher = open('output/cypher_edge.cypher', 'a')
    query = ''' Match (p1:Protein{identifier:line.protein_id1}), (p2:Protein{identifier:line.protein_id2}) Create (p1)-[:INTERACTS_PiI{source:"UniProt", license:"CC BY 4.0", url:"https://www.uniprot.org/uniprot/"+line.protein_id1, resource:["UniProt"], uniprot:'yes'}]->(b:Interaction{source:"UniProt", identifier:line.interaction_id,  license:"CC BY 4.0", resource:["UniProt"], uniprot:'yes', iso_of_protein_from:line.iso_of_protein_from, url:"https://www.uniprot.org/uniprot/"+line.protein_id1 , iso_of_protein_to:line.iso_of_protein_to, interaction_ids:split(line.interaction_ids, "|"), number_of_experiments:split(line.number_of_experiments, "|"), node_edge:true})-[:INTERACTS_IiP{source:"UniProt", license:"CC BY 4.0", resource:["UniProt"], url:"https://www.uniprot.org/uniprot/"+line.protein_id1, uniprot:'yes'}]->(p2) '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/uniprot/{file_name}',
                                              query)
    file_cypher.write(query)
    file_cypher.write(pharmebinetutils.prepare_index_query('Interaction', 'identifier'))

    counter = 0

    for (protein_id1, protein_id2, iso_of_protein_from, iso_of_protein_to), rela in dict_pairs_to_info.items():
        number_of_experiments = '|'.join(rela['number_of_experiments'])
        # if len(experimental)>1:
        #     print(protein_id1,protein_id2)
        #     print('different experiment')
        #     print(experimental)

        interaction_ids = '|'.join(rela['interaction_ids'])
        counter += 1
        csv_gene_disease.writerow(
            [protein_id1, protein_id2, counter, interaction_ids, iso_of_protein_to, iso_of_protein_from,
             number_of_experiments])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gather all information of the proteins')

    get_pairs_information()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate and write info in tsv file')

    write_info_into_tsv_file()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
