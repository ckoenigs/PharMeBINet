# -*- coding: utf-8 -*-
"""
Created on Thr Sep 26 12:52:43 2017

@author: ckoenig
"""

'''integrate the other diseases and relationships from disease ontology in hetionet'''

import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases


# disease ontology license
license = 'CC0 4.0 International'

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary csv files
dict_label_to_label_to_rela_to_csv = defaultdict(dict)

# header of csv file
header = ['go_id','other_id']


# cypher file
cypher_file = open('output/cypher_edge.cypher', 'w')




# dictionary for relationship ends
dict_relationship_ends = {
    "BiologicalProcess": 'BP',
    "MolecularFunction": 'MF',
    "CellularComponent": 'CC',
    "Protein":'P',
    "Gene":'G'
}


def get_go_rela_properties():
    query = '''MATCH (:protein_go)-[p]-(:go) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'''
    result = g.run(query)
    query_nodes_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/go/%s" As line FIELDTERMINATOR '\\t' '''

    part = ''' Match (b:%s{identifier:line.go_id}), (c:%s{identifier:line.other_id}) Create (c)-[:%s{'''
    for property, in result:
        if property in ['db_reference', 'with_from', 'annotation_extension', 'xrefs']:
            if property=='db_reference':
                part += 'pubMed_ids:split(line.pubmed_ids,"|"), '
                header.append('pubmed_ids')
            part += property + ':split(line.' + property + ',"|"), '
        else:
            if property in ['gene_product_id','qualifier']:
                part += property + ':line.' + property + ', '
            elif property=='gene_product_id':
                part += 'iso_form:line.' + property + ', '
            else:
                part += 'not:line.' + property + ', '
        header.append(property)
    global query_rela

    # combine the important parts of node creation
    query_rela = query_nodes_start + part + 'resource:["GO"], go:"yes", source:"Gene Ontology", url:"http://purl.obolibrary.org/obo/"+line.go_id, license:"' + license + '"}]->(b);\n'


def create_csv_file(go_label, other_label, rela_type):
    file_name='edge_go_protein_gene/%s_%s_%s.tsv' %(go_label,other_label,rela_type)
    file=open(file_name, 'w', encoding='utf-8')
    csv_writer=csv.DictWriter(file, delimiter='\t', fieldnames=header)
    csv_writer.writeheader()

    rela_type_neo4j=rela_type.upper()+'_'+dict_relationship_ends[other_label]+ ''.join([x[0].lower() for x in rela_type.split('_')])+ dict_relationship_ends[go_label]

    query= query_rela %(file_name,go_label, other_label, rela_type_neo4j)
    cypher_file.write(query)
    
    dict_label_to_label_to_rela_to_csv[go_label][other_label][rela_type]=csv_writer


'''
go through all go nodes and sort them into the dictionary 
'''


def get_all_relationship_pairs(go_label, other_label):
    query = '''Match (n:%s)--(:go)-[r]-(:protein_go)--(m:%s) Return n.identifier, m.identifier, type(r), r''' % (go_label, other_label)
    result = g.run(query)
    dict_label_to_label_to_rela_to_csv[go_label][other_label]={}
    for go_id, other_id, rela_type, rela, in result:
        if rela_type not in dict_label_to_label_to_rela_to_csv[go_label][other_label]:
            create_csv_file(go_label,other_label,rela_type)
            # seperate db_reference in db_ref and pubmed ids

        dict_rela={'go_id':go_id,'other_id':other_id}
        for prop, value in rela.items():
            if prop=='db_reference':
                pubmed_ids=set()
                for entry in value:
                    if entry.startswith('PMID:'):
                        pubmed_ids.add(entry.split(':',1)[1])
                dict_rela['pubmed_ids']='|'.join(pubmed_ids)

            if type(value)!=str:
                value='|'.join(value)
            elif prop=='qualifier':
                if value.startswith('NOT|'):
                    value=True
                else:
                    value=''

            dict_rela[prop]=value


        dict_label_to_label_to_rela_to_csv[go_label][other_label][rela_type].writerow(dict_rela)



# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('get all rela properties and prepare query')

    get_go_rela_properties()


    print(
        '#################################################################################################################################################################')
    print(datetime.datetime.utcnow())
    print('go through all gos rela in dictionary')
    
    for go_label in ['BiologicalProcess','MolecularFunction','CellularComponent']:
        for other_label in ['Protein','Gene']:
            print(go_label,other_label)

            get_all_relationship_pairs(go_label, other_label)

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
