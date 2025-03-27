import datetime
import os
import sys
import csv
import json

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


def get_MarkerDB_information(label_pharmebinet, label_markerdb, file_cypher, has_reference):
    '''
    Load all MarkerDB variant-conditions and save to tsv
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
        # query_rela_prop=f'MATCH (:{label_markerdb})-[p]-(:MarkerDB_Condition) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields order by allfields'

        # for prop, in g.run(query_rela_prop):
        #     list_props.append(prop+':line.'+prop)
        #     header.append(prop)
        header.append('type')
        header.append('reference')
        header.append('markerID')
        header.append('citations')
        header.append('rela_info')
        if not has_reference:
            header.append('pmids')
            part='r.pubMed_ids=split(line.pmids,"|")'
            condition='r.citations is not null or r.pmids is not null'
        else:
            header.append('reference')
            part='r.pubMed_ids=split(line.reference,"|")'
            condition='p.reference is not null'

        dict_label_to_type={'Variant':'sequence_variants','Gene':'sequence_variants','Metabolite':'chemicals','Protein':'proteins'}
        query = f' Match (v:{label_pharmebinet}{{identifier:line.variant_id}}), (d:{other_label}{{identifier:line.phenotype_id}}) Merge (v)-[r:IS_BIOMARKER_{pharmebinetutils.dictionary_label_to_abbreviation[label_pharmebinet]}ib{pharmebinetutils.dictionary_label_to_abbreviation[other_label]}]->(d) On Create Set r.rela_info=split(line.rela_info,"|"), r.resource=["MarkerDB"], r.markerdb="yes",r.citations=split(line.citations,"|"), r.types=split(line.type,"|"), r.source="MarkerDB", {part}, r.license="CC BY-NC 4.0", r.url="https://markerdb.ca/{dict_label_to_type[label_pharmebinet]}/"+line.markerID On Match Set r.rela_info=split(line.rela_info,"|"), r.markerdb="yes",r.citations=split(line.citations,"|"), r.types=split(line.type,"|")'
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
            dict_label_to_existing_pairs[other_label][(node_id_1, node_id_2)] = dict(edge)


    counter_disease = 0
    counter_sideEffect = 0
    counter_symptom = 0
    counter_phenotype = 0
    counter_all = 0
    counter_not_mapped = 0
    # {{identifier:'rs61277444'}}
    query = f"Match (n:{label_pharmebinet} )--(p:{label_markerdb})-[r]-(:MarkerDB_Condition)--(m:Phenotype ) Where {condition} Return p.id, p.reference, n.identifier, type(r), r, m.identifier, labels(m)"
    print(query)
    results = g.run(query)

    for record in results:
        [markerdb_id, reference, variant_id, rela_type, rela, phenotype_id, labels] = record.values()
        counter_all += 1
        rela_type=rela_type.split('_')[1]
        dict_all_rela={}
        rela= dict(rela)
        if label_pharmebinet=='Variant':
            if reference:
                dict_all_rela['reference']=str(reference)
        dict_all_rela['type']=rela_type
        dict_all_rela['markerID']=markerdb_id
        dict_all_rela['rela_info']=rela
        # mapping of new edges
        if "Disease" in labels:
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['Disease']:
                print('exists', variant_id, phenotype_id)
                sys.exit(f'edge exists between disease and {label_pharmebinet}, check properties to combine and resource!')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['Disease']:
                dict_label_to_new_pairs['Disease'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['Disease'][(variant_id, phenotype_id)].append(dict_all_rela)
            counter_disease += 1
        elif "SideEffect" in labels:
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['SideEffect']:
                print('exists', variant_id, phenotype_id)
                sys.exit(f'edge exists between SE and {label_pharmebinet}, check properties to combine and resource!')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['SideEffect']:
                dict_label_to_new_pairs['SideEffect'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['SideEffect'][(variant_id, phenotype_id)].append(dict_all_rela)
            counter_sideEffect += 1
        elif "Symptom" in labels:
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['Symptom']:
                print('exists', variant_id, phenotype_id)
                sys.exit(f'edge exists between symptom and {label_pharmebinet}, check properties to combine and resource!')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['Symptom']:
                dict_label_to_new_pairs['Symptom'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['Symptom'][(variant_id, phenotype_id)].append(dict_all_rela)
            counter_symptom += 1
            # when label is only phenotype
        elif (variant_id, phenotype_id) :
            if (variant_id, phenotype_id)  in dict_label_to_existing_pairs['Phenotype']:
                print('exists', variant_id, phenotype_id)
                sys.exit(f'edge exists between phenotype and {label_pharmebinet}, check properties to combine and resource!')
            if not (variant_id, phenotype_id) in dict_label_to_new_pairs['Phenotype']:
                dict_label_to_new_pairs['Phenotype'][(variant_id, phenotype_id)]= []
            dict_label_to_new_pairs['Phenotype'][(variant_id, phenotype_id)].append(dict_all_rela)
            counter_phenotype += 1

    # prepare the data for add them to the TSV file
    for label, dict_pair_to_types in dict_label_to_new_pairs.items():
        for (variant_id, phenotype_id), list_dict_rela_prop in dict_pair_to_types.items():
            new_dict={'variant_id':variant_id, 'phenotype_id':phenotype_id}

            for dict_rela_prop in list_dict_rela_prop:
                for key, value in dict_rela_prop.items():
                    if key in ['type', 'markerID','reference']:
                        if not key in new_dict:
                            new_dict[key]=set()
                        new_dict[key].add(value)
                    else:
                        if not key in new_dict:
                            new_dict[key] = set()

                        if len(value) > 0:
                            new_dict[key].add(json.dumps( value).lower())
                            for rela_key, rela_value in value.items():
                                if rela_key in ['citations','pmids']:
                                    if rela_key not in new_dict:
                                        new_dict[rela_key] = set()
                                    if rela_key =='pmids':
                                        for pmid in rela_value:
                                            new_dict[rela_key].add(str(pmid))
                                    else:
                                        new_dict[rela_key]= new_dict[rela_key].union(rela_value)

            for key, value in new_dict.items():

                if type(value) in [set,list] and key!='markerID':
                    new_dict[key] = "|".join(value)
                elif key=='markerID':
                    new_dict[key] = list(value)[0]
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

    for (label_pharmebinet, label_markerdb, has_reference) in [
                                                ('Variant', 'MarkerDB_SequenceVariant',True),
                                                ('Protein', 'MarkerDB_Protein',False),
                                                ('Metabolite', 'MarkerDB_Chemical',False)
                                                ]:
        get_MarkerDB_information(label_pharmebinet, label_markerdb, file_cypher, has_reference)

    driver.close()
    file_cypher.close()

    print('##########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
