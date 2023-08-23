import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped, pubchem_id):
    """
    Write mapped pair into the file
    :param csv_writer:
    :param raw_id:
    :param mapped_ids:
    :param how_mapped:
    :param pubchem_id
    :return:
    """
    for map_id in mapped_ids:
        csv_writer.writerow(
            [raw_id, map_id, pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[map_id], "TTD"),
             how_mapped, pubchem_id])


def load_chemical_information():
    """
    Load chemical information into different dictionaries
    :return:
    """
    global dict_chemical_id_to_resource, dict_name_to_chemical_ids, dict_inchikey_to_chemical_ids
    global dict_pubchem_c_ids_to_identifier, dict_smiles_to_chemicals
    dict_chemical_id_to_resource = {}
    dict_name_to_chemical_ids = {}
    dict_inchikey_to_chemical_ids = {}
    dict_smiles_to_chemicals = {}
    dict_pubchem_c_ids_to_identifier = {}

    query = "MATCH (n:Chemical) RETURN n.identifier, n.xrefs, n.resource"
    result = g.run(query)

    for record in result:
        [identifier, xrefs, resource] = record.values()

        dict_chemical_id_to_resource[identifier] = resource

        if xrefs is not None:
            for x in xrefs:
                if "PubChem Compound" in x:
                    pubchem_compound = x.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_pubchem_c_ids_to_identifier, pubchem_compound,
                                                              identifier)


def compound_ttd_mapping():
    """
    Create TSV file. Then load the compounds of TTD and map it to Chemical. The mapped ones are written into the TSV
    file. In the last step the cypher queryis prepared and written into the cypher file.
    :return:
    """
    file_name = 'drug/compound_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["node_id", "identifier", "resource", "how_mapped", 'pubchem_cid']
        writer.writerow(line)
        query = "MATCH (n:TTD_Compound) RETURN n.id, n.pubchem_cid"
        result = g.run(query)

        counter = 0
        counter_mapped = 0
        for record in result:
            [node_id, pubchem_cid] = record.values()
            counter += 1
            mapping_found = False

            if pubchem_cid is not None:
                if pubchem_cid in dict_pubchem_c_ids_to_identifier:
                    mapping_found = True
                    write_infos_into_file(writer, node_id, dict_pubchem_c_ids_to_identifier[pubchem_cid], 'pubchem',
                                          pubchem_cid)

            if mapping_found:
                counter_mapped += 1
                continue

    print('number of nodes:', counter)
    print('number of mapped nodes:', counter_mapped)
    print("######### Start: Cypher #########")

    # cypher file
    with open("output/cypher.cypher", "a", encoding="utf-8") as cypher_file:

        query = f'Match (p1:TTD_Compound{{id:line.node_id}}),(p2:Chemical{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.ttd="yes" Create (p1)-[:equal_to_ttd_drug{{how_mapped:line.how_mapped }}]->(p2)'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                                  query)
        cypher_file.write(query)

    print("######### End: Cypher #########")


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd')

    print(datetime.datetime.now())
    print('create connection')
    create_connection_with_neo4j()

    print('#' * 50)
    print(datetime.datetime.now())
    print('load chemical information')
    load_chemical_information()

    print('#' * 50)
    print(datetime.datetime.now())
    print('map compound')
    compound_ttd_mapping()

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
