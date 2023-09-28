import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# cypher file
cypher_file = open('rela_protein/cypher.cypher', 'a', encoding='utf-8')

# set of protein identifiers
set_protein_identifier = set()


def load_all_proteins():
    """
    Load all protein ids in a set
    :return:
    """
    query = 'Match (n:Protein) Return n.identifier'
    results = g.run(query)
    for record in results:
        [identifier] = record.values()
        set_protein_identifier.add(identifier)


# dictionary label to url
dict_label_to_url = {
    'Metabolite': 'https://go.drugbank.com/metabolites/',
    'Compound': 'https://go.drugbank.com/drugs/',
    'Protein': 'https://go.drugbank.com/bio_entities/'
}


def prepare_cypher_query_rela(file_name, label, direction):
    """
    Prepare the different cypher queries for the different edge types.
    :param file_name: string
    :param label: string
    :param direction: string
    :return:

    """
    query_new = f' Match (n:Reaction{{identifier:line.reaction_id}}), (m:%s{{identifier:line.other_id}}) Create (n)%s[:%s{{url:"{dict_label_to_url[label]}"+line.drugbank_id, license:"%s", source:"DrugBank", drugbank:"yes", resource:["DrugBank"]}}]%s(m)'
    abbreviation = pharmebinetutils.dictionary_label_to_abbreviation[label] if label != 'Compound' else 'CH'
    if direction == 'right':
        query_new = query_new % (label, '<-',
                                 f'IS_OUTPUT_OF_{abbreviation}ioo' + pharmebinetutils.dictionary_label_to_abbreviation[
                                     'ReactionLikeEvent'], license, '-')
    elif direction == 'left':
        query_new = query_new % (label, '<-', 'IS_INPUT_OF_' + abbreviation + 'iio' +
                                 pharmebinetutils.dictionary_label_to_abbreviation['ReactionLikeEvent'], license, '-')
    else:
        query_new = query_new % (label, '<-', 'TAKES_PART_IN_' + abbreviation + 'tpi' +
                                 pharmebinetutils.dictionary_label_to_abbreviation['ReactionLikeEvent'], license, '-')
    query_new = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/drugbank/{file_name}',
                                                  query_new)
    cypher_file.write(query_new)


# dictionary label to direction to tsv file
dict_label_to_direction_to_tsv_file = {}


def create_files():
    """
    This prepares the different TSV files for the Reaction nodes and the reaction edges.Additionally, the cypher queries
    are prepared.
    :return:
    """
    global csv_writer
    file_name = 'reaction/reaction.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier'])

    query = ' Match (m:Reaction_DrugBank{identifier:line.identifier})  Create (m)<-[:equal_to_reaction_drugbank]-(n:Reaction :ReactionLikeEvent{identifier:line.identifier, license:m.license, sequence:m.sequence, node_edge:true, url:"https://go.drugbank.com/drugs/"+m.start_drugbank_id, source:"DrugBank", resource:["DrugBank"], drugbank:"yes" })'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/{file_name}',
                                              query)
    cypher_file.write(query)

    for label in ['Metabolite', 'Compound']:
        dict_label_to_direction_to_tsv_file[label] = {}
        dict_label_to_direction_to_pairs[label] = {}
        for direction in ['left', 'right']:
            file_name_reaction_direction = 'reaction/reaction_%s_%s.tsv' % (label, direction)
            dict_label_to_direction_to_pairs[label][direction] = set()
            file_reaction_direction = open(file_name_reaction_direction, 'w', encoding='utf-8')
            csv_writer_reaction_direction = csv.writer(file_reaction_direction, delimiter='\t')
            csv_writer_reaction_direction.writerow(['reaction_id', 'other_id', 'drugbank_id'])
            prepare_cypher_query_rela(file_name_reaction_direction, label, direction)
            dict_label_to_direction_to_tsv_file[label][direction] = csv_writer_reaction_direction

    label = 'Protein'
    direction = 'part'
    dict_label_to_direction_to_tsv_file[label] = {}
    dict_label_to_direction_to_pairs[label] = {}
    file_name_reaction_direction = 'reaction/reaction_to_%s.tsv' % (label)
    dict_label_to_direction_to_pairs[label][direction] = set()
    file_reaction_direction = open(file_name_reaction_direction, 'w', encoding='utf-8')
    csv_writer_reaction_direction = csv.writer(file_reaction_direction, delimiter='\t')
    csv_writer_reaction_direction.writerow(['reaction_id', 'other_id', 'drugbank_id'])
    prepare_cypher_query_rela(file_name_reaction_direction, label, direction)
    dict_label_to_direction_to_tsv_file[label][direction] = csv_writer_reaction_direction


