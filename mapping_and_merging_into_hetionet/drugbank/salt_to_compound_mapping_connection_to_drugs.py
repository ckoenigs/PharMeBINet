import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases  # , authenticate
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# label of salt
label_of_salt = 'Salt_DrugBank'

# name of the tsv file
file_node = 'salt_compound'

# name rela file
file_rela = 'salt_compound_rela'


def create_cypher_and_tsv_files():
    """
    Create cypher and tsv files for nodes and relationships
    :return:
    """
    # open cypher file
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    # get properties of salt nodes
    query = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    query = query % (label_of_salt)
    result = g.run(query)
    header = []
    part = '''Match (a:%s {identifier:line.identifier}) Create (b:Compound :Salt{'''
    part = part % (label_of_salt)
    for record in result:
        property = record.data()['l']
        part += property + ':line.' + property + ', '
        header.append(property)
    query = part + ' source:"DrugBank", license:"%s" ,drugbank:"yes", resource:["DrugBank"], url:"https://www.drugbank.ca/salts/"+line.identifier}) Create (b)-[:equal_to_drugbank]->(a)'
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/salts/{file_node}.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.close()
    node_file = open('salts/' + file_node + '.tsv', 'w')
    rela_file = open('salts/' + file_rela + '.tsv', 'w')
    global csv_node, csv_rela
    csv_node = csv.DictWriter(node_file, fieldnames=header, delimiter='\t')
    csv_node.writeheader()
    cypher_rela = open('output/cypher_rela.cypher', 'a', encoding='utf-8')
    rela_header = ['salt_id', 'compound_id']
    query_rela = 'Match (b:Compound :Salt{identifier:line.salt_id}), (a:Compound {identifier:line.compound_id}) Create (a)-[r:PART_OF_CpoSA{license:"%s", url:"https://go.drugbank.com/drugs/"+line.compound_id, source:"DrugBank", resource:["DrugBank"], drugbank:"yes" }]->(b)'
    query_rela = query_rela % (license)
    query_rela = pharmebinetutils.get_query_import(path_of_directory,
                                                   f'mapping_and_merging_into_hetionet/drugbank/salts/{file_rela}.tsv',
                                                   query_rela)
    cypher_rela.write(query_rela)
    cypher_rela.close()
    csv_rela = csv.writer(rela_file, delimiter='\t')
    csv_rela.writerow(rela_header)

    # delete compound nodes which are whether drugbank compound nor salt
    # this must be the last step of the compound integration, because else the merge nodes are also removed and this would be a problem
    cypher_delete_file = open('cypher_delete_compound.cypher', 'w')
    query = '''Match (c:Compound) Where c.drugbank is NULL Detach Delete c;\n'''
    cypher_delete_file.write(query)
    cypher_delete_file.close()


# the new table for unii drugbank pairs
unii_drugbank_table_file = open('data/map_unii_to_drugbank_id.tsv', 'a')
csv_unii_drugbank_table = csv.writer(unii_drugbank_table_file, delimiter='\t')




def prepare_node_tsv():
    """
    Gather all salt and make a new tsv to integrate them as compound into neo4j also check if a salt is on of the not
    mapped compounds. Prepare the tsv for salt integration, because they are not in pharmebinet they can be directly
    integrated, also check on the drugs which did not mapped, because some of them might be now salts
    :return:
    """
    query = '''MATCH (n:Salt_DrugBank) RETURN n'''
    result = g.run(query)
    for record in result:
        node = record.data()['n']
        csv_node.writerow(node)
        node_id = node['identifier']
        if 'unii' in node:
            unii = node['unii']
            csv_unii_drugbank_table.writerow([unii, node_id])


def fill_rela_tsv():
    """
    Fill the rela tsv file
    :return:
    """
    query = '''MATCH (n:Salt_DrugBank)-[:has_ChS]-(b:Compound_DrugBank) RETURN n.identifier, b.identifier'''
    result = g.run(query)
    for record in result:
        [salt_id, compound_id] = record.values()
        csv_rela.writerow([salt_id, compound_id])


def main():
    # path to directory of project
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need a license')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]
    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('open and create cypher and tsv files')

    create_cypher_and_tsv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('prepare node tsv and make bash for merging not mapped compounds to salt')

    prepare_node_tsv()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('create rela')

    fill_rela_tsv()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
