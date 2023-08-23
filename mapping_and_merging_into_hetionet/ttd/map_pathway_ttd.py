import datetime
import csv
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary with pharmebinet pathways with identifier as key and value the name
dict_pathway_pharmebinet = {}

# dictionary with pharmebinet pathways with name as key and value the identifier
dict_pathway_pharmebinet_names = {}

# dictionary from own id to new identifier
dict_own_id_to_identifier = {}

# dictionary from own id to xrefs
dict_own_id_to_xrefs = {}

# dictionary pathway id to resource
dict_pathway_id_to_resource = {}


def load_pharmebinet_pathways_in():
    """
    load in all pathways from pharmebinet in a dictionary
    :return:
    """
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.name, n.synonyms, n.source, n.xrefs, n.resource'''
    results = g.run(query)

    for record in results:
        [identifier, name, synonyms, source, xrefs, resource] = record.values()
        dict_pathway_id_to_resource[identifier] = resource
        synonyms = synonyms if not synonyms is None else []
        if xrefs:
            dict_own_id_to_xrefs[identifier] = set(xrefs)
            for id in xrefs:
                split_source_id = id.split(':', 1)
                source = split_source_id[0]

                if not source in dict_own_id_to_identifier:
                    dict_own_id_to_identifier[source] = {}
                if source != 'wikipathways':
                    pharmebinetutils.add_entry_to_dict_to_set(dict_own_id_to_identifier[source], split_source_id[1],
                                                              identifier)
                else:
                    pharmebinetutils.add_entry_to_dict_to_set(dict_own_id_to_identifier[source],
                                                              split_source_id[1].split('_')[0], identifier)
        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_pathway_pharmebinet_names, name.lower(), identifier)

        for synonym in synonyms:
            pharmebinetutils.add_entry_to_dict_to_set(dict_pathway_pharmebinet_names, synonym.lower(), identifier)
        synonyms.append(name)
        dict_pathway_pharmebinet[identifier] = synonyms

    print('number of pathway nodes in pharmebinet:' + str(len(dict_pathway_pharmebinet)))


# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w')
csv_not_mapped = csv.writer(file_not_mapped_pathways, delimiter='\t')
csv_not_mapped.writerow(['id', 'name', 'source'])

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w')
csv_mapped = csv.writer(file_mapped_pathways, delimiter='\t')
csv_mapped.writerow(['id', 'id_pharmebinet', 'mapped', 'resource', 'xrefs'])

# dictionary to transform the xrefs name of the pathway to the same as in TTD
dict_source_ttd_to_source_pharmebinet = {
    'Reactome': 'reactome',
    'PANTHER Pathway': 'panther',
    'WikiPathway': 'wikipathways',
    # the netpathway ids looks different
    # 'NetPathway': 'netpath',
    'PathWhiz Pathway': 'pathwhiz'
}


def load_ttd_pathways_in():
    """
    load all ttd pathways and check if they are in pharmebinet or not
    :return:
    """
    query = '''MATCH (n:TTD_Pathway) RETURN n.id, n.name, n.source'''
    results = g.run(query)

    counter_map_with_id = 0
    counter_map_with_name = 0
    counter_not_mapped = 0
    for record in results:
        [pathway_id, name, source] = record.values()
        name = name.lower()
        found_mapping = False
        if source in dict_source_ttd_to_source_pharmebinet:
            other_source_name = dict_source_ttd_to_source_pharmebinet[source]
            if pathway_id in dict_own_id_to_identifier[other_source_name]:
                found_mapping = True
                counter_map_with_id += 1
                for identifier in dict_own_id_to_identifier[other_source_name][pathway_id]:
                    xrefs = dict_own_id_to_xrefs[identifier]
                    if source == 'NetPathway':
                        xrefs.add('netpath:' + identifier)
                    csv_mapped.writerow([pathway_id, identifier, other_source_name,
                                         pharmebinetutils.resource_add_and_prepare(
                                             dict_pathway_id_to_resource[identifier],
                                             'TTD'), '|'.join(xrefs)])
        if found_mapping:
            continue

        if name in dict_pathway_pharmebinet_names:
            counter_map_with_name += 1
            print(pathway_id)
            print(dict_pathway_pharmebinet_names[name])
            print('mapped with name')
            for identifier in dict_pathway_pharmebinet_names[name]:
                xrefs = dict_own_id_to_xrefs[identifier]
                if source == 'NetPathway':
                    xrefs.add('netpath:' + pathway_id)
                csv_mapped.writerow([pathway_id, identifier, 'name', pharmebinetutils.resource_add_and_prepare(
                    dict_pathway_id_to_resource[identifier],
                    'TTD'), '|'.join(xrefs)])


        else:
            csv_not_mapped.writerow([pathway_id, name, source])
            counter_not_mapped += 1

    print('number of mapping with name:' + str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print('number of not mapped:' + str(counter_not_mapped))
    # print(dict_mapped_source)


def create_cypher_file():
    """
    Generate cypher file and add cypher query to map TTD pathway to pathway.
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
    query = ''' Match (d:Pathway{identifier:line.id_pharmebinet}),(c:TTD_Pathway{id:line.id}) Create (d)-[:equal_to_ttd_pathway{how_mapped:line.mapped}]->(c) Set d.resource= split(line.resource, "|"), d.xrefs=split(line.xrefs,"|") , d.ttd="yes"'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ttd/pathway/mapped_pathways.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.close()


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
    print('Load all ttd pathways from neo4j into a dictionary')

    load_ttd_pathways_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate new pathways and connect them to ttd ')

    create_cypher_file()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
