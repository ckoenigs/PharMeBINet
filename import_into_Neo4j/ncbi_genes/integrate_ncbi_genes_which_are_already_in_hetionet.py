'''integrate the'''
from Bio.pairwise2 import identity_match
from py2neo import Graph, authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

#dictionary with all gene ids to there name
dict_hetionet_gene_ids_to_name={}

'''
load all ncbi identifier from the gene ides into a dictionary (or list)
'''
def get_all_ncbi_ids_form_hetionet_genes():
    query='''Match (g:Gene) Return g.identifier, g.name;'''
    results=g.run(query)
    for identifier, name, in results:
        dict_hetionet_gene_ids_to_name[identifier]=name

    print('number of genes in hetionet:'+str(len(dict_hetionet_gene_ids_to_name)))

# list of found gene ids, because i think not all gene ids from hetionet exists anymore
found_gene_ids=[]

'''
load ncbi tsv file in and write only the important lines into a new csv file for integration into Neo4j
'''
def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():

    # read file to get the information
    load_file=open('data/gene_info','r')
    reader=csv.DictReader(load_file,delimiter='\t')

    dict_header={}
    for header_property in reader.fieldnames:
        if header_property=='#tax_id':
            dict_header[header_property]='tax_id'
        else:
            dict_header[header_property]=header_property

    # file for integration into hetionet
    file = open('output_data/genes.csv', 'w')
    writer = csv.DictWriter(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=reader.fieldnames)
    # writer.writeheader()
    writer.writerow(dict_header)

    # file with all gene from hetionet which are not human
    file_nH = open('output_data/genes_not_human.csv', 'w')
    writer_not_human = csv.DictWriter(file_nH, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                            fieldnames=reader.fieldnames)
    writer_not_human.writeheader()


    # file with all gene  are human but not in hetionet
    file_H = open('output_data/genes_human_not_in_hetionet.csv', 'w')
    writer_human_not_in_hetionet = csv.DictWriter(file_H, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                            fieldnames=reader.fieldnames)
    writer_human_not_in_hetionet.writeheader()

    #count all row in the file
    counter_all=0
    #count all row which will be integrated
    counter_included=0
    #counter all gene which are human and in hetionet
    counter_gene_in_hetionet_and_human=0

    cypher_file=open('cypher_node.cypher','w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ncbi_genes/output_data/genes.csv" As line Fieldterminator '\\t' Create (n:Gene_Ncbi {'''

    for property in reader.fieldnames:

        if property in  ['Synonyms','dbXrefs','map_location','Feature_type']:
            query += property + ':split(line.' + property + ",'|') ,"
        elif property in ['#tax_id', 'GeneID']:
            if property=='GeneID':
                query+= 'identifier:line.'+property+' ,'
            else:
                query += 'tax_id:line.tax_id ,'
        else:
            query+= property+':line.'+property+' ,'

    query= query[:-2]+'});\n'
    cypher_file.write(query)
    query = 'Create Constraint On (node:Gene_Ncbi) Assert node.identifier Is Unique;\n'
    cypher_file.write(query)

    for row in reader:

        counter_all+=1
        gene_id =row['GeneID']
        if gene_id=='100422997':
            print('ok')
        #tax id 9606 is human
        tax_id=row['#tax_id']
        if int(gene_id) in dict_hetionet_gene_ids_to_name:
            if tax_id!='9606':
                writer_not_human.writerow(row)
                found_gene_ids.append(int(gene_id))
            else:
                counter_gene_in_hetionet_and_human+=1
                counter_included+=1
                writer.writerow(row)
                found_gene_ids.append(int(gene_id))
        else:
            if tax_id=='9606':
                counter_included+=1
                writer_human_not_in_hetionet.writerow(row)
                writer.writerow(row)

    all_ids_inhetionet=dict_hetionet_gene_ids_to_name.keys()
    difference= set(all_ids_inhetionet).difference(found_gene_ids)
    # print(found_gene_ids)
    print(len(found_gene_ids))
    print('dddddddddddddddddddddddddddddddddddddddddddddddddd')
    print(len(difference))
    print(difference)
    print('all rows in ncbi gene_info file:'+str(counter_all))
    print('all included ncbi gene_info rows in new file:'+str(counter_included))
    print('all genes which are in hetionet and human:'+str(counter_gene_in_hetionet_and_human))





def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the hetionet genes')

    get_all_ncbi_ids_form_hetionet_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gnerate a tsv file with only the hetionet genes')

    load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()