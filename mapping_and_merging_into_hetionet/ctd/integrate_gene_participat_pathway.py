
import datetime
import csv, sys

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", )
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary with all pairs and properties as value
dict_gene_pathway = {}

'''
get all relationships between gene and pathway, take the hetionet identifier an save all important information in a tsv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_pathway():
    # generate cypher file
    cypherfile = open('output/cypher_edge.cypher', 'w',encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/ctd/gene_pathway/relationships.tsv" As line  FIELDTERMINATOR '\\t' Match (n:Gene{identifier:line.GeneID}), (b:Pathway{identifier:line.PathwayID}) Merge (n)-[r:PARTICIPATES_IN_GpiPW]->(b) On Create Set r.ctd='yes', r.url="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.source="CTD", r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2021 NC State University. All rights reserved.", r.unbiased=false, r.resource=["CTD"] On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID, r.resource=r.resource+"CTD";\n '''
    cypherfile.write(query)
    cypherfile.close()

    csvfile = open('gene_pathway/relationships.tsv', 'w')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['GeneID', 'PathwayID'])

    query = '''MATCH (gene:CTD_gene)-[r:participates_GP]->(pathway:CTD_pathway) Where ()-[:equal_to_CTD_gene]->(gene)  RETURN gene.gene_id, r, pathway.hetionet_id'''
    results = g.run(query)
    count_multiple_pathways = 0
    count_possible_relas = 0
    for gene_id, rela, pathway_hetionet_id, in results:
        rela = dict(rela)
        if len(rela) > 1:
            print('change integration of properties')
        if not (gene_id, pathway_hetionet_id) in dict_gene_pathway:
            dict_gene_pathway[(gene_id, pathway_hetionet_id)] = rela
            writer.writerow([gene_id, pathway_hetionet_id])
            count_possible_relas += 1
        else:
            count_multiple_pathways += 1
        if count_possible_relas % 1000 == 0:
            print(count_possible_relas)

        # query='''MATCH p=(gene:Gene{identifier:%s})-[r:PARTICIPATES_GpPW]->(pathway:Pathway{identifier:"%s"}) Return p'''
        # query=query%(gene_id,pathway_hetionet_id)
        # match_result=g.run(query)
        # has_one_enty=match_result.evaluate()
        # if has_one_enty==None:
        #     print('no entry')
        #     print(gene_id,pathway_hetionet_id)

    print('number of new rela:' + str(count_possible_relas))
    print('number of relationships which appears multiple time:' + str(count_multiple_pathways))


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

    take_all_relationships_of_gene_pathway()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()