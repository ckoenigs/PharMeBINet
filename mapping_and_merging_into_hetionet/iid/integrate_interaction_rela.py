import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

# dictionary chemical name to id
dict_name_to_chemical_ids={}

def add_entry_to_dictionary(dictionary, key, value):
    """
    prepare dictionary with value
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key]=set()
    dictionary[key].add(value)

def load_chemical_to_dict():
    """
    Prepare dictionary from name to chemical id
    :return:
    """
    query='''Match (c:Chemical) Where not c:Product Return c.name, c.synonyms, c.identifier;'''
    results=g.run(query)
    for name, synonyms, identifier, in results:
        if name:
            name=name.lower()
            add_entry_to_dictionary(dict_name_to_chemical_ids,name, identifier)
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                add_entry_to_dictionary(dict_name_to_chemical_ids, synonym, identifier)


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
    file_name_drug='interaction/rela_drug'

    cypher_file = open('interaction/cypher.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/iid/%s.tsv" As line FIELDTERMINATOR '\\t' 
            Match (p1:Protein{identifier:line.protein_id_1}), (p2:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PRiI]->(b:Interaction{ '''
    query = query % (path_of_directory, file_name)

    header = ['protein_id_1', 'protein_id_2', 'id']
    for head, in results:
        header.append(head)
        if head in ['targeting_drugs', 'evidence_type', 'dbs', 'methods', 'pmids']:
            query += head + ':split(line.' + head + ',"|"), '
        else:
            query += head + ':line.' + head + ', '

    query += ' license:"blub", iid:"yes", resource:["IID"], url:"blub", identifier:"IPP_"+line.id, meta_edge:true})-[:INTERACTS_IiPR]->(p2);\n'
    cypher_file.write(query)
    cypher_file.write('Create Constraint On (node:Interaction) Assert node.identifier Is Unique;\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/iid/%s.tsv" As line FIELDTERMINATOR '\\t' 
                Match (i:Interaction{identifier:"IPP_"+line.id}), (c:Chemical{identifier:line.chemical_id}) Create (i)<-[:DRUG_TARGET_CdtI]-(c);\n'''
    query = query % (path_of_directory, file_name_drug)
    cypher_file.write(query)
    cypher_file.close()

    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()

    file_drug = open(file_name_drug + '.tsv', 'w', encoding='utf-8')
    csv_writer_drug = csv.writer(file_drug, delimiter='\t')
    csv_writer_drug.writerow(['id','chemical_id'])
    return csv_writer, csv_writer_drug


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
    new_dict['id']=counter
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}

# dictionary pair to drugs id
dict_pair_to_drug_ids={}

def run_through_results_and_add_to_dictionary(results):
    """
    run through all results and add to the dictionaries. ALso check if have target drug and map to chemical!
    :param results: neo4j result
    :return:
    """
    for p1_id, rela, p2_id, in results:
        rela_info = dict(rela)
        if (p1_id, p2_id) not in dict_pair_to_infos:
            dict_pair_to_infos[(p1_id, p2_id)] = []
            dict_pair_to_drug_ids[(p1_id,p2_id)]=set()
        drugs= rela['targeting_drugs']
        if drugs:
            for drug in drugs:
                drug=drug.lower()
                if drug in dict_name_to_chemical_ids:
                    for chemical_id in dict_name_to_chemical_ids[drug]:
                        dict_pair_to_drug_ids[(p1_id, p2_id)].add(chemical_id)
                else:
                    print('ohno')
                    print(drug)

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
    query= '''Match p=(a:Protein)-[:equal_to_iid_protein]->(d:protein_IID)-[r:interacts]-(d) Where 'exp' in r.evidence_types Return  a.identifier as p1 , r, a.identifier as p2 '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)


def write_info_into_files():
    csv_writer, csv_writer_drug = generate_file_and_cypher()
    counter = 0
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        counter += 1

        if (p1,p2) in dict_pair_to_drug_ids:
            for drug in dict_pair_to_drug_ids[(p1,p2)]:
                csv_writer_drug.writerow([counter, drug])

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
    print('load chemical')

    load_chemical_to_dict()

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
