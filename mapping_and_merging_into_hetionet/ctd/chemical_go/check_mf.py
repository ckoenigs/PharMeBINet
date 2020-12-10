import  csv, sys,datetime
sys.path.append("../..")
import create_connection_to_databases, authenticate

authenticate("localhost:7474", "neo4j", "test")
global g
g = Graph("http://localhost:7474/db/data/")

dict_chemical={}
dict_go={}
dict_pairs={}
print (datetime.datetime.utcnow())

file= open('mf.csv','r')
reader=csv.DictReader(file)
counter=0
counter_multiple=0
for line in reader:
    counter+=1
    chemical_id=line['ChemicalID']
    go_id = line['GOID']
    if not (chemical_id,go_id) in dict_pairs:
        dict_pairs[(chemical_id,go_id)]=1
    else:
        print(go_id)
        print(chemical_id)
        counter_multiple+=1
        # sys.exit('multi pair')
    # if  not go_id in dict_go:
    #     query='''MATCH (n:MolecularFunction) Where n.identifier='%s' RETURN n LIMIT 25'''
    #     query=query %(go_id)
    #     result=g.run(query)
    #     first= result.evaluate()
    #     if first is None:
    #         print(go_id)
    #         print(chemical_id)
    #         print('false go')
    #         sys.exit()
    #     dict_go[go_id]=1
    # if not chemical_id in dict_chemical:
    #     query = '''MATCH (n:Chemical) Where n.identifier='%s' RETURN n LIMIT 25'''
    #     query = query % (chemical_id)
    #     result = g.run(query)
    #     first = result.evaluate()
    #     if first is None:
    #         print(go_id)
    #         print(chemical_id)
    #         print('false chemical')
    #         sys.exit()
    #     dict_chemical[chemical_id]=1
    if counter %100000==0:
        print(counter)
        print (datetime.datetime.utcnow())

print(counter_multiple)