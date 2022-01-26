import datetime
from distutils.command.sdist import sdist
import os
import sys
import csv
import json
from collections import defaultdict

import create_connection_to_databases


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    global g
    g = create_connection_to_databases.database_connection_neo4j()


#dictionary pairs to info
dict_pairs_to_info = defaultdict()


def load_edges_from_database_and_add_to_dict():
    '''
    Load all Gene-Disease edges from Graph-DB and add rela-info into a dictionary
    '''
    print("query_started----------")
    query = f"MATCH (n:Gene)-[r:ASSOCIATES_DaG]-(p:Disease) RETURN n.identifier,r,p.identifier "
    results = g.run(query)
    print("query_ended----------")

    count = 0
    print(datetime.datetime.utcnow())
    for gene_id, rela, disease_id, in results:
        count += 1
        if count % 5000 == 0:
            print(f"process: {count}")
            print(datetime.datetime.utcnow())
        if (gene_id, disease_id) in dict_pairs_to_info and dict_pairs_to_info[(gene_id, disease_id)] != rela:
            print('------ohje------')
            print(gene_id)
            print(rela)
            print(dict_pairs_to_info[(gene_id, disease_id)])
        dict_pairs_to_info[(gene_id, disease_id)] = rela


def check_for_double_entries(results):
    double_check_dict = defaultdict()

    for disease_id, rela, gene_id, in results:
        if (gene_id, disease_id) in double_check_dict and double_check_dict[(gene_id, disease_id)] != rela:
            rela_old = double_check_dict[(gene_id, disease_id)]

            # Check1: combine pmid's if unequal
            difference_pmid = list(set(rela['pmid']).difference(set(rela_old['pmid']))) if rela_old['pmid'] else []
            if difference_pmid:
                # check if list is already nested structure or not. If not, wrap it in a list.
                rela_old['pmid'] = rela_old['pmid'] if isinstance(rela_old['pmid'], list) else [rela_old['pmid']]
                double_check_dict[(gene_id, disease_id)]['pmid'] = rela_old['pmid'].append(difference_pmid)  # append new list of pmid

            # Check2: combine NofSnps in a list
            # difference_snps = list(set(rela['NofSnps']).difference(set(rela_old['NofSnps']))) if rela_old['NofSnps'] else []
            rela_old['NofSnps'] = [rela_old['NofSnps']] if isinstance(rela_old['NofSnps'], str) else rela_old['NofSnps']
            if rela_old['NofSnps']:
                rela_old['NofSnps'].append(rela['NofSnps'])

            #Check3: combine "source, score, YearFinal, Yearinitial" in JSON-string and append to list "sources"
            # e.g. sources = ["{source:'' score:'', YearFinal:, YearInitial:}"]
            rela_new_comb = {"source": rela['source'], "score": rela["score"], "YearInitial": rela["YearInitial"], "YearFinal": rela["YearFinal"]}
            if 'sources' in double_check_dict[(gene_id, disease_id)]: #if entry already exists
                double_check_dict[(gene_id, disease_id)]['sources'].append(json.dumps(rela_new_comb))
            else:
                rela_old_comb = {"source": rela_old['source'], "score": rela_old["score"], "YearInitial": rela_old["YearInitial"], "YearFinal": rela_old["YearFinal"]}
                double_check_dict[(gene_id, disease_id)]['sources'] = [json.dumps(rela_old_comb), json.dumps(rela_new_comb)]

        else:
            comb = {"source": rela['source'], "score": rela["score"], "YearInitial": rela["YearInitial"], "YearFinal": rela["YearFinal"]}
            double_check_dict[(gene_id, disease_id)] = rela
            double_check_dict[(gene_id, disease_id)]['sources'] = [json.dumps(comb)];
    return double_check_dict

