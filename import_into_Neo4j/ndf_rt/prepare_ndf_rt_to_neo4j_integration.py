import xml.dom.minidom as dom

import datetime, csv, sys

sys.path.append("../..")
import pharmebinetutils

# dictionary of all entities with code as key and value is the entity
dict_entities = {}

# dictionary of all properties with code as key and the name as value
dict_properties = {}

# dictionary of all qualifiers with code as key and the name as value
dict_qualifiers = {}

# dictionary of all association with code as key and the name as value
dict_associations = {}

# dictionary with all ndf-rt relationships
dict_relationships = {}

# dictionary with entity as key and and value a list of dictionaries of the different nodes
dict_entity_to_nodes = {}

# dictionary entity to file
dict_entity_to_file = {}

# dictionary relationship to file name
dict_rela_to_file = {}

# dictionary filename to file
dict_rela_file_name_to_file = {}

'''
add all information into a given dictionary
'''


def extract_and_add_info_into_dictionary(dictionary, terminology, element):
    element_list = terminology.getElementsByTagName(element)
    for combined_element in element_list:
        name = combined_element.getElementsByTagName('name')[0].childNodes[0].nodeValue
        code = combined_element.getElementsByTagName('code')[0].childNodes[0].nodeValue
        dictionary[code] = name


# cypher file to integrate nodes and relationships
cypher_file = open('cypher_file.cypher', 'w', encoding='utf-8')

# cypher file to delte nodes without relationships
cypher_file_delete = open('cypher_file_delete.cypher', 'w', encoding='utf-8')

# dictionary rela file name to code combination
dict_rela_to_list_of_code_tuples = {}


