from collections import defaultdict
import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()

#dictionary pairs to info
dict_pairs_to_info={}

def combine_info(tuple_ids_and_iso, rela):
    for prop in ['experiments', 'interaction_ids']:  # ,  'iso_of_protein_to', 'iso_of_protein_from'
        if prop != 'interaction_ids':
            dict_pairs_to_info[tuple_ids_and_iso][prop].add(rela[prop])
        else:
            dict_pairs_to_info[tuple_ids_and_iso][prop] = \
            dict_pairs_to_info[tuple_ids_and_iso][prop].union(rela[prop])

'''
Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
'''

def get_pairs_information():

    # only the interaction in the same organism
    query="""Match (n:Protein_Uniprot)-[r]->(p:Protein_Uniprot) Where r.organismsDiffer='false' Return Distinct n.identifier, r, p.identifier """
    results=g.run(query)

    for protein_id1, rela, protein_id2, in results:
        iso_of_protein_from = rela['iso_of_protein_from'] if 'iso_of_protein_from' in rela else ''
        iso_of_protein_to = rela['iso_of_protein_to'] if 'iso_of_protein_to' in rela else ''

        if (protein_id1,protein_id2, iso_of_protein_from, iso_of_protein_to) in dict_pairs_to_info:
            print(protein_id1,protein_id2)
            combine_info((protein_id1,protein_id2, iso_of_protein_from, iso_of_protein_to), rela)

        elif (protein_id2,protein_id1, iso_of_protein_to, iso_of_protein_from) in dict_pairs_to_info:
            combine_info((protein_id2,protein_id1, iso_of_protein_to, iso_of_protein_from), rela)

        else:
            dict_rela={}
            for prop in ['experiments','interaction_ids']: #:,'iso_of_protein_to','iso_of_protein_from'
                if prop!='interaction_ids':
                    dict_rela[prop]={rela[prop]}
                else:
                    dict_rela[prop] = set(rela[prop])
            dict_pairs_to_info[(protein_id1,protein_id2, iso_of_protein_from, iso_of_protein_to)]= dict_rela



def write_info_into_csv_file():
    # generate a file with all uniprots to
    file_name = 'output/protein_interaction.csv'
    file_gene_disease = open(file_name, 'w')
    csv_gene_disease = csv.writer(file_gene_disease)
    csv_gene_disease.writerow(
        ['protein_id1', 'protein_id2', 'interaction_ids', 'iso_of_protein_to', 'iso_of_protein_from', 'experiments'])

    # query gene-disease association

    file_cypher = open('output/cypher_edge.cypher', 'a')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line MATCH (g:Protein{identifier:line.protein_id1}),(b:Protein{identifier:line.protein_id2}) Create (b)-[r:INTERACTS_PiP{source:"UniProt", license:"CC BY 4.0", resource:["UniProt"], uniprot:'yes', iso_of_protein_from:line.iso_of_protein_from, iso_of_protein_to:line.iso_of_protein_to, interaction_ids:split(line.interaction_ids, "|"), experiments:split(line.experiments, "|")}]->(g) ;\n'''
    query = query % (file_name)
    file_cypher.write(query)

    for (protein_id1, protein_id2, iso_of_protein_from, iso_of_protein_to), rela in dict_pairs_to_info.items():
        experimental = '|'.join(rela['experiments'])
        # if len(experimental)>1:
        #     print(protein_id1,protein_id2)
        #     print('different experiment')
        #     print(experimental)

        interaction_ids = '|'.join(rela['interaction_ids'])

        csv_gene_disease.writerow(
            [protein_id1, protein_id2, interaction_ids, iso_of_protein_to, iso_of_protein_from, experimental])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the proteins')

    get_pairs_information()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('generate and write info in csv file')

    write_info_into_csv_file()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
