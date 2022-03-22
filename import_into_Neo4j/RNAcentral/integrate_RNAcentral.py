import csv
import pandas as pd
import json
import gzip, sys
import datetime

# cypher file
cypher_file=open("cypher.cypher","w",encoding="utf-8")

def genome_coordinates():
    '''
    Prepares the homo sapiens genome coordinates file and saves it as tsv file
    https://rnacentral.org/
    file: homo_sapiens.GRCh38.bed.gz
    chromName       - name of the chromosome or scaffold
    chromStart      - Start position of the feature in standard chromosomal coordinates (i.e. first base is 0)
    chromEnd        - End position of the feature in standard chromosomal coordinates
    name            - A score between 0 and 1000
    score           - RNACentralID
    strand          - Defines the strand. Either "." (=no strand) or "+" or "-".
    thickStart      - coordinate at which to start drawing the feature as a solid rectangle (for example, the start codon in gene displays).
                      When there is no thick part, thickStart and thickEnd are usually set to the chromStart position.
    thickEnd        - coordinate at which to stop drawing the feature as a solid rectangle
    itemRgb         - an RGB colour value (e.g. 0,0,255).
    blockCount      - The number of blocks (exons) within the feature
    blockSizes      - A comma-separated list of the block sizes
    blockStarts     - the start coordinate of each sub-element
    -               - no information
    type            - type of the feature
    databases       - Databases in which the feature occurs
    '''

    print("########### Start: genome_coordinates() ###############")
    file = pd.read_csv(path+'homo_sapiens.GRCh38.bed.gz', compression='gzip', sep='\t')
    file.set_axis(["chromName", "chromStart", "chromEnd", "rnacentral_id",
                   "score", "strand", "thickStart", "thickEnd",
                   "itemRgb", "blockCount", "blockSizes", "blockStarts", "-", "type", "databases"], axis=1,
                  inplace=True)
    del file['-']
    file = file.replace(",", "|", regex=True)
    file.to_csv("homo_sapiens_RNACentral.tsv", sep='\t', index=False)
    print("########### End: genome_coordinates() ###############")


def homo_json():
    '''
    Prepares all json files, merges them with the genome coordinates file and saves it as tsv file
    json files:
    rnacentral_id    - RNACentralID
    description      - description of the feature
    sequence         - sequence of the feature
    md5              - MD5 hash value of uppercase DNA corresponding to RNAcentral sequence
    rna_type         - type of the feature
    taxon_id         - identifer for a taxon in the Taxonomy Database by the NCBI
    xrefs            - []
    '''
    #
    print("########### Start: homo_json() ###############")
    numbers = [100001,300001,500001,600001,
               1000001,1100001,1300001,1400001,1500001,1600001,1700001,
               2200001,2300001,2500001,2600001,2800001,2900001,3400001]

    all_json = pd.DataFrame()

    i=0

    while (i<18):
        url = "http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/json/ensembl-xref-" + str(numbers[i]) + "-" + str(numbers[i]+ 100000) + ".json"
        file_json = pd.read_json(url)
        df_homo = file_json['taxon_id'] == 9606         # filter according to the NCBI taxonomy id for Homo sapiens (9606)
        df_homo = file_json[df_homo]
        del df_homo['taxon_id'], df_homo['rna_type']
        all_json=all_json.append(df_homo)
        i+=1
        print(i, len(all_json))

    print(datetime.datetime.now(),'first json files')
    i = 3900001
    while (i <= 36200001):
        url = "http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/json/ensembl-xref-" + str(i) + "-" + str(i + 100000) + ".json"
        file_json = pd.read_json(url)
        df_homo = file_json['taxon_id'] == 9606         # filter according to the NCBI taxonomy id for Homo sapiens (9606)
        df_homo = file_json[df_homo]
        del df_homo['taxon_id'], df_homo['rna_type']
        all_json=all_json.append(df_homo)

        i+=100000
        print(i, len(all_json))
        if (i-1)%1000000==0:
            print(datetime.datetime.now())
    print(datetime.datetime.now(), 'second json files')

    url = "http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/json/ensembl-xref-36300001-36366056.json"
    file_json = pd.read_json(url)
    df_homo = file_json['taxon_id'] == 9606             # filter according to the NCBI taxonomy id for Homo sapiens (9606)
    df_homo = file_json[df_homo]
    del df_homo['taxon_id'], df_homo['rna_type']
    all_json=all_json.append(df_homo)

    # Merging the genome coordinates dataframe and the json dataframe together into one by aligning the rows from each based on the common attribute RNACentralID
    # The “outer” merge combines all the rows for left and right dataframes with NaN when there are no matched values in the rows.
    file_coordinates = pd.read_csv("homo_sapiens_RNACentral.tsv", sep='\t')
    file_coordinates = file_coordinates.merge(all_json, how='outer')

    file_coordinates.to_csv('homo_sapiens_coord_json.tsv', sep='\t')

    print("########### End: json() ###############")

def id_mapping():
    '''
    Prepares the id mapping file by saving the relevant information into a dictionary
    file: id_mapping.tsv.gz - RNAcentral id, corresponding external id, NCBI taxon id, RNA type (according to INSDC classification), gene name
    :return dictionary
    '''

    print("########### Start: id_mapping() ###############")
    d = {}

    with gzip.open(path+'id_mapping.tsv.gz','rt') as tsv_datei:
        reader = csv.reader(tsv_datei, delimiter='\t')
        for row in reader:
            if (row[3] == "9606" and (row[0]+'_9606' in d) == False):
                d[row[0]+'_9606'] = {}
                d[row[0]+'_9606']['geneName'] = row[5]

                if (row[2].startswith(row[1]) == True):
                    d[row[0]+'_9606']['xrefs'] = row[2]
                else:
                    d[row[0]+'_9606']['xrefs'] = row[1] + ":" + row[2]

            elif (row[3] == "9606" and (row[0]+'_9606' in d) == True):
                if (row[2].startswith(row[1]) == True):
                    d[row[0]+'_9606']['xrefs'] = d[row[0]+'_9606']['xrefs'] + "|" + row[2]
                else:
                    d[row[0]+'_9606']['xrefs'] = d[row[0]+'_9606']['xrefs'] + "|" + row[1] + ":" + row[2]

    print("########### End: id_mapping() ###############")

    return(d)

