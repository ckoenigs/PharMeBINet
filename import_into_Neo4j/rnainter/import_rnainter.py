import datetime, sys
import pandas as pd

cypher_file = open("output/cypher.cypher", "w", encoding="utf-8")


def cypher_node(filename, label, properties, unique_property):
    """
    Generate cypher query and index for node and add to cypher file.
    :param filename: name of source file
    :param label: e.g. gene, protein_db
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param unique_property: identifier (e.g. diseaseId)
    """

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}import_into_Neo4j/rnainter/{filename}" As line fieldterminator "\\t" '

    query = query_start + 'Create (p:%s_RNAInter{' % (label)
    for x in properties:
        query += x[0:-1] + ':line.' + x + ', '
    # delete last comma
    query = query[:-2] + '});\n'
    cypher_file.write(query)

    query2 = 'Create Constraint On (node:%s_RNAInter) Assert node.%s Is Unique; \n' % (label, unique_property)
    cypher_file.write(query2)
    # write everything in same file


def cypher_edge(filename, label, properties, edge_name):
    """
    Prepre Rna-other node edges and add to cypher file
    :param filename: name of source file
    :param label: list of connecting nodes, e.g. ['variant', 'disease']
    :param properties: columns der Tabelle (auf Leerzeichen achten)
    :param edge_name: specifies how the connection btw. two nodes is called
    """

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}import_into_Neo4j/rnainter/{filename}" As line fieldterminator "\\t" '
    query = query_start + f'Match (p1:rna_RNAInter{{Raw_ID:line.Raw_ID1}}),(p2:{label}_RNAInter{{Raw_ID:line.Raw_ID2}}) Create (p1)-[:{edge_name}{{  '
    for header in properties:
        if header in ['strong', 'weak', 'predict']:
            query += header + ':split(line.' + header + ',"|"), '
        else:
            query += f'{header}:line.{header}, '

    query = query[:-2] + '}]->(p2);\n'
    cypher_file.write(query)


def edges(file, name):
    """
    Prepare file for relationships and generate cypher query
    :param file: string
    :param name: string
    :return:
    """
    file.set_axis(["RNAInterID", "Interactor1", "Category1", "Species1",
                   "Interactor2", "Category2", "Species2", "Raw_ID1",
                   "Raw_ID2", "score", "strong", "weak", "predict"], axis=1, inplace=True)

    edge_set = ("RNAInterID", "Raw_ID1", "Raw_ID2", "Interactor1", "Interactor2", "score", "strong", "weak", "predict")
    edge = file.loc[:, edge_set]

    edge["Raw_ID1"].fillna(edge["Interactor1"], inplace=True)
    edge["Raw_ID2"].fillna(edge["Interactor2"], inplace=True)

    edge = edge.replace(to_replace="//", value="|", regex=True)
    edge = edge.set_index("RNAInterID")
    file_name = "output/rna_" + name + ".tsv"
    edge.to_csv(file_name, sep='\t')
    cypher_edge(file_name, name, ["RNAInterID", "score", "strong", "weak", "predict"], "associate")


def nodes(file, name):
    """
    Prepare the node information to node files and rna
    :param file: string
    :param name: string
    :return:
    """
    edge_set1 = ("Raw_ID1", "Interactor1", "Category1", "Species1")
    edge_set2 = ("Raw_ID2", "Interactor2", "Category2", "Species2")

    file.set_axis(["RNAInterID", "Interactor1", "Category1", "Species1",
                   "Interactor2", "Category2", "Species2", "Raw_ID1",
                   "Raw_ID2", "score", "strong", "weak", "predict"], axis=1, inplace=True)

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
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        if len(sys.argv) == 3:
            species_condition = True
            species = sys.argv[2]
    else:
        sys.exit('need a path rna_inter')

    d = {"rna": "Download_data_RR.tar.gz", "protein": "Download_data_RP.tar.gz",
         "dna": "Download_data_RD.tar.gz", "compound": "Download_data_RC.tar.gz",
         "histone": "Download_data_RH.tar.gz"}

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
        a = nodes(csv, i)
        rna = pd.concat([rna, a])
        edges(csv, i)

    rna["Raw_ID1"].fillna(rna["Interactor1"], inplace=True)
    rna = rna.drop_duplicates(subset=['Raw_ID1'])
    rna = rna.set_index('Raw_ID1')
    rna.to_csv(file_name_rna, sep='\t')
    print('##################################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
