import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connetion_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary of all diseases in pharmebinet to resource
dict_diseases_in_resource = {}

# dictionary doid to mondo ids
dict_doid_to_mondo_ids={}
# dictionary doid to mondo ids
dict_name_to_mondo_ids={}


def load_all_disease_in_dictionary():
    query = '''Match (n:Disease) RETURN n.identifier, n.name, n.xrefs, n.resource '''
    results = g.run(query)
    for identifier, name, xrefs, resource, in results:
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_mondo_ids,name.lower(),identifier)
        if xrefs:
            for xref in xrefs:
                if xref.startswith('DOID:'):
                    pharmebinetutils.add_entry_to_dict_to_set(dict_doid_to_mondo_ids, xref, identifier)
        dict_diseases_in_resource[identifier] = resource

    print('size of diseases before the rest of disease ontology was add: ' + str(len(dict_diseases_in_resource)))

# tsv file for DOID which are already in pharmebinet
file_included = open('output/mapped.tsv', 'w', encoding='utf-8')
csv_writer_included = csv.writer(file_included, delimiter='\t')
csv_writer_included.writerow(['disease_id','mondo_id','resource','how_mapped'])

def generate_cypher_file():
    """
    Prepare cypher query
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

    query_set = ' Match (n:Disease{identifier:line.mondo_id}), (b:DISEASES_Disease{id:line.disease_id}) Set  n.disease="yes", n.resource=split(line.resource,"|") Create (n)-[:equal_to {how_mapped:line.how_mapped}]->(b)'
    print(query_set)
    query_set = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/diseases/output/mapped.tsv',
                                                  query_set)
    cypher_file.write(query_set)

    cypher_file.close()


def map_diseases_disease():
    query='MATCH (n:DISEASES_Disease) RETURN n.id, n.name'
    counter=0
    counter_not_mapped=0
    for identifier, name, in g.run(query):
        counter+=1
        is_mapped=False

        # wrong name and doid by DOID:0050156
        if name and identifier !='DOID:0050156':
            name=name.lower()
            if name in dict_name_to_mondo_ids:
                is_mapped=True
                for mondo_id in dict_name_to_mondo_ids[name]:
                    csv_writer_included.writerow([identifier,mondo_id,pharmebinetutils.resource_add_and_prepare(dict_diseases_in_resource[mondo_id], 'DISEASES'),'name'])

        if is_mapped:
            continue

        if identifier in dict_doid_to_mondo_ids:
            is_mapped=True
            for mondo_id in dict_doid_to_mondo_ids[identifier]:
                csv_writer_included.writerow([identifier,mondo_id,pharmebinetutils.resource_add_and_prepare(dict_diseases_in_resource[mondo_id], 'DISEASES'),'doid'])

        if is_mapped:
            continue

        counter_not_mapped+=1

    print('number of all diseases', counter)
    print('number of not mapped',counter_not_mapped)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('generate cypher file')

    generate_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all pharmebinet diseases in dictionary')

    load_all_disease_in_dictionary()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('load all disease ontology diseases in dictionary')

    map_diseases_disease()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
