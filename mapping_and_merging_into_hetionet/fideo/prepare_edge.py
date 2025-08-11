import csv
import sys
import datetime
from collections import defaultdict

from sympy import false

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# label of fideo nodes
label_other_node = 'FIDEO_Entry'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# set of fideo ids which are part of food drug-interaction
set_fideo_ids_for_interaction = set()


def get_all_FIDEO_food_drug_interaction_nodes():
    """
    Load all food-drug interaction nodes. FIDEO:00000006 stands for food-drug interaction
    :return:
    """
    # FIDEO:00000006:food drug interaction
    query = f"Match (n:{label_other_node}{{id:'FIDEO:00000006'}})-[r:intersection_of]-(m:{label_other_node}) Return m.id"
    for identifier, in g.run(query):
        set_fideo_ids_for_interaction.add(identifier)


# dictionary from FIDEO node to reference information
dict_FIDEO_edge_to_reference = {}


def get_all_FIDEO_reference_edge_info():
    """
    Get for food-drug interaction nodes the reference information
    :return:
    """
    query = f"Match (n:{label_other_node})<-[r:is_about]-(m:{label_other_node}) Return m.id, m.xref, n.id"
    for reference_id, reference_url, edge_id, in g.run(query):
        if edge_id not in dict_FIDEO_edge_to_reference:
            dict_FIDEO_edge_to_reference[edge_id] = []
        dict_FIDEO_edge_to_reference[edge_id].append((reference_id,reference_url))


def prepare_query(file_name):
    """
    Prepare the cypher fle and query
    :param file_name:
    :return:
    """
    with open('output/cypher_edge.cypher', 'w', encoding='utf8') as f:
        query = '''Match (s:Chemical{identifier:line.chemical_id }), (m:Food{identifier:line.food_id}) Create (s)<-[:INTERACTS_FiCH{fideo:"yes", license:"", text:line.edge_info , resource:["FIDEO"], url:""+line.edge_id, reference:split(line.reference,'|')}]-(m) '''
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/fideo/{file_name}',
                                                  query)
        f.write(query)
# dictionary from reference node to chemical id
dict_reference_id_to_chemical={}

def load_reference_to_chemical():
    query = f"Match (m:Chemical)--(n:{label_other_node})  Where (n)-[:is_about]-(:{label_other_node}) Return Distinct m.identifier,n.id "
    for chemical_id, reference_id, in g.run(query):
        if reference_id in dict_reference_id_to_chemical:
            print('ohno referefnekfdnslfk!!!!!')
        dict_reference_id_to_chemical[reference_id]=chemical_id

def prepare_edge():
    """
    Prepare cypher file with query, the tsv file and load all chemical-food pairs and prepare the infomation and write them into the tsv file
    :return:
    """
    query = 'Match (i:Chemical)--(:FIDEO_Entry)-[j]-(k:FIDEO_Entry)-[r]-(:FIDEO_Entry)--(h:Food)  Where not j:is_about Return Distinct  i.identifier, i.name, h.identifier, k.id, k.name'
    file_name = 'edges/food_drug_interaction.tsv'
    prepare_query(file_name)
    set_of_chemical_food_tuples = set()
    with open(file_name, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter='\t')
        csv_writer.writerow(['chemical_id', 'food_id', 'edge_id', 'edge_info', 'reference'])
        counter_all = 0
        counter_no_reference = 0
        for chemical_id, chemical_name, food_id, edge_id, edge_info, in g.run(query):
            counter_all += 1
            if (chemical_id, food_id) in set_of_chemical_food_tuples and chemical_name.lower() in edge_info.lower():
                print('multiple edge', chemical_id, food_id)
                sys.exit('')
            if not edge_id in dict_FIDEO_edge_to_reference:
                print('oh no, no reference', edge_id)
                counter_no_reference += 1
                continue
            if edge_id not in set_fideo_ids_for_interaction:
                print('not an interaction :O', edge_id)
                sys.exit(');')
            if chemical_name.lower() in edge_info.lower():
                csv_writer.writerow(
                    [chemical_id, food_id, edge_id, edge_info, "|".join([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])])
                set_of_chemical_food_tuples.add((chemical_id, food_id))
            else:
                reference_node_ids = set([x[0] for x in dict_FIDEO_edge_to_reference[edge_id]])
                set_possible_chemicals =set()
                found_reference_chemical =False
                for reference_id in reference_node_ids:
                    if reference_id in dict_reference_id_to_chemical:
                        found_reference_chemical=True
                        if dict_reference_id_to_chemical[reference_id]== chemical_id:
                            csv_writer.writerow(
                                [chemical_id, food_id, edge_id, edge_info,
                                 "|".join([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])])
                            set_of_chemical_food_tuples.add((chemical_id, food_id))
                            break
                        else:
                            set_possible_chemicals.add(dict_reference_id_to_chemical[reference_id])
                if len(set_possible_chemicals):
                    print('change chemical', chemical_id, 'to', set_possible_chemicals)
                    for possible_chemical in set_possible_chemicals:
                            csv_writer.writerow(
                                [possible_chemical, food_id, edge_id, edge_info,
                                 "|".join([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])])
                            set_of_chemical_food_tuples.add((possible_chemical, food_id))
                elif not found_reference_chemical:
                    print('different text but no alternatives', chemical_id, food_id)
                    csv_writer.writerow(
                        [chemical_id, food_id, edge_id, edge_info,
                         "|".join([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])])
                    set_of_chemical_food_tuples.add((chemical_id, food_id))



        print('number of all edge', counter_all)
        print('number of no_reference', counter_no_reference)


def main():
    print(datetime.datetime.now())

    global path_of_directory, director
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path fideo')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('create connection to neo4j')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('get all food-drug interaction edge node ids')

    get_all_FIDEO_food_drug_interaction_nodes()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare dictionary edge node to source')

    get_all_FIDEO_reference_edge_info()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load all reference chemical connections')

    load_reference_to_chemical()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('prepare tsv file and fill with edges')

    prepare_edge()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
