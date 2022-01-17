import csv, datetime, sys
sys.path.append("../..")
import create_connection_to_databases

# check why 20 edges of RNA-RNA inter are not integrated

print(datetime.datetime.now(), 'load ids from neo4j')
g = create_connection_to_databases.database_connection_neo4j()

set_of_ids_in_neo4j=set()
query='MATCH (n:rna_RNAInter) RETURN n.Raw_ID '
results=g.run(query)
for raw_id, in results:
    set_of_ids_in_neo4j.add(raw_id)

print(datetime.datetime.now(), 'load ids from file')


file=open('data/Download_data_RR.txt','r',encoding='utf-8')
csv_reader=csv.DictReader(file, delimiter='\t')

set_rna_ids=set()
set_where_no_raw_id=set()

def get_the_identifier(raw_id_name, symbol, row):
    raw_id = row[raw_id_name]
    if raw_id == 'N/A':
        gene_symbol = row[symbol]
        set_where_no_raw_id.add(gene_symbol)
        raw_id = gene_symbol
    set_rna_ids.add(raw_id)
    if raw_id not in set_of_ids_in_neo4j:
        print(raw_id, type(raw_id))
    return raw_id

counter_row=0
counter_empty_identifier=0
for row in csv_reader:
    counter_row+=1

    raw_id_1=get_the_identifier('Raw_ID1','Interactor1.Symbol',row)
    raw_id_2 = get_the_identifier('Raw_ID2', 'Interactor2.Symbol',row)
    # print entries which are still N/A (so raw id and gene symbol are N/A)
    if raw_id_2=='N/A' or raw_id_1=='N/A':
        print(counter_row, raw_id_1,raw_id_2)
        counter_empty_identifier+=1
    # print(raw_id_1,raw_id_2)
    # break

print('number of rna in file',len(set_rna_ids))
print('number of rna without an raw id:',len(set_where_no_raw_id))
print('number of rows where for at least one rna no information exists:', counter_empty_identifier)
print(datetime.datetime.now(), 'finished')