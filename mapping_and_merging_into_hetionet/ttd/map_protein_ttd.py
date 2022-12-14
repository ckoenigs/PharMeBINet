import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary
dict_protein_name_ids = {}
dict_proteinId_to_resource = {}
dict_protein_uniProt_to_id = {}


def load_protein_in():
    """
    Load Protein information from PharMeBINet
    :return:
    """
    # query ist ein String
    query = '''MATCH (n:Protein) RETURN n'''
    results = graph_database.run(query)

    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        prot_name = node["name"].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_ids, prot_name, identifier)
        uniProt = node["entry_name"]

        xrefs = node['xrefs'] if "xrefs" in node else []

        synonyms = node["synonyms"] if "synonyms" in node else []
        dict_proteinId_to_resource[identifier] = resource

        dict_protein_uniProt_to_id[uniProt] = identifier
        # synonyms
        for name in synonyms:
            name = name.lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_protein_name_ids, name, identifier)


# dictionary gene_symbol to protein ids
dict_gene_symbol_to_protein_ids = {}


def load_gene_to_protein_ids():
    """
    Prepare mapping with gene symbol to protein ids
    :return:
    """
    query = "MATCH (r:Gene)--(n:Protein) RETURN r.gene_symbol,n.identifier"
    results = graph_database.run(query)
    for gene_symbol, protein_id, in results:
        pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_protein_ids, gene_symbol, protein_id)


def load_and_map_ttd_protein(csv_mapped, csv_not_mapped):
    query = '''MATCH (n:TTD_Target) RETURN n.id, n.name, n.synonyms, n.uniprot_id, n.gene_name  '''
    results = graph_database.run(query)

    counter = 0
    counter_mapped = 0
    for node_id, name, synonyms, uniprot_accssion, gene_name, in results:
        counter += 1

        found_mapping = False


        if gene_name in dict_gene_symbol_to_protein_ids:
            counter_mapped+=1
            found_mapping=True
            for protein_id in dict_gene_symbol_to_protein_ids[gene_name]:
                csv_mapped.writerow([node_id, protein_id,
                                     pharmebinetutils.resource_add_and_prepare(dict_proteinId_to_resource[protein_id],
                                                                               'TTD'), 'gene_symbol'])
        if found_mapping:
            continue

        if name is not None:
            name=name.lower()
            name=name.rsplit(' (',1)[0]
            if name in dict_protein_name_ids:
                counter_mapped+=1
                found_mapping=True
                for protein_id in dict_protein_name_ids[name]:
                    csv_mapped.writerow([node_id, protein_id,
                                         pharmebinetutils.resource_add_and_prepare(dict_proteinId_to_resource[protein_id],
                                                                               'TTD'), 'name'])
        if found_mapping:
            continue


        if uniprot_accssion in dict_protein_uniProt_to_id:
            counter_mapped += 1
            found_mapping = True
            protein_id = dict_protein_uniProt_to_id[uniprot_accssion]
            csv_mapped.writerow([node_id, protein_id,
                                 pharmebinetutils.resource_add_and_prepare(dict_proteinId_to_resource[protein_id],
                                                                           'TTD'), 'uniprot_accession'])

        if found_mapping:
            continue

        if synonyms is not None:
            for synonym in synonyms:
                if synonym in dict_protein_name_ids:
                    counter_mapped += 1
                    found_mapping = True
                    for protein_id in dict_protein_name_ids[synonym]:
                        csv_mapped.writerow([node_id, protein_id,
                                             pharmebinetutils.resource_add_and_prepare(
                                                 dict_proteinId_to_resource[protein_id],
                                                 'TTD'), 'synonym'])
        if found_mapping:
            continue
            
        csv_not_mapped.writerow([node_id, uniprot_accssion, name])
    print('number of mapped nodes:', counter_mapped)
    print('number of nodes:', counter)


def generate_cypher_file(file_nameProtein):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')

    query_Protein = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/ttd/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:TTD_Target{id:line.node_id}), (c:Protein{identifier:line.id_pharmebinet})  Set c.ttd='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_protein_ttd{how_mapped:line.how_mapped}]->(n); \n'''
    query_Protein = query_Protein % (path_of_directory, file_nameProtein)
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
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())
    print("load protein in")
    load_protein_in()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())
    print("load gene to protein")
    load_gene_to_protein_ids()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())
    print("create tsv and cypher files")
    csv_mapped, csv_not_mapped = create_tsv_and_cypher_query()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())
    print("load and map ttd protein")
    load_and_map_ttd_protein(csv_mapped, csv_not_mapped)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
