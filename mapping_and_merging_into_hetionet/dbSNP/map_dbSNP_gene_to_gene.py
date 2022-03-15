import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases


'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary variant identifier to resources and xrefs
dict_identifier_to_resource = {}

'''
Load all Genes from my database  and add them into a dictionary
'''


def load_gene_from_database_and_add_to_dict():
    query = "MATCH (n:Gene) RETURN n.identifier, n.resource"
    results = g.run(query)
    for identifier, resource,  in results:
        dict_identifier_to_resource[identifier] = resource

# cypher file
cypher_file = open('output_mapping/cypher.cypher', 'a', encoding='utf-8')

def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'output_mapping/gene_to_gene'
    file = open( file_name + '.tsv', 'w', encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['dbsnp_gene_id', 'gene_id', 'resource']
    csv_mapping.writerow(header)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/dbSNP/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:gene_dbSNP{identifier:line.dbsnp_gene_id}), (v:Gene{identifier:line.gene_id}) Set v.dbsnp="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_drugbank_variant]->(n);\n'''

    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    return csv_mapping


'''
Load all dbSNP gene ids  and map them. The integrate them into the right tsv, generate the queries
'''


def load_all_dbSnp_gene_and_finish_the_files(csv_mapping):
    query = "MATCH (n:gene_dbSNP) RETURN n"
    results = g.run(query)
    counter_map = 0
    counter_not_mapped = 0
    for node, in results:
        identifier = node['identifier']

        if identifier in dict_identifier_to_resource:
            counter_map+=1
            resource = dict_identifier_to_resource[identifier]
            resource.append('dbSNP')
            resource='|'.join(sorted(set(resource)))

            csv_mapping.writerow([identifier, identifier, resource])
        else:
            counter_not_mapped+=1
            print(identifier)


    print('not mapped:', counter_not_mapped)
    print('counter mapped:', counter_map)


def main():
    print(datetime.datetime.now())
    global path_of_directory, license
    if len(sys.argv) < 2:
        sys.exit('need  path to directory gene variant and license')
    path_of_directory = sys.argv[1]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Gene from database')

    load_gene_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all variation from database')

    load_all_dbSnp_gene_and_finish_the_files(csv_mapping)


    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
