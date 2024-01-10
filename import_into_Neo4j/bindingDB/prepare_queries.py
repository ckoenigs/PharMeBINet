import datetime
import sys

import numpy as np
import pandas as pd

sys.path.append("../..")
import pharmebinetutils

additional_to_label = 'bindingDB'

# tables names as list
tables = ['article', 'assay', 'cobweb_bdb', 'complex_component', 'entry',
          'enzyme_reactant_set', 'ki_result', 'pdb_bdb', 'complex_and_names', 'polymer_and_names', 'mono_struct_names']
# 'itc_result_a_b_ab', 'itc_run_a_b_ab', 'instrument','data_fit_meth', 'entry_citation',


# list of tabels which will be an edge
tables_index_edges = ['article']  # , 'itc_result_a_b_ab'
#
kanten = [['entry', 'entry_citation', 'article']]  # , ['entry', 'itc_run_a_b_ab', 'itc_result_a_b_ab']

tables_keys = {'article': ['articleid'], 'assay': ['entryid', 'assayid'], 'cobweb_bdb': [],
               'complex_component': ['complexid', 'componentid'],
               'entry': ['entryid'],
               'enzyme_reactant_set': ['entryid', 'rectant_set_id'],
               'ki_result': ['entryid', 'ki_result_id'],
               'pdb_bdb': [], 'complex_and_names': ['complexid'], 'polymer_and_names': ['polymerid'],
               'mono_struct_names': ['monomerid']}
# 'itc_run_a_b_ab': ['entryid', 'itc_run_a_b_ab_id'], 'instrument': ['instrumentid'], 'entry_citation': ['articleid', 'entryid'],
#                'itc_result_a_b_ab': ['entryid', 'itc_result_a_b_ab_id'], 'data_fit_meth': ['data_fit_meth_id'],

# every element of the list is a list of 3 items
# containing the name of the tables with direct connection and the name of the index column(s) in the original tsv file
# note that the index column is always related to the second table.
# list of list [table1, table2, property_name_table_1, property_name_table_2]
list_of_direct_connected_tables_and_properties = [['mono_struct_names', 'cobweb_bdb', 'monomer_id', 'monomerid'],
                                                  ['mono_struct_names', 'complex_component', 'monomerid', 'monomerid'],
                                                  ['polymer_and_names', 'complex_component', 'polymerid', 'polymerid'],
                                                  ['enzyme_reactant_set', 'cobweb_bdb', 'reactant_set_id',
                                                   'reactant_set_id'],
                                                  ['entry', 'enzyme_reactant_set', 'entryid', 'entryid'],
                                                  ['enzyme_reactant_set', 'pdb_bdb', 'reactant_set_id_str',
                                                   'reactant_set_id'],
                                                  ['entry', 'assay', 'entryid', 'entryid'],
                                                  ['assay', 'ki_result', 'assayid', 'assayid'],
                                                  ['entry', 'ki_result', 'entryid', 'entryid'],
                                                  ['complex_and_names', 'complex_component', 'complexid', 'complexid']]
# ['data_fit_meth', 'itc_result_a_b_ab', 'data_fit_meth_id', 'data_fit_meth_id'],
# ['instrument', 'itc_result_a_b_ab', 'instrumentid', 'instrumentid'],
#               ['instrument', 'ki_result', 'instrumentid', 'instrumentid'],
#             ['data_fit_meth', 'ki_result', 'data_fit_meth_id', 'data_fit_meth_id'],
#             ['entry', 'itc_result_a_b_ab', 'entryid', 'entryid']

# special columns as list
special_col = ['inhibitor_polymerid', 'enzyme_polymerid', 'substrate_polymerid', 'enzyme_complexid',
               'inhibitor_complexid', 'substrate_complexid', 'substrate_monomerid', 'inhibitor_monomerid',
               'enzyme_monomerid']


def create_node_queries(tab):
    """
    prepare cypher file and add for each node table a cypher query to the cypher file
    :param tab:
    :return:
    """
    with open('output/create_nodes.cypher', 'w') as file:
        # Generate and write the queries to the file
        for table in tab:
            if table not in ['complex_and_names', 'polymer_and_names', 'mono_struct_names']:
                query = "create (:" + additional_to_label + "_" + table + "{"
                file_name = "tsv_from_mysql/" + table + ".tsv"
                for column in get_columns_names_from_tsv(file_name):
                    if column != 'comments':
                        query += column.lower() + ":line." + column + ","
                    else:
                        query += 'comment:line.' + column + ','
                query = query[:-1]
                query += "})"
                query = pharmebinetutils.get_query_import(file_path,
                                                          "import_into_Neo4j/bindingDB/tsv_from_mysql/" + table + ".tsv",
                                                          query)
                file.write(query)
            else:
                query = "create (:" + additional_to_label + "_" + table + "{"
                file_name = "tsv_from_mysql/" + table + ".tsv"
                for column in get_columns_names_from_tsv(file_name):
                    if column in ['names', 'synonyms']:
                        query += column.lower() + ':split(line.' + column + ',"|"),'
                    elif column == 'comments':
                        query += 'comment:line.' + column + ','
                    elif column in ['pdb_ids']:
                        query += column.lower() + ':split(line.' + column + ',","),'
                    else:
                        query += column.lower() + ":line." + column + ","
                query = query[:-1]
                query += "})"
                query = pharmebinetutils.get_query_import(file_path,
                                                          "import_into_Neo4j/bindingDB/tsv_from_mysql/" + table + ".tsv",
                                                          query)
                file.write(query)
    print("Queries saved to 'create_nodes.cypher' file.")


