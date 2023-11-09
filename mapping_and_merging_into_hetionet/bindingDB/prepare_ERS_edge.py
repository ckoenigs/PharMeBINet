import datetime
import os, sys
import csv
sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


polymer_protein_dict = {}
monomer_chemical_dict = {}
complex_dict = {}
ers_inhibitor_chem_dict = {}
ers_enzyme_prot_dict = {}
ers_enzyme_chem_dict = {}
ers_enzyme_complex_dict = {}
ers_substrate_prot_dict = {}
ers_substrate_chem_dict = {}
ers_substrate_complex_dict = {}

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
    load polymer, monomer, and complex ids and store them in the above defined dictionaries
    '''
    query = "MATCH (n:bindingDB_polymer_and_names)--(m:Protein) RETURN n.polymerid,m.identifier"
    results = g.run(query)
    for record in results:
        [node_ploxmer_id, node_protein_id] = record.values()
        polymer_protein_dict[node_ploxmer_id] = node_protein_id

    query = "MATCH (n:bindingDB_mono_struct_names)--(m:Chemical) RETURN n.monomerid,m.identifier"
    results = g.run(query)
    for record in results:
        [node_monomer_id, node_chemical_id] = record.values()
        monomer_chemical_dict[node_monomer_id] = node_chemical_id

    query = "MATCH (n:bindingDB_complex_and_names)--(m:Complex) RETURN n.complexid,m.identifier"
    results = g.run(query)
    for record in results:
        [node_BDcomplex_id, node_complex_id] = record.values()
        complex_dict[node_BDcomplex_id] = node_complex_id


def get_enzyme_reactant_set_properties():
    query = '''MATCH (p:bindingDB_enzyme_reactant_set) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    result = g.run(query)

    part = ''' Match (b:bindingDB_enzyme_reactant_set{reactant_set_id:line.reactant_set_id})'''
    query_nodes_start = part
    query_middle_new = ' Create (a:ERS{'
    for record in result:
        property = record.data()['l']
        if property == "reactant_set_id":
            query_middle_new += 'identifier:b.' + property + ', '

        elif ("enzyme" in property) or ("substrate" in property) or ("inhibitor" in property):
            continue
        else:
            query_middle_new += property + ':b.' + property + ', '
    query_end = ''' Create (a)-[:equal]->(b)'''
    # combine the important parts of node creation
    query_new = query_nodes_start + query_middle_new + 'url:"https://www.bindingdb.org/rwd/jsp/dbsearch/Summary_ki.jsp?entryid=1571&ki_result_id=22134&reactant_set_id=22135", license:"", resource:["bindingDB"], source:"bindingDB"})' + query_end
    return query_new




