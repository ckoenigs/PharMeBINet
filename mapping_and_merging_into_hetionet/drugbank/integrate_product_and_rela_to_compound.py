from py2neo import Graph  # , authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))



#
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
    query = ''' MATCH (p:Product_DrugBank) WITH DISTINCT keys(p) AS keys
    UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
    RETURN allfields;'''


    results = g.run(query)

    query_start=''' Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/%s" As line FIELDTERMINATOR '\\t' 
    Match (n:Product_DrugBank{identifier:line.identifier}) Create (v:Product :Compound {'''
    for product_property, in results:
        query_start+= product_property +':n.'+product_property+', '

    query_start+= ' url:line.url, resource:["DrugBank"]})-[:equal_drugbank_product]->(n);\n'
    query=query_start %(path_of_directory, file_name)
    cypher_file=open('output/cypher.cypher', 'a', encoding='utf-8')
    cypher_file.write(query)
    query = 'Create Constraint On (node:Product) Assert node.identifier Is Unique;\n'
    cypher_file.write(query)
    cypher_file.close()
    cypher_rela = open('output/cypher_rela.csv', 'a', encoding='utf-8')
    query_rela='Match (n:Compound)--(:Compound_DrugBank)--(:Product_DrugBank)--(m:Product) Create (n)-[:HAS_ChP{source:"DrugBank", resource:["DrugBank"], license:"%s", drugbank:"yes"}]->(m);\n'
    query_rela= query_rela %(license)
    cypher_rela.write(query_rela)



def prepare_file():
    file_name='product/integration.tsv'
    file = open(file_name,'w', encoding='utf-8')
    csv_writer=csv.writer(file,  delimiter="\t")
    csv_writer.writerow(['identifier','url'])

    return csv_writer, file_name

'''
Load all Products and add to file
'''


def laod_all_products():
    # generate and get csv writer
    csv_writer, file_name=prepare_file()

    # prepare the
    prepare_cypher_query(file_name)

    # get products
    query = "MATCH (n:Product_DrugBank) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']
        source= node['source']
        name = node['name']
        url=dict_source_to_url[source]
        if source=="EMA":
            url=url %(name.lower())
        elif source=="FDA NDC":
            url= url %(identifier,identifier)
        csv_writer.writerow([identifier,url])



def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need a license')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all products from drugbank')

    laod_all_products()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
