import sys
import csv

import datetime, time
sys.path.append("../..")
import create_connection_to_databases, authenticate


# encoding=utf8
reload(sys)
sys.setdefaultencoding('utf8')

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

'''
go through unichem mapping between chembl and drugban and check if they have the same information or new information
'''
def load_and_check_chembl_drugbank_mapping():
    file=open('extra/src1src2.txt','r')
    csv_reader=csv.DictReader(file, delimiter='\t')

    write_file=open('extra/new_mapped.csv','w')
    csv_writer=csv.writer(write_file)
    csv_writer.writerow(['DrugBank_id','ChEMBL_ID'])
    counter_equal_mapping=0
    counter_new_mapping=0
    counter_unequal=0
    counter_all_drugbank_mapps=0
    for row in csv_reader:
        counter_all_drugbank_mapps+=1
        drugbank_id=row["To src:'2'"]
        chembl_id=row["From src:'1'"]
        query='''MATCH (n:Compound_DrugBank{identifier:'%s'}) RETURN n.ChEMBL''' %(drugbank_id)
        result=g.run(query)
        for chembl_id_db, in result:
            if drugbank_id=='DB07403':
                print('df')
            if chembl_id_db!=chembl_id and not chembl_id_db is  None :
                print('unequal')
                print(drugbank_id)
                print(chembl_id_db)
                print(chembl_id)
                counter_unequal+=1
            elif chembl_id_db==chembl_id:
                counter_equal_mapping+=1
            else:
                print('new')
                print(drugbank_id)
                print(chembl_id_db)
                print(chembl_id)
                csv_writer.writerow([drugbank_id,chembl_id])
                counter_new_mapping+=1

    print('number of all mapped drugbank:'+str(counter_all_drugbank_mapps))
    print('number of equal mapped:'+str(counter_equal_mapping))
    print('number of new mapped:'+str(counter_new_mapping))
    print('number of different mapped:'+str(counter_unequal))




def main():
    print (datetime.datetime.utcnow())
    print('create connection')

    create_connection_with_neo4j_mysql()


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('generate shell script')

    load_and_check_chembl_drugbank_mapping()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()