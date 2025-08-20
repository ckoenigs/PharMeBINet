import sys
import datetime, csv
from itertools import groupby
from collections import defaultdict

sys.path.append("../..")
import pharmebinetutils


# use to delimit between the blocks
def contains_information(line):
    return True if line.strip() else False


if len(sys.argv) != 5:
    sys.exit('need the obo file, directory, neo4j label')

# file path to data source
file_name = sys.argv[1]

# directory
directory = sys.argv[2]

# neo4j label
neo4j_label = sys.argv[3]

# path to project directory
path_of_directory = sys.argv[4]

# dictionary with all identifier and a dictionary for all information of this identifier
dict_all_entries = {}

# all properties
set_all_properties_in_database = set([])

# list of all properties which are lists
set_list_properties = set([])

# list other relationships
list_other_rela = set([])

# dictionary with list of the other relationships
dict_other_rela_parent_child = defaultdict(set)

# type definition dictionary
type_def = {}

# set of all properties with !
set_properties_with_bang = set([])

# counter of all relationships
counter_rela = 0

'''

'''


def add_information_to_dictionary(dict_all_info, key_term, value):
    if value[-1] == '}':
        # print(key_term, value)
        splitted_value = value.split(' {')
        value = splitted_value[0]
        if len(splitted_value) > 1:
            if key_term == 'xref' and not ('equivalentTo' in splitted_value[1] or 'xref=' in splitted_value[
                1]):  # ('superClassOf' in splitted_value[1] or 'subClassOf' in splitted_value[1]) and
                # print('removed', splitted_value)
                return
    # for some properties more than one value appears
    if not key_term in dict_all_info:
        dict_all_info[key_term] = value.replace("\\", "")
    # if more than one value appears for a key the key is add to the list of multi values keys
    # also the values are connected with a |
    else:
        dict_all_info[key_term] += '|' + value.replace("\\", "")
        set_list_properties.add(key_term)


# dictionary which form
dict_synonyms = {
    'EXACT': 'synonym',
    'BROAD': 'broad_synonym',
    'RELATED': 'related_synonym',
    'NARROW': 'narrow_synonym'
}

list_synonyms_type = dict_synonyms.keys()

'''
go through a block of information and add the node information into a dictionary
the relationships are either shown as relationships or contain a !
return the identifier of the node and all node information as dictionary
'''


def extract_information_from_block(group, is_type):
    global counter_rela
    # dictionary for all values
    dict_all_info = {}
    # go through all properties of the block
    for info in group:
        # seperate key and value
        (key_term, value) = [element.strip() for element in info.split(":", 1)]
        # check if the key is a relationship or not and add the information to the right dictionary
        if key_term != 'relationship':
            # print(value)
            # some other relationships are not defined A RELATIONSHIP but have a ' ! '
            if value.find(' ! ') == -1:
                if key_term != 'synonym':
                    if value == 'UBERON:4000171':
                        print('test')
                    add_information_to_dictionary(dict_all_info, key_term, value)
                    set_all_properties_in_database.add(key_term)
                else:

                    found_type = False

                    for synonym_type, key_name in dict_synonyms.items():
                        if '" ' + synonym_type + ' ' in value:
                            found_type = True
                            first_part_synonym_second_additional_information = value.split(' ' + synonym_type + ' ', 1)
                            synonym = first_part_synonym_second_additional_information[0]
                            new_key = key_name
                            addtional_info_and_xrefs = first_part_synonym_second_additional_information[1].split("[", 1)
                            if len(addtional_info_and_xrefs[1]) > 1:
                                synonym += ' [' + addtional_info_and_xrefs[1]
                            else:
                                if synonym.startswith('"') and synonym[-1] == '"':
                                    synonym = synonym[1:-1]

                    if not found_type:
                        print(value)
                        sys.exit('different formart for synonyms')
                    add_information_to_dictionary(dict_all_info, new_key, synonym)
                    set_all_properties_in_database.add(new_key)


            # check for not type definition the relationship
            elif not is_type:
                set_properties_with_bang.add(key_term)
                identifier = dict_all_info['id']
                split_whole_into_rela_and_additional_part = value.strip().split(' ! ')
                parent_id = split_whole_into_rela_and_additional_part[0].split(' {')[0]
                counter_rela += 1
                splitted_parent_id = parent_id.split(' ')
                key_term = key_term.replace('-', '_')
                if len(splitted_parent_id) > 1:
                    # should be only intersection_of
                    if len(splitted_parent_id) == 2:
                        rela = splitted_parent_id[0]
                        parent_id = splitted_parent_id[1]
                        dict_other_rela_parent_child[key_term].add((parent_id, identifier, rela+':'+split_whole_into_rela_and_additional_part[1]))
                        continue
                    else:
                        add_information_to_dictionary(dict_all_info, key_term, value)
                        set_all_properties_in_database.add(key_term)
                        continue
                dict_other_rela_parent_child[key_term].add((parent_id, identifier, split_whole_into_rela_and_additional_part[1]))
                list_other_rela.add(key_term)

        # is a relationship but depending on the type it is add to a different set
        else:
            rela_info = value.split('!')[0].split(' ')
            rela_type = rela_info[0].replace('-', '_')
            parent_id = rela_info[1]
            identifier = dict_all_info['id']
            dict_other_rela_parent_child[rela_type].add((parent_id, identifier, value.split('!')[1].strip() if '!' in value else ''))
            list_other_rela.add(rela_type)

    return dict_all_info['id'], dict_all_info


