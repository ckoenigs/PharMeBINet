
sys.path.append("../..")
import create_connection_to_databases, authenticate
import datetime
import sys, csv

# reload(sys)
# sys.setdefaultencoding("utf-8")


'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

'''
generate table for compounds to xrefs
'''
def generate_table():
    file_csv=open('drugbank_to_cross_ref.tsv','w')
    csv_writer= csv.writer(file_csv,delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['drugbank_id','name','chembl_id','other_cross_refs'])

    query= '''MATCH (n:Compound_DrugBank) RETURN n.identifier, n.name, n.external_identifiers'''
    results=g.run(query)

    for identifier, name, xrefs, in results:
        chembl=[]
        other_cross_refs=[]
        if xrefs:
            for xref in xrefs:
                xref_split=xref.split(':',1)
                if xref_split[0]=='ChEMBL':
                    chembl.append(xref_split[1])
                else:
                    other_cross_refs.append(xref)
        chembl='|'.join(chembl)
        other_cross_refs='|'.join(other_cross_refs)
        csv_writer.writerow([identifier.encode('utf-8'),name.encode('utf-8'),chembl.encode('utf-8'),other_cross_refs.encode('utf-8')])



def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load all hetionet compound in dictionary')

    generate_table()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()