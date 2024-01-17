import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases  # , authenticate
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with all pairs and properties as value
dict_disease_pathway = {}

'''
get all relationships between gene and pathway, take the pharmebinet identifier and gaather all information in a dictionary 
'''


def take_all_relationships_of_gene_disease():
    query = '''MATCH (disease)-[r:associates_DP]->(pathway) RETURN pathway.pharmebinet_id, r, disease.mondos '''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    counter_all = 0
    for record in results:
        [pathway_id, rela, disease_mondos] = record.values()
        counter_all += 1
        rela = dict(rela)
        inferenceGeneSymbol = rela['inferenceGeneSymbol'] if 'inferenceGeneSymbol' in rela else ''
        for mondo in disease_mondos:

            if not (pathway_id, mondo) in dict_disease_pathway:
                dict_disease_pathway[(pathway_id, mondo)] = [inferenceGeneSymbol]

                count_possible_relas += 1
            else:
                count_multiple_pathways += 1
                dict_disease_pathway[(pathway_id, mondo)].append(inferenceGeneSymbol)
        if count_possible_relas % 1000 == 0:
            print(count_possible_relas)

    print(counter_all)
    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))


'''
Generate the tsv and cypher file
'''


def generate_tsv_and_cypher_file():
    # generate cypher file
    cypherfile = open('disease_pathway/cypher.cypher', 'w')

    query = '''Match (n:Pathway{identifier:line.PathwayID}), (b:Disease{identifier:line.DiseaseID}) Merge (b)-[r:ASSOCIATES_DaP]->(n) On Create Set  r.inferenceGeneSymbol=split(line.inferenceGeneSymbol,'|') , r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2024 NC State University. All rights reserved.", r.unbiased=false On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=disease&acc="+line.DiseaseID, r.inferenceGeneSymbol=split(line.inferenceGeneSymbol,'|')  '''

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/disease_pathway/relationships.tsv',
                                              query)
    cypherfile.write(query)

    csvfile = open('disease_pathway/relationships.tsv', 'wb')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['PathwayID', 'DiseaseID', 'inferenceGeneSymbol'])

    for (pathway_id, mondo), inferenceGeneSymbols in dict_disease_pathway.items():
        inferenceGeneSymbol = '|'.join(inferenceGeneSymbols)
        writer.writerow([pathway_id, mondo, inferenceGeneSymbol])


# path to directory
path_of_directory = ''


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
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Take all gene-pathway relationships and generate tsv and cypher file')

    take_all_relationships_of_gene_disease()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('generate tsv and cypher file')

    generate_tsv_and_cypher_file()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
