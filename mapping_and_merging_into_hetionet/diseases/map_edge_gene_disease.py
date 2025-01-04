import datetime
import json
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


dict_existing_gene_disease_to_resource = {}


def load_existing_edges():
    """
    Load all drug interaction from database
    :return:
    """
    query = '''MATCH (a:Gene)<-[s:ASSOCIATES_DaG]-(b:Disease) RETURN a.identifier, b.identifier, s.resource'''
    results = g.run(query)
    for gene_id, disease_id, resource, in results:
        dict_existing_gene_disease_to_resource[(gene_id, disease_id)] = resource

    print('number of edges in database already:', len(dict_existing_gene_disease_to_resource))


def create_file_and_tsv_writer(file_name):
    """
    Generate file as tsv writer.
    :param file_name: string
    :return:
    """
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['gene_id', 'disease_id',  'rela_infos', 'doid' , 'resource'])
    return csv_writer


def load_diseases_edges(directory):
    """
    load all ddintere drug-drug interaction an map to existing or else create new edges.
    :param directory: directory
    :return:
    """

    # tsv_file
    file_name_mapped = directory + '/mapped_edges.tsv'
    csv_writer_mapped = create_file_and_tsv_writer(file_name_mapped)

    file_name_new = directory + '/new_edges.tsv'
    csv_writer_new = create_file_and_tsv_writer(file_name_new)

    # generate cypher files to integrate information
    generate_cypher_file(file_name_mapped, file_name_new)

    # get the DISEASES edges
    query = '''MATCH (n:Gene)--(:DISEASES_Gene)-[r:DISEASES_ASSOCIATED_WITH]-(j:DISEASES_Disease)--(m:Disease) Where r.evidence_type in ["data_source","experiment"] RETURN n.identifier, m.identifier, collect(r), collect(j.id) '''
    results = g.run(query)

    counter_all = 0
    counter_new = 0

    for gene_id,disease_id, rela_infos, diseases_ids, in results:
        counter_all += 1
        rela_infos = set([json.dumps(dict(x)) for x in rela_infos])
        if len(rela_infos)>1:
            print('ohje')
        if (gene_id,disease_id,) in dict_existing_gene_disease_to_resource:
            csv_writer_mapped.writerow([gene_id,disease_id, '|'.join(rela_infos), diseases_ids[0],
                                        pharmebinetutils.resource_add_and_prepare(
                                            dict_existing_gene_disease_to_resource[(gene_id,disease_id,)],
                                            "DISEASES")])
        else:
            counter_new += 1
            csv_writer_new.writerow(
                [gene_id,disease_id, '|'.join(rela_infos), diseases_ids[0]])

    print('count all edges:', counter_all)
    print('count new edges:', counter_new)


# cypher file generation
cypher_file = open('output/cypher_edge.cypher', 'w')


def generate_cypher_file(file_name, file_name_new):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param file_name_new: string
    :return:
    """
    query = ''' MATCH (n:Gene{identifier:line.gene_id}), (c:Disease{identifier:line.disease_id}) Match (c)-[r:ASSOCIATES_DaG]->(n)  Set r.resource=split(line.resource,"|"), r.diseases="yes",  r.diseases_rela_infos=split(line.rela_infos,"|")'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/diseases/{file_name}', query)
    cypher_file.write(query)

    query = '''MATCH (n:Gene{identifier:line.gene_id}), (c:Disease{identifier:line.disease_id}) Create (c)-[r:ASSOCIATES_DaG{ resource:["DISEASES"], source:"DISEASES", diseases:"yes" , license:"%s", url:"https://diseases.jensenlab.org/Entity?order=textmining,knowledge,experiments&textmining=10&knowledge=10&experiments=10&type1=-26&type2=9606&id1="+line.doid , diseases_rela_infos:split(line.rela_infos,"|")}]->(n) '''
    query = query % (license)
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/diseases/{file_name_new}',
                                              query)
    cypher_file.write(query)


def main():
    global path_of_directory, license
    license = ''
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license ')

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load existings edges')

    load_existing_edges()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in edges from diseases in')

    load_diseases_edges('output')

    driver.close()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
