import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary name/synonym and dbsnp id to clinvar ids
dict_name_dbsnp_id_to_clinvar_id = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_variant_from_database_and_add_to_dict():
    query = "MATCH (n:Variant) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']

        name = node['name'].lower()
        if name not in dict_name_dbsnp_id_to_clinvar_id:
            dict_name_dbsnp_id_to_clinvar_id[name] = set()
        dict_name_dbsnp_id_to_clinvar_id[name].add(identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = synonym.lower()
            if synonym not in dict_name_dbsnp_id_to_clinvar_id:
                dict_name_dbsnp_id_to_clinvar_id[synonym] = set()
            dict_name_dbsnp_id_to_clinvar_id[synonym].add(identifier)

        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('dbSNP:'):
                dbSNO_ID = xref.split(':', 1)[1]
                if dbSNO_ID not in dict_name_dbsnp_id_to_clinvar_id:
                    dict_name_dbsnp_id_to_clinvar_id[dbSNO_ID] = set()
                dict_name_dbsnp_id_to_clinvar_id[dbSNO_ID].add(identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and csv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'gene_variant_to_variant'
    file = open('gene_variant/' + file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['gene_variant_drugbank', 'variant_id']
    csv_mapping.writerow(header)

    # file generate new variant
    file_name_new = 'new_variant'
    file_new = open('gene_variant/' + file_name_new + '.tsv', 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header = ['variant_id', 'xrefs']
    csv_new.writerow(header)
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/gene_variant/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:Mutated_protein_gene_DrugBank{identifier:line.gene_variant_drugbank}), (v:Variant{identifier:line.variant_id}) Set v.drugbank="yes", v.resource=v.resource+"DrugBank" Create (v)-[:equal_to_drugbank_variant]->(n);\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/gene_variant/%s.tsv" As line FIELDTERMINATOR '\\t' 
            Match (n:Mutated_protein_gene_DrugBank{identifier:line.variant_id}) Create (v:Variant :GeneVariant{identifier:line.variant_id, defining_change:n.defining_change, gene_symbol:n.gene_symbol, license:"%s", allele:n.allele, protein_name:n.protein_name, drugbank:"yes",  source:"dbSNP from DrugBank", resource:["DrugBank"] ,xrefs:split(line.xrefs,"|") }) Create (v)-[:equal_to_drugbank_variant]->(n);\n'''
    query = query % (path_of_directory, file_name_new, license)
    cypher_file.write(query)

    return csv_mapping, csv_new


'''
Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
'''


def load_all_variants_and_finish_the_files(csv_mapping, csv_new):
    query = "MATCH (n:Mutated_protein_gene_DrugBank) RETURN n"
    results = g.run(query)
    counter_map = 0
    counter_not_mapped = 0
    counter_new = 0
    for node, in results:
        identifier = node['identifier']
        if identifier in dict_name_dbsnp_id_to_clinvar_id:
            counter_map += 1
            for variant in dict_name_dbsnp_id_to_clinvar_id[identifier]:
                csv_mapping.writerow([identifier, variant])
        else:
            if 'allele' in node:
                allele = node['allele'].lower()
                if allele in dict_name_dbsnp_id_to_clinvar_id:
                    counter_map += 1
                    for variant in dict_name_dbsnp_id_to_clinvar_id[allele]:
                        csv_mapping.writerow([identifier, variant])
                    continue
                else:
                    counter_not_mapped += 1
            else:
                counter_not_mapped += 1
            if 'rs_id' in node:
                counter_new += 1
                if node['rs_id'] != identifier:
                    print('oh no')
                xrefs = ['dbSNP:' + identifier]
                if 'uniprot_id' in node:
                    xrefs.append('UniProt:' + node['uniprot_id'])
                xrefs = go_through_xrefs_and_change_if_needed_source_name(xrefs, 'dbSNP')
                csv_new.writerow([identifier, '|'.join(xrefs)])

    print('not mapped:', counter_not_mapped)
    print('counter new:', counter_new)
    print('counter mapped:', counter_map)


def main():
    print(datetime.datetime.utcnow())
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need license and path to directory gene variant')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all Variant from database')

    load_variant_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher and csv file')

    csv_mapping, csv_new = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all variation from database')

    load_all_variants_and_finish_the_files(csv_mapping, csv_new)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
