'''integrate the'''

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


# dictionary of name/synonym to chemical (not compound)
dict_name_to_chemical_id = {}

# dictionary chemical to resources
dict_chemical_to_resource = {}


def add_name_to_dict(name, identifier, dictionary):
    """
    add a name in  dictionary and check if it alerady included
    :param name: string
    :param identifier: string
    :return:
    """
    name = name.lower()
    if name not in dictionary:
        dictionary[name] = set()
    dictionary[name].add(identifier)


def load_all_chemicals_and_generate_dictionary():
    """
    load all chemicals which are also compounds (they are from drugbank and if the where targetes they had an own
     drugbank id, but it seems not so) and generate a dictionary of name to chemical id
    :return:
    """
    query = 'Match (c:Chemical) Return c.identifier, c.name, c.synonyms, c.resource;'
    result = g.run(query)
    for record in result:
        [chemical_id, name, synonyms, resources] = record.values()
        add_name_to_dict(name, chemical_id, dict_name_to_chemical_id)
        dict_chemical_to_resource[chemical_id] = resources
        if synonyms:
            for synonym in synonyms:
                add_name_to_dict(synonym, chemical_id, dict_name_to_chemical_id)


# dictionary pharmebinet protein with uniprot identifier as key and value is the whole node as dictionary
dict_pharmebinet_protein = {}

# dictionary name/synonym to protein id
dict_name_to_protein_id = {}

# dictionary protein id to resource
dict_protein_id_to_resource = {}

'''
gather all pharmebinet proteins in a dictionary
'''


def load_all_pharmebinet_proteins_in_dictionary():
    query = '''MATCH (n:Protein) RETURN n.identifier, n ;'''
    results = g.run(query)
    counter_multiple_identifier = 0
    for record in results:
        [identifier, node] = record.values()
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        dict_pharmebinet_protein[identifier] = [dict(node)]
        name = node['name'] if 'name' in node else ''
        synonyms = node['synonyms'] if 'synonyms' in node else []
        resource = node['resource']
        dict_protein_id_to_resource[identifier] = resource
        add_name_to_dict(name, identifier, dict_name_to_protein_id)
        for synonym in synonyms:
            add_name_to_dict(synonym, identifier, dict_name_to_protein_id)

        for alternative_id in alternative_ids:
            if not alternative_id in dict_pharmebinet_protein:
                dict_pharmebinet_protein[alternative_id] = [dict(node)]
            else:
                counter_multiple_identifier += 1
                dict_pharmebinet_protein[alternative_id].append(dict(node))
                # print(alternative_id)
                # print(dict_pharmebinet_protein[alternative_id])
                # print(node)
    print('number of identifier which appears multiple times:' + str(counter_multiple_identifier))


# dictionary of maybe protein or not (the drugbank proteins which has only a drugbank id and no components)
# currently 50 are proteins and 63 not, was manual checked
dict_be_identifier_sort_to_protein_or_not = {}

'''
load information about the proteins which are proteins or not from the target entities which has no uniprot id and are not connect with one with uniprot id.
This information where manual checked by me.
'''


