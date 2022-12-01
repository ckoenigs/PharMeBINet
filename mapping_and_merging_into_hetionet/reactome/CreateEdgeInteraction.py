
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


# dictionary with pharmebinet interactions between proteins with interactor1_id as key and value interactor2_id
dict_interactions_pharmebinet = {}

# dictionary from identifiers to resource_1
dict_identifiers_to_resource = {}

# dictionary of all properties of egde
dict_rela_info = {}

# dictionary from protein identifier to iso_from and iso_to
dict_protein_ids_to_iso_from_and_to = {}

# dictionary from protein identifier to iso_form and iso_to for created interactions
dict_protein_ids_to_iso_from_and_to_2 = {}


'''
load in all Interactions from pharmebinet into dictionary
'''


def load_pharmebinet_interactions_in():
    global maximal_id
    query = '''MATCH (n:Compound)-[r:INTERACTS_CiC]->(m:Compound) RETURN n.identifier, m.identifier, r.resource;'''
    results = graph_database.run(query)

    for compound1, compound2, resource, in results:
        dict_identifiers_to_resource[
            (compound1, compound2)] =  resource


'''
load all reactome interactions and check if they are in pharmebinet or not
'''

set_pair = set()


def load_reactome_drug_in(label_1, label_2):
    global highest_identifier, dict_protein_ids_to_iso_from_and_to, dict_protein_ids_to_iso_from_and_to_2
    dict_protein_ids_to_iso_from_and_to = {}
    dict_protein_ids_to_iso_from_and_to_2 = {}
    query = '''MATCH (p:%s]-(r:ReferenceEntity_reactome)<-[:interactor]-(n:Interaction_reactome)-[:interactor]->(s:ReferenceEntity_reactome)-[:%s RETURN p.identifier, r.identifier, r.schemaClass, r.variantIdentifier, q.identifier, s.schemaClass, s.variantIdentifier, n.accession, n.pubmed;'''
    query = query % (label_1, label_2)
    print(query)
    results = graph_database.run(query)
    counter_map_with_id = 0

    for interactor1_rea_id, reactome_identifier, schemaClass_1, variantIdentifier_1, interactor2_rea_id, schemaClass_2, variantIdentifier_2, accession, pubmed_ids, in results:
        mapped = False
        if schemaClass_1 != "ReferenceIsoform":
            variantIdentifier_1 = ""
        if schemaClass_2 != "ReferenceIsoform":
            variantIdentifier_2 = ""
        if (interactor1_rea_id, interactor2_rea_id) in dict_identifiers_to_resource:
            interaction_ids = json.loads(accession)
            if (interactor1_rea_id, interactor2_rea_id) in dict_protein_ids_to_iso_from_and_to:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor1_rea_id, interactor2_rea_id)][
                    'interaction_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor1_rea_id, interactor2_rea_id)][
                        'interaction_ids'].union(
                        interaction_ids)
                dict_protein_ids_to_iso_from_and_to[
                    (interactor1_rea_id, interactor2_rea_id)][
                    'pubmed_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor1_rea_id, interactor2_rea_id)][
                        'pubmed_ids'].union(
                        pubmed_ids)
            else:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor1_rea_id, interactor2_rea_id)] = {
                    'interaction_ids': interaction_ids, 'pubmed_ids': set(pubmed_ids)}
            counter_map_with_id += 1
            mapped = True
        elif (interactor2_rea_id, interactor1_rea_id) in dict_identifiers_to_resource:
            interaction_ids = json.loads(accession)
            if (interactor2_rea_id, interactor1_rea_id) in dict_protein_ids_to_iso_from_and_to:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor2_rea_id, interactor1_rea_id)][
                    'interaction_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor2_rea_id, interactor1_rea_id)][
                        'interaction_ids'].union(
                        interaction_ids)
                dict_protein_ids_to_iso_from_and_to[
                    (interactor2_rea_id, interactor1_rea_id)]['pubmed_ids'] = \
                    dict_protein_ids_to_iso_from_and_to[
                        (interactor2_rea_id, interactor1_rea_id)][
                        'pubmed_ids'].union(
                        pubmed_ids)
            else:
                dict_protein_ids_to_iso_from_and_to[
                    (interactor2_rea_id, interactor1_rea_id)] = {
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
                    'interaction_ids': interaction_ids, 'pubmed_ids': set(pubmed_ids), 'reactome_identifier':reactome_identifier}


def generate_file(csv_mapped):
    for (interactor1_rea_id, interactor2_rea_id), dict_iso_interaction_ids in dict_protein_ids_to_iso_from_and_to.items():
        # csv_mapped.writerow([interactor1_rea_id, interactor2_rea_id, resource, '|'.join(dict_iso_interaction_ids['interaction_ids']), '|'.join(dict_iso_interaction_ids['iso_from']), '|'.join(dict_iso_interaction_ids['iso_to'])])
        if len(dict_iso_interaction_ids['pubmed_ids']) > 0:
            csv_mapped.writerow(
                [interactor1_rea_id, interactor2_rea_id,
                 pharmebinetutils.resource_add_and_prepare(dict_identifiers_to_resource[
                                                               (interactor1_rea_id, interactor2_rea_id)][
                                                               'resource'], 'Reactome'),
                 '|'.join(dict_iso_interaction_ids['interaction_ids']),
                 '|'.join(dict_iso_interaction_ids['pubmed_ids'])])

