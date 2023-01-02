import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global graph_database
    graph_database = create_connection_to_databases.database_connection_neo4j()


# dictionary
dict_protein = {}
dict_protein_to_name = {}
dict_protein_name = {}
dict_mapping_parameter = {}
dict_proteinId_to_resource = {}
dict_protein_uniProt = {}
dict_protein_altIdentifiers = {}
dict_protein_mapping = defaultdict(dict)
dict_target_mapping = defaultdict(dict)


def load_protein_in():
    #query ist ein String
    query = '''MATCH (n:Protein) RETURN n'''
    results = graph_database.run(query)

    #results werden einzeln durchlaufen
    for node, in results:
        identifier = node["identifier"]
        resource = node["resource"]
        prot_name = node["name"]
        uniProt = node["entry_name"]

        xrefs = node['xrefs'] if "xrefs" in node else []

        names = node["synonyms"] if "synonyms" in node else[]
        #xrefs = node["xrefs"] if "xrefs" in node else []
        #im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        dict_protein_to_name[identifier] = prot_name
        dict_proteinId_to_resource[identifier] = resource
        dict_protein_uniProt[uniProt] = identifier



        #name
        for name in names:
            if name not in dict_protein_name:
                dict_protein_name[name] = set()
            dict_protein_name[name].add(identifier)




def load_bioactivity_in():
    query = '''MATCH (n:DC_Bioactivity) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_proteins = set()
    dict_node_to_methode = {}

    for node, node_id, in results:
        accession = node["accession"]
        if accession is not None:
            accession_nbrs = accession.split('|')
            if len(accession_nbrs) == 1:
                accession_nbr = accession_nbrs[0]
            else:
                continue

        protein_name = node["target_name"]
        organism = node["organism"]

        # list of swissprot ids, split at '|', consider only the ones that have a length of 1 in order to
        # prevent mapping to protein subunit
        swissprots = node["swissprot"]
        if swissprots is not None:
            swissprot = swissprots.split('|')
            if len(swissprot) == 1:
                swissProt = swissprot[0]
            else:
                continue

        if accession_nbr in dict_protein_to_name:
            if accession_nbr not in dict_protein_mapping[node_id]:
                dict_protein_mapping[node_id][accession_nbr] = set()
            dict_protein_mapping[node_id][accession_nbr].add('accession')
            mapped_proteins.add(node_id)

        if swissProt in dict_protein_uniProt:

            prot_id = dict_protein_uniProt[swissProt]
            if prot_id not in dict_protein_mapping[node_id]:
                dict_protein_mapping[node_id][prot_id] = set()
                dict_protein_mapping[node_id][prot_id].add('swissprot')
                mapped_proteins.add(node_id)

        if node_id not in mapped_proteins:
            csv_not_mapped.writerow([node_id, accession_nbr, protein_name, organism])

    for node_id in mapped_proteins:
        for protein_id in dict_protein_mapping[node_id]:
            methodes = list(dict_protein_mapping[node_id][protein_id])
            resource = set(dict_proteinId_to_resource[protein_id])
            # print(resource, protein_id)
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped.writerow([node_id, protein_id, resource, methodes])



def load_target_in():
    query = '''MATCH (n:DC_TargetComponent) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_target = set()
    dict_nodes_to_target = {}
    dict_node_to_methode = {}

    for node, node_id, in results:
        accession = node["accession"]
        swissProt = node["swissprot"]
        if accession is not None:
            accession_nbrs = accession.split('|')
        protein_name = node["name"]
        organism = node["organism"]


        for accession_nr in accession_nbrs:
            if accession_nr in dict_protein_to_name:
                if accession_nr not in dict_target_mapping[node_id]:
                    dict_target_mapping[node_id][accession_nr] = set()
                dict_target_mapping[node_id][accession_nr].add('accession')
                mapped_target.add(node_id)


            if swissProt in dict_protein_uniProt:
                prot_id = dict_protein_uniProt[swissProt]
                if prot_id not in dict_target_mapping[node_id]:
                    dict_target_mapping[node_id][prot_id] = set()
                dict_target_mapping[node_id][prot_id].add('swissprot')
                mapped_target.add(node_id)


        if node_id not in mapped_target:
            # print(node_id, umls_cui, sct_id, disease_name)
            csv_not_mapped_target.writerow([node_id, accession_nr, protein_name, organism])

    for node_id in mapped_target:
        for protein_id in dict_target_mapping[node_id]:
            methodes = list(dict_target_mapping[node_id][protein_id])
            resource = set(dict_proteinId_to_resource[protein_id])
            # print(resource, protein_id)
            resource.add('DrugCentral')
            resource = '|'.join(resource)
            csv_mapped_target.writerow([node_id, protein_id, resource, methodes])




# file for mapped or not mapped identifier
#erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_protein = open('protein/not_mapped_protein.tsv', 'w', encoding="utf-8")
#Dateiformat wird gesetzt mit Trenner: Tabulator
csv_not_mapped = csv.writer(file_not_mapped_protein,delimiter='\t', lineterminator='\n')
#Header setzen
csv_not_mapped.writerow(['id', 'accession_number', 'name', 'organismus'])

file_mapped_protein = open('protein/mapped_protein.tsv', 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_protein,delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['node_id','id_pharmebinet', 'resource', 'how_mapped'])

file_not_mapped_target = open('protein/not_mapped_target.tsv', 'w', encoding="utf-8")
csv_not_mapped_target = csv.writer(file_not_mapped_target,delimiter='\t', lineterminator='\n')
csv_not_mapped_target.writerow(['id', 'accession_number', 'name'])

file_mapped_target = open('protein/mapped_target.tsv', 'w', encoding="utf-8")
csv_mapped_target = csv.writer(file_mapped_target,delimiter='\t', lineterminator='\n')
csv_mapped_target.writerow(['node_id','id_pharmebinet', 'resource', 'how_mapped'])



def generate_cypher_file(file_nameProtein, file_nameTarget):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')


    query_Protein = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/drugcentral/protein/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:DC_Bioactivity), (c:Protein{identifier:line.id_pharmebinet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_Bioactivity_drugcentral{how_mapped:line.how_mapped}]->(n); \n'''
    query_Protein = query_Protein % (path_of_directory, file_nameProtein)
    cypher_file.write(query_Protein)

    query_Target = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smapping_and_merging_into_hetionet/drugcentral/protein/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:DC_TargetComponent), (c:Protein{identifier:line.id_pharmebinet}) Where ID(n)= ToInteger(line.node_id)  Set c.drugcentral='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_TargetComponent_drugcentral{how_mapped:line.how_mapped}]->(n); \n'''
    query_Target = query_Target % (path_of_directory,file_nameTarget)
    cypher_file.write(query_Target)

    cypher_file.close()



def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral protein')
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()
    print("load protein in")
    load_protein_in()
    print("load biodiversity")
    load_bioactivity_in()

    print("load target component in")
    load_target_in()

    print('###########################################################################################################################')

    generate_cypher_file("mapped_protein.tsv", "mapped_target.tsv")


    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
