import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary pair to relatype
dict_pair_to_rela_type = {}

# dictionary_rela type to csv file
dict_rela_type_to_csv_file = {}

# dictionary rela type to rela label
dict_type_to_label = {
    'may_treat': 'TREATS_CtD',
    'may_prevent': 'PREVENTS_CpD',
    'CI_with': 'CONTRAINDICATES_CcD',
    'induces': 'INDUCES_CiD',
    'may_diagnose': 'MAY_DIAGNOSES_CmdD'
}

# cypher file
cypher_file = open('relationships/cypher.cypher', 'w', encoding='utf-8')

'''
load all connection types from ndf-rt between drug and disease
and integrate them in different csv files
'''


def integrate_connection_into_hetionet(label):
    # count of integrated contra-indication relationship
    count_contra_indicate = 0
    # count of integrated induces relationships
    count_induces = 0
    # count all mapped codes
    count_code = 0

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' Match (a:%s{identifier:line.chemical_id}), (b:Disease{identifier:line.disease_id})  '''


    counter_contraindication_double = 0
    counter_induces_double = 0

    query = '''MATCH (a:%s)--(n:NDFRT_DRUG_KIND)-[r]-(:NDFRT_DISEASE_KIND)--(b:Disease) RETURN Distinct a.identifier, type(r), r.source, b.identifier'''
    query =query %(label)
    print(query)
    result = g.run(query)

    # rela to list of pairs
    dict_rela_to_pairs={}

    for chemical_id, rela_type,rela_source, disease_id, in result:
        if (rela_type,label) not in dict_rela_type_to_csv_file:
            dict_rela_to_pairs[rela_type]=[]
            file_name='rela_' + rela_type +'_' + label+'.tsv'
            file = open('relationships/'+file_name, 'w', encoding='utf-8')
            csv_writer = csv.writer(file, delimiter='\t')
            csv_writer.writerow(['chemical_id', 'disease_id', 'source'])
            dict_rela_type_to_csv_file[(rela_type,label)] = csv_writer
            query_check = 'Match p=(:%s)-[:%s]-(:Disease) Return p Limit 1' % (label,dict_type_to_label[rela_type])
            results = g.run(query_check)
            result = results.evaluate()
            if result:
                query = query_start + 'Merge (a)-[r:%s]->(b) On Create Set r.source=line.source, r.resource=["NDF-RT"], r.ndf_rt="yes", r.unbiased=false, r.license="UMLS license, available at https://uts.nlm.nih.gov/license.html" On Match Set r.resource=r.resource+"NDF-RT", r.ndf_rt="yes";\n '
            else:
                query = query_start + "Create (a)-[r:%s{source:line.source, resource:['NDF-RT'], ndf_rt:'yes', unbiased:false, license:'UMLS license, available at https://uts.nlm.nih.gov/license.html'}]->(b);\n"
            query = query % ('relationships/'+file_name, label ,dict_type_to_label[rela_type])
            cypher_file.write(query)

        count_code += 1
        source= 'NDF-RT' if rela_source=='NDFRT' else rela_source+' via NDF-RT'
        if not (chemical_id,disease_id) in dict_rela_to_pairs[rela_type]:
            dict_rela_type_to_csv_file[(rela_type,label)].writerow([chemical_id, disease_id, source])
            dict_rela_to_pairs[rela_type].append((chemical_id,disease_id))
        else:
            sys.exit('multiple edges for the same pair!')

    print('number of contra indications connections:' + str(count_contra_indicate))
    print('number of induces connections:' + str(count_induces))
    print('double of contra indicates connection:' + str(counter_contraindication_double))
    print('double of induces connection:' + str(counter_induces_double))
    print(dict_rela_type_to_csv_file.keys())


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in chemical from hetionet')

    for label in ['Chemical', 'PharmacologicClass']:

        integrate_connection_into_hetionet(label)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
