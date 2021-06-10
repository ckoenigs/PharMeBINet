import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

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

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def get_go_cellular_component_id():
    """
    get cellular component ids
    :return:
    """
    query = 'Match (n:CellularComponent) Where toLower(n.name) in ["%s"] Return n.name, n.identifier'
    query = query % ('","'.join(set_of_gos))
    results = g.run(query)
    for name, identifier, in results:
        dict_go_name_to_id[name.lower()] = identifier
    print('number of gos:', len(dict_go_name_to_id))


def add_entry_to_dictionary(dictionary, key, value):
    """
    prepare dictionary with value
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def generate_file_and_cypher():
    """
    generate cypher file and csv file
    :return:
    """
    query = '''MATCH (:protein_IID)-[p:interacts]->(:protein_IID) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields; '''
    results = g.run(query)

    file_name = 'interaction/rela'
    file_name_go = 'interaction/rela_go'

    cypher_file = open('interaction/cypher.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/iid/%s.tsv" As line FIELDTERMINATOR '\\t' 
            Match (p1:Protein{identifier:line.protein_id_1}), (p2:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PiI]->(b:Interaction{ '''
    query = query % (path_of_directory, file_name)

    header = ['protein_id_1', 'protein_id_2', 'id']
    for head, in results:
        header.append(head)
        if head in ['evidence_type', 'dbs', 'methods', 'pmids']:
            query += head + ':split(line.' + head + ',"|"), '
        elif head in ['targeting_drugs', 'enzymes', 'ion_channels', 'receptors_transporters', 'drug_targets',
                      'orthologs_are_drug_targets', 'drugs targeting orthologs']:
            continue
        elif head in set_of_disease_categories_with_ or head in set_of_disease_with_ or head in set_of_gos_with_:
            continue
        else:
            query += head + ':line.' + head + ', '

    query += ' license:"free to use for academic purposes", iid:"yes", source:"Integrated Interactions Database", resource:["IID"], url:"http://iid.ophid.utoronto.ca/", identifier:"IPP_"+line.id, node_edge:true})-[:INTERACTS_IiP]->(p2);\n'
    cypher_file.write(query)
    cypher_file.write('Create Constraint On (node:Interaction) Assert node.identifier Is Unique;\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/iid/%s.tsv" As line FIELDTERMINATOR '\\t' 
                Match (i:Interaction{identifier:"IPP_"+line.id}), (c:CellularComponent{identifier:line.go_id}) Set i.subcellular_location="GO term enrichment" Create (i)-[:MIGHT_SUBCELLULAR_LOCATES_ImslCC]->(c);\n'''
    query = query % (path_of_directory, file_name_go)
    cypher_file.write(query)
    cypher_file.close()

    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()

    file_go = open(file_name_go + '.tsv', 'w', encoding='utf-8')
    csv_writer_go = csv.writer(file_go, delimiter='\t')
    csv_writer_go.writerow(['id', 'go_id'])
    return csv_writer, csv_writer_go


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
    for p1_id, rela, p2_id, in results:
        rela_info = dict(rela)
        if (p1_id, p2_id) not in dict_pair_to_infos:
            dict_pair_to_infos[(p1_id, p2_id)] = []
            dict_pair_to_go_ids[(p1_id, p2_id)] = set()

        for property, value in rela_info.items():
            property = property.lower()
            if property in dict_go_name_to_id:
                dict_pair_to_go_ids[(p1_id, p2_id)].add(dict_go_name_to_id[property])

        rela_info['protein_id_1'] = p1_id
        rela_info['protein_id_2'] = p2_id

        dict_pair_to_infos[(p1_id, p2_id)].append(rela_info)


def load_and_prepare_IID_human_data():
    """
    write only rela with exp into file
    """

    query = '''Match (p1:Protein)-[:equal_to_iid_protein]-(d:protein_IID)-[r:interacts]->(:protein_IID)-[:equal_to_iid_protein]-(p2:Protein) Where 'exp' in r.evidence_types Return p1.identifier, r, p2.identifier '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)

    # to check for selfloops interaction
    query = '''Match p=(a:Protein)-[:equal_to_iid_protein]->(d:protein_IID)-[r:interacts]-(d) Where 'exp' in r.evidence_types Return  a.identifier as p1 , r, a.identifier as p2 '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)


def write_info_into_files():
    csv_writer, csv_writer_go = generate_file_and_cypher()
    counter = 0
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        counter += 1

        if (p1, p2) in dict_pair_to_go_ids:
            for go in dict_pair_to_go_ids[(p1, p2)]:
                csv_writer_go.writerow([counter, go])

        if len(list_of_dict) == 1:
            csv_writer.writerow(prepare_dictionary(list_of_dict[0], counter))
        else:
            print('multi')
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

            csv_writer.writerow(prepare_dictionary(new_dict, counter))
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

    print(datetime.datetime.utcnow())
    print('generate connection to neo4j')

    create_connection_with_neo4j()
    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load go ')

    get_go_cellular_component_id()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('load IID human data')

    load_and_prepare_IID_human_data()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('prepare files')

    write_info_into_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
