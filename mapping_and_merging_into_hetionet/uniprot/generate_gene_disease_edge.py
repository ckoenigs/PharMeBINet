import datetime
import sys, csv

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

# dictionary that get for every uniprot id to kex to pubmed id
dict_uniprot_id_to_key_evidence_to_pubmed_id={}

def load_all_pubmed_ids_for_proteins():
    """
    Get reference information for the different evidences!
    :return:
    """
    query='''Match (:Disease_Uniprot)-[r]-(a:Protein_Uniprot)-[h]-(:Evidence_Uniprot) Return a.identifier, h.key, h.sources'''
    results=g.run(query)
    for uniprot_id, key_id, sources, in results:
        if not uniprot_id in dict_uniprot_id_to_key_evidence_to_pubmed_id:
            dict_uniprot_id_to_key_evidence_to_pubmed_id[uniprot_id]={}
        if not key_id in dict_uniprot_id_to_key_evidence_to_pubmed_id[uniprot_id]:
            # print(uniprot_id)
            # print(key_id)
            # print(sources)
            # print(sources is None)
            if sources  is None:
                continue

            elif len(sources)>1:
                print('sources greater than one', sources)
                sys.exit()
            dict_uniprot_id_to_key_evidence_to_pubmed_id[uniprot_id][key_id]=sources
        else:
            if dict_uniprot_id_to_key_evidence_to_pubmed_id[uniprot_id][key_id]!= sources:
                print('ohje :(')
                print(dict_uniprot_id_to_key_evidence_to_pubmed_id[uniprot_id][key_id])

def write_rela_in_file(csv_writer, dict_pairs_to_info):
    """
    Go through dictionary and write rela into file.
    :param csv_writer: csv writer
    :param dict_pairs_to_info: dictionary
    :return:
    """
    for (gene_id,disease_id), info_list in dict_pairs_to_info.items():
        csv_writer.writerow([gene_id,disease_id, '|'.join(info_list[0]), '|'.join(info_list[1]), '|'.join(info_list[2])])


'''
Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
'''

def get_pairs_information():
    # generate a file with all uniprots to
    file_name='uniprot_disease/db_gene_to_disease.tsv'
    file_gene_disease = open(file_name, 'w')
    csv_gene_disease = csv.writer(file_gene_disease, delimiter='\t')
    csv_gene_disease.writerow(['gene_ids', 'disease_id','notes', 'pubmeds', 'references'])

    # query gene-disease association

    file_cypher = open('output/cypher_edge.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line FIELDTERMINATOR "\\t" MATCH (b:Disease{identifier:line.disease_id})-[r:ASSOCIATES_DaG]->(g:Gene{identifier:line.gene_ids}) Where not exists(r.pubMed_ids) Set r.pubMed_ids=[] ;\n'''
    query = query % (file_name)
    file_cypher.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line FIELDTERMINATOR "\\t" MATCH (g:Gene{identifier:line.gene_ids}),(b:Disease{identifier:line.disease_id}) Merge (b)-[r:ASSOCIATES_DaG]->(g) On Create Set r.source="UniProt", r.resource=["UniProt"], r.uniprot='yes', r.kind_of_rela=split(line.notes,'|'), r.references=split(r.references,'|'), r.pubMed_ids=split(line.pubmeds,'|'), r.sources=split(line.source,"|"), r.url="https://www.uniprot.org/uniprot/"+line.uniprot_ids, r.license='CC BY 4.0' On Match Set r.uniprot="yes", r.resource=r.resource+"UniProt",  r.pubMed_ids=r.pubMed_ids+split(line.pubmeds,'|'), r.kind_of_rela=split(line.notes,'|'), r.references=split(r.references,'|') ;\n'''
    query =query %(file_name)
    file_cypher.write(query)

    query="""Match (n:Disease)--(:Disease_Uniprot)-[r]-(:Protein_Uniprot)--(p:Protein)-[:PRODUCES_GpP]-(g:Gene) Return Distinct p.identifier ,n.identifier, r, g.identifier , n.name """
    results=g.run(query)

    #dictionary pairs to info
    dict_pairs_to_info={}

    counter_all_pairs=0
    counter_added=0
    counter_without_references=0

    for protein_id,disease_id, rela, gene_id, disease_name, in results:
        evidences= rela['evidence'].split() if 'evidence' in rela else []

        references=set()
        pubmeds=set()
        counter_all_pairs+=1
        for evidence in evidences:
            if evidence in dict_uniprot_id_to_key_evidence_to_pubmed_id[protein_id]:
                sources=dict_uniprot_id_to_key_evidence_to_pubmed_id[protein_id][evidence]
                references=references.union(sources)
                for source in sources:
                    if source.startswith('PubMed:'):
                        pubmeds.add(source.split(':')[1])

        if (gene_id,disease_id) in dict_pairs_to_info :
            entry=dict_pairs_to_info[(gene_id, disease_id)]
            entry[0].add(rela['text'])
            entry[1]=entry[1].union(pubmeds)
            entry[2]=entry[2].union(references)
            continue
        if len(pubmeds)>0:
            counter_added+=1
            # csv_gene_disease.writerow([gene_id,disease_id,rela['text']])
            dict_pairs_to_info[(gene_id,disease_id)]=[set([rela['text']]), pubmeds, references]
        elif len(references)>0:
            counter_without_references+=1
            print(disease_id, gene_id, protein_id)
            print(disease_name, dict(rela))
            print(references)
            # break

        else:
            counter_without_references+=1
            # print(disease_id, gene_id, protein_id, disease_name)
            # print(dict(rela))

    print('number of all edges:', counter_all_pairs)
    print('number of all added edges:', counter_added)
    print('number of all edges without references:', counter_without_references)

    write_rela_in_file(csv_gene_disease,dict_pairs_to_info)




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
    print('load all pubmeds')

    load_all_pubmed_ids_for_proteins()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gather all information of the proteins')

    get_pairs_information()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
