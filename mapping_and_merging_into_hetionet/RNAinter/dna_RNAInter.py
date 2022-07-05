import csv,sys
sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

# cypher file
cypher_file=open("output/cypher.cypher","w",encoding="utf-8")


def dna_RNAInter():
    print("######### load_from_database #########")
    dnaRNAInter = {}

    # save the RAW_IDs from dna_RNAInter in a dictionary
    # structure dictionary => { "database": { "ID" : "Raw_ID"}
    query = "MATCH (n:dna_RNAInter) RETURN n.Raw_ID "
    result = g.run(query)
    for raw_id, in result:
        id= raw_id.split(":", 1)
        if len(id)==2:
            if id[0] not in dnaRNAInter:
                dnaRNAInter[id[0]] ={}
                dnaRNAInter[id[0]][id[1]]=raw_id
            else:
                dnaRNAInter[id[0]][id[1]]=raw_id

    # compare the identifiers from Gene with the RAW_IDs from dna_RNAInter
    # save the IDs that appear in both of them in a tsv file
    query = "MATCH (n:Gene) RETURN n.identifier"
    result = g.run(query)

    file_name='output/DNAedges.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["Raw_ID", "identifier"]
        writer.writerow(line)
        for id, in result:
            if id in dnaRNAInter["NCBI"]:
                list = []
                list.append(dnaRNAInter["NCBI"][id]), list.append(id)
                writer.writerow(list)
    tsv_file.close()

    #
    print("######### Start: Cypher #########")
    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAinter/{file_name}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:dna_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:Gene{{identifier:line.identifier}}) Create (p1)-[:associateGeneDnaRNAInter{{  '
    query = query[:-2]+'}]->(p2);\n'
    cypher_file.write(query)
    print("######### End: Cypher #########")

def main():

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnaInter')

    create_connection_with_neo4j()
    dna_RNAInter()

if __name__ == "__main__":
    # execute only if run as a script
    main()
