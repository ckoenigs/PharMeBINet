import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases
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
dict_gene_go = {}

# tsv files for bp. mf, cc
bp_file = open('gene_go/bp.tsv', 'w')
bp_writer = csv.writer(bp_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
bp_writer.writerow(['GeneID', 'GOID'])

mf_file = open('gene_go/mf.tsv', 'w')
mf_writer = csv.writer(mf_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
mf_writer.writerow(['GeneID', 'GOID'])

cc_file = open('gene_go/cc.tsv', 'w')
cc_writer = csv.writer(cc_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
cc_writer.writerow(['GeneID', 'GOID'])

# dictionary with for biological_process, cellular_component, molecular_function the right file
dict_process = {
    "Biological Process": bp_writer,
    "Molecular Function": mf_writer,
    "Cellular Component": cc_writer
}

# dictionary counter for bp, cc, mf
dict_process_counter = {
    "Biological Process": 0,
    "Molecular Function": 0,
    "Cellular Component": 0
}

# dict of labels of the go in hetionet to file names
dict_labels_go_to_file_name = {
    'BiologicalProcess': 'bp',
    'MolecularFunction': 'mf',
    'CellularComponent': 'cc'
}

'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a tsv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_go():
    # generate cypher file
    cypherfile = open('output/cypher_edge.cypher', 'a', encoding='utf-8')
    query = ''' Match (n:Gene{identifier:line.GeneID}), (b:%s{identifier:line.GOID}) Merge (n)-[r:PARTICIPATES_Gp%s]->(b) On Create Set  r.ctd='yes', r.url="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2024 NC State University. All rights reserved.", r.unbiased=false, r.resource=['CTD'] On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID, r.resource=r.resource+'CTD' '''
    for label, file_name in dict_labels_go_to_file_name.items():
        label_query = query % (label, file_name.upper())
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/ctd/gene_go/{file_name}.tsv',
                                                  query)
        cypherfile.write(label_query)
    cypherfile.close()

    query = '''MATCH (gene:CTD_gene)-[r:associates_GGO]->(go:CTD_GO) Where ()-[:equal_to_CTD_gene]->(gene)  RETURN gene.gene_id, r, go.go_id, go.ontology'''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    for record in results:
        [gene_id, rela, go_id, ontology] = record.values()
        rela = dict(rela)
        if len(rela) > 1:
            print('change integration of properties')
        if not (gene_id, go_id) in dict_gene_go:
            dict_gene_go[(gene_id, go_id)] = rela
            dict_process_counter[ontology] += 1
            writer = dict_process[ontology]
            writer.writerow([gene_id, go_id])
            count_possible_relas += 1
        else:
            count_multiple_pathways += 1
        if count_possible_relas % 1000 == 0:
            print(count_possible_relas)

    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))
    print(dict_process_counter)


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
    print('Take all gene-go relationships and generate tsv files and cypher file')

    take_all_relationships_of_gene_go()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
