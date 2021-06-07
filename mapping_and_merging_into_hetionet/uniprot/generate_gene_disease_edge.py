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


'''
Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
'''

def get_pairs_information():
    # generate a file with all uniprots to
    file_name='uniprot_disease/db_gene_to_disease.csv'
    file_gene_disease = open(file_name, 'w')
    csv_gene_disease = csv.writer(file_gene_disease)
    csv_gene_disease.writerow(['gene_ids', 'disease_id','note'])

    # query gene-disease association

    file_cypher = open('output/cypher_edge.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line MATCH (b:Disease{identifier:line.disease_id})-[r:ASSOCIATES_DaG]->(g:Gene{identifier:line.gene_ids}) Where not exists(r.kind_of_rela) Set r.kind_of_rela=[] ;\n'''
    query = query % (file_name)
    file_cypher.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line MATCH (g:Gene{identifier:line.gene_ids}),(b:Disease{identifier:line.disease_id}) Merge (b)-[r:ASSOCIATES_DaG]->(g) On Create Set r.source="UniProt", r.resource=["UniProt"], r.uniprot='yes', r.kind_of_rela=[line.note], r.sources=split(line.source,"|"), r.url="https://www.uniprot.org/uniprot/"+line.uniprot_ids, r.license='CC BY 4.0' On Match Set r.uniprot="yes", r.resource=r.resource+"UniProt", r.kind_of_rela=r.kind_of_rela+line.note ;\n'''
    query =query %(file_name)
    file_cypher.write(query)

    query="""Match (n:Disease)--(:Disease_Uniprot)-[r]-(:Protein_Uniprot)--(p:Protein)-[:PRODUCES_GpP]-(g:Gene) Return Distinct n.identifier, r, g.identifier  """
    results=g.run(query)

    #dictionary pairs to info
    dict_pairs_to_info={}

    for disease_id, rela, gene_id, in results:
        if (gene_id,disease_id) in dict_pairs_to_info and dict_pairs_to_info[(gene_id,disease_id)]!=rela['text']:
            print('ohje')
            print(gene_id)
            print(rela['text'])
            print(dict_pairs_to_info[(gene_id,disease_id)])
        csv_gene_disease.writerow([gene_id,disease_id,rela['text']])
        dict_pairs_to_info[(gene_id,disease_id)]=rela['text']




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


if __name__ == "__main__":
    # execute only if run as a script
    main()
