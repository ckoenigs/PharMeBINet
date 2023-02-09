import datetime, sys
import pandas as pd

sys.path.append("../..")
import pharmebinetutils

cypher_file = open("output/cypher.cypher", "w", encoding="utf-8")
cypher_file_edge = open("output/cypher_edge.cypher", "w", encoding="utf-8")


def cypher_node(file_name, label, properties, unique_property):
    """
    Generate cypher query and index for node and add to cypher file.
    :param file_name: name of source file
    :param label: e.g. gene, protein_db
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param unique_property: identifier (e.g. diseaseId)
    """

    query = 'Create (p:%s_RNAInter{' % (label)
    for x in properties:
        query += x[0:-1] + ':line.' + x + ', '
    # delete last comma
    query = query[:-2] + '})'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/rnainter/{file_name}', query)
    cypher_file.write(query)

    cypher_file.write(pharmebinetutils.prepare_index_query(label + '_RNAInter', unique_property))
    # write everything in same file


def cypher_edge(file_name, label, properties, edge_name):
    """
    Prepre Rna-other node edges and add to cypher file
    :param file_name: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query = f'Match (p1:rna_RNAInter{{Raw_ID:line.Raw_ID1}}),(p2:{label}_RNAInter{{Raw_ID:line.Raw_ID2}}) Create (p1)-[:{edge_name}{{  '
    for header in properties:
        if header in ['strong', 'weak', 'predict']:
            query += header + ':split(line.' + header + ',"|"), '
        else:
            query += f'{header}:line.{header}, '

    query = query[:-2] + '}]->(p2)'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/rnainter/{file_name}', query)
    cypher_file_edge.write(query)


def edges(file, name, reduced):
    """
    Prepare file for relationships and generate cypher query
    :param file: string
    :param name: string
    :return:
    """
    file = file.set_axis(["RNAInterID", "Interactor1", "Category1", "Species1",
                          "Interactor2", "Category2", "Species2", "Raw_ID1",
                          "Raw_ID2", "score", "strong", "weak", "predict"], axis=1, copy=True)

    edge_set = ("RNAInterID", "Raw_ID1", "Raw_ID2", "Interactor1", "Interactor2", "score", "strong", "weak", "predict")
    edge = file.loc[:, edge_set]

    edge["Raw_ID1"].fillna(edge["Interactor1"], inplace=True)
    edge["Raw_ID2"].fillna(edge["Interactor2"], inplace=True)

    edge = edge.replace(to_replace="//", value="|", regex=True)
    if reduced:
        edge= edge[edge['score'] >= 0.5]
    edge = edge.set_index("RNAInterID")
    file_name = "output/rna_" + name + ".tsv"
    edge.to_csv(file_name, sep='\t')
    cypher_edge(file_name, name, ["RNAInterID", "score", "strong", "weak", "predict"], "associate")


def nodes(file, name):
    """
    Prepare the node information to node files and rna
    :param file: dataframe
    :param name: string
    :return:
    """
    edge_set1 = ("Raw_ID1", "Interactor1", "Category1", "Species1")
    edge_set2 = ("Raw_ID2", "Interactor2", "Category2", "Species2")

    file = file.set_axis(["RNAInterID", "Interactor1", "Category1", "Species1",
                          "Interactor2", "Category2", "Species2", "Raw_ID1",
                          "Raw_ID2", "score", "strong", "weak", "predict"], axis=1, copy=True)

    if (name == "rna"):
        rna = file.loc[:, edge_set2]
        rna.rename(columns={"Interactor2": "Interactor1", "Category2": "Category1", "Species2": "Species1",
                            "Raw_ID2": "Raw_ID1"}, inplace=True)
        rna = pd.concat([file.loc[:, edge_set1], rna])

    else:
        rna = file.loc[:, edge_set1]

        file = file.loc[:, edge_set2]
        file["Raw_ID2"].fillna(file["Interactor2"], inplace=True)
        file = file.drop_duplicates(subset=['Raw_ID2'])
        file = file.set_index('Raw_ID2')
        file_name = 'output/' + name + ".tsv"
        file.to_csv(file_name, sep='\t')
        cypher_node(file_name, name, ["Raw_ID2", "Interactor2", "Category2", "Species2"], "Raw_ID")

    return (rna)


def main():
    global path_of_directory

    species_condition = False
    # "Homo sapiens"
    species = ''
    #boolean if reduced number of edges should be integrated
    reduced=True
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        if len(sys.argv) == 3:
            species_condition = True
            species = sys.argv[2]
    else:
        sys.exit('need a path rna_inter')

    d = {"rna": "Download_data_RR.tar.gz",
         "dna": "Download_data_RD.tar.gz", "compound": "Download_data_RC.tar.gz",
         "histone": "Download_data_RH.tar.gz", "protein": "Download_data_RP.tar.gz", }

    print('##################################################################################')
    print(datetime.datetime.now())

    # pd.concat(d)

    rna = pd.DataFrame()
    file_name_rna = "output/rna.tsv"
    cypher_node(file_name_rna, "rna", ["Raw_ID1", "Interactor1", "Category1", "Species1"], "Raw_ID")

    for i, file in d.items():
        print(i)
        print(datetime.datetime.now())
        csv = pd.read_csv("data/" + file, compression='gzip', sep='\t', low_memory=False)
        if (species_condition):
            if i not in ['compound', 'histone']:
                csv = csv[(csv.Species1 == species) & (csv.Species2 == species)]
            else:
                csv = csv[(csv.Species1 == species)]
        csv = csv[(csv['Interactor1.Symbol'] != 'Interactor1.Symbol')]
        a = nodes(csv, i)
        rna = pd.concat([rna, a])
        edges(csv, i, reduced)

    rna["Raw_ID1"].fillna(rna["Interactor1"], inplace=True)
    rna = rna.drop_duplicates(subset=['Raw_ID1'])
    rna = rna.set_index('Raw_ID1')
    rna.to_csv(file_name_rna, sep='\t')
    print('##################################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
