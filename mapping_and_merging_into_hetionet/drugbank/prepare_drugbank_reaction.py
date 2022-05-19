import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


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
    for identifier, in results:
        set_protein_identifier.add(identifier)

def prepare_cypher_query_rela(file_name, label, direction):
    """
    Prepare the different cypher queries for the different edge types.
    :param file_name: string
    :param label: string
    :param direction: string
    :return:
    """
    query_new = query_start % (file_name)
    query_new+= ' Match (n:Reaction{identifier:line.reaction_id}), (m:%s{identifier:line.other_id}) Create (n)%s[:%s{url:"", license:"%s"}]%s(m);\n'
    if direction=='right':
        query_new= query_new %(label,'-','RESULTS_IN_Rri'+label[0],license,'->')
    elif direction=='left':
        query_new = query_new % (label, '<-', 'INPUT_' + label[0]+'iR', license, '-')
    else:
        query_new = query_new % (label, '<-', 'TAKES_PART_IN_' + label[0]+'tpiR', license, '-')
    cypher_file.write(query_new)

# dictionary label to direction to tsv file
dict_label_to_direction_to_tsv_file = {}


def create_files():
    """
    This prepare the different TSV files for the Reaction nodes and the reaction edges.Additionally, the cypher queries
    are prepared.
    :return:
    """
    global csv_writer
    file_name = 'reaction/reaction.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier'])

    query=query_start %(file_name)
    query+= ' Match (m:Reaction_DrugBank{identifier:line.identifier})  Create (m)<-[:equal_to_reaction_drugbank]-(n:Reaction{identifier:line.identifier, license:m.license, sequence:m.sequence, node_edge:true });\n'
    cypher_file.write(query)

    for label in ['Metabolite', 'Compound']:
        dict_label_to_direction_to_tsv_file[label] = {}
        dict_label_to_direction_to_pairs[label] = {}
        for direction in ['left', 'right']:
            file_name_reaction_direction = 'reaction/reaction_%s_%s.tsv' %(label, direction)
            dict_label_to_direction_to_pairs[label][direction] = set()
            file_reaction_direction = open(file_name_reaction_direction, 'w', encoding='utf-8')
            csv_writer_reaction_direction = csv.writer(file_reaction_direction, delimiter='\t')
            csv_writer_reaction_direction.writerow(['reaction_id', 'other_id'])
            prepare_cypher_query_rela(file_name_reaction_direction, label, direction)
            dict_label_to_direction_to_tsv_file[label][direction] = csv_writer_reaction_direction

    label='Protein'
    direction='part'
    dict_label_to_direction_to_tsv_file[label] = {}
    dict_label_to_direction_to_pairs[label] = {}
    file_name_reaction_direction = 'reaction/reaction_to_%s.tsv' % (label)
    dict_label_to_direction_to_pairs[label][direction] = set()
    file_reaction_direction = open(file_name_reaction_direction, 'w', encoding='utf-8')
    csv_writer_reaction_direction = csv.writer(file_reaction_direction, delimiter='\t')
    csv_writer_reaction_direction.writerow(['reaction_id', 'other_id'])
    prepare_cypher_query_rela(file_name_reaction_direction, label, direction)
    dict_label_to_direction_to_tsv_file[label][direction] = csv_writer_reaction_direction

# dictionary label to direction to pair reaction id and other id
dict_label_to_direction_to_pairs = {}


def check_direction_and_write_into_tsv_writer(rela_type, reaction_id, node_id, label):
    """
    First check out the direction from reaction to node. The add to tsv file if pair is not already added.
    :param rela_type: string
    :param reaction_id: string
    :param node_id: string
    :param label: string
    :return:
    """
    if  rela_type.startswith('left'):
        direction = 'left'
    elif  rela_type.startswith('right'):
        direction= 'right'
    else:
        direction= 'part'
    if (reaction_id, node_id) not in dict_label_to_direction_to_pairs[label][direction]:
        dict_label_to_direction_to_tsv_file[label][direction].writerow([reaction_id, node_id])
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
    query = '''Match p=(c:%s)--(:%s_DrugBank)-[r1]->(a:Reaction_DrugBank)-[r2]->(:%s_DrugBank)--(b:%s)  Where not (a)--(:Protein_DrugBank) Return c.identifier ,type(r1), a.identifier,type(r2),b.identifier '''
    query = query % (label1, label1, label2, label2)
    results = g.run(query)
    for node_1, rela_type1, reaction_id, rela_type2, node_2, in results:
        check_direction_and_write_into_tsv_writer(rela_type1, reaction_id, node_1, label1)
        check_direction_and_write_into_tsv_writer(rela_type2, reaction_id, node_2, label2)
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
    query = '''Match p=(c:%s)--(:%s_DrugBank)-[r1]->(a:Reaction_DrugBank)-[r2]->(:%s_DrugBank)--(b:%s)  Where  (a)--(:Protein_DrugBank) With c,r1,a,r2,b Match (a)--(t:Protein_DrugBank) With c, r1,a,r2,b , collect(t.identifier) as por Return c.identifier ,type(r1), a.identifier,type(r2),b.identifier,  por '''
    query = query % (label1, label1, label2, label2)
    results = g.run(query)
    for node_1, rela_type1, reaction_id, rela_type2, node_2, proteins, in results:
        proteins = set(proteins)
        length_protein = len(proteins)
        intersection = proteins.intersection(set_protein_identifier)
        if len(intersection) != length_protein:
            continue
        check_direction_and_write_into_tsv_writer(rela_type1, reaction_id, node_1, label1)
        check_direction_and_write_into_tsv_writer(rela_type2, reaction_id, node_2, label2)
        for protein_id in proteins:
            check_direction_and_write_into_tsv_writer('part', reaction_id, protein_id, 'Protein')
        if reaction_id not in set_reaction_ids:
            csv_writer.writerow([reaction_id])
            set_reaction_ids.add(reaction_id)


def main():
    global path_of_directory, query_start,  license

    if len(sys.argv) < 2:
        sys.exit('need license and path to directory')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/drugbank/%s" As line Fieldterminator '\\t' '''


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

    for label1 in ['Compound','Metabolite']:
        for label2 in ['Compound','Metabolite']:
            print(datetime.datetime.now())
            print('load all  pairs without enzyme ', label1, label2)
            load_all_reaction_pairs(label1,label2)


            print('load all  pairs with enzyme ', label1, label2)
            print(datetime.datetime.now())
            load_all_reaction_pairs_with_enzymes(label1,label2)

    cypher_file.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
