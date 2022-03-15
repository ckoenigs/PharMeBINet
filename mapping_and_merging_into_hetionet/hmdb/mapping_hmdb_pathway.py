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
        dictionary[key] = set()
    dictionary[key].add(value)


# dictionary name/synonym to pc ids
dict_name_to_pathway_ids = {}

# dictionary pathway id to resource
dict_pathway_id_to_resource={}

# dictionary hmdb id to pathway id
dict_hmdb_id_to_pathway_ids={}


def load_pw_from_database():
    """
    Load all pc into different mapping dictionaries
    :return:
    """
    query = '''Match (n:Pathway) Return n'''
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']
        dict_pathway_id_to_resource[identifier]=set(node['resource'])
        name = node['name'].lower()
        add_entry_to_dictionary(dict_name_to_pathway_ids, name, identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            add_entry_to_dictionary(dict_name_to_pathway_ids, synonym.lower(), identifier)

        xrefs= node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            split_xrefs=xref.split(':',1)
            if split_xrefs[0]=='pathbank':
                add_entry_to_dictionary(dict_hmdb_id_to_pathway_ids, split_xrefs[1], identifier)
            elif split_xrefs[0]=='smpdb':
                add_entry_to_dictionary(dict_hmdb_id_to_pathway_ids, split_xrefs[1], identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv files
    """
    # file from relationship between gene and variant
    file_name = 'pathway/mapping_pathway.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    header = ['pathway_hmdb_id', 'pathway_id', 'resource', 'how_mapped']
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    # not mapped file
    file_name_not = 'pathway/not_mapped_pathway.tsv'
    file_not = open(file_name_not, 'w', encoding='utf-8')
    header_not = ['pathway_smpdb_id', 'name', 'new_id']
    csv_not_mapped = csv.writer(file_not, delimiter='\t')
    csv_not_mapped.writerow(header_not)

    cypher_file = open('output/cypher_part2.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR '\\t' 
        Match (n:Pathway{identifier:line.pathway_id}), (v:Pathway_HMDB{identifier:line.pathway_hmdb_id}) Create (n)-[r:equal_to_pathway_hmdb{how_mapped:line.how_mapped}]->(v) Set n.hmdb="yes", n.resource=split(line.resource,"|") ;\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    return csv_mapping, csv_not_mapped

def add_source_to_resource_and_prepare_string(resource):
    """
    prepare resource to string
    :param resource:
    :return:
    """
    resource.add('HMDB')
    return '|'.join(sorted(resource))


# dictionary mapping db pathway and pathway to how mapped
dict_db_pathway_pathway_to_how_mapped = {}


def load_all_hmdb_pw_and_map(csv_mapping, csv_not_mapped):
    global highest_identifier
    query = "MATCH (v:Pathway_HMDB) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped = 0
    counter_not_mapped = 0

    for node, in results:
        identifier= node['identifier']
        smpdb_id = node['smpdb_id'].replace('P','P00') if 'smpdb_id' in node else ''
        name = node['name'].lower()
        found_mapping = False
        if smpdb_id in dict_hmdb_id_to_pathway_ids:
            found_mapping=True
            for pathway_id in dict_hmdb_id_to_pathway_ids[smpdb_id]:
                if (identifier, pathway_id) not in dict_db_pathway_pathway_to_how_mapped:
                    dict_db_pathway_pathway_to_how_mapped[(identifier, pathway_id)] = 'smpdb_id_mapped'
                    csv_mapping.writerow([identifier, pathway_id, add_source_to_resource_and_prepare_string(dict_pathway_id_to_resource[pathway_id]),'smpdb_id_mapped'])
                else:
                    print('multy mapping')
        if found_mapping:
            counter_mapped += 1
            continue

        if name in dict_name_to_pathway_ids:
            found_mapping = True
            for pathway_id in dict_name_to_pathway_ids[name]:
                if (identifier, pathway_id) not in dict_db_pathway_pathway_to_how_mapped:
                    dict_db_pathway_pathway_to_how_mapped[(identifier, pathway_id)] = 'name_mapped'
                    csv_mapping.writerow([identifier, pathway_id, add_source_to_resource_and_prepare_string(dict_pathway_id_to_resource[pathway_id]),'name_mapped'])
                else:
                    print('multy mapping with name')
        if found_mapping:
            counter_mapped += 1
        else:
            counter_not_mapped += 1
            csv_not_mapped.writerow([identifier, name])
    print('number of mapped node:', counter_mapped)
    print('number of not mapped node:', counter_not_mapped)


def main():
    print(datetime.datetime.now())
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need path for hmdb pathway')

    path_of_directory = sys.argv[1]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pw from neo4j')

    load_pw_from_database()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping, csv_not_mapped = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pc from hmdb and map')

    load_all_hmdb_pw_and_map(csv_mapping, csv_not_mapped)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