def create_node(path_of_directory, cypher_file):
    '''
    create ERS node that has properties which were already mapped
    '''
    ers_ids = set()
    enzyme_type_list = ['enzyme_polymerid', 'enzyme_monomerid', 'enzyme_complexid']
    substrate_type_list = ['substrate_polymerid', 'substrate_monomerid', 'substrate_complexid']
    query = "MATCH (n:bindingDB_enzyme_reactant_set) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        ersid = node['reactant_set_id']
        enzyme_exists = False
        substrate_exists = False
        enzyme_ok = False
        substrate_ok = False

        inhibitor = node['inhibitor_monomerid']
        if inhibitor not in monomer_chemical_dict:
            continue

        for enzyme in enzyme_type_list:
            if enzyme in node:
                enzyme_exists = True
                if 'polymer' in enzyme:
                    if node[enzyme] in polymer_protein_dict:
                        enzyme_ok = True
                        break
                    else:
                        break
                elif 'monomer' in enzyme:
                    if node[enzyme] in monomer_chemical_dict:
                        enzyme_ok = True
                        break
                    else:
                        break
                elif 'complex' in enzyme:
                    if node[enzyme] in complex_dict:
                        enzyme_ok = True
                        break
                    else:
                        break

        if (not enzyme_exists) or (enzyme_exists and not enzyme_ok):
            continue

        for substrate in substrate_type_list:
            if substrate in node:
                substrate_exists = True
                if 'polymer' in substrate:
                    if node[substrate] in polymer_protein_dict:
                        substrate_ok = True
                    else:
                        substrate_ok = False
                        break
                elif 'monomer' in substrate:
                    if node[substrate] in monomer_chemical_dict:
                        substrate_ok = True
                    else:
                        substrate_ok = False
                        break
                elif 'complex' in substrate:
                    if node[substrate] in complex_dict:
                        substrate_ok = True
                    else:
                        substrate_ok = False
                        break

        if substrate_exists and not substrate_ok:
            continue

        ers_ids.add(ersid)
        ers_inhibitor_chem_dict[ersid] = monomer_chemical_dict[node['inhibitor_monomerid']]

        if 'enzyme_polymerid' in node:
            ers_enzyme_prot_dict[ersid] = polymer_protein_dict[node['enzyme_polymerid']]
        elif 'enzyme_monomerid' in node:
            ers_enzyme_chem_dict[ersid] = monomer_chemical_dict[node['enzyme_monomerid']]
        elif 'enzyme_complexid' in node:
            ers_enzyme_complex_dict[ersid] = node['enzyme_complexid']

        if 'substrate_polymerid' in node:
            ers_substrate_prot_dict[ersid] = polymer_protein_dict[node['substrate_polymerid']]
        if 'substrate_monomerid' in node:
            ers_substrate_chem_dict[ersid] = monomer_chemical_dict[node['substrate_monomerid']]
        if 'substrate_complexid' in node:
            ers_substrate_complex_dict[ersid] = node['substrate_complexid']
    file_name = 'ers_ids'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(['reactant_set_id'])
    for id in ers_ids:
        csv_mapping.writerow([id])

    # create ERS node and match it with bindingDB_enzyme_reactant_set

    #query = f'Match (n:bindingDB_enzyme_reactant_set{{reactant_set_id:line.reactant_set_id}}) Create (m:ERS) Set m=n, m.identifier=line.reactant_set_id, m.resource=["bindingDB"], m.source="bindingDB" Create (m)-[:equal]->(n)'
    query = get_enzyme_reactant_set_properties()
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(query)

    query = pharmebinetutils.prepare_index_query('ERS', 'identifier')
    cypher_file.write(query)
    cypher_file.write('CALL db.awaitIndex("indexERS", 300);\n')


def create_ers_edges(path_of_directory, cypher_file):
    '''
    create ers-enzyme(protein, complex, chemical), ers-inhibitor(chemical), and ers-substrate(protein, complex, chemical) edges
    '''
    file_names = ['ers_inhibitor_chem', 'ers_enzyme_prot', 'ers_enzyme_chem', 'ers_enzyme_complex', 'ers_substrate_prot', 'ers_substrate_chem', 'ers_substrate_complex']
    node_name = ['Chemical', 'Protein', 'Chemical', 'Complex', 'Protein', 'Chemical', 'Complex']

    dictionaries = [ers_inhibitor_chem_dict, ers_enzyme_prot_dict, ers_enzyme_chem_dict, ers_enzyme_complex_dict, ers_substrate_prot_dict, ers_substrate_chem_dict, ers_substrate_complex_dict]
    relationship_names = ['inhibitor_chemical', 'enzyme_protein', 'enzyme_chemical', 'enzyme_complex', 'substrate_protein', 'substrate_chemical', 'substrate_complex']
    headers = [['ersid', k] for k in relationship_names]

    for i in range(len(dictionaries)):
        file_name = file_names[i]
        header = headers[i]
        file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
        csv_mapping = csv.writer(file, delimiter='\t')
        csv_mapping.writerow(header)
        l = []
        for d in dictionaries[i]:
            j = [d, dictionaries[i][d]]
            l.append(j)
        for row in l:
            csv_mapping.writerow(row)

        query = f'Match (n:ERS{{identifier:line.ersid}}), (m:{node_name[i]}{{identifier:line.{header[1]}}}) Create (n)-[:{relationship_names[i]}{{ source:"bindingDB", resource:["bindingDB"]}}] -> (m)'
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
    cypher_file = open(os.path.join(source, 'cypher_edge_2.cypher'), 'w', encoding='utf-8')
    path_of_directory = os.path.join(home, 'ERS/')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()

    print('##########################################################################')
    print('Load dictionaries', datetime.datetime.now())
    load_dictionaries()
    print('##########################################################################')
    print('Create Enzyme_reactant_set node', datetime.datetime.now())
    create_node(path_of_directory, cypher_file)
    print('##########################################################################')
    print('Create the edges',datetime.datetime.now())
    create_ers_edges(path_of_directory, cypher_file)
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()






