

import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary with pharmebinet pathways with identifier as key and value the name
dict_pathway_pharmebinet = {}

# dictionary with pharmebinet pathways with name as key and value the identifier
dict_pathway_pharmebinet_names = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary pathway id to resource
dict_pathway_id_to_resource={}

'''
load in all pathways from pharmebinet in a dictionary
'''


def load_pharmebinet_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.name, n.synonyms, n.source, n.xrefs, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, source, xrefs, resource]=record.values()
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
        if name is not None:
            if not name in dict_pathway_pharmebinet_names:
                dict_pathway_pharmebinet_names[name.lower()] = set()
            dict_pathway_pharmebinet_names[name.lower()].add(identifier)
        # else:
        #     sys.exit('double name not considered')
        for synonym in synonyms:
            if synonym not in dict_pathway_pharmebinet_names:
                dict_pathway_pharmebinet_names[synonym.lower()] = set()
            dict_pathway_pharmebinet_names[synonym.lower()].add(identifier)
            # else:
            #     sys.exit('double name not considered')
        synonyms.append(name)
        dict_pathway_pharmebinet[identifier] = synonyms

    print('number of pathway nodes in pharmebinet:' + str(len(dict_pathway_pharmebinet)))


# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w')
csv_not_mapped = csv.writer(file_not_mapped_pathways, delimiter='\t')
csv_not_mapped.writerow(['id', 'name', 'source'])

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w')
csv_mapped = csv.writer(file_mapped_pathways, delimiter='\t')
csv_mapped.writerow(['id', 'id_pharmebinet', 'mapped', 'resource'])

file_multiple_mapped_pathways = open('pathway/multiple_mapped_pathways.tsv', 'w')
csv_mapped_multi = csv.writer(file_multiple_mapped_pathways, delimiter='\t')
csv_mapped_multi.writerow(['id_s', 'name', 'source_sources', 'id_pharmebinet', 'source_himmelstein'])

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
load all ctd pathways and check if they are in pharmebinet or not
'''


def load_ctd_pathways_in():
    query = '''MATCH (n:CTD_pathway) RETURN n'''
    results = g.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_not_mapped = 0
    for record in results:
        pathways_node=record.data()['n']
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


        elif pathways_name in dict_pathway_pharmebinet_names:
            counter_map_with_name += 1
            print(pathways_id)
            print(dict_pathway_pharmebinet_names[pathways_name])
            print('mapped with name')
            for pathway_id in dict_pathway_pharmebinet_names[pathways_name]:
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
generate connection between mapping pathways of ctd and pharmebinet and generate new pharmebinet nodes for the not existing nodes
'''


def create_cypher_file():
    cypher_file = open('output/cypher.cypher', 'a',encoding='utf-8')
    query = ''' Match (d:Pathway{identifier:line.id_pharmebinet}),(c:CTD_pathway{pathway_id:line.id}) Create (d)-[:equal_to_CTD_pathway{how_mapped:line.mapped}]->(c) Set d.resource= split(line.resource, "|") , d.ctd="yes", d.ctd_url="http://ctdbase.org/detail.go?type=pathway&acc=%"+line.id, c.pharmebinet_id=line.id_pharmebinet'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/pathway/mapped_pathways.tsv',
                                              query)
    cypher_file.write(query)



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
    print('Load all pathways from pharmebinet into a dictionary')

    load_pharmebinet_pathways_in()

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

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
