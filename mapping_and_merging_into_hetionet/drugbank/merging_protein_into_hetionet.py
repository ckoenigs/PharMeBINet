'''integrate the'''
from py2neo import Graph
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# dictionary hetionet protein with uniprot identifier as key and value is the whole node as dictionary
dict_hetionet_protein = {}

'''
gather all hetionet proteins in a dictionary
'''


def load_all_hetionet_proteins_in_dictionary():
    query = '''MATCH (n:Protein) RETURN n.identifier, n ;'''
    results = g.run(query)
    counter_multiple_identifier = 0
    for identifier, node, in results:
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        dict_hetionet_protein[identifier] = [dict(node)]
        for alternative_id in alternative_ids:
            if not alternative_id in dict_hetionet_protein:
                dict_hetionet_protein[alternative_id] = [dict(node)]
            else:
                counter_multiple_identifier += 1
                dict_hetionet_protein[alternative_id].append(dict(node))
                # print(alternative_id)
                # print(dict_hetionet_protein[alternative_id])
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
    csv_file = open('protein/maybe_proteins_manual_checked.tsv.csv', 'r')
    reader = csv.DictReader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        identifier = row['identifier']
        is_protein = True if row['Protein_ja=1_und_nein=0'] == '1' else False
        dict_be_identifier_sort_to_protein_or_not[identifier] = is_protein
    # print(dict_be_identifier_sort_to_protein_or_not)


# dictionary with all possible proteins
dict_proteins = {}

# list of all properties in drugbank proteins
list_of_all_properties_of_proteins = ["allfields", "locus", "synonyms", "pfams", "cellular_location", "go_classifiers",
                                      "amino_acid_sequence", "drugbank_id", "id_source", "molecular_weight",
                                      "gene_name", "license", "theoretical_pi", "name", "general_function", "xrefs",
                                      "gene_sequence", "identifier", "specific_function", "chromosome_location",
                                      "transmembrane_regions", "signal_regions"]

