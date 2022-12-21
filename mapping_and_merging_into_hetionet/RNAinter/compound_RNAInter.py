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
cypher_file=open("output/cypher.cypher","a",encoding="utf-8")

def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped):
    for map_id in mapped_ids:
        csv_writer.writerow([raw_id, map_id, pharmebinetutils.resource_add_and_prepare(Chemical[map_id], "RNAInter"), how_mapped])


def compound_RNAInter():
    print("######### load_from_database ##################")
    global Chemical
    Chemical = {}
    ChemicalXref={}
    ChemicalName={}

    query = "MATCH (n:Chemical) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms"
    result = g.run(query)

    for id, xref, resource, name, syn, in result:

        Chemical[id] = resource

        if xref is not None:
            for x in xref:
                if "PubChem Compound" in x:
                    pubid = x.lstrip("PubChem Compound:")

                    if pubid not in ChemicalXref:
                        ChemicalXref[pubid] = [id]
                    else:
                        ChemicalXref[pubid].append(id)

        if name is not None:
            if name.lower() not in ChemicalName:
                ChemicalName[name.lower()] = [id]
            else:
                ChemicalName[name.lower()].append(id)


        if syn is not None:
            for s in syn:
                if s.lower() in ChemicalName and (s.lower() != name.lower()):
                    ChemicalName[s.lower()].append(id)

                elif s.lower() not in ChemicalName:
                    ChemicalName[s.lower()] = [id]


    CompoundChemical = {}

    # save the identifier and the Raw_ID in a tsv file
    file_name='output/Compound_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = [ "Raw_ID","identifier", "resource", "how_mapped"]
        writer.writerow(line)
        query = "MATCH (n:compound_RNAInter) RETURN n.Raw_ID, n.Interactor"
        result = g.run(query)

        for raw_id, inter, in result:
            rid = raw_id.split(":", 1)
            if len(rid) == 2:
                rid=rid[1]
            else:
                rid=raw_id

            if rid in Chemical:
                write_infos_into_file(writer,raw_id, [rid], 'raw_id')
            elif rid in ChemicalXref:
                write_infos_into_file(writer,raw_id, ChemicalXref[rid], 'xrefs')
            elif rid.lower() in ChemicalName:
                write_infos_into_file(writer,raw_id, ChemicalName[rid.lower()], 'raw_id_name')
            elif inter.lower() in ChemicalName:
                write_infos_into_file(writer,raw_id, ChemicalName[inter.lower()], 'name')


    print("######### Start: Cypher #########")
    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAinter/{file_name}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:compound_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:Chemical{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.rnainter="yes" Create (p1)-[:associateCompoundRNAInter{{how_mapped:line.how_mapped }}]->(p2);\n'
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

if __name__ == "__main__":
    # execute only if run as a script
    main()