def complete_dictionary(d_map):
    print("########### Start: complete_dictionary() ###############")
    df = pd.read_csv('homo_sapiens_coord_json.tsv', sep='\t')

    # generates a final dictionary
    d = {}
    names = ['score', 'itemRgb',  'type', 'databases','description', 'sequence', 'md5',
             'chromName','chromStart','chromEnd', 'strand', 'thickStart',
             'thickEnd', 'blockCount', 'blockSizes','blockStarts']

    global_i=1

    for index, row in df.iterrows():
        if ((row['rnacentral_id'] in d) == False):
            d[row['rnacentral_id']] = {}

            if (pd.isna(row["chromStart"]) == False):
                d[row['rnacentral_id']][global_i] = {}

            for i in range(0, 16):
                if(pd.isna(row[names[i]]) == False and i <7):
                    d[row['rnacentral_id']][names[i]] = row[names[i]]
                elif(pd.isna(row[names[i]]) == False and i >=7):
                    d[row['rnacentral_id']][global_i][names[i]] = row[names[i]]

            if (row['rnacentral_id'] in d_map.keys()):
                d[row['rnacentral_id']]['geneName'] = d_map[row['rnacentral_id']]['geneName']
                d[row['rnacentral_id']]['xrefs'] = d_map[row['rnacentral_id']]['xrefs']

            global_i += 1

        else:
            d[row['rnacentral_id']][global_i] = {}

            for i in range(7, 16):
                if (pd.isna(row[names[i]]) == False):
                    d[row['rnacentral_id']][global_i][names[i]] = row[names[i]]

            global_i+= 1

    # generate the three tsv files with the information of the nodes and edges
    nodes1 = ['rnacentral_id', 'score', 'itemRgb', 'type', 'databases', 'description', 'sequence', 'md5','geneName', 'xrefs']
    edges = ["rnacentral_id", "id"]
    nodes2 =['id','chromName','chromStart','chromEnd', 'strand', 'thickStart','thickEnd', 'blockCount', 'blockSizes','blockStarts']

    file_name_node1='output/RNACentral_nodes1.tsv'
    file_name_node2='output/RNACentral_nodes2.tsv'
    file_name_edge='output/RNACentral_edges.tsv'
    with open(file_name_node1, 'w',newline='') as tsv_file1:
        with open(file_name_edge, 'w', newline='') as tsv_file2:
            with open(file_name_node2, 'w', newline='') as tsv_file3:
                writer1,writer2, writer3 = csv.writer(tsv_file1),csv.writer(tsv_file2), csv.writer(tsv_file3)
                writer1.writerow(nodes1), writer2.writerow(edges), writer3.writerow(nodes2)

                for key in d:
                    l1=[]
                    l1.append(key)
                    for i in nodes1:
                        if i in d[key].keys() :
                            l1.append(d[key][i])
                        elif i != nodes1[0]:
                            l1.append('')
                    writer1.writerow(l1)

                    for i in list(filter(lambda e: isinstance(e, int), list(d[key]))):
                        l2, l3 =[],[]
                        l2.append(key), l2.append(i), writer2.writerow(l2)
                        l3.append(i)
                        for j in nodes2:
                            if j in d[key][i].keys():
                                l3.append(d[key][i][j])
                            elif j != nodes2[0]:
                                l3.append('')
                        writer3.writerow(l3)

    tsv_file1.close()
    tsv_file2.close()
    tsv_file3.close()

    cypher_node(nodes1, file_name_node1, "rna1", 'rnacentral_id')
    cypher_node(nodes2, file_name_node2, "rna2", 'id')

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}master_database_change/import_into_Neo4j/RNAcentral/{file_name_edge}" As line fieldterminator "," '
    query = query_start + f'Match (p1:rna1_RNACentral{{rnacentral_id:line.rnacentral_id}}),(p2:rna2_RNACentral{{id:line.id}}) Create (p1)-[:associate{{  '
    query = query[:-2]+'}]->(p2);\n'
    cypher_file.write(query)

    print("########### End: complete_dictionary() ###############")

def cypher_node(keys, file_name, label, unique_identifier):
    '''
    generates cypher query to integrate nodes into neo4j
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    '''

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}master_database_change/import_into_Neo4j/RNAcentral/{file_name}" As line fieldterminator "," '
    query = query_start + 'Create (p:%s_RNACentral{' % (label)
    for x in keys:
        if x in ['blockSizes','blockStarts','itemRgb','xrefs','databases']:  # properties that are lists must be splitted
            query += x + ':split(line.' + x + ',"|"), '
        else:
            query += x + ':line.' + x + ', '

    query = query[:-2] + '});\n'
    cypher_file.write(query)

    query2 = 'Create Constraint On (node:%s_RNACentral) Assert node.%s Is Unique; \n' % (label, unique_identifier)
    cypher_file.write(query2)

path='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/RNAcentral/'

def main():
    global path_of_directory
    path_of_directory = ""
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnaCentral')


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('genome coordination')
    genome_coordinates()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('json')
    homo_json()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('id mapping file')
    d_map = id_mapping()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('complete dictionary')
    complete_dictionary(d_map)


if __name__ == "__main__":
    # execute only if run as a script
    main()
