import csv
import sys
import datetime
import shelve

cypher_file = open('cypher.cypher', 'w', encoding='utf-8')

addition = '_reactome'

get_properties_types = shelve.open('label_to_property_type')


def write_indices_into_cypher_file():
    queries = ''':begin
    CREATE INDEX ON :LiteratureReference%s(pubMedIdentifier);
    CREATE INDEX ON :Person%s(orcidId);
    CREATE INDEX ON :ReferenceEntity%s(variantIdentifier);
    CREATE INDEX ON :ReferenceIsoform%s(variantIdentifier);
    CREATE INDEX ON :ReferenceEntity%s(identifier);
    CREATE INDEX ON :ReferenceIsoform%s(identifier);
    CREATE CONSTRAINT ON (node:DatabaseObject%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Complex%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:DatabaseObject%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Complex%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:DatabaseObject%s) ASSERT (node.oldStId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:EntitySet%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Event%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:EntitySet%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Event%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:GenomeEncodedEntity%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Pathway%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:GenomeEncodedEntity%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Pathway%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:ReferenceEntity%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:ReactionLikeEvent%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:ReferenceEntity%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:ReactionLikeEvent%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Taxon%s) ASSERT (node.taxId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Reaction%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Species%s) ASSERT (node.taxId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:Reaction%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:PhysicalEntity%s) ASSERT (node.dbId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:PhysicalEntity%s) ASSERT (node.stId) IS UNIQUE;
    CREATE CONSTRAINT ON (node:DatabaseObject%s) ASSERT (node.id) IS UNIQUE;
    :commit\n'''
    queries = queries % (
        addition, addition, addition, addition, addition, addition, addition, addition, addition, addition, addition,
        addition, addition, addition, addition, addition, addition, addition, addition, addition, addition, addition,
        addition, addition, addition, addition, addition, addition, addition, addition)
    cypher_file.write(queries)


def generate_csv_file(labels, header, dict_tuple_to_csv, give_file_name_back=False, differen_directory=''):
    """
    generate the csv file for each label pair
    :param labels: tuple
    :param header: list of strings
    """
    file_name = 'data/' + differen_directory + '_'.join(labels) + '.csv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(header)

    dict_tuple_to_csv[labels] = csv_writer
    if not give_file_name_back:
        dict_label_tuple_to_file_name[labels] = file_name
    else:
        return file_name


def prepare_query(labels, file_name, query_end):
    """
    prepare cyfer query for the different nodes and write into file
    :param labels: tuple
    :param file_name: string
    :param query_end: string
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/reactome/%s" As line FIELDTERMINATOR '\t' Create (p:%s{''' + query_end
    join_addition = addition + ' :'
    query = query % (file_name, join_addition.join(labels) + addition)
    cypher_file.write(query)


def prepare_middle(labels):
    labels=sorted(labels)
    labels = '|'.join(labels)
    query_middle = ''
    if labels in get_properties_types:
        dict_prop_to_type = get_properties_types[labels]
        for head in header_node:
            if head == 'id':
                query_middle += head + ':toInteger(line.' + head + '), '
            if head == 'labels' or head not in dict_prop_to_type:
                continue

            if dict_prop_to_type[head] == 'STRING':
                query_middle += head + ':line.' + head + ', '
            elif dict_prop_to_type[head] == 'INTEGER':
                query_middle += head + ':toInteger(line.' + head + '), '
            elif dict_prop_to_type[head] == 'BOOLEAN':
                query_middle += head + ':toBoolean(line.' + head + '), '
            elif dict_prop_to_type[head].startswith('LIST'):
                query_middle += head + ':split(line.' + head + ',"||"), '
            elif dict_prop_to_type[head] == 'FLOAT':
                query_middle += head + ':toFloat(line.' + head + '), '
            else:
                print(head)
                print(dict_prop_to_type[head])

    else:
        print('label not in file ;(')
        print(labels)
    query_middle = query_middle[:-2] + '});\n'
    return query_middle



def generate_cypher_queries():
    """
    prepare the property part of the query and generate for each label combination cypher query
    """

    for labels, file_name in dict_label_tuple_to_file_name.items():
        query_middle = prepare_middle(labels)
        prepare_query(labels, file_name, query_middle)


# dictionary for the other labels the name of the identifier
dict_other_identifier = {
    'DBInfo': 'id',
}


def generate_rela_queries(file_name, tuple_info):
    """
    generate query for rela integration
    :param file_name: string
    :param tuple_info: tuple
    :return:
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/reactome/%s" As line FIELDTERMINATOR '\t' MATCH (s:%s{%s:toInteger(line.start)}), (e:%s{%s:toInteger(line.end)}) Create (s)-[:%s{order:toInteger(line.order), stoichiometry:toInteger(line.stoichiometry)}]->(e);\n '''
    start_id = dict_other_identifier[tuple_info[0]] if tuple_info[0] in dict_other_identifier else 'dbId'
    end_id = dict_other_identifier[tuple_info[1]] if tuple_info[1] in dict_other_identifier else 'dbId'
    query = query % (
        file_name, tuple_info[0] + addition, start_id, tuple_info[1] + addition, end_id, tuple_info[2])
    cypher_file.write(query)


