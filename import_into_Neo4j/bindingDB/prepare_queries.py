import pharmebinetutils
import pandas as pd
import numpy as np
import sys

tables = ['ARTICLE', 'ASSAY', 'COBWEB_BDB', 'COMPLEX_COMPONENT', 'DATA_FIT_METH', 'ENTRY',
          'ENTRY_CITATION', 'ENZYME_REACTANT_SET', 'INSTRUMENT', 'ITC_RESULT_A_B_AB', 'ITC_RUN_A_B_AB',
          'KI_RESULT', 'PDB_BDB', 'COMPLEX_AND_NAMES', 'POLYMER_AND_NAMES', 'MONO_STRUCT_NAMES']
tables_index_edges = ['ARTICLE', 'ITC_RESULT_A_B_AB']
kanten = [['ENTRY', 'ENTRY_CITATION', 'ARTICLE'], ['ENTRY', 'ITC_RUN_A_B_AB', 'ITC_RESULT_A_B_AB']]

tables_keys = {'ARTICLE': ['ARTICLEID'], 'ASSAY': ['ENTRYID', 'ASSAYID'], 'COBWEB_BDB': [],
               'COMPLEX_COMPONENT': ['COMPLEXID', 'COMPONENTID'], 'DATA_FIT_METH': ['DATA_FIT_METH_ID'],
               'ENTRY': ['ENTRYID'], 'ENTRY_CITATION': ['ARTICLEID', 'ENTRYID'],
               'ENZYME_REACTANT_SET': ['ENTRYID', 'RECTANT_SET_ID'], 'INSTRUMENT': ['INSTRUMENTID'],
               'ITC_RUN_A_B_AB': ['ENTRYID', 'ITC_RUN_A_B_AB_ID'],
               'ITC_RESULT_A_B_AB': ['ENTRYID', 'ITC_RESULT_A_B_AB_ID'], 'KI_RESULT': ['ENTRYID', 'KI_RESULT_ID'],
               'PDB_BDB': [], 'COMPLEX_AND_NAMES': ['COMPLEXID'], 'POLYMER_AND_NAMES': ['POLYMERID'],
               'MONO_STRUCT_NAMES': ['MONOMERID']}

# Every element of the list is a list of 3 items
# containing the name of the tables with direct connection and the name of the index column(s) in the original tsv file
# note that the index column is always related to the second table.
edges_id = [['MONO_STRUCT_NAMES', 'COBWEB_BDB', 'MONOMER_ID', 'MONOMERID'],
            ['MONO_STRUCT_NAMES', 'COMPLEX_COMPONENT', 'MONOMERID', 'MONOMERID'],
            ['MONO_STRUCT_NAMES', 'ENZYME_REACTANT_SET', 'ENZYME_MONOMERID', 'MONOMERID'],
            ['POLYMER_AND_NAMES', 'ENZYME_REACTANT_SET', 'ENZYME_POLYMERID', 'POLYMERID'],
            ['POLYMER_AND_NAMES', 'COMPLEX_COMPONENT', 'POLYMERID', 'POLYMERID'],
            ['ENZYME_REACTANT_SET', 'COBWEB_BDB', 'REACTANT_SET_ID', 'REACTANT_SET_ID'],
            ['ENTRY', 'ENZYME_REACTANT_SET', 'ENTRYID', 'ENTRYID'],
            ['COMPLEX_AND_NAMES', 'ENZYME_REACTANT_SET', 'ENZYME_COMPLEXID', 'COMPLEXID'],
            ['ENZYME_REACTANT_SET', 'PDB_BDB', 'REACTANT_SET_ID_STR', 'REACTANT_SET_ID'],
            ['ENTRY', 'ASSAY', 'ENTRYID', 'ENTRYID'], ['ASSAY', 'KI_RESULT', 'ASSAYID', 'ASSAYID'],
            ['ENTRY', 'KI_RESULT', 'ENTRYID', 'ENTRYID'],
            ['DATA_FIT_METH', 'KI_RESULT', 'DATA_FIT_METH_ID', 'DATA_FIT_METH_ID'],
            ['INSTRUMENT', 'KI_RESULT', 'INSTRUMENTID', 'INSTRUMENTID'],
            ['DATA_FIT_METH', 'ITC_RESULT_A_B_AB', 'DATA_FIT_METH_ID', 'DATA_FIT_METH_ID'],
            ['INSTRUMENT', 'ITC_RESULT_A_B_AB', 'INSTRUMENTID', 'INSTRUMENTID'],
            ['COMPLEX_AND_NAMES', 'COMPLEX_COMPONENT', 'COMPLEXID', 'COMPLEXID']]


