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
    g = driver.session()


# human xrefs from obo file
# treat-xrefs-as-reverse-genus-differentia with 9606
set_human_xrefs = set(['DHBA', 'EHDAA2', 'FMA', 'HBA', 'HsapDv'])


def get_properties_and_generate_tsv_files_and_cypher_file():
    """
    Create TSV files for new nodes and update nodes. Prepare the additional cypher queries for the nodes and the is-a
    relationship.
    :return:
    """
    # generate csv files
    global csv_update, csv_new

    file_name_new = 'output/new_nodes.tsv'
    new_nodes = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(new_nodes, delimiter='\t')
    csv_new.writerow(['id', 'name', 'synonyms', 'xrefs'])

    file_name_mapped = 'output/update_nodes.tsv'
    update_nodes = open(file_name_mapped, 'w', encoding='utf-8')
    csv_update = csv.writer(update_nodes, delimiter='\t')
    csv_update.writerow(['id', 'synonyms', 'xrefs', 'resource'])

    # fill the list with all properties in drugbank and not in pharmebinet
    query = '''MATCH (p:uberon_extend) Where p.id starts with 'UBERON' and p.is_obsolete is null WITH DISTINCT keys(p) AS keys
            UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
            RETURN allfields as l;'''
    result = g.run(query)

    query_match = []
    query_new = []
    for record in result:
        property = record.data()['l']
        if property in ['created_by', 'creation_date']:
            continue

        # property_values
        if property == 'alt_ids':
            query_match.append('l.alternative_ids=a.' + property)
            query_new.append('alternative_ids:a.' + property)
        elif property == 'defs':
            query_match.append('l.definitions=a.' + property)
            query_new.append('definitions:a.' + property)
        elif property == 'id':
            query_new.append('identifier:a.' + property)
        elif property == 'names':
            query_new.append('name:line.name')
        elif property in ['xrefs', 'synonyms']:
            query_match.append(f'l.{property}=split(line.{property},"|")')
            query_new.append(f'{property}:split(line.{property},"|")')

        else:
            query_match.append(f'l.{property}=a.' + property)
            query_new.append(property + ':a.' + property)

    query_start = ''' Match (a:uberon_extend{id:line.id})'''
    query_match = query_start + ' , (l:Anatomy{identifier:line.id}) Set ' + ', '.join(
        query_match) + ', l.uberon="yes", l.resource=split(line.resource,"|") Create (l)-[:equal_anatomy_uberon]->(a)'
    query_create = query_start + ' Create (l:Anatomy{' + ', '.join(
        query_new) + ', uberon:"yes",  url:"http://purl.obolibrary.org/obo/"+ split(line.id,":")[0]+"_"+ split(line.id,":")[1], license:"CC BY 3.0", source:"UBERON", resource:["UBERON"]})-[:equal_anatomy_uberon]->(a)'

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/uberon/{file_name_new}',
                                                     query_create)
    cypher_file.write(query_create)
    query_match = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/uberon/{file_name_mapped}',
                                                    query_match)
    cypher_file.write(query_match)

    query = 'Match (n:Anatomy)--(:uberon_extend)-[:is_a]->(:uberon_extend)--(m:Anatomy) Create (n)-[:IS_A_AisA{uberon:"yes",  url:"http://purl.obolibrary.org/obo/"+ split(n.identifier,":")[0]+"_"+ split(n.identifier,":")[1], license:"CC BY 3.0", source:"UBERON", resource:["UBERON"]}]->(m)'
    cypher_file.write(query)

    query = 'Match (n:Anatomy)--(:uberon_extend)-[:part_of]->(:uberon_extend)--(m:Anatomy) Create (n)-[:PART_OF_ApoA{uberon:"yes",  url:"http://purl.obolibrary.org/obo/"+ split(n.identifier,":")[0]+"_"+ split(n.identifier,":")[1], license:"CC BY 3.0", source:"UBERON", resource:["UBERON"]}]->(m)'
    cypher_file.write(query)
    cypher_file.close()


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


def load_all_pharmebinet_anatomy_in_dictionary():
    """
    Load all existing Anatomy nodes into dictionaries
    :return:
    """
    query = '''Match (n:Anatomy) RETURN n '''
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        dict_anatomy_id_to_resource[identifier] = set(node['resource'])
        dict_anatomy_id_to_xrefs[identifier] = set(node['xrefs']) if 'xrefs' in node else set()

    print('size of anatomies in pharmebinet before the rest of DrugBank is added: ', len(dict_anatomy_id_to_resource))


