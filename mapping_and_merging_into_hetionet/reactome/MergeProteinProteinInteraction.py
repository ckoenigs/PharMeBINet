import datetime
import csv
import sys
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet interactions between proteins with interactor1_id as key and value interactor2_id
dict_interactions_hetionet = {}

# dictionary from identifier to resource_1
dict_identifier_to_resource = {}

# dictionary of all properties of egde
dict_rela_info = {}

# dictionary from protein identifier to iso_from and iso_to
dict_protein_ids_to_iso_from_and_to = {}

# dictionary from protein identifier to iso_form and iso_to for created interactions
dict_protein_ids_to_iso_from_and_to_2 = {}

'''
load in all Interactions from hetionet into dictionary
'''


def load_hetionet_interactions_in():
    global maximal_id
    query = '''MATCH (n:Protein)-->(a:Interaction)-->(m:Protein) RETURN n.identifier, m.identifier, a.resource, a.identifier, a.interaction_ids, a.iso_of_protein_from, a.iso_of_protein_to;'''
    results = graph_database.run(query)

    for interactor1_het_id, interactor2_het_id, resource, interaction_id, interaction_ids_EBI, iso_of_protein_from, iso_of_protein_to, in results:
        iso_of_protein_from = iso_of_protein_from if iso_of_protein_from is not None else ""
        iso_of_protein_to = iso_of_protein_to if iso_of_protein_to is not None else ""
        interaction_ids_EBI = interaction_ids_EBI if not interaction_ids_EBI is None else []
        dict_identifier_to_resource[
            (interactor1_het_id, interactor2_het_id, iso_of_protein_from, iso_of_protein_to)] = {'resource': resource,
                                                                                                 'interaction_ids_EBI': interaction_ids_EBI,
                                                                                                 'interaction_id': interaction_id}
    query = 'MATCH (n:Interaction) With toInteger(n.identifier ) as int_id RETURN max(int_id)'

    maximal_id = graph_database.run(query).evaluate()

    print('number of interactions in hetionet: ' + str(
        len(dict_identifier_to_resource)))


'''
load all reactome interactions and check if they are in hetionet or not
'''

set_pair = set()


