import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    # create a connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary name to pharmacologic class id
dict_name_to_pharmacologic_class_id = {}

# dictionary pharmacologic class id to resource
dict_pharmacologic_class_id_to_resource = {}


def load_pharmacologic_class_from_database_and_add_to_dict():
    """
    Load all PharmacologicClass from my database  and add them into a dictionary
    :return:
    """
    query = "MATCH (n:PharmacologicClass) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        resource = node['resource']
        name = node['name'].lower()
        if name not in dict_name_to_pharmacologic_class_id:
            dict_name_to_pharmacologic_class_id[name] = set()
        dict_name_to_pharmacologic_class_id[name].add(identifier)
        dict_pharmacologic_class_id_to_resource[identifier] = set(resource)


# dictionary atc codes to compound ids
dict_atc_code_to_compound_ids = {}


def load_compounds_from_database_and_add_to_dict():
    """
    Load all chemical with atc codes into a dictionary
    :return:
    """
    query = "MATCH (n:Compound) Where n.atc_codes is not NULL RETURN n.identifier, n.atc_codes"
    results = g.run(query)
    for record in results:
        [identifier, atc_codes] = record.values()
        for atc_code in atc_codes:
            pharmebinetutils.add_entry_to_dict_to_set(dict_atc_code_to_compound_ids, atc_code, identifier)


# open cypher file
cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')


