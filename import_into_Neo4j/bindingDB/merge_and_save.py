import shutil
import numpy as np
from collections import defaultdict
import pandas as pd
import csv
import datetime
import sys

sys.path.append("../..")
import create_connection_to_databases

BATCH_SIZE = 500000


def prepare_results(row):
    """
    Prepare row result of mysql for empty values, null to empty string and replace " with '
    :param row:
    :return:
    """
    return [str(value).replace("\"", "\'").replace('\r', '').replace("\n", "").replace('NULL', '').replace('null',
                                                                                                           '') if not value is None else ''
            for value in row]


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


def get_table_columns(table_name, connection):
    describe_query = f"DESCRIBE {table_name}"
    with connection.cursor() as cursor:
        cursor.execute(describe_query)
        columns = [desc[0] for desc in cursor.fetchall()]
    return columns


def join_polymer_or_complex_new(connection, main_table_name, identifier, sub_table_name, file_name):
    cursor = connection.cursor()

    # Retrieve the total number of rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM {main_table_name}")
    total_rows = cursor.fetchone()[0]
    print('total rows', total_rows)

    # header of tsv file
    header = []

    # Generate the dynamic SELECT statement
    select_query_start = "SELECT "
    table_columns = get_table_columns(main_table_name, connection)
    for column in table_columns:
        header.append(column)
        select_query_start += f"{main_table_name}.{column}, "
    header.append('synonyms')
    select_query_start += f' names.synonyms'

    select_query_start += f"""
           FROM {main_table_name}
           LEFT OUTER JOIN (SELECT {identifier}, GROUP_CONCAT(NAME ORDER BY NAME SEPARATOR '|') as synonyms FROM {sub_table_name}
            GROUP BY  {identifier}) as names ON {main_table_name}.{identifier} = names.{identifier}
           """

    output_file = f'tsv_from_mysql/{file_name}.tsv'
    with open(output_file, 'w', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter='\t')
        csv_writer.writerow(header)

        # Retrieve and write the data in batches
        offset = 0
        while offset < total_rows:
            # Fetch a batch of data using LIMIT and OFFSET
            query = select_query_start + f" LIMIT {BATCH_SIZE} OFFSET {offset}"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Write the batch of rows to the TSV file
            for row in rows:
                result = prepare_results(row)
                csv_writer.writerow(result)

            # Increment the offset for the next batch
            offset += BATCH_SIZE
            if offset % 100000 == 0:
                print("I'm at ", offset, datetime.datetime.now())


def join_monomer_new(connection):
    batch_size_mono = 300000
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
           LEFT OUTER JOIN (SELECT MONOMERID, GROUP_CONCAT(NAME ORDER BY NAME SEPARATOR '|') as synonyms FROM MONO_NAME
            GROUP BY  MONOMERID) as names ON MONOMER.MONOMERID = names.MONOMERID
           """

    output_file = 'tsv_from_mysql/MONO_STRUCT_NAMES.tsv'

    # set of all monomer ids
    set_of_monomer_ids=set()
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
                identifier=result[-2]
                if identifier in set_of_monomer_ids:
                    continue
                csv_writer.writerow(result)
                set_of_monomer_ids.add(identifier)

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
    for table in tables:
        print('create table', table, datetime.datetime.now())
        write_tsv(cur, table)
    #
    # # merge complex names and complex
    print('start complex', datetime.datetime.now())
    join_polymer_or_complex_new(conn, 'COMPLEX', 'COMPLEXID', 'COMPLEX_NAME', 'COMPLEX_AND_NAMES')

    # merge polymer names and polymer
    print('start polymer', datetime.datetime.now())
    join_polymer_or_complex_new(conn, 'POLYMER', 'POLYMERID', 'POLY_NAME', 'POLYMER_AND_NAMES')

    # create a monomer_names table where names are grouped by monomer id
    print('start monomer', datetime.datetime.now())
    # join monomer, monomer struct and monomer names
    join_monomer_new(conn)

    print('end', datetime.datetime.now())