def load_ndf_rt_xml_inferred_in():
    print(datetime.datetime.now())
    tree = dom.parse("NDFRT_Public_2018.02.05_TDE.xml")
    print(datetime.datetime.now())

    terminology = tree.documentElement

    # save all kindDef (Entities) in a dictionary with code and name
    extract_and_add_info_into_dictionary(dict_entities, terminology, 'kindDef')
    properties_of_node = ['code', "name", "id", "properties"]
    for code, entity_name in dict_entities.items():
        file_name = 'results/' + entity_name + '_file.tsv'
        entity_file = open(file_name, 'w', encoding='utf-8')
        csv_writer = csv.writer(entity_file, delimiter='\t', quotechar='"', lineterminator='\n')
        csv_writer.writerow(properties_of_node)
        dict_entity_to_file[code] = csv_writer
        query = ''' Create (n: NDFRT_''' + entity_name + '{'
        for propertie in properties_of_node:
            if not propertie in ['properties']:
                query += propertie + ':line.' + propertie + ','
            else:
                query += propertie + ':split(line.' + propertie + ',"|"),'
        query = query[:-1] + '})'
        query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/ndf_rt/{file_name}', query)
        cypher_file.write(query)
        # create index on code of all ndf-rt enities
        cypher_file.write(pharmebinetutils.prepare_index_query('NDFRT_' + entity_name, 'code'))
        query = '''Match (n: NDFRT_''' + entity_name + ''') Where not (n)-[]-() Delete n; \n'''
        cypher_file_delete.write(query)

    # save for all properties the code and name in a dictionary
    extract_and_add_info_into_dictionary(dict_properties, terminology, 'propertyDef')

    # save all qualifier in a dictionary with code and name
    extract_and_add_info_into_dictionary(dict_qualifiers, terminology, 'qualifierDef')

    # save all association in a dictionary
    extract_and_add_info_into_dictionary(dict_associations, terminology, 'associationDef')

    # save all association in a dictionary and generate the different cypher queries for the different relationships
    element_list = terminology.getElementsByTagName('roleDef')
    rela_info_list = ['start_node', 'end_node', 'source']
    for combined_element in element_list:
        name_source = combined_element.getElementsByTagName('name')[0].childNodes[0].nodeValue
        name_source = name_source.split(' {')
        name = name_source[0]
        source = name_source[1].replace('}', '')
        code = combined_element.getElementsByTagName('code')[0].childNodes[0].nodeValue
        dict_relationships[code] = [name, source]

        # this part is for generating and adding the cypher queries
        start_node_code = combined_element.getElementsByTagName('domain')[0].childNodes[0].nodeValue
        end_node_code = combined_element.getElementsByTagName('range')[0].childNodes[0].nodeValue

        file_name = 'results/' + name + '_file.tsv'
        dict_rela_to_file[code] = file_name
        if file_name not in dict_rela_file_name_to_file:
            dict_rela_to_list_of_code_tuples[file_name] = []
            entity_file = open(file_name, 'w', encoding='utf-8')
            csv_writer = csv.writer(entity_file, delimiter='\t', quotechar='"', lineterminator='\n')
            csv_writer.writerow(rela_info_list)
            dict_rela_file_name_to_file[file_name] = csv_writer
            query = ''' Match (start: NDFRT_''' + \
                    dict_entities[start_node_code] + '''{code:line.''' + rela_info_list[0] + '''}), (end: NDFRT_''' + \
                    dict_entities[end_node_code] + '''{code:line.''' + rela_info_list[
                        1] + '''}) Create (start)-[:%s{source:line.source}]->(end)'''
            # print(query)
            query = query % (name)
            query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/ndf_rt/{file_name}', query)

            cypher_file.write(query)

    # get all important concepts
    concepts = terminology.getElementsByTagName('conceptDef')
    # dictionary code to type
    dict_code_to_type = {}
    # dictionary association pairs
    dict_association_pair = {}
    for concept in concepts:
        # gete information about node
        entity_code = concept.getElementsByTagName('kind')[0].childNodes[0].nodeValue
        name = concept.getElementsByTagName('name')[0].childNodes[0].nodeValue
        code = concept.getElementsByTagName('code')[0].childNodes[0].nodeValue
        ndf_rt_id = concept.getElementsByTagName('id')[0].childNodes[0].nodeValue
        dict_code_to_type[code] = entity_code

        # go through all possible Role (Relationships) and add the to the different tsv files
        definitionRoles = concept.getElementsByTagName('definingRoles')[0]
        if definitionRoles.hasChildNodes() == True:
            roles = definitionRoles.getElementsByTagName('role')
            for role in roles:
                rela_code = role.getElementsByTagName('name')[0].childNodes[0].nodeValue
                to_code = role.getElementsByTagName('value')[0].childNodes[0].nodeValue
                if (code, to_code) not in dict_rela_to_list_of_code_tuples[dict_rela_to_file[rela_code]]:
                    dict_rela_file_name_to_file[dict_rela_to_file[rela_code]].writerow(
                        [code, to_code, dict_relationships[rela_code][1]])
                    dict_rela_to_list_of_code_tuples[dict_rela_to_file[rela_code]].append((code, to_code))

        # go through all properties of this drug and generate a list of string
        prop = concept.getElementsByTagName('properties')[0]
        properties = prop.getElementsByTagName('property')
        properties_list = []
        for proper in properties:
            name_property = proper.getElementsByTagName('name')[0].childNodes[0].nodeValue
            value = proper.getElementsByTagName('value')[0].childNodes[0].nodeValue
            value = value.replace('"', '\'')
            text = dict_properties[name_property] + ':' + value
            properties_list.append(text)

        properties_string = '|'.join(properties_list)

        # go through association of this drug and generate a list of string
        association_list = []
        if len(concept.getElementsByTagName('associations')) > 0:
            associat = concept.getElementsByTagName('associations')[0]
            associations = associat.getElementsByTagName('association')

            if len(associations) > 0:

                for association in associations:
                    name_association = association.getElementsByTagName('name')[0].childNodes[0].nodeValue
                    value = association.getElementsByTagName('value')[0].childNodes[0].nodeValue
                    text = dict_associations[name_association] + ':' + value
                    association_list.append(text)
                    dict_association_pair[(code, value)] = dict_associations[name_association]
        # association_string='|'.join(association_list)

        dict_entity_to_file[entity_code].writerow([code, name, ndf_rt_id, properties_string])

    association_file = open('results/associates_file.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(association_file, delimiter='\t', quotechar='"', lineterminator='\n')
    csv_writer.writerow(['code1', 'code2'])
    query = ''' Match (start: NDFRT_DRUG_KIND{code:line.code1}), (end: NDFRT_DRUG_KIND {code:line.code2}) Create (start)-[:product_of]->(end)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'import_into_Neo4j/ndf_rt/results/associates_file.tsv', query)
    cypher_file.write(query)
    for (code1, code2), association_name in dict_association_pair.items():
        csv_writer.writerow([code1, code2])
    association_file.close()


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ndf-rt')

    # start the function to load in the xml file and save the importen values in list and dictionaries
    print('#############################################################')
    print(datetime.datetime.now())
    print('load in the xml data')
    load_ndf_rt_xml_inferred_in()

    print('#############################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
