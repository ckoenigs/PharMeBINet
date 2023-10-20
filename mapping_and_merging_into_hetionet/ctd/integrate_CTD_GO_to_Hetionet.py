import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with pharmebinet biological process with identifier as key and value the name
dict_biological_process_pharmebinet = {}
# dictionary with pharmebinet biological process with alternative id as key and value identifier
dict_biological_process_alternative_pharmebinet = {}

# dictionary with pharmebinet cellular component with identifier as key and value the name
dict_cellular_component_pharmebinet = {}
# dictionary with pharmebinet cellular component with alternative id as key and value identifier
dict_cellular_component_alternative_pharmebinet = {}

# dictionary with pharmebinet molecular function with identifier as key and value the name
dict_molecular_function_pharmebinet = {}
# dictionary with pharmebinet molecular function with alternative id as key and value identifier
dict_molecular_function_alternative_pharmebinet = {}

# dictionary go id to resource
dict_go_id_to_resource = {}

'''
get information and put the into a dictionary one norma identifier and one alternative identifier to normal identifier
'''


def get_information_and_add_to_dict(label, dict_pharmebinet, dict_alternative_ids_pharmebinet):
    query = '''MATCH (n:%s) RETURN n.identifier,n.name, n.alternative_ids, n.resource'''
    query = query % (label)
    results = g.run(query)

    for record in results:
        [identifier, name, alternative_ids, resource] = record.values()
        dict_pharmebinet[identifier] = name
        if alternative_ids:
            for alternative_id in alternative_ids:
                dict_alternative_ids_pharmebinet[alternative_id] = identifier
        dict_go_id_to_resource[identifier] = set(resource)


'''
load in all biological process, molecular function and cellular components from pharmebinet in a dictionary
'''


def load_pharmebinet_go_in():
    # fill dict for biological process
    get_information_and_add_to_dict('BiologicalProcess', dict_biological_process_pharmebinet,
                                    dict_biological_process_alternative_pharmebinet)

    # fill dict for molecular function
    get_information_and_add_to_dict('MolecularFunction', dict_molecular_function_pharmebinet,
                                    dict_molecular_function_alternative_pharmebinet)

    # fill dict for cellular components
    get_information_and_add_to_dict('CellularComponent', dict_cellular_component_pharmebinet,
                                    dict_cellular_component_alternative_pharmebinet)

    print('number of biological process nodes in pharmebinet:' + str(len(dict_biological_process_pharmebinet)))
    print('number of cellular component nodes in pharmebinet:' + str(len(dict_cellular_component_pharmebinet)))
    print('number of molecular function nodes in pharmebinet:' + str(len(dict_molecular_function_pharmebinet)))


# csv of nodes without ontology
file_without_ontology = open('GO/nodes_without_ontology.tsv', 'w')
csv_without_ontology = csv.writer(file_without_ontology, delimiter='\t')
csv_without_ontology.writerow(['id', 'ontology'])

'''
check if go is in pharmebinet or not
'''


