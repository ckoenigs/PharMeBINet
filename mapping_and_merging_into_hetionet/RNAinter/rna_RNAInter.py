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
    dict_mirBase_to_identifiers = {}
    dict_ensembl_to_identifiers = {}
    dict_name_to_identifiers = {}
    dict_gene_to_identifier = {}
    dict_product_to_identifiers = {}

    query = "MATCH (n:RNA) RETURN n.identifier, n.name,n.xrefs, n.resource, n.gene, n.product, labels(n)"
    result = g.run(query)

    for record in result:
        [identifier, name, xref, resource, gene, product, labels] = record.values()

        RNA[identifier] = resource

        is_miRNA = False if not 'miRNA' in labels else True

        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_identifiers, name.lower(), identifier)
        if product is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_product_to_identifiers, product, identifier)

        dict_gene_to_identifier[gene] = identifier
        if xref is not None:
            for x in xref:

                pubid = x.split(':', 1)[1]

                if x.startswith('miRBase'):
                    # avoid mirbase xrefs where the id is pr-RNA (MI****)
                    if is_miRNA and not pubid.startswith('MIMAT'):
                        continue
                    pharmebinetutils.add_entry_to_dict_to_set(dict_mirBase_to_identifiers, pubid, identifier)
                elif x.startswith('Ensembl'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_ensembl_to_identifiers, pubid, identifier)

    dict_ncbi_gene_id_to_identifier = {}
    dict_product_to_identifiers = {}

    query = "MATCH (m:Gene)--(n:RNA) RETURN n.identifier, m.identifier"
    result = g.run(query)

    for record in result:
        [identifier, gene_id] = record.values()
        pharmebinetutils.add_entry_to_dict_to_set(dict_ncbi_gene_id_to_identifier, gene_id, identifier)

    # save the identifier and the Raw_ID in a tsv file
    file_name = 'output/RNA_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["Raw_ID", "identifier", "resource", "how_mapped"]
        writer.writerow(line)

        query = "MATCH (n:rna_RNAInter) RETURN n.Raw_ID, n.Interactor"
        result = g.run(query)

        counter = 0
        counter_mapped = 0
        for record in result:
            [raw_id, inter] = record.values()
            counter += 1
            source = ''
            if raw_id is not None:
                rid_split = raw_id.split(":", 1)
                if len(rid_split) == 2 and len(rid_split[1]) > 2:
                    rid = rid_split[1]
                else:
                    rid = raw_id
                source = rid_split[0]

            # manual check that the gene symbol and the ensemble id are not fitting and no ensemble gene mapping method
            # exist!
            if rid == 'ENSG00000088298':
                continue

            if source == 'Ensembl' and rid in dict_ensembl_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, dict_ensembl_to_identifiers[rid], 'ensembl')
            elif source == 'miRBase' and rid in dict_mirBase_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, dict_mirBase_to_identifiers[rid], 'mirbase')
            elif source == "NCBI" and rid in dict_ncbi_gene_id_to_identifier:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, dict_ncbi_gene_id_to_identifier[rid], 'ncbi_gene')

            elif source == 'miRBase' and inter in dict_product_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, dict_product_to_identifiers[inter], 'inter_product')
            elif raw_id in dict_gene_to_identifier:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, [dict_gene_to_identifier[raw_id]], 'raw_id_gene')
            elif inter in dict_gene_to_identifier:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, [dict_gene_to_identifier[inter]], 'inter_gene')
            elif raw_id in dict_name_to_identifiers:
                counter_mapped += 1
                write_infos_into_file(writer, raw_id, dict_name_to_identifiers[rid], 'name')

    tsv_file.close()
    print('number of nodes', counter)
    print('number of mapped nodes', counter_mapped)

    print("######### Start: Cypher #########")
    query = f'Match (p1:rna_RNAInter{{Raw_ID:line.Raw_ID}}),(p2:RNA{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.rnainter = "yes" Create (p1)-[:associateRNA{{how_mapped:line.how_mapped  }}]->(p2)'
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
