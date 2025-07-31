import datetime
import sys, csv

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
    g = driver.session(database='graph')


# dictionary uniprot_id to resource
dict_node_id_to_resource = {}



def generate_files(label, cypher_file):
    """
    generate cypher file and tsv file
    :return: csv writer
    """
    # file from relationship between gene and variant
    file_name = 'output/go_rna_to_%s' % label
    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    tsv_mapping = csv.writer(file, delimiter='\t')
    header = ['identifier', 'other_id', 'resource', 'mapped_with']
    tsv_mapping.writerow(header)

    query = '''Match (n:gene_product_go{identifier:line.identifier}), (v:%s{identifier:line.other_id}) Set v.go='yes', v.resource=split(line.resource,"|") Create (v)-[:equal_to_go_%s{how_mapped:line.mapped_with}]->(n)'''
    query = query % (label, label.lower())
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/go/{file_name}.tsv',
                                              query)
    cypher_file.write(query)

    return tsv_mapping

# dictionary rnacentral id to RNA identifier
dict_rna_central_to_identifier={}

'''
Load all RNAs from database  and add them into a dictionary
'''


def load_rna_and_add_to_dictionary():
    query = "MATCH (n:RNA) RETURN n.identifier, n.resource, n.xrefs"
    results = g.run(query)
    for identifier, resource, xrefs, in results:

        dict_node_id_to_resource[identifier] = resource
        if xrefs:
            for xref in xrefs:
                if xref.startswith('RNAcentral:'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_rna_central_to_identifier, xref.split(':')[1], identifier)

    print('number of rnas:', len(dict_node_id_to_resource))


'''
Load all pharmacologic class of drugbank and map to the pc from my database and write into file
'''


def load_all_rna_form_go_and_map_and_write_to_file():
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    tsv_writer = generate_files('RNA', cypher_file)

    query = "MATCH (n:gene_product_go) RETURN n"
    results = g.run(query)
    counter = 0
    counter_not_mapped = 0
    for record in results:
        node = record.data()['n']
        counter += 1
        identifier = node['identifier']
        if identifier in dict_rna_central_to_identifier:
            for id_pharmebinet in dict_rna_central_to_identifier[identifier]:
                tsv_writer.writerow(
                    [identifier, id_pharmebinet,
                     pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[id_pharmebinet], 'GO'), 'id_mapped'])
        else:
            counter_not_mapped += 1


    print('all:', counter)
    print('not mapped:', counter_not_mapped)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path go rna')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all RNAs from database')

    load_rna_and_add_to_dictionary()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all rna from go and map')

    load_all_rna_form_go_and_map_and_write_to_file()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
