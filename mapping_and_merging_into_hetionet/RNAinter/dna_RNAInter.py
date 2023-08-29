import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()



def dna_RNAInter():
    """
    Load first all RNAinter DNA and the generate a TSV file. Next, load all gene nodes and map to RNAinter DNA. Write
    into to TSV file
    :return:
    """
    print("######### load_from_database #########")
    dnaRNAInter = {}

    # save the RAW_IDs from dna_RNAInter in a dictionary
    # structure dictionary => { "database": { "ID" : "Raw_ID"}
    query = "MATCH (n:dna_RNAInter) RETURN n.Raw_ID "
    result = g.run(query)
    for recod in result:
        [raw_id] = recod.values()
        id = raw_id.split(":", 1)
        if len(id) == 2:
            if id[0] not in dnaRNAInter:
                dnaRNAInter[id[0]] = {}
                dnaRNAInter[id[0]][id[1]] = raw_id
            else:
                dnaRNAInter[id[0]][id[1]] = raw_id

    # compare the identifiers from Gene with the RAW_IDs from dna_RNAInter
    # save the IDs that appear in both of them in a tsv
    query = "MATCH (n:Gene) RETURN n.identifier, n.resource"
    result = g.run(query)

    file_name = 'output/DNA_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["identifier", "Raw_ID", "resource"]
        writer.writerow(line)
        for record in result:
            [id, resource] = record.values()
            if id in dnaRNAInter["NCBI"]:
                list = []
                list.append(id), list.append(dnaRNAInter["NCBI"][id])
                newresource = pharmebinetutils.resource_add_and_prepare(resource, "RNAInter")
                list.append(newresource)
                writer.writerow(list)
    tsv_file.close()

    # cypher file
    cypher_file = open("output/cypher.cypher", "w", encoding="utf-8")
    print("######### Start: Cypher #########")
    query = f'Match (p1:dna_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:Gene{{identifier:line.identifier}})  SET p2.rnainter="yes", p2.resource = split(line.resource,"|") Create (p1)-[:associateGeneDnaRNAInter]->(p2)  '
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/RNAinter/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnaInter')

    print('###########################################################################')
    print(datetime.datetime.now(), 'create connections')
    create_connection_with_neo4j()

    print('###########################################################################')
    print(datetime.datetime.now(), 'mapping')
    dna_RNAInter()

    driver.close()

    print('###########################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
