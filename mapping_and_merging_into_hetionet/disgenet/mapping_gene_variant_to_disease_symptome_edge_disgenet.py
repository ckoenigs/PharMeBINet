import datetime
import os
import sys
import csv
import json
from collections import defaultdict

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


def load_edges_from_database_and_add_to_dict(label, other_label):
    '''
    Load all Gene-Disease edges from Graph-DB and add rela-info into a dictionary
    '''
    global dict_pairs_to_info
    print("query_started----------")
    query = f"MATCH (n:{other_label})-[r:ASSOCIATES_{label[0]}a{other_label[0]}]-(p:{label}) RETURN n.identifier,r,p.identifier "
    results = g.run(query)
    print("query_ended----------")

    dict_pairs_to_info = {}
    count = 0
    print(datetime.datetime.now())
    for record in results:
        [gene_id, rela, disease_id] = record.values()
        rela = dict(rela)
        count += 1
        if count % 5000 == 0:
            print(f"process: {count}")
            print(datetime.datetime.now())
        if (gene_id, disease_id) in dict_pairs_to_info and dict_pairs_to_info[(gene_id, disease_id)] != rela:
            print('------ohje------')
            print(gene_id)
            print(rela)
            print(dict_pairs_to_info[(gene_id, disease_id)])
        dict_pairs_to_info[(gene_id, disease_id)] = rela


def prepare_sources_information(rela):
    """
    prepare sources information as dictionary and add if exists add EI
    :param rela: dictionary
    :return: dictionary
    """
    comb = {"source": rela['source'], "score": rela["score"], "years": rela["years"]}
    if "EI" in rela:
        comb["EI"] = rela["EI"]
    return comb


def combine_possible_properties(rela_old, rela, name):
    """
    Combine information.
    :param rela_old:
    :param rela:
    :param name:
    :return:
    """
    if name in rela_old or name in rela:
        association_type_old = set(rela_old[name]) if name in rela_old else set()
        association_type_new = rela[name] if name in rela else []
        rela_old[name] = association_type_old.union(association_type_new)


def check_for_double_entries(results):
    """
    go through the results add information to dictionary or combine them.
    :param results:
    :return:
    """
    double_check_dict = defaultdict()

    for record in results:
        [disease_id, rela, gene_id, snp_id] = record.values()
        rela = dict(rela)
        if (gene_id, disease_id) in double_check_dict and double_check_dict[(gene_id, disease_id)] != rela:
            rela_old = double_check_dict[(gene_id, disease_id)]
            # if disease_id=='MONDO:0013000' and gene_id=='210':
            #     print('hier')
            new_pmid = rela['pmid']
            old_pmid = rela_old['pmid']
            double_check_dict[(gene_id, disease_id)]['pmid'] = list(set(new_pmid).union(old_pmid))
            # if len(old_pmid)< len(double_check_dict[(gene_id, disease_id)]['pmid']):
            #     print(gene_id, disease_id, 'double')

            # Check2: combine NofSnps in a list
            # difference_snps = list(set(rela['NofSnps']).difference(set(rela_old['NofSnps']))) if rela_old['NofSnps'] else []
            if 'NofSnpsString' in rela_old:
                rela_old['NofSnpsString'] = set([rela_old['NofSnpsString']]) if isinstance(rela_old['NofSnpsString'],
                                                                                           str) else rela_old[
                    'NofSnpsString']
                if rela_old['NofSnpsString']:
                    rela_old['NofSnpsString'].add(rela['NofSnpsString'])

            combine_possible_properties(rela_old, rela, 'associationType')
            combine_possible_properties(rela_old, rela, 'sentence')

            # Check3: combine "source, score, YearFinal, Yearinitial" in JSON-string and append to list "sources"
            # e.g. sources = ["{source:'' score:'', YearFinal:, YearInitial:}"]
            rela_new_comb = prepare_sources_information(rela)

            double_check_dict[(gene_id, disease_id)]['score'] += float(rela["score"])
            double_check_dict[(gene_id, disease_id)]['counter'] += 1
            double_check_dict[(gene_id, disease_id)]['EI'] += float(rela["EI"]) if "EI" in rela else 0.0
            if 'sources' in double_check_dict[(gene_id, disease_id)]:  # if entry already exists
                double_check_dict[(gene_id, disease_id)]['sources'].add(json.dumps(rela_new_comb))
            else:
                print('why :O')
                # rela_old_comb = {"source": rela_old['source'], "score": rela_old["score"],
                #                  "YearInitial": rela_old["YearInitial"], "YearFinal": rela_old["YearFinal"]}
                # double_check_dict[(gene_id, disease_id)]['sources'] = [json.dumps(rela_old_comb),
                #                                                        json.dumps(rela_new_comb)]

        else:
            double_check_dict[(gene_id, disease_id)] = dict(rela)
            double_check_dict[(gene_id, disease_id)]['sources'] = set([json.dumps(prepare_sources_information(rela))])
            double_check_dict[(gene_id, disease_id)]['score'] = float(rela["score"])

            double_check_dict[(gene_id, disease_id)]['EI'] = float(rela["EI"]) if "EI" in rela else 0.0
            double_check_dict[(gene_id, disease_id)]['counter'] = 1
            double_check_dict[(gene_id, disease_id)]['snp_id'] = snp_id if not snp_id is None else ''

    return double_check_dict


