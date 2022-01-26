import datetime
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


def check_for_double_entries(results):
    
    double_check_dict = defaultdict()

    for disease_id, rela, variant_id, in results:
        if (variant_id, disease_id) in double_check_dict and double_check_dict[(variant_id, disease_id)] != rela:
            rela_old = double_check_dict[(variant_id, disease_id)]

            # Check1: combine pmid's if unequal
            difference_pmid = list(set(rela['pmid']).difference(set(rela_old['pmid']))) if rela_old['pmid'] else []
            if difference_pmid:
                # check if list is already nested structure or not. If not, wrap it in a list.
                rela_old['pmid'] = rela_old['pmid'] if isinstance(rela_old['pmid'], list) else [rela_old['pmid']]
                double_check_dict[(variant_id, disease_id)]['pmid'] = rela_old['pmid'].append(difference_pmid)  # append new list of pmid

            #Check2: combine "source, score, YearFinal, Yearinitial" in JSON-string and append to list "sources"
            # e.g. sources = ["{source:'' score:'', YearFinal:, YearInitial:}"]
            rela_new_comb = {"source": rela['source'], "score": rela["score"], "YearInitial": rela["YearInitial"], "YearFinal": rela["YearFinal"]}
            if 'sources' in double_check_dict[(variant_id, disease_id)]: #if entry already exists
                double_check_dict[(variant_id, disease_id)]['sources'].append(json.dumps(rela_new_comb))
            else:
                rela_old_comb = {"source": rela_old['source'], "score": rela_old["score"], "YearInitial": rela_old["YearInitial"], "YearFinal": rela_old["YearFinal"]}
                double_check_dict[(variant_id, disease_id)]['sources'] = [json.dumps(rela_old_comb), json.dumps(rela_new_comb)]

        else:
            comb = {"source": rela['source'], "score": rela["score"], "YearInitial": rela["YearInitial"], "YearFinal": rela["YearFinal"]}
            double_check_dict[(variant_id, disease_id)] = rela
            double_check_dict[(variant_id, disease_id)]['sources'] = [json.dumps(comb)];
    return double_check_dict

def get_DisGeNet_information( type = 'Disease', cyphermode='w'):
    '''
    Load all DisGeNet variant-disease-edges and save to csv
    @param cyphermode:  either overwrite or add a line to the cypher-query.
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    # Create csv for NON-existing edges
    edge_type = 'ASSOCIATES_DaV' if type == 'Disease' else 'ASSOCIATES_SaV'
    other_id = 'disease_id' if type == 'Disease' else 'symptom_id'
    file_name = 'new_variant_disease_edges.csv' if type == 'Disease' else 'new_variant_symptom_edges.csv'

    file_path = os.path.join(path_of_directory, file_name)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file_variant_disease = open(file_path, mode)
    csv_variant_disease = csv.writer(file_variant_disease)
    csv_variant_disease.writerow(['variant_id', other_id, 'sources', 'DSI', 'DPI', 'EI', 'pmid'])

    counter_all = 0

    query = f"MATCH (n:{type})--(:disease_DisGeNet)-[r]-(:variant_DisGeNet)--(p:Variant) WHERE r.NofPmids<>'0' RETURN n.identifier, r, p.identifier"
    results = g.run(query)

    #1. Dict erstellen, doppelte Einträge kombinieren
    # mehrfach vorkommende Vebrindungen suchen und als dict ausgeben
    combined_dict = check_for_double_entries(results)

    # Weitere Schleife mit if-Bedingungen zum kombinieren der Kanten
    for (variant_id, disease_id), combined_info in combined_dict.items():
        counter_all += 1

        # combined entries computed from results beforehand
        sources = '|'.join(combined_info['sources']) if isinstance(combined_info['sources'], list) else combined_info['sources']
        dsi = combined_info['DSI']
        dpi = combined_info['DPI']
        ei = combined_info['EI']
        pmid = '|'.join(combined_info['pmid']) if isinstance(combined_info['pmid'], list) else combined_info['pmid']

        csv_variant_disease.writerow([variant_id, disease_id, sources, dsi, dpi, ei, pmid])
    
    file_variant_disease.close()
    print('number of all edges:', counter_all)

    # 2 cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    file_cypher = open(cypher_path, cyphermode, encoding='utf-8')
    # Create… (finde beide KNOTEN)
    query = f'USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:{path_of_directory}{file_name}" AS line Match (n:{type}{{identifier:line.{other_id}}}), (v:Variant{{identifier:line.variant_id}}) Create (n)-[:{edge_type}{{source:"DisGeNet", sources:split(line.sources,"|"), DisGeNet:"yes", DSI:line.DSI, DPI:line.DPI, EI:line.EI, pmid:split(line.pmid,"|")}}]->(v);\n'
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
        sys.exit('need a path disgenet rela')

    os.chdir(path_of_directory + 'master_database_change/mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'variant_disease_edge/')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')
    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the DisGeNet variant/diseases')
    get_DisGeNet_information( type = 'Disease', cyphermode='a')
    
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the DisGeNet variant/symptom')
    get_DisGeNet_information( type = 'Symptom', cyphermode='a')

    print('##########################################################################')

    print(datetime.datetime.utcnow())

if __name__ == "__main__":
    # execute only if run as a script
    main()
