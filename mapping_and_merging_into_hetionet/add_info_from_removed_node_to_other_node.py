import sys
import datetime

sys.path.append("../..")
sys.path.append("..")
import create_connection_to_databases

# dictionary with the differences sources as and the name as property in pharmebinet
dict_resources = {
    'AEOLUS': 'aeolus',
    'ClinVar': 'clinvar',
    'CTD': 'ctd',
    'dbSNP': 'dbsnp',
    'Disease Ontology': 'diseaseOntology',
    'DrugBank': 'drugbank',
    'GO': 'go',
    'Hetionet': 'hetionet',
    'hetionet': 'hetionet',
    'HPO': 'hpo',
    'IID': 'iid',
    'MonDO': 'mondo',
    'NCBI': 'ncbi',
    'NDF-RT': 'ndf_rt',
    'OMIM': 'omim',
    # for pathway it is missing
    'PharmGKB': 'pharmgkb',
    'Reactome': 'reactome',
    'SIDER': 'sider',
    'UniProt': 'uniprot'
}


# connect with the neo4j database
def database_connection():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary with label as key and value is the constraint property
dict_label_to_unique_prop = {}

'''
Get for all label the unique property, after a : is the label and after a . is the property
'''


def generate_dictionary_for_labels():
    query = 'SHOW INDEXES'
    # query = '''CALL db.constraints'''
    results = g.run(query)
    for record in results:
        # [name, constraint_string, details] = record.values()
        # # print(constraint_string)
        # label = constraint_string.split(':')[1].split(' )')[0]
        # unique_property = constraint_string.split('.')[1].split(' ')[0].rsplit(')', 1)[0]
        # dict_label_to_unique_prop[label] = unique_property
        [id, name, state, populationPercent, type, entityType, labelsOrTypes, properties, indexProvider,
         owningConstraint] = record.values()
        if labelsOrTypes:
            if len(labelsOrTypes) > 1:
                sys.exit('ohno, multiple labels')
            if len(properties) > 1:
                sys.exit('ohno multiple properties')
            dict_label_to_unique_prop[labelsOrTypes[0]] = properties[0]
    # print(dict_label_to_unique_prop)


cypher_file = open('cypher_merge.cypher', 'w', encoding='utf-8')

'''
add the resource to merged node
'''


def merge_resource_to_node(delete_node, label, merged_node):
    # get all resources of a node

    query = '''Match (s:%s) Where s.identifier in ["%s"] Return s'''
    query = query % (label, delete_node + '","' + merged_node)
    results = g.run(query)
    dict_delete_node = {}
    dict_merge_node = {}
    for record in results:
        node = record.data()['s']
        identifier = node["identifier"]
        if identifier == delete_node:
            dict_delete_node = dict(node)
        else:
            dict_merge_node = dict(node)
    resources_list = dict_delete_node['resource'] if 'resource' in dict_delete_node else []
    url_ctd = dict_delete_node['ctd_url'] if 'ctd_url' in dict_delete_node else ''

    combined_resource = set(resources_list).union(
        dict_merge_node['resource']) if 'resource' in dict_merge_node else set()

    print('delete node:' + delete_node)
    print('merged node:' + merged_node)

    query_start = '''Match (s:%s{identifier:"%s"}) With s Set s.resource=["%s"], '''
    query_start = query_start % (label, merged_node, '","'.join(combined_resource))
    # make all this source to a yes in the merged node

    for source in resources_list:
        add_query = ''' s.%s="yes",''' % (dict_resources[source])
        query_start += add_query

    # if it comes from CTD also add the ctd url
    if url_ctd != '' and 'url_ctd' not in dict_merge_node:
        add_query = ''' s.url_ctd="%s", ''' % (url_ctd)
        query_start += add_query

    if 'merged_identifier' in dict_merge_node:
        merge_ids = set(dict_merge_node['merged_identifier'])
        merge_ids.add(delete_node)
    else:
        merge_ids = set([delete_node])

    add_part = 's.merged_identifier=["%s"]' % ('","'.join(merge_ids))
    query_start = query_start + add_part + ';\n '
    cypher_file.write(query_start)


'''
The DB13390 is revoked but DB06723 has this as ingredient and fit for the mapping of NDF-RT
So first get all edges and nodes with type
'''


def get_rela_info_and_add_cypher_queries(identifier, label, merged_node_id):
    query = '''Match (c:%s{identifier:"%s"})-[r]->(a) Return Distinct Type(r),  labels(a) '''
    query = query % (label, identifier)
    # print(query)
    results = g.run(query)

    set_of_rela_label_tuple = set()
    for record in results:
        [rela_type, node_labels] = record.values()
        node_label = node_labels[0]
        if not (rela_type, node_label) in set_of_rela_label_tuple:
            set_of_rela_label_tuple.add((rela_type, node_label))
            query = '''Match (c1:%s{identifier:"%s"})-[r:%s]->(a:%s), (c2:%s{identifier:"%s"}) Where ID(a)<>ID(c2) Merge (c2)-[h:%s]->(a) On Create Set h=r ;\n '''
            query = query % (label, identifier, rela_type, node_label, label, merged_node_id, rela_type)
            cypher_file.write(query)

    print('number of rela from node to other:' + str(len(list_node_to_other)))

    query = '''Match (c:%s{identifier:"%s"})<-[r]-(a) Return Distinct Type(r),  labels(a)  '''
    query = query % (label, identifier)
    # print(query)
    results = g.run(query)
    for record in results:
        [rela_type, node_labels] = record.values()

        node_label = node_labels[0]
        if not (rela_type, node_label) in set_of_rela_label_tuple:
            set_of_rela_label_tuple.add((rela_type, node_label))
            query = '''Match (c1:%s{identifier:"%s"})<-[r:%s]-(a:%s), (c2:%s{identifier:"%s"}) Where ID(a)<>ID(c2) Merge (c2)<-[h:%s]-(a) On Create Set h=r ;\n '''
            query = query % (label, identifier, rela_type, node_label, label, merged_node_id, rela_type)
            cypher_file.write(query)

    print('number of rela from other to node:' + str(len(list_other_to_node)))


'''
delete the merged node
'''


def delete_merged_node(identifier, label):
    query = ''' Match (n:%s{identifier:"%s"}) Detach Delete n;\n'''
    query = query % (label, identifier)
    cypher_file.write(query)


#
def main():
    if len(sys.argv) < 3:
        sys.exit('need 3 arguments old identifier, into identifier, label')

    old_id = sys.argv[1]
    into = sys.argv[2]
    label = sys.argv[3]

    global list_other_to_node, list_node_to_other
    # list from the specific node to the other with (rela_type,dict_rela,node_labels,dict_node)
    list_node_to_other = []

    # list from  the other with to the specific node  (rela_type,dict_rela,node_labels,dict_node)
    list_other_to_node = []

    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('add resources to merged node')

    merge_resource_to_node(old_id, label, into)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate dictionary for labels with unique property ')

    generate_dictionary_for_labels()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all information for the node that is merged into another node ')

    get_rela_info_and_add_cypher_queries(old_id, label, into)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('delete merged node')

    # delete_merged_node('DB13390', 'Compound')
    delete_merged_node(old_id, label)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
