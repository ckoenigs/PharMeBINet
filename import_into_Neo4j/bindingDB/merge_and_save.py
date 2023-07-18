import shutil

import pymysql
import numpy as np
from collections import defaultdict
import pandas as pd
import csv
import re

def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password="password",
        db='BindingDB',
    )
    return conn


def replace_none_with_empty_string(input_tab):
    # Specify the file paths
    #input_file = "input.tsv"
    input_file = "tsv_from_mysql/" + input_tab + ".tsv"
    temp_file = "tsv_from_mysql/" + input_tab + "_temp.tsv"

    # Set the batch size
    batch_size = 1000  # Number of rows to process in each batch

    # Open the input and temporary files
    with open(input_file, "r", newline="", encoding="utf-8") as f_in, open(temp_file, "w", newline="",
                                                                           encoding="utf-8") as f_temp:
        reader = csv.reader(f_in, delimiter="\t")
        writer = csv.writer(f_temp, delimiter="\t")

        # Process the file in batches
        batch = []
        for i, row in enumerate(reader):
            # Replace "None" strings with empty strings
            modified_row = ["" if cell == "None" else cell for cell in row]
            batch.append(modified_row)

            # Write the batch to the temporary file if it reaches the specified size
            if len(batch) >= batch_size:
                writer.writerows(batch)
                batch = []

        # Write any remaining rows to the temporary file
        if batch:
            writer.writerows(batch)

    # Replace the original file with the temporary file
    shutil.move(temp_file, input_file)




def get_np_from_tsv(file_name):
    data_array = pd.read_csv(file_name, sep='\t', low_memory=False)
    data_array = data_array.replace("\"", "\'", regex=True)
    #data_array = data_array.replace("None", "", regex=True)
    head = np.array(data_array.columns)
    data_array = data_array.values
    data_array = np.vstack((head, data_array))
    return data_array


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
                result = '\t'.join(str(value) for value in row) + '\n'
                if "\"" in result:
                    result = result.replace("\"", "\'")
                file.write(result)

            # Increment the offset for the next batch
            offset += batch_size
            print("I'm at ", offset)
    print(f"done {table_name}")


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
        print(table_name, ": I'm at ", offset)
    data_array = np.concatenate(data_batches, axis=0)
    data_array = np.vstack([column_names, data_array])
    return data_array


def names_by_id(tab):
    # Create a default dict to store the names by ID
    _names_by_id = defaultdict(list)

    # Iterate over each row in the array and group the names by ID
    i = 0
    for row in tab:
        id_val, name = row
        _names_by_id[id_val].append(name)
        print("I'm at ", i)
        i += 1

    _names_by_id = dict(_names_by_id)

    ids = np.array(list(_names_by_id.keys()))
    names = np.empty(ids.shape[0], dtype='U7000')
    #print(names[0])
    names[0] = "NAMES"
    for i in range(ids.shape[0]):
        if i > 0:
            l = _names_by_id.get(ids[i])
            if l is None:
                names[i] = None
            elif len(l) > 1:
                length = 0
                #for x in l:
                    #length += len(x)
                #if length > 5000:
                    #print(length)
                names[i] = ";".join(l)
                #print(names[i])
            elif len(l) == 1:
                names[i] = l[0]

    #names = np.array(list(_names_by_id.values()), dtype=object)

    # Create a 2D NumPy array with IDs and names
    result_array = np.column_stack((ids, names))
    #result_array[0][1] = 'Names'
    #print(result_array)
    return result_array


def merge_arrays_optimized(array1, array2):
    head1 = array1[0].tolist()
    head2 = array2[0].tolist()
    print(head1)
    print(head2)
    df1 = pd.DataFrame(array1, columns=head1)
    df2 = pd.DataFrame(array2, columns=head2)
    df = pd.merge(df1, df2, on='POLYMERID', how='outer')
    df = df.replace({'\"': '\''}, regex=True)
    return df


