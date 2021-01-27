import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of all disease ids to resource
dict_disease_to_resource = {}

# dictionary disease symbol to disease id
dict_disease_name_to_disease_id = {}

# dictionary umls to disease
dict_umls_to_disease={}
# dictionary mesh to disease
dict_mesh_to_disease={}
# dictionary meddra to disease
dict_meddra_to_disease={}

def add_entry_to_dictionary(dictionary, key, value):
    if key not in dictionary:
        dictionary[key]=set()
    dictionary[key].add(value)

'''
load in all compound from hetionet in a dictionary
'''


def load_db_diseases_in():
    query = '''MATCH (n:Disease) RETURN n.identifier, n.name ,n.synonyms, n.resource, n.xrefs'''
    results = g.run(query)

    for identifier, name,  synonyms, resource, xrefs,  in results:
        dict_disease_to_resource[identifier] = set(resource) if resource else set()

        name=name.lower()
        add_entry_to_dictionary(dict_disease_name_to_disease_id,name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                add_entry_to_dictionary(dict_disease_name_to_disease_id, synonym, identifier)

        if xrefs:
            for xref in xrefs:
                if xref.startswith('UMLS'):
                    xref=xref.split(':',1)[1]
                    add_entry_to_dictionary(dict_umls_to_disease, xref, identifier)
                elif xref.startswith('MESH'):
                    xref=xref.split(':',1)[1]
                    add_entry_to_dictionary(dict_mesh_to_disease, xref, identifier)
                elif xref.startswith('MedDRA'):
                    xref=xref.split(':',1)[1]
                    add_entry_to_dictionary(dict_meddra_to_disease, xref, identifier)



    print('length of disease in db:' + str(len(dict_disease_to_resource)))


def check_for_mapping(dict_source_to_ids, source, dict_source_to_disease_ids, csv_writer, identifier):
    """
    go through all cui_ids of the different sources and check if the are in the dictionary to disease id. If so add
    them into csv file.
    :param dict_source_to_ids:
    :param source:
    :param dict_source_to_disease_ids:
    :param csv_writer:
    :param identifier:
    :return:
    """
    found_mapping=False
    for cui in dict_source_to_ids[source]:
        if cui in dict_source_to_disease_ids:
            found_mapping = True
            for disease_id in dict_source_to_disease_ids[cui]:
                resource = dict_disease_to_resource[disease_id]
                resource.add("PharmGKB")
                resource = "|".join(sorted(resource))
                csv_writer.writerow([disease_id, identifier, resource, source.lower()])
    return found_mapping

def load_pharmgkb_phenotypes_in():
    """
    diseaserate mapping file and cypher file
    mapp disease pharmgkb to disease
    :return:
    """
    # csv_file
    file_name = 'disease/mapping.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['disease_id', 'pharmgkb_id', 'resource', 'how_mapped'])

    # diseaserate cypher file
    diseaserate_cypher_file(file_name)

    query = '''MATCH (n:PharmGKB_Phenotype) RETURN n'''
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    for result, in results:
        identifier = result['id']
        dict_names={}
        name = result['name'].lower() if 'name' in result else ''
        add_entry_to_dictionary(dict_names,'name',name)

        external_identifiers = result['external_vocabulary'] if 'external_vocabulary' in result else []
        dict_source_to_ids={}
        for external_identifier in external_identifiers:
            source_info=external_identifier.split(':',1)
            add_entry_to_dictionary(dict_source_to_ids,source_info[0],source_info[1].split('(')[0])


        found_a_mapping = False

        if 'UMLS' in dict_source_to_ids:
            found_a_mapping=check_for_mapping(dict_source_to_ids, 'UMLS', dict_umls_to_disease, csv_writer,identifier)

        if found_a_mapping:
            continue

        if 'MeSH' in dict_source_to_ids:
            found_a_mapping=check_for_mapping(dict_source_to_ids, 'MeSH', dict_mesh_to_disease, csv_writer,identifier)

        if found_a_mapping:
            continue

        if 'MedDRA' in dict_source_to_ids:
            found_a_mapping=check_for_mapping(dict_source_to_ids, 'MedDRA', dict_meddra_to_disease, csv_writer,identifier)

        if found_a_mapping:
            continue

        if 'name' in dict_names:
            found_a_mapping=check_for_mapping(dict_names, 'name', dict_disease_name_to_disease_id, csv_writer,identifier)

        if found_a_mapping:
            continue

        # alternate_names would be another possibility


        counter_map += 1
    print('number of diseases which mapped:', counter_map)
    print('number of diseases which not mapped:', counter_not_mapped)


def diseaserate_cypher_file(file_name):
    cypher_file = open('output/cypher.cypher', 'a')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:PharmGKB_disease{id:line.pharmgkb_id}), (c:disease{identifier:line.disease_id})  Set c.pharmgkb='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_disease_pharmgkb{how_mapped:line.how_mapped}]->(n); \n'''
    query = query % (file_name)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in disease from hetionet')

    load_db_diseases_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in disease from pharmgb in')

    load_pharmgkb_phenotypes_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
