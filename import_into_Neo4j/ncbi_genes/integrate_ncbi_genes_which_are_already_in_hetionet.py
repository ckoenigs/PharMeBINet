
import datetime
import sys, csv


# list of found genes
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


    #count all row in the file
    counter_all=0
    #count all row which will be integrated
    counter_included=0
    #counter all gene which are human and in hetionet
    counter_gene_in_hetionet_and_human=0

    #create cypher file
    cypher_file=open('cypher_node.cypher','w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ncbi_genes/output_data/genes.csv" As line Fieldterminator '\\t' Create (n:Gene_Ncbi {'''

    # add properties into the queries
    for property in reader.fieldnames:

        if property in  ['Synonyms','dbXrefs','map_location','Feature_type','Other_designations']:
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
    counter_not_same_name_and_description=0

    # generate human gene csv
    for row in reader:

        counter_all+=1
        gene_id =row['GeneID']
        name=row['Full_name_from_nomenclature_authority']
        description=row['description']

        if name!=description and name != '-':
            counter_not_same_name_and_description+=1
            if tax_id == '9606':
                print(name)
                print(description)
                print(gene_id)

        # if gene_id=='100422997':
        #     print('ok')
        #tax id 9606 is human
        tax_id=row['#tax_id']
        if tax_id!='9606':
            writer_not_human.writerow(row)
            found_gene_ids.append(int(gene_id))
        else:
            counter_gene_in_hetionet_and_human+=1
            counter_included+=1
            writer.writerow(row)
            found_gene_ids.append(int(gene_id))

    print(len(found_gene_ids))
    print('all rows in ncbi gene_info file:'+str(counter_all))
    print('all included ncbi gene_info rows in new file:'+str(counter_included))
    print('all genes which are in hetionet and human:'+str(counter_gene_in_hetionet_and_human))
    print('number of name and description not equal:'+str(counter_not_same_name_and_description))





def main():
    print(datetime.datetime.utcnow())
    print('generate a tsv file with only the human genes')

    load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()