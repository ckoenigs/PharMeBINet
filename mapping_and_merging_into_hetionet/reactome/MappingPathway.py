import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()



# dictionary with pharmebinet pathways with identifier as key and value the xrefs
dict_pathway_pharmebinet_xrefs = {}

# dictionary with pharmebinet pathways with name as key and value the identifier
dict_pathway_pharmebinet_names = {}

# dictionary from own id to new identifier
dict_reactome_it_to_identifier = {}

# dictionary from pathway_id to resource
dict_pathwayId_to_resource = {}

# highest id for new pathway ids (PC_13_...)
highest_identifier = 0

'''
load in all pathways from pharmebinet in a dictionary
'''


def load_pharmebinet_pathways_in():
    global highest_identifier
    query = '''MATCH (n:Pathway) RETURN n.identifier, n.name, n.source, n.xrefs, n.resource'''
    results = graph_database.run(query)
    # run through results
    for identifier, name, source, xrefs, resource, in results:
        # try to get the highest existing pathway id
        if int(identifier.split("_", -1)[1]) > highest_identifier:
            highest_identifier = int(identifier.split("_", -1)[1])
        dict_pathway_pharmebinet_xrefs[identifier] = set(xrefs)
        dict_pathwayId_to_resource[identifier] = resource
        if xrefs:
            # go through all xrefs and prepare dictionary with reactome ids
            for xref in xrefs:
                xref = xref.split(':', 1)
                if xref[0]=='reactome':
                    if not xref[1] in dict_reactome_it_to_identifier:
                        dict_reactome_it_to_identifier[xref[1]] = identifier
                    else:
                        print(xref)
        if name is not None:
            dict_pathway_pharmebinet_names[name.lower()] = identifier

    print('number of pathway nodes in pharmebinet:' + str(len(dict_pathwayId_to_resource)))


# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_pathways, delimiter='\t', lineterminator='\n')
csv_not_mapped.writerow(['newId', 'id', 'name'])

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_pathways, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_pharmebinet', 'ownId', 'resource', 'Pathway_name', 'Pathway_names'])

'''
load all reactome pathways and check if they are in pharmebinet or not
'''


def load_reactome_pathways_in():
    global highest_identifier
    query = '''MATCH (n:Pathway_reactome)-[r]-(s:Species_reactome) WHERE s.taxId = "9606" RETURN Distinct n'''
    results = graph_database.run(query)

    # count how often map with name or with name
    counter_map_with_id = 0
    counter_map_with_name = 0
    for pathways_node, in results:
        pathways_id = pathways_node['stId']
        pathways_name = pathways_node['displayName'].lower()
        synonyms= pathways_node['name'] if 'name' in pathways_node else []
        #boolean to chek if a mapping happend or not
        found_mapping=False
        # check if the reactome pathway id is part in the pharmebinet xref
        # mapping with identifier
        if pathways_id in dict_reactome_it_to_identifier:
            counter_map_with_id += 1
            found_mapping=True
            pharmebinet_identifier = dict_reactome_it_to_identifier[pathways_id]
            xrefs = dict_pathway_pharmebinet_xrefs[pharmebinet_identifier]
            xrefs.add('reactome:'+pathways_id)
            string_xrefs = '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs,'pathway'))

            csv_mapped.writerow([pathways_id, pharmebinet_identifier, string_xrefs, pharmebinetutils.resource_add_and_prepare(dict_pathwayId_to_resource[pharmebinet_identifier],'reactome'), pathways_name])

        # mapping with Namen
        elif pathways_name in dict_pathway_pharmebinet_names:
            counter_map_with_name += 1
            found_mapping=True
            pharmebinet_identifier = dict_pathway_pharmebinet_names[pathways_name]
            xrefs = dict_pathway_pharmebinet_xrefs[pharmebinet_identifier]
            xrefs.add('reactome:'+pathways_id)
            string_xrefs = '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs,'pathway'))
            csv_mapped.writerow(
                [pathways_id, pharmebinet_identifier, string_xrefs, pharmebinetutils.resource_add_and_prepare(dict_pathwayId_to_resource[pharmebinet_identifier],'reactome'), pathways_name])

        if found_mapping:
            continue

        multiple_mappings_list=set()
        for synonym in synonyms:
            synonym=synonym.lower()

            if synonym in dict_pathway_pharmebinet_names:
                found_mapping=True
                pharmebinet_identifier = dict_pathway_pharmebinet_names[synonym]
                xrefs = dict_pathway_pharmebinet_xrefs[pharmebinet_identifier]
                xrefs.add('reactome:' + pathways_id)
                string_xrefs = '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'pathway'))
                csv_mapped.writerow(
                    [pathways_id, pharmebinet_identifier, string_xrefs,
                     pharmebinetutils.resource_add_and_prepare(dict_pathwayId_to_resource[pharmebinet_identifier],
                                                               'reactome'), pathways_name])

        if found_mapping :
            counter_map_with_name+=1


        # übrige Knoten, die nicht mappen, werden neu erstellt und bekommen neuen Identifier PC_11_Zahl
        # dafür braucht man die höchte Zahl +1, damit keiner überschrieben wird
        else:
            highest_identifier += 1
            new_identifier = "PC12_" + str(highest_identifier)
            csv_not_mapped.writerow([new_identifier, pathways_id, pathways_name])  # new_identifier, pathways_id,

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))


'''
generate connection between mapping pathways of reactome and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'w', encoding="utf-8")
    # mappt die Knoten, die es in pharmebinet und reactome gibt und fügt die properties hinzu
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/pathway/mapped_pathways.tsv" As line FIELDTERMINATOR "\\t" MATCH (d:Pathway{identifier:line.id_pharmebinet}),(c:Pathway_reactome{stId:line.id}) CREATE (d)-[: equal_to_reactome_pathway]->(c) SET d.resource = split(line.resource, '|'), d.reactome = "yes", d.name = c.displayName, d.synonyms = apoc.convert.fromJsonList(c.name), d.alternative_id = c.oldStId, d.books = c.books, d.pubMed_ids = c.pubMed_ids, d.figure_urls = c.figure_urls, d.publication_urls = c.publication_urls, d.doi = c.doi, d.definition = c.definition, d.xrefs = split(line.ownId,"|");\n'''
    query = query % (path_of_directory)
    cypher_file.write(query)

    # Neue Knoten werden erzeugt, von denen die nicht mappen
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/pathway/not_mapped_pathways.tsv" As line FIELDTERMINATOR "\\t" MATCH (c:Pathway_reactome{stId:line.id}) CREATE (d:Pathway{identifier:line.newId, resource:['Reactome'], reactome:"yes", name:c.displayName, synonyms:apoc.convert.fromJsonList(c.name), xrefs:["reactome:"+c.stId],  alternative_id:c.oldStId, books:c.books, pubMed_ids:c.pubMed_ids, figure_urls:c.figure_urls, publication_urls:c.publication_urls, doi:c.doi, definition:c.definition, source:"Reactome", url:"https://reactome.org/content/detail/"+line.id, license:"%s"}) CREATE (d)-[: equal_to_reactome_pathway]->(c) ;\n'''
    query = query % (path_of_directory, license)
    cypher_file.write(query)


def main():
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license=sys.argv[2]
    else:
        sys.exit('need a path  and license reactome protein')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all pathways from pharmebinet into a dictionary')

    load_pharmebinet_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all reactome pathways from neo4j into a dictionary')

    load_reactome_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate new pathways and connect them to reactome ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
