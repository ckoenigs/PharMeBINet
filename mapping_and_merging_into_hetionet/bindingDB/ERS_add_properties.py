import datetime
import os, sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary containing entryid as key and relevant information from assay to be added to the ers nodes
assay_dict = {}

# dictionary containing entryid as key and relevant information from article (and edge to entry) to be added to the ers nodes
article_dict = {}

# dictionary containing reactant_set_id and entryid as key and relevant information from ki_result to be added to the ers nodes
ki_result_dict = {}


def create_connection_with_neo4j():
    '''
    create a connection with neo4j
    '''
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def load_dictionaries():
    '''
    load assay, article and ki_result properties that will be added to the ERS node and store them in the above defined dictionaries
    '''

    print("Load assay dict")
    print("#########################################")
    query = "MATCH (n:bindingDB_ASSAY) return n.entryid, n.description "
    results = g.run(query)
    for record in results:
        [entryid, description] = record.values()
        if entryid in assay_dict:
            assay_dict[entryid].add(description)
        else:
            s = set()
            s.add(description)
            assay_dict[entryid] = s

    print("Load article dict")
    print("#########################################")
    #add info from edge to the dict (n)-[r](m) return r.art_purp
    query = "MATCH (n:bindingDB_ARTICLE)-[r]-(m:bindingDB_ENTRY) RETURN n.pmid, n.doi, m.entryid, r.art_purp"
    results = g.run(query)
    for record in results:
        [pmid, doi, entryid, art_purp] = record.values()
        if pmid is None and doi is None:
            continue
        if entryid not in article_dict:
            article_dict[entryid] = [set(), set(), set()]
        if pmid is not None:
            article_dict[entryid][0].add(pmid)
        if doi is not None:
            article_dict[entryid][1].add(doi)
        if art_purp not in ["___", "Not specified!", None]:
            article_dict[entryid][2].add(art_purp)


    print("Load ki_result dict")
    print("#########################################")
    query = "MATCH (n:bindingDB_KI_RESULT) RETURN n.reactant_set_id, n.entryid, n.ki_result_id, n.ic50, n.k_cat, n.ec_50, n.kd, n.koff, n.km, n.kon, n.temp, n.ph"
    results = g.run(query)
    for record in results:
        [reactant_set_id, entryid, ki_result_id, ic50, k_cat, ec_50, kd, koff, km, kon, temp, ph] = record.values()
        ki_result_dict[(reactant_set_id, entryid)] = [ki_result_id, ic50, k_cat, ec_50, kd, koff, km, kon, temp, ph]

def add_ers_properties():
    '''
    prepare tsv file containing properties that need to be added to the ERS node
    '''
    file_name = 'ers_properties'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(
        ['reactant_set_id', 'description', 'pmid', 'doi', 'art_purp', 'ki_result_id', 'ic50', 'k_cat', 'ec_50', 'kd', 'koff',
         'km', 'kon', 'temp', 'ph'])
    query = "MATCH (n:ERS) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        ersid = node['identifier']
        l = []
        entry_id = node['entryid']
        if entry_id in assay_dict:
            l.append(["|".join(assay_dict[entry_id])])
        else:
            l.append([])
        if entry_id in article_dict:
            l.append(["|".join(x) for x in article_dict[entry_id]])
        else:
            continue
        if (ersid, entry_id) in ki_result_dict:
            l.append(ki_result_dict[(ersid, entry_id)])
        else:
            l.append([])

        row = [ersid]
        for li in l:
            row += li
        csv_mapping.writerow(row)

def create_cypher_query(cypher_file):
    '''
    create cypher query to add properties to ERS node
    '''

    #art purp
    properties = ['description', 'pmid', 'doi', 'art_purp', 'ki_result_id', 'ic50', 'k_cat', 'ec_50',
                  'kd', 'koff', 'km', 'kon', 'temp', 'ph']

    q = ""
    for property in properties:
        if property in ['description', 'pmid', 'doi', 'art_purp']:
            q += "n." + property + "=split(line." + property + ', "|"), '
        else:
            q += "n." + property +"=line." + property + ", "
    q = q[:-2]

    query = (f'MATCH (n:ERS{{identifier:line.reactant_set_id}}) SET ')
    query += q
    file_name = "ers_properties"
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(query)



def main():
    print(datetime.datetime.now())
    global home
    global path_of_directory
    global source

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path bindingdb ers')

    os.chdir(path_of_directory + 'mapping_and_merging_into_hetionet/bindingDB/')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    cypher_file = open(os.path.join(source, 'cypher.cypher'), 'w', encoding='utf-8')
    path_of_directory = os.path.join(home, 'ERS/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')
    print('Load dictionaries')
    load_dictionaries()
    print('##########################################################################')
    print('Add properties to ERS')
    add_ers_properties()
    create_cypher_query(cypher_file)

if __name__ == "__main__":
    # execute only if run as a script
    main()
