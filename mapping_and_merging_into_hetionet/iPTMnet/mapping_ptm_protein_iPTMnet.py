import datetime
import os
import sys
import csv
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary ptm,protein edge to resource
dict_has_ptm_identifier_to_resource = {}
dict_involves_identifier_to_resource = {}

def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

def load_ptms_from_database_and_add_to_dict():
    """
    Load all Proteins from pharmebinet and add them into a dictionary
    """
    query = "MATCH (n:PTM)-[r]-(p:Protein) RETURN type(r) as edge_type, n.identifier, r.resource, p.identifier"
    results = g.run(query)

    for edge_type, ptm_identifier, resource, protein_identifer in results:
        if edge_type == "HAS_PhPTM":
            dict_has_ptm_identifier_to_resource[(ptm_identifier, protein_identifer)] = resource
        elif edge_type == "INVOLVES":
            dict_involves_identifier_to_resource[(ptm_identifier, protein_identifer)] = resource

def generate_files(path_of_directory, edge_type):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = f'iPTMnet_edges_to_edges_{edge_type}'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['ptm_identifier', 'protein_identifier','resource', 'aggregated_properties']
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping_existing = csv.writer(file, delimiter='\t')
    csv_mapping_existing.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    new_file_name = f'new_edges_{edge_type}'
    new_file_path = os.path.join(path_of_directory, new_file_name) + '.tsv'
    new_file = open(new_file_path, 'w+', encoding='utf-8')
    csv_mapping_new = csv.writer(new_file, delimiter='\t')
    csv_mapping_new.writerow(['ptm_identifier', 'protein_identifier','resource', 'aggregated_properties', 'pmids'])

    if not os.path.exists(source):
        os.mkdir(source)



    query = ''
    if edge_type == 'iPTMnet_HAS_PTM':
        query = (f' MATCH (n:Protein {{identifier: line.protein_identifier}}), (v:PTM {{identifier: line.ptm_identifier}}) '
                 f'MATCH (n)-[r:HAS_PhPTM]->(v) SET r.iptmnet = "yes", '
                 f'r.resource = split(line.resource, "|"), r.properties_iptmnet = split(line.aggregated_properties,"|"), r.pubMed_ids =split(line.pmids,"|")')
    elif edge_type == 'iPTMnet_INVOLVES':
        query = (
            f' MATCH (n:Protein {{identifier: line.protein_identifier}}), (v:PTM {{identifier: line.ptm_identifier}}) '
            f'MATCH (v)-[r:INVOLVES]->(n) SET r.iptmnet = "yes", '
            f'r.resource = split(line.resource, "|"), r.pubMed_ids =split(line.pmids,"|")')

    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(query)

    if edge_type == 'iPTMnet_HAS_PTM':
        query = ('MATCH (n:Protein {identifier: line.protein_identifier}), (v:PTM {identifier: line.ptm_identifier}) '
                 'CREATE (n)-[:HAS_PhPTM{url:"https://research.bioinformatics.udel.edu/iptmnet/entry/"+line.protein_identifier, '
                 'license:"CC BY-NC-SA 4.0 Deed", properties_iptmnet : split(line.aggregated_properties,"|"), resource:["iPTMnet"], '
                 'source:"iPTMnet", iptmnet:"yes", pubMed_ids :split(line.pmids,"|")}]->(v)')
    elif edge_type == 'iPTMnet_INVOLVES':
        query = ('MATCH (n:Protein {identifier: line.protein_identifier}), (v:PTM {identifier: line.ptm_identifier}) '
                 'CREATE (v)-[:INVOLVES{url:"https://research.bioinformatics.udel.edu/iptmnet/entry/"+line.protein_identifier, '
                 'license:"CC BY-NC-SA 4.0 Deed", resource:["iPTMnet"], '
                 'source:"iPTMnet", iptmnet:"yes", pubMed_ids :split(line.pmids,"|")}]->(n)')
    query = pharmebinetutils.get_query_import(path_of_directory, new_file_name + '.tsv', query)
    cypher_file.write(query)

    return csv_mapping_existing, csv_mapping_new


