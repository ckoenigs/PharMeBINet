import csv, sys, datetime
import pandas as pd
import gzip
import os
import urllib.request

sys.path.append("../..")
import pharmebinetutils


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
    file = pd.read_csv(path + 'homo_sapiens.GRCh38.bed.gz', compression='gzip', sep='\t')
    file = file.set_axis(["chromName", "chromStart", "chromEnd", "rnacentral_id",
                          "score", "strand", "thickStart", "thickEnd",
                          "itemRgb", "blockCount", "blockSizes", "blockStarts", "-", "type", "databases"], axis=1,
                         copy=True)
    del file['-']
    file = file.replace(",", "|", regex=True)
    file.to_csv("output/homo_sapiens_RNACentral.tsv", sep='\t', index=False)
    print("########### End: genome_coordinates() ###############")


def get_json():
    try:
        from BeautifulSoup import BeautifulSoup
    except ImportError:
        from bs4 import BeautifulSoup

    def get_website_source(url: str) -> str:
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/35.0.1916.47 Safari/537.36'
        }
        request = urllib.request.Request(url, headers=request_headers)
        with urllib.request.urlopen(request) as response:
            # print(response.read())
            return response.read().decode('utf-8')

    print('Download page ')
    source = get_website_source('http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/json/')

    # print(source)
    parsed_html = BeautifulSoup(source, "lxml")

    names_json = []
    for row in parsed_html.find_all('a'):
        href = row['href']
        if 'ensembl-xref-' in href:
            names_json.append(href)

    return names_json


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

    print("########### Start: homo_json() ###############")

    # Creates a folder in which only the human information from each json file is stored.
    try:
        os.makedirs(path + "json_homo")
    except FileExistsError:
        pass

    all_json = pd.DataFrame()
    names_json = get_json()

    for i in names_json:
        filepath = path + "json_homo/" + str(i) + ".tsv"
        print(i)
        json = json_url(i, filepath)
        all_json = pd.concat([all_json, json])

    # Merging the genome coordinates dataframe and the json dataframe together into one by aligning the rows from each based on the common attribute RNACentralID
    # The “outer” merge combines all the rows for left and right dataframes with NaN when there are no matched values in the rows.
    file_coordinates = pd.read_csv("output/homo_sapiens_RNACentral.tsv", sep='\t')
    file_coordinates = file_coordinates.merge(all_json, how='outer')

    file_coordinates.to_csv('output/homo_sapiens_coord_json.tsv', sep='\t')

    print("########### End: homo_json() ###############")


def json_url(name_json, filepath):
    try:
        file_homo = pd.read_csv(filepath, sep='\t')
    except FileNotFoundError:
        print('File does not exist')
        url = "http://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/json/" + str(name_json)
        file_json = pd.read_json(url)
        file_homo = file_json['taxon_id'] == 9606  # filter according to the NCBI taxonomy id for Homo sapiens (9606)
        file_homo = file_json[file_homo]
        del file_homo['taxon_id'], file_homo['rna_type']
        file_homo.to_csv(filepath, sep='\t', index=False)
    return file_homo


def id_mapping():
    '''
    Prepares the id mapping file by saving the relevant information into a dictionary
    file: id_mapping.tsv.gz -
    0: RNAcentral id,
    1: database
    2: corresponding external id,
    3: NCBI taxon id,
    4: RNA type (according to INSDC classification),
    5: gene name
    :return dictionary
    '''

    print("########### Start: id_mapping() ###############")
    d = {}

    with gzip.open(path + 'id_mapping.tsv.gz', 'rt') as tsv_datei:
        reader = csv.reader(tsv_datei, delimiter='\t')
        for row in reader:
            if row[3] == "9606" and row[0] + '_9606' not in d:
                d[row[0] + '_9606'] = {}
                d[row[0] + '_9606']['geneName'] = set([row[5]]) if row[5] != '' else set()
                d[row[0] + '_9606']["type1"] = row[4]

                xref = row[2]
                xref = xref.replace(":" + row[0] + '_9606', "")
                xref = xref.replace(row[1] + ":", "")
                d[row[0] + '_9606']['xrefs'] = row[1] + ":" + xref

            elif row[3] == "9606" and row[0] + '_9606' in d:
                if row[5] != '':
                    d[row[0] + '_9606']['geneName'].add(row[5])
                d[row[0] + '_9606']["type1"] = d[row[0] + '_9606']["type1"] + '|' + row[4] if row[4] != \
                                                                                              d[row[0] + '_9606'][
                                                                                                  "type1"] else \
                    d[row[0] + '_9606']["type1"]
                xref = row[2]
                xref = xref.replace(":" + row[0] + '_9606', "")
                xref = xref.replace(row[1] + ":", "")
                d[row[0] + '_9606']['xrefs'] = d[row[0] + '_9606']['xrefs'] + "|" + row[1] + ":" + xref

    print("########### End: id_mapping() ###############")

    return (d)