def check_if_new_or_part_of_pharmebinet(pharmebinet_label, go_id, go_name, highestGOLevel):
    # is only used if the ontology is not existing
    found_with_alternative_id = False
    if pharmebinet_label == '':
        if go_id in dict_biological_process_pharmebinet:
            pharmebinet_label = 'Biological Process'
        elif go_id in dict_cellular_component_pharmebinet:
            pharmebinet_label = "Cellular Component"
        elif go_id in dict_molecular_function_pharmebinet:
            pharmebinet_label = 'Molecular Function'
        elif go_id in dict_biological_process_alternative_pharmebinet:
            found_with_alternative_id = True
            pharmebinet_label = 'Biological Process'
            alternative_id = go_id
            normal_id = dict_biological_process_alternative_pharmebinet[alternative_id]
        elif go_id in dict_cellular_component_alternative_pharmebinet:
            found_with_alternative_id = True
            pharmebinet_label = 'Cellular Component'
            alternative_id = go_id
            normal_id = dict_cellular_component_alternative_pharmebinet[alternative_id]
        elif go_id in dict_molecular_function_alternative_pharmebinet:
            found_with_alternative_id = True
            pharmebinet_label = 'Molecular Function'
            alternative_id = go_id
            normal_id = dict_molecular_function_alternative_pharmebinet[alternative_id]
        # if this is not found in pharmebinet then this is an old go id
        else:
            # print('should be delete?')
            # print(go_id)
            return
            # sys.exit(go_id)
        csv_without_ontology.writerow([go_id, pharmebinet_label])
    [dict_pharmebinet, dict_alternative_id_to_pharmebinet, dict_ctd_in_pharmebinet_alternative,
     dict_ctd_in_pharmebinet] = dict_process[pharmebinet_label]

    # check if this id is pharmebinet
    if go_id in dict_pharmebinet:
        if go_name == dict_pharmebinet[go_id]:
            dict_ctd_in_pharmebinet[go_id] = [go_name, highestGOLevel]
        else:
            # print('same id but different names')
            # print(go_id)
            # print(go_name)
            # print(dict_pharmebinet[go_id])
            dict_ctd_in_pharmebinet[go_id] = [go_name, highestGOLevel]
    # check if it is replaced by a new go id (this id will appear in the alternative ids of the new node)
    # is add to the alternative mapped dictionary
    elif go_id in dict_alternative_id_to_pharmebinet:
        dict_ctd_in_pharmebinet_alternative[go_id] = dict_alternative_id_to_pharmebinet[go_id]
    # if the ontology was unknown  then the  id is add to the alternative mapped dictionary and in the tsv
    # to set the ontology
    elif found_with_alternative_id:
        dict_ctd_in_pharmebinet_alternative[alternative_id] = normal_id
        csv_without_ontology.writerow([alternative_id, pharmebinet_label])
    # nodes which are not in go anymore
    else:
        return
        # print(go_id)
        # print(pharmebinet_label)
        # print('not good')


'''
load all ctd genes and check if they are in pharmebinet or not
'''


def load_ctd_go_in():
    query = '''MATCH (n:CTD_GO) RETURN n'''
    results = g.run(query)

    for record in results:
        go_node = record.data()['n']
        go_id = go_node['go_id']
        go_name = go_node['name']
        ontology = go_node['ontology'] if 'ontology' in go_node else ''
        highestGOLevel = go_node['highestGOLevel'] if 'highestGOLevel' in go_node else ''
        check_if_new_or_part_of_pharmebinet(ontology, go_id, go_name, highestGOLevel)

    print('number of existing biological process nodes:' + str(len(dict_ctd_biological_process_in_pharmebinet)))

    print('number of existing Molecular Function nodes:' + str(len(dict_ctd_molecular_function_in_pharmebinet)))

    print('number of existing Cellular Component nodes:' + str(len(dict_ctd_cellular_component_in_pharmebinet)))


# dictionary of ctd biological_process which are in pharmebinet with properties: name
dict_ctd_biological_process_in_pharmebinet = {}

# dictionary of ctd cellular_component which are in pharmebinet with properties: name
dict_ctd_cellular_component_in_pharmebinet = {}

# dictionary of ctd molecular_function which are in pharmebinet with properties: name
dict_ctd_molecular_function_in_pharmebinet = {}

# dictionary of ctd biological_process which are in pharmebinet with properties: name
dict_ctd_biological_process_in_pharmebinet_alternative = {}

# dictionary of ctd cellular_component which are in pharmebinet with properties: name
dict_ctd_cellular_component_in_pharmebinet_alternative = {}

# dictionary of ctd molecular_function which are in pharmebinet with properties: name
dict_ctd_molecular_function_in_pharmebinet_alternative = {}

