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


def write_tsv(cursor, table_name):
    # Retrieve the total number of rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]

    # Retrieve the column names from table metadata
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [column[0] for column in cursor.fetchall()]

    # Create the TSV file with the table name as the filename
    output_file = f"{table_name}.tsv"

    # Write the header with column names to the TSV file
    with open(output_file, 'w') as file:
        file.write('\t'.join(columns) + '\n')

        # Batch size for streaming
        batch_size = 1000

        # Retrieve and write the data in batches
        offset = 0
        while offset < total_rows:
            # Fetch a batch of data using LIMIT and OFFSET
            query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Write the batch of rows to the TSV file
            for row in rows:
                file.write('\t'.join(str(value) for value in row) + '\n')

            # Increment the offset for the next batch
            offset += batch_size
            print("I'm at ", offset)
    print(f"done {table_name}")



def get_np(cursor, table_name):
    batch_size = 1000
    offset = 0
    data_batches = []
    column_names = []
    file_name = table_name + ".tsv"
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
        #print("I'm at ", offset)
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
    write_tsv(cur, "MONO_NAME")






