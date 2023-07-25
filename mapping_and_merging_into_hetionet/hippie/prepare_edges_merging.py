import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# highest identifier of interaction
highest_interaction_id = 0

# dictionary protein pair to interaction id
dict_protein_pair_to_interaction_id = {}

# dictionary interaction id to resource
dict_interaction_id_to_interaction_dictionary = {}


def load_existing_interactions():
    '''
    Load existing interaction information
    :return:
    '''
    global highest_interaction_id
    query = 'Match (a:Protein)-->(i:Interaction)-->(b:Protein) Where not (i.iso_of_protein_from is not NULL or i.iso_of_protein_to is not NULL)  Return a.identifier, b.identifier, i.identifier, i.resource, i.pubMed_ids,i.methods '
    results = g.run(query)
    for record in results:
        [protein1, protein2, interaction_id, resource, pubmed_ids, methods] = record.values()
        dict_protein_pair_to_interaction_id[(protein1, protein2)] = interaction_id
        methods = set(methods) if methods is not None else set()
        pubmed_ids = set(pubmed_ids) if pubmed_ids is not None else set()
        dict_interaction_id_to_interaction_dictionary[interaction_id] = {"resource": resource, "pubmed_ids": pubmed_ids,
                                                                         "methods": methods}

    query = 'MATCH (n:Interaction) With toInteger(n.identifier ) as int_id RETURN max(int_id) as m'

    highest_interaction_id = g.run(query).single()['m']


