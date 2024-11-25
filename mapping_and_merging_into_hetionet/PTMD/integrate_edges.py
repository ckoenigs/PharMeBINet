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

def get_PTMD_information(label_pharmebinet, label_ptmd, file_cypher):
    '''
    Load all PTMD variant-conditions and save to tsv
    '''

    path_of_directory = os.path.join(home, f'edges/')
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)


    dict_label_to_csv_file = {}

    dict_label_to_existing_pairs={}

    dict_label_to_new_pairs={}

    for other_label in ['Disease', 'SideEffect', 'Symptom', 'Phenotype']:
        # Create tsv for variant-disease edges
        file_name_not_mapped = f'new_{label_pharmebinet}_{other_label.lower()}_edges.tsv'
        not_mapped_path = os.path.join(path_of_directory, file_name_not_mapped)
        header=['variant_id', 'phenotype_id']
        # 2. Create new edges, write cypher queries
        query_rela_prop=f'MATCH (:{label_ptmd})-[p]-(:PTMD_Disease) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields order by allfields'
        list_props=[]
        for prop, in g.run(query_rela_prop):
            list_props.append(prop+':line.'+prop)
            header.append(prop)
        header.append('type')
        list_props.append( 'types:split(line.type,"|")')

        query = f' Match (v:{label_pharmebinet}{{identifier:line.variant_id}}), (d:{other_label}{{identifier:line.phenotype_id}}) Create (v)-[:IS_BIOMARKER_{pharmebinetutils.dictionary_label_to_abbreviation[label_pharmebinet]}ib{pharmebinetutils.dictionary_label_to_abbreviation[other_label]}{{resource:["MarkerDB"],markerdb:"yes", {", ".join(list_props)} }}]->(d)'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  file_name_not_mapped,
                                                  query)
        file_cypher.write(query)

        file = open(not_mapped_path, 'w', encoding='utf-8')
        writer = csv.DictWriter(file, delimiter='\t', fieldnames=header)
        writer.writeheader()
        dict_label_to_csv_file[other_label] = writer


        query_rela=f'Match (v:{label_pharmebinet})-[r:IS_BIOMARKER_{pharmebinetutils.dictionary_label_to_abbreviation[label_pharmebinet]}ib{pharmebinetutils.dictionary_label_to_abbreviation[other_label]}]->(d:{other_label}) Return v.identifier, d.identifier, r'
        dict_label_to_existing_pairs[other_label] = {}
        dict_label_to_new_pairs[other_label] = {}
        for node_id_1, node_id_2, edge,  in g.run(query_rela):
            dict_label_to_existing_pairs[other_label][(node_id_1, node_id_2)] = edge


    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_all = 0
    counter_not_mapped = 0
    dict_all_mappings = {}

    query = f"Match (n:{label_pharmebinet})--(p:{label_ptmd})-[r]-(:MarkerDB_Condition)--(m:Phenotype) Return p.id, n.identifier, type(r), r, m.identifier, labels(m)"
    results = g.run(query)

    for record in results:
        [markerdb_id, variant_id, rela_type, rela, phenotype_id, labels] = record.values()
        counter_all += 1
        rela_type=rela_type.split('_')[1]
        rela= dict(rela)
        rela['type']=rela_type
        # mapping of new edges
        if "Disease" in labels:
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['Disease']:
                print('exists')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['Disease']:
                dict_label_to_new_pairs['Disease'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['Disease'][(variant_id, phenotype_id)].append(rela)
            counter_disease += 1
        elif "SideEffect" in labels and (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = rela_type
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['SideEffect']:
                print('exists')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['SideEffect']:
                dict_label_to_new_pairs['SideEffect'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['SideEffect'][(variant_id, phenotype_id)].append(rela)
            counter_sideEffect += 1
        elif "Symptom" in labels and (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = rela_type
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['Symptom']:
                print('exists')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['Symptom']:
                dict_label_to_new_pairs['Symptom'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['Symptom'][(variant_id, phenotype_id)].append(rela)
            counter_symptom += 1
            # when label is only phenotype
        elif (variant_id, phenotype_id) not in dict_all_mappings:
            dict_all_mappings[(variant_id, phenotype_id)] = rela_type
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['Phenotype']:
                print('exists')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['Phenotype']:
                dict_label_to_new_pairs['Phenotype'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['Phenotype'][(variant_id, phenotype_id)].append(rela)
            counter_phenotype += 1

    # prepare the data for add them to the TSV file
    for label, dict_pair_to_types in dict_label_to_new_pairs.items():
        for (variant_id, phenotype_id), list_dict_rela_prop in dict_pair_to_types.items():
            new_dict={'variant_id':variant_id, 'phenotype_id':phenotype_id}
            for dict_rela_prop in list_dict_rela_prop:
                for key, value in dict_rela_prop.items():
                    if not key in new_dict:
                        new_dict[key]=set()
                    if type(value) != list:
                        new_dict[key].add(value)
                    else:
                        new_dict[key].union(value)
            for key, value in new_dict.items():
                if type(value) == set:
                    new_dict[key] = "|".join(value)
            dict_label_to_csv_file[label].writerow(new_dict)

    print('number of disease edges:', counter_disease)
    print('number of sideEffect edges:', counter_sideEffect)
    print('number of symptom edges:', counter_symptom)
    print('number of phenotype edges:', counter_phenotype)
    print('number of not mapped edges:', counter_not_mapped)
    print('number of all edges:', counter_all)

######### MAIN #########
def main():
    global home
    global path_of_directory
    global source

    # path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test/"
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    # os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/markerdb')
    home = os.getcwd()
    source = os.path.join(home, 'output')


    # cypher queries
    cypher_path = os.path.join(source, 'cypher_edge.cypher')
    file_cypher = open(cypher_path, "w", encoding='utf-8')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')
    print('gather all information of the MarkerDB variants/phenotypes')

    for (label_pharmebinet, label_ptmd) in [('PTM', 'PTMD_PTM'),
                                                ('Protein', 'PTMD_Protein')]:
        get_PTMD_information(label_pharmebinet, label_ptmd, file_cypher)

    driver.close()
    file_cypher.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()