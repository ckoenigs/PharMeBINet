import csv, sys

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
    g = driver.session(database='graph')


# cypher file
cypher_file = open("output/cypher.cypher", "a", encoding="utf-8")


def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped):
    """
    Get all mapped compounds and write all information into the TSV file
    :param csv_writer:
    :param raw_id:
    :param mapped_ids:
    :param how_mapped:
    :return:
    """
    for map_id in mapped_ids:
        csv_writer.writerow(
            [raw_id, map_id, pharmebinetutils.resource_add_and_prepare(Chemical[map_id], "RNAInter"), how_mapped])


def compound_RNAInter():
    """
    First, load all chemicals into different dictionaries. Next, generate TSV file. Then, load the RNAinter compounds
    and amp the with different method to compound and write information into the TSV file. Last, the cypher query is
    generated and add to the cypher file.
    :return:
    """
    print("######### load_from_database ##################")
    global Chemical
    Chemical = {}
    chemical_xrefs = {}
    chemical_name = {}

    query = "MATCH (n:Chemical) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms"
    result = g.run(query)

    for record in result:
        [id, xref, resource, name, syn] = record.values()

        Chemical[id] = resource

        if xref is not None:
            for x in xref:
                if "PubChem Compound" in x:
                    pubid = x.lstrip("PubChem Compound:")

                    if pubid not in chemical_xrefs:
                        chemical_xrefs[pubid] = [id]
                    else:
                        chemical_xrefs[pubid].append(id)

        if name is not None:
            if name.lower() not in chemical_name:
                chemical_name[name.lower()] = [id]
            else:
                chemical_name[name.lower()].append(id)

        if syn is not None:
            for s in syn:
                if s.lower() in chemical_name and (s.lower() != name.lower()):
                    chemical_name[s.lower()].append(id)

                elif s.lower() not in chemical_name:
                    chemical_name[s.lower()] = [id]

    CompoundChemical = {}

    # save the identifier and the Raw_ID in a tsv file
    file_name = 'output/Compound_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["Raw_ID", "identifier", "resource", "how_mapped"]
        writer.writerow(line)
        query = "MATCH (n:compound_RNAInter) RETURN n.Raw_ID, n.Interactor"
        result = g.run(query)

        for record in result:
            [raw_id, inter] = record.values()
            rid = raw_id.split(":", 1)
            if len(rid) == 2:
                rid = rid[1]
            else:
                rid = raw_id

            if rid in Chemical:
                write_infos_into_file(writer, raw_id, [rid], 'raw_id')
            elif rid in chemical_xrefs:
                write_infos_into_file(writer, raw_id, chemical_xrefs[rid], 'xrefs')
            elif rid.lower() in chemical_name:
                write_infos_into_file(writer, raw_id, chemical_name[rid.lower()], 'raw_id_name')
            elif inter.lower() in chemical_name:
                write_infos_into_file(writer, raw_id, chemical_name[inter.lower()], 'name')

    print("######### Start: Cypher #########")
    query = f'Match (p1:compound_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:Chemical{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.rnainter="yes" Create (p1)-[:associateCompoundRNAInter{{how_mapped:line.how_mapped }}]->(p2)'
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

    create_connection_with_neo4j()
    compound_RNAInter()
    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
