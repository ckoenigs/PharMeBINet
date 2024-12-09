import datetime
import sys, csv


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


# dictionary with all gene ids to there name
dict_pharmebinet_gene_ids_to_resource = {}

'''
load all ncbi identifier from the gene ides into a dictionary (or list)
'''


def get_all_ncbi_ids_from_pharmebinet_genes():
    query = '''Match (g:Gene) Return g.identifier, g.resource;'''
    results = g.run(query)
    for identifier, resource, in results:

        dict_pharmebinet_gene_ids_to_resource[identifier] = resource

    print('number of genes in pharmebinet:' + str(len(dict_pharmebinet_gene_ids_to_resource)))



'''
load ncbi tsv file in and write only the important lines into a new tsv file for integration into Neo4j
'''


def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():
    # file for integration into pharmebinet
    file = open('output/genes.tsv', 'w')
    header = ['id1', 'id2', 'resource']
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(header)

    cypher_file = open('output/cypher.cypher', 'w')
    query = '''Match (n:Gene_hetionet {identifier:line.id1}), (g:Gene{identifier:line.id2 }) Set g.hetionet="yes", g.resource=split(line.resource,"|") Create (n)<-[:equal_to_hetionet_gene]-(g) '''



    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hetionet/output/genes.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.close()

    query = '''MATCH (n:Gene_hetionet) RETURN n.identifier;'''
    results = g.run(query)
    counter_not_same_name = 0
    counter_all = 0
    counter_all_in_pharmebinet = 0
    counter_mapped_and_similar_names=0
    for record in results:
        [gene_id] = record.values()
        counter_all += 1


        if gene_id in dict_pharmebinet_gene_ids_to_resource:
            counter_all_in_pharmebinet += 1
            writer.writerow([gene_id,gene_id, pharmebinetutils.resource_add_and_prepare(dict_pharmebinet_gene_ids_to_resource[gene_id],
                                                                           'Hetionet')])

        else:
            print('not in pharmebinet')
            print(gene_id)
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
    print('gather all information of the pharmebinet genes')

    get_all_ncbi_ids_from_pharmebinet_genes()

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
