'''integrate the'''
from py2neo import Graph, authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


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



'''
load all possible proteins from Drugbank and put only all as protein defined proteins into a dictionary
'''


def load_proteins_from_drugbank_into_dict():
    query = '''MATCH (n:Protein_DrugBank) RETURN n, labels(n) ;'''
    results = g.run(query)
    counter_not_a_protein = 0
    generate_csv = open('protein/proteins.csv', 'w')
    writer = csv.writer(generate_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['id','name'])

    # all queries which are used to integrate Protein with the extra labels into Hetionet
    cypherfile = open('protein/cypher_protein.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins.csv" As line MATCH (n:Protein_DrugBank{identifier:line.id}) Create (g:Protein{identifier:n.identifier, '''
    for property in list_of_all_properties_of_proteins:
        query += property + ':n.' + property + ', '


    query = query[:-2] + '''});\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_carrier.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Carrier ;\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_enzyme.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Enzyme ;\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_target.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Target ;\n'''
    cypherfile.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_transporter.csv" As line MATCH (g:Protein{identifier:line.id}) Set g:Transporter ;\n'''
    cypherfile.write(query)
    query='Create Constraint On (node:Protein) Assert node.identifier Is Unique; \n'
    cypherfile.write(query)
    cypherfile.close()

    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/uniprot_gene/db_uniprot_to_gene_rela.csv" As line MATCH (n:Protein_DrugBank{identifier:line.uniprot_id}), (g:Gene{identifier:toInteger(line.gene_id)}) Create (g)-[:PRODUCES_GpP]->(n);'''
    cypher_rela.write(query)

    file_uniprots_with_multiple= open('protein/uniprot_gene/db_uniprot_to_multi_genes.csv','w')
    writer_multi=csv.writer(file_uniprots_with_multiple)
    writer_multi.writerow(['uniprot_id','protein_name','genes','alternative_ids'])

    file_uniprots_gene_rela = open('protein/uniprot_gene/db_uniprot_to_gene_rela.csv', 'w')
    writer_rela = csv.writer(file_uniprots_gene_rela)
    writer_rela.writerow(['uniprot_id',  'gene_id','alternative_ids'])

    file_uniprots_without_rela = open('protein/uniprot_gene/db_uniprot_without_rela.csv', 'w')
    writer_without_rela = csv.writer(file_uniprots_without_rela)
    writer_without_rela.writerow(['uniprot_id','name'])

    file_uniprots_gene_with_alternative = open('protein/uniprot_gene/db_uniprot_to_gene_with_alternative.csv', 'w')
    writer_rela_with_alternative = csv.writer(file_uniprots_gene_with_alternative)
    writer_rela_with_alternative.writerow(['uniprot_id','alternative id','gene(s)'])

    counter_uniprot_with_no_gene_ids=0
    for node, labels, in results:
        identifier = node['identifier']
        alternative_uniprot_ids= node['alternative_uniprot_id'] if 'alternative_uniprot_id' in node else []

        if not identifier in dict_be_identifier_sort_to_protein_or_not or dict_be_identifier_sort_to_protein_or_not[
            identifier]:
            part_dict = dict(node)
            part_dict['labels'] = labels
            name = part_dict['name'] if 'name' in part_dict else ''
            name = name.encode('utf-8')
            labels.remove('Protein_DrugBank')
            for label in labels:
                dict_db_labels_to_csv_label_file[label].writerow([identifier])
            dict_proteins[identifier] = labels

            writer.writerow([identifier,name])
            if identifier in dict_uniprot_count_genes:
                writer_multi.writerow([identifier,name,dict_uniprot_to_gene_id[identifier]])
            elif identifier in dict_uniprot_to_gene_id:
                writer_rela.writerow([identifier,dict_uniprot_to_gene_id[identifier][0]])
            else:
                found_at_least_one_mapping=False
                list_alternative_ids_mapping=[]
                set_list_genese_of_alternative_ids=set([])
                for alternative_uniprot_id in alternative_uniprot_ids:
                    if alternative_uniprot_id in dict_uniprot_count_genes:
                        list_alternative_ids_mapping.append(alternative_uniprot_id)
                        set_list_genese_of_alternative_ids.union(dict_uniprot_to_gene_id[alternative_uniprot_id])
                        writer_rela_with_alternative.writerow([identifier,alternative_uniprot_id,dict_uniprot_to_gene_id[alternative_uniprot_id]])
                        found_at_least_one_mapping=True
                    elif alternative_uniprot_id in dict_uniprot_to_gene_id:
                        list_alternative_ids_mapping.append(alternative_uniprot_id)
                        set_list_genese_of_alternative_ids.add(dict_uniprot_to_gene_id[alternative_uniprot_id][0])
                        writer_rela_with_alternative.writerow([identifier,alternative_uniprot_id,dict_uniprot_to_gene_id[alternative_uniprot_id][0]])
                        found_at_least_one_mapping=True
                if not found_at_least_one_mapping:
                    writer_without_rela.writerow([identifier,name])
                    counter_uniprot_with_no_gene_ids+=1
                else:
                    if len(set_list_genese_of_alternative_ids)==1:
                        writer_rela.writerow([identifier, list(set_list_genese_of_alternative_ids)[0],list_alternative_ids_mapping])
                    else:
                        writer_multi.writerow([identifier, name, list(set_list_genese_of_alternative_ids),list_alternative_ids_mapping])


        else:
            counter_not_a_protein += 1
    # print(dict_proteins)
    print('number of proteins:' + str(len(dict_proteins)))
    print('number of not proteins:' + str(counter_not_a_protein))
    print('number of proteins without gene id:'+str(counter_uniprot_with_no_gene_ids))

# file for all rela which should be integrated
cypher_rela=open('protein/cypher_protein_rela.cypher', 'w')

'''
Generate csv with component relationships
'''
def generate_csv_componet_rela():
    query='MATCH p=(a:Protein_DrugBank)-[r:has_component_PIhcPI]->(b:Protein_DrugBank) RETURN a.identifier, b.identifier'
    result= g.run(query)


    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/drugbank/protein/proteins_rela_component.csv" As line MATCH (g:Protein{identifier:line.id1}),(b:Protein{identifier:line.id2}) Create (g)-[:HAS_COMPONENT_PRhcPR]->(b);\n'''
    cypher_rela.write(query)

    csv_file=open('protein/proteins_rela_component.csv','w')
    writer_csv=csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer_csv.writerow(['id1','id2'])

    counter_component_rela=0
    for identifier1, identifier2, in result:

        print(identifier1)
        counter_component_rela+=1
        writer_csv.writerow([identifier1,identifier2])

    print('number of component rela:'+str(counter_component_rela))



#dictionary from uniprot to gene id
dict_uniprot_to_gene_id={}

#dict_uniprot_count_genes
dict_uniprot_count_genes={}

'''
Find mapping between genes and proteins
'''
def get_all_genes():
    query='''MATCH (n:Gene) RETURN n.identifier, n.uniProtIDs'''
    results=g.run(query)
    counter_uniprot_to_multiple_genes=0
    for gene_id, list_uniprots, in results:
        if list_uniprots:
            for uniprot in list_uniprots:
                # generate dictionary for uniprot to gene(s)
                # and if more than two genes fit to one uniprot id they will be count
                if uniprot in dict_uniprot_to_gene_id:
                    dict_uniprot_to_gene_id[uniprot].append(gene_id)
                    dict_uniprot_count_genes[uniprot]=1+dict_uniprot_count_genes[uniprot] if uniprot in dict_uniprot_count_genes else 2
                    counter_uniprot_to_multiple_genes+=1
                else:
                    dict_uniprot_to_gene_id[uniprot]=[gene_id]

    file=open('protein/uniprot_gene/uniprot_to_multi_genes.csv','w')
    writer=csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['uniprot','gene_ids'])
    for uniprot in dict_uniprot_count_genes.keys():
        string_gene_list='|'.join(str(x) for x in dict_uniprot_to_gene_id[uniprot])
        writer.writerow([uniprot, string_gene_list])

    print('number of uniprots which appears in multiple genes:'+str(counter_uniprot_to_multiple_genes))
    print(len(dict_uniprot_to_gene_id))
    print(len(dict_uniprot_count_genes))
    print(dict_uniprot_count_genes)


def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all information to the nodes where I was not sure if they are proetins or not')

    load_manual_checked_proteins_or_not()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all genes and gather the information for uniprot gene')

    get_all_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all DrugBank proteins in dictionary')

    load_proteins_from_drugbank_into_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())

    print('load all DrugBank has component rela and write them in csv and generate cypher file for integration')

    # generate_csv_componet_rela()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
