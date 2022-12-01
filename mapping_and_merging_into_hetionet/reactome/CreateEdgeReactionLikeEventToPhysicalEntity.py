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


# dictionary with pharmebinet failedReaction with identifier as key and value the name
dict_reaction_pharmebinet_protein_pharmebinet = {}

'''
load in Reaction from pharmebinet in a dictionary
'''


def load_pharmebinet_reaction_pharmebinet_protein_in(csv_file, rela, dict_reaction_pharmebinet_protein_pharmebinet,
                                                    node_pharmebinet_label):
    query = '''MATCH (p:ReactionLikeEvent)--(o:ReactionLikeEvent_reactome)-[:%s]-(m:PhysicalEntity_reactome)-[a:referenceEntity]-(r:ReferenceEntity_reactome)-[v]-(n:%s) RETURN distinct p.identifier, n.identifier, v.order, v.stoichiometry, m.displayName'''
    query = query % ( rela, node_pharmebinet_label)
    print(query)
    results = graph_database.run(query)
    # for id1, id2, order, stoichiometry, in results:
    for reaction_id, protein_id, order, stoichiometry, name, in results:
        if (reaction_id, protein_id) in dict_reaction_pharmebinet_protein_pharmebinet:
            print(reaction_id, protein_id)
            print("Doppelte reaction-protein kombination")

            dict_reaction_pharmebinet_protein_pharmebinet[(reaction_id, protein_id)][2].add(name)

        else:
            dict_reaction_pharmebinet_protein_pharmebinet[(reaction_id, protein_id)] = [stoichiometry, order, set([name])]
        # csv_file.writerow([reaction_id, protein_id, order, stoichiometry, name])

    for (reaction_id, node_id), list_of_property in dict_reaction_pharmebinet_protein_pharmebinet.items():
        csv_file.writerow([reaction_id, node_id, list_of_property[1], list_of_property[0], '|'.join(list_of_property[2])])
    print('relationships in pharmebinet:' + str(len(dict_reaction_pharmebinet_protein_pharmebinet)))


'''
generate new relationships between reaction of pharmebinet and protein of pharmebinet nodes that mapped to reactome
'''


def create_cypher_file( file_path, node_label, rela_name):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:Reaction{identifier:line.id_pharmebinet_Reaction}),(c:%s{identifier:line.id_pharmebinet_node}) CREATE (c)-[: %s{order:line.order, stoichiometry:line.stoichiometry, from_names:split(line.from_name,"|") , source:"Reactome", resource: ['Reactome'], reactome: "yes", license:"%s", url:"https://reactome.org/content/detail/"+line.id_pharmebinet_Reaction}]->(d);\n'''
    query = query % (path_of_directory, file_path, node_label, rela_name, license)
    cypher_file.write(query)


def check_relationships_and_generate_file( node_pharmebinet_label,
                                          directory, rela_name, rela):
    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())
    print('Load all relationships from pharmebinet_reaction and pharmebinet_protein into a dictionary')
    # file for mapped or not mapped identifier
    file_name= directory + '/mapped_Reaction_to_'+rela_name+'.tsv'

    file_mapped_reaction_to_node = open(file_name,'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_reaction_to_node, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['id_pharmebinet_Reaction', 'id_pharmebinet_node', 'order', 'stoichiometry', "from_name"])

    dict_reaction_node = {}

    load_pharmebinet_reaction_pharmebinet_protein_in(csv_mapped, rela, dict_reaction_node, node_pharmebinet_label)

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())

    print('Integrate new relationships and connect them ')

    create_cypher_file( file_name, node_pharmebinet_label, rela_name)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license reactome edge')

    global cypher_file
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    # 0: rela in reactome; 1: node in PharMeBINet; 2: name of new relationship
    list_of_combinations = [
        ['input','Protein', 'IS_INPUT_OF_PiioRLE'],
        ['output', 'Protein', 'IS_OUTPUT_OF_PiooRLE'],
        ['input','Chemical', 'IS_INPUT_OF_CHiioRLE'],
        ['output', 'Chemical', 'IS_OUTPUT_OF_CHiooRLE']
    ]

    directory = 'physikalEntityEdges'
    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")

    for list_element in list_of_combinations:
        rela_reactome= list_element[0]
        node_pharmebinet_label = list_element[1]
        rela_name = list_element[2]

        check_relationships_and_generate_file(node_pharmebinet_label, directory, rela_name, rela_reactome)
    cypher_file.close()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()