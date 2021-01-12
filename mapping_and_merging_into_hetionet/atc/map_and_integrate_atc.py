import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j_and_mysql():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary name to pharmacologic class id
dict_name_to_pharmacologic_class_id = {}

# dictionary pharmacologic class id to resource
dict_pharmacologic_class_id_to_resource = {}

'''
Load all PharmacologicClass from my database  and add them into a dictionary
'''


def load_pharmacologic_class_from_database_and_add_to_dict():
    query = "MATCH (n:PharmacologicClass) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']
        resource = node['resource']
        name = node['name'].lower()
        if name not in dict_name_to_pharmacologic_class_id:
            dict_name_to_pharmacologic_class_id[name]=set()
        dict_name_to_pharmacologic_class_id[name].add(identifier)
        dict_pharmacologic_class_id_to_resource[identifier] = set(resource)

# dictionary atc codes to compound ids
dict_atc_code_to_compound_ids = {}

def load_compounds_from_database_and_add_to_dict():
    """
    Load all drugbank with atc codes into a dictionary
    :return:
    """
    query = "MATCH (n:Compound) Where exists(n.atc_codes) RETURN n.identifier, n.atc_codes"
    results = g.run(query)
    for identifier, atc_codes, in results:
        for atc_code in atc_codes:
            if atc_code not in dict_atc_code_to_compound_ids:
                dict_atc_code_to_compound_ids[atc_code]=set()
            dict_atc_code_to_compound_ids[atc_code].add(identifier)


cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')


def write_files(path_of_directory):
    # file from relationship between gene and variant
    file_name_mapped = 'output/mapping_compound.tsv'
    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_mapped = csv.writer(file_mapped, delimiter='\t')
    header_mapped = ['compound_id', 'id']
    csv_mapped.writerow(header_mapped)

    file_name_mapped_pc = 'output/mapping_pc.tsv'
    file_mapped_pc = open(file_name_mapped_pc, 'w', encoding='utf-8')
    csv_mapped_pc = csv.writer(file_mapped_pc, delimiter='\t')
    header_mapped = ['pc_id', 'id']
    csv_mapped_pc.writerow(header_mapped)

    file_name_new = 'output/new_pc.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header_new = [ 'id']
    csv_new.writerow(header_new)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/atc/%s" As line FIELDTERMINATOR '\\t' 
            Match (n:atc{identifier:line.id}), (v:Compound{identifier:line.compound_id}) Create (v)-[:equal_to_atc]->(n);\n'''
    query = query % (path_of_directory, file_name_mapped)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/atc/%s" As line FIELDTERMINATOR '\\t' 
                    Match  (v:PharmacologicClass{identifier:line.pc_id}) Set v.atc_codes=[];\n'''
    query = query % (path_of_directory, file_name_mapped_pc)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/atc/%s" As line FIELDTERMINATOR '\\t' 
                Match (n:atc{identifier:line.id}), (v:PharmacologicClass{identifier:line.pc_id}) Set v.atc_codes=v.atc_codes+line.id Create (v)-[:equal_to_atc]->(n);\n'''
    query = query % (path_of_directory, file_name_mapped_pc)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/atc/%s" As line FIELDTERMINATOR '\\t' 
                Match (n:atc{identifier:line.id}) Create (v:PharmacologicClass{identifier:line.id, drugbank:'yes', resource:['DrugBank'], source:'ATC from DrugBankT', url:'http://identifiers.org/atc:'+line.id, name:n.name, license:'', class_type:"ATC code", atc_codes:[line.id]}) Create (v)-[:equal_to_atc]->(n);\n'''
    query = query % (path_of_directory, file_name_new)
    cypher_file.write(query)

    list_of_labels=['Compound','PharmacologicClass']

    for [label_1, label_2] in [[x,y] for x in list_of_labels for y in list_of_labels]:
        query= "MATCH p=(n:%s)--(:atc)-[]->(:atc)--(b:%s) Where (n:Compound or n:PharmacologicClass) and (b:Compound or b:PharmacologicClass) Create (n)-[:BELONGS_TO_%sbt%s{source:'ATC from DrugBank', resource:['DrugBank'], drugbank:'yes'}]->(b);\n"
        query=query %( label_1,label_2, label_1[0], label_2[0])
        cypher_file.write(query)
    return csv_mapped, csv_new, csv_mapped_pc


def load_all_label_and_map( csv_map_drug, csv_new, csv_mapped_pc):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH (n:atc) RETURN n"
    results = g.run(query)

    # counter
    counter_mapped_to_compound=0
    counter_mapped_to_pc=0
    counter_new=0
    for node, in results:
        identifier = node['identifier']
        name = node['name'].lower() if 'name' in node else ''

        found_mapping = False
        # map to compound
        if identifier in dict_atc_code_to_compound_ids:
            counter_mapped_to_compound+=1
            for compound_id in dict_atc_code_to_compound_ids[identifier]:
                csv_map_drug.writerow([compound_id, identifier])
            continue
        if name in dict_name_to_pharmacologic_class_id:
            counter_mapped_to_pc+=1
            for pc_id in dict_name_to_pharmacologic_class_id[name]:
                csv_mapped_pc.writerow([pc_id, identifier])
            continue
        counter_new+=1
        csv_new.writerow([identifier])

    print('number of mapped to drug:',counter_mapped_to_compound)
    print('number of mapped to pc:', counter_mapped_to_pc)
    print('number of new:',counter_new)



def main():
    print(datetime.datetime.utcnow())

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path NDF-RT ')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all Pharmacologic classes from database')

    load_pharmacologic_class_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all compounds from database')

    load_compounds_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate files')

    csv_mapper, csv_new, csv_mapped_pc = write_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all label from database')

    load_all_label_and_map(csv_mapper, csv_new, csv_mapped_pc)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
