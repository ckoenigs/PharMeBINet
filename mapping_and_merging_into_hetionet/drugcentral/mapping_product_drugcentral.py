from py2neo import Graph
import datetime
import csv
import sys
import html
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary
dict_product_to_name = {}
dict_productId_to_resource = {}
dict_ndc_pc = defaultdict(set)


def load_product_in():
    """
    Load all Products and take the ndc product codes into a dictionary.
    :return:
    """
    query = '''MATCH (n:Product) RETURN n'''
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        ndc_pc = node["ndc_product_code"] if "ndc_product_code" in node else ""
        name = node["name"]

        # im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        dict_product_to_name[identifier] = name

        dict_productId_to_resource[identifier] = resource

        if ndc_pc != "":
            dict_ndc_pc[ndc_pc].add(identifier)


def load_DC_product_in():
    """
    Load all drugcentral products and map to product with ndc product code
    :return:
    """
    query = '''MATCH (n:DC_Product) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_products = set()
    dict_nodes_to_product = {}
    dict_node_to_methode = {}

    for node, node_id, in results:
        prod_ndc = node["ndc_product_code"]
        product_name = node["product_name"]
        product_name = product_name.lower()

        if prod_ndc in dict_ndc_pc:
            products = dict_ndc_pc[prod_ndc]
            for product_id in products:
                dict_nodes_to_product[node_id] = product_id
                if node_id not in dict_node_to_methode:
                    dict_node_to_methode[node_id] = set()
                dict_node_to_methode[node_id].add('ndc_pc')
                mapped_products.add(node_id)

        if node_id not in mapped_products:
            csv_not_mapped.writerow([node_id, prod_ndc, product_name])

    for node_id in mapped_products:
        methodes = list(dict_node_to_methode[node_id])
        product_id = dict_nodes_to_product[node_id]
        resource = set(dict_productId_to_resource[product_id])
        resource.add('DrugCentral')
        resource = '|'.join(resource)
        csv_mapped.writerow([node_id, product_id, resource, methodes])

def generate_csv_files():
    """
    Generate csv files for mapped and not mapped. Additionally, the cypher query is generated.
    :return:
    """
    global csv_mapped, csv_not_mapped
    # file for mapped or not mapped identifier
    # erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
    file_not_mapped_protein = open('product/not_mapped_product.tsv', 'w', encoding="utf-8")
    # Dateiformat wird gesetzt mit Trenner: Tabulator
    csv_not_mapped = csv.writer(file_not_mapped_protein, delimiter='\t', lineterminator='\n')
    # Header setzen
    csv_not_mapped.writerow(['id', 'ndc', 'name'])

    # prepare mapped file
    file_name='product/mapped_product.tsv'
    file_mapped_protein = open(file_name, 'w', encoding="utf-8")
    csv_mapped = csv.writer(file_mapped_protein, delimiter='\t', lineterminator='\n')
    csv_mapped.writerow(['node_id', 'id_hetionet', 'resource', 'how_mapped'])

    generate_cypher_file(file_name)


def generate_cypher_file(file_name):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugcentral/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:DC_Product), (c:Product{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_Product_drugcentral{how_mappeds:line.how_mapped}]->(n); \n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral product protein')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('generate csv files and cypher file')

    generate_csv_files()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print("load product in")

    load_product_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print("load DC_product_in")

    load_DC_product_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