# generation of the csv file for the different labels
generate_csv_carrier = open('protein/proteins_carrier.csv', 'w')
writer_carrier = csv.writer(generate_csv_carrier, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_carrier.writerow(['id'])

generate_csv_enzyme = open('protein/proteins_enzyme.csv', 'w')
writer_enzyme = csv.writer(generate_csv_enzyme, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_enzyme.writerow(['id'])

generate_csv_target = open('protein/proteins_target.csv', 'w')
writer_target = csv.writer(generate_csv_target, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_target.writerow(['id'])

generate_csv_transporter = open('protein/proteins_transporter.csv', 'w')
writer_transporter = csv.writer(generate_csv_transporter, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer_transporter.writerow(['id'])

# dictionary of Durgbank labels to hetionet labels:
dict_db_labels_to_csv_label_file = {
    'Enzyme_DrugBank': writer_enzyme,
    'Transporter_DrugBank': writer_transporter,
    'Carrier_DrugBank': writer_carrier,
    'Target_DrugBank': writer_target}

# protein csv which should be updated
generate_csv = open('protein/proteins.csv', 'w')
writer = csv.writer(generate_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['id', 'uniport', 'sequences'])

'''
preparation of the csv for merging for a given node
'''


def interagte_infos_into_csv(part_dict, protein_hetionet, list_input_protein):
    # first check on the as sequences and combine the if they are not the same, because they are isoforms
    # or  have only small changes like one as is changed
    as_seqs = part_dict['amino_acid_sequence'] if 'amino_acid_sequence' in part_dict else ''

    as_seq_hetionet = protein_hetionet['as_sequence'] if 'as_sequence' in protein_hetionet else ''
    if ':' in as_seq_hetionet:
        as_seq_hetionet_seq = as_seq_hetionet.split(':')[1]
    else:
        as_seq_hetionet_seq = as_seq_hetionet
    list_as_sequnces = []
    list_as_sequnces.append(as_seq_hetionet_seq)
    for as_seq in as_seqs:

        as_seq_part = as_seq.split(' ')[1]
        if as_seq_hetionet_seq != as_seq_part:
            list_as_sequnces.append(as_seq_part)

    list_as_sequnces = '|'.join(list_as_sequnces)
    list_input_protein.append(list_as_sequnces)

    # check on the pfams of both
    # to many were not correct and around 230 have to be checked
    # pfam_db= part_dict['pfams'] if 'pfams' in part_dict else []
    # pfam_db= [ x.replace('::',':') for x in pfam_db]
    # pfam_protein= protein_hetionet['pfam'] if 'pfam' in protein_hetionet else []
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
    # hetionet_gene_names=protein_hetionet['gene_name'] if 'gene_name' in protein_hetionet else []
    # db_gene_name=part_dict['gene_name'] if 'gene_name' in part_dict else ''
    # if not db_gene_name in hetionet_gene_names:
    #     print(part_dict['identifier'])
    #     print(hetionet_gene_names)
    #     print(db_gene_name)
    #     print('ohje gene name')

    writer.writerow(list_input_protein)


'''
load all possible proteins from Drugbank and put only all as protein defined proteins into a dictionary
'''


def load_proteins_from_drugbank_into_dict():
    # conncet the
    cypherfile = open('protein/cypher_protein.cypher', 'w')
    # this is only for the first time to have only the sequences as property and not with header
    query = '''Match (n:Protein) Where exists(n.as_sequence) Set n.as_sequence=split(n.as_sequence,':')[1];\n'''
    cypherfile.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Documents/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins.csv" As line MATCH (n:Protein_DrugBank{identifier:line.id}) ,(p:Protein{identifier:line.uniport}) Create (p)-[:equal_to_DB_protein]->(n) Set p.drugbank='yes', p.resource=p.resource+ 'DrugBank', p.locus=n.locus, p.molecular_weight=n.molecular_weight, p.as_sequence=split(line.sequences,'|'),p.pfams=split(line.pfams,'|') ;\n'''

    cypherfile.write(query)
    # all queries which are used to integrate Protein with the extra labels into Hetionet
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Documents/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_carrier.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Carrier ;\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Documents/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_enzyme.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Enzyme ;\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Documents/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_target.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Target ;\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Documents/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_transporter.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Transporter ;\n'''
    cypherfile.write(query)
    query = 'Create Constraint On (node:Protein) Assert node.identifier Is Unique; \n'
    cypherfile.write(query)
    cypherfile.close()

    file_uniprots_with_multiple = open('protein/uniprot_gene/db_uniprot_to_multi_genes.csv', 'w')
    writer_multi = csv.writer(file_uniprots_with_multiple)
    writer_multi.writerow(['uniprot_id', 'protein_name', 'genes', 'alternative_ids'])

    file_uniprots_without_rela = open('protein/uniprot_gene/db_uniprot_without_rela.csv', 'w')
    writer_without_rela = csv.writer(file_uniprots_without_rela)
    writer_without_rela.writerow(['uniprot_id', 'name'])

    file_uniprots_gene_with_alternative = open('protein/uniprot_gene/db_uniprot_to_gene_with_alternative.csv', 'w')
    writer_rela_with_alternative = csv.writer(file_uniprots_gene_with_alternative)
    writer_rela_with_alternative.writerow(['uniprot_id', 'alternative id', 'gene(s)'])

    header_not_mapped = ["gene_name", "pfams", "synonyms", "id_source", "amino_acid_sequence", "gene_sequence",
                         "chromosome_location", "xrefs", "cellular_location", "theoretical_pi", "signal_regions",
                         "molecular_weight", "general_function", "specific_function", "locus", "go_classifiers",
                         "license", "drugbank_id", "name", "identifier", "organism", "transmembrane_regions"]
    file_not_mapped= open('protein/not_mapped.tsv','w')
    writer_not_mapped=csv.DictWriter(file_not_mapped, fieldnames=header_not_mapped, delimiter='\t')
    writer_not_mapped.writeheader()

    query = '''MATCH (n:Protein_DrugBank) RETURN n, labels(n) ;'''
    results = g.run(query)
    counter_not_a_protein = 0
    counter_proteins_in_total = 0
    counter_mapped = 0
    counter_human_not_found = 0

    counter_uniprot_with_no_gene_ids = 0
    for node, labels, in results:
        counter_proteins_in_total += 1

        # input list for protein
        list_input_protein = []

        identifier = node['identifier']
        alternative_uniprot_ids = node['alternative_uniprot_id'] if 'alternative_uniprot_id' in node else []

        if not identifier in dict_be_identifier_sort_to_protein_or_not or dict_be_identifier_sort_to_protein_or_not[
            identifier]:

            list_input_protein.append(identifier)

            part_dict = dict(node)
            part_dict['labels'] = labels
            name = part_dict['name'] if 'name' in part_dict else ''
            name = name.encode('utf-8')
            labels.remove('Protein_DrugBank')
            for label in labels:
                dict_db_labels_to_csv_label_file[label].writerow([identifier])
            dict_proteins[identifier] = labels

            if identifier in dict_hetionet_protein:
                counter_mapped += 1
                if len(dict_hetionet_protein[identifier]) == 1:
                    protein_hetionet = dict_hetionet_protein[identifier][0]
                    list_input_protein.append(protein_hetionet['identifier'])

                    interagte_infos_into_csv(part_dict, protein_hetionet, list_input_protein)

                else:
                    print(len(dict_hetionet_protein[identifier]))
                    print(identifier)
                    for protein_hetionet in dict_hetionet_protein[identifier]:
                        list_multiple_input = []
                        list_multiple_input.append(identifier)
                        list_multiple_input.append(protein_hetionet['identifier'])
                        print(protein_hetionet['identifier'])
                        interagte_infos_into_csv(part_dict, protein_hetionet, list_multiple_input)
                    print('multiple mapping')
            elif identifier in dict_be_identifier_sort_to_protein_or_not:
                print('protein without uniprot id')
                counter_not_a_protein += 1
                print(node['name'])
                writer_not_mapped.writerow(dict(node))
                if node['organism'] == 'Humans':
                    counter_human_not_found += 1

                drugbank_id = node['drugbank_id']
                if identifier == drugbank_id:
                    print('do something different protein')
                # print(node)

            else:
                print('not found')
                print(identifier)
                print(node['organism'])
                counter_not_a_protein += 1
                writer_not_mapped.writerow(dict(node))
                if node['organism'] == 'Humans':
                    counter_human_not_found += 1
                drugbank_id=node['drugbank_id']
                if identifier==drugbank_id:
                    print('do something different')
                # print(node)
                # sys.exit('not found')


        else:
            drugbank_id=node['drugbank_id']
            if identifier==drugbank_id:
                print('do something different')
            counter_not_a_protein += 1
            writer_not_mapped.writerow(dict(node))

        if counter_proteins_in_total % 10 == 0:
            print(counter_proteins_in_total)
            print(counter_mapped)
            print(counter_not_a_protein)
    # print(dict_proteins)
    print('number of human proteins:' + str(counter_mapped))
    print('number of not proteins or not human or not reviewed:' + str(counter_not_a_protein))
    print('counter of not protein which were human:' + str(counter_human_not_found))
    print('nummer of all proteins in drugbank:' + str(counter_proteins_in_total))
    print('number of proteins without gene id:' + str(counter_uniprot_with_no_gene_ids))


# file for all rela which should be integrated
cypher_rela = open('protein/cypher_protein_rela.cypher', 'w')

'''
Generate csv with component relationships
'''


def generate_csv_componet_rela():
    query = 'MATCH p=(a:Protein_DrugBank)-[r:has_component_PIhcPI]->(b:Protein_DrugBank) RETURN a.identifier, b.identifier'
    result = g.run(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Documents/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_rela_component.csv" As line MATCH (g:Protein{identifier:line.id1}),(b:Protein{identifier:line.id2}) Create (g)-[:HAS_COMPONENT_PRhcPR]->(b);\n'''
    cypher_rela.write(query)

    csv_file = open('protein/proteins_rela_component.csv', 'w')
    writer_csv = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer_csv.writerow(['id1', 'id2'])

    counter_component_rela = 0
    for identifier1, identifier2, in result:
        print(identifier1)
        counter_component_rela += 1
        writer_csv.writerow([identifier1, identifier2])

    print('number of component rela:' + str(counter_component_rela))


def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all information to the nodes where I was not sure if they are proetins or not')

    load_manual_checked_proteins_or_not()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all genes and gather the information for uniprot gene')

    load_all_hetionet_proteins_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all DrugBank proteins in dictionary')

    load_proteins_from_drugbank_into_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all DrugBank has component rela and write them in csv and generate cypher file for integration')

    generate_csv_componet_rela()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
