from py2neo import Graph
import sys
import datetime
import csv
from itertools import groupby


def database_connection():
    '''
    create connection to neo4j
    '''
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))


# dictionary disease id to disease node
dict_disease_id_to_disease_node = {}

# dictionary xrefs to disease id
dict_xref_to_disease_id = {}

# dictionary disease names to set disease ids
dict_disease_name_to_ids = {}

# dictionary disease name and synonyms to set diease ids
dict_disease_name_synonyms_to_ids = {}


def load_genes_from_database_and_add_to_dict():
    '''
    Load all Disease from my database  and add them into a dictionary
    '''
    query = "MATCH (n:Disease) RETURN n"
    results = g.run(query)
    for disease, in results:
        identifier = disease['identifier']
        dict_disease_id_to_disease_node[identifier] = dict(disease)
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        for xref in xrefs:
            if xref not in dict_xref_to_disease_id:
                dict_xref_to_disease_id[xref] = set()
            dict_xref_to_disease_id[xref].add(identifier)
        if 'name' in disease:
            name = disease['name'].lower()
            if name not in dict_disease_name_to_ids:
                dict_disease_name_to_ids[name]=set()
            dict_disease_name_to_ids[name].add(identifier)


        prepare_name_synonym_for_disease(identifier, dict(disease), dict_disease_name_synonyms_to_ids,
                                         name_to_check=True)


cypher_file = open('disease/cypher_disease.cypher', 'w', encoding='utf-8')

