import sys
import datetime
sys.path.append("../..")
sys.path.append("..")
import create_connection_to_databases

# dictionary with the differences sources as and the name as property in Hetionet
dict_resources = {
    'AEOLUS': 'aeolus',
    'CTD': 'ctd',
    'Disease Ontology': 'diseaseOntology',
    'DrugBank': 'drugbank',
    'Hetionet': 'hetionet',
    'hetionet': 'hetionet',
    'NDF-RT': 'ndf_rt',
    'SIDER': 'sider',
    'MonDO': 'mondo'
}


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    # global con
    # con = mdb.connect('127.0.0.1', 'root', 'Za8p7Tf', 'umls')

    # authenticate("localhost:7474", )
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary with label as key and value is the constraint property
dict_label_to_unique_prop = {}

'''
Get for all label the unique property, after a : is the label and after a . is the property
'''


def generate_dictionary_for_labels():
    query = '''CALL db.constraints'''
    results = g.run(query)
    # version <=4.0.x
    # for name, constraint_string, in results:
    #version 4.2.x
    for name, constraint_string, details, in results:
        # print(constraint_string)
        label = constraint_string.split(':')[1].split(' )')[0]
        unique_property = constraint_string.split('.')[1].split(' ')[0].rsplit(')', 1)[0]
        dict_label_to_unique_prop[label] = unique_property
    # print(dict_label_to_unique_prop)


'''
add the resource to merged node
'''


def merge_resource_to_node(delete_node, label, merged_node):
    # get all resources of a node
    if type(delete_node) == int:
        query = '''Match (s:%s{identifier:%s}) Return s'''
    else:
        query = '''Match (s:%s{identifier:"%s"}) Return s'''
    query = query % (label, delete_node)
    results = g.run(query)
    dict_delete_node = {}
    for node, in results:
        dict_delete_node = dict(node)
    resources_list = dict_delete_node['resource'] if 'resource' in dict_delete_node else []
    url_ctd = dict_delete_node['ctd_url'] if 'ctd_url' in dict_delete_node else ''

    print('delete node:' + delete_node)
    print('merged node:' + merged_node)

    # make all this source to a yes in the merged node
    if len(resources_list) != 0:

        if type(merged_node) == int:
            query = '''Match (s:%s{identifier:%s}) Set'''
        else:
            query = '''Match (s:%s{identifier:"%s"}) Set'''
        query = query % (label, merged_node)
        for source in resources_list:
            add_query = ''' s.%s="yes",''' % (dict_resources[source])
            query += add_query

        query = query[0:-1] + ''' Return s'''
        results = g.run(query)
        result = results.evaluate()
        if result:
            resources_merged_node_list = result['resource'] if 'resource' in result else []
            combined_resource = list(set().union(resources_list, resources_merged_node_list))
            combined_resource_string = '","'.join(combined_resource)

            if type(merged_node) == int:
                query = '''Match (s:%s{identifier:%s}) Set s.resource=["%s"],'''
            else:
                query = '''Match (s:%s{identifier:"%s"}) Set s.resource=["%s"],'''
            query = query % (label, merged_node, combined_resource_string)

            # if it comes from CTD also add the ctd url
            if url_ctd != '':
                ctd_url_merged = result['url_ctd'] if 'url_ctd' in result else ''
                if ctd_url_merged == '':
                    add_query = ''' s.url_ctd="%s" ''' % (url_ctd)
                    query += add_query
            g.run(query[0:-1])
        else:
            sys.exit(query +' error line 96')


'''
The DB13390 is revoked but DB06723 has this as ingredient and fit for the mapping of NDF-RT
So first get all edges and nodes with type
'''