def complete_dictionary(d_map):
    print("########### Start: complete_dictionary() ###############", datetime.datetime.now())
    df = pd.read_csv('output/homo_sapiens_coord_json.tsv', sep='\t')

    # generates a final dictionary
    d = {}
    names = ['score', 'itemRgb', 'type', 'databases', 'description', 'sequence', 'md5',
             'chromName', 'chromStart', 'chromEnd', 'strand', 'thickStart',
             'thickEnd', 'blockCount', 'blockSizes', 'blockStarts']

    global_i = 1

    for index, row in df.iterrows():
        if ((row['rnacentral_id'] in d) == False):
            d[row['rnacentral_id']] = {}

            if (pd.isna(row["chromStart"]) == False):
                d[row['rnacentral_id']][global_i] = {}

            for i in range(0, 16):
                if (pd.isna(row[names[i]]) == False and i < 7):
                    d[row['rnacentral_id']][names[i]] = row[names[i]]
                elif (pd.isna(row[names[i]]) == False and i >= 7):
                    d[row['rnacentral_id']][global_i][names[i]] = row[names[i]]

            if (row['rnacentral_id'] in d_map.keys()):
                d[row['rnacentral_id']]['geneName'] = "|".join(d_map[row['rnacentral_id']]['geneName'])
                d[row['rnacentral_id']]['xrefs'] = d_map[row['rnacentral_id']]['xrefs']

            global_i += 1

        else:
            d[row['rnacentral_id']][global_i] = {}

            for i in range(7, 16):
                if (pd.isna(row[names[i]]) == False):
                    d[row['rnacentral_id']][global_i][names[i]] = row[names[i]]

            global_i += 1

    # generate the three tsv files with the information of the nodes and edges
    nodes1 = ['rnacentral_id', 'score', 'itemRgb', 'type', 'databases', 'description', 'sequence', 'md5', 'geneName',
              'xrefs']
    edges = ["rnacentral_id", "id"]
    nodes2 = ['id', 'chromName', 'chromStart', 'chromEnd', 'strand', 'thickStart', 'thickEnd', 'blockCount',
              'blockSizes', 'blockStarts']

    file_name_node1 = 'output/RNACentral_nodes1.tsv'
    file_name_node2 = 'output/RNACentral_nodes2.tsv'
    file_name_edge = 'output/RNACentral_edges.tsv'
    with open(file_name_node1, 'w', newline='') as tsv_file1:
        with open(file_name_edge, 'w', newline='') as tsv_file2:
            with open(file_name_node2, 'w', newline='') as tsv_file3:
                writer1, writer2, writer3 = csv.writer(tsv_file1, delimiter='\t'), csv.writer(tsv_file2,
                                                                                              delimiter='\t'), csv.writer(
                    tsv_file3, delimiter='\t')
                writer1.writerow(nodes1), writer2.writerow(edges), writer3.writerow(nodes2)

                for key in d:
                    l1 = []
                    l1.append(key)
                    for i in nodes1:
                        if i in d[key].keys():
                            l1.append(d[key][i])
                        elif i != nodes1[0]:
                            l1.append('')
                    writer1.writerow(l1)

                    for i in list(filter(lambda e: isinstance(e, int), list(d[key]))):
                        l2, l3 = [], []
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

    # cypher file
    cypher_file_edge = open("cypher_edge.cypher", "w", encoding="utf-8")

    query = f'Match (p1:rna1_RNACentral{{rnacentral_id:line.rnacentral_id}}),(p2:rna2_RNACentral{{id:line.id}}) Create (p1)-[:associate{{  '
    query = query[:-2] + '}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/RNAcentral/{file_name_edge}',
                                              query)
    cypher_file_edge.write(query)

    cypher_file_edge.close()

    print("########### End: complete_dictionary() ###############", datetime.datetime.now())


# cypher file
cypher_file = open("cypher.cypher", "w", encoding="utf-8")


def cypher_node(keys, file_name, label, unique_identifier):
    '''
    generates cypher query to integrate nodes into neo4j
    :param keys: list strings
    :param file_name: string
    :param label: string
    :param unique_identifier: string
    '''

    query = 'Create (p:%s_RNACentral{' % (label)
    for x in keys:
        if x in ['blockSizes', 'blockStarts', 'itemRgb', 'xrefs', 'databases',
                 'geneName']:  # properties that are lists must be splitted
            query += x + ':split(line.' + x + ',"|"), '
        else:
            query += x + ':line.' + x + ', '

    query = query[:-2] + '})'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/RNAcentral/{file_name}',
                                              query)
    cypher_file.write(query)

    cypher_file.write(pharmebinetutils.prepare_index_query(label + '_RNACentral', unique_identifier))


path = '/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/RNAcentral/'


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
