import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary name to pc ids
dict_name_to_pathway_ids = {}

# dictionary_smpdb_id_to_pathway_ids
dict_smpdb_id_to_pathway_ids = {}

# dictionary metabolite_id to resource
dict_pathway_id_to_resource = {}


def load_pathway_from_database():
    """
    Load all pc into different mapping dictionaries
    :return:
    """
    query = '''Match (n:Pathway) Return n'''
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_pathway_id_to_resource[identifier] = set(node['resource'])
        name = node['name'] if 'name' in node else ''
        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pathway_ids, name.lower(), identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pathway_ids, synonym.lower(), identifier)

        for xref in node['xrefs']:
            if xref.startswith('smpdb'):
                smpdb_id = xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_smpdb_id_to_pathway_ids, smpdb_id, identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv writers
    """
    # file from relationship between gene and variant
    file_name = 'pathway/mapping_pathway.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    header = ['pathway_db_id', 'pathway_id', 'resource', 'how_mapped']
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    # not mapped file
    file_name_not = 'pathway/not_mapped_pathway.tsv'
    file_not = open(file_name_not, 'w', encoding='utf-8')
    header_not = ['pathway_db_id', 'name']
    csv_not_mapped = csv.writer(file_not, delimiter='\t')
    csv_not_mapped.writerow(header_not)

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = '''Match (n:Pathway{identifier:line.pathway_id}), (v:Pathway_DrugBank{identifier:line.pathway_db_id}) Create (n)-[r:equal_to_pathway_drugbank{how_mapped:line.how_mapped}]->(v) Set n.drugbank="yes", n.resource=split(line.resource,"|") '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()

    return csv_mapping, csv_not_mapped


# dictionary mapping db pathway and pathway to howmapped
dict_db_pathway_pathway_to_how_mapped = {}

# dictionary_smpdb_id_to_pathway_ids
dict_smpdb_id_from_db_to_pathway_ids = {}


def load_all_drugbank_pc_and_map(csv_mapping, csv_not_mapped):
    query = "MATCH (v:Pathway_DrugBank) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped = 0
    counter_not_mapped = 0

    for record in results:
        node = record.data()['v']
        identifier = node['identifier']
        name = node['name'].lower()
        found_mapping = False
        if identifier in dict_smpdb_id_to_pathway_ids:
            found_mapping = True
            dict_smpdb_id_from_db_to_pathway_ids[identifier] = dict_smpdb_id_to_pathway_ids[identifier]
            for pathway_id in dict_smpdb_id_to_pathway_ids[identifier]:
                if (identifier, pathway_id) not in dict_db_pathway_pathway_to_how_mapped:
                    dict_db_pathway_pathway_to_how_mapped[(identifier, pathway_id)] = 'smpdb_id'
                    csv_mapping.writerow(
                        [identifier, pathway_id,
                         pharmebinetutils.resource_add_and_prepare(dict_pathway_id_to_resource[pathway_id], 'DrugBank'),
                         'smpdb'])
                else:
                    print('multy mapping with smpdb id')

        if found_mapping:
            counter_mapped += 1
            continue

        if name in dict_name_to_pathway_ids:
            found_mapping = True
            dict_smpdb_id_from_db_to_pathway_ids[identifier] = dict_name_to_pathway_ids[name]
            for pathway_id in dict_name_to_pathway_ids[name]:
                if (identifier, pathway_id) not in dict_db_pathway_pathway_to_how_mapped:
                    dict_db_pathway_pathway_to_how_mapped[(identifier, pathway_id)] = 'name_mapped'
                    csv_mapping.writerow(
                        [identifier, pathway_id,
                         pharmebinetutils.resource_add_and_prepare(dict_pathway_id_to_resource[pathway_id], 'DrugBank'),
                         'name'])
                else:
                    print('multy mapping with name')
        if found_mapping:
            counter_mapped += 1
        else:
            counter_not_mapped += 1
            csv_not_mapped.writerow([identifier, name])
    print('number of mapped node:', counter_mapped)
    print('number of not mapped node:', counter_not_mapped)


def generate_edge_files():
    """
    Prepare pathway compound edge file and cypher query.
    :return: csv writer
    """
    file_name = 'pathway/edge_pathway_compound.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    header = ['pathway_id', 'compound_id']
    csv_edge = csv.writer(file, delimiter='\t')
    csv_edge.writerow(header)

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = '''Match (n:Pathway{identifier:line.pathway_id}), (v:Compound{identifier:line.compound_id}) Create (v)-[r:ASSOCIATES_CaPW{license:"%s", source:"DrugBank", drugbank:"yes", resource:["DrugBank"], url:"https://go.drugbank.com/drugs/"+line.compound_id}]->(n) '''
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()

    return csv_edge


def prepare_edges_to_compound():
    """
    Prepare compound-pathway file and cypher query
    :return:
    """
    query = '''Match (v:Pathway_DrugBank)--(m:Compound_DrugBank) Return v.identifier, m.identifier '''
    results = g.run(query)

    csv_edge = generate_edge_files()
    for record in results:
        [smpdb_id, compound_id] = record.values()
        if smpdb_id in dict_smpdb_id_from_db_to_pathway_ids:
            for pathway_id in dict_smpdb_id_from_db_to_pathway_ids[smpdb_id]:
                csv_edge.writerow([pathway_id, compound_id])


def main():
    print(datetime.datetime.now())
    global path_of_directory, license
    if len(sys.argv) < 3:
        sys.exit('need path anf license pathway drugbank')

    path_of_directory = sys.argv[2]
    license = sys.argv[1]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pathway from neo4j')

    load_pathway_from_database()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping, csv_not_mapped = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pathways from drugbank and map')

    load_all_drugbank_pc_and_map(csv_mapping, csv_not_mapped)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Prepare pathway-compound edge')

    prepare_edges_to_compound()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
