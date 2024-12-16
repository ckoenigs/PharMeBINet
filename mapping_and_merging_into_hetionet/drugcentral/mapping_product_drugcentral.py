import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session(database='graph')


# dictionary
dict_productId_to_resource = {}
dict_ndc_pc = defaultdict(set)
dict_product_mapping = defaultdict(dict)


def load_product_in():
    """
    Load all Products and take the ndc product codes into a dictionary.
    :return:
    """
    query = '''MATCH (n:Product) RETURN n'''
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        ndc_pc = node["ndc_product_code"] if "ndc_product_code" in node else ""
        name = node["name"]

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

    for record in results:
        node = record.data()['n']
        node_id = record.data()['id(n)']
        prod_ndc = node["ndc_product_code"]
        product_name = node["product_name"] if "product_name" in node else []

        if product_name:
            product_name = product_name[0].lower()

        if prod_ndc in dict_ndc_pc:
            products = dict_ndc_pc[prod_ndc]
            for product_id in products:
                if product_id not in dict_product_mapping[node_id]:
                    dict_product_mapping[node_id][product_id] = set()
                dict_product_mapping[node_id][product_id].add('ndc_pc')
                mapped_products.add(node_id)

        if node_id not in mapped_products:
            csv_not_mapped.writerow([node_id, prod_ndc, product_name])

    for node_id in mapped_products:
        for product_id in dict_product_mapping[node_id]:
            methodes = list(dict_product_mapping[node_id][product_id])
            methodes = '|'.join(methodes)
            resource = set(dict_productId_to_resource[product_id])
            csv_mapped.writerow(
                [node_id, product_id, pharmebinetutils.resource_add_and_prepare(resource, 'DrugCentral'), methodes])


def generate_tsv_files():
    """
    Generate tsv files for mapped and not mapped. Additionally, the cypher query is generated.
    :return:
    """
    global csv_mapped, csv_not_mapped
    # file for not mapped identifier
    file_not_mapped_protein = open('product/not_mapped_product.tsv', 'w', encoding="utf-8")
    # Dateiformat wird gesetzt mit Trenner: Tabulator
    csv_not_mapped = csv.writer(file_not_mapped_protein, delimiter='\t', lineterminator='\n')
    # Header setzen
    csv_not_mapped.writerow(['id', 'ndc', 'name'])
    # prepare mapped file
    file_name = 'product/mapped_product.tsv'
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
    query = ''' MATCH (n:DC_Product), (c:Product{identifier:line.id_hetionet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_Product_drugcentral{how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/product/" + file_name,
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path dc product')
    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('generate tsv files and cypher file')

    generate_tsv_files()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("load product in")
    load_product_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print("load DC_product_in")
    load_DC_product_in()

    generate_cypher_file('mapped_product.tsv')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
