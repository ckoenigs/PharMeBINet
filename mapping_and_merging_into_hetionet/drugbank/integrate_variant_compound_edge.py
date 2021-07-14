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



def generate_files(path_of_directory):
    """
    generate cypher file and csv file
    :return: csv file
    """
    # file from relationship between gene and variant
    file_name = 'compound_to_variant'
    file = open('gene_variant/' + file_name + '.tsv', 'w', encoding='utf-8')
    header = ['variant_id', 'compound_id', "type", "description", "pubmed_ids", "license"]
    csv_mapping = csv.DictWriter(file, delimiter='\t', fieldnames=header)
    csv_mapping.writeheader()

    cypher_file = open('output/cypher_rela.cypher', 'a', encoding='utf-8')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/drugbank/gene_variant/%s.tsv" As line FIELDTERMINATOR '\\t' 
        Match (n:Compound{identifier:line.compound_id}), (v:Variant{identifier:line.variant_id}) MERGE (v)-[r:COMBINATION_CAUSES_ADR_VccaCH]->(n) On Create set r.type=line.type, r.license=line.license, r.description=line.description, r.pubMed_ids=split(line.pubmed_ids,"|"), r.drugbank="yes", r.resource=["DrugBank"], r.url="https://go.drugbank.com/drugs/"+line.compound_id On Match Set r.drugbank="yes", r.resource=r.resource+"DrugBank" ;\n'''
    query = query % (path_of_directory, file_name)
    cypher_file.write(query)

    return csv_mapping


'''
Load all variation sort the ids into the right csv, generate the queries, and add rela to the rela csv
'''


def load_all_pair_and_prepare_for_dictionary(csv_mapping):
    query = "MATCH (v:Variant)--(n:Mutated_protein_gene_DrugBank)-[r]-(:Compound_DrugBank)--(c:Compound) RETURN v.identifier, r, c.identifier"
    results = g.run(query)
    
    dict_drug_variant_pair_to_rela={}
    for variant_id, rela, drug_id, in results:
        if not (variant_id,drug_id) in dict_drug_variant_pair_to_rela:
            dict_drug_variant_pair_to_rela[(variant_id, drug_id)]={}
        for key, value in dict(rela).items():
            if key not in dict_drug_variant_pair_to_rela[(variant_id,drug_id)]:
                dict_drug_variant_pair_to_rela[(variant_id,drug_id)][key]=set()
            dict_drug_variant_pair_to_rela[(variant_id, drug_id)][key].add(value)

    for (variant_id, drug_id), dict_rela in dict_drug_variant_pair_to_rela.items():
        dict_all_infos={
            'variant_id':variant_id,
            'compound_id':drug_id
        }
        for key, value in dict_rela.items():
            if len(value)>1:
                print('multi')
                print(key)
                print(value)
            if key=='pubmed_id':
                dict_all_infos['pubmed_ids']='|'.join(value)
            elif key=='type':
                dict_all_infos['type'] = '; '.join(value)
            elif key=='license':
                dict_all_infos[key] = license
            else:
                dict_all_infos[key] = ' '.join(value)
        csv_mapping.writerow(dict_all_infos)



def main():
    print(datetime.datetime.utcnow())
    global path_of_directory, license
    if len(sys.argv) < 3:
        sys.exit('need path to directory gene variant')

    path_of_directory = sys.argv[1]
    license = sys.argv[2]
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate cypher and csv file')

    csv_mapping = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all variation from database')

    load_all_pair_and_prepare_for_dictionary(csv_mapping)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
