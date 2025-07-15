import datetime
import os, sys
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary containing polymerids and the corresponding protein identifiers
polymer_protein_dict = {}

# dictionary containing monomerids and the corresponding chemical identifiers
monomer_chemical_dict = {}

# set containing complexids 
set_complex = set()

# dictionary containing enzyme_reactant_set_ids and chemical identifiers corresponding to monomer_inhibitor
ers_inhibitor_chem_dict = {}

# dictionary containing enzyme_reactant_set_ids and protein identifiers corresponding to polymer_enzyme
ers_enzyme_prot_dict = {}

# dictionary containing enzyme_reactant_set_ids and chemical identifiers corresponding to monomer_enzyme
ers_enzyme_chem_dict = {}

# dictionary containing enzyme_reactant_set_ids and complex identifiers corresponding to complex_enzyme
ers_enzyme_complex_dict = {}

# dictionary containing enzyme_reactant_set_ids and protein identifiers corresponding to polymer_substrate
ers_substrate_prot_dict = {}

# dictionary containing enzyme_reactant_set_ids and chemical identifiers corresponding to monomer_substrate
ers_substrate_chem_dict = {}

# dictionary containing enzyme_reactant_set_ids and complex identifiers corresponding to complex_substrate
ers_substrate_complex_dict = {}