def create_names(connection):

    try:
        # Create a new table in the database
        create_table_query = """
        CREATE TABLE MONO_NAMES (
            MONOMERID INT,
            NAMES VARCHAR(16300)
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
        # Set the group_concat_max_len value for the current session
        set_max_len_query = "SET SESSION group_concat_max_len = 1000000"

        with connection.cursor() as cursor:
            cursor.execute(set_max_len_query)

        # Insert the concatenated results into the new table
        insert_query = """
        INSERT INTO MONO_NAMES (MONOMERID, NAMES)
        SELECT MONOMERID, GROUP_CONCAT(NAME ORDER BY NAME SEPARATOR '; ')
        FROM MONO_NAME
        GROUP BY MONOMERID
        """
        with connection.cursor() as cursor:
            cursor.execute(insert_query)

            # Commit the changes to the database
            connection.commit()
        print("done!")

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()


def get_table_columns(table_name, column_cache, connection):
    if table_name not in column_cache:
        describe_query = f"DESCRIBE {table_name}"
        with connection.cursor() as cursor:
            cursor.execute(describe_query)
            columns = [desc[0] for desc in cursor.fetchall()]
            column_cache[table_name] = columns
    return column_cache[table_name]


def join_monomer(connection):
    # Define the batch size and output file name
    batch_size = 1000
    output_file = 'MONO_STRUCT_NAMES.tsv'
    cache_column = {}

    # Generate the dynamic SELECT statement
    select_query = "SELECT "
    for table_name in ['MONOMER', 'MONOMER_STRUCT', 'MONO_NAMES']:
        table_columns = get_table_columns(table_name, cache_column, connection)
        for column in table_columns:
            if column != 'MONOMERID':  # Exclude the duplicate ID column
                select_query += f"{table_name}.{column}, "
    select_query += 'MONOMER.MONOMERID'
    select_query += f"""
       FROM MONOMER
       JOIN MONOMER_STRUCT ON MONOMER.MONOMERID = MONOMER_STRUCT.MONOMERID
       JOIN MONO_NAMES ON MONOMER.MONOMERID = MONO_NAMES.MONOMERID
       LIMIT {batch_size}"""

    # Execute the dynamic SELECT statement
    with connection.cursor() as cursor:
        cursor.execute(select_query)

    # Retrieve the total row count
    count_query = "SELECT COUNT(*) FROM MONOMER"
    with connection.cursor() as cursor:
        cursor.execute(count_query)
        total_rows = cursor.fetchone()[0]
        print(total_rows)

        # Open the output file for writing
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')

        # Fetch and write the data in batches
        for offset in range(0, total_rows, batch_size):
            # Select batch-wise with offset and limit
            if offset == 0:
                select_query += f" OFFSET {offset}"
            else:
                new_offset = f"OFFSET {offset}"
                select_query = re.sub(r'OFFSET \w+\s*', "", select_query)
                select_query += new_offset
            print(select_query)

            with connection.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                if not result:
                    break
                if offset == 0:
                    # Write the header row for the first batch
                    column_names = [desc[0] for desc in cursor.description]
                    writer.writerow(column_names)
                writer.writerows(result)
            print(f"I'm at: {offset}")

    print(f"Data written to {output_file}")


if __name__ == "__main__":
    conn = mysqlconnect()
    cur = conn.cursor()
    tables = ['ARTICLE', 'ASSAY', 'COBWEB_BDB', 'COMPLEX_COMPONENT', 'DATA_FIT_METH', 'ENTRY', 'ENTRY_CITATION',
              'ENZYME_REACTANT_SET', 'INSTRUMENT', 'ITC_RESULT_A_B_AB', 'ITC_RUN_A_B_AB', 'KI_RESULT', 'PDB_BDB']
    tables_1 = ['ARTICLE', 'ASSAY', 'COBWEB_BDB', 'COMPLEX_COMPONENT', 'DATA_FIT_METH', 'ENTRY', 'ENTRY_CITATION',
                'ENZYME_REACTANT_SET', 'INSTRUMENT', 'ITC_RESULT_A_B_AB', 'ITC_RUN_A_B_AB', 'KI_RESULT', 'PDB_BDB',
                'POLYMER_AND_NAMES', 'MONO_STRUCT_NAMES', 'COMPLEX_AND_NAMES']
    for table in tables:
        write_tsv(cur, table)
    # merge complex names and polymer
    write_tsv(cur, "COMPLEX")
    complex_name = get_np(cur, 'COMPLEX_NAME')
    complex_names_array = names_by_id(complex_name)
    complex_and_names = merge_arrays_optimized(get_np_from_tsv('COMPLEX.tsv'), complex_names_array)
    np.savetxt('COMPLEX_AND_NAMES.tsv', complex_and_names, delimiter='\t', fmt='%s')

    # merge polymer names and polymer
    polymer_name = get_np(cur, 'POLY_NAME')
    polymer_names_array = names_by_id(polymer_name)
    polymer_and_names = merge_arrays_optimized(get_np(cur, 'POLYMER'), polymer_names_array)
    np.savetxt('POLYMER_AND_NAMES.tsv', polymer_and_names, delimiter='\t', fmt='%s')

    #create a monomer_names table where names are grouped by monomer id
    create_names(conn)
    #join monomer, monomer struct and monomer names
    join_monomer(conn)
    mono_array = get_np_from_tsv('tsv_from_mysql/MONO_STRUCT_NAMES.tsv')
    np.savetxt('MONO_STRUCT_NAMES.tsv', mono_array, delimiter='\t', fmt='%s')

    #replace none cells with empty strings for each tsv table
    for table in tables_1:
        replace_none_with_empty_string(table)
        print(table + " finished!")










