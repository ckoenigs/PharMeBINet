

import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    # authenticate("localhost:7474", )
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary with hetionet pathways with identifier as key and value the name
dict_pathway_hetionet = {}

# dictionary with hetionet pathways with name as key and value the identifier
dict_pathway_hetionet_names = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary pathway id to resource
dict_pathway_id_to_resource={}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.name, n.synonyms, n.source, n.xrefs, n.resource'''
    results = g.run(query)

    for identifier, name, synonyms, source, xrefs, resource, in results:
        dict_pathway_id_to_resource[identifier]=resource
        # print(identifier)
        # print(name)
        # print(synonyms)
        # print(type(synonyms))
        if identifier == 'PC11_3095':
            print('lalal')
        synonyms = synonyms if not synonyms is None else []
        if xrefs:
            for id in xrefs:
                if not id in dict_own_id_to_identifier:
                    dict_own_id_to_identifier[id] = identifier
        if not name in dict_pathway_hetionet_names:
            dict_pathway_hetionet_names[name.lower()] = set()
        dict_pathway_hetionet_names[name.lower()].add(identifier)
        # else:
        #     sys.exit('double name not considered')
        for synonym in synonyms:
            if synonym not in dict_pathway_hetionet_names:
                dict_pathway_hetionet_names[synonym.lower()] = set()
            dict_pathway_hetionet_names[synonym.lower()].add(identifier)
            # else:
            #     sys.exit('double name not considered')
        synonyms.append(name)
        dict_pathway_hetionet[identifier] = synonyms

    print('number of pathway nodes in hetionet:' + str(len(dict_pathway_hetionet)))


# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w')
csv_not_mapped = csv.writer(file_not_mapped_pathways, delimiter='\t')
csv_not_mapped.writerow(['id', 'name', 'source'])

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w')
csv_mapped = csv.writer(file_mapped_pathways, delimiter='\t')
csv_mapped.writerow(['id', 'id_hetionet', 'mapped', 'resource'])

file_multiple_mapped_pathways = open('pathway/multiple_mapped_pathways.tsv', 'w')
csv_mapped_multi = csv.writer(file_multiple_mapped_pathways, delimiter='\t')
csv_mapped_multi.writerow(['id_s', 'name', 'source_sources', 'id_hetionet', 'source_himmelstein'])

# dictionary where a ctd pathway mapped to multiple pc or wp ids
dict_ctd_to_multiple_pc_or_wp_ids = {}

def prepare_resource(mapped_id):
    """
    Prepare the resource information
    :param mapped_id: string
    :return: string of resource
    """
    resource=set(dict_pathway_id_to_resource[mapped_id])
    resource.add('CTD')
    return '|'.join(sorted(resource))



'''
load all ctd pathways and check if they are in hetionet or not
'''


def load_ctd_pathways_in():
    query = '''MATCH (n:CTD_pathway) RETURN n'''
    results = g.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_not_mapped = 0
    for pathways_node, in results:
        pathways_id = pathways_node['pathway_id']
        pathways_name = pathways_node['name'].lower()
        pathways_id_type = pathways_node['id_type']
        # because kegg is not open source it is out
        if pathways_id_type == 'KEGG':
            counter_not_mapped += 1
            continue

        # check if the ctd pathway id is part in the xref
        if 'reactome:'+pathways_id in dict_own_id_to_identifier:
            counter_map_with_id += 1
            # if len(dict_own_id_to_pcid_and_other[pathways_id]) > 1:
            #     print('multiple für identifier')
            csv_mapped.writerow([pathways_id, dict_own_id_to_identifier['reactome:'+pathways_id], 'id', prepare_resource(dict_own_id_to_identifier['reactome:'+pathways_id])])


        elif pathways_name in dict_pathway_hetionet_names:
            counter_map_with_name += 1
            print(pathways_id)
            print(dict_pathway_hetionet_names[pathways_name])
            print('mapped with name')
            for pathway_id in dict_pathway_hetionet_names[pathways_name]:
                csv_mapped.writerow([pathways_id, pathway_id, 'name', prepare_resource(pathway_id)])


        else:
            csv_not_mapped.writerow([pathways_id, pathways_name, pathways_id_type])
            counter_not_mapped += 1
            # file_not_mapped_pathways.write(pathways_id+ '\t' +pathways_name+ '\t' + pathways_id_type+ '\n' )

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('number of not mapped:' + str(counter_not_mapped))
    # print(dict_mapped_source)


'''
generate connection between mapping pathways of ctd and hetionet and generate new hetionet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a',encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/ctd/pathway/mapped_pathways.tsv" As line FIELDTERMINATOR '\\t' Match (d:Pathway{identifier:line.id_hetionet}),(c:CTD_pathway{pathway_id:line.id}) Create (d)-[:equal_to_CTD_pathway{how_mapped:line.mapped}]->(c) Set d.resource= split(line.resource, "|") , d.ctd="yes", d.ctd_url="http://ctdbase.org/detail.go?type=pathway&acc=%"+line.id, c.hetionet_id=line.id_hetionet;\n'''
    cypher_file.write(query)

    # add query to update disease nodes with do='no'
    cypher_general = open('../cypher_general.cypher', 'a', encoding='utf-8')
    query = ''':begin\n MATCH (n:Pathway) Where not exists(n.ctd) Set n.ctd="no";\n :commit\n '''
    cypher_general.write(query)
    cypher_general.close()


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all pathways from hetionet into a dictionary')

    load_hetionet_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all ctd pathways from neo4j into a dictionary')

    load_ctd_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate new pathways and connect them to ctd ')

    create_cypher_file()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
