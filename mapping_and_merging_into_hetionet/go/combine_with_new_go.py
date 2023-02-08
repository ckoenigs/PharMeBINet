import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

# disease ontology license
license = 'CC BY 4.0'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# label of go nodes
label_go = 'go'

# dictionary new go
dict_new_go_to_node = {}

# dictionary of the new nodes
dict_new_nodes = {}

# dictionary tsv files
dict_label_to_mapped_to_tsv = defaultdict(dict)

# header of tsv file
header = []

# header to property name
dict_header_to_property = {}

# cypher file
cypher_file = open('output/cypher.cypher', 'w')

cypher_file_delete = open('output/cypher_delete.cypher', 'w')

'''
Get the  properties of go
'''


def get_go_properties():
    query = '''MATCH (p:go) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    result = g.run(query)

    part = ''' Match (b:%s{id:line.identifier})''' % (label_go)
    query_nodes_start = part
    query_middle_new = ' Create (a:%s{'
    for record in result:
        property = record.data()['l']
        if property in ['def', 'id', 'alt_ids', 'xrefs']:
            if property == 'id':
                query_middle_new += 'identifier:b.' + property + ', '
            elif property == 'alt_ids':
                query_middle_new += 'alternative_ids:b.' + property + ', '
            elif property == 'xrefs':
                query_middle_new += 'xrefs:split(line.' + property + ',"|"), '

            else:
                query_middle_new += 'definition:b.' + property + ', '
        elif property in ["namespace", "is_obsolete", "replaced_by"]:
            continue
        else:
            query_middle_new += property + ':b.' + property + ', '
    query_end = ''' Create (a)-[:equal_to_go]->(b)'''
    global query_new, query_delete

    # combine the important parts of node creation
    query_new = query_nodes_start + query_middle_new + 'resource:["GO"], go:"yes", source:"Gene Ontology", url:"http://purl.obolibrary.org/obo/"+line.identifier, license:"' + license + '"})' + query_end



'''
create the tsv files
'''


def create_tsv_files():
    for label in dict_go_to_pharmebinet_label:
        # delete the old nodes
        query_delete = '''Match (a:%s)  Detach Delete a;\n''' % dict_go_to_pharmebinet_label[label]
        cypher_file.write(query_delete)
        # prepare file and queries for new nodes
        file_name = 'output/integrate_go_' + label + '.tsv'
        query = query_new % (dict_go_to_pharmebinet_label[label])
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/go/{file_name}',
                                                  query)
        cypher_file.write(query)
        file = open(file_name, 'w')
        tsv_file = csv.writer(file, delimiter='\t')
        tsv_file.writerow(['identifier', 'xrefs'])
        dict_label_to_mapped_to_tsv[label] = tsv_file


# dictionary go namespace to node dictionary
dict_go_namespace_to_nodes = {}

# dictionary go label to pharmebinet label
dict_go_to_pharmebinet_label = {
    'molecular_function': 'MolecularFunction',
    'biological_process': 'BiologicalProcess',
    'cellular_component': 'CellularComponent'
}

'''
check if id is in a dictionary
'''


def write_into_tsv_if_not_obsolete(identifier, label_go, namespace, node, xrefs):
    found_id = False
    xref_string = "|".join(go_through_xrefs_and_change_if_needed_source_name(xrefs, label_go))

    if 'is_obsolete' in node:
        print('need to be delete')
        return found_id

    dict_label_to_mapped_to_tsv[namespace].writerow([identifier, xref_string])
    return True


# dictionary for relationship ends
dict_relationship_ends = {
    "biological_process": 'BPiaBP',
    "molecular_function": 'MFiaMF',
    "cellular_component": 'CCiaCC'
}

'''
Get all is_a relationships for bp, cc and mf and add the into a tsv file
'''


def get_is_a_relationships_and_add_to_tsv(namespace):
    query = '''Match (n:go)-[:is_a]->(m:go) Where n.namespace="%s"  Return n.id,m.id;'''
    query = query % namespace
    results = g.run(query)
    file_name = 'output/integrate_go_' + namespace + '_relationship.tsv'
    file = open(file_name, 'w')
    tsv_file = csv.writer(file, delimiter='\t')
    tsv_file.writerow(['identifier_1', 'identifier_2'])

    query = '''Match (a1:%s{identifier:line.identifier_1}), (a2:%s{identifier:line.identifier_2}) Create (a1)-[:IS_A_%s{license:"%s", source:"Gene Ontology", unbiased:false, resource:["GO"], go:'yes', url:"http://purl.obolibrary.org/obo/"+line.identifier_1}]->(a2)'''
    query = query % ( dict_go_to_pharmebinet_label[namespace], dict_go_to_pharmebinet_label[namespace],
                     dict_relationship_ends[namespace], license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/go/{file_name}',
                                              query)
    cypher_file.write(query)

    # go through the results
    for record in results:
        [id1, id2] = record.values()
        tsv_file.writerow([id1, id2])


'''
prepare the go internal relationships
'''


def prepare_go_internal_relationships():
    get_is_a_relationships_and_add_to_tsv('molecular_function')
    get_is_a_relationships_and_add_to_tsv('biological_process')
    get_is_a_relationships_and_add_to_tsv('cellular_component')


'''
go through all go nodes and sort them into the dictionary 
'''


def go_through_go():
    query = '''Match (n:%s) Return n''' % (label_go)
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['id']
        if identifier == 'GO:0099403':
            print('jupp')
        namespace = node['namespace']
        xrefs = node['xrefs'] if 'xrefs' in node else []
        new_xref = set()
        for xref in xrefs:
            splitted_xref = xref.split(' ')
            if len(splitted_xref) > 1:
                new_xref.add(splitted_xref[0])
            else:
                new_xref.add(xref)
        write_into_tsv_if_not_obsolete(identifier, label_go, namespace, node, new_xref)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('get go properties and generate queries')

    get_go_properties()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('create tsv for all names spaces and mapped a tsv')

    create_tsv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate pharmebinet dictionary')

    prepare_go_internal_relationships()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('go through all gos in dictionary')

    go_through_go()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
