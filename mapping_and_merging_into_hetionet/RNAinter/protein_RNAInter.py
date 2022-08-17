import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# cypher file
cypher_file = open("output/cypher.cypher", "a", encoding="utf-8")


def protein_RNAInter():
    print("######### load_from_database ##################")

    # save the RAW_IDs from protein_RNAInter in a dictionary
    # structure dictionary => { "database": { "ID" : "Raw_ID"}
    proteinRNAInter = {}
    Identifier = []
    query = "MATCH (n:protein_RNAInter) RETURN n.Raw_ID "
    result = g.run(query)
    for raw_id, in result:
        id = raw_id.split(":", 1)
        if len(id) == 2:
            if id[0] not in proteinRNAInter:
                Identifier.append(id[1])
                proteinRNAInter[id[0]] = {}
                proteinRNAInter[id[0]][id[1]] = raw_id
            else:
                Identifier.append(id[1])
                proteinRNAInter[id[0]][id[1]] = raw_id

    # compare the identifiers from Protein with the Raw_IDs from protein_RNAInter
    # save the IDs that appear in both of them in a dictionary
    # structure dictionary => { "identifier": "{rawid: "Raw_ID", resource: "resource"}}
    Protein_RNAInter = {}
    query = "MATCH (n:Protein) RETURN n.identifier, n.resource"
    result = g.run(query)
    for id, resource, in result:
        if id in proteinRNAInter["UniProt"]:
            Protein_RNAInter[id] = {}
            Protein_RNAInter[id]["rawid"] =proteinRNAInter["UniProt"][id]
            newresource = pharmebinetutils.resource_add_and_prepare(resource, "RNAInter")
            Protein_RNAInter[id]["resource"] = newresource

    # for the Raw_ID's that belong to the database "NCBI":
    # get the identifier of the protein using the connection between 'Gene' and 'Protein'
    identifier = "','".join(Identifier)
    query = "MATCH a=(m:Gene)--(b:Protein) WHERE m.identifier in ['" + identifier + "'] RETURN m.identifier,b.identifier, b.resource"
    result = g.run(query)
    for gene, protein, resource, in result:
        if protein not in Protein_RNAInter:
            Protein_RNAInter[protein]={}
            Protein_RNAInter[protein]["rawid"] ="NCBI:"+gene
            newresource = pharmebinetutils.resource_add_and_prepare(resource, "RNAInter")
            Protein_RNAInter[protein]["resource"] = newresource

    # save the identifier and the Raw_ID in a tsv file
    file_name='output/Proteinedges.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["Raw_ID", "identifier"]
        writer.writerow(line)
        for key, value in Protein_RNAInter.items():
            list = []
            list.append(key)
            for a in value:
                list.append(Protein_RNAInter[key][a])
            writer.writerow(list)
    tsv_file.close()

    print("######### Start: Cypher #########")
    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAinter/{file_name}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:protein_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:Protein{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.RNAInter = "yes" Create (p1)-[:associateProteinRNAInter{{  '
    query = query[:-2] + '}]->(p2);\n'
    cypher_file.write(query)
    print("######### End: Cypher #########")


def main():

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnaInter')

    create_connection_with_neo4j()
    protein_RNAInter()


if __name__ == "__main__":
    # execute only if run as a script
    main()