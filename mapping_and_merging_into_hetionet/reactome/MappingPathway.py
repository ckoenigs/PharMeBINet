import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet pathways with identifier as key and value the name
dict_pathway_hetionet = {}

# dictionary with hetionet pathways with identifier as key and value the xrefs
dict_pathway_hetionet_xrefs = {}

# dictionary with hetionet pathways with name as key and value the identifier
dict_pathway_hetionet_names = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary from pathway_id to resource
dict_pathwayId_to_resource = {}

# Höchste Zahl des Identifiers um neue Identifier zu vergeben (PC_11_...)
highest_identifier = 0

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    global highest_identifier
    # query ist ein String
    query = '''MATCH (n:Pathway) RETURN n.identifier, n.name, n.source, n.xrefs, n.resource'''
    # query = '''MATCH (n:Pathway) RETURN n.identifier,n.names, n.source, n.idOwns'''
    # graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    results = graph_database.run(query)
    # results werden einzeln durchlaufen
    for identifier, name, source, idOwns, resource, in results:
        # identifier von hetionet (PC_11_) herausbekommen, der die größte Zahl hat, damit keiner überschrieben wird
        if int(identifier.split("_", -1)[1]) > highest_identifier:
            # teilt den String PC_11_Zahl in PC_11_ und Zahl (durch -1 trennt er bei dem zweiten _
            # [1] gibt an, dass der zweite Teil als highest_identifier gespeichert wird
            highest_identifier = int(identifier.split("_", -1)[1])
        # im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        dict_pathway_hetionet[identifier] = name
        dict_pathway_hetionet_xrefs[identifier] = idOwns
        dict_pathwayId_to_resource[identifier] = resource
        if idOwns:
            # geht die Liste idOwns in neo4j durch und baut das dictionary auf an identifiern (von externen Identifier ist idOwn
            for idOwn in idOwns:
                idOwn = idOwn.split(':', 1)[1]
                if not idOwn in dict_own_id_to_identifier:
                    dict_own_id_to_identifier[idOwn] = identifier
                else:
                    print(idOwn)
        dict_pathway_hetionet_names[name.lower()] = identifier

    print('number of pathway nodes in hetionet:' + str(len(dict_pathway_hetionet)))


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w', encoding="utf-8")
# Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_pathways, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['newId', 'id', 'name'])

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_pathways, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_hetionet', 'ownId', 'resource', 'Pathway_name', 'Pathway_names'])

'''
load all reactome pathways and check if they are in hetionet or not
'''


def load_reactome_pathways_in():
    global highest_identifier
    query = '''MATCH (n:Pathway_reactome) RETURN n'''
    results = graph_database.run(query)

    # zähler wie oft id mapt und und oft der name mapt
    counter_map_with_id = 0
    counter_map_with_name = 0
    for pathways_node, in results:
        pathways_id = pathways_node['stId']
        pathways_name = pathways_node['displayName'].lower()
        # check if the reactome pathway id is part in the hetionet idOwn
        # mapping nach dem identifier
        if pathways_id in dict_own_id_to_identifier:
            counter_map_with_id += 1
            # print('id')
            # print(dict_own_id_to_identifier[pathways_id])
            pathway_names = dict_pathway_hetionet[dict_own_id_to_identifier[pathways_id]]
            # PC_11_Zahl Nummer wird im Dictionary nachgeschaut
            hetionet_identifier = dict_own_id_to_identifier[pathways_id]
            # Liste von idOwns wird nach dem PC_11_Zahl durchsucht und als String aneinandergehängt (join)
            # als Trennungssymbol wird | genutzt
            own_ids = dict_pathway_hetionet_xrefs[hetionet_identifier]
            own_ids.append('reactome:'+pathways_id)
            string_own_ids = '|'.join(go_through_xrefs_and_change_if_needed_source_name(own_ids,'pathway'))
            resource = set(dict_pathwayId_to_resource[hetionet_identifier])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            csv_mapped.writerow([pathways_id, hetionet_identifier, string_own_ids, resource, pathways_name])

        # mapping nach dem Namen
        elif pathways_name in dict_pathway_hetionet_names:
            counter_map_with_name += 1
            print(pathways_id)
            print('mapped with name')
            print(dict_pathway_hetionet_names[pathways_name])
            print(pathways_name)

            hetionet_identifier = dict_pathway_hetionet_names[pathways_name]
            own_ids = dict_pathway_hetionet_xrefs[hetionet_identifier]
            own_ids.append('reactome:'+pathways_id)
            string_own_ids = '|'.join(go_through_xrefs_and_change_if_needed_source_name(own_ids,'pathway'))
            resource = set(dict_pathwayId_to_resource[hetionet_identifier])
            resource.add('Reactome')
            resource = '|'.join(sorted(resource))
            pathway_names = dict_pathway_hetionet[dict_pathway_hetionet_names[pathways_name]]
            csv_mapped.writerow(
                [pathways_id, hetionet_identifier, string_own_ids, resource, pathways_name, pathway_names])

        # übrige Knoten, die nicht mappen, werden neu erstellt und bekommen neuen Identifier PC_11_Zahl
        # dafür braucht man die höchte Zahl +1, damit keiner überschrieben wird
        else:
            highest_identifier += 1
            new_identifier = "PC12_" + str(highest_identifier)
            csv_not_mapped.writerow([new_identifier, pathways_id, pathways_name])  # new_identifier, pathways_id,

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))


'''
generate connection between mapping pathways of reactome and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'w', encoding="utf-8")
    # mappt die Knoten, die es in hetionet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/pathway/mapped_pathways.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Pathway{identifier:line.id_hetionet}),(c:Pathway_reactome{stId:line.id}) CREATE (d)-[: equal_to_reactome_pathway]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes", d.name = c.displayName, d.synonyms = apoc.convert.fromJsonList(c.name), d.alternative_id = c.oldStId, d.books = c.books, d.pubMed_ids = c.pubMed_ids, d.figure_urls = c.figure_urls, d.publication_urls = c.publication_urls, d.doi = c.doi, d.definition = c.definition, d.xrefs = split(line.ownId,"|");\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)

    # Neue Knoten werden erzeugt, von denen die nicht mappen
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smaster_database_change/mapping_and_merging_into_hetionet/reactome/pathway/not_mapped_pathways.tsv" As line FIELDTERMINATOR "\\t" MATCH (c:Pathway_reactome{stId:line.id}) CREATE (d:Pathway{identifier:line.newId, resource:['Reactome'], reactome:"yes", name:c.displayName, synonyms:apoc.convert.fromJsonList(c.name), xrefs:["reactome:"+c.stId],  alternative_id:c.oldStId, books:c.books, pubMed_ids:c.pubMed_ids, figure_urls:c.figure_urls, publication_urls:c.publication_urls, doi:c.doi, definition:c.definition, source:"Reactome", url:"https://reactome.org/content/detail/"+line.id}) CREATE (d)-[: equal_to_reactome_pathway]->(c) ;\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)

    # cypher_file.write(':begin\n')
    # query = '''MATCH (d:Pathway_reactome) WHERE NOT  exists(d.reactome) SET d.reactome="no";\n '''
    # cypher_file.write(query)
    # cypher_file.write(':commit\n')


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path reactome protein')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all pathways from hetionet into a dictionary')

    load_hetionet_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all reactome pathways from neo4j into a dictionary')

    load_reactome_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Integrate new pathways and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