def get_the_information_and_the_direction(identifier, label, merged_node_id):
    query = '''Match (c:%s{identifier:"%s"})-[r]->(a) Return Type(r), r, labels(a), a '''
    query = query % (label, identifier)
    # print(query)
    results = g.run(query)
    for rela_type, rela, node_labels, node, in results:
        dict_rela = {}
        # this is to avoid loops
        other_node_id = node['identifier'] if 'identifier' in node else ''
        if other_node_id == merged_node_id:
            continue
        for key, property in dict(rela).items():
            dict_rela[key] = property
        dict_node = {}
        for key, property in dict(node).items():
            dict_node[key] = property

        list_node_to_other.append([rela_type, dict_rela, node_labels, node])

    print('number of rela from node to other:' + str(len(list_node_to_other)))

    query = '''Match (c:%s{identifier:"%s"})<-[r]-(a) Return Type(r), r, labels(a), a '''
    query = query % (label, identifier)
    # print(query)
    results = g.run(query)
    for rela_type, rela, node_labels, node, in results:
        dict_rela = {}
        # this is to avoid loops
        other_node_id = node['identifier'] if 'identifier' in node else ''
        if other_node_id == merged_node_id:
            continue
        for key, property in dict(rela).items():
            dict_rela[key] = property
        dict_node = {}
        for key, property in dict(node).items():
            dict_node[key] = property

        list_other_to_node.append([rela_type, dict_rela, node_labels, node])

    print('number of rela from other to node:' + str(len(list_other_to_node)))


'''
The node that get the information 
'''


def add_this_information_to_the_merged_node(identifier, label, delete_node_id):
    # make a list of all identifier which are merged into this node
    query = '''Match (node:%s{identifier:"%s"}) Return node'''
    query = query % (label, identifier)
    results = g.run(query)
    for node, in results:
        merged_identifier = set(node['merged_identifier']) if 'merged_identifier' in node else set([])
        merged_identifier.add(delete_node_id)
        merged_identifier_string = '","'.join(list(merged_identifier))
        query = '''Match (node:%s{identifier:"%s"}) Set node.merged_identifier=["%s"] '''
        query = query % (label, identifier, merged_identifier_string)
        g.run(query)

    # integrate the new relationships from this node to the other nodes into for this node into Hetionet
    count_new_relationships_from_this_node = 0
    length_list_node_other = len(list_node_to_other)
    for [rela_type, dict_rela, node_labels, node] in list_node_to_other:
        # test if not a relationship already exists
        if not node_labels[0] in dict_label_to_unique_prop:
            print('The rela  to this label node has to be manual integrated:' + node_labels[0])
            print(node)
            print('Rela type:' + rela_type)
            print(dict_rela)
            continue
        if type(node[dict_label_to_unique_prop[node_labels[0]]]) == int:
            query = ''' Match (a:%s{identifier:"%s"})-[r:%s]->(b:%s{%s:%s})  Return r'''
        else:
            query = ''' Match (a:%s{identifier:"%s"})-[r:%s]->(b:%s{%s:"%s"})  Return r'''
        query = query % (label, identifier, rela_type, node_labels[0], dict_label_to_unique_prop[node_labels[0]],
                         node[dict_label_to_unique_prop[node_labels[0]]])
        # print(query)
        results = g.run(query)
        result = results.evaluate()
        # if not generate the connection
        if result == None:
            if type(node[dict_label_to_unique_prop[node_labels[0]]]) == int:
                query = ''' Match (a:%s{identifier:"%s"}), (b:%s{%s:%s})
                                Create (a)-[r:%s{ '''
            else:
                query = ''' Match (a:%s{identifier:"%s"}), (b:%s{%s:"%s"})
                Create (a)-[r:%s{ '''
            query = query % (label, identifier, node_labels[0], dict_label_to_unique_prop[node_labels[0]],
                             node[dict_label_to_unique_prop[node_labels[0]]], rela_type)

            for key, property in dict_rela.items():
                if type(property) != list:
                    print(type(property))
                    if type(property) == str:
                        query = query + '''%s:"%s",'''
                    else:
                        query = query + '''%s:%s,'''
                    query = query % (key, property)
                else:
                    query = query + '''%s:["%s"],'''
                    property = '","'.join(property)
                    query = query % (key, property)

            query = query[0:-1] + '''}]->(b)'''
            # print(query)
            count_new_relationships_from_this_node += 1
            g.run(query)

    length_list_other_node = len(list_other_to_node)
    # integrate the new relationships from other nodes to this nodes into for this node into Hetionet
    count_new_relationships_to_this_node = 0
    for [rela_type, dict_rela, node_labels, node] in list_other_to_node:

        # test if not a relationship already exists
        if type(node[dict_label_to_unique_prop[node_labels[0]]]) == int:
            query = ''' Match (a:%s{identifier:"%s"})<-[r:%s]-(b:%s{%s:%s})  Return r'''
        else:
            query = ''' Match (a:%s{identifier:"%s"})<-[r:%s]-(b:%s{%s:"%s"})  Return r'''
        query = query % (label, identifier, rela_type, node_labels[0], dict_label_to_unique_prop[node_labels[0]],
                         node[dict_label_to_unique_prop[node_labels[0]]])
        results = g.run(query)
        result = results.evaluate()

        # if not generate the connection
        if result == None:

            if type(node[dict_label_to_unique_prop[node_labels[0]]]) == int:
                query = ''' Match (a:%s{identifier:"%s"}), (b:%s{%s:%s})
                                Create (a)<-[r:%s { '''
            else:
                query = ''' Match (a:%s{identifier:"%s"}), (b:%s{%s:"%s"})
                             Create (a)<-[r:%s { '''

            query = query % (label, identifier, node_labels[0], dict_label_to_unique_prop[node_labels[0]],
                             node[dict_label_to_unique_prop[node_labels[0]]], rela_type)
            for key, property in dict_rela.items():
                if type(property) != list:
                    if type(property) == str:
                        query = query + '''%s:"%s",'''
                    else:
                        query = query + '''%s:%s,'''
                    query = query % (key, property)
                else:
                    query = query + '''%s:["%s"],'''
                    property = '","'.join(property)
                    query = query % (key, property)

            query = query[0:-1] + '''}]-(b)'''
            # print(query)
            g.run(query)
            count_new_relationships_to_this_node += 1

    print('number of new relationships from this merged node:' + str(count_new_relationships_from_this_node))
    print('number of new relationships to this merged node:' + str(count_new_relationships_to_this_node))


