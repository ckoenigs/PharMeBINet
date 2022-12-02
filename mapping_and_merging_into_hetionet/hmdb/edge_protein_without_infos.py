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

# dictionary go to rela types which are general
dict_go_to_rela_types = {
    'BiologicalProcess': ["INVOLVED_IN_PiiBP", "PARTICIPATES_PpBP"],
    'MolecularFunction': ["ENABLES_PeMF", "CONTRIBUTES_TO_PctMF", "PARTICIPATES_PpMF"],
    'CellularComponent': ["PART_OF_PpoCC", "LOCATED_IN_PliCC", "PARTICIPATES_PpCC", "COLOCALIZES_WITH_PcwCC"]
}

def load_existing_pairs(label, other_label, dict_pair_to_resource):
    """
    Get all pairs for a specific label pair with a given relationship type and add to a set.
    :param label: string
    :param other_label: string
    :param dict_pair_to_resource: dictionary
    :return:
    """
    if other_label not in dict_go_to_rela_types:
        query = 'Match (n:%s)-[r]-(m:%s)  Where not exists(r.not) Return n.identifier, m.identifier, r.resource' % (
            label, other_label)
    else:
        query = 'Match (n:%s)-[r]-(m:%s) Where  not exists(r.not) and type(r) in ["%s"] Return n.identifier, m.identifier, r.resource' % (
            label, other_label, '","'.join(dict_go_to_rela_types[other_label]))
    # query = 'Match (n:%s)-[r:%s]-(m:%s) Return n.identifier, m.identifier, r.resource' % (label, rela_type, other_label)
    results = graph_database.run(query)
    for node_id_1, node_id_2, resource, in results:
        dict_pair_to_resource[(node_id_1, node_id_2)] = set(resource)


def prepare_resource(set_of_resource):
    """
    Add resource to list
    :param set_of_resource:
    :return:
    """
    set_of_resource.add('HMDB')
    return '|'.join(sorted(set_of_resource))


def load_pair_edges(csv_mapped, csv_new, label, own_label_hmdb, other_hmdb_label, other_label,
                    dict_pair_to_resource):
    """
    Load all pairs of hmdb for this pair and write the into mapped or not mapped files.
    :param csv_mapped: csv writer
    :param csv_new: csv writer
    :param label: string
    :param own_label_hmdb: string
    :param other_hmdb_label: string
    :param other_label: string
    :param dict_pair_to_resource: dictionary
    :return:
    """
    query = '''MATCH (p:%s)-[]-(r:%s)-[v]-(n:%s)-[]-(b:%s) RETURN p.identifier, b.identifier, r.identifier'''
    query = query % (label, own_label_hmdb, other_hmdb_label, other_label)
    print(query)
    results = graph_database.run(query)

    # set of all hmdb pairs
    set_of_used_pairs = set()

    # counter_mapped
    counter_mapped = 0

    # counter new
    counter_new = 0

    for node_id_1, node_id_2, hmdb_id, in results:
        if (node_id_1, node_id_2) in set_of_used_pairs:
            continue
        set_of_used_pairs.add((node_id_1, node_id_2))
        if (node_id_1, node_id_2) in dict_pair_to_resource:
            counter_mapped += 1
            csv_mapped.writerow([node_id_1, node_id_2, prepare_resource(dict_pair_to_resource[(node_id_1, node_id_2)])])
        else:
            counter_new += 1
            csv_new.writerow([node_id_1, node_id_2, hmdb_id])

    print('number of ' + label + '  and ' + other_label + ' relationships in pharmebinet:' + str(
        len(set_of_used_pairs)))
    print('number of mapped edges:', counter_mapped)
    print('number of new edges:', counter_new)


'''
generate new relationships between protein/metabolite and nodes that have edges in smpdb 
'''


