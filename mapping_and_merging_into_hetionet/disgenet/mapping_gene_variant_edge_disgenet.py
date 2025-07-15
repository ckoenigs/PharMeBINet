import datetime
import os
import sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary pairs to info
dict_pairs_to_info = {}


def load_edges_from_database_and_add_to_dict():
    '''
    Load all Gene-Variant edges from Graph-DB and add rela-info into a dictionary
    '''
    print("query_started--------")
    query = "MATCH (n:Gene)-[r:HAS_GhGV]-(p:Variant) RETURN n.identifier,r.resource,p.identifier"
    results = g.run(query)
    print("query_ended----------")

    count = 0
    print(datetime.datetime.now())
    for record in results:
        [gene_id, resource, variant_id] = record.values()
        count += 1
        if count % 50000 == 0:
            print(f"process: {count}")
            print(datetime.datetime.now())
        if (gene_id, variant_id) in dict_pairs_to_info and dict_pairs_to_info[(gene_id, variant_id)] != resource:
            print('------ohje------')
            print(gene_id)
            print(resource)
            print(dict_pairs_to_info[(gene_id, variant_id)])
        dict_pairs_to_info[(gene_id, variant_id)] = resource


def get_DisGeNet_information():
    '''
    Load all DisGeNet gene-variant-edges and save to tsv
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)
    # Create tsv for existing edges

    file_name = 'gene_variant_edges.tsv'
    file_path = os.path.join(path_of_directory, file_name)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file_gene_variant = open(file_path, mode)
    csv_gene_variant = csv.writer(file_gene_variant, delimiter='\t')
    csv_gene_variant.writerow(['gene_id', 'variant_id', 'resource', 'sources'])

    # Create tsv for NON-existing edges
    file_name_not_mapped = 'new_gene_variant_edges.tsv'
    not_mapped_path = os.path.join(path_of_directory, file_name_not_mapped)
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['gene_id', 'variant_id', 'sources', 'snp_id'])

    counter_not_mapped = 0
    counter_all = 0

    query = "MATCH (n:Variant)--(a:variant_DisGeNet)-[r]-(:gene_DisGeNet)--(p:Gene) Where 'DBSNP' in r.sourceId RETURN n.identifier, r, p.identifier, a.snpId"
    results = g.run(query)

    for record in results:
        [variant_id, rela, gene_id, snp_id] = record.values()
        counter_all += 1
        # mapping of existing edges
        if (gene_id, variant_id) in dict_pairs_to_info:
            # 4 columns: Id, Var_id, SourceId, resource, sourceS
            csv_gene_variant.writerow(
                [gene_id, variant_id,
                 pharmebinetutils.resource_add_and_prepare(dict_pairs_to_info[(gene_id, variant_id)], "DisGeNet"),
                 '|'.join(rela['sourceId'])])
        else:
            counter_not_mapped += 1
            writer.writerow([gene_id, variant_id, '|'.join(rela['sourceId']), snp_id])
    file.close()
    file_gene_variant.close()
    print('number of new edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    # 2 cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w'
    file_cypher = open(cypher_path, mode, encoding='utf-8')
    # 1. Set…
    query = f' Match (n:Variant{{identifier:line.variant_id}})-[r:HAS_GhGV]-(v:Gene{{identifier:line.gene_id}}) Set r.disgenet="yes",  r.resource = split(line.resource,"|"), r.sources = split(line.sources,"|") '
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    file_cypher.write(query)

    # 2. Create… (finde beide KNOTEN)
    # url:"https://www.disgenet.org/browser/2/1/0/"+line.variant_id
    query = f' Match (n:Variant{{identifier:line.variant_id}}), (v:Gene{{identifier:line.gene_id}}) Create (v)-[:HAS_GhGV{{source:"DisGeNet", resource:["DisGeNet"] , license:"Attribution-NonCommercial-ShareAlike 4.0 International License", sources:split(line.sources,"|"), disgenet:"yes", url:"https://www.disgenet.org/browser/0/0/2/0/0/25/snpid__"+line.snp_id+"-source__CURATED/_b./"}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_not_mapped,
                                              query)
    file_cypher.write(query)
    file_cypher.close()


######### MAIN #########
def main():
    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet gene-variant')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene_variant_edge/')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather all information of the genes/variants')

    load_edges_from_database_and_add_to_dict()

    print('##########################################################################')
    print('gather all information of the DisGeNet genes/variants')

    get_DisGeNet_information()

    driver.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