# dictionary with for biological_process, cellular_component, molecular_function the right dictionaries
# first dictionary has all identifier in pharmebinet, the second has all alternative pharmebinet ids to there identifier,
# third list of all ctd ids which map with alternative ids, fourth dict of all ctd which mapped directly to pharmebinet
dict_process = {
    "Biological Process": [dict_biological_process_pharmebinet, dict_biological_process_alternative_pharmebinet,
                           dict_ctd_biological_process_in_pharmebinet_alternative,
                           dict_ctd_biological_process_in_pharmebinet],
    "Molecular Function": [dict_molecular_function_pharmebinet, dict_molecular_function_alternative_pharmebinet,
                           dict_ctd_molecular_function_in_pharmebinet_alternative,
                           dict_ctd_molecular_function_in_pharmebinet],
    "Cellular Component": [dict_cellular_component_pharmebinet, dict_cellular_component_alternative_pharmebinet,
                           dict_ctd_cellular_component_in_pharmebinet_alternative,
                           dict_ctd_cellular_component_in_pharmebinet]
}

# define path to project
if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path')

# cypher file to integrate and update the go nodes
cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
# delete all old
# query='''begin\n MATCH p=()-[r:equal_to_CTD_go]->() Delete r commit\n'''
# cypher_file.write(query)
# add ontology to ctd go
query = ''' Match (n:CTD_GO{go_id:line.id}) SET n.ontology=line.ontology '''
query = pharmebinetutils.get_query_import(path_of_directory,
                                          f'mapping_and_merging_into_hetionet/ctd/GO/nodes_without_ontology.tsv',
                                          query)
cypher_file.write(query)


def add_resource(go_id):
    """
    add to a give id the ctd resource and return it as string
    :param go_id: string
    :return: string
    """
    resource = dict_go_id_to_resource[go_id]
    resource.add('CTD')
    return '|'.join(sorted(resource))


'''
Generate cypher and tsv for generating the new nodes and the relationships
'''


def generate_files(file_name_addition, ontology, dict_ctd_in_pharmebinet, dict_ctd_in_pharmebinet_alternative):
    # generate mapped csv
    with open('GO/mapping_' + file_name_addition + '.tsv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GOIDCTD', 'GOIDpharmebinet', 'highestGOLevel', 'resource'])
        # add the go nodes to cypher file

        for go_id, name in dict_ctd_in_pharmebinet.items():
            writer.writerow([go_id, go_id, '', add_resource(go_id)])

        for ctd_id, pharmebinet_id in dict_ctd_in_pharmebinet_alternative.items():
            writer.writerow([ctd_id, pharmebinet_id, '', add_resource(pharmebinet_id)])

    query = ''' Match (c:%s{ identifier:line.GOIDpharmebinet}), (n:CTD_GO{go_id:line.GOIDCTD}) SET  c.url_ctd=" http://ctdbase.org/detail.go?type=go&acc="+line.GOIDCTD, c.highestGOLevel=n.highestGOLevel, c.ctd="yes", c.resource=split(line.resource,"|") Create (c)-[:equal_to_CTD_go]->(n)'''
    query = query % (ontology)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/GO/mapping_{file_name_addition}.tsv',
                                              query)
    cypher_file.write(query)


# dictionary from ctd ontology to label and file name
dict_ctd_ontology_to_file_and_label = {
    "Biological Process": ('bp', 'BiologicalProcess'),
    "Cellular Component": ('cc', 'CellularComponent'),
    "Molecular Function": ('mf', 'MolecularFunction')
}


def main():
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all go from pharmebinet into a dictionary')

    load_pharmebinet_go_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all ctd go from neo4j into a dictionary')

    load_ctd_go_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map generate tsv and cypher file for all three labels ')

    for ontology, [dict_in_pharmebinet, dict_in_pharmebinet_alternative, dict_ctd_in_pharmebinet_alternative,
                   dict_ctd_in_pharmebinet] in dict_process.items():
        file_name, pharmebinet_label = dict_ctd_ontology_to_file_and_label[ontology]
        generate_files(file_name, pharmebinet_label, dict_ctd_in_pharmebinet, dict_ctd_in_pharmebinet_alternative)

    # delete the node which did not mapped because they are obsoleted
    cypher = 'MATCH (n:CTD_GO) where not (n)<-[:equal_to_CTD_go]-() Detach Delete n;\n'
    cypher_file.write(cypher)

    driver.close()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
