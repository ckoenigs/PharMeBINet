import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# cypher file
cypher_file = open("output/cypher.cypher", "w", encoding="utf-8")


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

    return g


def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped, dictionary):
    """
    Each mapping pair is written into the TSV file
    :param csv_writer:
    :param raw_id:
    :param mapped_ids:
    :param how_mapped:
    :param dictionary:
    :return:
    """
    for map_id in mapped_ids:
        csv_writer.writerow(
            [raw_id, map_id, pharmebinetutils.resource_add_and_prepare(dictionary[map_id], "RNADisease"), how_mapped])


def disease_RNAdisease():
    '''
    Mapping between Disease and disease_RNADisease
    '''

    print("######### load_from_database ##################")
    disease = {}
    disease_xref = {}
    disease_ids = {}
    disease_name = {}

    query = "MATCH (n:Disease) RETURN n.identifier, n.alternative_ids, n.xrefs, n.resource, n.name, n.synonyms"
    result = g.run(query)

    for record in result:
        [id, ids, xrefs, resource, name, synonym] = record.values()
        disease[id] = resource

        if xrefs is not None:
            for x in xrefs:
                if "MESH:" in x:
                    pubid = x[5:]
                    if pubid not in disease_xref:
                        disease_xref[pubid] = [id]
                    elif id not in disease_xref[pubid]:
                        disease_xref[pubid].append(id)
        if ids is not None:
            for y in ids:
                if y not in disease_ids:
                    disease_ids[y] = [id]
                elif id not in disease_ids[y]:
                    disease_ids[y].append(id)
        if name is not None:
            if name.lower() not in disease_name:
                disease_name[name.lower()] = [id]
            elif id not in disease_name[name.lower()]:
                disease_name[name.lower()].append(id)
        if synonym is not None:
            for syn in synonym:
                syn_name = pharmebinetutils.prepare_obo_synonyms(syn)
                if syn_name.lower() not in disease_name:
                    disease_name[syn_name.lower()] = [id]
                elif id not in disease_name[syn_name.lower()]:
                    disease_name[syn_name.lower()].append(id)

    symptom = {}
    symptom_name = {}
    symptom_xref = {}

    query = "MATCH (n:Symptom) RETURN n.identifier, n.resource, n.name, n.synonyms, n.xrefs"
    result = g.run(query)

    for record in result:
        [id, resource, name, synonym, xref] = record.values()
        symptom[id] = resource

        if name is not None:
            if name.lower() not in symptom_name:
                symptom_name[name.lower()] = [id]
            elif id not in symptom_name[name.lower()]:
                symptom_name[name.lower()].append(id)
        if synonym is not None:
            for syn in synonym:
                if syn.lower() not in symptom_name:
                    symptom_name[syn.lower()] = [id]
                elif id not in symptom_name[syn.lower()]:
                    symptom_name[syn.lower()].append(id)
        if xref is not None:
            for x in xref:
                if "MESH:" in x:
                    mid = x[5:]
                    if mid not in symptom_xref:
                        symptom_xref[mid] = [id]
                    else:
                        symptom_xref[mid].append(id)

    file_name = 'disease/disease_RNADiseaseedges.tsv'
    file_name_symptom = 'disease/disease_Symptom_edges.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        with open(file_name_symptom, 'w', newline='') as tsv_file1:
            writer = csv.writer(tsv_file, delimiter='\t')
            writer1 = csv.writer(tsv_file1, delimiter='\t')
            line = ["id1", "id2", "resource", "how_mapped"]
            writer.writerow(line)
            writer1.writerow(line)

            query = "MATCH (n:disease_RNADisease) RETURN n.DO_ID, n.MeSH_ID, n.Disease_Name"
            result = g.run(query)
            for record in result:
                [doid, mesh, name] = record.values()
                map = False

                if name.lower() in disease_name:
                    map = True
                    write_infos_into_file(writer, name, disease_name[name.lower()], "Disease_Name-Name/Synonyms",
                                          disease)
                elif name.lower() in symptom_name:
                    map = True
                    write_infos_into_file(writer1, name, symptom_name[name.lower()],
                                          "Disease_Name-Symptom Name/Synonyms", symptom)

                if map == False and mesh is not None:
                    for x in mesh:
                        if x in symptom:
                            map = True
                            write_infos_into_file(writer1, name, [x], "Disease_Mesh-Symptom_ID", symptom)

                # not good mapping ids
                if name.lower() in ['inflammation']:
                    continue
                if map == False and doid is not None:
                    for x in doid:
                        if x in disease_ids:
                            map = True
                            write_infos_into_file(writer, name, disease_ids[x], 'DO_ID-alternativeids', disease)
                if map == False and mesh is not None:
                    for y in mesh:
                        if y in disease_xref:
                            map = True
                            write_infos_into_file(writer, name, disease_xref[y], 'Mesh_Id-Diseasexrefs', disease)

        tsv_file.close()
        tsv_file1.close()

    print("######### Start: Cypher #########")
    query = f'Match (p1:disease_RNADisease{{Disease_Name:line.id1}}),(p2:Disease{{identifier:line.id2}}) SET p2.resource = split(line.resource,"|"), p2.rnadisease = "yes" Create (p1)-[:associateRNADisease_disease{{how_mapped:line.how_mapped}}]->(p2)'

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/RNAdisease/{file_name}',
                                              query)
    cypher_file.write(query)

    query = f'Match (p1:disease_RNADisease{{Disease_Name:line.id1}}),(p2:Symptom{{identifier:line.id2}}) SET p2.resource = split(line.resource,"|"), p2.rnadisease = "yes" Create (p1)-[:associateRNADisease_Symptom{{how_mapped:line.how_mapped}}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/RNAdisease/{file_name_symptom}',
                                              query)
    cypher_file.write(query)
    print("######### End: Cypher #########")