def load_manual_checked_proteins_or_not():
    csv_file = open('protein/maybe_proteins_manual_checked.tsv', 'r')
    reader = csv.DictReader(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        identifier = row['identifier']
        is_protein = True if row['Protein_ja=1_und_nein=0'] == '1' else False
        dict_be_identifier_sort_to_protein_or_not[identifier] = is_protein
    # print(dict_be_identifier_sort_to_protein_or_not)


# file mapping target chemical
file_mapping_chemical = open('protein/mapping_chemical_target.tsv', 'w', encoding='utf-8')
csv_mapping_chemical = csv.writer(file_mapping_chemical, delimiter='\t')
csv_mapping_chemical.writerow(['chemical_id', 'id', 'resource'])


def check_if_not_mapped_proteins_migth_be_chemical_targets_or_protein(drugbank_id, name, synonyms, labels,
                                                                      dict_to_resource,
                                                                      write_mapping_file, dict_name_to_ids):
    """
    check if the name or synonyms are in the chemical dictionary and add pair to file
    :param drugbank_id: string
    :param name: string
    :param synonyms: list of strings
    :param labels: list of string
    :return: boolean
    """
    found_mapping = False
    synonyms.append(name)
    ids = set()
    for synonym in synonyms:
        synonym = synonym.lower()
        if synonym in dict_name_to_ids:
            ids = ids.union(dict_name_to_ids[synonym])

    if len(ids) > 0:
        found_mapping = True
        print('found chemical')
        print(name)
        print(ids)
        print(labels)
        # if not 'Target_DrugBank' in labels:
        #     sys.exit('not Target ')
        for identifier in ids:
            resource = set(dict_to_resource[identifier])
            resource.add('DrugBank')
            resource = sorted(resource)
            write_mapping_file.writerow([identifier, drugbank_id, "|".join(resource)])
    return found_mapping


# dictionary with all possible proteins
dict_proteins = {}

# list of all properties in drugbank proteins
list_of_all_properties_of_proteins = ["allfields", "locus", "synonyms", "pfams", "cellular_location", "go_classifiers",
                                      "amino_acid_sequence", "drugbank_id", "id_source", "molecular_weight",
                                      "gene_name", "license", "theoretical_pi", "name", "general_function", "xrefs",
                                      "gene_sequence", "identifier", "specific_function", "chromosome_location",
                                      "transmembrane_regions", "signal_regions"]

# generation of the tsv file for the different labels
generate_csv_carrier = open('protein/proteins_carrier.tsv', 'w')
writer_carrier = csv.writer(generate_csv_carrier, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_carrier.writerow(['id'])

generate_csv_enzyme = open('protein/proteins_enzyme.tsv', 'w')
writer_enzyme = csv.writer(generate_csv_enzyme, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_enzyme.writerow(['id'])

generate_csv_target = open('protein/proteins_target.tsv', 'w')
writer_target = csv.writer(generate_csv_target, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_target.writerow(['id'])

generate_csv_transporter = open('protein/proteins_transporter.tsv', 'w')
writer_transporter = csv.writer(generate_csv_transporter, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_transporter.writerow(['id'])

# dictionary of drugbank labels to pharmebinet labels:
dict_db_labels_to_tsv_label_file = {
    'Enzyme_DrugBank': writer_enzyme,
    'Transporter_DrugBank': writer_transporter,
    'Carrier_DrugBank': writer_carrier,
    'Target_DrugBank': writer_target}

# protein csv which should be updated
generate_csv = open('protein/proteins.tsv', 'w')
writer = csv.writer(generate_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['id', 'uniport', 'resource', 'sequences'])

'''
preparation of the tsv for merging for a given node
'''


def integrate_infos_into_tsv(part_dict, protein_pharmebinet, list_input_protein):
    # first check on the as sequences and combine the if they are not the same, because they are isoforms
    # or  have only small changes like one as is changed
    # print(protein_pharmebinet)
    resource = set(protein_pharmebinet['resource'])
    resource.add('DrugBank')
    resource = sorted(resource)
    list_input_protein.append("|".join(resource))

    as_seqs = part_dict['amino_acid_sequence'] if 'amino_acid_sequence' in part_dict else ''

    as_seq_pharmebinet = protein_pharmebinet['as_sequences'] if 'as_sequences' in protein_pharmebinet else []
    if ':' in as_seq_pharmebinet[0]:
        as_seq_pharmebinet_seq = as_seq_pharmebinet[0].split(':')[1]
    else:
        as_seq_pharmebinet_seq = as_seq_pharmebinet[0]
    list_as_sequnces = []
    list_as_sequnces.append(as_seq_pharmebinet_seq)
    # list_as_sequnces.extend(as_seq_pharmebinet_seq)
    for as_seq in as_seqs:

        if as_seq.startswith('>'):
            as_seq_part = as_seq.split(' ')[1]
        else:
            as_seq_part = as_seq.split(':')[1]
        if as_seq_part == '':
            print('empyt as')
            print(as_seq)
        if as_seq_pharmebinet_seq != as_seq_part and as_seq_part != '':
            list_as_sequnces.append(as_seq_part)
    # print(list_as_sequnces)
    list_as_sequnces = '|'.join(list_as_sequnces)
    list_input_protein.append(list_as_sequnces)

    # check on the pfams of both
    # to many were not correct and around 230 have to be checked
    # pfam_db= part_dict['pfams'] if 'pfams' in part_dict else []
    # pfam_db= [ x.replace('::',':') for x in pfam_db]
    # pfam_protein= protein_pharmebinet['pfam'] if 'pfam' in protein_pharmebinet else []
    # pfam_protein= set(pfam_protein)
    # #this were manual check pfams which were not correct
    # if identifier not in ['Q6NUM9','P07307','O94760','P63151','O95865']:
    #     length_before_union=len(pfam_protein)
    #     pfam_protein=pfam_protein.union(pfam_db)
    #     if len(pfam_protein)> length_before_union:
    #         print(identifier)
    #         print(pfam_db)
    #         print('not the same pfams')
    #
    # pfam_protein='|'.join(pfam_protein)
    # list_input_protein.append(pfam_protein)

    # check on gene names are the same
    # pharmebinet_gene_names=protein_pharmebinet['gene_name'] if 'gene_name' in protein_pharmebinet else []
    # db_gene_name=part_dict['gene_name'] if 'gene_name' in part_dict else ''
    # if not db_gene_name in pharmebinet_gene_names:
    #     print(part_dict['identifier'])
    #     print(pharmebinet_gene_names)
    #     print(db_gene_name)
    #     print('ohje gene name')

    writer.writerow(list_input_protein)


def not_mapped_proteins(node, identifier, name, synonyms, labels, counter_not_a_protein, writer_not_mapped,
                        counter_human_not_found):
    """
    check if the not mapped "proteins are might be chemical target and if not write into not mapped file
    :param node: dictionary
    :param identifier: string
    :param name: string
    :param synonyms: list of string
    :param labels: list of string
    :param counter_not_a_protein: int
    :param writer_not_mapped: csv Dictionary writer
    :return:
    """
    drugbank_id = node['drugbank_id']
    found_chemical_map = False
    found_protein = False

    if node['organism'] == 'Humans':
        counter_human_not_found += 1
    if identifier == drugbank_id:
        found_chemical_map = check_if_not_mapped_proteins_migth_be_chemical_targets_or_protein(identifier, name,
                                                                                               synonyms, labels,
                                                                                               dict_chemical_to_resource,
                                                                                               csv_mapping_chemical,
                                                                                               dict_name_to_chemical_id)
        found_protein = check_if_not_mapped_proteins_migth_be_chemical_targets_or_protein(identifier, name,
                                                                                          synonyms, labels,
                                                                                          dict_protein_id_to_resource,
                                                                                          writer,
                                                                                          dict_name_to_protein_id)
        print('did a chemical map?')
    counter_not_a_protein += 1
    if not found_chemical_map and not found_protein:
        writer_not_mapped.writerow(dict(node))
    return counter_not_a_protein


'''
load all possible proteins from Drugbank and put only all as protein defined proteins into a dictionary
'''


def load_proteins_from_drugbank_into_dict():
    # conncet the
    cypherfile = open('protein/cypher_protein.cypher', 'w')
    # this is only for the first time to have only the sequences as property and not with header
    # query = '''Match (n:Protein) Where exists(n.as_sequence) Set n.as_sequence=split(n.as_sequence,':')[1]'''
    # cypherfile.write(query)

    query = ''' MATCH (n:Protein_DrugBank{identifier:line.id}) ,(p:Protein{identifier:line.uniport}) Create (p)-[:equal_to_DB_protein]->(n) Set p.drugbank='yes', p.resource=split(line.resource,"|"), p.locus=n.locus, p.molecular_weight=n.molecular_weight, p.as_sequences=split(line.sequences,'|'),p.pfams=split(line.pfams,'|') '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/proteins.tsv',
                                              query)
    cypherfile.write(query)
    query = ''' MATCH (n:Protein_DrugBank{identifier:line.id}) ,(p:Chemical{identifier:line.chemical_id}) Create (p)-[:equal_to_DB_target]->(n) Set p.drugbank='yes', p:Target, p.resource=split(line.resource,"|") '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/mapping_chemical_target.tsv',
                                              query)
    cypherfile.write(query)
    # all queries which are used to integrate Protein with the extra labels into pharmebinet
    query = ''' MATCH (g:Protein{identifier:line.id}) Set g:Carrier '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/proteins_carrier.tsv',
                                              query)
    cypherfile.write(query)
    query = ''' MATCH (g:Protein{identifier:line.id}) Set g:Enzyme '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/proteins_enzyme.tsv',
                                              query)
    cypherfile.write(query)
    query = ''' MATCH (g:Protein{identifier:line.id}) Set g:Target '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/proteins_target.tsv',
                                              query)
    cypherfile.write(query)
    query = ''' MATCH (g:Protein{identifier:line.id}) Set g:Transporter '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/proteins_transporter.tsv',
                                              query)
    cypherfile.write(query)
    cypherfile.close()

    file_uniprots_with_multiple = open('protein/uniprot_gene/db_uniprot_to_multi_genes.tsv', 'w')
    writer_multi = csv.writer(file_uniprots_with_multiple, delimiter='\t')
    writer_multi.writerow(['uniprot_id', 'protein_name', 'genes', 'alternative_ids'])

    file_uniprots_without_rela = open('protein/uniprot_gene/db_uniprot_without_rela.tsv', 'w')
    writer_without_rela = csv.writer(file_uniprots_without_rela, delimiter='\t')
    writer_without_rela.writerow(['uniprot_id', 'name'])

    file_uniprots_gene_with_alternative = open('protein/uniprot_gene/db_uniprot_to_gene_with_alternative.tsv', 'w')
    writer_rela_with_alternative = csv.writer(file_uniprots_gene_with_alternative, delimiter='\t')
    writer_rela_with_alternative.writerow(['uniprot_id', 'alternative id', 'gene(s)'])

    header_not_mapped = ["gene_name", "pfams", "synonyms", "id_source", "amino_acid_sequence", "gene_sequence",
                         "chromosome_location", "xrefs", "cellular_location", "theoretical_pi", "signal_regions",
                         "molecular_weight", "general_function", "specific_function", "locus", "go_classifiers",
                         "license", "drugbank_id", "name", "identifier", "organism", "transmembrane_regions",
                         "alternative_uniprot_id"]
    file_not_mapped = open('protein/not_mapped.tsv', 'w')
    writer_not_mapped = csv.DictWriter(file_not_mapped, fieldnames=header_not_mapped, delimiter='\t')
    writer_not_mapped.writeheader()

    query = '''MATCH (n:Protein_DrugBank) RETURN n, labels(n) ;'''
    results = g.run(query)
    counter_not_a_protein = 0
    counter_proteins_in_total = 0
    counter_mapped = 0
    counter_human_not_found = 0

    counter_uniprot_with_no_gene_ids = 0
    for record in results:
        [node, labels] = record.values()
        counter_proteins_in_total += 1

        # input list for protein
        list_input_protein = []

        identifier = node['identifier']
        alternative_uniprot_ids = node['alternative_uniprot_id'] if 'alternative_uniprot_id' in node else []
        name = node['name'] if 'name' in node else ''
        synonyms = node['synonyms'] if 'synonyms' in node else []

        if not identifier in dict_be_identifier_sort_to_protein_or_not or dict_be_identifier_sort_to_protein_or_not[
            identifier]:

            list_input_protein.append(identifier)

            part_dict = dict(node)
            part_dict['labels'] = labels

            labels.remove('Protein_DrugBank')
            for label in labels:
                dict_db_labels_to_tsv_label_file[label].writerow([identifier])
            dict_proteins[identifier] = labels

            if identifier in dict_pharmebinet_protein:
                counter_mapped += 1
                if len(dict_pharmebinet_protein[identifier]) == 1:
                    protein_pharmebinet = dict_pharmebinet_protein[identifier][0]
                    list_input_protein.append(protein_pharmebinet['identifier'])

                    integrate_infos_into_tsv(part_dict, protein_pharmebinet, list_input_protein)

                else:
                    print(len(dict_pharmebinet_protein[identifier]))
                    print(identifier)
                    for protein_pharmebinet in dict_pharmebinet_protein[identifier]:
                        list_multiple_input = []
                        list_multiple_input.append(identifier)
                        list_multiple_input.append(protein_pharmebinet['identifier'])
                        print(protein_pharmebinet['identifier'])
                        integrate_infos_into_tsv(part_dict, protein_pharmebinet, list_multiple_input)
                    print('multiple mapping')
            elif identifier in dict_be_identifier_sort_to_protein_or_not:
                print('protein without uniprot id')
                counter_not_a_protein += 1
                print(node['name'])
                writer_not_mapped.writerow(dict(node))
                if node['organism'] == 'Humans':
                    counter_human_not_found += 1

                drugbank_id = node['drugbank_id']
                # if identifier == drugbank_id:
                #     print('do something different protein')
                # print(node)

            else:
                counter_not_a_protein = not_mapped_proteins(node, identifier, name, synonyms, labels,
                                                            counter_not_a_protein, writer_not_mapped,
                                                            counter_human_not_found)


        else:
            counter_not_a_protein = not_mapped_proteins(node, identifier, name, synonyms, labels, counter_not_a_protein,
                                                        writer_not_mapped,
                                                        counter_human_not_found)

    # print(dict_proteins)
    print('number of human proteins:' + str(counter_mapped))
    print('number of not proteins or not human or not reviewed:' + str(counter_not_a_protein))
    print('counter of not protein which were human:' + str(counter_human_not_found))
    print('nummer of all proteins in drugbank:' + str(counter_proteins_in_total))
    print('number of proteins without gene id:' + str(counter_uniprot_with_no_gene_ids))


# file for all rela which should be integrated
cypher_rela = open('protein/cypher_protein_rela.cypher', 'w')

'''
Generate tsv with component relationships
'''


def generate_tsv_componet_rela():
    query = 'MATCH p=(a:Protein_DrugBank)-[r:has_component_PIhcPI]->(b:Protein_DrugBank) RETURN a.identifier, b.identifier'
    result = g.run(query)

    query = ''' MATCH (g:Protein{identifier:line.id1}),(b:Protein{identifier:line.id2}) Create (g)-[:HAS_COMPONENT_PRhcPR]->(b)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/protein/proteins_rela_component.tsv',
                                              query)
    cypher_rela.write(query)

    csv_file = open('protein/proteins_rela_component.tsv', 'w')
    writer_csv = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer_csv.writerow(['id1', 'id2'])

    counter_component_rela = 0
    for record in result:
        [identifier1, identifier2] = record.values()
        print(identifier1)
        counter_component_rela += 1
        writer_csv.writerow([identifier1, identifier2])

    print('number of component rela:' + str(counter_component_rela))


def main():
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need license and path')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all chemicals in a dictionary name to chemical id')

    load_all_chemicals_and_generate_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all information to the nodes where I was not sure if they are protein or not')

    load_manual_checked_proteins_or_not()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('load all Protein and gather the information ')

    load_all_pharmebinet_proteins_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('load all DrugBank proteins in dictionary')

    load_proteins_from_drugbank_into_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('load all DrugBank has component rela and write them in tsv and generate cypher file for integration')

    generate_tsv_componet_rela()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
