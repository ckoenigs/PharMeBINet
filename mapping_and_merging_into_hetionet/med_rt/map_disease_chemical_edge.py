import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary pair to relatype
dict_pair_to_rela_type = {}

# dictionary_rela type to tsv file
dict_rela_type_to_tsv_file = {}

# dictionary rela type to rela label
dict_type_to_label = {
    'may_treat': 'TREATS_%stD',
    'may_prevent': 'PREVENTS_%spD',
    'CI_with': 'CONTRAINDICATES_%scD',
    'induces': 'INDUCES_%siD',
    'may_diagnose': 'MAY_DIAGNOSES_%smdD'
}

# cypher file
cypher_file = open('output/cypher_edge.cypher', 'a', encoding='utf-8')

'''
load all connection types from ndf-rt between drug and disease
and integrate them in different tsv files
'''


def integrate_connection_into_pharmebinet(labels):
    # count all mapped codes
    count_code = 0

    query_start = ''' Match (a:%s{identifier:line.chemical_id}), (b:Disease{identifier:line.disease_id})  '''

    query = '''MATCH (a:%s)--(n:%s)-[r]-(:Disease_Finding_MEDRT)--(b:Disease) RETURN Distinct a.identifier, type(r), r.qualifier, b.identifier'''
    query = query % labels
    label = labels[0]
    result = g.run(query)

    # rela to list of pairs
    dict_rela_to_pairs = {}

    for record in result:
        [chemical_id, rela_type, rela_source, disease_id] = record.values()
        if (label, rela_type) not in dict_rela_type_to_tsv_file:
            dict_rela_to_pairs[(label, rela_type)] = {}
            file_name = 'rela_' + rela_type + '_' + label + '.tsv'
            file = open('chemical_edge/' + file_name, 'w', encoding='utf-8')
            letter = pharmebinetutils.dictionary_label_to_abbreviation[label]
            csv_writer = csv.writer(file, delimiter='\t')
            csv_writer.writerow(['chemical_id', 'disease_id', 'source'])
            dict_rela_type_to_tsv_file[(label, rela_type)] = csv_writer
            query_check = 'Match p=(:%s)-[:%s]-(:Disease) Return p Limit 1' % (label, dict_type_to_label[rela_type])

            query_check = query_check % letter
            results = g.run(query_check)
            result = results.single()
            if result:
                query = query_start + 'Merge (a)-[r:%s]->(b) On Create Set r.source=line.source, r.resource=["MED-RT"], r.med_rt="yes",  r.license="UMLS license, available at https://uts.nlm.nih.gov/license.html" On Match Set r.resource=r.resource+"MED-RT", r.med_rt="yes" '
            else:
                query = query_start + "Create (a)-[r:%s{source:line.source, resource:['MED-RT'], med_rt:'yes', license:'UMLS license, available at https://uts.nlm.nih.gov/license.html'}]->(b)"
            query = query % (label, dict_type_to_label[rela_type])
            query = query % letter

            query = pharmebinetutils.get_query_import(path_of_directory,
                                                      f'mapping_and_merging_into_hetionet/med_rt/chemical_edge/{file_name}',
                                                      query)
            cypher_file.write(query)

        count_code += 1
        source = 'MED-RT' if rela_source.split(':')[-1] == 'MEDRT' else rela_source.split(':')[-1] + ' via MED-RT'
        if not (chemical_id, disease_id) in dict_rela_to_pairs[(label, rela_type)]:

            dict_rela_to_pairs[(label, rela_type)][(chemical_id, disease_id)] = set([source])
        else:
            print(chemical_id, disease_id)
            dict_rela_to_pairs[(label, rela_type)][(chemical_id, disease_id)].add(source)
            print(rela_type, label)
            print('multiple edges for the same pair!')

    for (label, rela_type), dict_pair_to_sources in dict_rela_to_pairs.items():
        for (chemical_id, disease_id), sources in dict_pair_to_sources.items():
            dict_rela_type_to_tsv_file[(label, rela_type)].writerow([chemical_id, disease_id, ', '.join(sources)])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '#############################################################################################################')

    print(datetime.datetime.now())
    print('Load in chemical from pharmebinet')

    for labels in [('Chemical', 'Chemical_Ingredient_MEDRT'),
                   ('PharmacologicClass', 'FDA_Established_Pharmacologic_Classes_MEDRT')]:
        integrate_connection_into_pharmebinet(labels)

    driver.close()

    print(
        '#############################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
