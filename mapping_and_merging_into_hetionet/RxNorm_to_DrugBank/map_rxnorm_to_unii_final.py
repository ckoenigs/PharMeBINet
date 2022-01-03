# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 10:00:16 2017

@author: ckoenigs
"""

import csv, sys

sys.path.append("../..")
import create_connection_to_databases

# generate connection to mysql
con = create_connection_to_databases.database_connection_RxNorm()

# find all
cur = con.cursor()
# from himmelstein
query = ("SELECT DISTINCT RXCUI, CODE FROM RXNCONSO WHERE SAB = 'MTHSPL' AND TTY = 'SU' AND CODE != 'NOCODE';")
cur.execute(query)

# write all information into a file
g = open('results/map_rxnorm_to_UNII.tsv', 'w', encoding='utf-8')
csv_writer = csv.writer(g, delimiter='\t')
csv_writer.writerow(['rxcui', 'unii'])
for (rxcui, code) in cur:
    csv_writer.writerow([rxcui, code])
