import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()

# dictionary with hetionet disease with name as key and value the identifier
dict_disease_hetionet_names = {}

# dictionary with hetionet disease with synonym as key and value set of identifiers
dict_disease_hetionet_synonyms = {}

#dictionary from own id to new identifier
dict_doid_id_to_identifier = {}

#dictionary from disease_id to resource
dict_diseaseId_to_resource = {}

def add_to_dict(dictionary, key, one_value):
    """
    add information to a dictionary of form key to set
    :param dictionary: dictionary
    :param key: any key
    :param one_value: any value
    :return:
    """
    if not key in dictionary:
        dictionary[key]= set()
    dictionary[key].add(one_value)

'''
load in all disease from hetionet in a dictionary
'''


def load_hetionet_disease_in():
    query = '''MATCH (n:Disease) RETURN n.identifier, n.name, n.alternative_ids, n.resource, n.synonyms'''
    results = graph_database.run(query)

    #run through results
    for identifier, name, alternative_ids, resource, synonyms, in results:
        # if identifier == "MONDO:0005244":
        #     print("Egal was")
        dict_diseaseId_to_resource[identifier] = resource
        # run through alternative ids and prepare with the doid identifier a dictionary
        if alternative_ids:
            for doid in alternative_ids:
                if not doid.startswith('DOID:'):
                    continue
                doid = doid.replace("DOID:", "")
                add_to_dict(dict_doid_id_to_identifier,doid, identifier)

        if name:
            dict_disease_hetionet_names[name.lower()] = identifier

        if synonyms:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                add_to_dict(dict_disease_hetionet_synonyms,synonym, identifier)


    print('number of disease nodes in hetionet:' + str(len(dict_diseaseId_to_resource)))

# file for mapped or not mapped identifier
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_disease,delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id','name'])

file_mapped_disease = open('disease/mapped_disease.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_disease,delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id','id_hetionet', 'resource', 'how_mapped'])

def prepare_and_write_information_into_tsv(disease_id,identifier, how_mapped):
    """
    Prepare resource and write information into tsv file.
    :param disease_id: identifier of reactome
    :param identifier: identifier of pharmebinet
    :param how_mapped: string
    :return:
    """
    csv_mapped.writerow([disease_id, identifier, pharmebinetutils.resource_add_and_prepare(dict_diseaseId_to_resource[identifier],'Reactome'), how_mapped])

'''
load all reatome disease and check if they are in hetionet or not
'''


def load_reactome_disease_in():
    global highest_identifier
    query = '''MATCH (n:Disease_reactome) RETURN n'''
    results = graph_database.run(query)

    #count the different mappings
    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_map_with_synonyms=0
    for disease_node, in results:
        disease_id = disease_node['identifier']
        if disease_id=='104':
            print('huh')
        disease_name = disease_node['displayName'].lower()
        mapped_with_name_or_id=False
        #mapping with doid
        if disease_id in dict_doid_id_to_identifier:
            counter_map_with_id += 1
            mapped_with_name_or_id=True
            for pharmebinet_identifier in dict_doid_id_to_identifier[disease_id]:
                prepare_and_write_information_into_tsv(disease_id,pharmebinet_identifier,'disease_id')

        #mapping with name
        elif disease_name in dict_disease_hetionet_names:
            mapped_with_name_or_id=True
            counter_map_with_name += 1
            print(disease_id)
            print('mapped with name')
            print(dict_disease_hetionet_names[disease_name])
            print(disease_name)
            pharmebinet_identifier = dict_disease_hetionet_names[disease_name]
            prepare_and_write_information_into_tsv(disease_id,pharmebinet_identifier,'name')

        if mapped_with_name_or_id:
            continue
        # mapping with synonyms
        if disease_name in dict_disease_hetionet_synonyms:
            counter_map_with_synonyms+=1
            for pharmebinet_identifier in dict_disease_hetionet_synonyms[disease_name]:
                prepare_and_write_information_into_tsv(disease_id, pharmebinet_identifier, 'synonyms')


        #not mapped node are writen in other tsv file
        else:
            csv_not_mapped.writerow([disease_id, disease_name])

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('number of mapping with synonyms:' + str(counter_map_with_synonyms))

'''
generate connection between mapping disease of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    """
    prepare cypher query to integrate mapping and write query into cypher file
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding="utf-8")
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/disease/mapped_disease.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Disease{identifier:line.id_hetionet}),(c:Disease_reactome{identifier:line.id}) CREATE (d)-[: equal_to_reactome_disease{how_mapped:line.how_mapped}]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query= query % (path_of_directory)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')
    print (datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())
    print('Load all disease from hetionet into a dictionary')

    load_hetionet_disease_in()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())
    print('Load all reactome disease from neo4j into a dictionary')

    load_reactome_disease_in()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())
    print('Integrate new disease and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
