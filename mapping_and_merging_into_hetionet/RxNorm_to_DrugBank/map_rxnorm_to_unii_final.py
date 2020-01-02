# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 10:00:16 2017

@author: ckoenigs
"""

import MySQLdb as mdb
import csv

# generate connection to mysql
con = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'RxNorm')

# find all
cur = con.cursor()
# from himmelstein
query = ("SELECT DISTINCT RXCUI, CODE FROM RXNCONSO WHERE SAB = 'MTHSPL' AND TTY = 'SU' AND CODE != 'NOCODE';")
cur.execute(query)

# write all information into a file
g = open('results/map_rxnorm_to_UNII.tsv', 'w')
csv_writer=csv.writer(g,delimiter='\t')
csv_writer.writerow(['rxcui','unii'])
for (rxcui, code) in cur:
    csv_writer.writerow([rxcui , code ])