def create_edge_queries(simple_edges, edges):
    with open('output/create_edges.cypher', 'w') as file:
        query = ''
        for col in special_col:
            if "polymer" in col:
                query = "match (n1: " + additional_to_label + "_polymer_and_names {polymerid: line." + col + "}), (n2:" + additional_to_label + "_enzyme_reactant_set{reactant_set_id:line.reactant_set_id})\n create(n1) - [:" + col + "] -> (n2)"
            elif "monomer" in col:
                query = "match (n1: " + additional_to_label + "_mono_struct_names {monomerid: line." + col + "}), (n2:" + additional_to_label + "_enzyme_reactant_set{reactant_set_id:line.reactant_set_id})\n create(n1) - [:" + col + "] -> (n2)"
            elif "complex" in col:
                query = "match (n1: " + additional_to_label + "_complex_and_names {complexid: line." + col + "}), (n2:" + additional_to_label + "_enzyme_reactant_set{reactant_set_id:line.reactant_set_id})\n create(n1) - [:" + col + "] -> (n2)"

            query = pharmebinetutils.get_query_import(file_path,
                                                      'import_into_Neo4j/bindingDB/idx_tsv/enzyme_reactant_set-' +
                                                      col + '.tsv', query, batch_number=10000)
            file.write(query)

        for edge in simple_edges:
            if edge[0] == 'assay' and edge[1] == 'ki_result':
                query = "MATCH (n1:" + additional_to_label + "_assay{assayid:line.assayid, entryid:line.entryid}), (n2:" + additional_to_label + "_ki_result" \
                                                                                                                                                 "{assayid:line.assayid, entryid:line.entryid})\n Create (n1) -[:RELATIONSHIP] -> (n2)"
                query = pharmebinetutils.get_query_import(file_path,
                                                          'import_into_Neo4j/bindingDB/idx_tsv/assay-ki_result.tsv',
                                                          query, batch_number=10000)
                file.write(query)
            else:
                file_name = edge[0] + '-' + edge[1] + '.tsv'
                if edge[0] == 'enzyme_reactant_set' and edge[1] == 'pdb_bdb':
                    query = "MATCH (n1:" + additional_to_label + "_enzyme_reactant_set), (n2:" + additional_to_label + "_pdb_bdb{reactant_set_id_str:line.reactant_set_id_str}) " \
                                                                                                                       "where n1.reactant_set_id in split(line.reactant_set_id_str, ',') " \
                                                                                                                       "\nCreate (n1) -[:RELATIONSHIP] -> (n2)"
                    query = pharmebinetutils.get_query_import(file_path,
                                                              'import_into_Neo4j/bindingDB/idx_tsv/' + file_name, query,
                                                              batch_number=10000)
                    file.write(query)
                else:
                    query = "MATCH (n1:" + additional_to_label + "_" + edge[0] + "{" + edge[3].lower() + ":line." + \
                            edge[2] + "}), "
                    query = query + "(n2:" + additional_to_label + "_" + edge[1] + "{" + edge[2].lower() + ":line." + \
                            edge[2] + "}) \n"
                    query = query + "Create (n1) -[:RELATIONSHIP] -> (n2)"
                    query = pharmebinetutils.get_query_import(file_path,
                                                              'import_into_Neo4j/bindingDB/idx_tsv/' + file_name, query,
                                                              batch_number=10000)
                    file.write(query)
        for edge in edges:
            query = "MATCH (n1:" + additional_to_label + "_" + edge[0] + "{"
            for key in tables_keys.get(edge[0]):
                query = query + key.lower() + ": line." + key + ","
            query = query[:-1]
            query = query + "}), (n2:" + additional_to_label + "_" + edge[2] + "{"
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
    '''
    Prepare indices for the different edge type nodes
    :param edges:
    :param edges_2:
    :return:
    '''
    with open('output/create_index.cypher', 'w') as file:
        queries_list = []
        for edge in edges:
            query = "CREATE INDEX index" + edge[1] + "_" + edge[2].lower() + " FOR (node:" + additional_to_label + "_" + \
                    edge[1] + ") ON (node." + \
                    edge[2].lower() + ");\n"
            queries_list.append(query)
            query = "CREATE INDEX index" + edge[0] + "_" + edge[3].lower() + " FOR (node:" + additional_to_label + "_" + \
                    edge[0] + ") ON (node." + \
                    edge[3].lower() + ");\n"
            queries_list.append(query)
        for table in edges_2:
            query = "CREATE INDEX index" + table + " FOR (node:" + additional_to_label + "_" + table + ") ON ("
            for key in tables_keys.get(table):
                query = query + "node." + key.lower() + ", "
            query = query[:-2]
            query = query + ");\n"
            queries_list.append(query)
        for col in special_col:
            query = "CREATE INDEX indexENZYME_REACTANT_SET_" + col.lower() + \
                    " FOR (node:" + additional_to_label + "_enzyme_reactant_set) ON (node." + col.lower() + "); \n"
            queries_list.append(query)
        queries_list = list(dict.fromkeys(queries_list))
        for q in queries_list:
            file.write(q)
        print("Queries saved to 'create_index.cypher' file.")


