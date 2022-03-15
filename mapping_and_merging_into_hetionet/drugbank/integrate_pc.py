import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

# dictionary name to pc ids
dict_name_to_pc_ids={}

# dictionary_mesh_id_to_pc_ids
dict_mesh_id_to_pc_ids={}

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
        if not name in dict_name_to_pc_ids:
            dict_name_to_pc_ids[name]=set()
        dict_name_to_pc_ids[name].add(identifier)

        xrefs= node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('MeSH'):
                mesh_id=xref.split(':')[1]
                if not mesh_id in dict_mesh_id_to_pc_ids:
                    dict_mesh_id_to_pc_ids[mesh_id]=set()
                dict_mesh_id_to_pc_ids[mesh_id].add(identifier)


def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: csv writer
    """
    # file from relationship between gene and variant
    file_name = 'compound_to_variant'
    file = open('gene_variant/' + file_name + '.tsv', 'w', encoding='utf-8')
    header = ['variant_id', 'compound_id', "type", "description", "pubmed_ids", "license"]
    csv_mapping = csv.DictWriter(file, delimiter='\t', fieldnames=header)
    csv_mapping.writeheader()

    cypher_file = open('output/cypher_rela.cypher', 'a', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/gene_variant/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:Compound{identifier:line.compound_id}), (v:Variant{identifier:line.variant_id}) MERGE (v)-[r:COMBINATION_CAUSES_ADR_VccaC]->(n) On Create set r.type=line.type, r.license=line.license, r.description=line.description, r.pubmed_id=split(line.pubMed_ids,"|"), r.drugbank="yes", r.resource=["DrugBank"], r.url="https://go.drugbank.com/drugs/"+line.compound_id On Match Set r.drugbank="yes", r.resource=r.resource+"DrugBank" ;\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    return csv_mapping

# dictionary_pc_db_to_pc_id
dict_pc_db_to_pc_id={}


def load_all_drugbank_pc_and_map():
    query = "MATCH (v:PharmacologicClass_DrugBank) RETURN v"
    results = g.run(query)

    # counter
    counter_mapped=0
    counter_not_mapped=0

    for node, in results:
        identifier=node['identifier']
        name=node['name'].lower()
        mesh_id=node['mesh_id']
        found_mapping=False
        if mesh_id in dict_mesh_id_to_pc_ids:
            found_mapping=True
            for pc_id in dict_mesh_id_to_pc_ids[mesh_id]:
                if (identifier,pc_id) not in dict_pc_db_to_pc_id:
                    dict_pc_db_to_pc_id[(identifier,pc_id)]='mesh_mapped'
                else:
                    print('multy mapping with mesh')
        if not found_mapping:
            if name in dict_name_to_pc_ids:
                found_mapping = True
                for pc_id in dict_name_to_pc_ids[name]:
                    if (identifier, pc_id) not in dict_pc_db_to_pc_id:
                        dict_pc_db_to_pc_id[(identifier, pc_id)] = 'name_mapped'
                    else:
                        print('multy mapping with name')
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
        sys.exit('need path anf license pc drugbank')

    path_of_directory = sys.argv[1]
    license = sys.argv[2]
    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pc from neo4j')

    load_pc_from_database()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')

    # csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load pc from drugbank and map')

    load_all_drugbank_pc_and_map()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
