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

# dictionary name to pc ids
dict_name_to_pathway_ids={}

# dictionary_mesh_id_to_pathway_ids
dict_mesh_id_to_pathway_ids={}

def load_pc_from_database():
    """
    Load all pc into different mapping dictionaries
    :return:
    """
    query='''Match (n:Pathway) Return n'''
    results=g.run(query)
    for node, in results:
        identifier= node['identifier']
        name=node['name'].lower()
        add_entry_to_dictionary(dict_name_to_pathway_ids,name,identifier)

        synonyms= node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            add_entry_to_dictionary(dict_name_to_pathway_ids,synonym.lower(), identifier)



def generate_files(path_of_directory):
    """
    generate cypher file and csv file
    :return: csv files
    """
    # file from relationship between gene and variant
    file_name = 'pathway/mapping_pathway.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    header = [ 'pathway_db_id', 'pathway_id','resource']
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    # not mapped file
    file_name_not = 'pathway/not_mapped_pathway.tsv'
    file_not = open(file_name_not, 'w', encoding='utf-8')
    header_not = ['pathway_db_id', 'name']
    csv_not_mapped = csv.writer(file_not, delimiter='\t')
    csv_not_mapped.writerow(header_not)

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/%s" As line FIELDTERMINATOR '\\t' 
        Match (n:Pathway{identifier:line.pathway_id}), (v:Pathway_DrugBank{identifier:line.pathway_db_id}) Create (n)-[r:equal_to_pathway_drugbank]->(v) Set n.drugbank="yes", n.resource=split(line.resource,"|") ;\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    return csv_mapping, csv_not_mapped

# dictionary mapping db pathway and pathway to howmapped
dict_db_pathway_pathway_to_how_mapped={}


def load_all_drugbank_pc_and_map(csv_mapping, csv_not_mapped):
    query = "MATCH (v:Pathway_DrugBank) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped=0
    counter_not_mapped=0

    for node, in results:
        identifier=node['identifier']
        name=node['name'].lower()
        found_mapping=False
        if name in dict_name_to_pathway_ids:
            found_mapping = True
            for pathway_id in dict_name_to_pathway_ids[name]:
                if (identifier, pathway_id) not in dict_db_pathway_pathway_to_how_mapped:
                    dict_db_pathway_pathway_to_how_mapped[(identifier, pathway_id)] = 'name_mapped'
                    csv_mapping.writerow([identifier, pathway_id, 'name_mapped'])
                else:
                    print('multy mapping with name')
        if found_mapping:
            counter_mapped+=1
        else:
            counter_not_mapped+=1
            csv_not_mapped.writerow([identifier, name])
    print('number of mapped node:',counter_mapped)
    print('number of not mapped node:', counter_not_mapped)

def main():
    print(datetime.datetime.utcnow())
    global path_of_directory, license
    if len(sys.argv) < 3:
        sys.exit('need path anf license pc drugbank')

    path_of_directory = sys.argv[1]
    license = sys.argv[2]
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load pc from neo4j')

    load_pc_from_database()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher and csv file')

    csv_mapping, csv_not_mapped = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load pc from drugbank and map')

    load_all_drugbank_pc_and_map(csv_mapping, csv_not_mapped)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