'''
delete the merged node
'''


def delete_merged_node(identifier, label):
    query = ''' Match (n:%s{identifier:"%s"}) Detach Delete n'''
    query = query % (label, identifier)
    g.run(query)


'''
function that start the right programs in the right order to merge information from one node to another
'''


def merge_information_from_one_node_to_another(delete_node_id, merged_node_id, node_label):
    global list_other_to_node, list_node_to_other
    # list from the specific node to the other with (rela_type,dict_rela,node_labels,dict_node)
    list_node_to_other = []

    # list from  the other with to the specific node  (rela_type,dict_rela,node_labels,dict_node)
    list_other_to_node = []

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add resources to merged node')

    merge_resource_to_node(delete_node_id, node_label, merged_node_id)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate dictionary for labels with unique property ')

    generate_dictionary_for_labels()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all information for the node that is merged into another node ')

    get_the_information_and_the_direction(delete_node_id, node_label, merged_node_id)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate this into Hetionet')

    add_this_information_to_the_merged_node(merged_node_id, node_label, delete_node_id)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete merged node')

    # delete_merged_node(delete_node_id, node_label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


#
def main():
    if len(sys.argv) < 3:
        return

    old_id = sys.argv[1]
    into = sys.argv[2]
    label = sys.argv[3]

    global list_other_to_node, list_node_to_other
    # list from the specific node to the other with (rela_type,dict_rela,node_labels,dict_node)
    list_node_to_other = []

    # list from  the other with to the specific node  (rela_type,dict_rela,node_labels,dict_node)
    list_other_to_node = []

    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add resources to merged node')

    merge_resource_to_node(old_id, label, into)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate dictionary for labels with unique property ')

    generate_dictionary_for_labels()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('get all information for the node that is merged into another node ')

    # get_the_information_and_the_direction('DB13390', 'Compound')
    get_the_information_and_the_direction(old_id, label, into)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate this into Hetionet')

    # add_this_information_to_the_merged_node('DB06723', 'Compound','DB13390')
    add_this_information_to_the_merged_node(into, label, old_id)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete merged node')

    # delete_merged_node('DB13390', 'Compound')
    delete_merged_node(old_id, label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
