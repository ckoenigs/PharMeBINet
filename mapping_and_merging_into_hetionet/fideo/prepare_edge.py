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
    query = f"Match (n:{label_other_node})<-[r:is_about]-(m:{label_other_node}) Return m.id, m.xref, m.name, n.id"
    for reference_id, reference_url, reference_name, edge_id, in g.run(query):
        if edge_id not in dict_FIDEO_edge_to_reference:
            dict_FIDEO_edge_to_reference[edge_id] = []
        dict_FIDEO_edge_to_reference[edge_id].append((reference_id, reference_url, reference_name))


def prepare_query(file_name):
    """
    Prepare the cypher fle and query
    :param file_name:
    :return:
    """
    with open('output/cypher_edge.cypher', 'w', encoding='utf8') as f:
        query = '''Match (s:Chemical{identifier:line.chemical_id }), (m:Food{identifier:line.food_id}) Create (s)<-[:INTERACTS_FiCH{fideo:"yes", license:"CC-BY 4.0", text:line.edge_info , interaction_text:split(line.interaction_text,'|'), resource:["FIDEO"], url:"https://gitub.u-bordeaux.fr/erias/fideo",  hedrine_ids:split(line.hedrine,'|') ,reference:split(line.reference,'|')}]-(m) '''
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/fideo/{file_name}',
                                                  query)
        f.write(query)


# dictionary from reference node to chemical id
dict_reference_id_to_chemical = {}


def load_reference_to_chemical():
    """
    load all chemical-reference connection with food-interaction information and write into dictionary
    :return:
    """
    query = f"Match (m:Chemical)--(n:{label_other_node})  Where (n)-[:is_about]-(:{label_other_node}) Return Distinct m.identifier,n.id, m.food_interaction "
    for chemical_id, reference_id, food_interaction_text, in g.run(query):
        food_interaction_text = food_interaction_text if food_interaction_text else []
        if reference_id in dict_reference_id_to_chemical:
            print('ohno referefnekfdnslfk!!!!!')
        dict_reference_id_to_chemical[reference_id] = [chemical_id, food_interaction_text]


def get_interaction_text(interaction_texts, food_name, food_id):
    """
    try to extract form drugbank food interaction text. Therefore part of the food name need to be in the text. Some
    foods are excluded because tey are to general and also some words or symbols are exclude. For food product and
    alcoholic beverage got a manual mapper.
    :param interaction_texts:
    :param food_name:
    :param food_id:
    :return:
    """
    selected_interaction_texts = []
    if food_id in ['FOODON:03301014', 'FOODON:03309880', 'FOODON:03310207']:
        return selected_interaction_texts
    for interaction_text in interaction_texts:
        interaction_text_lower = interaction_text.lower()
        position = 0
        found_part = False
        for part_food_name in food_name.split(' '):
            if (part_food_name == 'food' and position != 0) or part_food_name in ['product', 'or', 'beverage',
                                                                                  '-'] or part_food_name.startswith(
                '(') or part_food_name[-1] == ')':
                position += 1
                continue
            if part_food_name in interaction_text_lower:
                found_part = True
                selected_interaction_texts.append(interaction_text)
            position += 1
        if not found_part and (
                (food_id == 'FOODON:00001002' and interaction_text.startswith('Take on an empty stomach')) or (
                food_id == 'FOODON:00001579' and 'alcohol' in interaction_text_lower)):
            selected_interaction_texts.append(interaction_text)

    return selected_interaction_texts


def prepare_edge():
    """
    Prepare cypher file with query, the tsv file and load all chemical-food pairs and prepare the infomation and write them into the tsv file
    :return:
    """
    query = 'Match (i:Chemical)--(:FIDEO_Entry)-[j]-(k:FIDEO_Entry)-[r]-(:FIDEO_Entry)--(h:Food)  Where not j:is_about Return Distinct  i.identifier, i.name, i.food_interaction, h.identifier, h.name, k.id, k.name'
    file_name = 'edges/food_drug_interaction.tsv'
    prepare_query(file_name)
    set_of_chemical_food_tuples = set()
    with open(file_name, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, delimiter='\t')
        csv_writer.writerow(
            ['chemical_id', 'food_id', 'edge_id', 'edge_info', 'reference', 'interaction_text', 'hedrine'])
        counter_all = 0
        counter_no_reference = 0
        for chemical_id, chemical_name, food_interaction, food_id, food_name, edge_id, edge_info, in g.run(query):
            counter_all += 1
            food_name = food_name.lower()
            food_interaction = food_interaction if food_interaction else []
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
                selected_interaction_texts = get_interaction_text(food_interaction, food_name, food_id)
                csv_writer.writerow(
                    [chemical_id, food_id, edge_id, edge_info,
                     "|".join(set([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])),
                     '|'.join(selected_interaction_texts),
                     "|".join(set([x[2] for x in dict_FIDEO_edge_to_reference[edge_id] if x[2].startswith('HEDRINE')]))])
                set_of_chemical_food_tuples.add((chemical_id, food_id))
            else:
                reference_node_ids = set([x[0] for x in dict_FIDEO_edge_to_reference[edge_id]])
                dict_possible_chemicals_to_interaction_texts = {}
                found_reference_chemical = False

                for reference_id in reference_node_ids:
                    if reference_id in dict_reference_id_to_chemical:
                        found_reference_chemical = True
                        if dict_reference_id_to_chemical[reference_id][0] == chemical_id:
                            selected_interaction_texts = get_interaction_text(
                                dict_reference_id_to_chemical[reference_id][1], food_name, food_id)
                            csv_writer.writerow(
                                [chemical_id, food_id, edge_id, edge_info,
                                 "|".join(set([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])),
                                 '|'.join(selected_interaction_texts),
                                 "|".join(set([x[2] for x in dict_FIDEO_edge_to_reference[edge_id] if
                                           x[2].startswith('HEDRINE')]))])
                            set_of_chemical_food_tuples.add((chemical_id, food_id))
                            break
                        else:
                            dict_possible_chemicals_to_interaction_texts[
                                dict_reference_id_to_chemical[reference_id][0]] = \
                                dict_reference_id_to_chemical[reference_id][1]
                if len(dict_possible_chemicals_to_interaction_texts):
                    print('change chemical', chemical_id, 'to', dict_possible_chemicals_to_interaction_texts)
                    for possible_chemical, interaction_texts in dict_possible_chemicals_to_interaction_texts.items():
                        selected_interaction_texts = get_interaction_text(interaction_texts, food_name, food_id)
                        csv_writer.writerow(
                            [possible_chemical, food_id, edge_id, edge_info,
                             "|".join(set([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])),
                             '|'.join(selected_interaction_texts),
                             "|".join(
                                 set([x[2] for x in dict_FIDEO_edge_to_reference[edge_id] if x[2].startswith('HEDRINE')]))])
                        set_of_chemical_food_tuples.add((possible_chemical, food_id))
                elif not found_reference_chemical:
                    print('different text but no alternatives', chemical_id, food_id)
                    selected_interaction_texts = get_interaction_text(food_interaction, food_name, food_id)
                    csv_writer.writerow(
                        [chemical_id, food_id, edge_id, edge_info,
                         "|".join(set([x[1] for x in dict_FIDEO_edge_to_reference[edge_id]])),
                         '|'.join(selected_interaction_texts),
                         "|".join(set([x[2] for x in dict_FIDEO_edge_to_reference[edge_id] if x[2].startswith('HEDRINE')]))])
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