def write_files(path_of_directory):
    """
    Prepare the different TSV files for mapping and new nodes. Additionally, prepare the different cypher queries to
    integrate the information PharMeBINet. Also, queries are prepared to generate edges  between the nodes.
    :param path_of_directory:
    :return:
    """
    # file from relationship between gene and variant
    file_name_mapped = 'output/mapping_compound.tsv'
    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_mapped = csv.writer(file_mapped, delimiter='\t')
    header_mapped = ['compound_id', 'id']
    csv_mapped.writerow(header_mapped)

    file_name_mapped_pc = 'output/mapping_pc.tsv'
    file_mapped_pc = open(file_name_mapped_pc, 'w', encoding='utf-8')
    csv_mapped_pc = csv.writer(file_mapped_pc, delimiter='\t')
    header_mapped = ['pc_id', 'id', 'resource']
    csv_mapped_pc.writerow(header_mapped)

    file_name_new = 'output/new_pc.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header_new = ['id']
    csv_new.writerow(header_new)

    query = '''Match (n:atc_kegg{identifier:line.id}), (v:PharmacologicClass{identifier:line.pc_id}) Set v.atc_codes=[line.id], v.resource=split(line.resource,"|"), v.kegg="yes" Create (v)-[:equal_to_atc]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/atc/{file_name_mapped_pc}',
                                              query)
    cypher_file.write(query)

    query = '''Match (n:atc_kegg{identifier:line.id}) Create (v:PharmacologicClass{identifier:line.id, kegg:'yes', resource:['KEGG'], source:'ATC from KEGG', url:'http://identifiers.org/atc:'+line.id, name:n.name, license:"Use of all or parts of the material requires reference to the WHO Collaborating Centre for Drug Statistics Methodology. Copying and distribution for commercial purposes is not allowed. Changing or manipulating the material is not allowed.", class_type:["ATC code"], atc_codes:[line.id]}) Create (v)-[:equal_to_atc]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/atc/{file_name_new}',
                                              query)
    cypher_file.write(query)

    list_of_labels = ['PharmacologicClass']

    for [label_1, label_2] in [[x, y] for x in list_of_labels for y in list_of_labels]:
        query = '''MATCH p=(n:%s)--(:atc_kegg)-[]->(a:atc_kegg)--(b:%s) Merge (n)-[r:BELONGS_TO_%sbt%s]->(b) On Create Set r.source='ATC from KEGG', r.url="http://identifiers.org/atc:"+a.identifier , r.resource=['KEGG'], r.kegg='yes', r.license="Use of all or parts of the material requires reference to the WHO Collaborating Centre for Drug Statistics Methodology. Copying and distribution for commercial purposes is not allowed. Changing or manipulating the material is not allowed.";\n'''
        query = query % (
            label_1, label_2, pharmebinetutils.dictionary_label_to_abbreviation[label_1],
            pharmebinetutils.dictionary_label_to_abbreviation[label_2])
        cypher_file.write(query)

    query = f'''Match (n:PharmacologicClass{{identifier:line.id}}), (v:Compound{{identifier:line.compound_id}}) Create (v)-[:BELONGS_TO_{pharmebinetutils.dictionary_label_to_abbreviation['Chemical']}bt{pharmebinetutils.dictionary_label_to_abbreviation['PharmacologicClass']}{{source:'ATC from KEGG', url:"http://identifiers.org/atc:"+n.id , resource:['KEGG'], kegg:'yes', license:"Use of all or parts of the material requires reference to the WHO Collaborating Centre for Drug Statistics Methodology. Copying and distribution for commercial purposes is not allowed. Changing or manipulating the material is not allowed."}}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/atc/{file_name_mapped}',
                                              query)
    cypher_file.write(query)

    return csv_mapped, csv_new, csv_mapped_pc


# dictionary mapped pc id to atc codes
dict_pc_id_to_atc_codes = {}

# check that each pair exists only one time
set_of_rela_pairs = set()
dict_atc_to_drug_ids = {}


def load_all_label_and_map(csv_map_drug, csv_new):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH (n:atc_kegg) RETURN n"
    results = g.run(query)

    # counter
    counter_mapped_to_compound = 0
    counter_mapped_to_pc = 0
    counter_new = 0
    for node, in results:
        identifier = node['identifier']
        name = node['name'].lower() if 'name' in node else ''

        if name in dict_name_to_pharmacologic_class_id:
            counter_mapped_to_pc += 1
            for pc_id in dict_name_to_pharmacologic_class_id[name]:
                if pc_id not in dict_pc_id_to_atc_codes:
                    dict_pc_id_to_atc_codes[pc_id] = set()
                dict_pc_id_to_atc_codes[pc_id].add(identifier)
            continue
        counter_new += 1
        csv_new.writerow([identifier])
        check_if_id_mapped_to_compound(identifier, csv_map_drug, identifier)

    print('number of mapped to pc:', counter_mapped_to_pc)
    print('number of new:', counter_new)


def check_if_id_mapped_to_compound(atc_id, csv_map_drug, pc_id):
    """
    Get an atc id and check if this is in the compounds and if so write into tsv file.
    :param atc_id:
    :param csv_map_drug:
    :param pc_id:
    :return:
    """
    if atc_id in dict_atc_code_to_compound_ids:
        for drug_id in dict_atc_code_to_compound_ids[atc_id]:
            csv_map_drug.writerow([drug_id, pc_id])


def to_avoid_multiple_mapping(csv_mapped_pc, csv_new, csv_map_drug):
    """
    go through all name mapped
    :return:
    """
    for pc_id, set_of_atcs in dict_pc_id_to_atc_codes.items():
        resource = pharmebinetutils.resource_add_and_prepare(dict_pharmacologic_class_id_to_resource[pc_id], 'KEGG')
        if len(set_of_atcs) == 1:
            atc_id = set_of_atcs.pop()
            csv_mapped_pc.writerow([pc_id, atc_id, resource])
            check_if_id_mapped_to_compound(atc_id, csv_map_drug, pc_id)
        else:
            longest_one = max(set_of_atcs, key=len)
            csv_mapped_pc.writerow([pc_id, longest_one, resource])
            check_if_id_mapped_to_compound(longest_one, csv_map_drug, pc_id)
            for atc in set_of_atcs:
                if atc != longest_one:
                    csv_new.writerow([atc])
                    check_if_id_mapped_to_compound(atc_id, csv_map_drug, atc)


def main():
    print(datetime.datetime.now())

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path atc ')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Pharmacologic classes from database')

    load_pharmacologic_class_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all compounds from database')

    load_compounds_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate files')

    csv_drug_connection, csv_new, csv_mapped_pc = write_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all label from database')

    load_all_label_and_map(csv_drug_connection, csv_new)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('map only to one for pc')

    to_avoid_multiple_mapping(csv_mapped_pc, csv_new, csv_drug_connection)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
