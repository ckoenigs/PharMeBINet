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


def add_entry_to_dictionary(dictionary, key, value):
    """
    prepare dictionary with value
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)


def generate_file_and_cypher():
    """
    generate cypher file and tsv file
    :return:
    """

    file_name = 'treatment/rela'
    file_name_go = 'treatment/rela_go'

    cypher_file = open('output/cypher_drug_edge.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/reactome/%s.tsv" As line FIELDTERMINATOR '\\t'
            Match (p1:Chemical{identifier:line.drug_reactome_id}), (p2:Disease{identifier:line.disease_reactome_id}) Create (p1)-[:TREATS_CHtT{license:"%s", reactome:"yes", source:"Reactome", resource:["Reactome"]}]->(b:Treatment{license:"%s", reactome:"yes", source:"Reactome", resource:["Reactome"], url:"https://reactome.org/content/detail/"+line.stid, stoichiometry: line.stoichiometry , order:line.order , identifier:"T_"+line.id, node_edge:true})-[:TREATS_TtD{license:"%s", reactome:"yes", source:"Reactome", resource:["Reactome"]}]->(p2);\n '''
    query = query % (path_of_directory, file_name, license, license, license)
    header = ['drug_reactome_id', 'disease_reactome_id', 'id', 'stoichiometry', 'order', 'stid']
    cypher_file.write(query)
    cypher_file.write('Create Constraint On (node:Treatment) Assert node.identifier Is Unique;\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/reactome/%s.tsv" As line FIELDTERMINATOR '\\t'
                Match (i:Treatment{identifier:"T_"+line.id}), (c:CellularComponent{identifier:line.go_id}) Set i.subcellular_location="GO term enrichment" Create (i)-[:IS_LOCALIZED_IN_TiliCC{license:"%s", reactome:"yes", source:"Reactome", resource:["Reactome"]}]->(c);\n'''
    query = query % (path_of_directory, file_name_go, license)
    cypher_file.write(query)
    cypher_file.close()

    file = open(file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()

    file_go = open(file_name_go + '.tsv', 'w', encoding='utf-8')
    csv_writer_go = csv.writer(file_go, delimiter='\t')
    csv_writer_go.writerow(['id', 'go_id'])
    return csv_writer, csv_writer_go


def prepare_dictionary(dictionary, counter):
    """
    prepare the list values in dictionary to strings
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) == list:
            value = '|'.join(value)
        new_dict[key] = value
    new_dict['id'] = counter
    return new_dict


# dictionary rela pairs to infos
dict_pair_to_infos = {}


# dictionary pair to go
dict_pair_to_go_ids = {}


def run_through_results_and_add_to_dictionary(results):
    """
    run through all results and add to the dictionaries. ALso check if have rela to go!
    :param results: neo4j result
    :return:
    """
    #hier muss noch go dazu
    for p1_id, rela, p2, p2_id, go_accession, stid, in results:
        rela_info = dict(rela)
        go_accession = "GO:" + go_accession
        if (p1_id, p2_id) not in dict_pair_to_infos:
            dict_pair_to_infos[(p1_id, p2_id)] = []
            dict_pair_to_go_ids[(p1_id, p2_id)] = set()

        dict_pair_to_go_ids[(p1_id, p2_id)].add(go_accession)

        rela_info['drug_reactome_id'] = p1_id
        rela_info['disease_reactome_id'] = p2_id
        rela_info['stid']=stid

        dict_pair_to_infos[(p1_id, p2_id)].append(rela_info)


def load_and_prepare_reactome_data():
    """
    write only rela with exp into file
    """

    query = '''match p=(c:Chemical)--(:ReferenceTherapeutic_reactome)--(d:Drug_reactome)-[rela:disease]-(:Disease_reactome)--(e:Disease) with c,d,e,rela match (d)--(f:GO_CellularComponent_reactome) return c.identifier, rela, e,  e.identifier , f.accession, d.stId'''
    results = g.run(query)
    run_through_results_and_add_to_dictionary(results)


def write_info_into_files():
    csv_writer, csv_writer_go = generate_file_and_cypher()
    counter = 0
    for (p1, p2), list_of_dict in dict_pair_to_infos.items():
        counter += 1

        if (p1, p2) in dict_pair_to_go_ids:
            for go in dict_pair_to_go_ids[(p1, p2)]:
                csv_writer_go.writerow([counter, go])

        if len(list_of_dict) == 1:
            csv_writer.writerow(prepare_dictionary(list_of_dict[0], counter))
        else:
            print('multi')
            new_dict = {}
            for dictionary in list_of_dict:
                for key, value in dictionary.items():
                    if not key in new_dict:
                        new_dict[key] = value
                    elif new_dict[key] != value:
                        print(p1)
                        print(p2)
                        print(key)
                        print(value)
                        print(new_dict[key])
                        if type(value) == list:
                            set_value = set(value)
                            set_value = set_value.union(new_dict[key])
                            new_dict[key] = list(set_value)
                        else:
                            print('also different type problem')

            csv_writer.writerow(prepare_dictionary(new_dict, counter))
        if counter % 10000 == 0:
            print(counter)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license reactome edge')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate connection to neo4j')

    create_connection_with_neo4j()


    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('load reactome data')

    load_and_prepare_reactome_data()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('prepare files')

    write_info_into_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
