import datetime
import os
import sys
import csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g
    g = create_connection_to_databases.database_connection_neo4j()


#dictionary pairs to info
dict_pairs_to_info = {}

def load_edges_from_database_and_add_to_dict():
    '''
    Load all Gene-Variant edges from Graph-DB and add rela-info into a dictionary
    '''
    print("query_started--------")
    # TODO: LIMIT to 10.000?
    query = "MATCH (n:Gene)-[r:HAS_GhV]-(p:Variant) RETURN n.identifier,r.resource,p.identifier"
    results = g.run(query)
    print("query_ended----------")

    count = 0
    print(datetime.datetime.utcnow())
    for gene_id, resource, variant_id, in results:
        count += 1
        if count % 50000 == 0:
            print(f"process: {count}")
            print(datetime.datetime.utcnow())
        if (gene_id, variant_id) in dict_pairs_to_info and dict_pairs_to_info[(gene_id, variant_id)] != resource:
            print('------ohje------')
            print(gene_id)
            print(resource)
            print(dict_pairs_to_info[(gene_id, variant_id)])
        dict_pairs_to_info[(gene_id, variant_id)] = resource


def get_DisGeNet_information():
    '''
    Load all DisGeNet gene-variant-edges and save to csv
    '''
    
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)
    # Create csv for existing edges

    file_name = 'gene_variant_edges.csv'
    file_path = os.path.join(path_of_directory, file_name)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file_gene_variant = open(file_path, mode)
    csv_gene_variant = csv.writer(file_gene_variant)
    csv_gene_variant.writerow(['gene_id', 'variant_id',  'resource', 'sources'])
    
    # Create csv for NON-existing edges
    file_name_not_mapped='new_gene_variant_edges.csv'
    not_mapped_path = os.path.join(path_of_directory, file_name_not_mapped)
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow(['gene_id', 'variant_id', 'resource'])

    counter_not_mapped = 0
    counter_all = 0

    query = "MATCH (n:Variant)--(:variant_DisGeNet)-[r]-(:gene_DisGeNet)--(p:Gene) RETURN n.identifier, r, p.identifier"
    results = g.run(query)

    for variant_id, rela, gene_id, in results:
        counter_all += 1
        # mapping of existing edges
        if (gene_id, variant_id) in dict_pairs_to_info:
            # resource-info aus dict auslesen, und resource um "DisGeNet" erweitern
            resource = dict_pairs_to_info[(gene_id, variant_id)]
            resource = [resource] if isinstance(resource, str) else resource
            resource.append("DisGeNet")
            # 4 columns: Id, Var_id, SourceId, resource, sourceS
            csv_gene_variant.writerow([gene_id, variant_id,  resource, rela['sourceId']])
        else:
            counter_not_mapped += 1
            writer.writerow([gene_id, variant_id, rela['sourceId']])
    file.close()
    file_gene_variant.close()
    print('number of new edges:', counter_not_mapped)
    print('number of all edges:', counter_all)


    # 2 cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    mode = 'a' if os.path.exists(cypher_path) else 'w'
    file_cypher = open(cypher_path, mode, encoding='utf-8')
    # 1. Set…
    query = f'USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}{file_name}" AS line  Match (n:Variant{{identifier:line.variant_id}})-[r:HAS_GhV]-(v:Gene{{identifier:line.gene_id}}) Set r.DisGeNet="yes",  r.resource = line.resource, r.sources = line.sources;\n'
    file_cypher.write(query)
    # 2. Create… (finde beide KNOTEN)
    query = f'USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}{file_name_not_mapped}" AS line Match (n:Variant{{identifier:line.variant_id}}), (v:Gene{{identifier:line.gene_id}}) Create (v)-[:HAS_GhV{{source:"DisGeNet", resource:line.resource, DisGeNet:"yes"}}]->(n);\n'
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

    os.chdir(path_of_directory + 'master_database_change/mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene_variant_edge/')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the genes/variants')

    load_edges_from_database_and_add_to_dict()

    print('##########################################################################')
    print('gather all information of the DisGeNet genes/variants')

    get_DisGeNet_information()

    print('##########################################################################')
    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
