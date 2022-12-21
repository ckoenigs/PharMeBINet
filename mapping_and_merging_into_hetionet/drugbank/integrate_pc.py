import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j_and_mysql():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()
    
    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

# dictionary name to pc ids
dict_name_to_pc_ids={}

# dictionary_mesh_id_to_pc_ids
dict_mesh_id_to_pc_ids={}

# dictionary_umls_id_to_pc_ids
dict_umls_cui_to_pc_ids={}

def load_pc_from_database():
    """
    Load all pc into different mapping dictionaries
    :return:
    """
    query='''Match (n:PharmacologicClass) Return n'''
    results=g.run(query)
    for node, in results:
        identifier= node['identifier']
        name=node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pc_ids, name, identifier)

        synonyms= node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = synonym.lower()
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pc_ids, synonym, identifier)

        xrefs= node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('MeSH'):
                mesh_id=xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_mesh_id_to_pc_ids, mesh_id, identifier)
            elif xref.startswith('UMLS_CUI'):
                umls_cui=xref.split(':')[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_umls_cui_to_pc_ids, umls_cui, identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv writer
    """
    # file from relationship between gene and variant
    file_name = 'pharmacological_class/map_pc'
    file = open( file_name + '.tsv', 'w', encoding='utf-8')
    header = ['pc_id_DB', 'pc_id', "how_mapped"]
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file = open('protein/cypher_protein.cypher', 'a', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/drugbank/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:PharmacologicClass_DrugBank{identifier:line.pc_id_DB}), (v:PharmacologicClass{identifier:line.pc_id}) Create (v)-[r:equal_to_pc_drugbank{how_mapped:line.how_mapped}]->(n)  ;\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)
    cypher_file.close()

    return csv_mapping

# dictionary_pc_db_to_pc_id
dict_pc_db_to_pc_id={}


def load_all_drugbank_pc_and_map(csv_mapping):
    query = "MATCH (v:PharmacologicClass_DrugBank) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped=0
    counter_not_mapped=0

    for node, in results:
        identifier=node['identifier']
        name=node['name'].lower()
        mesh_id=node['mesh_id'] if 'mesh_id' in node else ''
        found_mapping=False
        if mesh_id in dict_mesh_id_to_pc_ids:
            found_mapping=True
            for pc_id in dict_mesh_id_to_pc_ids[mesh_id]:
                if (identifier,pc_id) not in dict_pc_db_to_pc_id:
                    dict_pc_db_to_pc_id[(identifier,pc_id)]='mesh_mapped'
                    csv_mapping.writerow([identifier,pc_id,'mesh_mapped'])
                else:
                    print('multy mapping with mesh')
        if not found_mapping:
            if name in dict_name_to_pc_ids:
                found_mapping = True
                for pc_id in dict_name_to_pc_ids[name]:
                    if (identifier, pc_id) not in dict_pc_db_to_pc_id:
                        dict_pc_db_to_pc_id[(identifier, pc_id)] = 'name_mapped'
                        csv_mapping.writerow([identifier,pc_id,'name_synonyms_mapped'])
                    else:
                        print('multy mapping with name')
        if found_mapping:
            counter_mapped+=1
            continue

        if mesh_id:
            # start = time.time()
            cur = con.cursor()
            query = ("Select CUI From MRCONSO Where STR= '%s';")
            query = query % (name)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (cui ) in cur:
                    if cui in dict_umls_cui_to_pc_ids:
                        found_mapping = True
                        for pc_id in dict_umls_cui_to_pc_ids[cui]:
                            if (identifier, pc_id) not in dict_pc_db_to_pc_id:
                                dict_pc_db_to_pc_id[(identifier, pc_id)] = 'name_umls_mapped'
                                csv_mapping.writerow([identifier, pc_id, 'name_umls_mapped'])
                            else:
                                print('multy mapping with name_umls_mapped')
        if found_mapping:
            counter_mapped+=1
            continue

        # start = time.time()
        cur = con.cursor()
        query = ("Select CUI From MRCONSO Where SAB='MSH' and CODE='%s' ;")
        query = query % (mesh_id)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            for (cui) in cur:
                if cui in dict_umls_cui_to_pc_ids:
                    found_mapping = True
                    for pc_id in dict_umls_cui_to_pc_ids[cui]:
                        if (identifier, pc_id) not in dict_pc_db_to_pc_id:
                            dict_pc_db_to_pc_id[(identifier, pc_id)] = 'mesh_umls_mapped'
                            csv_mapping.writerow([identifier, pc_id, 'mesh_umls_mapped'])
                        else:
                            print('multy mapping with mesh_umls_mapped')

        if found_mapping:
            counter_mapped+=1
        else:
            counter_not_mapped+=1
    print('number of mapped node:',counter_mapped)
    print('number of not mapped node:', counter_not_mapped)

def main():
    print(datetime.datetime.now())
    global path_of_directory, license
    if len(sys.argv) < 3:
        sys.exit('need path and license pc drugbank')

    path_of_directory = sys.argv[1]
    license = sys.argv[2]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pc from neo4j')

    load_pc_from_database()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pc from drugbank and map')

    load_all_drugbank_pc_and_map(csv_mapping)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
