import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary name to protein ids
dict_protein_name_ids = {}
# dictionary protein id to resource
dict_proteinId_to_resource = {}
# dictionary uniprot entry name to ids
dict_protein_uniProt_to_id = {}
# dictionary protein sequence to ids
dict_seq_to_ids = {}


def load_protein_in():
    """
    Load Protein information from PharMeBINet
    :return:
    """
    # query ist ein String
    query = '''MATCH (n:Protein) RETURN n'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        prot_name = node["name"].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_ids, prot_name, identifier)
        uniProt = node["entry_name"]
        sequences = node["as_sequences"] if 'as_sequences' in node else []
        for seq in sequences:

            # multiple proteins have the same sequence :O
            # if seq in dict_seq_to_ids:
            #     print('ohje')
            #     print(dict_seq_to_ids[seq])
            #     print(identifier)
            if not seq in dict_seq_to_ids:
                dict_seq_to_ids[seq] = set()

            dict_seq_to_ids[seq].add(identifier)

        dict_proteinId_to_resource[identifier] = resource

        dict_protein_uniProt_to_id[uniProt] = identifier
        # synonyms
        # for name in synonyms:
        #     name = name.lower()
        #     pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_ids, name, identifier)


# dictionary gene_symbol to protein ids
dict_gene_symbol_to_protein_ids = {}


def load_gene_to_protein_ids():
    """
    Prepare mapping with gene symbol to protein ids
    :return:
    """
    query = "MATCH (r:Gene)--(n:Protein) RETURN r.gene_symbol,n.identifier"
    results = graph_database.run(query)
    for record in results:
        [gene_symbol, protein_id] = record.values()
        pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_protein_ids, gene_symbol, protein_id)


def load_and_map_ttd_protein(csv_mapped, csv_not_mapped):
    """
    Load all TTD target and map them with uniprot accession, name and gene symbol. Write all mapped into a TSV file.
    :param csv_mapped:
    :param csv_not_mapped:
    :return:
    """
    query = '''MATCH (n:TTD_Target) RETURN n.id, n.name,  n.uniprot_ids, n.gene_names, n.sequence  '''
    results = graph_database.run(query)

    counter = 0
    counter_mapped = 0
    for record in results:
        [node_id, name, uniprot_accssions, gene_names, sequence] = record.values()
        counter += 1

        found_mapping = False

        if uniprot_accssions:
            if len(uniprot_accssions) == 1:
                uniprot_accssion = uniprot_accssions[0]
                if uniprot_accssion in dict_protein_uniProt_to_id:
                    counter_mapped += 1
                    found_mapping = True
                    protein_id = dict_protein_uniProt_to_id[uniprot_accssion]
                    csv_mapped.writerow([node_id, protein_id,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_proteinId_to_resource[protein_id],
                                             'TTD'), 'uniprot_accession'])

        if found_mapping:
            continue

        if name is not None:
            name = name.lower()
            name = name.rsplit(' (', 1)[0]
            if name in dict_protein_name_ids:
                counter_mapped += 1
                found_mapping = True
                for protein_id in dict_protein_name_ids[name]:
                    csv_mapped.writerow([node_id, protein_id,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_proteinId_to_resource[protein_id],
                                             'TTD'), 'name'])
        if found_mapping:
            continue

        if gene_names:
            if len(gene_names) == 1:
                gene_name = gene_names[0]
                if gene_name in dict_gene_symbol_to_protein_ids:
                    counter_mapped += 1
                    found_mapping = True
                    for protein_id in dict_gene_symbol_to_protein_ids[gene_name]:
                        csv_mapped.writerow([node_id, protein_id,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_proteinId_to_resource[protein_id],
                                                 'TTD'), 'gene_symbol'])
        if found_mapping:
            continue

        # the sequences are not specific
        # if sequence in dict_seq_to_ids:
        #     counter_mapped += 1
        #     found_mapping = True
        #     for protein_id in dict_seq_to_ids[sequence]:
        #         csv_mapped.writerow([node_id, protein_id,
        #                              pharmebinetutils.resource_add_and_prepare(dict_proteinId_to_resource[protein_id],
        #                                                                        'TTD'), 'sequences'])
        # if found_mapping:
        #     continue

        csv_not_mapped.writerow([node_id, uniprot_accssions, name])
    print('number of mapped nodes:', counter_mapped)
    print('number of nodes:', counter)


def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w')

    query_Protein = ''' MATCH (n:TTD_Target{id:line.node_id}), (c:Protein{identifier:line.id_pharmebinet})  Set c.ttd='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_protein_ttd{how_mapped:line.how_mapped}]->(n)'''
    query_Protein = pharmebinetutils.get_query_import(path_of_directory,
                                                      f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                                      query_Protein)
    cypher_file.write(query_Protein)

    cypher_file.close()


def create_tsv_and_cypher_query():
    """
    Create not mapped and mapped tsv files and return the csv writer
    :return:
    """
    file_not_mapped_protein = open('protein/not_mapped_protein.tsv', 'w', encoding="utf-8")
    csv_not_mapped = csv.writer(file_not_mapped_protein, delimiter='\t', lineterminator='\n')
    csv_not_mapped.writerow(['id', 'accession_number', 'name'])

    file_name = 'protein/mapped_protein.tsv'
    file_mapped_protein = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_protein, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['node_id', 'id_pharmebinet', 'resource', 'how_mapped'])
    generate_cypher_file(file_name)
    return csv_mapped, csv_not_mapped


def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd protein')
    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("load protein in")
    load_protein_in()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("load gene to protein")
    load_gene_to_protein_ids()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("create tsv and cypher files")
    csv_mapped, csv_not_mapped = create_tsv_and_cypher_query()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())
    print("load and map ttd protein")
    load_and_map_ttd_protein(csv_mapped, csv_not_mapped)

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
