import csv, sys
sys.path.append("../..")
import create_connection_to_databases, authenticate

print(sys.argv)
csv.field_size_limit(100000000)
file_path= sys.argv[1]
readfile=open(file_path,'r')
csv_reader=csv.DictReader(readfile, delimiter=',')

authenticate("localhost:7474", "neo4j", "test")
g = Graph("http://localhost:7474/db/data/")

counter=0
counter_not_protein=0
counter_not_gene=0
for row in csv_reader:
    counter+=1
    chemical=row['ChemicalID']
    gene_id=row['GeneID']

    query = '''Match (b:Chemical{identifier:"%s"}) Return b.identifier;'''
    query = query % (chemical)
    results = g.run(query)
    first = results.evaluate()
    if first is None:
        print('chemical')
        print(row)
        print(counter)
        sys.exit()

    query = '''Match (b:Gene{identifier:%s}) Return b.identifier;'''
    query = query % (gene_id)
    results = g.run(query)
    first = results.evaluate()
    if first is None:
        counter_not_gene += 1
        print('gene')
        print(row)
        print(counter)
        continue
        # sys.exit()

    query = '''Match (g:Gene{identifier:%s})-[:PRODUCES_GpP]->(n:Protein) Return n.identifier;'''
    query = query % (gene_id)
    results = g.run(query)
    first = results.evaluate()
    if first is None:
        counter_not_protein += 1
        print('protein')
        print(row)
        print(counter)
        # sys.exit()
print('number of not existing protein:'+str(counter_not_protein))
print('number of not existing gene:'+str(counter_not_gene))