import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# names of go terms in iid
set_of_gos = set(
    ['golgi apparatus', 'cytoplasm', 'cytoskeleton', 'endoplasmic reticulum', 'extracellular space', 'mitochondrion',
     'nuclear matrix', 'nucleolus', 'nucleoplasm', 'nucleus', 'peroxisome', 'plasma membrane', 'vacuole'])
set_of_gos_with_ = set([x.replace(' ', '_') for x in set_of_gos])

# dictionary cellular component go_name to go id
dict_go_name_to_id = {}

# iid disease categories
set_of_disease_categories_with_ = set(
    ['cancer', 'thoracic_cancer', 'organ_system_cancer', 'male_reproductive_organ_cancer', 'reproductive_organ_cancer',
     'gastrointestinal_system_cancer', 'intestinal_cancer', 'female_reproductive_organ_cancer', 'cell_type_cancer',
     'respiratory_system_cancer', 'lung_cancer', 'tauopathy', 'nervous_system_disease', 'neurodegenerative_disease',
     'central_nervous_system_disease', 'disease_of_anatomical_entity', 'immune_system_cancer', 'hematologic_cancer',
     'urinary_system_cancer', 'artery_disease', 'cardiovascular_system_disease', 'vascular_disease', 'bone_disease',
     'bone_inflammation_disease', 'arthritis', 'connective_tissue_disease', 'musculoskeletal_system_disease',
     'myeloid_leukemia', 'cognitive_disorder', 'psychotic_disorder', 'disease_of_mental_health', 'overnutrition',
     'acquired_metabolic_disease', 'disease_of_metabolism', 'nutrition_disease', 'carcinoma', 'astrocytoma',
     'glucose_metabolism_disease', 'carbohydrate_metabolism_disease', 'pancreatic_cancer', 'endocrine_gland_cancer',
     'autonomic_nervous_system_neoplasm', 'peripheral_nervous_system_neoplasm', 'nervous_system_cancer',
     'bone_marrow_cancer', 'myeloid_neoplasm', 'lower_respiratory_tract_disease', 'respiratory_system_disease',
     'lung_disease', 'bronchial_disease', 'obstructive_lung_disease', 'arteriosclerotic_cardiovascular_disease',
     'arteriosclerosis', 'lymphocytic_leukemia'])

# iid_set_of_disease
set_of_disease_with_ = set(
    ['breast_cancer', 'breast_carcinoma', 'prostate_cancer', 'prostate_carcinoma', 'stomach_cancer',
     'large_intestine_cancer', 'colorectal_cancer', 'ovarian_cancer', 'melanoma', 'malignant_glioma',
     'lung_carcinoma', 'stomach_carcinoma', 'Alzheimer\'s_disease', 'leukemia',
     'non-small_cell_lung_carcinoma', 'urinary_bladder_cancer', 'colon_carcinoma',
     'coronary_artery_disease', 'rheumatoid_arthritis', 'acute_myeloid_leukemia', 'schizophrenia',
     'obesity', 'squamous_cell_carcinoma', 'colon_cancer', 'glioblastoma_multiforme',
     'type_2_diabetes_mellitus', 'pancreatic_carcinoma', 'adenocarcinoma', 'liver_cancer',
     'neuroblastoma', 'diabetes_mellitus', 'multiple_myeloma', 'asthma', 'lymphoma', 'atherosclerosis',
     'hypertension', 'chronic_lymphocytic_leukemia'])

# iid set of species
set_of_species = set(
    ["alpaca", "cat", "chicken", "cow", "dog", "duck", "fly", "guinea_pig", "horse", "mouse", "pig", "rabbit", "rat",
     "sheep", "turkey", "worm", "yeast"])

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def get_go_cellular_component_id():
    """
    get cellular component ids
    :return:
    """
    query = 'Match (n:CellularComponent) Where toLower(n.name) in ["%s"] Return n.name, n.identifier'
    query = query % ('","'.join(set_of_gos))
    results = g.run(query)
    for record in results:
        [name, identifier] = record.values()
        dict_go_name_to_id[name.lower()] = identifier
    print('number of gos:', len(dict_go_name_to_id))


