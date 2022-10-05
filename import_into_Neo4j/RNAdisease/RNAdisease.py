import pandas as pd
import numpy as np
import zipfile
import wget
import csv, sys


# cypher file
cypher_file=open("cypher.cypher","w",encoding="utf-8")


def nodes_edges(file):
    print("########### Start: nodes_edges() ###############")
    rnanodes = {}
    diseasenodes={}
    file = file.replace(np.nan, '')

    for index, row in file.iterrows():
        if row["RNA_Symbol"] not in rnanodes:
            rnanodes[row["RNA_Symbol"]]={}
            rnanodes[row["RNA_Symbol"]]["RNA_Type"]=[row["RNA_Type"]]
        elif row["RNA_Symbol"] in rnanodes and row["RNA_Type"] not in rnanodes[row["RNA_Symbol"]]["RNA_Type"]:
            rnanodes[row["RNA_Symbol"]]["RNA_Type"].append(row["RNA_Type"])

        if row['Disease_Name'] not in diseasenodes:
            diseasenodes[row['Disease_Name']]={}
            diseasenodes[row['Disease_Name']]['DO_ID']=[row['DO_ID']]
            diseasenodes[row['Disease_Name']]['MeSH_ID'] = [row['MeSH_ID']]
            diseasenodes[row['Disease_Name']]['KEGG_disease_ID'] = [row['KEGG_disease_ID']]
        elif row['Disease_Name'] in diseasenodes and row['DO_ID'] not in diseasenodes[row['Disease_Name']]['DO_ID']:
            diseasenodes[row['Disease_Name']]['DO_ID'].append(row['DO_ID'])
            diseasenodes[row['Disease_Name']]['MeSH_ID'].append(row['MeSH_ID'])
            diseasenodes[row['Disease_Name']]['KEGG_disease_ID'].append(['KEGG_disease_ID'])

    file_name_rna = 'output/rna_RNADisease.tsv'
    file_name_disease = 'output/disease_RNADisease.tsv'
    with open(file_name_rna, 'w', newline='',encoding="utf-8") as tsv_file1:
        with open(file_name_disease, 'w', newline='', encoding="utf-8") as tsv_file2:
            writer1,writer2= csv.writer(tsv_file1,delimiter='\t'), csv.writer(tsv_file2,delimiter='\t'),
            writer1.writerow(["RNA_Symbol","RNA_Type"]), writer2.writerow(["Disease_Name","DO_ID",'MeSH_ID','KEGG_disease_ID'])

            for key in rnanodes:
                rna = []
                rna.append(key)
                for i in rnanodes[key].keys():
                    rna.append("|".join(rnanodes[key][i]))
                writer1.writerow(rna)

            for key in diseasenodes:
                disease=[]
                disease.append(key)
                for i in diseasenodes[key].keys():
                    if isinstance(diseasenodes[key][i], list) == True:
                        disease.append("|".join(diseasenodes[key][i]))
                    else:
                        disease.append(diseasenodes[key][i])
                writer2.writerow(disease)


    cypher_node(['RNA_Symbol','RNA_Type'], file_name_rna,'RNA_Symbol', 'rna_RNADisease')
    cypher_node(["Disease_Name","DO_ID",'MeSH_ID','KEGG_disease_ID'], file_name_disease, "Disease_Name", 'disease_RNADisease')

    edges = file[["RNA_Symbol", "Disease_Name", "RDID","PMID","score"]]
    edges.drop_duplicates()
    file_name_edge="output/rna_disease_RNADisease.tsv"
    edges.to_csv(file_name_edge, sep='\t', index=False)
    cypher_edge(file_name_edge, 'rna_RNADisease', 'disease_RNADisease', ["RDID","PMID","score"], 'associate_rna_disease')


    print("########### End: nodes_edges() ###############")

def cypher_node(keys, file_name, unique_identifier, label):
    '''
    generates cypher query to integrate nodes into neo4j
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    '''

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}import_into_Neo4j/RNAdisease/{file_name}" As line fieldterminator "\\t" '
    query = query_start + 'Create (p:%s{'% (label)
    for x in keys:
        if x in ['RNA_Type', "DO_ID",'MeSH_ID','KEGG_disease_ID']:  # properties that are lists must be splitted
            query += x + ':split(line.' + x + ',"|"), '
        else:
            query += x + ':line.' + x + ', '

    query = query[:-2] + '});\n'
    cypher_file.write(query)


    query2 = 'Create Constraint On (node:%s) Assert node.%s Is Unique; \n' % (label, unique_identifier)
    cypher_file.write(query2)

def cypher_edge(file_name, label1, label2, properties, edge_name):
    """
    :param cypher_file: destination file to write the queries to
    :param file_name: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param id_list: the keys that are only for matching (they do not need to be part of the edge-information)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}import_into_Neo4j/RNAdisease/{file_name}" As line fieldterminator "\t"'
    query = query_start + f'Match (p1:{label1}{{RNA_Symbol:line.RNA_Symbol}}),(p2:{label2}{{Disease_Name:line.Disease_Name}}) Create (p1)-[:{edge_name}{{'
    for header in properties:
            query += f'{header}:line.{header}, '
    query = query[:-2]+'}]->(p2);\n'
    cypher_file.write(query)

def get_data():
    print("########### Start: get_data() ###############")
    '''
    Prepares the RNA-disease experimental data file and saves it as tsv file
    http://www.rnadisease.org/
    file: RNADiseasev4.0_RNA-disease_experiment_all.xlsx
    - RDID:             unique identifier for each entry in RNADisease database
    - RNA symbol:       official RNA symbol
    - RNA type:         category of RNA
    - Disease name:     official disease name
    - DO ID:            disease ID in Disease Ontology
    - MeSH ID:          disease ID in MeSH
    - KEGG disease ID:  disease ID in KEGG
    - Species:          organism
    - PMID:             the PubMed ID of all references
    - Score:            the confidence score of the current entry
    '''

    file_name='data/RNADiseasev4.0_RNA-disease_experiment_all.zip'

    try:
        archive = zipfile.ZipFile(file_name, 'r')
        print('File does exist')
    except FileNotFoundError:
        print('File does not exist')
        url = "http://www.rnadisease.org/static/download/RNADiseasev4.0_RNA-disease_experiment_all.zip"
        wget.download(url, out='data/')
        archive = zipfile.ZipFile(file_name, 'r')
        
    file = archive.open('RNADiseasev4.0_RNA-disease_experiment_all.xlsx')
    df = pd.read_excel(file)

    df.rename(columns={'DO ID': 'DO_ID', 'RNA Symbol': 'RNA_Symbol', 'RNA Type': 'RNA_Type',
                             'Disease Name': 'Disease_Name',
                             'MeSH ID': 'MeSH_ID', 'KEGG disease ID': 'KEGG_disease_ID', 'specise': 'species'},inplace=True)

    df = df.drop(df[df.species != "Homo sapiens"].index)
    print("########### End: get_data() ###############")
    return df


def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path RNAdisease')
    df = get_data()
    nodes_edges(df)
if __name__ == "__main__":
    # execute only if run as a script
    main()