def rna_RNAdisease():
    '''
    Mapping between RNA and rna_RNADisease
    '''

    print("######### load_from_database #########")
    rna = {}
    rna_xref = {}
    dict_gene_name_to_identifiers = {}
    dict_product_name_to_identifiers = {}

    query = "MATCH (n:RNA) RETURN n.identifier, n.gene, n.product, n.xrefs, n.resource"
    result = g.run(query)

    for id, name, product, xrefs, resource, in result:
        rna[id] = resource

        if xrefs is not None:
            for x in xrefs:
                result = x.split(":")[1]
                pharmebinetutils.add_entry_to_dict_to_set(rna_xref, result, id)
        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_name_to_identifiers, name, id)
        if product is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_product_name_to_identifiers, product, id)

    dict_gene_symbol_to_identifiers = {}

    query = "MATCH (m:Gene)--(n:RNA) RETURN n.identifier, m.gene_symbols"
    result = g.run(query)

    for record in result:
        [id, gene_symbols] = record.values()

        if gene_symbols :
            for x in gene_symbols:
                pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_identifiers, x, id)

    file_name = 'rna/rna_RNADiseaseedges.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["id1", "id2", "resource", "how_mapped"]
        writer.writerow(line)

        query = "MATCH (n:rna_RNADisease) RETURN n.RNA_Symbol"
        result = g.run(query)
        counter = 0
        counter_mapped = 0
        for record in result:
            counter += 1
            [symbol] = record.values()
            if symbol in dict_gene_name_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, symbol, dict_gene_name_to_identifiers[symbol], 'Symbol_Gene_Name', rna)
            elif symbol in dict_product_name_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, symbol, dict_product_name_to_identifiers[symbol], 'Symbol_Product_Name', rna)
            elif symbol in dict_gene_symbol_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, symbol, dict_gene_symbol_to_identifiers[symbol], 'Symbol_Gene_Symbol_to_rna', rna)

            # elif symbol in RNAXref:
            #     # the AC identifier mapping is not good
            #     if symbol.startswith('AC'):
            #         continue
            #     write_infos_into_file(writer, symbol, RNAXref[symbol], 'Symbol-Xrefs', RNA)
        print('number of rnas', counter)
        print('number of mapped rnas', counter_mapped)
        tsv_file.close()

    print("######### Start: Cypher #########")
    query = f'Match (p1:rna_RNADisease{{RNA_Symbol:line.id1}}),(p2:RNA{{identifier:line.id2}}) SET p2.resource = split(line.resource,"|"), p2.rnadisease = "yes" Create (p1)-[:associateRNADisease_rna{{how_mapped:line.how_mapped}}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/RNAdisease/{file_name}',
                                              query)
    cypher_file.write(query)
    print("######### End: Cypher #########")


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnadisease')

    print(datetime.datetime.now(), '#' * 20)
    create_connection_with_neo4j()
    print(datetime.datetime.now(), '#' * 20)
    disease_RNAdisease()
    print(datetime.datetime.now(), '#' * 20)
    rna_RNAdisease()

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
