import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# cypher file
cypher_file = open("output/cypher.cypher", "a", encoding="utf-8")


def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped):
    for map_id in mapped_ids:
        csv_writer.writerow(
            [raw_id, map_id, pharmebinetutils.resource_add_and_prepare(RNA[map_id], "RNAInter"), how_mapped])


def rna_RNAInter():
    print("######### load_from_database ##################")
    global RNA
    RNA = {}
    RNAXref = {}
    RNAName = {}

    query = "MATCH (n:RNA) RETURN n.identifier, n.geneName,n.xrefs, n.resource"
    result = g.run(query)

    for record in result:
        [id, names, xref, resource] = record.values()

        RNA[id] = resource

        if names is not None:
            for name in names:
                if name.lower() not in RNAName:
                    RNAName[name.lower()] = [id]
                else:
                    RNAName[name.lower()].append(id)

        if xref is not None:
            for x in xref:

                if "MIRBASE:" in x:
                    pubid = x[8:]
                    if pubid not in RNAXref:
                        RNAXref[pubid] = [id]
                    else:
                        RNAXref[pubid].append(id)
                elif "ENSEMBL:" in x:
                    pubid = x[8:]
                    if pubid not in RNAXref:
                        RNAXref[pubid] = [id]
                    else:
                        RNAXref[pubid].append(id)

    # save the identifier and the Raw_ID in a tsv file
    file_name = 'output/RNA_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["Raw_ID", "identifier", "resource", "how_mapped"]
        writer.writerow(line)

        query = "MATCH (n:rna_RNAInter) RETURN n.Raw_ID, n.Interactor"
        result = g.run(query)

        for record in result:
            [raw_id, inter] = record.values()

            if raw_id is not None:
                rid = raw_id.split(":", 1)
                if len(rid) == 2 and len(rid[1]) > 2:
                    rid = rid[1]
                else:
                    rid = raw_id

            if rid in RNA:
                write_infos_into_file(writer, raw_id, [rid], 'raw_id-identifier')
            elif rid in RNAXref:
                write_infos_into_file(writer, raw_id, RNAXref[rid], 'raw_id-xrefs')
            elif rid.lower() in RNAName:
                write_infos_into_file(writer, raw_id, RNAName[rid.lower()], 'raw_id-name')
            elif inter is not None and inter.lower() in RNAName:
                write_infos_into_file(writer, raw_id, RNAName[inter.lower()], 'interactor-name')
            elif inter is not None and inter.lower() in RNAXref:
                write_infos_into_file(writer, raw_id, RNAXref[inter.lower()], 'interactor-xrefs')
    tsv_file.close()

    print("######### Start: Cypher #########")
    query = f'Match (p1:rna_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:RNA{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.RNAInter = "yes" Create (p1)-[:associateRNA{{how_mapped:line.how_mapped  }}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/RNAinter/{file_name}',
                                              query)
    cypher_file.write(query)

    print("######### End: Cypher #########")


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnaInter')
    print(datetime.datetime.now())
    create_connection_with_neo4j()
    print(datetime.datetime.now())
    rna_RNAInter()
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