def create_node_queries(tab):
    with open('output/create_nodes.cypher', 'w') as file:
        # Generate and write the queries to the file
        for table in tab:
            if table not in ['COMPLEX_AND_NAMES', 'POLYMER_AND_NAMES', 'MONO_STRUCT_NAMES']:
                query = "create (:" + table + "{"
                file_name = "tsv_from_mysql/" + table + ".tsv"
                for column in get_columns_names_from_tsv(file_name):
                    str_to_add = column.lower() + ":line." + column + ","
                    query += str_to_add
                query = query[:-1]
                query += "})"
                query = pharmebinetutils.get_query_import(file_path,
                                                          "import_into_Neo4j/bindingDB/tsv_from_mysql/" + table + ".tsv", query)
                file.write(query)
            else:
                query = "create (:" + table + "{"
                file_name = "tsv_from_mysql/" + table + ".tsv"
                for column in get_columns_names_from_tsv(file_name):
                    if column == 'NAMES':
                        str_to_add = column.lower() + ':split(line.' + column + ',";"),'
                        query += str_to_add
                    else:
                        str_to_add = column.lower() + ":line." + column + ","
                        query += str_to_add
                query = query[:-1]
                query += "})"
                query = pharmebinetutils.get_query_import(file_path,
                                                          "import_into_Neo4j/bindingDB/tsv_from_mysql/" + table + ".tsv", query)
                file.write(query)
    print("Queries saved to 'create_nodes.cypher' file.")


def create_edge_queries(simple_edges, edges):
    with open('output/create_edges.cypher', 'w') as file:
        for edge in simple_edges:
            if edge[0] == 'ASSAY' and edge[1] == 'KI_RESULT':
                query = "MATCH (n1:ASSAY{assayid:line.ASSAYID, entryid:line.ENTRYID}), (n2:KI_RESULT" \
                        "{assayid:line.ASSAYID, entryid:line.ENTRYID})\n Create (n1) -[:RELATIONSHIP] -> (n2)"
                query = pharmebinetutils.get_query_import(file_path,
                                                          'import_into_Neo4j/bindingDB/idx_tsv/ASSAY-KI_RESULT.tsv',
                                                          query, batch_number=500)
                file.write(query)
            else:
                file_name = edge[0] + '-' + edge[1] + '.tsv'
                if edge[0] == 'ENZYME_REACTANT_SET' and edge[1] == 'PDB_BDB':
                    query = "MATCH (n1:ENZYME_REACTANT_SET), (n2:PDB_BDB{reactant_set_id_str:line.REACTANT_SET_ID_STR}) " \
                            "where n1.reactant_set_id in split(line.REACTANT_SET_ID_STR, ',') " \
                            "\nCreate (n1) -[:RELATIONSHIP] -> (n2)"
                    query = pharmebinetutils.get_query_import(file_path,
                                                              'import_into_Neo4j/bindingDB/idx_tsv/' + file_name, query, batch_number=500)
                    file.write(query)
                else:
                    query = "MATCH (n1:" + edge[0] + "{" + edge[3].lower() + ":line." + edge[2] + "}), "
                    query = query + "(n2:" + edge[1] + "{" + edge[2].lower() + ":line." + edge[2] + "}) \n"
                    query = query + "Create (n1) -[:RELATIONSHIP] -> (n2)"
                    query = pharmebinetutils.get_query_import(file_path,
                                                              'import_into_Neo4j/bindingDB/idx_tsv/' + file_name, query, batch_number=500)
                    file.write(query)
        for edge in edges:
            query = "MATCH (n1:" + edge[0] + "{"
            for key in tables_keys.get(edge[0]):
                query = query + key.lower() + ": line." + key + ","
            query = query[:-1]
            query = query + "}), (n2:" + edge[2] + "{"
            for key in tables_keys.get(edge[2]):
                query = query + key.lower() + ":line." + key + ","
            query = query[:-1]
            query = query + "})\n"
            query = query + "Create (n1) - [: " + edge[1].lower() + "{"
            not_keys_col = []
            for col in get_columns_names_from_tsv("tsv_from_mysql/" + edge[1] + ".tsv"):
                if col not in tables_keys.get(edge[0]) and col not in tables_keys.get(edge[2]):
                    not_keys_col.append(col)
            if len(not_keys_col) > 0:
                for col in not_keys_col:
                    query = query + col.lower() + ":line." + col + ","
            query = query[:-1]
            query += "}"
            if len(not_keys_col) == 0:
                query = query[:-1]
            query = query + "]->(n2)"
            query = pharmebinetutils.get_query_import(file_path,
                                                      "import_into_Neo4j/bindingDB/tsv_from_mysql/" + edge[1] + ".tsv",
                                                      query)
            file.write(query)
        print("Queries saved to 'create_edges.cypher' file.")