def load_all_iptmnet_ptms_and_finish_the_files(batch_size, csv_mapping_existing, csv_mapping_new, edge_type):
    """
    Load all variation, sort the ids into the right tsv, generate the queries, and add relationships to the rela tsv.
    """
    allowed_sources = ["unip", "sign", "psp", "pro", "rlim+", "rlim", "pomb", "nrpo"]
    # Choose the appropriate dictionary for the edge type

    counter_new_edges = 0
    counter_mapped = 0
    counter_all = 0
    all_edges_iptmnet = {}

    # Choose dictionary based on edge_type
    dict_edge_identifier_to_resource = (
        dict_has_ptm_identifier_to_resource
        if edge_type == 'iPTMnet_HAS_PTM' else dict_involves_identifier_to_resource
    )

    skip = 0
    counter_new_edges = 0
    counter_mapped_edges = 0
    counter_total = 0

    while True:
        query = f"""
            MATCH (ptm:PTM)-[:equal_to_iPTMnet_ptm]-(n)-[r]-(v)-[:equal_to_iPTMnet_protein]-(p:Protein)
            WHERE type(r) = $edge_type
            WITH ptm, p, collect(properties(r)) AS edges_properties SKIP {skip} LIMIT {batch_size}
            RETURN p.identifier AS protein_identifier, ptm.identifier AS ptm_identifier, edges_properties
        """
        results = g.run(query, parameters={"edge_type": edge_type})
        batch_count = 0

        for protein_identifier, ptm_identifier, edges in results:
            batch_count += 1
            counter_total += 1
            edge = (ptm_identifier, protein_identifier)

            aggregated_properties = []
            pubmed_ids = set()
            edge_has_allowed_source = False

            # Process properties
            for edge_properties in edges:
                if 'pmid' in edge_properties:
                    pubmed_ids.add(str(edge_properties['pmid']))
                if 'source' in edge_properties and edge_properties['source'] in (allowed_sources or []):
                    edge_has_allowed_source = True
                if edge_properties:
                    aggregated_properties.append(json.dumps(edge_properties))

            # Determine whether to include the edge
            include_edge = bool(pubmed_ids) or edge_has_allowed_source or edge_type == 'iPTMnet_INVOLVES'

            if not include_edge:
                continue

            # Existing edge
            if edge in dict_edge_identifier_to_resource:
                csv_mapping_existing.writerow([
                    ptm_identifier, protein_identifier,
                    pharmebinetutils.resource_add_and_prepare(dict_edge_identifier_to_resource[edge], "iPTMnet"),
                    "|".join(aggregated_properties),
                    "|".join(pubmed_ids)
                ])
                counter_mapped_edges += 1
            else:
                # New edge
                csv_mapping_new.writerow([
                    ptm_identifier, protein_identifier, "iPTMnet"
                    "|".join(aggregated_properties), "|".join(pubmed_ids)
                ])
                counter_new_edges += 1

        if batch_count < batch_size:
            break
        skip += batch_size

    print(f'Edge type: {edge_type}')
    print(f'Number of new ptm_protein edges: {counter_new_edges}')
    print(f'Number of extended ptm_protein edges: {counter_mapped_edges}')
    print(f'Number of all ptms: {counter_total}')




def main():
    global path_of_directory
    global source
    global home, cypher_file


    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'ptm_protein_edge/')
    cypher_file_path = os.path.join(source, 'cypher_edge.cypher')
    cypher_file = open(cypher_file_path, 'w', encoding='utf-8')

    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all PTMs from database')
    load_ptms_from_database_and_add_to_dict()
    print('##########################################################################')

    print("Edge: iPTMnet_HAS_PTM")
    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping_existing, csv_mapping_new = generate_files(path_of_directory, "iPTMnet_HAS_PTM")

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all iPTMnet ptms from database')
    load_all_iptmnet_ptms_and_finish_the_files(10000,csv_mapping_existing, csv_mapping_new, 'iPTMnet_HAS_PTM')

    print('##########################################################################')
    print("Edge: iPTMnet_INVOLVES")
    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping_existing_involve, csv_mapping_new_involve = generate_files(path_of_directory, "iPTMnet_INVOLVES")

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all iPTMnet ptms from database')
    load_all_iptmnet_ptms_and_finish_the_files(10000,csv_mapping_existing_involve, csv_mapping_new_involve, 'iPTMnet_INVOLVES')

    cypher_file.close()
    driver.close()

if __name__ == "__main__":
    main()