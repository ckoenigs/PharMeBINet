import csv, datetime
import json, sys

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# cypher file
cypher_file = open("output/cypher.cypher", "w", encoding="utf-8")


def load_from_database():
    print(datetime.datetime.now())
    print("######### load_from_database ##################")

    rna2_RNACentral = {}
    query = "MATCH p=(s:rna1_RNACentral)-[r:associate]->(n:rna2_RNACentral) RETURN n, s.rnacentral_id"
    result = g.run(query)
    for node, rnacentral_id, in result:
        if rnacentral_id not in rna2_RNACentral:
            a = dict(node)
            del a['id']
            rna2_RNACentral[rnacentral_id] = [json.dumps(a)]
        else:
            a = dict(node)
            del a['id']
            rna2_RNACentral[rnacentral_id].append(json.dumps(a))

    print(rna2_RNACentral['URS00019A6210_9606'])
    properties = []
    query = "MATCH (p:rna1_RNACentral) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields"
    result = g.run(query)
    for property, in result:
        properties.append(property)
    properties.append('locations')

    print(datetime.datetime.now())
    print("######### Start: generate TSV #########")

    query = "MATCH (n:rna1_RNACentral) RETURN n, n.rnacentral_id"
    result = g.run(query)

    file_name = 'output/RNACentral.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        properties_i = properties.copy()
        properties_i[2] = "identifier"
        writer.writerow(properties_i)

        for node, rnacentral_id in result:
            list = []
            for i in properties:
                if i == "locations" and rnacentral_id in rna2_RNACentral:
                    list.append("|".join(rna2_RNACentral[rnacentral_id]))
                else:
                    if isinstance(node.get(i), type(list)) == True:
                        s = ""
                        for x in node.get(i):
                            s = s + "|" + x
                        list.append(s[1:])
                    else:
                        list.append(node.get(i, ''))

            writer.writerow(list)
    tsv_file.close()
    print(datetime.datetime.now())
    print("######### End: generate TSV #########")

    cypher(properties_i, file_name, "RNA", 'identifier')


def cypher(keys, file_name, label, unique_identifier):
    '''
    generates cypher query to integrate nodes into neo4j
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    '''

    print(datetime.datetime.now())
    print("######### cypher file ##################")
    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAcentral/{file_name}" As line fieldterminator "\t" '
    query = query_start + f' Match (p1:rna1_RNACentral{{rnacentral_id:line.identifier}}) '
    query = query + 'Create (p:%s{' % (label)

    for x in keys:
        if x in ['itemRgb', 'xrefs', 'databases', 'locations']:  # properties that are lists must be splitted
            query += x + ':split(line.' + x + ',"|"), '
        else:
            query += x + ':line.' + x + ', '

    query = query + ' rnacentral:"yes", url:"https://rnacentral.org/rna/"+split(line.identifier,"_")[0]+"/"+split(line.identifier,"_")[1], license:"CC0", resource:["RNAcentral"], source:"RNAcentral"})'
    query = query + f' Create (p1)-[:equal_to_rnacenral]->(p);\n'

    cypher_file.write(query)

    query2 = 'Create Constraint On (node:%s) Assert node.%s Is Unique; \n' % (label, unique_identifier)
    cypher_file.write(query2)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnaCentral')

    print('Generate connection to Neo4j')
    print(datetime.datetime.now())
    create_connection_with_neo4j()

    print('Generate connection to Neo4j')
    print(datetime.datetime.now())
    print('#########################################################################')
    load_from_database()

    print(datetime.datetime.now())
    print('#########################################################################')


if __name__ == "__main__":
    # execute only if run as a script
    main()