def get_DisGeNet_information(type = 'Disease', cyphermode = 'w'):
    '''
    Load all DisGeNet gene-disease and gene-symptom-edges (respectively) and save to csv
    @param type:        the node-type with which to perform the mapping (either 'Disease' or 'Symptom')
    @param limit:       the limit of cypher queries returned.
    @param cyphermode:  either overwrite or add a line to the cypher-query.
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    # Create csv for existing edges
    edge_type = 'ASSOCIATES_DaG' if type == 'Disease' else 'ASSOCIATES_SaG'
    other_id = 'disease_id' if type == 'Disease' else 'symptom_id'
    file_name = 'gene_disease_edges.csv' if type == 'Disease' else 'gene_symptom_edges.csv'
    
    file_path = os.path.join(path_of_directory, file_name)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file_gene_other = open(file_path, mode)
    csv_gene_other = csv.writer(file_gene_other)
    csv_gene_other.writerow(['gene_id', other_id, 'resource', 'sources', 'DSI', 'DPI', 'EI', 'pmid', 'NofSnps'])

    # Neo4j query
    # edge = 'r' if type == 'Disease' else 's'
    query = f"MATCH (n:{type})--(:disease_DisGeNet)-[r]-(:gene_DisGeNet)--(p:Gene) WHERE r.NofPmids<>'0' RETURN n.identifier, r, p.identifier "
    results = g.run(query)

    counter_not_mapped = 0
    counter_all = 0

    # Match Sympton to Gene
    # if type == 'Symptom':
    #     for symptom_id, rela, gene_id, in results:
    #         counter_all += 1
    #         counter_not_mapped += 1
    #         csv_gene_other.writerow([gene_id, symptom_id, rela['mapped_with']])
    
    #     # Create…
    #     query = f'USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:/Users/MT/UNI/Vorlesungen_SS_21/ISY-Projects/KnowledgeEngineering/data/DisGeNet/mapping/gene_disease_edge/{file_name}" AS line Match (n:{type}{{identifier:line.symptom_id}}), (v:Gene{{identifier:line.gene_id}}) Create (n)-[:{edge_type}{{source:"DisGeNet", DisGeNet:"yes", mapped_with:line.mapping_method}}]->(v); \n'
    #     file_cypher.write(query)

    # # Match Disease to Gene (type == 'Disease')
    # else:
    # Create csv for NON-existing edges
    file2_name = 'new_gene_disease_edges.csv' if type == 'Disease' else 'new_gene_symptom_edges.csv'
    not_mapped_path = os.path.join(path_of_directory, file2_name)
    mode = 'w' if os.path.exists(not_mapped_path) else 'w+'
    file = open(not_mapped_path, mode, encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow(['gene_id', other_id, 'sources', 'DSI', 'DPI', 'EI', 'pmid', 'NofSnps'])

    #1. Dict erstellen, doppelte Einträge kombinieren
    # mehrfach vorkommende Vebrindungen suchen und als dict ausgeben
    combined_dict = check_for_double_entries(results)

    # Weitere Schleife mit if-Bedingungen zum kombinieren der Kanten
    for (gene_id, disease_id), combined_info in combined_dict.items():
        counter_all += 1

        # combined entries computed from results beforehand
        sources = '|'.join(combined_info['sources']) if isinstance(combined_info['sources'], list) else combined_info['sources']
        dsi = combined_info['DSI']
        dpi = combined_info['DPI']
        ei = combined_info['EI']
        pmid = '|'.join(combined_info['pmid']) if isinstance(combined_info['pmid'], list) else combined_info['pmid']
        nofsnps = '|'.join(combined_info['NofSnps']) if isinstance(combined_info['NofSnps'], list) else combined_info['NofSnps']

        # mapping of existing edges
        if (gene_id, disease_id) in dict_pairs_to_info:
            # Verschiedene infos aus beiden Kanten kombinieren
            resource = dict_pairs_to_info[(gene_id, disease_id)]['resource']
            resource = [resource] if isinstance(resource, str) else resource
            resource.append("DisGeNet")
            resource = '|'.join(resource)
            # restliche Kanten-Informationen direkt übertragen
            csv_gene_other.writerow([gene_id, disease_id, resource, sources, dsi, dpi, ei, pmid, nofsnps])
        else:
            counter_not_mapped += 1
            writer.writerow([gene_id, disease_id, sources, dsi, dpi, ei, pmid, nofsnps])


    # create/open cypher-query file
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    file_cypher = open(cypher_path, cyphermode, encoding='utf-8')


    file.close()
    file_gene_other.close()

    # 1. Set…
    query = f'USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}{file_name}" AS line Match (n:{type}{{identifier:line.{other_id}}}), (v:Gene{{identifier:line.gene_id}}) Merge (n)-[r:{edge_type}]->(v) On Match Set r.DisGeNet = "yes", r.sources = split(line.sources, "|"), r.resource = split(line.resource, "|"), r.DSI = line.DSI, r.DPI = line.DPI, r.EI = line.EI, r.pmid = split(line.pmid, "|"), r.NofSnps = split(line.NofSnps, "|"); \n'
    file_cypher.write(query)
    # 2. Create… (finde beide KNOTEN)
    query = f'USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}{file2_name}" AS line Match (n:{type}{{identifier:line.{other_id}}}), (v:Gene{{identifier:line.gene_id}}) Create (n)-[:{edge_type}{{source:"DisGeNet", sources:split(line.sources,"|"), DisGeNet:"yes", DSI:line.DSI, DPI:line.DPI, EI:line.EI, pmid:split(line.pmid,"|"), NofSnps:split(line.NofSnps, "|")}}]->(v); \n'
    file_cypher.write(query)
    file_cypher.close()

    print('number of new edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

    




######### MAIN #########
def main():
    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path disgenet protein')

    os.chdir(path_of_directory + 'master_database_change/mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'gene_disease_edge/')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the genes/diseases')

    load_edges_from_database_and_add_to_dict()

    print('##########################################################################')
    print('gather all information of the DisGeNet genes/diseases')

    get_DisGeNet_information('Disease', 'a')

    print('##########################################################################')
    print('gather all information of the DisGeNet genes/symptoms')
    get_DisGeNet_information( 'Symptom', 'a')

    print('##########################################################################')
    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
