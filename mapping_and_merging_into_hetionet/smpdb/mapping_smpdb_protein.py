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
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary protein id to resource
dict_protein_id_to_resource = {}

# dictionary alternative protein id to ids
dict_alt_id_to_id = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_protein_from_database_and_add_to_dict():
    query = "MATCH (n:Protein) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_protein_id_to_resource[identifier] = node['resource']
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for alternative_id in alternative_ids:
            if alternative_id not in dict_alt_id_to_id:
                dict_alt_id_to_id[alternative_id] = set()
            dict_alt_id_to_id[alternative_id].add(identifier)
    print('number of proteins:', len(dict_protein_id_to_resource))


# dictionary compound id to name and resource
dict_compound_id_to_name = {}


def load_compound_from_database_and_add_to_dict():
    """
    Load all compound data for mapping to drugbank.
    :return:
    """
    query = "MATCH (n:Compound) RETURN n.identifier, n.name, n.resource"
    results = g.run(query)
    for record in results:
        [identifier, name, resource] = record.values()
        dict_compound_id_to_name[identifier] = {'name': name, 'resource': resource}
    print('number of compound:', len(dict_compound_id_to_name))


def generate_files(path_of_directory, label):
    """
    generate cypher file and tsv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'protein/smpdb_protein_to_%s' % label
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['identifier', 'other_id', 'resource', 'mapped_with']
    csv_mapping.writerow(header)

    query = ''' Match (n:protein_smpdb{identifier:line.identifier}), (v:%s{identifier:line.other_id}) Set v.smpdb='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_smpdb_%s{how_mapped:line.mapped_with}]->(n)'''
    query = query % (label, label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/smpdb/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return csv_mapping


def resource(resource):
    resource = set(resource)
    resource.add('SMPDB')
    return '|'.join(resource)


'''
Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
'''


def load_all_smpdb_protein_and_finish_the_files(csv_mapping_protein, csv_mapping_compound):
    query = "MATCH (n:protein_smpdb) RETURN n"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['identifier']
        uniprot_id = node['uniprot_id'] if 'uniprot_id' in node else ''
        drugbank_id = node['drugbank_id'] if 'drugbank_id' in node else ''
        if uniprot_id != '':
            if uniprot_id in dict_protein_id_to_resource:
                csv_mapping_protein.writerow(
                    [identifier, uniprot_id, resource(dict_protein_id_to_resource[uniprot_id]), 'id'])
            elif uniprot_id in dict_alt_id_to_id:
                for protein_id in dict_alt_id_to_id[uniprot_id]:
                    csv_mapping_protein.writerow(
                        [identifier, protein_id, resource(dict_protein_id_to_resource[protein_id]), 'alternative id'])
            else:
                counter_not_mapped += 1
                print(identifier)
        elif drugbank_id != '':
            if identifier in dict_compound_id_to_name:
                csv_mapping_compound.writerow(
                    [identifier, drugbank_id, resource(dict_compound_id_to_name[identifier]['resource']), 'id'])
            else:
                counter_not_mapped += 1
        else:
            counter_not_mapped += 1
    print('number of not mapped proteins:', counter_not_mapped)
    print('number of all proteins:', counter_all)


def main():
    print(datetime.datetime.now())

    global path_of_directory, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path smpdb protein')

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Protein from database')

    load_protein_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Compound from database')

    load_compound_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping_protein = generate_files(path_of_directory, 'Protein')
    csv_mapping_compound = generate_files(path_of_directory, 'Compound')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all smpdb protein from database')

    load_all_smpdb_protein_and_finish_the_files(csv_mapping_protein, csv_mapping_compound)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
