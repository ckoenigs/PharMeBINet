from py2neo import Graph
import datetime
import csv
import sys

'''
create connection to neo4j
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global graph_database
    graph_database = Graph("http://localhost:7474/db/data/", auth= ("neo4j", "test"))



#dictionary with name hetionet as key and uniprotID as value
dict_uniprot_id_to_name ={}

#dictionary with name hetionet as key and alternative ids as value
dict_name_alt_ids_hetionet = {}

#dictionary with name reactome as key and uniprotID as value
dict_name_uniprot_reactome = {}

#dictionary with uniprotID as key and resource as value
dict_uniprot_to_resource =  {}

dict_alternative_id_to_protein_id = {}

'''
load in all uniprotIDs of Protein from hetionet in a dictionary
'''

def load_hetionet_uniprotIDs_in():
    query = '''MATCH (n:Protein) RETURN n.identifier, n.name, n.alternative_ids, n.resource'''
    results = graph_database.run(query)

    for identifier, name, alternative_ids, resource, in results:
        dict_uniprot_id_to_name[identifier] = name.lower()
        dict_uniprot_to_resource[identifier] = resource if resource else []
        if alternative_ids:
            for alt_id in alternative_ids:
                #print(alt_id)
                dict_alternative_id_to_protein_id[alt_id] = identifier

    print('number of uniprotIDs in hetionet Protein:' + str(len(dict_uniprot_id_to_name)))

file_not_mapped_uniprotIDs = open('uniprotIDs/not_mapped_uniprotIDs.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_uniprotIDs,delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['id','name'])

file_mapped_uniprotIDs = open('uniprotIDs/mapped_uniprotIDs.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_uniprotIDs,delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id','id_hetionet', 'resource'])

'''
load all reactome uniprotIDs ReferenceEntity and check if they are in hetionet or not
'''

def load_reactome_referenceEntity_in():
    global highest_identifier
    query = '''MATCH (n:PhysicalEntity_reactome)-[r:referenceEntity]-(a:ReferenceEntity_reactome) WHERE a.databaseName = 'UniProt' RETURN a.identifier, a.name, n.name'''
    # p = (n:PhysicalEntity) - [r:referenceEntity]-(a:ReferenceEntity) Where a.databaseName = 'UniProt' RETURN n, r, a Limit 25
    results = graph_database.run(query)
    set_pairs = set()
    counter_map_with_id = 0
    for identifier, names, physicalEntityNames in results:
        name = names[0].lower() if names else physicalEntityNames[0].lower()
        if identifier in dict_uniprot_id_to_name:
            if not (identifier, identifier) in set_pairs:
                counter_map_with_id += 1
                #print(identifier)
                resource = dict_uniprot_to_resource[identifier]
                resource.append('Reactome')
                resource = set(resource)
                resource = '|'.join(sorted(resource))
                csv_mapped.writerow([identifier, identifier, resource])
                set_pairs.add((identifier, identifier))
        elif identifier in dict_alternative_id_to_protein_id:
            hetionet_uniprotID = dict_alternative_id_to_protein_id[identifier]
            if not (identifier, hetionet_uniprotID) in set_pairs:
                resource = dict_uniprot_to_resource[hetionet_uniprotID]
                resource.append('Reactome')
                resource = set(resource)
                resource = '|'.join(sorted(resource))
                csv_mapped.writerow([identifier, hetionet_uniprotID, resource])
                set_pairs.add((identifier, hetionet_uniprotID))
        else:
            csv_not_mapped.writerow([identifier, name])

    print('number of mapping with id:' + str(counter_map_with_id))

'''
generate connection between mapping ReferenceEntity of reactome and Protein hetionet and generate new edges
'''


def create_cypher_file():
    cypher_file = open('output/cypher_mapping2.cypher','a', encoding="utf-8")
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/uniprotIDs/mapped_uniprotIDs.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Protein{identifier:line.id_hetionet}),(c:ReferenceEntity_reactome{identifier:line.id}) CREATE (d)-[: equal_to_reactome_uniprot]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query= query %(path_of_directory)
    cypher_file.write(query)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')

    print (datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print (datetime.datetime.now())
    print('Load all uniprotIDs from hetionet Protein into a dictionary')

    load_hetionet_uniprotIDs_in()


    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print (datetime.datetime.now())
    print('Load all reactome uniprotIDs from ReferenceEntity from neo4j into a dictionary')

    load_reactome_referenceEntity_in()


    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print (datetime.datetime.now())
    print('Integrate new edges to reactome ')

    create_cypher_file()

    print(
        '###...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...*...###')

    print (datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
