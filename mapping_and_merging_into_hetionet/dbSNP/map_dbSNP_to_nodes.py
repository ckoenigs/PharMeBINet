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


# dictionary variant identifier to resources and xrefs
dict_identifier_to_resource_and_xrefs = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_variant_from_database_and_add_to_dict():
    query = "MATCH (n:GeneVariant) RETURN n.identifier, n.resource, n.xrefs"
    results = g.run(query)
    for identifier, resource, xrefs, in results:
        dict_identifier_to_resource_and_xrefs[identifier] = [resource, xrefs]

# cypher file
cypher_file = open('output_mapping/cypher.cypher', 'w', encoding='utf-8')

def generate_files(path_of_directory):
    """
    generate cypher file and csv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'output_mapping/gene_variant_to_variant'
    file = open( file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['dbsnp_id', 'variant_id', 'resource', 'xrefs']
    csv_mapping.writerow(header)

    information_query = '''MATCH (p:snp_dbSNP) WITH DISTINCT keys(p) AS keys
    UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
    RETURN allfields;'''

    results = g.run(information_query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/dbSNP/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:snp_dbSNP{identifier:line.dbsnp_id}), (v:Variant{identifier:line.variant_id}) Set '''
    for property, in results:
        if property in ['is_alt', 'license', 'is_top_level', 'last_update_build_id', 'deleted_sequence', 'identifier',
                        'is_patch', 'is_chromosome', 'xrefs','clinical_variant_ids']:
            continue
        query += 'v.' + property + '=n.'+ property + ', '

    query += '''v.dbsnp="yes", v.resource=split(line.resource,"|"), v.source='dbSNP', v.license='https://www.ncbi.nlm.nih.gov/home/about/policies/' ,v.xrefs=split(line.xrefs,"|") Create (v)-[:equal_to_drugbank_variant]->(n);\n'''

    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    return csv_mapping

# dictionary  variant type to csv
dict_variant_typ_to_csv_file={}

# dictionary variant type to variant label
dict_variant_typ_to_label={
    'snv': 'SingleNucleotideVariant', #'SingleNucleotideVariation'
    'delins':'Indel',
    'ins':'Insertion',
    'del':'Deletion',
    'mnv':' MultipleNucleotideVariation'
}

def generate_label_csv_and_query(variant_type):
    """
    generate csv file for label
    :param variant_type: string
    :return:
    """
    file_name='output_mapping/'+variant_type+'.tsv'
    file=open(file_name,'w')
    csv_writer=csv.writer(file,delimiter='\t')
    csv_writer.writerow(['identifier'])
    dict_variant_typ_to_csv_file[variant_type]=csv_writer

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/dbSNP/%s" As line FIELDTERMINATOR '\\t' 
            Match (v:Variant{identifier:line.identifier}) Set v:%s;\n'''
    if variant_type in dict_variant_typ_to_label:
        label=dict_variant_typ_to_label[variant_type]
    else:
        print(variant_type)
        sys.exit('need a label')
    query=query %(path_of_directory, file_name, label)
    cypher_file.write(query)

'''
Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
'''


def load_all_variants_and_finish_the_files(csv_mapping):
    query = "MATCH (n:snp_dbSNP) RETURN n"
    results = g.run(query)
    counter_map = 0
    counter_not_mapped = 0
    counter_new = 0
    for node, in results:
        identifier = node['identifier']
        [resource, xrefs] = dict_identifier_to_resource_and_xrefs['rs' + identifier]
        variant_type = node['variant_type']
        dbxrefs= node['xrefs'] if 'xrefs' in node else []
        clinical_variant_ids = ['ClinVar:'+x for x in node['clinical_variant_ids']] if 'clinical_variant_ids' in node else []
        dbxrefs.extend(clinical_variant_ids)
        dbxrefs.extend(xrefs)
        resource.append('dbSNP')
        resource='|'.join(sorted(set(resource)))

        dbxrefs= '|'.join(go_through_xrefs_and_change_if_needed_source_name(dbxrefs,'Variant'))
        csv_mapping.writerow([identifier, 'rs'+identifier, resource, dbxrefs])

        if not variant_type in dict_variant_typ_to_csv_file:
            generate_label_csv_and_query(variant_type)
        dict_variant_typ_to_csv_file[variant_type].writerow(['rs'+identifier])

    print('not mapped:', counter_not_mapped)
    print('counter new:', counter_new)
    print('counter mapped:', counter_map)


def main():
    print(datetime.datetime.utcnow())
    global path_of_directory, license
    if len(sys.argv) < 2:
        sys.exit('need  path to directory gene variant and license')
    path_of_directory = sys.argv[1]
    license= sys.argv[2]
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

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all variation from database')

    load_all_variants_and_finish_the_files(csv_mapping)

    # delete the Variant nodes which have an not real dbSNP or a merged rs id (is not known which is which only for the drugbank one)
    query='''Match p=(n:Variant) Where n.identifier starts with 'rs' and not (n)--(:snp_dbSNP) and not exists(n.drugbank) Detach Delete n;\n'''
    cypher_file.write(query)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