# dictionary protein pair to dictionary with resource and interaction id and other information
dict_protein_pair_to_dictionary = {}


def get_information_from_pharmebinet():
    """
    Get pharmebinet protein-protein-interaction information
    :return:
    """
    global maximal_id

    query = '''MATCH (n:Protein)-->(a:Interaction)-->(m:Protein) Where not (a.iso_of_protein_from is not NULL or a.iso_of_protein_to  is not NULL)  RETURN n.identifier, m.identifier, a.resource, a.identifier, a.interaction_ids'''
    results = g.run(query)

    for record in results:
        [interactor1_het_id, interactor2_het_id, resource, interaction_id, interaction_ids_EBI] = record.values()
        dict_protein_pair_to_dictionary[
            (interactor1_het_id, interactor2_het_id)] = {'resource': resource,
                                                         'interaction_ids_EBI': interaction_ids_EBI,
                                                         'interaction_id': interaction_id}

    query = 'MATCH (n:Interaction) With toInteger(n.identifier ) as int_id RETURN max(int_id) as v'

    maximal_id = g.run(query).single()['v']


def generate_file_and_cypher():
    """
    generate cypher file and tsv file
    :return:
    """
    query = '''MATCH (:protein_IID)-[p:interacts]->(:protein_IID) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields as l; '''
    results = g.run(query)

    file_name = 'interaction/rela'
    file_name_update = 'interaction/rela_match'
    file_name_go = 'interaction/rela_go'

    cypher_file = open('interaction/cypher.cypher', 'w', encoding='utf-8')

    query = '''Match (p1:Protein{identifier:line.protein_id_1}), (p2:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PiI{iid:'yes', source:'Integrated Interactions Database', resource:['IID'], url:"http://iid.ophid.utoronto.ca/" ,license:"free to use for academic purposes"}]->(b:Interaction{ identifier:line.id, '''

    query_update = '''Match (p1:Protein{identifier:line.protein_id_1})-[a:INTERACTS_PiI]->(m:Interaction{identifier:line.id})-[b:INTERACTS_IiP]->(p2:Protein{identifier:line.protein_id_2}) Set '''

    header = ['protein_id_1', 'protein_id_2', 'id']
    for head in results:
        head = head.data()['l']
        header.append(head)
        if head in ['evidence_types', 'dbs', 'methods', 'pmids', 'db_with_ppis',
                    'drugs_targeting_one_or_both_proteins']:
            if head != 'pmids':
                query += head + ':split(line.' + head + ',"|"), '
                query_update += 'm.' + head + '=split(line.' + head + ',"|"), '
            else:
                query += 'pubMed_ids:split(line.' + head + ',"|"), '
                query_update += 'm.pubMed_ids=split(line.' + head + ',"|"), '
        elif head in ['targeting_drugs', 'enzymes', 'ion_channels', 'receptors_transporters', 'drug_targets',
                      'orthologs_are_drug_targets', 'drugs targeting orthologs']:
            continue
        elif head in set_of_disease_categories_with_ or head in set_of_disease_with_ or head in set_of_gos_with_ or head in set_of_species:
            continue
        else:
            query += head + ':line.' + head + ', '
            query_update += 'm.' + head + '=line.' + head + ', '

    query += ' license:"free to use for academic purposes", iid:"yes", source:"Integrated Interactions Database", resource:["IID"], url:"http://iid.ophid.utoronto.ca/",  node_edge:true})-[:INTERACTS_IiP{iid:"yes", source:"Integrated Interactions Database", url:"http://iid.ophid.utoronto.ca/", resource:["IID"], license:"free to use for academic purposes"}]->(p2)'

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/iid/{file_name}.tsv',
                                              query)
    cypher_file.write(query)
    query_update += ' a.iid="yes", a.resource=split(line.resource,"|"), m.iid="yes", m.resource=split(line.resource,"|"), b.iid="yes", b.resource=split(line.resource,"|")'
    query_update = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/iid/{file_name_update}.tsv',
                                                     query_update)
    cypher_file.write(query_update)
    query = '''Match (i:Interaction{identifier:line.id}), (c:CellularComponent{identifier:line.go_id}) Set i.subcellular_location="GO term enrichment" Create (i)-[:MIGHT_SUBCELLULAR_LOCATES_ImslCC{license:"free to use for academic purposes", iid:"yes", source:"Integrated Interactions Database", url:"http://iid.ophid.utoronto.ca/" ,resource:["IID"]}]->(c)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/iid/{file_name_go}.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.close()

    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()

    header_merge = header.copy()
    header_merge.append('resource')
    file_merge = open(file_name_update + '.tsv', 'w', encoding='utf-8')
    csv_writer_merge = csv.DictWriter(file_merge, fieldnames=header_merge, delimiter='\t')
    csv_writer_merge.writeheader()

    file_go = open(file_name_go + '.tsv', 'w', encoding='utf-8')
    csv_writer_go = csv.writer(file_go, delimiter='\t')
    csv_writer_go.writerow(['id', 'go_id'])
    return csv_writer, csv_writer_go, csv_writer_merge


def prepare_dictionary(dictionary, counter):
    """
    prepare the list values in dictionary to strings
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) == list:
            value = '|'.join(value)
        new_dict[key] = value
    new_dict['id'] = counter
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}

# dictionary pair to go
dict_pair_to_go_ids = {}


def run_through_results_and_add_to_dictionary(results):
    """
    run through all results and add to the dictionaries. ALso check if have rela to go!
    :param results: neo4j result
    :return:
    """
    for record in results:
        [p1_id, rela, p2_id] = record.values()
        rela_info = dict(rela)
        if (p1_id, p2_id) not in dict_pair_to_infos and (p2_id, p1_id) not in dict_pair_to_infos:
            dict_pair_to_infos[(p1_id, p2_id)] = []
            dict_pair_to_go_ids[(p1_id, p2_id)] = set()
        if (p1_id, p2_id) in dict_pair_to_infos:
            for property, value in rela_info.items():
                property = property.lower()
                if property in dict_go_name_to_id:
                    dict_pair_to_go_ids[(p1_id, p2_id)].add(dict_go_name_to_id[property])

            dict_pair_to_infos[(p1_id, p2_id)].append(rela_info)
        else:
            for property, value in rela_info.items():
                property = property.lower()
                if property in dict_go_name_to_id:
                    dict_pair_to_go_ids[(p2_id, p1_id)].add(dict_go_name_to_id[property])

            dict_pair_to_infos[(p2_id, p1_id)].append(rela_info)


def load_and_prepare_IID_human_data():
    """
    write only rela with exp into file
    and p1.identifier in ['Q9NRW4', 'P45985'] and p2.identifier in ['Q9NRW4', 'P45985']
    """
    query = "Match l=(p1:Protein)-[:equal_to_iid_protein]-(d)-[r:interacts]->()-[:equal_to_iid_protein]-(p2:Protein) Where 'exp' in r.evidence_types Return count(l)"
    number_of_edges = g.run(query).single().values()[0]
    print(number_of_edges)
    max_number_of_results = 50000
    counter = 0
    while counter < number_of_edges:
        query = f'Match (p1:Protein)-[:equal_to_iid_protein]-(d)-[r:interacts]->()-[:equal_to_iid_protein]-(p2:Protein) Where "exp" in r.evidence_types With p1,r,p2 Skip {counter} Limit {max_number_of_results} Return p1.identifier, r, p2.identifier '
        print(query)
        results = g.run(query)
        run_through_results_and_add_to_dictionary(results)
        counter += max_number_of_results
        print(counter)

    # to check for selfloops interaction
    query = "Match l=(a:Protein)-[:equal_to_iid_protein]->(d)-[r:interacts]-(d) Where 'exp' in r.evidence_types Return count(l)"
    number_of_edges = g.run(query).single().values()[0]
    counter = 0
    while counter < number_of_edges:
        query = f'Match p=(a:Protein)-[:equal_to_iid_protein]->(d)-[r:interacts]-(d) Where "exp" in r.evidence_types With a,r Skip {counter} Limit {max_number_of_results} Return  a.identifier as p1 , r, a.identifier as p2 '
        results = g.run(query)
        run_through_results_and_add_to_dictionary(results)
        counter += max_number_of_results


def prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2):
    """
    Prepare if multiple edges exists for a pair a combined information edge.
    :param list_of_dict: list of dicitonaries
    :param p1: string
    :param p2: string
    :return:
    """
    new_dict = {}
    for dictionary in list_of_dict:
        for key, value in dictionary.items():
            if not key in new_dict:
                new_dict[key] = value
            elif new_dict[key] != value:
                print(p1)
                print(p2)
                print(key)
                print(value)
                print(new_dict[key])
                if type(value) == list:
                    set_value = set(value)
                    set_value = set_value.union(new_dict[key])
                    new_dict[key] = list(set_value)
                else:
                    print('also different type problem')
    return new_dict


def prepareMappedEdges(p1, p2, list_of_dict, csv_merge):
    """
    Prepare the mapped information to one edge and writ it into a csv file
    :param p1: string
    :param p2: string
    :param list_of_dict:list of dictionaries
    :param csv_merge: csv writer
    :return:
    """
    identifier = dict_protein_pair_to_dictionary[(p1, p2)]['interaction_id']
    if len(list_of_dict) == 1:
        final_dictionary = list_of_dict[0]
    else:
        print('multi')
        final_dictionary = prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2)
    final_dictionary['resource'] = pharmebinetutils.resource_add_and_prepare(
        dict_protein_pair_to_dictionary[(p1, p2)]['resource'], 'IID')
    final_dictionary['protein_id_1'] = p1
    final_dictionary['protein_id_2'] = p2
    csv_merge.writerow(prepare_dictionary(final_dictionary, identifier))
    return identifier


# set of added pairs
set_of_added_pair = set()


def write_info_into_files():
    """
    Check if a pair exist already in Pharmebinet or not and prepare the information for this.
    :return:
    """
    print_one_example_other_way_around = False
    csv_writer, csv_writer_go, csv_merge = generate_file_and_cypher()
    counter = maximal_id
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        if (p1, p2) in dict_protein_pair_to_dictionary:
            identifier = prepareMappedEdges(p1, p2, list_of_dict, csv_merge)
        elif (p2, p1) in dict_protein_pair_to_dictionary:
            identifier = prepareMappedEdges(p2, p1, list_of_dict, csv_merge)
            if not print_one_example_other_way_around:
                print_one_example_other_way_around = True
        else:
            # consider only one direction
            if (p1, p2) in set_of_added_pair or (p2, p1) in set_of_added_pair:
                continue
            counter += 1
            identifier = counter
            if len(list_of_dict) == 1:
                final_dictionary = list_of_dict[0]
            else:
                print('multi')
                final_dictionary = prepare_multiple_edges_between_same_pairs(list_of_dict, p1, p2)
            final_dictionary['protein_id_1'] = p1
            final_dictionary['protein_id_2'] = p2
            csv_writer.writerow(prepare_dictionary(final_dictionary, identifier))
            set_of_added_pair.add((p1, p2))

        if (p1, p2) in dict_pair_to_go_ids:
            for go in dict_pair_to_go_ids[(p1, p2)]:
                csv_writer_go.writerow([identifier, go])

        if counter % 10000 == 0:
            print(counter)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate connection to neo4j')

    create_connection_with_neo4j()
    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load go ')

    get_go_cellular_component_id()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('load IID human data')

    load_and_prepare_IID_human_data()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('get ppi information')

    get_information_from_pharmebinet()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('prepare files')

    write_info_into_files()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
