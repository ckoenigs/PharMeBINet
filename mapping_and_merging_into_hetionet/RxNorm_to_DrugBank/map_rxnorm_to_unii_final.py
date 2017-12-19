# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 10:00:16 2017

@author: ckoenigs
"""

import MySQLdb as mdb

# generate connection to mysql
con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'RxNorm')

# find all
cur = con.cursor()
# from himmelstein
query = ("SELECT DISTINCT RXCUI, CODE FROM RXNCONSO WHERE SAB = 'MTHSPL' AND TTY = 'SU' AND CODE != 'NOCODE';")
cur.execute(query)

# write all information into a file
g = open('map_rxnorm_to_UNII.tsv', 'w')
g.write('rxcui \t cuii\n')
for (rxcui, code) in cur:
    g.write(rxcui + '\t' + code + '\n')