def load_reactome_drug_in(label_1, label_2):
    global highest_identifier, dict_protein_ids_to_iso_from_and_to, dict_protein_ids_to_iso_from_and_to_2
    dict_protein_ids_to_iso_from_and_to = {}
    dict_protein_ids_to_iso_from_and_to_2 = {}
    query = '''MATCH (p:%s]-(r:ReferenceEntity_reactome)<-[:interactor]-(n:Interaction_reactome)-[:interactor]->(s:ReferenceEntity_reactome)-[:%s RETURN p.identifier, r.schemaClass, r.variantIdentifier, q.identifier, s.schemaClass, s.variantIdentifier, n.accession, n.pubmed;'''
    # query = '''MATCH (p:Protein)-[:equal_to_reactome_uniprot]-(r:ReferenceEntity_reactome)<-[:interactor]-(n:Interaction_reactome)-[:interactor]->(s:ReferenceEntity_reactome)-[:equal_to_reactome_uniprot]-(q:Protein) RETURN r.identifier, r.schemaClass, r.variantIdentifier, s.identifier, s.schemaClass, s.variantIdentifier, n.accession;'''
    query = query % (label_1, label_2)
    print(query)
    results = graph_database.run(query)
    counter_map_with_id = 0

    for interactor1_rea_id, schemaClass_1, variantIdentifier_1, interactor2_rea_id, schemaClass_2, variantIdentifier_2, accession, pubmed_ids, in results:
        mapped = False
        if schemaClass_1 != "ReferenceIsoform":
            variantIdentifier_1 = ""
        if schemaClass_2 != "ReferenceIsoform":
            variantIdentifier_2 = ""
        if (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1,
            variantIdentifier_2) in dict_identifier_to_resource:
            dict_rela_info = dict_identifier_to_resource[
                (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)]
            accession_list = json.loads(accession)
            interaction_ids = set(accession_list + dict_rela_info['interaction_ids_EBI'])
            if (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1,
                variantIdentifier_2) in dict_protein_ids_to_iso_from_and_to:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                    'interaction_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                        'interaction_ids'].union(
                        interaction_ids)
                dict_protein_ids_to_iso_from_and_to[
                    (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                    'pubmed_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                        'pubmed_ids'].union(
                        pubmed_ids)
            else:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)] = {
                    'interaction_ids': interaction_ids, 'pubmed_ids': set(pubmed_ids)}
            counter_map_with_id += 1
            mapped = True
        elif (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2,
              variantIdentifier_1) in dict_identifier_to_resource:
            dict_rela_info = dict_identifier_to_resource[
                (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)]
            accession_list = json.loads(accession)
            interaction_ids = set(accession_list + dict_rela_info['interaction_ids_EBI'])
            if (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2,
                variantIdentifier_1) in dict_protein_ids_to_iso_from_and_to:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)][
                    'interaction_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)][
                        'interaction_ids'].union(
                        interaction_ids)
                dict_protein_ids_to_iso_from_and_to[
                    (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)]['pubmed_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)][
                        'pubmed_ids'].union(
                        pubmed_ids)
            else:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)] = {
                    'interaction_ids': interaction_ids, 'pubmed_ids': set(pubmed_ids)}
            counter_map_with_id += 1
            mapped = True
        else:
            accession_list = json.loads(accession)
            interaction_ids = set(accession_list)
            if (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2,
                variantIdentifier_1) in dict_protein_ids_to_iso_from_and_to_2:
                dict_protein_ids_to_iso_from_and_to_2[
                    (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)][
                    'interaction_ids'] = \
                    dict_protein_ids_to_iso_from_and_to_2[
                        (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)][
                        'interaction_ids'].union(
                        interaction_ids)
                dict_protein_ids_to_iso_from_and_to_2[
                    (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)]['pubmed_ids'] = \
                    dict_protein_ids_to_iso_from_and_to_2[
                        (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)][
                        'pubmed_ids'].union(
                        pubmed_ids)
            elif (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1,
                  variantIdentifier_2) in dict_protein_ids_to_iso_from_and_to_2:
                dict_protein_ids_to_iso_from_and_to_2[
                    (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                    'interaction_ids'] = \
                    dict_protein_ids_to_iso_from_and_to_2[
                        (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                        'interaction_ids'].union(
                        interaction_ids)
                dict_protein_ids_to_iso_from_and_to_2[
                    (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                    'pubmed_ids'] = \
                    dict_protein_ids_to_iso_from_and_to_2[
                        (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                        'pubmed_ids'].union(
                        pubmed_ids)
            else:
                dict_protein_ids_to_iso_from_and_to_2[
                    (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2, variantIdentifier_1)] = {
                    'interaction_ids': interaction_ids, 'pubmed_ids': set(pubmed_ids)}


def generate_file(csv_mapped):
    for (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1,
         variantIdentifier_2), dict_iso_interaction_ids in dict_protein_ids_to_iso_from_and_to.items():
        # csv_mapped.writerow([interactor1_rea_id, interactor2_rea_id, resource, '|'.join(dict_iso_interaction_ids['interaction_ids']), '|'.join(dict_iso_interaction_ids['iso_from']), '|'.join(dict_iso_interaction_ids['iso_to'])])
        if len(dict_iso_interaction_ids['pubmed_ids']) > 0:
            csv_mapped.writerow(
                [interactor1_rea_id, interactor2_rea_id,
                 pharmebinetutils.resource_add_and_prepare(dict_identifier_to_resource[
                                                               (interactor1_rea_id, interactor2_rea_id,
                                                                variantIdentifier_1, variantIdentifier_2)][
                                                               'resource'], 'Reactome'),
                 '|'.join(dict_iso_interaction_ids['interaction_ids']),
                 '|'.join(dict_iso_interaction_ids['pubmed_ids']), dict_identifier_to_resource[
                     (interactor1_rea_id, interactor2_rea_id, variantIdentifier_1, variantIdentifier_2)][
                     'interaction_id']])


def generate_file_else(csv_not_mapped):
    counter = maximal_id
    for (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2,
         variantIdentifier_1), dict_iso_interaction_ids in dict_protein_ids_to_iso_from_and_to_2.items():
        # csv_not_mapped.writerow([interactor2_rea_id, interactor1_rea_id, '|'.join(dict_iso_interaction_ids['interaction_ids']), '|'.join(dict_iso_interaction_ids['iso_from']), '|'.join(dict_iso_interaction_ids['iso_to']), resource])
        if len(dict_iso_interaction_ids['pubmed_ids']) > 0:
            counter += 1
            csv_not_mapped.writerow(
                [interactor1_rea_id, interactor2_rea_id, '|'.join(dict_iso_interaction_ids['interaction_ids']),
                 variantIdentifier_1, variantIdentifier_2, '|'.join(dict_iso_interaction_ids['pubmed_ids']), counter])


'''
generate connection between mapping interactions of reactome and hetionet and generate new hetionet interaction edges
'''


def create_cypher_file(label_1, label_2, csv_mapped_name, csv_not_mapped_name):
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (a:%s{identifier:line.interactor1_het_id})-[b]->(m:Interaction{identifier:line.interaction_id})-[d]->(c:%s{identifier:line.interactor2_het_id}) SET b.resource = split(line.resource, '|'), b.reactome = "yes", m.resource = split(line.resource, '|'), m.reactome = "yes", m.interaction_ids = split(line.interaction_ids_EBI, "|"), m.pubMed_ids = split(line.pubmed_ids, "|"), d.resource = split(line.resource, '|'), d.reactome = "yes";\n'''
    query = query % (path_of_directory, csv_mapped_name, label_1, label_2)
    # because of a crazy error that I do not what happend with the protein-protein interaction and periodic commit
    if label_2 == label_1 and label_2 == 'Protein':
        query = query[28:]
    cypher_file.write(query)
    # new interactions
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.interactor1_het_id}),(c:%s{identifier:line.interactor2_het_id}) CREATE (d)-[:INTERACTS_PiI{ resource:["Reactome"], reactome:"yes", source:"Reactome",  license:"CC BY 4.0"}]->(:Interaction{interaction_ids: split(line.accession, "|"), iso_of_protein_from:line.iso_from, iso_of_protein_to:line.iso_to, resource:["Reactome"], reactome:"yes", source:"Reactome", pubMed_ids : split(line.pubmed_ids, "|"), license:"CC BY 4.0"})-[:INTERACTS_IiP{ resource:["Reactome"], reactome:"yes", source:"Reactome",  license:"CC BY 4.0"}]->(c);\n'''
    query = query % (path_of_directory, csv_not_mapped_name, label_1, label_2)
    cypher_file.write(query)


def main():
    global csv_mapped, csv_not_mapped, cypher_file
    global path_of_directory, license
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        license = sys.argv[2]
    else:
        sys.exit('need a path and license reactome edge interaction')

    cypher_file = open('output/cypher_drug_edge.cypher', 'a', encoding="utf-8")
    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())
    print('Load all interactions from hetionet into a dictionary')

    load_hetionet_interactions_in()

    print(
        '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

    print(datetime.datetime.now())
    print('Load all reactome interactions from neo4j into a dictionary')

    # 0: query start;   1: query path end    2: label in PharMeBINet;
    # 3: label in PharMeBINet;  4: file name;  5: relationship name
    list_of_combinations = [
        ['Protein)-[:equal_to_reactome_uniprot', 'equal_to_reactome_uniprot]-(q:Protein)', 'Protein', 'Protein',
         'protein_to_protein'],
    ]
    for list_element in list_of_combinations:
        pathlabel_1 = list_element[0]
        pathlabel_2 = list_element[1]
        label_1 = list_element[2]
        label_2 = list_element[3]
        file_name = list_element[4]
        load_reactome_drug_in(pathlabel_1, pathlabel_2)

        print(
            '__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')

        print(datetime.datetime.now())

        # file for mapped or not mapped identifier
        file_name_not_mapped = 'interactions/not_mapped_interactions_' + file_name + '.tsv'
        file_not_mapped_interactions = open(file_name_not_mapped, 'w', encoding="utf-8")
        csv_not_mapped = csv.writer(file_not_mapped_interactions, delimiter='\t', lineterminator='\n')
        csv_not_mapped.writerow(
            ['interactor1_het_id', 'interactor2_het_id', 'accession', 'iso_from', 'iso_to', 'pubmed_ids',
             'interaction_id'])

        file_name_mapped = 'interactions/mapped_interactions_' + file_name + '.tsv'
        file_mapped_interactions = open(file_name_mapped, 'w', encoding="utf-8")
        csv_mapped = csv.writer(file_mapped_interactions, delimiter='\t', lineterminator='\n')
        csv_mapped.writerow(
            ['interactor1_het_id', 'interactor2_het_id', 'resource', 'interaction_ids_EBI',
             'pubmed_ids', 'interaction_id'])

        print('Generate file mapped_interactions.tsv with properties')

        generate_file(csv_mapped)

        print(
            '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

        print(datetime.datetime.now())

        print('Generate file not_mapped_interactions.tsv with properties')

        generate_file_else(csv_not_mapped)

        print(
            '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

        print(datetime.datetime.now())

        print('Integrate new interactions')

        create_cypher_file(label_1, label_2, file_name_mapped, file_name_not_mapped)

        print(
            '__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')
        print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
