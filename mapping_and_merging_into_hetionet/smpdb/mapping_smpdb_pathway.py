import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary name/synonym to pc ids
dict_name_to_pathway_ids = {}

# dictionary pathway id to resource
dict_pathway_id_to_resource = {}

# dictionary smpdb id to pathway id
dict_smpdb_id_to_pathway_ids = {}

# dictionary pathway id to xrefs
dict_pathway_id_to_xrefs = {}


def load_pw_from_database():
    """
    Load all pc into different mapping dictionaries
    :return:
    """
    global highest_identifier
    query = '''Match (n:Pathway) Return n'''
    results = g.run(query)
    highest_identifier = 0
    for node, in results:
        identifier = node['identifier']
        dict_pathway_id_to_resource[identifier] = set(node['resource'])
        # find the highest number
        if int(identifier.split("_", -1)[1]) > highest_identifier:
            highest_identifier = int(identifier.split("_", -1)[1])

        name = node['name']
        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pathway_ids, name.lower(), identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pathway_ids, synonym.lower(), identifier)

        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            split_xrefs = xref.split(':', 1)
            if split_xrefs[0] == 'pathbank':
                pharmebinetutils.add_entry_to_dict_to_set(dict_smpdb_id_to_pathway_ids, split_xrefs[1], identifier)
        dict_pathway_id_to_xrefs[identifier] = set(xrefs)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv files
    """
    # file from relationship between gene and variant
    file_name = 'pathway/mapping_pathway.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    header = ['pathway_smpdb_id', 'pathway_id', 'resource', 'how_mapped', 'xrefs']
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    # not mapped file
    file_name_not = 'pathway/not_mapped_pathway.tsv'
    file_not = open(file_name_not, 'w', encoding='utf-8')
    header_not = ['pathway_smpdb_id', 'name', 'new_id', 'xrefs']
    csv_not_mapped = csv.writer(file_not, delimiter='\t')
    csv_not_mapped.writerow(header_not)

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/smpdb/%s" As line FIELDTERMINATOR '\\t' 
        Match (n:Pathway{identifier:line.pathway_id}), (v:pathway_smpdb{smpdb_id:line.pathway_smpdb_id}) Create (n)-[r:equal_to_pathway_smpdb{how_mapped:line.how_mapped}]->(v) Set n.smpdb="yes", n.resource=split(line.resource,"|") , n.description=v.description, n.xrefs= split(line.xrefs,"|"), n.category=v.category, n.source= n.source+', SMPDB', n.license=n.license+'SMPDB is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (SMPDB) and the original publication.';\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/smpdb/%s" As line FIELDTERMINATOR '\\t' 
            Match  (v:pathway_smpdb{smpdb_id:line.pathway_smpdb_id}) Merge (n:Pathway{identifier:line.new_id}) On Create Set  n.smpdb="yes", n.resource=["SMPDB"], n.source="SMPDB", n.license="SMPDB is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (SMPDB) and the original publication",n.category=v.category, n.description=v.description, n.name=v.name, n.xrefs=split(line.xrefs,'|'), n.url="https://smpdb.ca/view/"+line.pathway_smpdb_id  Create (n)-[r:equal_to_pathway_smpdb]->(v);\n'''
    query = query % (path_of_directory, file_name_not)
    cypher_file.write(query)

    return csv_mapping, csv_not_mapped


def add_sources_to_xrefs_and_prepare_string(xrefs, add_list):
    """
    prepare resource to string
    :param xrefs:
    :return:
    """
    xrefs=xrefs.union(add_list)
    return '|'.join(sorted(xrefs))


# dictionary mapping db pathway and pathway to how mapped
dict_db_pathway_pathway_to_how_mapped = {}

# dictionary name pathway name to pathway id
dict_new_pathway_name_to_pathway_ids = {}


def load_all_smpdb_pw_and_map(csv_mapping):
    query = "MATCH (v:pathway_smpdb) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped = 0
    counter_not_mapped = 0

    for node, in results:
        identifier = node['smpdb_id']
        name = node['name'].lower()
        path_whiz_id = node['pw_id']
        found_mapping = False
        if identifier in dict_smpdb_id_to_pathway_ids:
            found_mapping = True
            for pathway_id in dict_smpdb_id_to_pathway_ids[identifier]:
                if (identifier, pathway_id) not in dict_db_pathway_pathway_to_how_mapped:
                    dict_db_pathway_pathway_to_how_mapped[(identifier, pathway_id)] = 'smpdb_id_mapped'
                    csv_mapping.writerow([identifier, pathway_id, pharmebinetutils.resource_add_and_prepare(
                        dict_pathway_id_to_resource[pathway_id], 'SMPDB'), 'smpdb_id_mapped',
                                          add_sources_to_xrefs_and_prepare_string(
                                              dict_pathway_id_to_xrefs[pathway_id],
                                              ['smpdb:' + identifier, 'pathwhiz:' + path_whiz_id])])
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
                    csv_mapping.writerow([identifier, pathway_id, pharmebinetutils.resource_add_and_prepare(
                        dict_pathway_id_to_resource[pathway_id], 'SMPDB'), 'name_mapped',
                                          add_sources_to_xrefs_and_prepare_string(
                                              dict_pathway_id_to_xrefs[pathway_id],
                                              ['smpdb:' + identifier, 'pathwhiz:' + path_whiz_id])])
                else:
                    print('multy mapping with name')
        if found_mapping:
            counter_mapped += 1
        else:
            counter_not_mapped += 1

            if name not in dict_new_pathway_name_to_pathway_ids:
                dict_new_pathway_name_to_pathway_ids[name] = [set(),set()]
            dict_new_pathway_name_to_pathway_ids[name][0].add('smpdb:'+identifier)
            dict_new_pathway_name_to_pathway_ids[name][0].add('pathwhiz:'+path_whiz_id)
            dict_new_pathway_name_to_pathway_ids[name][1].add( identifier)

    print('number of mapped node:', counter_mapped)
    print('number of not mapped node:', counter_not_mapped)


def new_pathway_add_to_file(csv_not_mapped):
    """
    Write the new pathways into a file
    :param csv_not_mapped: csv writer
    :return:
    """
    global highest_identifier
    for name, two_set_of_ids in dict_new_pathway_name_to_pathway_ids.items():
        xrefs = '|'.join(two_set_of_ids[0])
        highest_identifier += 1
        for identifier in two_set_of_ids[1]:
            csv_not_mapped.writerow([identifier, name, 'PC12_' + str(highest_identifier), xrefs])


def main():
    print(datetime.datetime.now())
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need path for smpdb pathway')

    path_of_directory = sys.argv[1]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pc from neo4j')

    load_pw_from_database()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping, csv_not_mapped = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pc from smpdb and map')

    load_all_smpdb_pw_and_map(csv_mapping)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Write new pathway nodes in file')

    new_pathway_add_to_file(csv_not_mapped)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