def add_nodes_to_different_files(results, set_not_considered_nodes, dict_nodes, set_ids_of_level, counter,
                                 counter_mapped):
    """
    Get the result nodes of one hirarchy level. Check if this is a human node, or has no taxonomical information or the
    xrefs are from human source. These nodes are mapped to anatomy and written into the TSV file. The not mapped are
    written into the new TSV file.
    :param results:
    :param set_not_considered_nodes:
    :param dict_nodes:
    :param set_ids_of_level:
    :param counter:
    :param counter_mapped:
    :return:
    """
    for record in results:
        [node_id, names, xrefs_uberon, synonyms] = record.values()
        if node_id in dict_nodes or node_id in set_not_considered_nodes:
            continue
        counter += 1
        xrefs_uberon = xrefs_uberon if xrefs_uberon is not None else []
        set_ids_of_level.add(node_id)
        dict_nodes[node_id] = (names, xrefs_uberon)

        # xref check
        set_xrefs = {x.split(':')[0] for x in xrefs_uberon}
        # consider no human nodes as next generation node but only add nodes to tsv if they are human or without reference
        if (node_id in dict_anatomy_id_to_human and dict_anatomy_id_to_human[node_id] == False and not bool(
                set_xrefs & set_human_xrefs)):
            continue
        names = set(names)
        # print(type(synonyms), synonyms)
        synonyms = set(synonyms) if not synonyms is None else []
        xrefs_uberon = set(xrefs_uberon) if not xrefs_uberon is None else []
        if node_id in dict_anatomy_id_to_resource:
            counter_mapped += 1
            synonyms = names.union(synonyms)
            xrefs = dict_anatomy_id_to_xrefs[node_id]
            xrefs = xrefs.union(xrefs_uberon)
            resource = dict_anatomy_id_to_resource[node_id]
            csv_update.writerow(
                [node_id, '|'.join(synonyms),
                 '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'Anatomy')),
                 pharmebinetutils.resource_add_and_prepare(resource, 'UBERON')])
        else:
            name = names.pop()
            synonyms = names.union(synonyms)
            csv_new.writerow([node_id, name, '|'.join(synonyms),
                              '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs_uberon, 'Anatomy'))])
    return counter, counter_mapped


def load_all_uberon_anatomy_nodes():
    """
    Load all nodes below anatomical structure as anatomy nodes. COnsider the below nodes is-a and part-of.
    :return:
    """
    query_nodes = 'MATCH (n:uberon_extend)-[:%s]->(m:uberon_extend ) Where n.is_obsolete is NULL and m.id in ["%s"] and n.id starts with "UBERON" RETURN n.id, n.names, n.xrefs, n.synonyms'

    dict_nodes = {}

    level = 1
    # UBERON:0001062 anatomical entity
    # UBERON:0000061  anatomical structure
    # UBERON:0000465 material anatomical entity
    dict_level_to_ids = {level: set(['UBERON:0000061'])}
    set_not_considered_nodes = dict_level_to_ids[level]

    counter = 0
    counter_mapped = 0

    while level in dict_level_to_ids:
        set_ids_of_level = set()
        new_query = query_nodes
        new_query = new_query % ('part_of', '","'.join(dict_level_to_ids[level]))
        results = g.run(new_query)
        counter, counter_mapped = add_nodes_to_different_files(results, set_not_considered_nodes, dict_nodes,
                                                               set_ids_of_level, counter, counter_mapped)

        new_query = query_nodes
        new_query = new_query % ('is_a', '","'.join(dict_level_to_ids[level]))
        results = g.run(new_query)
        counter, counter_mapped = add_nodes_to_different_files(results, set_not_considered_nodes, dict_nodes,
                                                               set_ids_of_level, counter, counter_mapped)

        if len(set_ids_of_level) == 0:
            break
        level += 1
        dict_level_to_ids[level] = set_ids_of_level

    print('number of nodes in uberon: ', counter)
    print('number of mapped nodes in uberon: ', counter_mapped)


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
    print('load all pharmebinet anatomy in dictionary')

    load_all_pharmebinet_anatomy_in_dictionary()

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
