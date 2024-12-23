import datetime
import os
import sys
import csv
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary ptm id to resource
dict_identifier_to_resource = {}

# dictionary ptm name to identifier
dict_protein_name_to_identifier = {}

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
    query = "MATCH (n:PTM)-[r]-(p:Protein) RETURN n.identifier, r.resource, p.identifier"
    results = g.run(query)

    for ptm_identifier, resource, protein_identifer in results:
        dict_identifier_to_resource[(ptm_identifier, protein_identifer)] = resource

def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'qPTM_edges_to_edges'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['ptm_identifier', 'protein_identifer','resource', 'aggregated_properties']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping_existing = csv.writer(file, delimiter='\t')
    csv_mapping_existing.writerow(header)

    if not os.path.exists(source):
        os.mkdir(source)

    new_file_name = 'new_edges'
    new_file_path = os.path.join(path_of_directory, new_file_name) + '.tsv'
    new_file = open(new_file_path, 'w+', encoding='utf-8')
    csv_mapping_new = csv.writer(new_file, delimiter='\t')
    csv_mapping_new.writerow(['ptm_identifier', 'protein_identifier','resource', 'aggregated_properties'])

    if not os.path.exists(source):
        os.mkdir(source)


    cypher_file_path = os.path.join(source, 'cypher_edge.cypher')
    query = (f' MATCH (n:Protein {{identifier: line.protein_identifer}}), (v:PTM {{identifier: line.ptm_identifier}}) '
             f'MATCH (n)-[r:HAS_PhPTM]-(v) SET r.qptm = "yes", r.url="https://qptm.omicsbio.info/", r.license="ONLY freely available for academic research", '
             f'r.resource = split(line.resource, "|"), r.source="qPTM", r.properties_qptm = line.aggregated_properties')
    mode = 'w' if os.path.exists(file_path) else 'w+'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    query = ('MATCH (n:Protein {identifier: line.protein_identifier}), (v:PTM {identifier: line.ptm_identifier}) '
             'CREATE (n)-[:HAS_PhPTM]->(v)')

    query = pharmebinetutils.get_query_import(path_of_directory, new_file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, 'a', encoding='utf-8')
    cypher_file.write(query)
    query = (f' MATCH (n:Protein {{identifier: line.protein_identifier}}), (v:PTM {{identifier: line.ptm_identifier}}) '
             f'MATCH (n)-[r:HAS_PhPTM]-(v) SET r.qptm = "yes", '
             f'r.resource = split(line.resource, "|"), r.properties_qptm = line.aggregated_properties')
    query = pharmebinetutils.get_query_import(path_of_directory, new_file_name + '.tsv', query)
    cypher_file.write(query)

    return csv_mapping_existing, csv_mapping_new


def load_all_qptm_ptms_and_finish_the_files(csv_mapping_existing, csv_mapping_new):
    """
    Load all variation, sort the ids into the right tsv, generate the queries, and add relationships to the rela tsv.
    """
    query = (
        "MATCH (ptm:PTM)--(n:qPTM_PTM)-[r]-(v:qPTM_Protein)--(p:Protein) "
        "RETURN id(r) as relationshipId, p.identifier as protein_identifier, ptm.identifier as ptm_identifier, "
        "r.condition as condition, r.reliability as reliability, r.pmid as pmid"
    )
    results = g.run(query)

    counter_new_edges = 0
    counter_mapped = 0
    all_edges_qptm = {}

    # Create dictionary for key: edge, value: properties
    for relationshipId, protein_identifier, ptm_identifier, condition, reliability, pmid in results:
        edge = (ptm_identifier, protein_identifier)
        if edge not in all_edges_qptm:
            all_edges_qptm[edge] = []
        all_edges_qptm[edge].append({
            "condition": condition or '',
            "reliability": reliability or '',
            "pmid": pmid or ''
        })

    for edge, properties_list in all_edges_qptm.items():
        ptm_identifier, protein_identifier = edge
        cleaned_properties = [
            {k: v for k, v in prop.items() if v}  # Remove empty values
            for prop in properties_list
        ]

        # Existing edge
        if edge in dict_identifier_to_resource:
            csv_mapping_existing.writerow([
                ptm_identifier, protein_identifier,
                pharmebinetutils.resource_add_and_prepare(
                    dict_identifier_to_resource[edge], "qPTM"
                ), cleaned_properties
            ])
            counter_mapped += 1
        else:
            # New edge
            csv_mapping_new.writerow([ptm_identifier, protein_identifier, "qPTM", cleaned_properties])
            counter_new_edges += 1
            #print(f"New edge: {ptm_identifier}, {protein_identifier}")



    print(f'Number of new ptm_protein edges: {counter_new_edges}')
    print(f'Number of extended ptm_protein edges: {counter_mapped}')




def main():
    global path_of_directory
    global source
    global home

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'ptm_protein_edge/')

    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all PTMs from database')
    load_ptms_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping_existing, csv_mapping_new = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all qPTM ptms from database')
    load_all_qptm_ptms_and_finish_the_files(csv_mapping_existing, csv_mapping_new)

    driver.close()

if __name__ == "__main__":
    main()