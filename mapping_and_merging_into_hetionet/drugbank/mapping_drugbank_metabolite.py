import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

def add_entry_to_dictionary(dictionary, key, value):
    """
    prepare entry in dictionary if not exists. Then add new value.
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key]=set()
    dictionary[key].add(value)

# dictionary for the different mapping methods
dict_different_mapping_methods=defaultdict(dict)

# dictionary metabolite_id to resource
dict_metabolite_id_to_resource={}

def load_metabolite_from_database():
    """
    Load all pc into different mapping dictionaries
    :return:
    """
    query='''Match (n:Metabolite) Return n'''
    results=g.run(query)
    for node, in results:
        identifier= node['identifier']
        dict_metabolite_id_to_resource[identifier]=set(node['resource'])
        name=node['name'].lower()
        add_entry_to_dictionary(dict_different_mapping_methods['name'],name,identifier)

        # synonyms= node['synonyms'] if 'synonyms' in node else []
        # for synonym in synonyms:
        #     add_entry_to_dictionary(dict_different_mapping_methods['name'],synonym.lower(), identifier)

        inchikey=node['inchikey']
        if inchikey:
            add_entry_to_dictionary(dict_different_mapping_methods['inchikey'], inchikey, identifier)

        smiles = node['smiles']
        if inchikey:
            add_entry_to_dictionary(dict_different_mapping_methods['smiles'], smiles, identifier)




def generate_files(path_of_directory):
    """
    generate cypher file and csv file
    :return: csv files
    """
    # file from relationship between gene and variant
    file_name = 'metabolite/mapping_metabolite.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    header = [ 'metabolite_db_id', 'metabolite_id','resource', 'how_mapped']
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    # not mapped file
    file_name_not = 'metabolite/not_mapped_metabolite.tsv'
    file_not = open(file_name_not, 'w', encoding='utf-8')
    header_not = ['metabolite_db_id', 'name']
    csv_not_mapped = csv.writer(file_not, delimiter='\t')
    csv_not_mapped.writerow(header_not)

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/%s" As line FIELDTERMINATOR '\\t' 
        Match (n:Metabolite{identifier:line.metabolite_id}), (v:Metabolite_DrugBank{identifier:line.metabolite_db_id}) Create (n)-[r:equal_to_metabolite_drugbank{how_mapped:line.how_mapped}]->(v) Set n.drugbank="yes", n.resource=split(line.resource,"|") ;\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)
    cypher_file.close()

    return csv_mapping, csv_not_mapped

# set of  mapping db metabolite and metabolite
set_of_metabolite_pairs=set()

# dictionary db metabolite to metabolite_ids
dict_db_metabolite_id_to_metabolite_ids={}


def add_resource(set_resource):
    """
    Add resource and prepare string
    :param set_resource: set
    :return:
    """
    set_resource.add('DrugBank')
    return '|'.join(sorted(set_resource))

def load_all_drugbank_pc_and_map(csv_mapping, csv_not_mapped):
    query = "MATCH (v:Metabolite_DrugBank) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped=0
    counter_not_mapped=0

    for node, in results:
        identifier=node['identifier']
        name=node['name'].lower()
        inchi_key = node['inchi_key']
        smiles=node['smiles']
        found_mapping=False
        if inchi_key in dict_different_mapping_methods['inchikey']:
            found_mapping = True
            dict_db_metabolite_id_to_metabolite_ids[identifier] = dict_different_mapping_methods['inchikey'][inchi_key]
            for metabolite_id in dict_different_mapping_methods['inchikey'][inchi_key]:
                if (identifier, metabolite_id) not in set_of_metabolite_pairs:
                    set_of_metabolite_pairs.add((identifier, metabolite_id))
                    csv_mapping.writerow(
                        [identifier, metabolite_id, add_resource(dict_metabolite_id_to_resource[metabolite_id]),'inchi_key'])
                else:
                    print('multy mapping with inchikey')

        if found_mapping:
            counter_mapped += 1
            continue

        if smiles in dict_different_mapping_methods['smiles']:
            found_mapping = True
            dict_db_metabolite_id_to_metabolite_ids[identifier] = dict_different_mapping_methods['smiles'][smiles]
            for metabolite_id in dict_different_mapping_methods['smiles'][smiles]:
                if (identifier, metabolite_id) not in set_of_metabolite_pairs:
                    set_of_metabolite_pairs.add((identifier, metabolite_id))
                    csv_mapping.writerow(
                        [identifier, metabolite_id, add_resource(dict_metabolite_id_to_resource[metabolite_id]),'smiles'])
                else:
                    print('multy mapping with smiles')

        if found_mapping:
            counter_mapped += 1
            continue

        if name in dict_different_mapping_methods['name']:
            found_mapping = True
            dict_db_metabolite_id_to_metabolite_ids[identifier] = dict_different_mapping_methods['name'][name]
            for metabolite_id in dict_different_mapping_methods['name'][name]:
                if (identifier, metabolite_id) not in set_of_metabolite_pairs:
                    set_of_metabolite_pairs.add((identifier, metabolite_id))
                    csv_mapping.writerow(
                        [identifier, metabolite_id, add_resource(dict_metabolite_id_to_resource[metabolite_id]),'name'])
                else:
                    print('multy mapping with name')


        if found_mapping:
            counter_mapped += 1
        else:
            counter_not_mapped += 1
            csv_not_mapped.writerow([identifier, name])
    print('number of mapped node:',counter_mapped)
    print('number of not mapped node:', counter_not_mapped)

def main():
    print(datetime.datetime.utcnow())
    global path_of_directory, license
    if len(sys.argv) < 3:
        sys.exit('need path anf license metabolite drugbank')

    path_of_directory = sys.argv[2]
    license = sys.argv[1]
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load metabolite from neo4j')

    load_metabolite_from_database()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher and csv file')

    csv_mapping, csv_not_mapped = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load metabolites from drugbank and map')

    load_all_drugbank_pc_and_map(csv_mapping, csv_not_mapped)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