def generate_file_and_cypher(file_name_mapped, file_name_new):
    """
    generate cypher file and tsv file
    :return:
    """
    query = '''MATCH (:Protein_Hippie)-[p:INTERACTS]->(:Protein_Hippie) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields as l; '''
    results = g.run(query)

    file_name = 'output/rela'

    cypher_file = open('output/cypher_edge.cypher', 'w', encoding='utf-8')

    query = '''Match (p1:Protein{identifier:line.protein_id_1}), (p2:Protein{identifier:line.protein_id_2}) Create (p1)-[:INTERACTS_PiI{hippie:'yes', source:'HIPPIE', resource:['HIPPIE'], url:"http://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/query.php?s="+line.protein_id_1 ,license:"free to use for academic purposes"}]->(b:Interaction{ '''
    query_update = '''Match (p1:Protein{identifier:line.id_1})-[r]->(i:Interaction{identifier:line.id})-[b]->(p2:Protein{identifier:line.id_2}) Set r.resource=split(line.resource, "|"), r.hippie="yes",  b.resource=split(line.resource, "|"), b.hippie="yes", i.resource=split(line.resource, "|"), '''

    header = ['protein_id_1', 'protein_id_2', 'id']
    for record in results:
        head = record.data()['l']
        header.append(head)
        if head in ['publication_id', 'detection_methods', 'source_dbs']:
            if head not in ['publication_id', 'detection_methods']:
                query += head + ':split(line.' + head + ',"|"), '
                query_update += 'i.' + head + '=split(line.' + head + ',"|"), '
            else:
                if head == 'publication_id':
                    query += 'pubMed_ids:split(line.' + head + ',"|"), '
                    query_update += 'i.pubMed_ids=split(line.' + head + ',"|"), '
                else:
                    query += 'methods:split(line.' + head + ',"|"), '
                    query_update += 'i.methods=split(line.' + head + ',"|"), '
        elif head in ['publication_author']:
            continue
        else:
            query += head + ':line.' + head + ', '
            query_update += 'i.' + head + '=line.' + head + ', '

    query += ' license:"free to use for academic purposes", identifier:line.id,url:"http://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/query.php?s="+line.protein_id_1, source:"HIPPIE", node_edge:true, hippie:"yes", resource:["HIPPIE"]})-[:INTERACTS_IiP{hippie:"yes", source:"HIPPIE", resource:["HIPPIE"], url:"http://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/query.php?s="+line.protein_id_1 ,license:"free to use for academic purposes"}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hippie/{file_name_new}',
                                              query)
    cypher_file.write(query)
    query_update += '''i.pubMed_ids=split(line.pubmed_ids, "|"), i.methods=split(line.methods, "|"), i.hippie="yes" '''

    query_update = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/hippie/{file_name_mapped}',
                                              query_update)
    cypher_file.write(query_update)

    cypher_file.close()

    file = open(file_name_new, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()

    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_writer_mapped = csv.writer(file_mapped, delimiter='\t')
    csv_writer_mapped.writerow(['id', 'resource', 'id_1', 'id_2', 'pubmed_ids', 'methods'])

    return csv_writer, csv_writer_mapped


def prepare_dictionary(dictionary, counter):
    """
    prepare the list values in dictionary to strings
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) in [list, set]:
            value = '|'.join(value)
        new_dict[key] = value
    new_dict['id'] = counter
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}

# dictionary mapped pair to interaction id
dict_mapped_pair_to_interaction_id = {}


def addMappedEdgeInformation(p1_id, p2_id, rela_info):
    interaction_id = dict_protein_pair_to_interaction_id[(p1_id, p2_id)]
    if (p1_id, p2_id, interaction_id) not in dict_mapped_pair_to_interaction_id:
        dict_mapped_pair_to_interaction_id[(p1_id, p2_id, interaction_id)] = []
    dict_mapped_pair_to_interaction_id[
        (p1_id, p2_id, dict_protein_pair_to_interaction_id[(p1_id, p2_id)])].append(rela_info)


def run_through_results_and_add_to_dictionary(results):
    """
    run through all results and add to the dictionaries. ALso check if have rela to go!
    :param results: neo4j result
    :return:
    """
    for record in results:
        [p1_id, rela, p2_id] = record.values()
        rela_info = dict(rela)
        if type(rela_info['publication_id']) == set:
            print('crazy')
        # use as now directed edges
        if (p1_id, p2_id) in dict_protein_pair_to_interaction_id:
            addMappedEdgeInformation(p1_id, p2_id, rela_info)
            continue
        # elif (p2_id,p1_id) in dict_protein_pair_to_interaction_id:
        #     addMappedEdgeInformation(p2_id ,p1_id,rela_info)
        #     continue
        # print(p1_id,p2_id)
        if (p1_id, p2_id) not in dict_pair_to_infos:
            dict_pair_to_infos[(p1_id, p2_id)] = []

        publications = set()
        prepare_pubmed_information(rela, publications)
        rela_info['publication_id'] = publications

        methods = set()
        prepare_method_information(rela, methods)
        rela_info['detection_methods'] = methods

        rela_info['protein_id_1'] = p1_id
        rela_info['protein_id_2'] = p2_id

        dict_pair_to_infos[(p1_id, p2_id)].append(rela_info)


def load_and_prepare_IID_human_data():
    """
    write only rela with exp into file
    """

    query = '''Match (p1:Protein)-[:equal_to_protein_hippie]-(d:Protein_Hippie)-[r:INTERACTS]->(:Protein_Hippie)-[:equal_to_protein_hippie]-(p2:Protein) Where r.publication_id is not NULL   Return p1.identifier, r, p2.identifier '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)

    # to check for selfloops interaction
    query = '''Match p=(a:Protein)-[:equal_to_protein_hippie]->(d:Protein_Hippie)-[r:INTERACTS]-(d) Where r.publication_id is not NULL  Return  a.identifier as p1 , r, a.identifier as p2 '''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)


def prepare_pubmed_information(rela_information, publications):
    if 'publication_id' in rela_information:
        for publication in rela_information['publication_id']:
            if publication.startswith('pubmed'):
                publications.add(publication.split(':')[1])
            else:
                print('other source then pubmed', publication)
    else:
        print('has no publications')


def prepare_method_information(rela_information, methods):
    if 'detection_methods' in rela_information:
        for method in rela_information['detection_methods']:
            if '(' in method:
                methods.add(method.split('(', 1)[1][:-1])
            else:
                methods.add(method)

    # else:
    #     print('has no detection_methods')


def write_info_into_files():
    csv_writer, csv_writer_mapping = generate_file_and_cypher("output/mapped_interaction.tsv",
                                                              "output/new_interactions.tsv")
    counter = highest_interaction_id

    print('###################################### new ##############################################')
    # prepare the new interactions
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        counter += 1

        if len(list_of_dict) == 1:
            csv_writer.writerow(prepare_dictionary(list_of_dict[0], counter))
        else:
            # print('multi')
            new_dict = {}
            for dictionary in list_of_dict:
                for key, value in dictionary.items():
                    if not key in new_dict:
                        if key != 'confidence_value':
                            new_dict[key] = value
                        else:
                            new_dict[key] = float(value)
                    elif key == 'confidence_value':
                        new_dict[key] += float(value)


                    elif new_dict[key] != value:
                        # print(p1)
                        # print(p2)
                        # print(key)
                        # print(value)
                        # print(new_dict[key])
                        if type(value) == list or type(value) == set:
                            set_value = set(value)
                            set_value = set_value.union(new_dict[key])
                            new_dict[key] = set_value
                        else:
                            print('other properties')
            # compute average confidence value
            new_dict['confidence_value'] = new_dict['confidence_value'] / len(list_of_dict)
            csv_writer.writerow(prepare_dictionary(new_dict, counter))
        if counter % 10000 == 0:
            print(counter)

    print('############################################ mapping ##################################################')

    #  detection_methods==methods, publication_id==pubMed_ids
    for (protein_1, protein_2, interaction_id), list_rela_information in dict_mapped_pair_to_interaction_id.items():
        publications = dict_interaction_id_to_interaction_dictionary[interaction_id]['pubmed_ids']

        methods = dict_interaction_id_to_interaction_dictionary[interaction_id]['methods']
        for rela_information in list_rela_information:
            prepare_pubmed_information(rela_information, publications)
            prepare_method_information(rela_information, methods)

        csv_writer_mapping.writerow([interaction_id, pharmebinetutils.resource_add_and_prepare(
            dict_interaction_id_to_interaction_dictionary[interaction_id]['resource'], 'HIPPIE'), protein_1,
                                     protein_2, '|'.join(publications), '|'.join(methods)])


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate connection to neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load existing interactions')

    load_existing_interactions()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('load Hippie human data')

    load_and_prepare_IID_human_data()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('prepare files')

    write_info_into_files()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
