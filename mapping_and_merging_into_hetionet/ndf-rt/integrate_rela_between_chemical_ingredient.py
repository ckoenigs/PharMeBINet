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


# open cypher file
cypher_file = open('relationships/cypher.cypher', 'a', encoding='utf-8')


def write_files(label, direction_1, direction_2, rela_name):
    '''
    generate csv file and generate query for cypher file
    :param direction_1: string
    :param direction_2: string
    :param rela_name: string
    :return:  csv writer
    '''
    # give the rela the right abbreviation
    if label == 'Chemical':
        rela_name = rela_name % ('CH')
    else:
        rela_name = rela_name % ('PC')

    # file from relationship between gene and variant
    file_name = 'chemical_ingredient/rela_' + rela_name + '_' + label + '.tsv'
    file_rela = open(file_name, 'w', encoding='utf-8')
    csv_rela = csv.writer(file_rela, delimiter='\t')
    header_rela = ['chemical_id', 'ingredient_chemical_id', 'source']
    csv_rela.writerow(header_rela)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
            Match (c:%s{identifier:line.chemical_id}), (p:Chemical{identifier:line.ingredient_chemical_id}) Merge (c)%s[r:%s]%s(p) On Create Set r.source=line.source, r.resource=['NDF-RT'], r.url='http://purl.bioontology.org/ontology/NDFRT/'+line.ingredient_chemical_id , r.license='UMLS license, available at https://uts.nlm.nih.gov/license.html', r.unbiased=false, r.ndf_rt='yes' On Match Set r.resource=r.resource+'NDF-RT' , r.ndf_rt='yes';\n'''
    query = query % (path_of_directory, file_name, label, direction_1, rela_name, direction_2)
    cypher_file.write(query)

    return csv_rela


# dictionary_mapping_pairs
dict_mapping_pairs = {}

# dictionary relationship to csv
dict_rela_to_csv = {}

# dictionary rela name in ndf-rt to information needed
# has_active_metabolites
dict_rela_name_to_other_information = {
    'has': ['-', '->', 'HAS_INGREDIENT_%shiCH'],
    'CI': ['-', '->', 'CONTRAINDICATES_%scCH'],
    'has_Chemical_Structure': ['-', '->', 'HAS_CHEMICAL_STRUCTURE_%shcsCH'],
    'has_active_metabolites': ['-', '->', 'HAS_ACTIVE_METABOLITE_%shamCH']
}


def load_connections(label):
    '''
    Load all connection between chemical and pharmacological class from ndf-rt
    :return:
    '''
    query = "Match (c:%s)--(:NDFRT_DRUG_KIND)-[t]-(:NDFRT_INGREDIENT_KIND)--(d:Chemical) Return c.identifier, type(t), t, d.identifier"
    query = query % (label)
    results = g.run(query)
    for chemical_id, rela_type, rela, ingredient_chemical_id, in results:
        source = rela['source'] if 'source' in rela else ''
        # remove the different suffix
        if rela_type.count('_') == 1:
            rela_type = rela_type.split('_')[0]

        if rela_type in dict_rela_name_to_other_information:
            if (rela_type, label) not in dict_rela_to_csv:
                rela_info = dict_rela_name_to_other_information[rela_type]
                csv_writer = write_files(label, rela_info[0], rela_info[1], rela_info[2])
                dict_rela_to_csv[(rela_type, label)] = csv_writer
                dict_mapping_pairs[(rela_type, label)] = {}
        else:
            print(rela_type)
            continue

        # add only pair which are not already added and do not integrate self-loops
        if chemical_id == ingredient_chemical_id:
            continue
        if (chemical_id, ingredient_chemical_id) in dict_mapping_pairs[(rela_type, label)]:  # or (
            print(dict_mapping_pairs[(rela_type, label)][(chemical_id, ingredient_chemical_id)])
            print(source)
            continue

        dict_mapping_pairs[(rela_type, label)][chemical_id, ingredient_chemical_id] = source
        dict_rela_to_csv[(rela_type, label)].writerow([chemical_id, ingredient_chemical_id, source])


def main():
    print(datetime.datetime.utcnow())
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path NDF-RT rela')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load pairs and generate files')

    for label in ['Chemical', 'PharmacologicClass']:
        load_connections(label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
