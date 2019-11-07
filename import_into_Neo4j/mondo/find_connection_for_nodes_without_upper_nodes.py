from py2neo import Graph#, authenticate
import datetime
import csv,sys

# connect with the neo4j database
def database_connection():
    # authenticate("localhost:7474", )
    global g
    g = Graph("http://localhost:7474/db/data/",auth=("neo4j", "test"))


def find_an_upper_node(query, disease_id,jumper):
    results = g.run(query)
    target_dict = {}
    found_upper_mondo=False
    for relationships, node_id, in results:
        found_upper_mondo = True
        equivalentOriginalNodeSource = relationships[
            'equivalentOriginalNodeSource'] if 'equivalentOriginalNodeSource' in relationships else ''
        equivalentOriginalNodeTarget = relationships[
            'equivalentOriginalNodeTarget'] if 'equivalentOriginalNodeTarget' in relationships else ''
        isDefinedBy = relationships['isDefinedBy'] if 'isDefinedBy' in relationships else ''
        lbl = relationships['lbl'] if 'lbl' in relationships else ''
        if equivalentOriginalNodeTarget in target_dict:
            continue
        writer.writerow(
            [disease_id, node_id, jumper, equivalentOriginalNodeSource, equivalentOriginalNodeTarget, isDefinedBy, lbl])
        target_dict[equivalentOriginalNodeTarget] = equivalentOriginalNodeSource
    return found_upper_mondo

'''
open file with nodes without upper nodes and check for everyone if im mondo some upper node with mondo id exists and
integrate this information into a new file
'''
def generate_integration_file_with_nodes_without_upper_nodes():
    output_file= open('connection_nodes_without_upper.csv','wb')
    global writer
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['ID_a', 'ID_b','jump_number','equivalentOriginalNodeSource','equivalentOriginalNodeTarget','isDefinedBy','lbl'])

    part_query='''-[:subClassOf]->()'''

    cypherfile=open('cypher_file_not_connected_nodes.cypher','w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/import_into_Neo4j/mondo/connection_nodes_without_upper.csv" As line Match (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.ID_a}), (b:disease{`http://www.geneontology.org/formats/oboInOwl#id`:line.ID_b}) CREATE (a)-[:subClassOf{equivalentOriginalNodeSource:line.equivalentOriginalNodeSource,equivalentOriginalNodeTarget:line.equivalentOriginalNodeTarget,isDefinedBy:line.isDefinedBy,lbl:line.lbl}]->(b) With line, a Set a.level_add=line.jump_number;\n'''
    cypherfile.write(query)


    counter_of_all=1
    counter_no_subclass_connection=0
    count_where_nothing_is_found=0
    with open('nodes_without_upper_nodes.csv', 'r') as csvfile:
        reader=csv.DictReader(csvfile)
        for row in reader:
            counter_of_all += 1
            disease_id=row['ID']
            print(
                '#########################################################################################################')
            print(disease_id)
            found_upper_mondo=False

            # check if it has even one -subclass-> relationship so i do not run many loop to finde something
            query='''Match p=(n:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[r:subClassOf]->(b) Return p'''
            query=query %(disease_id)
            results=g.run(query)
            result= results.evaluate()
            # if no subclass relation is found check if on equivalent class exist with mondo id and take his upper node
            if result is None:
                print('no subclass relationship')
                print(disease_id)
                counter_no_subclass_connection+=1
                query='''Match (n:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[r:equivalentClass]-(b) Where b.`http://www.geneontology.org/formats/oboInOwl#id` Contains 'MONDO' Return Distinct(b.`http://www.geneontology.org/formats/oboInOwl#id`)'''
                query= query % (disease_id)
                results=g.run(query)
                found_something=False
                found_an_equivalent_class=False
                for node_id, in results:
                    query='''Match (n:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})-[r:subClassOf]->(b) Where b.`http://www.geneontology.org/formats/oboInOwl#id` Contains 'MONDO' Return r,b.`http://www.geneontology.org/formats/oboInOwl#id` '''
                    query=query %(node_id)
                    print(query)
                    found_something=find_an_upper_node(query,disease_id,'') or found_something
                    found_an_equivalent_class=True
                if not found_something and not found_an_equivalent_class:
                    print('also equivalent class did not help')
                    count_where_nothing_is_found += 1
                elif not found_something:
                    print('has equivalent class but this has also no subclass')
                    count_where_nothing_is_found += 1
                else:
                    print('found something with equ. class')

                continue

            # if it has subclass relationshp find the next upper node(s) which has a mondo id
            start_query = '''Match (n:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})'''
            start_query= start_query %(disease_id)
            jumper=0
            while not found_upper_mondo:
                if jumper > 20:
                    print('never ending')
                    print(disease_id)
                    break
                query = start_query+'''-[r:subClassOf]->(b) Where b.`http://www.geneontology.org/formats/oboInOwl#id` Contains 'MONDO' Return r,b.`http://www.geneontology.org/formats/oboInOwl#id` '''
                print(query)
                found_upper_mondo= find_an_upper_node(query,disease_id,jumper)
                jumper+=1
                start_query=start_query+part_query
            # if i> 2:
            #     break

    cypherfile.close()


    print('number of not connected node:'+str(counter_of_all))
    print('number of nodes  which has no subclass relationship:'+str(counter_no_subclass_connection))
    print('number of nodes which get no subclass relationship:'+str(count_where_nothing_is_found))

# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate integration files with all nodes which has no upper node but will get one now')

    generate_integration_file_with_nodes_without_upper_nodes()


    print('##########################################################################')


    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