# other: stId; Taxon,Species : taxId
labels_with_index = set(
    ['Complex', 'EntitySet', 'Event', 'GenomeEncodedEntity', 'Pathway', 'ReferenceEntity', 'ReactionLikeEvent', 'Taxon',
     'Reaction', 'Species', 'PhysicalEntity'])

# header of nodes and of rela
header_node = []
header_rela = []

# dictionary from tuple to csv writer
dict_label_tuple_to_csv = {}

# dictionary from tuple to file name
dict_label_tuple_to_file_name = {}

# dictionary start_label_end_label_rela_type to csv
dict_st_label_end_label_rela_to_csv = {}

# set of position which are lists
set_of_list_position = set()

# from general id to label specific identifier
dict_id_to_label_identifier = {}


def prepare_csv_file_to_csv_files():
    existing_file = open("/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/reactome/pathway.csv", "r",
                         encoding="utf8")
    # existing_file = open("pathway.csv", "r", encoding="utf8")
    csv_reader = csv.reader(existing_file)
    header = next(csv_reader)
    print(header)

    #  position important id
    position_dbId = 0

    counter = 0

    # position of array where switch between node and rela infos
    position_of_rela = 0

    # dictionary postion to property
    dict_pos_to_property = {}

    property_node = True
    for property in header:
        if property.startswith('_start'):
            property_node = False
            position_of_rela = counter
        if property.startswith('_'):
            property = property.replace('_', '')
        if property == 'dbId':
            position_dbId = counter
        if property_node:
            header_node.append(property)
        else:
            header_rela.append(property)
        dict_pos_to_property[counter] = property
        counter += 1

    counter = 0
    # add_node_queries
    add_node_queries = False
    for line in csv_reader:

        # check if node or edge
        if line[0] != '':
            labels = line[1].split(':')
            labels = labels[1:]
            labels = tuple(labels)

            unique_label = ''
            intersection = labels_with_index.intersection(labels)
            if len(intersection) > 0:
                unique_label = intersection.pop()
            elif 'DatabaseObject' in labels:
                unique_label = 'DatabaseObject'
            else:
                unique_label = labels[0]

            if unique_label not in ['DBInfo']:
                dict_id_to_label_identifier[line[0]] = [unique_label, line[position_dbId]]
            # elif unique_label in ['Taxon', 'Species']:
            #     dict_id_to_label_identifier[line[0]] = [unique_label, line[position_taxId]]
            else:
                dict_id_to_label_identifier[line[0]] = [unique_label, line[0]]

            # prepare file
            if labels not in dict_label_tuple_to_csv:
                generate_csv_file(labels, header_node, dict_label_tuple_to_csv)

            # prepare values
            for pro_counter, value in enumerate(line[0:position_of_rela]):
                # if pro_counter
                if value.startswith('['):
                    value = value.replace('["', '', 1).rsplit('"]', 1)[0].split('","')
                    value = '||'.join(value)
                    line[pro_counter] = value
                if '"' in value:
                    line[pro_counter] = value.replace('"', '\'')

            dict_label_tuple_to_csv[labels].writerow(line[0:position_of_rela])
        else:
            if not add_node_queries:
                generate_cypher_queries()
                add_node_queries = True
                print(datetime.datetime.utcnow())
                print('start rela')
            rela_infos = line[position_of_rela:]
            start = dict_id_to_label_identifier[rela_infos[0]]
            start_label = start[0]
            start_identifier = start[1]
            if start_identifier == '':
                print(start)
            end = dict_id_to_label_identifier[rela_infos[1]]
            end_label = end[0]
            end_identifier = end[1]
            if end_identifier == '':
                print(end)
            rela_type = rela_infos[2]
            rela_general_info_tuple = (start_label, end_label, rela_type)
            if not rela_general_info_tuple in dict_st_label_end_label_rela_to_csv:
                file_name = generate_csv_file(rela_general_info_tuple, header_rela, dict_st_label_end_label_rela_to_csv,
                                              True, 'rela/')
                generate_rela_queries(file_name, rela_general_info_tuple)
            rela_info_list = [start_identifier, end_identifier]
            rela_info_list.extend(rela_infos[2:])
            dict_st_label_end_label_rela_to_csv[rela_general_info_tuple].writerow(rela_info_list)
        counter += 1
        if counter % 500000 == 0:
            print(counter)


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('write indices in cypher file')

    write_indices_into_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('parse csv in other system')

    prepare_csv_file_to_csv_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
