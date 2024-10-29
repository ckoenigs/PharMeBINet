import datetime
import sys, csv

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

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
    g = driver.session(database='graph')


# dictionary of all compounds with key the drugbank id and list of url, name, inchi, inchikey, food interaction,
# alternative ids
dict_compounds = {}

# old_properties
old_properties = []

# new compound properties
list_new_properties = []

# neo4j_label_drugbank='DrugBankdrug'
neo4j_label_drugbank = 'Compound_DrugBank'

# neo4j_interaction_rela_label='interacts'
neo4j_interaction_rela_label = 'INTERACTS_CHiCH'

# set of properties which are list element
set_of_list_properties = set([])


def get_properties_and_generate_tsv_files():
    """
    Get all properties of the pharmebinet compounds and drugbank compounds and use them to generate the tsv files
    :return:
    """

    # fill the list with all properties in drugbank and not in pharmebinet
    query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys
            UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
            RETURN allfields as l;''' % (neo4j_label_drugbank)
    result = g.run(query)
    for record in result:
        property = record.data()['l']
        if property =='external_identifiers':
            continue
        list_new_properties.append(property)

    list_new_properties.append('xrefs')
    global all_properties
    all_properties = list_new_properties

    # generate csv files
    global csv_new

    new_nodes = open('output/new_nodes.tsv', 'w', encoding='utf-8')
    csv_new = csv.writer(new_nodes, delimiter='\t')
    csv_new.writerow(['identifier','xrefs'])




def load_all_DrugBank_compound_in_dictionary():
    """
    Load in all information from DrugBank and generate unii-drugbank table file
    :return:
    """
    query = '''Match (n:''' + neo4j_label_drugbank + ''')  RETURN n.identifier, n.external_identifiers '''
    print(query)
    results = g.run(query)
    for record in results:
        [id, external_ids] = record.values()
        external_ids =external_ids if external_ids else []
        xrefs=go_through_xrefs_and_change_if_needed_source_name(external_ids,'chemical')
        csv_new.writerow([id,'|'.join(xrefs)])

    print('size of drugbank: ' + str(len(dict_compounds)))


# dictionary with (durg1, drug2) and url, description
dict_interact_relationships_with_infos = {}


def load_in_all_interaction_connection_from_drugbank_in_dict():
    """
    load all the interacts edges between compounds into a dictionary with the resource
    :return:
    """
    query = f'MATCH p=(a:{neo4j_label_drugbank})-[r:{neo4j_interaction_rela_label} ]->(b:{neo4j_label_drugbank}) RETURN a.identifier, r.description ,b.identifier '
    print(query)
    results = g.run(query)
    print(datetime.datetime.now())
    counter_interactions = 0
    counter_multiple = 0
    for record in results:
        [compound1_id, description, compound2_id] = record.values()
        counter_interactions += 1
        if (compound1_id, compound2_id) in dict_interact_relationships_with_infos:
            dict_interact_relationships_with_infos[(compound1_id, compound2_id)].append(description)
            counter_multiple += 1
        elif (compound2_id, compound1_id) in dict_interact_relationships_with_infos:
            dict_interact_relationships_with_infos[(compound2_id, compound1_id)].append(description)
            counter_multiple += 1
        else:
            dict_interact_relationships_with_infos[(compound1_id, compound2_id)] = [description]
    # counter+=1

    print(counter_interactions)
    print('number of double interaction:' + str(counter_multiple))
    print('number of interaction:' + str(len(dict_interact_relationships_with_infos)))




def create_cypher_file():
    # cypher file
    cypher_file = open('compound_interaction/cypher.cypher', 'w', encoding='utf-8')

    query_start = ''' Match (a:%s{identifier:line.identifier}) '''
    query_create = ''
    for property in all_properties:
        # this is for all similar
        if property in ['resource', 'license', 'source', 'url']:
            continue
        if property == 'xrefs':
            query_create += property + ':split(line.' + property + ',"|"), '
            continue
        # if property in set_of_list_properties:
        #     query_create += property + ':split(line.' + property + ',"||"), '
        # else:
        query_create += property + ':a.' + property + ', '



    query_create = query_start + 'Create (b:Compound{identifier:line.identifier, drugbank:"yes", ' + query_create + 'resource:["DrugBank"], source:"DrugBank", url:"http://www.drugbank.ca/drugs/"+line.identifier, license:"%s"}) Create (b)-[:equal_to_drugbank]->(a)'
    query_create = query_create % (neo4j_label_drugbank, license)

    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/drugbank/output/new_nodes.tsv',
                                                     query_create)
    cypher_file.write(query_create)

    cypher_file.write(pharmebinetutils.prepare_index_query('Compound','identifier'))
    cypher_file.write(pharmebinetutils.prepare_index_query_text('Compound', 'name'))



def generation_of_interaction_file():
    """
    Generate the the interaction file and the cypher file to integrate the information from the tsv into neo4j
    :return:
    """
    # generate cypher file for interaction
    counter_connection = 0

    counter_both_alternative = 0
    one_alternative = 0
    count_no_alternative = 0

    g_csv = open('compound_interaction/interaction.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(g_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['db1', 'db2', 'description'])
    cypherfile = open('output/cypher_rela.cypher', 'w', encoding='utf-8')
    query = ''' Match (c1:Compound{identifier:line.db1}), (c2:Compound{identifier:line.db2}) Create (c1)-[:INTERACTS_CHiCH{source:"DrugBank", url:"http://www.drugbank.ca/drugs/"+line.db1, unbiased:false, resource:['DrugBank'], drugbank:'yes',  license:'%s', descriptions:split(line.description,'||')}]->(c2) '''
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/compound_interaction/interaction.tsv',
                                              query)
    cypherfile.write(query)
    cypherfile.close()

    set_alt = set([])
    counter_all_interaction = 0

    for (compound1, compound2), description in dict_interact_relationships_with_infos.items():

        counter_all_interaction += len(description)
        description = list(set(description))
        description = '||'.join(description)
        count_no_alternative += 1
        counter_connection += 1
        description = description
        csv_writer.writerow([compound1, compound2, description])


    print(counter_connection)
    print('one has the alternative id in pharmebinet:' + str(one_alternative))
    print('both have the alternative id in pharmebinet:' + str(counter_both_alternative))
    print('both are in pharmebinet with normal id:' + str(count_no_alternative))
    print('counter of all interaction:' + str(counter_all_interaction))
    print(set_alt)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need license')
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
    print('load all properties of compound and drugbank compound and use the information to generate tsv files')

    get_properties_and_generate_tsv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('load all DrugBank compounds in dictionary')

    load_all_DrugBank_compound_in_dictionary()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all connection in dictionary')

    load_in_all_interaction_connection_from_drugbank_in_dict()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('create cypher queries and cypher file')

    create_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('generate cypher file for interaction')

    generation_of_interaction_file()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