def generate_file_else(csv_not_mapped):
    for (interactor2_rea_id, interactor1_rea_id, variantIdentifier_2,
         variantIdentifier_1), dict_iso_interaction_ids in dict_protein_ids_to_iso_from_and_to_2.items():
        # csv_not_mapped.writerow([interactor2_rea_id, interactor1_rea_id, '|'.join(dict_iso_interaction_ids['interaction_ids']), '|'.join(dict_iso_interaction_ids['iso_from']), '|'.join(dict_iso_interaction_ids['iso_to']), resource])
        if len(dict_iso_interaction_ids['pubmed_ids']) > 0:
            csv_not_mapped.writerow(
                [interactor1_rea_id, interactor2_rea_id, '|'.join(dict_iso_interaction_ids['interaction_ids']),
                 variantIdentifier_1, variantIdentifier_2, '|'.join(dict_iso_interaction_ids['pubmed_ids']), dict_iso_interaction_ids['reactome_identifier']])


'''
generate connection between mapping interactions of reactome and pharmebinet and generate new pharmebinet interaction edges
'''


def create_cypher_file(label_1, label_2, csv_not_mapped_name, csv_mapped_name,rela_label):
    # new interactions
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (d:%s{identifier:line.interactor1_het_id}),(c:%s{identifier:line.interactor2_het_id}) CREATE (d)-[:%s{ resource:["Reactome"], reactome:"yes", source:"Reactome", license:"CC BY 4.0", url:"https://reactome.org/content/detail/interactor/"+ line.reactome_identifier,  interaction_ids : split(line.accession, "|"),pubMed_ids : split(line.pubmed_ids, "|"),iso_of_protein_from : line.iso_from, iso_of_protein_to : line.iso_to}]->(c);\n'''
    query = query % (path_of_directory, csv_not_mapped_name, label_1, label_2, rela_label)
    cypher_file.write(query)
    query = '''Using Periodic Commit 10000 LOAD CSV  WITH HEADERS FROM "file:%smapping_and_merging_into_hetionet/reactome/%s" As line FIELDTERMINATOR "\\t" MATCH (a:%s{identifier:line.interactor1_het_id})-[m:%s]->(c:%s{identifier:line.interactor2_het_id}) SET m.resource = split(line.resource, '|'), m.reactome = "yes", m.interaction_ids = split(line.interaction_ids_EBI, "|"), m.pubMed_ids = split(line.pubmed_ids, "|");\n'''
    query = query % (path_of_directory, csv_mapped_name, label_1, label_2, rela_label)
    # because of a crazy error that I do not what happend with the protein-protein interaction and periodic commit
    # if label_2 == label_1 and label_2 == 'Protein':
    #     query = query[28:]
    cypher_file.write(query)

def main():
    global  csv_not_mapped, cypher_file
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
    print('Load all reactome interactions from neo4j into a dictionary')

    # 0: query start;   1: query path end    2: label in PharMeBINet;
    # 3: label in PharMeBINet;  4: file name;  5: relationship name
    list_of_combinations = [
        ['Chemical)-[:equal_to_reactome_drug', 'equal_to_reactome_uniprot]-(q:Protein)', 'Chemical', 'Protein',
         'chemical_to_protein', 'INTERACTS_CHiP'],
        ['Chemical)-[:equal_to_reactome_drug', 'equal_to_reactome_drug]-(q:Chemical)', 'Chemical', 'Chemical',
         'chemical_to_chemical', 'INTERACTS_CiC']
    ]
    for list_element in list_of_combinations:
        pathlabel_1 = list_element[0]
        pathlabel_2 = list_element[1]
        label_1 = list_element[2]
        label_2 = list_element[3]
        file_name = list_element[4]
        rela_label = list_element[5]
        load_reactome_drug_in(pathlabel_1, pathlabel_2)

        print(
            '__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')

        print(datetime.datetime.now())

        # file for mapped or not mapped identifier
        file_name_not_mapped = 'interactions/not_mapped_interactions_' + file_name + '.tsv'
        file_not_mapped_interactions = open(file_name_not_mapped, 'w', encoding="utf-8")
        csv_not_mapped = csv.writer(file_not_mapped_interactions, delimiter='\t', lineterminator='\n')
        csv_not_mapped.writerow(
            ['interactor1_het_id', 'interactor2_het_id', 'accession', 'iso_from', 'iso_to', 'pubmed_ids', 'reactome_identifier'])

        file_name_mapped = 'interactions/mapped_interactions_' + file_name + '.tsv'
        file_mapped_interactions = open(file_name_mapped, 'w', encoding="utf-8")
        csv_mapped = csv.writer(file_mapped_interactions, delimiter='\t', lineterminator='\n')
        csv_mapped.writerow(
            ['interactor1_het_id', 'interactor2_het_id', 'resource', 'interaction_ids_EBI',
             'pubmed_ids'])

        print(
            '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

        print(datetime.datetime.now())

        print('Generate file not_mapped_interactions.tsv with properties')

        generate_file_else(csv_not_mapped)



        print(
            '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

        print(datetime.datetime.now())

        print('Generate file not_mapped_interactions.tsv with properties')



        generate_file(csv_mapped)

        print(
            '°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°')

        print(datetime.datetime.now())

        print('Integrate new interactions')

        create_cypher_file(label_1, label_2,  file_name_not_mapped, file_name_mapped, rela_label)

        print(
            '__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-.__.-°-._')
        print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