# dictionary containing protein identifiers and the corresponding unpid1
polymer_edge_dict = {}

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
    load polymer, monomer, and complex ids and store them in the above defined dictionaries
    '''
    print("Load polymer-protein dict")
    print("#########################################")
    query = "MATCH (n:bindingDB_polymer_and_names)--(m:Protein) RETURN n.polymerid, m.identifier, n.unpid1"
    results = g.run(query)
    for record in results:
        [node_ploymer_id, node_protein_id, node_unpid1] = record.values()
        polymer_protein_dict[node_ploymer_id] = node_protein_id

        # relevant for the edges between polymer and ers
        polymer_edge_dict[node_protein_id] = node_unpid1

    query = "MATCH (n:bindingDB_mono_struct_names)--(m:Chemical) RETURN n.monomerid,m.identifier"
    results = g.run(query)
    for record in results:
        [node_monomer_id, node_chemical_id] = record.values()
        monomer_chemical_dict[node_monomer_id] = node_chemical_id

    query = "MATCH (n:bindingDB_complex_and_names)--(m:Complex) RETURN m.identifier"
    results = g.run(query)
    for record in results:
        [node_complex_id] = record.values()
        set_complex.add(node_complex_id)

    '''
        load assay, article and ki_result properties that will be added to the ERS node and store them in the above defined dictionaries
        '''

    print("Load assay dict")
    print("#########################################")
    query = "MATCH (n:bindingDB_assay) return n.entryid, n.description "
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
    # add info from edge to the dict (n)-[r](m) return r.art_purp
    query = "MATCH (n:bindingDB_article)-[r]-(m:bindingDB_entry) RETURN n.pmid, n.doi, m.entryid, r.art_purp"
    results = g.run(query)
    for record in results:
        [pmid, doi, entryid, art_purp] = record.values()
        if pmid is None and doi is None:
            continue
        if entryid not in article_dict:
            # pubmed, dois, art_purp, patent number
            article_dict[entryid] = [set(), set(), set(), set()]
        if pmid is not None:
            if not pmid.startswith('US'):
                article_dict[entryid][0].add(pmid)
            else:
                article_dict[entryid][3].add(pmid)
        if doi is not None:
            article_dict[entryid][1].add(doi)
        if art_purp not in ["___", "Not specified!", None]:
            article_dict[entryid][2].add(art_purp)

    print("Load ki_result dict")
    print("#########################################")
    query = "MATCH (n:bindingDB_ki_result) RETURN n.reactant_set_id, n.entryid, n.ki_result_id, n.ic50, n.k_cat, n.ec50, n.kd, n.koff, n.km, n.kon, n.temp, n.ph, n.ki"
    results = g.run(query)
    for record in results:
        [reactant_set_id, entryid, ki_result_id, ic50, k_cat, ec_50, kd, koff, km, kon, temp, ph, ki] = record.values()
        ki_result_dict[(reactant_set_id, entryid)] = [ki_result_id, ic50, k_cat, ec_50, kd, koff, km, kon, temp, ph, ki]


properties = ['description', 'pmid', 'doi', 'art_purp', 'patents', 'ki_result_id', 'ic50', 'k_cat', 'ec50',
              'kd', 'koff', 'km', 'kon', 'temp', 'ph', 'ki']


def get_enzyme_reactant_set_properties():
    '''
    get enzyme_reactant_set properties that will be added to the ers node
    '''

    query = '''MATCH (p:bindingDB_enzyme_reactant_set) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields as l;'''
    result = g.run(query)

    part = ''' Match (b:bindingDB_enzyme_reactant_set{reactant_set_id:line.reactant_set_id})'''
    query_nodes_start = part
    query_middle_new = ' Create (a:EnzymeReactantSet{'
    for record in result:
        property = record.data()['l']
        if property == "reactant_set_id":
            query_middle_new += 'identifier:b.' + property + ', '

        elif ("enzyme" in property) or ("substrate" in property) or ("inhibitor" in property):
            continue
        else:
            query_middle_new += property + ':b.' + property + ', '

    for property in properties:
        if property in ['description', 'doi', 'art_purp']:
            query_middle_new += property + "s:split(line." + property + ', "|"), '
        elif property =='pmid':
            query_middle_new += "pubMed_ids:split(line." + property + ', "|"), '
        else:
            query_middle_new += property + ":line." + property + ", "
    query_end = ''' Create (a)-[:equal]->(b)'''
    # combine the important parts of node creation
    query_new = query_nodes_start + query_middle_new + 'url:"https://www.bindingdb.org/rwd/jsp/dbsearch/Summary_ki.jsp?entryid="+b.entryid+"&ki_result_id="+line.ki_result_id+"&reactant_set_id="+b.reactant_set_id, node_edge:true , license:"CC BY 3.0 US Deed", resource:["BindingDB"], source:"BindingDB", bindingdb:"yes"})' + query_end
    return query_new


def create_node(path_of_directory, cypher_file):
    '''
    create ERS node that has properties which were already mapped
    '''

    # save the ers_ids in a tsv file
    file_name = 'ers_ids'
    file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    header = ['reactant_set_id']
    header.extend(properties)
    csv_mapping.writerow(header)

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
                    if node[enzyme] in set_complex:
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
                    if node[substrate] in set_complex:
                        substrate_ok = True
                    else:
                        substrate_ok = False
                        break

        if substrate_exists and not substrate_ok:
            continue

        l = [ersid]
        entry_id = node['entryid']
        if entry_id in assay_dict:
            l.append("|".join(assay_dict[entry_id]))
        else:
            l.append('')
        if entry_id in article_dict:
            l.extend(["|".join(x) for x in article_dict[entry_id]])
        else:
            continue
        if (ersid, entry_id) in ki_result_dict:
            l.extend(ki_result_dict[(ersid, entry_id)])
        else:
            print('without ki', ersid)
        csv_mapping.writerow(l)

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

    # create ERS node and match it with bindingDB_enzyme_reactant_set

    query = get_enzyme_reactant_set_properties()
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file.write(pharmebinetutils.prepare_index_query('EnzymeReactantSet', 'identifier'))
    cypher_file.write(query)

    cypher_file.write('CALL db.awaitIndex("indexEnzymeReactantSet", 300);\n')


def create_ers_edges(path_of_directory, cypher_file):
    '''
    create ers-enzyme(protein, complex, chemical), ers-inhibitor(chemical), and ers-substrate(protein, complex, chemical) edges
    '''
    file_names = ['ers_inhibitor_chem', 'ers_enzyme_prot', 'ers_enzyme_chem', 'ers_enzyme_complex',
                  'ers_substrate_prot', 'ers_substrate_chem', 'ers_substrate_complex']
    node_name = ['Chemical', 'Protein', 'Chemical', 'MolecularComplex', 'Protein', 'Chemical', 'MolecularComplex']

    dictionaries = [ers_inhibitor_chem_dict, ers_enzyme_prot_dict, ers_enzyme_chem_dict, ers_enzyme_complex_dict,
                    ers_substrate_prot_dict, ers_substrate_chem_dict, ers_substrate_complex_dict]
    relationship_names = ['INHIBITS', 'IS_ENZYME', 'IS_ENZYME', 'IS_ENZYME',
                          'IS_SUBSTRATE', 'IS_SUBSTRATE', 'IS_SUBSTRATE']
    headers = [['ersid', k] for k in relationship_names]

    for i in range(len(dictionaries)):
        file_name = file_names[i]
        header = headers[i]
        if "prot" in file_name:
            header.append('unpid1')
        file = open(os.path.join(path_of_directory, file_name) + '.tsv', 'w', encoding='utf-8', newline="")
        csv_mapping = csv.writer(file, delimiter='\t')
        csv_mapping.writerow(header)
        l = []
        for d in dictionaries[i]:
            j = [d, dictionaries[i][d]]
            if dictionaries[i] in [ers_enzyme_prot_dict, ers_substrate_prot_dict]:
                j.append(polymer_edge_dict[dictionaries[i][d]])
            l.append(j)
        for row in l:
            csv_mapping.writerow(row)
        # for POLYMER: add unpid1 to edge (variant)
        if "prot" in file_name:
            query = f'Match (n:EnzymeReactantSet{{identifier:line.ersid}}), (m:{node_name[i]}{{identifier:line.{header[1]}}}) Create (m)-[:{relationship_names[i]}_{pharmebinetutils.dictionary_label_to_abbreviation[node_name[i]]}{"".join([x[0].lower() for x in relationship_names[i].split("_")])}{pharmebinetutils.dictionary_label_to_abbreviation["EnzymeReactantSet"]}{{ source:"BindingDB", resource:["BindingDB"], url:"https://www.bindingdb.org/rwd/jsp/dbsearch/Summary_ki.jsp?entryid="+n.entryid+"&ki_result_id="+n.ki_result_id+"&reactant_set_id="+line.ersid, bindingdb:"yes", license:"CC BY 3.0 US Deed", variant: line.unpid1}}] -> (n)'
        else:
            query = f'Match (n:EnzymeReactantSet{{identifier:line.ersid}}), (m:{node_name[i]}{{identifier:line.{header[1]}}}) Create (m)-[:{relationship_names[i]}_{pharmebinetutils.dictionary_label_to_abbreviation[node_name[i]]}{"".join([x[0].lower() for x in relationship_names[i].split("_")])}{pharmebinetutils.dictionary_label_to_abbreviation["EnzymeReactantSet"]}{{ source:"BindingDB", bindingdb:"yes", url:"https://www.bindingdb.org/rwd/jsp/dbsearch/Summary_ki.jsp?entryid="+n.entryid+"&ki_result_id="+n.ki_result_id+"&reactant_set_id="+line.ersid, license:"CC BY 3.0 US Deed", resource:["BindingDB"]}}] -> (n)'
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
        sys.exit('need a path bindingdb EnzymeReactantSet')

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
    print('Create the edges', datetime.datetime.now())
    create_ers_edges(path_of_directory, cypher_file)
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