def prepare_info_of_rela_property_to_string(dictionary, name):
    """
    prepare information
    :param dictionary:
    :param name:
    :return:
    """
    if name in dictionary:
        return '|'.join(dictionary[name])
    return ''


def get_DisGeNet_information(type='Disease', cyphermode='w', other_label='Gene'):
    '''
    Load all DisGeNet gene-disease and gene-symptom-edges (respectively) and save to tsv
    @param type:        the node-type with which to perform the mapping (either 'Disease' or 'Symptom')
    @param limit:       the limit of cypher queries returned.
    @param cyphermode:  either overwrite or add a line to the cypher-query.
    '''

    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    # Create tsv for existing edges and not existing edges
    edge_type = f'ASSOCIATES_Da{other_label[0]}' if type == 'Disease' else f'ASSOCIATES_Sa{other_label[0]}'
    other_id = 'disease_id' if type == 'Disease' else 'symptom_id'
    file_name = f'{other_label.lower()}_{type.lower()}_edges.tsv'

    file_path = os.path.join(path_of_directory, file_name)
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file_gene_other = open(file_path, mode)
    csv_gene_other = csv.writer(file_gene_other, delimiter='\t')
    csv_gene_other.writerow(
        [f'{other_label.lower()}_id', other_id, 'resource', 'sources', 'EI', 'pmid', 'NofSnps', 'score',
         'associationType', 'sentence'])

    # Neo4j query
    # edge = 'r' if type == 'Disease' else 's'
    query = f"MATCH (n:{type})--(:disease_DisGeNet)-[r]-(a:{other_label.lower()}_DisGeNet)--(p:{other_label}) WHERE r.NofPmids<>'0' RETURN n.identifier, r, p.identifier , a.snpId "
    results = g.run(query)

    counter_not_mapped = 0
    counter_all = 0

    # 1. Dict erstellen, doppelte Einträge kombinieren
    # mehrfach vorkommende Vebrindungen suchen und als dict ausgeben
    combined_dict = check_for_double_entries(results)

    # Weitere Schleife mit if-Bedingungen zum kombinieren der Kanten
    for (gene_id, disease_id), combined_info in combined_dict.items():
        # print(gene_id,disease_id)
        counter_all += 1

        # combined entries computed from results beforehand
        sources = '|'.join(combined_info['sources'])

        count_combination_edge = combined_info['counter']
        ei = round(combined_info['EI'] / count_combination_edge, 4)
        score = round(combined_info['score'] / count_combination_edge, 4)
        pmid = '|'.join(combined_info['pmid'])

        if 'NofSnpsString' in combined_info:
            if isinstance(combined_info['NofSnpsString'], set):
                nofsnps = list(combined_info['NofSnpsString'])
                try:
                    while True:
                        nofsnps.remove('0')
                except ValueError:
                    pass
                # if len(nofsnps)>1:
                #     print('more than 1 no of snps',nofsnps)
                nofsnps = '|'.join(nofsnps)
            else:
                nofsnps = combined_info['NofSnpsString'] if combined_info['NofSnpsString'] != '0' else ''
        else:
            nofsnps = ''

        # mapping of existing edges
        if (gene_id, disease_id) in dict_pairs_to_info:
            # Verschiedene infos aus beiden Kanten kombinieren
            resource = pharmebinetutils.resource_add_and_prepare(dict_pairs_to_info[(gene_id, disease_id)]['resource'],
                                                                 "DisGeNet")

            pubmed_id_existing = set(dict_pairs_to_info[(gene_id, disease_id)]['pubMed_ids']) if 'pubMed_ids' in \
                                                                                                 dict_pairs_to_info[(
                                                                                                     gene_id,
                                                                                                     disease_id)] else set()
            pubmed_id_existing = pubmed_id_existing.union(combined_info['pmid'])
            # restliche Kanten-Informationen direkt übertragen
            csv_gene_other.writerow(
                [gene_id, disease_id, resource, sources, ei, '|'.join(pubmed_id_existing), nofsnps, score,
                 prepare_info_of_rela_property_to_string(combined_info, 'associationType'),
                 prepare_info_of_rela_property_to_string(combined_info, 'sentence')])
        else:
            counter_not_mapped += 1
            csv_gene_other.writerow([gene_id, disease_id, 'DisGeNet', sources, ei, pmid, nofsnps, score,
                                     prepare_info_of_rela_property_to_string(combined_info, 'associationType'),
                                     prepare_info_of_rela_property_to_string(combined_info, 'sentence')])

    # create/open cypher-query file
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    file_cypher = open(cypher_path, cyphermode, encoding='utf-8')
    
    file_gene_other.close()

    # 1. Set…
    url = '"https://www.disgenet.org/browser/2/1/0/"+line.snp_id' if other_label == 'Variant' else '"https://www.disgenet.org/browser/1/1/1/"+line.gene_id'

    query = f'  Match (n:{type}{{identifier:line.{other_id}}}), (v:{other_label}{{identifier:line.{other_label.lower()}_id}}) Merge (n)-[r:{edge_type}]->(v) On Match Set r.disgenet = "yes", r.sources = split(line.sources, "|"), r.resource = split(line.resource, "|"),  r.EI = line.EI, r.pubMed_ids = split(line.pmid, "|"),r.NofSnps=split(line.NofSnps,"|"), r.associationType=split(line.associationType,"|"), r.sentences=split(line.sentence,"|") , r.score=line.score On Create Set r.source="DisGeNet", r.license="Attribution-NonCommercial-ShareAlike 4.0 International License", r.sources=split(line.sources,"|"), r.score=line.score,  r.resource=["DisGeNet"], r.disgenet="yes",  r.EI=line.EI, r.pubMed_ids=split(line.pmid,"|"), r.NofSnps=split(line.NofSnps,"|"), r.associationType=split(line.associationType,"|"), r.sentences=split(line.sentence,"|") , r.url={url}'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    file_cypher.write(query)
    # 2. Create… (finde beide KNOTEN)
    # query =get_query_start(path_of_directory, file_name + '.tsv') + f' Match (n:{type}{{identifier:line.{other_id}}}), (v:{other_label}{{identifier:line.{other_label.lower()}_id}}) Create (n)-[:{edge_type}{{source:"DisGeNet", sources:split(line.sources,"|"), score:line.score,  resource:["DisGeNet"], disgenet:"yes",  EI:line.EI, pubMed_ids:split(line.pmid,"|"), NofSnps:split(line.NofSnps,"|"), associationType:split(line.associationType,"|"), sentences:split(line.sentence,"|") , url:{url}}}]->(v)'
    # file_cypher.write(query)
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

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/disgenet')
    home = os.getcwd()
    source = os.path.join(home, 'output')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    for first_label in ['Gene', 'Variant']:
        path_of_directory = os.path.join(home, first_label.lower() + '_disease_edge/')

        for label in ['Disease', 'Symptom']:
            print('##########################################################################')

            print(datetime.datetime.now())
            print(f'gather all information of the {first_label}/' + label)

            load_edges_from_database_and_add_to_dict(label, first_label)

            print('##########################################################################')
            print(f'gather all information of the DisGeNet {first_label}/' + label)

            get_DisGeNet_information(label, 'a', first_label)

    driver.close()
    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
