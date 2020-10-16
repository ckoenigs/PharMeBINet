import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

def generate_file_and_cypher():
    query='''MATCH (:protein_IID)-[p:interacts]->(:protein_IID) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields; '''
    results=g.run(query)

    file_name='interaction/rela'

    cypher_file = open('interaction/cypher.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/iid/%s.tsv" As line FIELDTERMINATOR '\\t' 
            Match (p1:Protein{identifier:line.protein_id_1}), (v:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PRiPR{ '''
    query = query % (path_of_directory, file_name)

    header=['protein_id_1','protein_id_2']
    for head, in results:
        header.append(head)
        if head in ['targeting_drugs','evidence_type','dbs','methods','pmids']:
            query+= head+':split(line.'+head+',"|"), '
        else:
            query += head + ':line.' + head + ', '

    query+= ' license:"blub", iid:"yes", resource:["IID"], url:"blub"}]->(p2);\n'
    cypher_file.write(query)
    file=open(file_name+'.tsv','w',encoding='utf-8')
    csv_writer=csv.DictWriter(file,fieldnames=header, delimiter='\t')
    csv_writer.writeheader()
    return csv_writer


def load_and_prepare_IID_human_data():

    query='''Match (p1:Protein)--(:protein_IID)-[r:interacts]->(:protein_IID)--(p2:Protein) Return p1.identifier, r, p2.identifier; '''
    results=g.run(query)

    csv_writer=generate_file_and_cypher()

    for p1_id, rela, p2_id, in results:
        evidence_types = rela['evidence_types'] if 'evidence_types' in rela else []
        if 'exp' in evidence_types:
            rela_info=dict(rela)
            rela_info['protein_id_1']=p1_id
            rela_info['protein_id_2'] = p1_id
            csv_writer.writerow(rela_info)



 # path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('generate connection to neo4j')

    create_connection_with_neo4j()

    print(datetime.datetime.utcnow())
    print('load IID human data')


    load_and_prepare_IID_human_data()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()