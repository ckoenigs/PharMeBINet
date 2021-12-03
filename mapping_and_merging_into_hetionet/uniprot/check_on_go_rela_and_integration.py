from py2neo import Graph
import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary go to short form
dict_go = {'BiologicalProcess': 'bc', 'MolecularFunction': 'mf', 'CellularComponent': 'cc'}

# dictionary go to rela types which are general
dict_go_to_rela_types = {
    'BiologicalProcess': ["INVOLVED_IN_PiiBP", "PARTICIPATES_PpBP"],
    'MolecularFunction': ["ENABLES_PeMF", "CONTRIBUTES_TO_PctMF", "PARTICIPATES_PpMF"],
    'CellularComponent': ["PART_OF_PpoCC", "LOCATED_IN_PliCC", "PARTICIPATES_PpCC", "COLOCALIZES_WITH_PcwCC"]
}


def load_existing_pairs(label, dict_pair_to_resource):
    """
    Get all pairs for a specific label pair with a given relationship type and add to a set.
    :param label: string
    :param other_label: string
    :param rela_type: string
    :param dict_pair_to_resource: dictionary
    :return:
    """
    query = 'Match (n:%s)-[r]-(m:%s) Where  not exists(r.not) and type(r) in ["%s"] Return n.identifier, m.identifier, r.resource, type(r)' % (
        label, 'Protein', '","'.join(dict_go_to_rela_types[label]))
    results = graph_database.run(query)
    for node_id_1, node_id_2, resource, rela_type, in results:
        dict_pair_to_resource[(node_id_1, node_id_2)] = set(resource)
        if (node_id_1, node_id_2) not in dict_go_protein_to_rela_type:
            dict_go_protein_to_rela_type[(node_id_1, node_id_2)] = set()
        dict_go_protein_to_rela_type[(node_id_1, node_id_2)].add(rela_type)


def prepare_resource(set_of_resource):
    """
    Add resource to list
    :param set_of_resource:
    :return:
    """
    set_of_resource.add('UniProt')
    return '|'.join(sorted(set_of_resource))


def load_pair_edges(csv_mapped, csv_new, label, dict_pair_to_resource):
    """
    Load all pairs of go-.protein for this pair and write the into mapped or not mapped files.
    :param csv_mapped: csv writer
    :param csv_new: csv writer
    :param label: string
    :param dict_pair_to_resource: dictionary
    :return:
    """
    file = open('uniprot_go/db_uniprots_to_' + dict_go[label] + '.csv', 'r')
    csv_reader = csv.reader(file, delimiter=',')
    next(csv_reader)

    # set of all hmdb pairs
    set_of_used_pairs = set()

    # counter_mapped
    counter_mapped = 0

    # counter new
    counter_new = 0

    for line in csv_reader:
        go_id = line[1]
        uniprot_id = line[0]
        if (go_id, uniprot_id) in set_of_used_pairs:
            continue
        set_of_used_pairs.add((go_id, uniprot_id))
        if (go_id, uniprot_id) in dict_pair_to_resource:
            counter_mapped += 1
            csv_mapped.writerow([go_id, uniprot_id, prepare_resource(dict_pair_to_resource[(go_id, uniprot_id)])])
            if len(dict_go_protein_to_rela_type[(go_id, uniprot_id)]) > 1:
                print('multi rela types')
                print(go_id, uniprot_id)
                print(dict_go_protein_to_rela_type[(go_id, uniprot_id)])
        else:
            counter_new += 1
            csv_new.writerow([go_id, uniprot_id])

    print('number of ' + label + '  and Protein relationships in hetionet:' + str(
        len(set_of_used_pairs)))
    print('number of mapped edges:', counter_mapped)
    print('number of new edges:', counter_new)


#
dict_label_to_rela_short = {
    'BiologicalProcess': 'BP',
    'CellularComponent': 'CC',
    'MolecularFunction': 'MF',
}


def create_cypher_file(file_name, file_name_new, label):
    """
    Prepare mapping edges and creation cypher queries.
    :param file_name: string
    :param file_name_new: string
    :param label: string
    :return:
    """
    # b.resource=split(line.resource,'|'),
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line FIELDTERMINATOR "\\t" Match (g:Protein{identifier:line.node_id_2}),(b:%s{identifier:line.node_id_1}) Set  b.uniprot='yes' Create (g)-[:PARTICIPATES_Pp%s{resource:['UniProt'],source:'UniProt', uniprot:'yes', license:'CC BY 4.0', url:'https://www.uniprot.org/uniprot/'+line.node_id_2}]->(b);\n'''
    query = query % (file_name_new, label, dict_label_to_rela_short[label])
    cypher_file.write(query)

    query = '''LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/uniprot/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.node_id_1})-[r]-(c:Protein{identifier:line.node_id_2}) Where not exists(r.not) and type(r) in ["%s"] Set  r.resource=split(line.resource,'|'), r.uniprot='yes';\n'''
    query = query % (path_of_directory, file_name, label, '","'.join(dict_go_to_rela_types[label]))
    cypher_file.write(query)


def check_relationships_and_generate_file(label):
    """

    :param label:
    :return:
    """

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all relationships from metabolite/protein-node and hetionet_nodes into a dictionary')
    global dict_go_protein_to_rela_type
    # dictionary_go_protein_pair_to_rela_type
    dict_go_protein_to_rela_type = {}

    # file for mapped or not mapped identifier
    file_name = 'uniprot_go/edge_' + label + '_to_protein.tsv'

    file_edge_pro_or_meta_to_node = open(file_name, 'w', encoding="utf-8")
    csv_edge = csv.writer(file_edge_pro_or_meta_to_node, delimiter='\t', lineterminator='\n')
    csv_edge.writerow(['node_id_1', 'node_id_2', 'resource'])

    file_name_new = 'uniprot_go/edge_new_' + label + '_to_protein.tsv'

    file_edge_pro_or_meta_to_node_new = open(file_name_new, 'w', encoding="utf-8")
    csv_edge_new = csv.writer(file_edge_pro_or_meta_to_node_new, delimiter='\t', lineterminator='\n')
    csv_edge_new.writerow(['node_id_1', 'node_id_2'])

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all relationships from pairs from pharmebinet into a set')

    dict_pair_to_resource = {}

    load_existing_pairs(label, dict_pair_to_resource)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all relationships pairs of uniprot')

    load_pair_edges(csv_edge, csv_edge_new, label, dict_pair_to_resource)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, file_name_new, label)


def main():
    global path_of_directory, license
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path uniprot-go edges')

    global cypher_file
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('prepare for the different gos')

    cypher_file = open('output/cypher_edge_go.cypher', 'w', encoding="utf-8")

    for label in dict_go.keys():
        print(label)
        check_relationships_and_generate_file(label)

    cypher_file.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
