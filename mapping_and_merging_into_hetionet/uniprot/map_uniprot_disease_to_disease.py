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
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary omim to disease
dict_omim_to_disease_ids = {}

# dictionary name and synonym to disease ids
dict_name_to_disease_ids = {}

# dictionary disease id to resource
dict_id_to_resource = {}

# dictionary disease id to set of name and synonyms
dict_disease_id_to_set_of_name_and_synonyms = {}


def load_all_disease_information():
    """
    get the important information for disease into the different dictionaries
    :return:
    """
    query = 'Match (n:Disease) Return n'
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        resource = node['resource']
        dict_id_to_resource[identifier] = resource
        xrefs = node['xrefs'] if 'xrefs' in node else []
        name = node['name'].lower()
        dict_disease_id_to_set_of_name_and_synonyms[identifier] = {name}
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_disease_ids, name, identifier)

        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
            dict_disease_id_to_set_of_name_and_synonyms[identifier].add(synonym)
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_disease_ids, synonym, identifier)

        for xref in xrefs:
            if xref.startswith('OMIM'):
                omim_id = xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_omim_to_disease_ids, omim_id, identifier)
    # print(dict_omim_to_disease_ids)


def write_pair_into_file(disease_id, identifier, csv_disease, how_mapped):
    """
    write  mapping pair in TSV file
    :param disease_id:
    :param identifier:
    :param csv_disease:
    :param how_mapped:
    :return:
    """
    resource = set(dict_id_to_resource[disease_id])
    csv_disease.writerow(
        [identifier, disease_id, pharmebinetutils.resource_add_and_prepare(resource, 'UniProt'), how_mapped])


def gather_uniprot_disease_infos_and_add_to_file():
    """
    Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
    """
    # generate a file with all uniprots to
    file_name = 'uniprot_disease/mapping_disease.tsv'
    file_gene_disease = open(file_name, 'w')
    csv_disease = csv.writer(file_gene_disease, delimiter='\t')
    csv_disease.writerow(['uniprot_disease_id', 'disease_id', 'resource', 'how_mapped'])
    # csv_gene_disease.writerow(['gene_ids', 'disease_id','source','note','resource'])

    # query gene-disease association

    file_cypher = open('output/cypher.cypher', 'a')
    query = '''MATCH (g:Disease_Uniprot{identifier:line.uniprot_disease_id}),(b:Disease{identifier:line.disease_id}) Create (b)-[r:equal_to_uniprot_disease{how_mapped:line.how_mapped}]->(g) Set b.resource=split(line.resource,"|"), b.uniprot='yes' '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/uniprot/{file_name}',
                                              query)
    file_cypher.write(query)

    query = """Match (n:Disease_Uniprot) Return n """
    results = g.run(query)

    counter_all = 0
    counter_mapped = 0
    for record in results:
        node = record.data()['n']
        counter_all += 1
        identifier = node['identifier']
        xrefs = node['xrefs']
        name = node['name'].lower()

        has_mapped = False
        disease_ids_with_similar_name = set()
        for xref in xrefs:
            if xref.startswith('MIM'):
                xref = xref.split(':')[1]
                if xref in dict_omim_to_disease_ids:
                    counter_mapped += 1
                    has_mapped = True
                    omim_disease_ids = dict_omim_to_disease_ids[xref]
                    # if len(omim_disease_ids)>1:
                    #     print('ohje')
                    #     print(xref)
                    for disease_id in omim_disease_ids:
                        if name in dict_disease_id_to_set_of_name_and_synonyms[disease_id]:
                            disease_ids_with_similar_name.add(disease_id)

                    if len(disease_ids_with_similar_name) > 0:
                        for disease_id in disease_ids_with_similar_name:
                            write_pair_into_file(disease_id, identifier, csv_disease, 'omim_id_name')
                    else:
                        for disease_id in omim_disease_ids:
                            write_pair_into_file(disease_id, identifier, csv_disease, 'omim_id')

                # else:
                #     print(identifier)
                #     print(node)
                #     print(xref)
        if has_mapped:
            continue

        if name in dict_name_to_disease_ids:
            counter_mapped += 1
            for disease_id in disease_ids_with_similar_name:
                write_pair_into_file(disease_id, identifier, csv_disease, 'name')


    print('number of mapped diseases:', counter_mapped)
    print('number of all diseases:', counter_all)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gather all information of the pharmebinet disease')

    load_all_disease_information()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gather all information of the proteins')

    gather_uniprot_disease_infos_and_add_to_file()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