# dictionary label to direction to pair reaction id and other id
dict_label_to_direction_to_pairs = {}


def check_direction_and_write_into_tsv_writer(rela_type, reaction_id, node_id, label, drugbank_id):
    """
    First check out the direction from reaction to node. The add to tsv file if pair is not already added.
    :param rela_type: string
    :param reaction_id: string
    :param node_id: string
    :param label: string
    :return:
    """
    if rela_type.startswith('left'):
        direction = 'left'
    elif rela_type.startswith('right'):
        direction = 'right'
    else:
        direction = 'part'
    if (reaction_id, node_id) not in dict_label_to_direction_to_pairs[label][direction]:
        dict_label_to_direction_to_tsv_file[label][direction].writerow([reaction_id, node_id, drugbank_id])
        dict_label_to_direction_to_pairs[label][direction].add((reaction_id, node_id))


# set of all add reaction id
set_reaction_ids = set()


def load_all_reaction_pairs(label1, label2):
    """
    Get all reaction which are connected to pharmebinet and are not connected to protein. The information are written
    into the tsv files.
    :param label1: string
    :param label2: string
    :return:
    """
    query = '''Match p=(c:%s)--(c2:%s_DrugBank)-[r1]->(a:Reaction_DrugBank)-[r2]->(b2:%s_DrugBank)--(b:%s)  Where not (a)--(:Protein_DrugBank) Return c.identifier, c2.identifier ,type(r1), a.identifier,type(r2),b.identifier, b2.identifier '''
    query = query % (label1, label1, label2, label2)
    results = g.run(query)
    for record in results:
        [node_1, drugbank_id1, rela_type1, reaction_id, rela_type2, node_2, drugbank_id2] = record.values()
        check_direction_and_write_into_tsv_writer(rela_type1, reaction_id, node_1, label1, drugbank_id1)
        check_direction_and_write_into_tsv_writer(rela_type2, reaction_id, node_2, label2, drugbank_id2)
        if reaction_id not in set_reaction_ids:
            csv_writer.writerow([reaction_id])
            set_reaction_ids.add(reaction_id)


def load_all_reaction_pairs_with_enzymes(label1, label2):
    """
    Get all reaction which are connected to pharmebinet and are connected to protein. Only if all proteins are in
    PharMeBINEt then the information are written into the tsv files.
    :param label1: string
    :param label2: string
    :return:
    """
    query = '''Match p=(c:%s)--(c2:%s_DrugBank)-[r1]->(a:Reaction_DrugBank)-[r2]->(b2:%s_DrugBank)--(b:%s)  Where  (a)--(:Protein_DrugBank) With c,c2, r1,a,r2,b, b2 Match (a)--(t:Protein_DrugBank) With c, c2, r1,a,r2,b , b2, collect({identifier:t.identifier, db_id:t.drugbank_id}) as por Return c.identifier, c2.identifier ,type(r1), a.identifier,type(r2),b.identifier, b2.identifier, por '''
    query = query % (label1, label1, label2, label2)
    results = g.run(query)
    for record in results:
        [node_1, drugbank_id1, rela_type1, reaction_id, rela_type2, node_2, drugbank_id2, proteins] = record.values()

        dict_uniprot_id_to_db_id = {x['identifier']: x['db_id'] for x in proteins}

        proteins = set(dict_uniprot_id_to_db_id.keys())
        length_protein = len(proteins)
        intersection = proteins.intersection(set_protein_identifier)
        if len(intersection) != length_protein:
            continue
        check_direction_and_write_into_tsv_writer(rela_type1, reaction_id, node_1, label1, drugbank_id1)
        check_direction_and_write_into_tsv_writer(rela_type2, reaction_id, node_2, label2, drugbank_id2)
        for protein_id in proteins:
            check_direction_and_write_into_tsv_writer('part', reaction_id, protein_id, 'Protein',
                                                      dict_uniprot_id_to_db_id[protein_id])
        if reaction_id not in set_reaction_ids:
            csv_writer.writerow([reaction_id])
            set_reaction_ids.add(reaction_id)


def main():
    global path_of_directory, license

    if len(sys.argv) < 2:
        sys.exit('need license and path to directory')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]

    print(sys.argv)
    print(path_of_directory)
    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all protein ids')

    load_all_proteins()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('prepare the files')

    create_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all rela and add to dictionary')

    for label1 in ['Compound', 'Metabolite']:
        for label2 in ['Compound', 'Metabolite']:
            print(datetime.datetime.now())
            print('load all  pairs without enzyme ', label1, label2)
            load_all_reaction_pairs(label1, label2)

            print('load all  pairs with enzyme ', label1, label2)
            print(datetime.datetime.now())
            load_all_reaction_pairs_with_enzymes(label1, label2)

    cypher_file.close()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