query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/clinvar/disease/%s.tsv" As line FIELDTERMINATOR '\\t' 
    Match '''


def add_query_to_cypher_file():
    '''
    add query for a specific csv to cypher file
    '''
    this_start_query = query_start + "(n:trait_Disease_ClinVar {identifier:line.trait_id}), (m:Disease{identifier:line.disease_id}) Create (m)-[:equal_to_clinvar_disease{mapping_methode:split(line.mapping_method,'|')}]->(n);\n"
    query = this_start_query % (path_of_directory, 'mapping')
    cypher_file.write(query)


# dictionary_clinvar_disease_id_to_node
dict_clinvar_id_to_node = {}

# dictionary of mapping tuples
dict_of_mapped_tuples = {}

# set of not mapped clinvar disease ids
set_not_mapped_ids = set()

# set of all xrefs from clinvar
set_of_all_xref_types = set()

# set of all xref type used for mapping
set_of_all_xref_types_to_map = set()

# dictionary from xref type in clinvar to the different in mondo
dict_cv_type_to_mondo_type = {
    'MeSH': 'MESH'
}


def load_all_clinvar_disease_and_start_mapping():
    """
    load all trait disease in and mapp with xref to the mondo diseases
    """
    query = "MATCH (n:trait_Disease_ClinVar) RETURN n"
    results = g.run(query)
    counter_mapped = 0
    for node, in results:
        identifier = node['identifier']

        dict_clinvar_id_to_node[identifier] = dict(node)

        xrefs = node['xrefs'] if 'xrefs' in node else []

        found_at_least_one_mapping = False
        for xref in xrefs:
            xref_type = xref.split(':')[0]
            set_of_all_xref_types.add(xref_type)
            # some source are different written
            if xref_type in dict_cv_type_to_mondo_type:
                xref = xref.replace(xref_type, dict_cv_type_to_mondo_type[xref_type])
            # hpo is in mondo but do not have an extra prefix
            elif xref_type == 'Human Phenotype Ontology':
                xref = xref.split(':', 1)[1]
            # has a differnet id for like EFO:EFO_id
            elif xref_type == 'EFO':
                xref = xref.replace('EFO_', '')
            elif xref_type == 'OMIM':
                if 'PS' in xref:
                    xref = xref.replace('PS', '').replace('OMIM', 'OMIMPS')

            if xref in dict_xref_to_disease_id:
                for disease_id in dict_xref_to_disease_id[xref]:
                    mapping_pair = (identifier, disease_id)
                    if mapping_pair not in dict_of_mapped_tuples:
                        dict_of_mapped_tuples[mapping_pair] = set()
                    set_of_all_xref_types_to_map.add(xref_type)
                    dict_of_mapped_tuples[mapping_pair].add(xref_type)
                found_at_least_one_mapping = True

        if not found_at_least_one_mapping:
            set_not_mapped_ids.add(identifier)
        else:
            counter_mapped += 1

    print(dict_of_mapped_tuples)
    print('number of mapped disease:' + str(counter_mapped))
    print('number of not mapped disease:' + str(len(set_not_mapped_ids)))
    print(set_of_all_xref_types)
    print('used xref:')
    print(set_of_all_xref_types_to_map)


def group_mappings_after_trait(set_of_infos):
    """
    gruped a list of tuples after the first tuple element
    :param set_of_infos: set of tuples
    :return:
    """
    group_function = lambda x: x[0]
    return groupby(set_of_infos, group_function)


def prepare_name_synonym_for_disease(disease_id, dictionary_with_names, to_dictionary, id=False, name_to_check=False):
    """
    check name and synonyms for a disease id out. prepare the strings.
    the synonyms have often in the end [source:id] so this is splitted.
    :param disease_id: string
    """
    if 'name' in dictionary_with_names:
        disease_name = dictionary_with_names['name'].lower()
        if name_to_check:
            if disease_name not in to_dictionary:
                to_dictionary[disease_name] = set()
            to_dictionary[disease_name].add(disease_id)
    else:
        disease_name = ''
    disease_synoynms = dictionary_with_names['synonyms'] if 'synonyms' in dictionary_with_names else []

    disease_set_names = set([disease_name]) if disease_name != '' else set()
    for synonym in disease_synoynms:
        if synonym[-1] == ']':
            synonym = synonym.rsplit('[')[0]
        synonym = synonym.lower()
        disease_set_names.add(synonym)
        if name_to_check:
            if synonym not in to_dictionary:
                to_dictionary[synonym] = set()
            to_dictionary[synonym].add(disease_id)
    if id:
        to_dictionary[disease_id] = disease_set_names


# dictionary of disease id to preparted synonyms
dict_disease_id_to_synonymsy_set = {}


def write_into_csv_file(disease_id, trait_id, trait_name, tuple_pair, csv_mapping_writer, mapped_with=None):
    """
    write into the csv file
    :param disease_id: string
    :param trait_id: string
    :param trait_name:  string
    :param tuple_pair: tuple
    :param csv_mapping_writer: csv writer
    """
    disease_name = dict_disease_id_to_disease_node[disease_id]['name'] if 'name' in \
                                                                          dict_disease_id_to_disease_node[
                                                                              disease_id] else ''
    mapping_set = dict_of_mapped_tuples[tuple_pair] if tuple_pair in dict_of_mapped_tuples else mapped_with
    csv_mapping_writer.writerow([trait_id, disease_id, "|".join(list(mapping_set)), trait_name, disease_name])

def check_for_mapping_and_write_in_csv_file(name, dictionary,counter_new_mapped, trait_id,mapped_ids, mapped_with):
    """
    check if name mapps to a given dictionary and if so write into a csv file
    :param name: stirng
    :param dictionary:  dictionary
    :param counter_new_mapped: int
    :param trait_id: string
    :param mapped_ids: set
    :param mapped_with: list with mapping methods
    :return: found a mappping or not , the counter
    """
    name = name.lower()
    if name in dictionary:
        counter_new_mapped += 1
        mapped_ids.add(trait_id)
        for disease_id in dictionary[name]:
            write_into_csv_file(disease_id, trait_id, name, (trait_id, disease_id), csv_mapping_writer,
                                mapped_with=mapped_with)
        return True, counter_new_mapped
    return False, counter_new_mapped


# files for mapping csv
file_mapping = open('disease/mapping.tsv', 'w', encoding='utf-8')
csv_mapping_writer = csv.writer(file_mapping, delimiter='\t')
csv_mapping_writer.writerow(['trait_id', 'disease_id', 'mapping_method'])


def mapping_with_name():
    """
    mapping with only name of traint to name and synoynms in clinvar
    """
    counter_new_mapped = 0
    mapped_ids = set()
    for trait_id in set_not_mapped_ids:
        if 'name' in dict_clinvar_id_to_node[trait_id]:
            name = dict_clinvar_id_to_node[trait_id]['name']
            found, counter_new_mapped= check_for_mapping_and_write_in_csv_file(name, dict_disease_name_to_ids, counter_new_mapped, trait_id, mapped_ids, ['name'])
            if found:
                continue

            # only if no name-name mapping is possible then check from name to name and synonyms from mondo
            found, counter_new_mapped = check_for_mapping_and_write_in_csv_file(name, dict_disease_name_synonyms_to_ids,
                                                                                counter_new_mapped, trait_id,
                                                                                mapped_ids,['name and synonyms'])
            if found:
                continue

        # only if no mappng is found the check for synonyms
        if 'synonyms' in dict_clinvar_id_to_node[trait_id]:
            found_synonyms = False
            for synonym in dict_clinvar_id_to_node[trait_id]['synonyms']:
                synonym = synonym.lower()
                if synonym in dict_disease_name_synonyms_to_ids:
                    found_synonyms = True
                    for disease_id in dict_disease_name_synonyms_to_ids[synonym]:
                        write_into_csv_file(disease_id, trait_id, synonym, (trait_id, disease_id), csv_mapping_writer,
                                            mapped_with=['synonym'])
            if found_synonyms:
                counter_new_mapped += 1
                mapped_ids.add(trait_id)

    for trait_id in mapped_ids:
        set_not_mapped_ids.remove(trait_id)

    print('number of new mapped:' + str(counter_new_mapped))
    print('number of not mapped:' + str(len(set_not_mapped_ids)))


def write_in_csv_files():
    """
    write in the different csv files, the mapped and not mapped ids
    """

    # because a lot of multiple mapping between trait disease and disease appears and not all are so good it try to reduce this
    # with check name mapping

    # group after trait id
    for trait_id, group in group_mappings_after_trait(dict_of_mapped_tuples.keys()):
        group = list(group)
        trait_name = dict_clinvar_id_to_node[trait_id]['name'] if 'name' in dict_clinvar_id_to_node[trait_id] else ''
        # not multiple mapped can be written directly into the csv file
        if len(group) == 1:
            tuple_pair = group[0]
            disease_id = tuple_pair[1]
            write_into_csv_file(disease_id, trait_id, trait_name, tuple_pair, csv_mapping_writer)
            continue
        synonyms_trait = [x.lower() for x in dict_clinvar_id_to_node[trait_id]['synonyms']] if 'synonyms' in \
                                                                                               dict_clinvar_id_to_node[
                                                                                                   trait_id] else []
        synonyms_trait = set(synonyms_trait)
        synonyms_trait.add(trait_name.lower())

        found_exact_map = False
        list_of_exact_map = set()
        for (x, disease_id) in group:
            if disease_id not in dict_disease_id_to_synonymsy_set:
                prepare_name_synonym_for_disease(disease_id, dict_disease_id_to_disease_node,
                                                 dict_disease_id_to_synonymsy_set, id=True)
            intersection = synonyms_trait.intersection(dict_disease_id_to_synonymsy_set[disease_id])

            # search for similar names
            if len(intersection) > 0:
                found_exact_map = True
                list_of_exact_map.add(disease_id)

        if found_exact_map:
            for disease_id in list_of_exact_map:
                write_into_csv_file(disease_id, trait_id, trait_name, (trait_id, disease_id), csv_mapping_writer)
        else:
            for (x, disease_id) in group:
                write_into_csv_file(disease_id, trait_id, trait_name, (trait_id, disease_id), csv_mapping_writer)

    file_mapping.close()

    # files for not mapped
    file = open('disease/not_mapping.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['trait_id', 'name', 'xrefs'])

    for trait_id in set_not_mapped_ids:
        name = dict_clinvar_id_to_node[trait_id]['name'] if 'name' in dict_clinvar_id_to_node[trait_id] else ''
        xrefs = dict_clinvar_id_to_node[trait_id]['xrefs'] if 'xrefs' in dict_clinvar_id_to_node[trait_id] else ''
        csv_writer.writerow([trait_id, name, "|".join(xrefs)])


def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ClinVar')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all disease from database')

    load_genes_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all disease clinvar from database')

    load_all_clinvar_disease_and_start_mapping()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Mapping with names')

    mapping_with_name()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher file')

    add_query_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Write the csv')

    write_in_csv_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
