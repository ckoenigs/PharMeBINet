from py2neo import Graph
import datetime
import csv
import sys, json

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()

def load_pair_edges(label):
    """
    Load all pairs of hmdb for this pair and write the into mapped or not mapped files.
    :param label: string
    :return:
    """
    query = '''MATCH (p:%s)-[]-(r:%s_HMDB)-[v]-(n:Metabolite_HMDB)-[]-(b:Metabolite) Where exists(v.references)  RETURN p.identifier, b.identifier, v'''
    query= query %(label,label)
    results = graph_database.run(query)

    # set of all hmdb pairs
    dict_of_used_pairs = {}

    # counter
    counter= 0

    # set
    set_distinct_reference_text=set()

    for node_id_1, node_id_2, rela, in results:
        counter+=1
        references= rela['references']
        pubmed_ids=set()
        urls=set()

        references_set=set()
        # print(node_id_1, node_id_2)
        # if node_id_1=='MONDO:0007452' and node_id_2=='HMDB0029182':
        #     print(references)
        for reference in references:
            # if node_id_1 == 'MONDO:0005240' and node_id_2 == 'HMDB0000092':
            #     print(reference)
            reference= json.loads(reference)
            if 'pubmed_id' in reference:
                if  reference['pubmed_id']  !='':
                    pubmed_ids.add(reference['pubmed_id'])
                else:
                    print(node_id_1,node_id_2,reference, 'with none')
            else:
                if len(reference)>1:
                    print('no pubmed:',reference)
                reference_text=reference['reference_text']
                splitted_reference_text=reference_text.split(' ')
                last_word=splitted_reference_text[-1]
                if last_word.startswith('https:') or last_word.startswith('http:'):
                    if last_word[-1]==')':
                        last_word=last_word[:-1]
                    urls.add(last_word)
                else:
                    references_set.add(reference_text)
                set_distinct_reference_text.add(reference['reference_text'])
        if (node_id_1,node_id_2) not in dict_of_used_pairs:
            dict_of_used_pairs[(node_id_1,node_id_2)]=[pubmed_ids, urls, references_set]
        else:
            print('double')
            dict_of_used_pairs[(node_id_1, node_id_2)][0]= dict_of_used_pairs[(node_id_1,node_id_2)][0].union(pubmed_ids)
            dict_of_used_pairs[(node_id_1, node_id_2)][1] = dict_of_used_pairs[(node_id_1, node_id_2)][1].union(urls)
            dict_of_used_pairs[(node_id_1, node_id_2)][2] = dict_of_used_pairs[(node_id_1, node_id_2)][2].union(references_set)
    print('number of disease  and metabolite relationships in hetionet:' ,
        len(dict_of_used_pairs))
    print('number of edges:', counter)
    print(len(set_distinct_reference_text))
    for entry in set_distinct_reference_text:
        print(entry)

    file_name='metabolite_disease_protein/integrate_edges_%s.tsv' %(label)
    file=open(file_name,'w',encoding='utf-8')
    csv_writer=csv.writer(file, delimiter='\t')
    csv_writer.writerow(['node_id_1','node_id_2','pubmed_ids', 'urls', 'references'])

    for (disease_id, metabolite_id), pubmed_ids_urls in dict_of_used_pairs.items():
        csv_writer.writerow([disease_id,metabolite_id, '|'.join(pubmed_ids_urls[0]), '|'.join(pubmed_ids_urls[1]), '|'.join(pubmed_ids_urls[2])])

    create_cypher_file(file_name,label)




def create_cypher_file(file_name, label):
    """
    Prepare integration of disease-metabolite edges
    :param file_name: string
    :return:
    """

    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.node_id_1}),(c:Metabolite{identifier:line.node_id_2}) CREATE (d)-[: ASSOCIATES_%saM{ resource: ['HMDB'], hmdb: "yes", url:"https://hmdb.ca/metabolites/"+line.node_id_2, source:"HMDB", pubMed_ids:split(line.pubmed_ids,"|"), urls:split(line.urls,"|"), references:split(line.references,"|"), license:"Creative Commons (CC) Attribution-NonCommercial (NC) 4.0 International Licensing "}]->(c);\n'''
    query = query % (path_of_directory, file_name, label, label[0])
    cypher_file.write(query)




def main():
    global path_of_directory, license, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hmdb edges without info')

    cypher_file = open('output/cypher_edge.cypher', 'a', encoding="utf-8")


    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    for label in ['Disease','Protein']:

        print(
            '###########################################################################################################################')

        print(datetime.datetime.now())
        print('load rela data', label)

        load_pair_edges(label)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    cypher_file.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