def get_columns_names_from_tsv(file_name):
    with open(file_name, 'r') as tsv:
        columns = tsv.readline().split('\t')
        columns[-1] = columns[-1].strip('\n')
    return columns


def create_index_queries(edges, edges_2):
    with open('output/create_index.cypher', 'w') as file:
        queries_list = []
        for edge in edges:
            query = "CREATE INDEX index" + edge[1] + "_" + edge[2].lower() + " FOR (node:" + edge[1] + ") ON (node." + \
                    edge[2].lower() + ");\n"
            queries_list.append(query)
            query = "CREATE INDEX index" + edge[0] + "_" + edge[3].lower() + " FOR (node:" + edge[0] + ") ON (node." + \
                    edge[3].lower() + ");\n"
            queries_list.append(query)
        for table in edges_2:
            query = "CREATE INDEX index" + table + " FOR (node:" + table + ") ON ("
            for key in tables_keys.get(table):
                query = query + "node." + key.lower() + ", "
            query = query[:-2]
            query = query + ");\n"
            queries_list.append(query)
        queries_list = list(dict.fromkeys(queries_list))
        for q in queries_list:
            file.write(q)
        print("Queries saved to 'create_index.cypher' file.")


def create_idx_tsv(edges_id):
    for edges in edges_id:
        file_name = 'idx_tsv/' + edges[0] + '-' + edges[1] + '.tsv'
        tab_name = 'tsv_from_mysql/' + edges[1] + '.tsv'
        idx_column = edges[2]

        batch_size = 10000

        # Create an empty set to store unique values
        unique_values = set()
        # Read the TSV file in batches
        iterator = pd.read_csv(tab_name, sep='\t', usecols=[idx_column], chunksize=batch_size, na_values=[np.nan, ''])
        for batch_df in iterator:
            if edges[1] == "PDB_BDB" or edges[0] == "PDB_BDB":
                unique_values.update(batch_df[idx_column].dropna().drop_duplicates())
            else:
                unique_values.update(batch_df[idx_column].dropna().drop_duplicates().astype(int))
        # Create a DataFrame from the unique values
        unique_column_df = pd.DataFrame(unique_values, columns=[idx_column])
        # Save the unique column as a TSV file
        unique_column_df.to_csv(file_name, sep='\t', header=True, index=False)
        print("index saved to " + file_name)
    # create tsv file for the edge ASSAY-KI-RESULTS containing ASSAYID and ENTRYID (from the KI-RESULTS table)
    file_name = 'idx_tsv/ASSAY-KI_RESULT.tsv'
    batch_size = 10000
    columns_to_keep = ["ASSAYID", "ENTRYID"]
    unique_rows = pd.DataFrame(columns=columns_to_keep)
    for chunk in pd.read_csv("tsv_from_mysql/KI_RESULT.tsv", sep='\t', usecols=columns_to_keep, chunksize=batch_size,
                             na_values=[np.nan, '']):
        chunk = chunk.dropna(subset=columns_to_keep, how='any', inplace=False)
        chunk.drop_duplicates(inplace=True)
        chunk[columns_to_keep] = chunk[columns_to_keep].astype(int)
        unique_rows = pd.concat([unique_rows, chunk])
        unique_rows[columns_to_keep].drop_duplicates(inplace=True)

    unique_rows.to_csv(file_name, sep='\t', index=False, header=True)
    print('index saved to ', file_name)


if __name__ == "__main__":
    global file_path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        sys.exit('need a path')
    create_idx_tsv(edges_id)
    create_node_queries(tables)
    create_index_queries(edges_id, tables_index_edges)
    create_edge_queries(edges_id, kanten)
