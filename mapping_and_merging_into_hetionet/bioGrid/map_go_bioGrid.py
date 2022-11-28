import datetime
import sys, os
import csv
import general_function_bioGrid

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary gene id to resource
dict_node_id_to_resource = {}

# dictionary alternative id to go id
dict_alternative_ids_to_go_ids = {}


def load_nodes_from_database_and_add_to_dict(label):
    """
    Load all GO from my database  and add them into a dictionary
    """
    query = "MATCH (n:%s) RETURN n" % (label)
    results = g.run(query)

    for node, in results:
        identifier = node['identifier']
        dict_node_id_to_resource[identifier] = node['resource']
        alternative_ids = node['alternative_ids'] if 'alternative_ids' in node else []
        for alternative_id in alternative_ids:
            pharmebinetutils.add_entry_to_dict_to_set(dict_alternative_ids_to_go_ids, alternative_id, identifier)


def load_all_bioGrid_genes_and_finish_the_files(csv_mapping, label):
    """
    Load all bioGrid gene map to gene and write into file
    """

    query = "MATCH (n:%s) RETURN n" % label
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    for node, in results:
        counter_all += 1
        identifier = node['id']

        # mapping
        found_mapping = False
        if identifier in dict_node_id_to_resource:
            found_mapping = True
            csv_mapping.writerow(
                [identifier, identifier,
                 pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[identifier], "bioGrid"), 'id'])
        elif identifier in dict_alternative_ids_to_go_ids:
            for go_id in dict_alternative_ids_to_go_ids[identifier]:
                csv_mapping.writerow(
                    [identifier, go_id,
                     pharmebinetutils.resource_add_and_prepare(dict_node_id_to_resource[go_id], "bioGrid"),
                     'alternative_ids'])


        else:
            counter_not_mapped += 1
            print('not mapped')
            print(identifier)
    print('number of not-mapped nodes:', counter_not_mapped)
    print('number of all nodes:', counter_all)


######### MAIN #########
def main():
    print(datetime.datetime.now())

    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path biogrid go')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bioGrid')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'GO/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    dict_label_to_biogrid_label = {
        'BiologicalProcess': 'bioGrid_biological_process', 'CellularComponent': 'bioGrid_cellular_component'
    }

    for label in ['BiologicalProcess', 'CellularComponent']:
        biogrid_label = dict_label_to_biogrid_label[label]
        print('##########################################################################')

        print(datetime.datetime.now())
        print('Load all %s from database' % label)
        load_nodes_from_database_and_add_to_dict(label)

        print('##########################################################################')

        print(datetime.datetime.now())
        print('Generate cypher and tsv file')

        csv_mapping = general_function_bioGrid.generate_files(path_of_directory, 'mapping_%s.tsv' % label, source,
                                                              biogrid_label,
                                                              label, ['id'])

        print('##########################################################################')

        print(datetime.datetime.now())
        print('Load all DisGeNet %s from database' % label)
        load_all_bioGrid_genes_and_finish_the_files(csv_mapping, biogrid_label)


if __name__ == "__main__":
    # execute only if run as a script
    main()