def create_idx_tsv(list_of_direct_connected_tables_and_properties):
    """
    Prepare TSV file for connected tables with no edge information and special edge between assay and ki-result.
    This needs two properties as foreigen keys.
    :param list_of_direct_connected_tables_and_properties: 
    :return: 
    """
    for edges in list_of_direct_connected_tables_and_properties:
        file_name = 'idx_tsv/' + edges[0] + '-' + edges[1] + '.tsv'
        tab_name = 'tsv_from_mysql/' + edges[1] + '.tsv'
        idx_column = edges[2]

        batch_size = 50000

        # Create an empty set to store unique values
        unique_values = set()
        # Read the TSV file in batches
        iterator = pd.read_csv(tab_name, sep='\t', usecols=[idx_column], chunksize=batch_size, na_values=[np.nan, ''])
        for batch_df in iterator:
            if edges[1] == "pdb_bdb" or edges[0] == "pdb_bdb":
                unique_values.update(batch_df[idx_column].dropna().drop_duplicates())
            else:
                unique_values.update(batch_df[idx_column].dropna().drop_duplicates().astype(int))
        # Create a DataFrame from the unique values
        unique_column_df = pd.DataFrame(unique_values, columns=[idx_column])
        # Save the unique column as a TSV file
        unique_column_df.to_csv(file_name, sep='\t', header=True, index=False)
        print("index saved to " + file_name)
    # create tsv file for the edge ASSAY-KI-RESULTS containing ASSAYID and ENTRYID (from the KI-RESULTS table)
    file_name = 'idx_tsv/assay-ki_result.tsv'
    batch_size = 10000
    columns_to_keep = ["assayid", "entryid"]
    unique_rows = pd.DataFrame(columns=columns_to_keep)
    for chunk in pd.read_csv("tsv_from_mysql/ki_result.tsv", sep='\t', usecols=columns_to_keep, chunksize=batch_size,
                             na_values=[np.nan, '']):
        chunk = chunk.dropna(subset=columns_to_keep, how='any', inplace=False)
        chunk.drop_duplicates(inplace=True)
        chunk[columns_to_keep] = chunk[columns_to_keep].astype(int)
        unique_rows = pd.concat([unique_rows, chunk])
        unique_rows[columns_to_keep].drop_duplicates(inplace=True)

    unique_rows.to_csv(file_name, sep='\t', index=False, header=True)
    print('index saved to ', file_name)

    for col in special_col:
        unique_rows = pd.DataFrame(columns=[col, 'reactant_set_id'])

        for chunk in pd.read_csv("tsv_from_mysql/enzyme_reactant_set.tsv", sep='\t', usecols=[col, 'reactant_set_id'],
                                 chunksize=batch_size, na_values=[np.nan, '']):
            chunk = chunk.dropna(subset=[col, 'reactant_set_id'], how='any', inplace=False)
            chunk.drop_duplicates(inplace=True)
            chunk[col] = chunk[col].astype(int)
            chunk['reactant_set_id'] = chunk['reactant_set_id'].astype(int)
            unique_rows = pd.concat([unique_rows, chunk])
            unique_rows[col].drop_duplicates(inplace=True)

        unique_rows.to_csv('idx_tsv/enzyme_reactant_set-' + col + '.tsv', sep='\t', index=False, header=True)
        print('index saved to ', 'enzyme_reactant_set-' + col + '.tsv')


if __name__ == "__main__":
    global file_path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        sys.exit('need a path')

    print('*' * 30)
    print(datetime.datetime.now())
    print('prepare tsv for direct edges')
    create_idx_tsv(list_of_direct_connected_tables_and_properties)

    print('*' * 30)
    print(datetime.datetime.now())
    print('prepare node cypher file with the fitting cypher queries')
    create_node_queries(tables)
    create_index_queries(list_of_direct_connected_tables_and_properties, tables_index_edges)
    create_edge_queries(list_of_direct_connected_tables_and_properties, kanten)
