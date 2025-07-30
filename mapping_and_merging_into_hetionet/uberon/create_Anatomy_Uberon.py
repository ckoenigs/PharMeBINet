import datetime
import sys, csv

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# human xrefs from obo file
# treat-xrefs-as-reverse-genus-differentia with 9606
set_human_xrefs = set(['DHBA', 'EHDAA2', 'FMA', 'HBA', 'HsapDv'])

# treat-xrefs-as-reverse-genus-differentia:
# AAO part_of NCBITaxon:8292
#  EMAPA part_of NCBITaxon:10090
#  FBbt part_of NCBITaxon:7227
#  FBdv part_of NCBITaxon:7227
#  HAO part_of NCBITaxon:7399
#  MA part_of NCBITaxon:10090
#  MFO part_of NCBITaxon:8089
#  MmusDv part_of NCBITaxon:10090
#  OlatDv part_of NCBITaxon:8089
#  PBA part_of NCBITaxon:9443
#  SPD part_of NCBITaxon:6893
#  TADS part_of NCBITaxon:6939
#  TAO part_of NCBITaxon:32443
#  TGMA part_of NCBITaxon:44484
#  WBbt part_of NCBITaxon:6237
#  WBls part_of NCBITaxon:6237
#  XAO part_of NCBITaxon:8353
#  ZFA part_of NCBITaxon:7954
#  ZFS part_of NCBITaxon:7954
set_not_human_xrefs = set(
    ['AAO', 'EMAPA', 'FBbt', 'FBdv', 'HAO', 'MA', 'MFO', 'MmusDv', 'OlatDv', 'PBA', 'SPD', 'TADS', 'TAO', 'TGMA',
     'WBbt', 'WBls', 'XAO', 'ZFA', 'ZFS'])


def get_properties_and_generate_tsv_files_and_cypher_file():
    """
    Create TSV files for new nodes and update nodes. Prepare the additional cypher queries for the nodes and the is-a
    relationship.
    :return:
    """
    # generate csv files
    global csv_new

    file_name_new = 'output/new_nodes.tsv'
    new_nodes = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(new_nodes, delimiter='\t')
    csv_new.writerow(['id', 'name', 'synonyms', 'xrefs'])

    # fill the list with all properties in drugbank and not in pharmebinet
    query = '''MATCH (p:uberon_extend) Where p.id starts with 'UBERON' and p.is_obsolete is null WITH DISTINCT keys(p) AS keys
            UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
            RETURN allfields as l;'''
    result = g.run(query)
    query_new = []
    for record in result:
        property = record.data()['l']
        if property in ['created_by', 'creation_date']:
            continue

        # property_values
        if property == 'alt_ids':
            query_new.append('alternative_ids:a.' + property)
        elif property == 'defs':
            query_new.append('definitions:a.' + property)
        elif property == 'id':
            query_new.append('identifier:a.' + property)
        elif property == 'names':
            query_new.append('name:line.name')
        elif property in ['xrefs', 'synonyms']:
            query_new.append(f'{property}:split(line.{property},"|")')

        else:
            query_new.append(property + ':a.' + property)

    query_start = ''' Match (a:uberon_extend{id:line.id})'''
    query_create = query_start + ' Create (l:Anatomy{' + ', '.join(
        query_new) + ', uberon:"yes",  url:"http://purl.obolibrary.org/obo/"+ split(line.id,":")[0]+"_"+ split(line.id,":")[1], license:"CC BY 3.0", source:"UBERON", resource:["UBERON"]})-[:equal_anatomy_uberon]->(a)'

    with open('output/cypher.cypher', 'w', encoding='utf-8') as cypher_file:
        query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                         f'mapping_and_merging_into_hetionet/uberon/{file_name_new}',
                                                         query_create)
        cypher_file.write(pharmebinetutils.prepare_index_query('Anatomy','identifier'))
        cypher_file.write(pharmebinetutils.prepare_index_query_text('Anatomy', 'name'))
        cypher_file.write(query_create)

    with open('output/cypher_edge.cypher','w', encoding='utf-8') as cypher_file:
        query = 'Match (n:Anatomy)--(:uberon_extend)-[:is_a]->(:uberon_extend)--(m:Anatomy) Create (n)-[:IS_A_AiaA{uberon:"yes",  url:"http://purl.obolibrary.org/obo/"+ split(n.identifier,":")[0]+"_"+ split(n.identifier,":")[1], license:"CC BY 3.0", source:"UBERON", resource:["UBERON"]}]->(m);\n'
        cypher_file.write(query)

        query = 'Match (n:Anatomy)--(:uberon_extend)-[:part_of]->(:uberon_extend)--(m:Anatomy) Create (n)-[:PART_OF_ApoA{uberon:"yes",  url:"http://purl.obolibrary.org/obo/"+ split(n.identifier,":")[0]+"_"+ split(n.identifier,":")[1], license:"CC BY 3.0", source:"UBERON", resource:["UBERON"]}]->(m)'
        cypher_file.write(query)



