import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    # create connection with neo4j
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with pharmebinet RNA with identifier as key and value node as dictionary
dict_node_id_mirna_to_resource = {}
dict_node_id_pre_mirna_to_resource = {}

# dictionary mirbase id to identifier
dict_mirbase_id_to_miRNA = {}
dict_mirbase_id_to_pre_miRNA = {}


def load_pharmebinet_nodes_in(label, dict_xref_to_ids, dict_id_to_resource_and_xrefs):
    '''
    load in all miRNA/primary transcript from pharmebinet in a dictionary
    '''
    query = f'''MATCH (n:{label}) RETURN n'''
    results = g.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        xrefs = set(node['xrefs']) if 'xrefs' in node else set()
        for xref in xrefs:
            if xref.startswith('miRBase:'):
                mirbase_id = xref.rsplit(':', 1)[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_xref_to_ids, mirbase_id, identifier)
        dict_id_to_resource_and_xrefs[identifier] = [node['resource'], xrefs]

    print('number of gene nodes in pharmebinet:', len(dict_id_to_resource_and_xrefs))


def generate_files(label, additional_condition=''):
    '''
    Generate cypher and tsv for generating the new nodes and the relationships
    '''
    file_name = f'output/mapping_{label}.tsv'
    csvfile = open(file_name, 'w', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['rna_id', 'mirbase_id', 'how_mapped', 'resource', 'xrefs'])

    # generate cypher file
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = f''' Match (c:RNA{{ identifier:line.rna_id}}), (n:{label}{{id:line.mirbase_id}})  Create (c)-[:equal_to_miRBase_rna{{how_mapped:line.how_mapped}}]->(n) Set c.mirbase="yes", c.resource=split(line.resource,"|"), c.xrefs=split(line.xrefs,"|"), c.sequence=n.sequence {additional_condition} '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/miRBase/{file_name}',
                                              query)
    cypher_file.write(query)
    cypher_file.close()
    return writer


def map_to_RNA(label, writer, dict_mirbase_id_to_mapped_node, dict_id_to_resource, condition=''):
    """
    map miRNABase to RNA and write into TSV file
    :param label:
    :param writer:
    :return:
    """
    query = f'''MATCH (n:{label}) Where (n){condition}--(:miRBase_Species{{ncbi_taxid:9606}}) RETURN n.id, n.accession, n.xrefs '''
    results = g.run(query)

    counter = 0
    mapped = 0
    for record in results:
        counter += 1
        [identifier, mirbase_id, xrefs] = record.values()
        xrefs=xrefs if not xrefs is None else []
        if mirbase_id:
            if mirbase_id in dict_mirbase_id_to_mapped_node:
                for rna_id in dict_mirbase_id_to_mapped_node[mirbase_id]:
                    own_xrefs=dict_id_to_resource[rna_id][1]
                    own_xrefs=own_xrefs.union(xrefs)
                    writer.writerow([rna_id, identifier, 'mirBase_id',
                                     pharmebinetutils.resource_add_and_prepare(dict_id_to_resource[rna_id][0],
                                                                               'miRBase'), '|'.join(own_xrefs)])
                    mapped += 1
                    continue

    print('number of existing', label, counter)
    print('number of mapped ', label, mapped)


def load_and_map_miRBase_rna():
    """
    Load all human genes and try to map with entrez id and hgnc id. All mapped are written into a TSV file.
    :return:
    """
    writer_mirna = generate_files('miRBase_miRNA')
    writer_pre_mirna = generate_files('miRBase_pre_miRNA', additional_condition=', c.strand=n.strand, c.fold=n.fold, c.contig_start=n.contig_start, c.contig_end=n.contig_end, c.xsome=n.xsome, c.alignment=n.alignment ')

    map_to_RNA('miRBase_miRNA', writer_mirna, dict_mirbase_id_to_miRNA, dict_node_id_mirna_to_resource,
               condition='--(:miRBase_pre_miRNA)')
    map_to_RNA('miRBase_pre_miRNA', writer_pre_mirna, dict_mirbase_id_to_pre_miRNA, dict_node_id_pre_mirna_to_resource)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all miRNA/pre-miRNA from pharmebinet into a dictionary')

    load_pharmebinet_nodes_in('miRNA', dict_mirbase_id_to_miRNA, dict_node_id_mirna_to_resource)
    load_pharmebinet_nodes_in('PrimaryTranscript', dict_mirbase_id_to_pre_miRNA, dict_node_id_pre_mirna_to_resource)

    print(dict_node_id_mirna_to_resource['rna-MIR2054'])

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all ctd genes from neo4j into a dictionary')

    load_and_map_miRBase_rna()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
