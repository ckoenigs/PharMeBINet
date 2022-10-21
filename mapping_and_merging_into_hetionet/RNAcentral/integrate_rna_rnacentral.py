import csv, datetime
import json, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# cypher file
cypher_file = open("output/cypher.cypher", "w", encoding="utf-8")

# dictionary hgnc to gene ids
dict_hgnc_to_ids={}

# dictionary ensembl to gene ids
dict_ensmbl_to_ids={}

# dictionary gene_symbol to gene ids
dict_gene_symbol_to_ids={}

# dictionary gene id to resource
dict_gene_id_to_resource={}

def load_gene_into_dictionary():
    query="Match (a:Gene) Return a.identifier, a.xrefs, a.resource, a.gene_symbols"
    result=g.run(query)
    for gene_id, xrefs, resource, gene_symbols,  in result:
        dict_gene_id_to_resource[gene_id]=resource
        for gene_symbol in gene_symbols:
            pharmebinetutils.add_entry_to_dict_to_set(dict_gene_symbol_to_ids, gene_symbol.lower(), gene_id)

        if xrefs:
            for xref in xrefs:
                if xref.startswith("HGNC"):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_hgnc_to_ids, xref.split(':')[1], gene_id)
                elif xref.startswith("Ensembl"):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_ensmbl_to_ids, xref.split(':')[1], gene_id)



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
    properties_i = []
    query = "MATCH (p:rna1_RNACentral) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields"
    result = g.run(query)
    for property, in result:

        properties.append(property)
        if property != 'rnacentral_id':
            properties_i.append(property)
        else:
            properties_i.append('identifier')
    properties.append('locations')
    properties_i.append('locations')

    print(datetime.datetime.now())
    print("######### Start: generate TSV #########")

    query = "MATCH (n:rna1_RNACentral) RETURN n, n.rnacentral_id "
    result = g.run(query)

    file_name = 'output/RNACentral.tsv'
    counter=0
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        writer.writerow(properties_i)
        for node, rnacentral_id in result:
            if "geneName" in node:
                for gene_name in node["geneName"]:
                    if gene_name.startswith("ENSG"):
                        if gene_name in dict_ensmbl_to_ids:
                            counter+=1
                    elif gene_name.lower() in dict_gene_symbol_to_ids:
                        counter+=1

            if "xrefs" in node:
                for xref in node["xrefs"]:
                    if xref.startswith("HGNC"):
                        hgnc_id=xref.split(':')[-1]
                        if hgnc_id in dict_hgnc_to_ids:
                            counter+=1
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
    print('mapping to gene:', counter)
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
        if x in ['itemRgb', 'xrefs', 'databases', 'locations',
                 'geneName']:  # properties that are lists must be splitted
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

    print(datetime.datetime.now())
    print('#########################################################################')
    print('Generate connection to Neo4j')
    print(datetime.datetime.now())
    create_connection_with_neo4j()

    print(datetime.datetime.now())
    print('#########################################################################')
    print('Load gene information')

    load_gene_into_dictionary()

    print('Generate connection to Neo4j')
    print(datetime.datetime.now())
    print('#########################################################################')
    load_from_database()

    print(datetime.datetime.now())
    print('#########################################################################')


if __name__ == "__main__":
    # execute only if run as a script
    main()