# dictionary anatomy id to resource
dict_anatomy_id_to_resource = {}
# dictionary anatomy id to xrefs
dict_anatomy_id_to_xrefs = {}
# dictionary anatomy id to human or not (True/False)
dict_anatomy_id_to_human = {}


def load_all_uberon_with_taxonomy_information():
    """
    Get for each node that has a taxon relationship get if it is human or not in a dictionary
    :return:
    """
    query = '''Match p=(n:uberon_extend)-[r:present_in_taxon]->(m:uberon_extend) RETURN n.id, m.id '''
    results = g.run(query)
    for record in results:
        [node_id, taxon_id] = record.values()
        if taxon_id.split(':')[1] == '9606':
            dict_anatomy_id_to_human[node_id] = True
        else:
            if node_id in dict_anatomy_id_to_human and dict_anatomy_id_to_human[node_id]:
                continue
            dict_anatomy_id_to_human[node_id] = False



def add_nodes_to_different_files(results, set_not_considered_nodes, dict_nodes, set_ids_of_level, counter):
    """
    Get the result nodes of one hirarchy level. Check if this is a human node, or has no taxonomical information or the
    xrefs are from human source. These nodes are mapped to anatomy and written into the TSV file. The not mapped are
    written into the new TSV file.
    :param results:
    :param set_not_considered_nodes:
    :param dict_nodes:
    :param set_ids_of_level:
    :param counter:
    :return:
    """
    for record in results:
        [node_id, names, xrefs_uberon, synonyms, subsets] = record.values()
        if node_id in dict_nodes or node_id in set_not_considered_nodes:
            continue
        counter += 1
        xrefs_uberon = xrefs_uberon if xrefs_uberon is not None else []
        set_ids_of_level.add(node_id)
        dict_nodes[node_id] = (names, xrefs_uberon)

        # xref check
        set_xrefs = {x.split(':')[0] for x in xrefs_uberon}
        has_human_xref= bool(set_xrefs & set_human_xrefs)
        # consider no human nodes as next generation node but only add nodes to tsv if they are human or without reference
        if (node_id not in dict_anatomy_id_to_human or (node_id in dict_anatomy_id_to_human and dict_anatomy_id_to_human[node_id] == False)) and not has_human_xref and (not subsets or (subsets and not 'human_reference_atlas' in subsets  )):
            continue

        # if not has human xref but xrefs from other taxonomies continue
        if (not has_human_xref and bool(set_xrefs & set_not_human_xrefs)):
            if subsets is None or not 'human_reference_atlas' in subsets:
                continue

        names = set(names)
        # print(type(synonyms), synonyms)
        synonyms = set(synonyms) if not synonyms is None else []
        xrefs_uberon = set(xrefs_uberon) if not xrefs_uberon is None else []

        name = names.pop()
        synonyms = names.union(synonyms)
        csv_new.writerow([node_id, name, '|'.join(synonyms),
                          '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs_uberon, 'Anatomy'))])
    return counter


def load_all_uberon_anatomy_nodes():
    """
    Load all nodes below anatomical structure as anatomy nodes. COnsider the below nodes is-a and part-of.
    :return:
    """
    query_nodes = 'MATCH (n:uberon_extend)-[:%s]->(m:uberon_extend ) Where n.is_obsolete is NULL and m.id in ["%s"] and n.id starts with "UBERON" RETURN n.id, n.names, n.xrefs, n.synonyms, n.subsets'

    dict_nodes = {}

    level = 1
    # UBERON:0001062 anatomical entity
    # UBERON:0000061  anatomical structure
    # UBERON:0000465 material anatomical entity
    # UBERON:0034923 disconnected anatomical group
    dict_level_to_ids = {level: set(['UBERON:0000061', 'UBERON:0034923'])}
    set_not_considered_nodes = dict_level_to_ids[level]

    counter = 0

    while level in dict_level_to_ids:
        set_ids_of_level = set()
        new_query = query_nodes
        new_query = new_query % ('part_of', '","'.join(dict_level_to_ids[level]))
        results = g.run(new_query)
        counter = add_nodes_to_different_files(results, set_not_considered_nodes, dict_nodes,
                                                               set_ids_of_level, counter)

        new_query = query_nodes
        new_query = new_query % ('is_a', '","'.join(dict_level_to_ids[level]))
        results = g.run(new_query)
        counter = add_nodes_to_different_files(results, set_not_considered_nodes, dict_nodes,
                                                               set_ids_of_level, counter)

        if len(set_ids_of_level) == 0:
            break
        level += 1
        dict_level_to_ids[level] = set_ids_of_level

    print('number of nodes in uberon: ', counter)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path uberon')
    print(path_of_directory)
    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all properties of compound and drugbank compound and use the information to generate tsv files')

    get_properties_and_generate_tsv_files_and_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all properties of compound and drugbank compound and use the information to generate tsv files')

    load_all_uberon_with_taxonomy_information()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())

    print('load all DrugBank compounds in dictionary')

    load_all_uberon_anatomy_nodes()

    driver.close()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
