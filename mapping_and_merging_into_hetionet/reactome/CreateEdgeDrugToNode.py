# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

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


# dictionary with hetionet failedReaction with identifier as key and value the name
dict_compound_hetionet_node_hetionet = {}

'''
load in all Compounds from hetionet in a dictionary
'''


def load_hetionet_compound_hetionet_node_in(label, csv_file, dict_compound_hetionet_node_hetionet,
                                                  new_relationship,
                                                  node_reactome_label, rela_equal_name, node_hetionet_label, direction1, direction2):
    # {identifier:'DB01025'}
    query = '''MATCH (p:Chemical)-[:equal_to_reactome_drug]-(r:ReferenceEntity_reactome)<-[:referenceEntity]-(z:%s)%s[v:%s]%s(n:%s)-[:%s]-(b:%s) RETURN p.identifier, b.identifier, v.order, v.stoichiometry, z.displayName, z.stId'''
    query = query % (label, direction1, new_relationship, direction2, node_reactome_label, rela_equal_name, node_hetionet_label)
    #print(query)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for compound_id, node_id, order, stoichiometry, displayName, stid, in results:
        compartment = ""
        displayName = displayName.split("[")
        compartment = displayName[1]
        compartment = compartment.replace("]", "")
        if (compound_id, node_id) not in dict_compound_hetionet_node_hetionet:
            dict_compound_hetionet_node_hetionet[(compound_id, node_id)] = [stoichiometry, order, set([compartment]), set([stid])]
            # csv_file.writerow([compound_id, node_id, order, stoichiometry, compartment])
            continue
        else:
            print(compound_id,node_id)
            dict_compound_hetionet_node_hetionet[(compound_id, node_id)][2].add(compartment)
            dict_compound_hetionet_node_hetionet[(compound_id, node_id)][3].add(stid)
            print(compartment)
        # dict_compound_hetionet_node_hetionet[(compound_id, node_id)] = [stoichiometry, order]
        # csv_file.writerow([compound_id, node_id, order, stoichiometry, compartment])
    print('number of reaction-'+node_reactome_label+' relationships in hetionet:' + str(
        len(dict_compound_hetionet_node_hetionet)))

'''
generate new relationships between Compound of hetionet and Drug of hetionet nodes that mapped to reactome 
'''


def create_cypher_file(directory, file_path, node_label, rela_name, direction1, direction2):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:Chemical{identifier:line.id_hetionet_Compound}),(c:%s{identifier:line.id_hetionet_node}) CREATE (d)%s[: %s{order:line.order, stoichiometry:line.stoichiometry, compartments: split(line.compartment, "|"), resource: ['Reactome'], reactome: "yes", license:"%s", source:"Reactome", url:"https://reactome.org/content/detail/"+line.stid}]%s(c);\n'''
    query = query % (path_of_directory, file_path, node_label, direction1, rela_name, license ,direction2)
    cypher_file.write(query)


def check_relationships_and_generate_file(new_relationship, node_reactome_label, rela_equal_name, node_hetionet_label,
                                          directory, rela_name, direction1, direction2):
    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())
    print('Load all relationships from hetionet_Compound and hetionet_nodes into a dictionary')
    # file for mapped or not mapped identifier
    file_name= directory + '/mapped_Compound_to_'+node_reactome_label+'_'+rela_name+'.tsv'

    file_mapped_drug_to_node = open(file_name,'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_drug_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_hetionet_Compound', 'id_hetionet_node', 'order', 'stoichiometry', 'compartment', 'stid'])

    dict_compound_node = {}

    for label in ["Drug_reactome", "PhysicalEntity_reactome"]:
        load_hetionet_compound_hetionet_node_in(label, csv_mapped, dict_compound_node, new_relationship,
                                                      node_reactome_label,
                                                      rela_equal_name, node_hetionet_label, direction1, direction2)
    for (compound_id, node_id), list_of_properties in dict_compound_node.items():
        csv_mapped.writerow([compound_id, node_id, list_of_properties[0], list_of_properties[1], "|".join(list_of_properties[2]), list_of_properties[3].pop()])

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file(directory, file_name, node_hetionet_label, rela_name, direction1, direction2)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path reactome protein')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: old relationship;           1: name of node in Reactome;        2: relationship equal to Hetionet-node
    # 3: name of node in Hetionet;   4: name of directory                5: name of new relationship
    # 6: compartment
    list_of_combinations = [
        ['input', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction',
         'HAS_INPUT_RiCH', '<-', '-' ],
        ['input', 'FailedReaction_reactome', 'equal_to_reactome_failedreaction', 'FailedReaction',
         'HAS_INPUT_FiCH', '<-',  '-'],
        ['input', 'BlackBoxEvent_reactome', 'equal_to_reactome_blackBoxEvent', 'BlackBoxEvent',
         'HAS_INPUT_BiCH', '<-',  '-'],
        ['output', 'Reaction_reactome', 'equal_to_reactome_reaction', 'Reaction',
         'HAS_OUTPUT_RoCH', '<-', '-']
    ]

    directory = 'DrugEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        new_relationship = list_element[0]
        node_reactome_label = list_element[1]
        rela_equal_name = list_element[2]
        node_hetionet_label = list_element[3]
        rela_name = list_element[4]
        direction1 = list_element[5]
        direction2 = list_element[6]
        check_relationships_and_generate_file(new_relationship, node_reactome_label, rela_equal_name,
                                              node_hetionet_label, directory,
                                              rela_name, direction1, direction2)
    cypher_file.close()

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