def create_cypher_file(file_name, file_name_new, label, node_pharmebinet_label, direction_first, direction_last,
                       rela_name):
    """
    Prepare mapping edges and creation cypher queries.
    :param file_name: string
    :param file_name_new: string
    :param label: string
    :param node_pharmebinet_label: string
    :param rela_name: string
    :param direction_first: string
    :param direction_last: string
    :return:
    """
    if label=='Metabolite' or node_pharmebinet_label=='Pathway':
        query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.node_id_1}),(c:%s{identifier:line.node_id_2}) CREATE (d)%s[: %s{ resource: ['HMDB'], hmdb: "yes", license:"Creative Commons (CC) Attribution-NonCommercial (NC) 4.0 International Licensing ", url:"https://hmdb.ca/%s/"+line.hmdb_id, source:"HMDB"}]%s(c);\n'''
        query = query % (path_of_directory, file_name_new, label, node_pharmebinet_label, direction_first, rela_name,
                         'proteins' if label == 'Protein' else 'metabolites', direction_last)
        cypher_file.write(query)

    if node_pharmebinet_label not in dict_go_to_rela_types:
        query = '''LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.node_id_1})-[r]-(c:%s{identifier:line.node_id_2}) Where not exists(r.not) Set  r.resource=split(line.resource,'|'), r.hmdb='yes';\n'''
        query = query % (path_of_directory, file_name, label, node_pharmebinet_label)
    else:
        print('GOs')
        query = '''LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.node_id_1})-[r]-(c:%s{identifier:line.node_id_2}) Where not exists(r.not) and type(r) in ["%s"] Set  r.resource=split(line.resource,'|'), r.hmdb='yes';\n'''
        query = query % (path_of_directory, file_name, label, node_pharmebinet_label, '","'.join(dict_go_to_rela_types[node_pharmebinet_label]))
    cypher_file.write(query)


def check_relationships_and_generate_file(label, own_hmdb_label, other_node_hmdb_label, node_pharmebinet_label,
                                          directory, direction_first, direction_last, rela_name):
    """

    :param label: string
    :param own_hmdb_label: string
    :param other_node_hmdb_label: striing
    :param node_pharmebinet_label: string
    :param directory: dictionary
    :param direction_first: string
    :param direction_last: string
    :param rela_name: string
    :return:
    """

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from metabolite/protein-node and pharmebinet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name = directory + '/edge_' + label + '_to_' + other_node_hmdb_label + '.tsv'

    file_edge_pro_or_meta_to_node = open(file_name, 'w', encoding="utf-8")
    csv_edge = csv.writer(file_edge_pro_or_meta_to_node, delimiter='\t', lineterminator='\n')
    csv_edge.writerow(['node_id_1', 'node_id_2', 'resource'])

    file_name_new = directory + '/edge_new_' + label + '_to_' + other_node_hmdb_label + '.tsv'

    file_edge_pro_or_meta_to_node_new = open(file_name_new, 'w', encoding="utf-8")
    csv_edge_new = csv.writer(file_edge_pro_or_meta_to_node_new, delimiter='\t', lineterminator='\n')
    csv_edge_new.writerow(['node_id_1', 'node_id_2', 'hmdb_id'])

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships from pairs from pharmebinet into a set')

    dict_pair_to_resource = {}

    load_existing_pairs(label, node_pharmebinet_label, dict_pair_to_resource)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all relationships pairs of hmdb')

    load_pair_edges(csv_edge, csv_edge_new, label, own_hmdb_label, other_node_hmdb_label, node_pharmebinet_label,
                    dict_pair_to_resource)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(file_name, file_name_new, label, node_pharmebinet_label, direction_first, direction_last,
                       rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hmdb edges without info')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    dict_label_to_infos = {
        'Metabolite': [['Metabolite_HMDB', 'Pathway_HMDB', 'Pathway', '<-', '-', 'ASSOCIATES_PWaM']],
        # 'Protein': [
        #     ['Protein_HMDB', 'Pathway_HMDB', 'Pathway', '<-', '-', 'ASSOCIATES_PWaP'],
        #     ['Protein_HMDB', 'Biologicalprocess_HMDB', 'BiologicalProcess', '-', '->', 'PARTICIPATES_PpBP'],
        #     ['Protein_HMDB', 'Cellularcomponent_HMDB', 'CellularComponent', '-', '->', 'PARTICIPATES_PpCC'],
        #     ['Protein_HMDB', 'Molecularfunction_HMDB', 'MolecularFunction', '-', '->', 'PARTICIPATES_PpMF']
        # ]
    }

    directory = 'edge_protein_metabolite_without_info'
    cypher_file = open('output/cypher_edge.cypher', 'w', encoding="utf-8")

    for label, list_of_combinations in dict_label_to_infos.items():
        for list_element in list_of_combinations:
            own_hmdb_label = list_element[0]
            other_hmdb_label = list_element[1]
            node_label = list_element[2]
            direction_first = list_element[3]
            direction_last = list_element[4]
            rela_name = list_element[5]
            check_relationships_and_generate_file(label, own_hmdb_label, other_hmdb_label, node_label, directory,
                                                  direction_first, direction_last, rela_name
                                                  )

    cypher_file.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
