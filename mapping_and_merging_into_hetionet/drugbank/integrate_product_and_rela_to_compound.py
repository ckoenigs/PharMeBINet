import datetime
import sys, csv

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


# dictionary source to url
dict_source_to_url = {
    "FDA NDC": "https://ndclist.com/ndc/%s/package/%s",  # double id
    "EMA": "https://www.ema.europa.eu/en/medicines/human/EPAR/%s",  # name
    "DPD": "https://health-products.canada.ca/dpd-bdpp/index-eng.jsp"
}


def prepare_cypher_query(file_name):
    """
    get all properties of drugbank product and add to list of header
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    # query = 'Create Constraint On (node:Product) Assert node.identifier Is Unique'
    # cypher_file.write(query)

    query = ''' MATCH (p:Product_DrugBank) WITH DISTINCT keys(p) AS keys
    UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
    RETURN allfields as l;'''

    results = g.run(query)

    query_start = '''Match (n:Product_DrugBank{identifier:line.identifier}) Create (v:Product {'''
    for record in results:
        product_property = record.data()['l']
        query_start += product_property + ':n.' + product_property + ', '

    query_start += ' url:line.url, resource:["DrugBank"], drugbank:"yes", license:"%s"})-[:equal_drugbank_product]->(n)'
    query = query_start % (license)

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/{file_name}',
                                              query)
    cypher_file.write(pharmebinetutils.prepare_index_query('Product', 'identifier'))
    cypher_file.write(pharmebinetutils.prepare_index_query_text('Product', 'name'))
    cypher_file.write(query)
    cypher_file.close()
    cypher_rela = open('output/cypher_rela.cypher', 'a', encoding='utf-8')
    query_rela = 'Match (n:Compound)--(:Compound_DrugBank)--(:Product_DrugBank)--(m:Product) With Distinct n, m Create (n)-[:HAS_CHhPR{source:"DrugBank", resource:["DrugBank"], license:"%s", drugbank:"yes"}]->(m);\n'
    query_rela = query_rela % (license)
    cypher_rela.write(query_rela)


def prepare_file():
    """
    prepare TSV file and return csv writer and file name.
    :return: 
    """
    file_name = 'product/integration.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter="\t")
    csv_writer.writerow(['identifier', 'url'])

    return csv_writer, file_name


def load_all_products():
    """
    Load all Products and add to file
    :return: 
    """
    # generate and get csv writer
    csv_writer, file_name = prepare_file()

    # prepare the
    prepare_cypher_query(file_name)

    # get products
    query = "MATCH (n:Product_DrugBank) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        source = node['source']
        name = node['name']
        url = dict_source_to_url[source]
        if source == "EMA":
            url = url % (name.lower())
        elif source == "FDA NDC":
            url = url % (identifier, identifier)
        csv_writer.writerow([identifier, url])


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need a license')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all products from drugbank')

    load_all_products()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