'''
group the terms together and get the information from the different terms and gather all term information in a dictionary
further fill the dictionary for the hierarchical set
'''


def gather_information_from_obo():
    # open the obo file
    with open(file_name, encoding='utf-8') as f:
        # group lines together which are in a block and go through every block
        f.readline()
        line_2 = f.readline()
        file = open('version_obo.txt', 'w')
        file.write(line_2)
        file.close()
        for (key, group) in groupby(f, contains_information):
            if key:
                # for python 2.*
                # header = group.next().rstrip('\n')
                # for python 3.*
                # print(group.__next__())
                header = group.__next__().rstrip('\n')

                # take only the information from the terms and add to dictionary and add relationships to dictionaries
                if header.find('[Term]') >= 0:
                    identifier, dict_all_info = extract_information_from_block(group, False)
                    dict_all_entries[identifier] = dict_all_info
                # remember the type definition
                elif header.find('[Typedef]') >= 0:

                    identifier, dict_all_info = extract_information_from_block(group, True)
                    type_def[identifier] = dict_all_info

    print(set_properties_with_bang)
    print(counter_rela)


'''
generate cypher file
'''


def generate_cypher_file():
    # create cypher file
    cypher_file = open('cypher.cypher', 'w')
    cypher_file_edge = open('cypher_edge.cypher', 'w')
    query = ''' Create (:''' + neo4j_label + '''{'''
    for property in set_all_properties_in_database:
        if not property in set_list_properties:
            query += property + ':line.' + property + ', '
        # add a 's' at the end of a list property, because they have multiple values :D
        else:
            query += property + 's:split(line.' + property + ',"|"), '
    query = query[:-2] + '})'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              '''import_into_Neo4j/''' + directory + '/output/node.tsv', query)
    cypher_file.write(query)
    cypher_file.write(pharmebinetutils.prepare_index_query(neo4j_label, 'id'))

    # create node tsv
    file = open('output/node.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=list(set_all_properties_in_database), delimiter='\t')
    csv_writer.writeheader()

    for disease_id, dict_value in dict_all_entries.items():
        # add all properties of a node into csv file
        csv_writer.writerow(dict_value)
    file.close()

    print(list_other_rela)

    header_for_two = ['parent_id', 'child_id']
    heeader_for_three = ['parent_id', 'child_id', 'rela']

    # generate cypher query and csv for all rela types
    for rela_type, list_of_infos in dict_other_rela_parent_child.items():
        if ':' in rela_type and rela_type not in type_def:
            print('no rela name')
            print(rela_type)
            continue
        if rela_type in type_def:
            if 'name' in type_def[rela_type]:
                if not rela_type == type_def[rela_type]['name']:
                    # because a typedef can have multiple names only one is needed
                    if len(type_def[rela_type]['name'].split('|')) > 1:
                        type_def[rela_type]['name'] = type_def[rela_type]['name'].split('|')[0]
                    rela_type = type_def[rela_type]['name'].replace(' ', '_').replace('-', '_').replace('(','_').replace(')','_').replace('__','_') if not '/' in type_def[
                        rela_type][
                        'name'] else rela_type
                    rela_type = rela_type if rela_type[-1]!='_' else rela_type[:-1]

        # create csv for relationships
        file_name = 'rela_' + rela_type + '.tsv'
        file = open('output/' + file_name, 'w')
        csv_writer = csv.writer(file, delimiter='\t')
        list_of_infos = list(list_of_infos)
        # depending if the relationships contains also information about a relationships type the query and the csv file is a bit different
        if len(list_of_infos[0]) == 2:
            query = ''' Match (a:%s{id:line.child_id}), (b:%s{id:line.parent_id}) Create (a)-[:%s]->(b)'''
            csv_writer.writerow(header_for_two)
        else:
            print(rela_type)
            query = ''' Match (a:%s{id:line.child_id}), (b:%s{id:line.parent_id}) Create (a)-[:%s{relationship:line.rela}]->(b)'''
            csv_writer.writerow(heeader_for_three)
        # fill the query ND WRITE INTO FILE
        query = query % (neo4j_label, neo4j_label, rela_type)
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'import_into_Neo4j/{directory}/output/{file_name}', query)
        cypher_file_edge.write(query)

        # write information into the csv file
        for info in list_of_infos:
            info = list(info)
            csv_writer.writerow(info)
        file.close()


def main():
    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('gather symptoms information ')

    gather_information_from_obo()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('put all relationship and node information into a tsv and create a cypher file')

    generate_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
