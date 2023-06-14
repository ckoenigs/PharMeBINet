import pymysql
import numpy as np
from collections import defaultdict


def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password="password",
        db='BindingDB',
    )
    cursor = conn.cursor()
    return cursor


def get_np(cursor, table_name):
    batch_size = 1000
    offset = 0
    data_batches = []
    column_names = []
    while True:
        query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
        cursor.execute(query)
        rows = cur.fetchall()
        if len(rows) == 0:
            break
        if offset == 0:
            column_names = [desc[0] for desc in cur.description]
            column_names = np.array(column_names)
        batch_array = np.array(rows)
        data_batches.append(batch_array)
        offset += batch_size
        print("I'm at ", offset)
    data_array = np.concatenate(data_batches, axis=0)
    data_array = np.vstack([column_names, data_array])
    return data_array


def names_by_id(tab):
    # Create a defaultdict to store the names by ID
    _names_by_id = defaultdict(list)

    # Iterate over each row in the array and group the names by ID
    for row in tab:
        id_val, name = row
        _names_by_id[id_val].append(name)

    _names_by_id = dict(_names_by_id)

    ids = np.array(list(_names_by_id.keys()))
    names = np.array(list(_names_by_id.values()), dtype=object)

    # Create a 2D NumPy array with IDs and names
    result_array = np.column_stack((ids, names))
    return result_array


def merge_arrays(array1, array2, idxID1, idxID2):
    # Extract the ID column from each array
    ids1 = array1[:, idxID1]
    ids2 = array2[:, idxID2]
    for i in range(ids2.shape[0]):
        if i > 0:
            ids2[i] = int(ids2[i])

    # Find the indices where the IDs match
    indices = np.where(np.isin(ids1, ids2))

    # Create a new column with the corresponding values from array2
    new_column = np.full_like(array1[:, idxID1], fill_value=None, dtype=object)
    new_column[indices] = array2[np.isin(ids2, ids1), 1]

    # Add the z column to array1
    new_array = np.column_stack((array1, new_column))

    # Print the updated array
    return new_array


if __name__ == "__main__":
    polymer = "POLYMER"
    polymer_name = "POLY_NAME"
    complex = "COMPLEX"
    complex_name = "COMPLEX_NAME"
    monomer = "MONOMER"
    monomer_name = "MONO_NAME"
    cur = mysqlconnect()
    #polymer_array = get_np(cur, polymer)
    #polymer_name_array = get_np(cur, polymer_name)
    #complex_array = get_np(cur, complex)
    #complex_name_array = get_np(cur, complex_name)
    #cobweb_array = get_np(cur, "COBWEB_BDB")
    #np.savetxt('COBWEB_BDB.tsv', cobweb_array, delimiter='\t', fmt='%s')
    #enzyme_array = get_np(cur, "ENZYME_REACTANT_SET")
    #np.savetxt('ENZYME_REACTANT_SET.tsv', enzyme_array, delimiter='\t', fmt='%s')
    ####assay_array = get_np(cur, "ASSAY")
    ####np.savetxt('ASSAY.tsv', assay_array, delimiter='\t', fmt='%s')
    #pdb_array = get_np(cur, "PDB_BDB")
    #np.savetxt('PDB_BDB.tsv', pdb_array, delimiter='\t', fmt='%s')
    #complex_component_array = get_np(cur, "COMPLEX_COMPONENT")
    #np.savetxt('COMPLEX_COMPONENT.tsv', complex_component_array, delimiter='\t', fmt='%s')
    ki_result_array = get_np(cur, "KI_RESULT")
    np.savetxt('KI_RESULT.tsv', ki_result_array, delimiter='\t', fmt='%s')
    entry_array = get_np(cur, "ENTRY")
    np.savetxt('ENTRY.tsv', entry_array, delimiter='\t', fmt='%s')
    data_fit_meth_array = get_np(cur, "DATA_FIT_METH")
    np.savetxt('DATA_FIT_METH.tsv', data_fit_meth_array, delimiter='\t', fmt='%s')
    instrument_array = get_np(cur, "INSTRUMENT")
    np.savetxt('INSTRUMENT.tsv', instrument_array, delimiter='\t', fmt='%s')
    itc_result_array = get_np(cur, "ITC_RESULT_A_B_AB")
    np.savetxt('ITC_RESULT_A_B_AB.tsv', itc_result_array, delimiter='\t', fmt='%s')
    itc_run_array = get_np(cur, "ITC_RUN_A_B_AB")
    np.savetxt('ITC_RUN_A_B_AB.tsv', itc_run_array, delimiter='\t', fmt='%s')
    entry_citation_array = get_np(cur, "ENTRY_CITATION")
    np.savetxt('ENTRY_CITATION.tsv', entry_citation_array, delimiter='\t', fmt='%s')
    article_array = get_np(cur, "ARTICLE")
    np.savetxt('ARTICLE.tsv', article_array, delimiter='\t', fmt='%s')
    monomer_struct_array = get_np(cur, "MONOMER_STRUCT")
    np.savetxt('MONOMER_STRUCT.tsv', monomer_struct_array, delimiter='\t', fmt='%s')
    monomer_array = get_np(cur, monomer)
    monomer_name_array = get_np(cur, monomer_name)
    #polymer_name_array_new = names_by_id(polymer_name_array)
    #complex_name_array_new = names_by_id(complex_name_array)
    monomer_name_array_new = names_by_id(monomer_name_array)
    #merged_array = merge_arrays(polymer_array, polymer_name_array_new, 18, 0)
    #merged_array_complex = merge_arrays(complex_array, complex_name_array_new, 0, 0)
    merged_array_monomer = merge_arrays(monomer_array, monomer_name_array_new, 11, 0)
    #print(merged_array_monomer.shape)
    #np.savetxt('POLYMER_AND_NAMES.tsv', merged_array, delimiter='\t', fmt='%s')
    #np.savetxt('COMPLEX_AND_NAMES.tsv', merged_array_complex, delimiter='\t', fmt='%s')
    np.savetxt('MONOMER_AND_NAMES.tsv', merged_array_monomer, delimiter='\t', fmt='%s')






