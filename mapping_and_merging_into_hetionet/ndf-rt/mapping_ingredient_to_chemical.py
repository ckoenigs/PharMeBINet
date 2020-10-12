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

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = create_connection_to_databases.database_connection_RxNorm()


# dictionary mesh id to chemical ids
dict_mesh_to_chemical_id = {}

# dictionary name to chemical ids
dict_name_to_chemical_id = {}

# dictionary umls id to chemical ids
dict_umls_to_chemical_id = {}

# dictionary rnxnorm id to chemical ids
dict_rnxnorm_to_chemical_id = {}

# dictionary chemical id to resource
dict_chemical_id_to_resource = {}

'''
Load all Chemical from my database  and add them into a dictionary
'''


def load_chemical_from_database_and_add_to_dict():
    query = "MATCH (n:Chemical) RETURN n, labels(n)"
    results = g.run(query)
    for node, labels, in results:
        identifier = node['identifier']
        resource = node['resource']
        dict_chemical_id_to_resource[identifier] = resource

        if 'Compound' not in labels:
            if identifier not in dict_mesh_to_chemical_id:
                dict_mesh_to_chemical_id[identifier] = set()
            dict_mesh_to_chemical_id[identifier].add(identifier)

        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB, STR From MRCONSO Where SAB in ('MSH','DRUGBANK') and CODE= '%s';")
        query = query % (identifier)

        rows_counter = cur.execute(query)
        if rows_counter > 0:
            for (cui, lat, code, sab, umls_name) in cur:
                if cui not in dict_umls_to_chemical_id:
                    dict_umls_to_chemical_id[cui] = set()
                dict_umls_to_chemical_id[cui].add(identifier)

        name = node['name'].lower()
        if name not in dict_name_to_chemical_id:
            dict_name_to_chemical_id[name] = set()
        dict_name_to_chemical_id[name].add(identifier)
        synonyms = node['synonyms'] if 'synonyms' in node else []
        for synonym in synonyms:
            synonym = synonym.lower()
            if synonym not in dict_name_to_chemical_id:
                dict_name_to_chemical_id[synonym] = set()
            dict_name_to_chemical_id[synonym].add(identifier)

        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('RxNorm_Cui:'):
                xref = xref.split(':', 1)[1]
                if xref not in dict_rnxnorm_to_chemical_id:
                    dict_rnxnorm_to_chemical_id[xref] = set()
                dict_rnxnorm_to_chemical_id[xref].add(identifier)


def write_files(path_of_directory):
    # file from relationship between gene and variant
    file_name = 'ingredient/mapping.tsv'
    file_rela = open(file_name, 'w', encoding='utf-8')
    csv_rela = csv.writer(file_rela, delimiter='\t')
    header_rela = ['code', 'chemical_id', 'resource', 'how_mapped']
    csv_rela.writerow(header_rela)

    cypher_file = open('ingredient/cypher.cypher', 'w', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
            Match (n:NDF_RT_INGREDIENT_KIND{code:line.code}), (v:Chemical{identifier:line.chemical_id}) Set v.ndf_rt='yes', v.resource=split(line.resource,'|') Create (v)-[:equal_to_ingredient_ndf_rt{how_mapped:split(line.how_mapped,"|")}]->(n);'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)
    cypher_file.close()

    return csv_rela

# dictionary_mapping_pairs
dict_mapping_pairs={}

def try_to_map(identifier, key, dictionary, how_mapped):
    if key in dictionary:
        for chemical_id in dictionary[key]:
            if not (identifier,chemical_id) in dict_mapping_pairs:
                dict_mapping_pairs[(identifier,chemical_id)]=set()
            dict_mapping_pairs[(identifier,chemical_id)].add(how_mapped)



def load_all_ingredients_and_map():
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH (n:NDF_RT_INGREDIENT_KIND) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['code']
        name = node['name'].split(' [Chemical/Ingredient')[0].lower()
        try_to_map(identifier, name, dict_name_to_chemical_id, 'name_mapping')

        for property in node['properties']:
            # if property.startswith('UMLS_CUI:'):
            #     cui = property.split(':')[1]
            #     try_to_map(identifier, cui, dict_umls_to_chemical_id, 'umls_mapping')
            if property.startswith('MeSH_CUI:') or property.startswith('MeSH_DUI:') :
                cui = property.split(':')[1]
                try_to_map(identifier, cui, dict_mesh_to_chemical_id, 'mesh_mapping')

            elif property.startswith('RxNorm_CUI:'):
                cui = property.split(':')[1]
                try_to_map(identifier, cui, dict_rnxnorm_to_chemical_id, 'rxcui_mapping')

def write_mapping_into_file(csv_map):
    for (identifier, chemical_id), how_mapped in dict_mapping_pairs.items():
        resource = set(dict_chemical_id_to_resource[chemical_id])
        resource.add('NDR-RT')
        csv_map.writerow([identifier, chemical_id, '|'.join(sorted(resource)), '|'.join(how_mapped)])


def main():
    print(datetime.datetime.utcnow())

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path NDF-RT ingredient')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate files')

    csv_writer = write_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all Chemicals from database')

    load_chemical_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all ingredients from database')

    load_all_ingredients_and_map()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Write mapping into file')

    write_mapping_into_file(csv_writer)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
