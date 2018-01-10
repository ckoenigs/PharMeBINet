# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 13:05:35 2017

@author: Cassandra
"""

'''
0:drugbank_id	
1:name	
2:type	
3:groups	
4:atc_codes	
5:categories	
6:inchikey	
7:inchi	
8:inchikeys	
9:synonyms	
10:unii	
11:uniis	
12:external_identifiers	
13:extra_names	
14:brands	
15:description
'''

f=open('../data/drugbank_with_synonyms_uniis_extern_ids.tsv','r')
g=open('map_unii_to_drugbank_id.tsv','w')
next(f)
g.write('unii \t drugbank_id \n')
for line in f:
    splitted=line.split('\t')
    if splitted[0][0:2]=='DB':
        unii=splitted[10]
        drugbank_id=splitted[0]
        if not unii=='':
            g.write(unii+'\t'+drugbank_id+'\n')
        uniis=splitted[11]
        if len(uniis)>2:
            uniis=uniis.replace('[','').replace(']','')
            uniis=uniis.replace("'","")
            uniis=uniis.split('|')
            for unii in uniis:
                g.write(unii+'\t'+drugbank_id+'\n')
            
g.close()
f.close()
            
        
    