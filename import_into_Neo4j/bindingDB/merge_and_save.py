import shutil
import numpy as np
from collections import defaultdict
import pandas as pd
import csv
import datetime
import sys
sys.path.append("../..")
import create_connection_to_databases

BATCH_SIZE = 100000


def get_np_from_tsv(file_name):
    data_array = pd.read_csv(file_name, sep='\t', low_memory=False)
    data_array = data_array.replace("\"", "\'", regex=True)
    # data_array = data_array.replace("None", "", regex=True)
    head = np.array(data_array.columns)
    data_array = data_array.values
    data_array = np.vstack((head, data_array))
    return data_array


def prepare_results(row):
    """
    Prepare row result of mysql for empty values, nullt to empty string and replace " with '
    :param row:
    :return:
    """
    return [str(value).replace("\"", "\'").replace('NULL', '').replace('null', '')  if not value is None else '' for value in row]


def write_tsv(cursor, table_name):
    # Retrieve the total number of rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]

    # Retrieve the column names from table metadata
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [column[0] for column in cursor.fetchall()]

    # Create the TSV file with the table name as the filename
    output_file = f"tsv_from_mysql/{table_name}.tsv"

    print('total row', total_rows)

    # Write the header with column names to the TSV file
    with open(output_file, 'w', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(columns)

        # Retrieve and write the data in batches
        offset = 0
        while offset < total_rows:
            # Fetch a batch of data using LIMIT and OFFSET
            query = f"SELECT * FROM {table_name} LIMIT {BATCH_SIZE} OFFSET {offset}"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Write the batch of rows to the TSV file
            for row in rows:
                result = prepare_results(row)
                csv_writer.writerow(result)

            # Increment the offset for the next batch
            offset += BATCH_SIZE
            if offset % 500000 == 0:
                print("I'm at ", offset, datetime.datetime.now())

    print(f"done {table_name}")


def get_np(cursor, table_name):
    offset = 0
    data_batches = []
    column_names = []
    while True:
        query = f"SELECT * FROM {table_name} LIMIT {BATCH_SIZE} OFFSET {offset}"
        cursor.execute(query)
        rows = cur.fetchall()
        if len(rows) == 0:
            break
        if offset == 0:
            column_names = [desc[0] for desc in cur.description]
            column_names = np.array(column_names)

        batch_array = np.array(rows)
        data_batches.append(batch_array)
        offset += BATCH_SIZE
        if offset % 100000 == 0:
            print(table_name, ": I'm at ", offset, datetime.datetime.now())
    data_array = np.concatenate(data_batches, axis=0)
    data_array = np.vstack([column_names, data_array])
    data_array[data_array == None] = ''
    data_array[data_array == 'NULL'] = ''
    return data_array


def names_by_id(tab):
    # Create a default dict to store the names by ID
    _names_by_id = defaultdict(list)

    # Iterate over each row in the array and group the names by ID
    i = 0
    for row in tab:
        id_val, name = row
        _names_by_id[id_val].append(name)
        if i % 1000 == 0:
            print("I'm at ", i)
        i += 1

    _names_by_id = dict(_names_by_id)

    ids = np.array(list(_names_by_id.keys()))
    names = np.empty(ids.shape[0], dtype='U7000')
    # print(names[0])
    names[0] = "NAMES"
    for i in range(ids.shape[0]):
        if i > 0:
            l = _names_by_id.get(ids[i])
            if l is None:
                names[i] = None
            elif len(l) > 1:
                length = 0
                # for x in l:
                # length += len(x)
                # if length > 5000:
                # print(length)
                names[i] = ";".join(l)
                # print(names[i])
            elif len(l) == 1:
                names[i] = l[0]

    # names = np.array(list(_names_by_id.values()), dtype=object)

    # Create a 2D NumPy array with IDs and names
    result_array = np.column_stack((ids, names))
    # result_array[0][1] = 'Names'
    # print(result_array)
    return result_array


def merge_arrays_optimized(array1, array2, merge_id):
    head1 = array1[0].tolist()
    head2 = array2[0].tolist()
    df1 = pd.DataFrame(array1, columns=head1)
    df2 = pd.DataFrame(array2, columns=head2)
    df = pd.merge(df1, df2, on=merge_id, how='outer')
    df = df.replace({'\"': '\''}, regex=True)
    df = df.fillna('')
    return df


def get_table_columns(table_name, connection):
    describe_query = f"DESCRIBE {table_name}"
    with connection.cursor() as cursor:
        cursor.execute(describe_query)
        columns = [desc[0] for desc in cursor.fetchall()]
    return columns


def join_monomer_new(connection):
    batch_size_mono = 100000
    cursor = connection.cursor()

    # Retrieve the total number of rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM MONOMER")
    total_rows = cursor.fetchone()[0]
    print('total rows', total_rows)

    # header of tsv file
    header = []

    # Generate the dynamic SELECT statement
    select_query_start = "SELECT "
    for table_name in ['MONOMER', 'MONOMER_STRUCT']:
        table_columns = get_table_columns(table_name, connection)
        for column in table_columns:
            if column != 'MONOMERID':  # Exclude the duplicate ID column
                header.append(column)
                select_query_start += f"{table_name}.{column}, "
    header.append('MONOMERID')
    header.append('synonyms')
    select_query_start += 'MONOMER.MONOMERID, names.synonyms'

    select_query_start += f"""
           FROM MONOMER
           LEFT OUTER JOIN MONOMER_STRUCT ON MONOMER.MONOMERID = MONOMER_STRUCT.MONOMERID
           LEFT OUTER JOIN (SELECT MONOMERID, GROUP_CONCAT(NAME ORDER BY NAME SEPARATOR '; ') as synonyms FROM MONO_NAME
            GROUP BY  MONOMERID) as names ON MONOMER.MONOMERID = names.MONOMERID
           """

    output_file = 'tsv_from_mysql/MONO_STRUCT_NAMES.tsv'
    with open(output_file, 'w', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(header)

        # Retrieve and write the data in batches
        offset = 0
        while offset < total_rows:
            # Fetch a batch of data using LIMIT and OFFSET
            query = select_query_start + f" LIMIT {batch_size_mono} OFFSET {offset}"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Write the batch of rows to the TSV file
            for row in rows:
                result = prepare_results(row)
                csv_writer.writerow(result)

            # Increment the offset for the next batch
            offset += batch_size_mono
            if offset % 100000 == 0:
                print("I'm at ", offset, datetime.datetime.now())


if __name__ == "__main__":
    print(datetime.datetime.now())
    conn = create_connection_to_databases.mysqlconnect_bindingDB()
    cur = conn.cursor()
    tables = ['ARTICLE', 'ASSAY', 'COBWEB_BDB', 'COMPLEX_COMPONENT', 'DATA_FIT_METH', 'ENTRY', 'ENTRY_CITATION',
              'ENZYME_REACTANT_SET', 'INSTRUMENT', 'ITC_RESULT_A_B_AB', 'ITC_RUN_A_B_AB', 'KI_RESULT', 'PDB_BDB']
    tables_1 = ['ARTICLE', 'ASSAY', 'COBWEB_BDB', 'COMPLEX_COMPONENT', 'DATA_FIT_METH', 'ENTRY', 'ENTRY_CITATION',
                'ENZYME_REACTANT_SET', 'INSTRUMENT', 'ITC_RESULT_A_B_AB', 'ITC_RUN_A_B_AB', 'KI_RESULT', 'PDB_BDB',
                'POLYMER_AND_NAMES', 'MONO_STRUCT_NAMES', 'COMPLEX_AND_NAMES']
    for table in tables:
        print('create table', table, datetime.datetime.now())
        write_tsv(cur, table)

    # merge complex names and polymer
    print('start complex', datetime.datetime.now())
    write_tsv(cur, "COMPLEX")
    complex_name = get_np(cur, 'COMPLEX_NAME')
    complex_names_array = names_by_id(complex_name)
    complex_and_names = merge_arrays_optimized(get_np_from_tsv('tsv_from_mysql/COMPLEX.tsv'), complex_names_array,
                                               'COMPLEXID')
    np.savetxt('tsv_from_mysql/COMPLEX_AND_NAMES.tsv', complex_and_names, delimiter='\t', fmt='%s')

    # merge polymer names and polymer
    print('start polymer', datetime.datetime.now())
    polymer_name = get_np(cur, 'POLY_NAME')
    polymer_names_array = names_by_id(polymer_name)
    polymer_and_names = merge_arrays_optimized(get_np(cur, 'POLYMER'), polymer_names_array, 'POLYMERID')
    np.savetxt('tsv_from_mysql/POLYMER_AND_NAMES.tsv', polymer_and_names, delimiter='\t', fmt='%s')

    # create a monomer_names table where names are grouped by monomer id
    print('start monomer', datetime.datetime.now())
    # create_names(conn)

    # join monomer, monomer struct and monomer names
    join_monomer_new(conn)
    # mono_array = get_np_from_tsv('tsv_from_mysql/MONO_STRUCT_NAMES.tsv')
    # np.savetxt('MONO_STRUCT_NAMES.tsv', mono_array, delimiter='\t', fmt='%s')

    print('end', datetime.datetime.now())
