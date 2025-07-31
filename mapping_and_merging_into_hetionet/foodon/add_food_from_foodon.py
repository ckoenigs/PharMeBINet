import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

# disease ontology license
license = 'CC BY 4.0'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# label of FO nodes
label_FO = 'FoodOn_Food'
# new label
label = 'Food'

# dictionary new FO
dict_new_FO_to_node = {}

# dictionary of the new nodes
dict_new_nodes = {}

# header of tsv file
header = []

# header to property name
dict_header_to_property = {}

'''
Get the  properties of FO
'''


def get_FO_properties():
    query = f'''MATCH (p:{label_FO}) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    result = g.run(query)

    part = ''' Match (b:%s{id:line.identifier})''' % (label_FO)
    query_nodes_start = part
    query_middle_new = ' Create (a:%s{'
    for record in result:
        property = record.data()['l']
        if property in ['def', 'id', 'alt_ids', 'xrefs', 'names']:
            if property == 'id':
                query_middle_new += 'identifier:b.' + property + ', '
            elif property == 'alt_ids':
                query_middle_new += 'alternative_ids:b.' + property + ', '
            elif property == 'xrefs':
                query_middle_new += 'xrefs:split(line.' + property + ',"|"), '
            elif property == 'names':
                query_middle_new += 'name:b.' + property + '[0], '

            else:
                query_middle_new += 'definition:b.' + property + ', '
        elif property in ["namespace", "is_obsolete", "replaced_by"]:
            continue
        else:
            query_middle_new += property + ':b.' + property + ', '
    query_end = ''' Create (a)-[:equal_to_FO]->(b)'''

    # combine the important parts of node creation
    query_new = query_nodes_start + query_middle_new + 'resource:["FoodOn"], foodon:"yes", source:"FoodON", url:"https://www.ebi.ac.uk/ols4/ontologies/foodon/classes?obo_id="+line.identifier, license:"' + license + '"})' + query_end
    return query_new


'''
create the tsv files
'''


def create_tsv_files():
    # prepare file and queries for new nodes
    file_name = 'output/integrate_FO.tsv'
    query = get_FO_properties() % (label)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/foodon/{file_name}',
                                              query)

    # cypher file
    with open('output/cypher.cypher', 'w', encoding='utf-8') as cypher_file:
        cypher_file.write(pharmebinetutils.prepare_index_query(label, 'identifier'))
        cypher_file.write(pharmebinetutils.prepare_index_query_text(label, 'name'))
        cypher_file.write(query)
    file = open(file_name, 'w')
    tsv_file = csv.writer(file, delimiter='\t')
    tsv_file.writerow(['identifier', 'xrefs'])
    return tsv_file


'''
Get all is_a relationships for bp, cc and mf and add the into a tsv file
'''


def get_is_a_relationships_and_add_to_tsv(cypher_file):
    query = f'''Match (n:{label_FO})-[r]->(m:{label_FO})  Where  n.id starts with "FOODON:"  and  m.id starts with "FOODON:" Return n.id,m.id, type(r)'''
    results = g.run(query)

    dict_type_to_tsv = {}

    # set of rela types which should not be considered
    # bearer_of?
    # has_quality?
    set_not_considered_rela_types = {"derives_from", "disjoint_from", "has_consumer", "immersed_in", "intersection_of",
                                     "in_taxon", "is_about", "member_of", "surrounded_by", "union_of"}

    # go through the results
    for record in results:
        [id1, id2, rela_type] = record.values()
        if rela_type in set_not_considered_rela_types:
            continue
        if rela_type not in dict_type_to_tsv:
            print(rela_type)
            file_name = f'edges/integrate_FO_relationship_{rela_type}.tsv'
            file = open(file_name, 'w')
            tsv_file = csv.writer(file, delimiter='\t')
            tsv_file.writerow(['identifier_1', 'identifier_2'])

            query = '''Match (a1:%s{identifier:line.identifier_1}), (a2:%s{identifier:line.identifier_2}) Create (a1)-[:%s{license:"%s", source:"FoodOn", unbiased:false, resource:["FoodOn"], foodon:'yes', url:"https://www.ebi.ac.uk/ols4/ontologies/foodon/classes?obo_id="+line.identifier_1}]->(a2)'''
            query = query % (label, label,
                             pharmebinetutils.prepare_rela_great(rela_type, label, label), license)
            query = pharmebinetutils.get_query_import(path_of_directory,
                                                      f'mapping_and_merging_into_hetionet/foodon/{file_name}',
                                                      query)
            cypher_file.write(query)
            dict_type_to_tsv[rela_type] = tsv_file

        dict_type_to_tsv[rela_type].writerow([id1, id2])


# set of foodon ids which are consumer
set_consumer_ids = set()


def get_consumer_from_foodon():
    """
    Get all foodon consumer
    :return:
    """
    query = '''Match (:%s)-[r]->(n:%s) Where n.id starts with "FOODON:" and type(r) in ["has_consumer","surrounded_by"] Return n.id''' % (
    label_FO, label_FO)
    for id, in g.run(query):
        set_consumer_ids.add(id)


'''
go through all FO nodes and sort them into the dictionary 
'''


def go_through_FO():
    tsv_file = create_tsv_files()
    query = '''Match (n:%s) Where n.id starts with "FOODON:" and n.is_obsolete is null Return n.id, n.xrefs''' % (
        label_FO)
    results = g.run(query)
    for identifier, xrefs, in results:
        if identifier in set_consumer_ids:
            continue
        new_xref = set()
        if xrefs:
            for xref in xrefs:
                splitted_xref = xref.split(' ')
                if len(splitted_xref) > 1:
                    new_xref.add(splitted_xref[0])
                else:
                    new_xref.add(xref)
        xref_string = "|".join(go_through_xrefs_and_change_if_needed_source_name(new_xref, label_FO))
        tsv_file.writerow([identifier, xref_string])


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('find all consumer')

    get_consumer_from_foodon()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.now())
    print('go through all FOs in dictionary')

    go_through_FO()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate pharmebinet dictionary')

    with open('output/cypher_edge.cypher', 'w', encoding='utf-8') as cypher_file:
        get_is_a_relationships_and_add_to_tsv(cypher_file)

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
