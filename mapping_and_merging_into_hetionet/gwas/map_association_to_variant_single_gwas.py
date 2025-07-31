import csv
import datetime
import os
import re, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# import create_connection_to_database_metabolite


# dictionary variant id to resource
dict_variant_id_to_resource = {}

# dictionary name to identifier
dict_name_to_id = {}

# dictionary dbSNP id to identifier
dbsnp_identifier_map = {}

dict_id_to_name = {}


def load_variants_from_database_and_add_to_dict():
    # Define the Cypher query to fetch dbSNP IDs and identifiers
    cypher_query = (
        "MATCH (n:Variant) Where n.identifier Starts with 'rs'  RETURN n.identifier AS identifier, n.xrefs as xrefs, n.resource AS resource, n.name as name, n.cytogenetic_location")
    results = g.run(cypher_query)
    for record in results:
        [identifier, xrefs, resource, name, location] = record.values()
        dict_variant_id_to_resource[identifier] = resource
        if xrefs:
            for xref in xrefs:
                if xref.startswith('dbSNP'):
                    dbsnp_id = xref.split(":")[1]  # Extract dbSNP ID
                    pharmebinetutils.add_entry_to_dict_to_set(dbsnp_identifier_map, dbsnp_id, identifier)

        name = name
        dict_id_to_name[identifier] = name
        if name:
            if len(name.split(':')) > 1:
                name = name.split(':')[1]
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_id, name.lower(), (identifier, location))


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'variant_to_Variant'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['variant_id', 'identifier', 'resource', 'mapping_method']
    file = open(file_path, 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    file_name_new = 'not_mapped.tsv'
    file_path_new = os.path.join(path_of_directory, file_name_new)
    file_new = open(file_path_new, "w", encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    csv_new.writerow(['variant_id', 'identifier'])

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    query = (f' Match (n:GWASCatalog_Association), (v:Variant{{'
             f'identifier:line.identifier}}) Where ID(n) =  toInteger(line.variant_id) Set v.gwas="yes", v.chromosome=n.chr_id, v.position=n.chr_position, v.resource=split(line.resource,"|") Create (v)-['
             f':equal_to_GWAS_variant{{mapped_with:line.mapping_method}}]->(n)')
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, 'a', encoding='utf-8')
    cypher_file.write(query)

    query = f' Match (n:GWASCatalog_Association) Where ID(n)=toInteger(line.variant_id) Merge (p:Variant :GeneVariant{{identifier:line.identifier}}) On Create Set p.chromosome=n.chr_id, p.position=n.chr_position , p.resource=["GWAS"], p.xrefs=["dbSNP:"+line.identifier], p.gwas="yes", p.source="dbSNP from GWAS", p.license="CC BY-NC 4.0 Deed"  Create (p)-[:equal_to_GWAS_variant{{mapped_with:"new"}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_new,
                                              query)
    cypher_file.write(query)

    return csv_mapping, csv_new


def load_all_GWAS_variants_and_finish_the_files(csv_mapping, csv_new):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """
    #  Where n.variation contains 'rs'
    query = "Match (n:GWASCatalog_Association) Where not n.snps contains ' x ' and not n.mapped_traits is null Return ID(n), n.snps, n.snp_gene_ids, n.strongest_snp_risk_allele, n.mapped_genes"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    counter_new = 0
    pattern = r'rs\d+'
    for record in results:
        [unique_id ,snp_id, ensg_id, stronges_alles, mapped_gene] = record.values()
        counter_all += 1
        rs_id = ''
        match = re.search(pattern, snp_id)
        if match:
            rs_id = match.group()
        # mapping
        # if rs_id == "rs368270856":
        # print(rs_id, dict_variant_id_to_resource[rs_id])

        is_mapped = False

        if rs_id in dbsnp_identifier_map:
            for variant_id in dbsnp_identifier_map[rs_id]:
                csv_mapping.writerow(
                    [unique_id, variant_id,
                     pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[variant_id], "GWAS"),
                     'dbSNP'])

        else:
            if rs_id:
                csv_new.writerow([unique_id, rs_id])
                counter_new += 1
                continue
            counter_not_mapped += 1
            print(snp_id)

    print('number of not-mapped variants:', counter_not_mapped)
    print('number of new variants:', counter_new)
    print('number of all variants:', counter_all)


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    # driver = create_connection_to_database_metabolite.database_connection_neo4j_driver()
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def main():
    global path_of_directory
    global source
    global home

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'variant/')

    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Variants from database')
    load_variants_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping, csv_new = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all GWAS variants from database')
    load_all_GWAS_variants_and_finish_the_files(csv_mapping, csv_new)

    driver.close()


if __name__ == "__main__":
    main()
